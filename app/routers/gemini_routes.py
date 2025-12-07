"""
Gemini 2.5 Flash WebSocket 및 HTTP 라우터
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from app.services.gemini_service import generate_gemini_stream, generate_gemini_simple
from app.schemas.chat_schema import ChatRequest
import json
from typing import Optional

router = APIRouter(tags=["Gemini Chat"])


@router.websocket("/gemini/ws")
async def gemini_websocket(websocket: WebSocket):
    """
    Gemini 2.5 Flash WebSocket 엔드포인트
    
    클라이언트는 다음 형식으로 메시지를 보내야 합니다:
    {
        "type": "message",
        "content": "사용자 메시지",
        "model": "gemini-2.5-flash" (선택적),
        "chat_history": [...] (선택적)
    }
    
    서버는 다음 형식으로 응답합니다:
    - {"type": "start"} - 스트리밍 시작
    - {"type": "chunk", "content": "텍스트 청크"} - 스트리밍 데이터
    - {"type": "end"} - 스트리밍 완료
    - {"type": "error", "content": "에러 메시지"} - 에러 발생
    """
    await websocket.accept()
    
    chat_history = []
    
    try:
        while True:
            # 클라이언트로부터 메시지 수신
            raw_text = await websocket.receive_text()
            data = json.loads(raw_text)
            
            if data.get('type') == 'message':
                message = data.get('content', '')
                model = data.get('model', 'gemini-2.5-flash')
                chat_history = data.get('chat_history', chat_history)
                
                if not message:
                    await websocket.send_json({
                        "type": "error",
                        "content": "메시지가 비어있습니다."
                    })
                    continue
                
                # 사용자 메시지를 히스토리에 추가
                chat_history.append({"role": "user", "content": message})
                
                # 스트리밍 시작 신호
                await websocket.send_json({"type": "start"})
                
                # 스트리밍 응답 생성
                full_response = ""
                async for chunk in generate_gemini_stream(message, chat_history, model):
                    if chunk.startswith("Error:"):
                        await websocket.send_json({
                            "type": "error",
                            "content": chunk
                        })
                        break
                    
                    full_response += chunk
                    await websocket.send_json({
                        "type": "chunk",
                        "content": chunk
                    })
                
                # 응답을 히스토리에 추가
                if full_response and not full_response.startswith("Error:"):
                    chat_history.append({"role": "assistant", "content": full_response})
                
                # 스트리밍 완료 신호
                await websocket.send_json({"type": "end"})
            
            elif data.get('type') == 'clear_history':
                # 대화 히스토리 초기화
                chat_history = []
                await websocket.send_json({
                    "type": "info",
                    "content": "대화 히스토리가 초기화되었습니다."
                })
            
            else:
                await websocket.send_json({
                    "type": "error",
                    "content": f"알 수 없는 메시지 타입: {data.get('type')}"
                })
                
    except WebSocketDisconnect:
        print("WebSocket 연결이 종료되었습니다.")
    except Exception as e:
        print(f"WebSocket 오류: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "content": f"서버 오류: {str(e)}"
            })
        except:
            pass
        await websocket.close()


@router.post("/gemini/chat")
async def gemini_chat_endpoint(request: ChatRequest):
    """
    Gemini 2.5 Flash HTTP 스트리밍 엔드포인트
    
    NDJSON 형식으로 스트리밍 응답 반환
    """
    async def generate_ndjson():
        async for chunk in generate_gemini_stream(
            request.message,
            model=getattr(request, 'model', 'gemini-2.5-flash')
        ):
            data = {
                "type": "content",
                "content": chunk
            }
            yield json.dumps(data) + "\n"
    
    return StreamingResponse(
        generate_ndjson(),
        media_type="application/x-ndjson"
    )


@router.post("/gemini/chat/simple")
async def gemini_chat_simple(request: ChatRequest):
    """
    Gemini 2.5 Flash HTTP 단순 응답 엔드포인트 (비스트리밍)
    """
    response = await generate_gemini_simple(
        request.message,
        model=getattr(request, 'model', 'gemini-2.5-flash')
    )
    return {
        "message": response,
        "model": getattr(request, 'model', 'gemini-2.5-flash')
    }





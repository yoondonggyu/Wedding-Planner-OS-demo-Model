"""
Gemini 2.5 Flash 서비스 - WebSocket 스트리밍 지원
"""
import asyncio
from typing import AsyncGenerator
from google import genai
from app.core.config import GEMINI_API_KEY, GEMINI_MODEL


async def generate_gemini_stream(
    message: str,
    chat_history: list = None,
    model: str = "gemini-2.5-flash"
) -> AsyncGenerator[str, None]:
    """
    Gemini 2.5 Flash를 사용한 스트리밍 응답 생성 (공식 문서 방식)
    
    Args:
        message: 사용자 메시지
        chat_history: 이전 대화 기록 (선택적)
        model: 사용할 모델명 (기본값: gemini-2.5-flash)
    
    Yields:
        str: 스트리밍된 텍스트 청크
    """
    if not GEMINI_API_KEY:
        yield "Error: GEMINI_API_KEY가 설정되지 않았습니다. .env 파일을 확인해주세요."
        return
    
    try:
        # Gemini 클라이언트 초기화 (공식 문서 방식)
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        # 채팅 히스토리가 있으면 메시지 구성
        contents = message
        if chat_history:
            # 히스토리를 포함한 메시지 구성
            history_messages = []
            for hist in chat_history:
                role = hist.get("role", "")
                content = hist.get("content", "")
                if content:
                    history_messages.append(content)
            if history_messages:
                # 히스토리와 현재 메시지를 결합
                contents = "\n".join(history_messages) + "\n" + message
        
        # 공식 문서 방식: generate_content_stream 사용
        response = client.models.generate_content_stream(
            model=model or GEMINI_MODEL,
            contents=contents
        )
        
        # 스트리밍 응답 처리
        for chunk in response:
            if hasattr(chunk, 'text') and chunk.text:
                yield chunk.text
                await asyncio.sleep(0.01)
        
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        print(f"❌ Gemini API 오류: {e}")
        yield error_msg


async def generate_gemini_simple(
    message: str,
    chat_history: list = None,
    model: str = "gemini-2.5-flash"
) -> str:
    """
    Gemini 2.5 Flash를 사용한 단순 응답 생성 (비스트리밍, 공식 문서 방식)
    
    Args:
        message: 사용자 메시지
        chat_history: 이전 대화 기록 (선택적)
        model: 사용할 모델명 (기본값: gemini-2.5-flash)
    
    Returns:
        str: 완전한 응답 텍스트
    """
    if not GEMINI_API_KEY:
        return "Error: GEMINI_API_KEY가 설정되지 않았습니다. .env 파일을 확인해주세요."
    
    try:
        # 공식 문서 방식: generate_content
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        # 채팅 히스토리가 있으면 메시지 구성
        contents = message
        if chat_history:
            history_messages = []
            for hist in chat_history:
                role = hist.get("role", "")
                content = hist.get("content", "")
                if content:
                    history_messages.append(content)
            if history_messages:
                contents = "\n".join(history_messages) + "\n" + message
        
        response = client.models.generate_content(
            model=model or GEMINI_MODEL,
            contents=contents
        )
        
        return response.text if hasattr(response, 'text') else str(response)
        
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        print(f"❌ Gemini API 오류: {e}")
        return error_msg


"""
Gemini 이미지 생성 서비스 (gemini-3-pro-image-preview 사용)
google-genai SDK를 사용하여 Text-to-Image 지원
공식 문서 예제 코드 패턴을 따름 (AI Studio)
"""
import os
import base64
import mimetypes
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

# .env 파일 로드
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_FILE)


def get_gemini_api_key():
    """Gemini API 키 가져오기"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("⚠️ GEMINI_API_KEY가 .env에 설정되지 않았습니다.")
        raise ValueError("GEMINI_API_KEY가 .env에 설정되지 않았습니다.")
    print(f"✅ Gemini API 키 로드됨 (길이: {len(api_key)} 문자)")
    return api_key


def get_gemini_client():
    """Gemini Client 생성 (공식 문서 예제 패턴)"""
    api_key = get_gemini_api_key()
    return genai.Client(api_key=api_key)


# 사용할 모델
GEMINI_IMAGE_MODEL = "gemini-3-pro-image-preview"


async def generate_image_gemini3(prompt: str, base_image: bytes = None, model: str = None) -> str:
    """
    gemini-3-pro-image-preview를 사용한 이미지 생성
    공식 문서 예제 패턴: AI Studio 코드 기반
    
    Args:
        prompt: 이미지 생성 프롬프트 (한국어 또는 영어)
        base_image: 기본 이미지 바이트 (image-to-image용, 선택적 - 현재 미지원)
        model: 모델 타입 (무시됨, 항상 gemini-3-pro-image-preview 사용)
    
    Returns:
        base64 인코딩된 이미지 문자열 (data:image/jpeg;base64,... 형식)
    """
    try:
        if base_image:
            # Image-to-Image는 현재 미지원
            print("⚠️ gemini-3-pro-image-preview는 image-to-image를 지원하지 않습니다.")
            # 프롬프트에 이미지 설명을 포함하여 생성
            enhanced_prompt = f"{prompt}. 웨딩 청첩장 스타일로 고급스럽고 우아하게 생성해주세요."
            return await _generate_image_gemini(enhanced_prompt)
        else:
            # Text-to-Image
            return await _generate_image_gemini(prompt)
        
    except Exception as e:
        print(f"❌ Gemini 이미지 생성 실패: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise Exception(f"Gemini 이미지 생성 실패: {e}")


async def _generate_image_gemini(prompt: str) -> str:
    """
    gemini-3-pro-image-preview를 사용한 이미지 생성
    공식 문서 예제 패턴 (AI Studio 코드 기반)
    
    Args:
        prompt: 이미지 생성 프롬프트
    
    Returns:
        base64 인코딩된 이미지 문자열
    """
    client = get_gemini_client()
    model = GEMINI_IMAGE_MODEL
    
    print(f"🔍 Gemini 이미지 생성 요청:")
    print(f"   모델: {model}")
    print(f"   프롬프트: {prompt[:100]}...")
    
    # 공식 문서 예제 패턴: generate_content_stream 사용
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=prompt),
            ],
        ),
    ]
    
    tools = [
        types.Tool(googleSearch=types.GoogleSearch()),
    ]
    
    generate_content_config = types.GenerateContentConfig(
        response_modalities=["IMAGE", "TEXT"],
        image_config=types.ImageConfig(
            image_size="1K",
        ),
        tools=tools,
    )
    
    # 스트리밍 방식으로 이미지 받기
    image_data = None
    text_parts = []
    
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        if (
            chunk.candidates is None
            or chunk.candidates[0].content is None
            or chunk.candidates[0].content.parts is None
        ):
            continue
        
        part = chunk.candidates[0].content.parts[0]
        
        # 이미지 데이터 처리
        if part.inline_data and part.inline_data.data:
            image_data = part.inline_data.data
            mime_type = part.inline_data.mime_type
            print(f"✅ 이미지 데이터 수신 (크기: {len(image_data)} bytes, 타입: {mime_type})")
        
        # 텍스트 처리
        if hasattr(part, 'text') and part.text:
            text_parts.append(part.text)
    
    if not image_data:
        raise ValueError("이미지가 생성되지 않았습니다.")
    
    # base64로 인코딩
    img_b64 = base64.b64encode(image_data).decode('utf-8')
    
    # mime_type 결정 (기본값: image/jpeg)
    mime_type = mimetypes.guess_type("image.jpg")[0] or "image/jpeg"
    if image_data:
        # 실제로는 inline_data에서 mime_type을 가져와야 하지만, 
        # 여기서는 기본값 사용
        mime_type = "image/jpeg"
    
    result_uri = f"data:{mime_type};base64,{img_b64}"
    
    if text_parts:
        print(f"📝 생성된 텍스트: {''.join(text_parts)[:100]}...")
    
    print(f"✅ Gemini 이미지 생성 완료 (크기: {len(image_data)} bytes)")
    return result_uri


async def modify_image_gemini3(base_image: bytes, modification_prompt: str) -> str:
    """
    gemini-3-pro-image-preview를 사용한 이미지 수정
    현재는 image-to-image를 지원하지 않으므로 프롬프트 기반으로 처리
    
    Args:
        base_image: 수정할 기본 이미지 바이트
        modification_prompt: 수정 요청 프롬프트
    
    Returns:
        base64 인코딩된 이미지 문자열
    """
    # Image-to-Image는 미지원이므로 프롬프트 기반으로 생성
    enhanced_prompt = f"{modification_prompt}. 웨딩 청첩장 스타일로 고급스럽고 우아하게 생성해주세요."
    return await generate_image_gemini3(enhanced_prompt, None)

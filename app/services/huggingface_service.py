"""
HuggingFace Inference API를 사용한 이미지 생성 서비스
공식 문서 예제 코드 패턴을 따름
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from PIL import Image
from io import BytesIO
import base64

# .env 파일 로드
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_FILE)


def get_hf_api_key():
    """HuggingFace API 키 가져오기 (HF_TOKEN 또는 HUGGINGFACE_API_KEY)"""
    api_key = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_API_KEY")
    if not api_key:
        print("⚠️ HF_TOKEN 또는 HUGGINGFACE_API_KEY가 .env에 설정되지 않았습니다.")
        raise ValueError("HF_TOKEN 또는 HUGGINGFACE_API_KEY가 .env에 설정되지 않았습니다.")
    print(f"✅ HuggingFace API 키 로드됨 (길이: {len(api_key)} 문자)")
    return api_key


def get_hf_client_nscale():
    """HuggingFace InferenceClient 생성 (nscale provider - SDXL용)"""
    api_key = get_hf_api_key()
    return InferenceClient(
        provider="nscale",
        api_key=api_key
    )


def get_hf_client_fal():
    """HuggingFace InferenceClient 생성 (fal-ai provider - FLUX.2-dev용)"""
    api_key = get_hf_api_key()
    return InferenceClient(
        provider="fal-ai",
        api_key=api_key
    )


def get_hf_client_nebius():
    """HuggingFace InferenceClient 생성 (nebius provider - FLUX.1-dev용)"""
    api_key = get_hf_api_key()
    return InferenceClient(
        provider="nebius",
        api_key=api_key
    )


def get_hf_client_default():
    """HuggingFace InferenceClient (기본 provider)"""
    api_key = get_hf_api_key()
    return InferenceClient(
        token=api_key
    )


async def generate_image_sdxl(prompt: str) -> str:
    """
    Stable Diffusion XL Base를 사용한 텍스트→이미지 생성
    공식 문서 예제 패턴: nscale provider 사용
    
    Args:
        prompt: 이미지 생성 프롬프트 (영어)
    
    Returns:
        base64 인코딩된 이미지 문자열 (data:image/png;base64,...)
    """
    try:
        client = get_hf_client_nscale()
        
        # output is a PIL.Image object (공식 문서 예제와 동일)
        image = client.text_to_image(
            prompt,
            model="stabilityai/stable-diffusion-xl-base-1.0"
        )
        
        # base64로 인코딩
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
        
    except Exception as e:
        print(f"❌ SDXL 이미지 생성 실패: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise Exception(f"SDXL 이미지 생성 실패: {e}")


async def generate_image_flux(prompt: str, base_image: bytes = None) -> str:
    """
    FLUX.2-dev를 사용한 이미지 생성
    공식 문서 예제 패턴: fal-ai provider 사용
    
    Args:
        prompt: 이미지 생성 프롬프트 (영어)
        base_image: 기본 이미지 바이트 (image-to-image용, 선택적)
    
    Returns:
        base64 인코딩된 이미지 문자열 (data:image/png;base64,...)
    """
    try:
        client = get_hf_client_fal()
        
        if base_image:
            # Image-to-Image (공식 문서 예제 패턴)
            # output is a PIL.Image object
            image = client.image_to_image(
                base_image,
                prompt=prompt,
                model="black-forest-labs/FLUX.2-dev"
            )
        else:
            # Text-to-Image
            image = client.text_to_image(
                prompt,
                model="black-forest-labs/FLUX.2-dev"
            )
        
        # base64로 인코딩
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
        
    except Exception as e:
        print(f"❌ FLUX 이미지 생성 실패: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise Exception(f"FLUX 이미지 생성 실패: {e}")


async def generate_image_flux_schnell(prompt: str) -> str:
    """
    FLUX.1-schnell을 사용한 텍스트→이미지 생성 (빠른 버전)
    fal-ai provider 사용
    
    Args:
        prompt: 이미지 생성 프롬프트 (영어)
    
    Returns:
        base64 인코딩된 이미지 문자열
    """
    try:
        client = get_hf_client_fal()
        
        image = client.text_to_image(
            prompt,
            model="black-forest-labs/flux-schnell"
        )
        
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
        
    except Exception as e:
        print(f"❌ FLUX Schnell 이미지 생성 실패: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise Exception(f"FLUX Schnell 이미지 생성 실패: {e}")


async def generate_image_flux_dev(prompt: str) -> str:
    """
    FLUX.1-dev를 사용한 텍스트→이미지 생성
    공식 문서 예제 패턴: nebius provider 사용
    
    Args:
        prompt: 이미지 생성 프롬프트 (영어)
    
    Returns:
        base64 인코딩된 이미지 문자열
    """
    try:
        client = get_hf_client_nebius()
        
        # output is a PIL.Image object (공식 문서 예제와 동일)
        image = client.text_to_image(
            prompt,
            model="black-forest-labs/FLUX.1-dev"
        )
        
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
        
    except Exception as e:
        print(f"❌ FLUX.1-dev 이미지 생성 실패: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise Exception(f"FLUX.1-dev 이미지 생성 실패: {e}")


async def generate_image_playground_v25(prompt: str) -> str:
    """
    Playground v2.5를 사용한 텍스트→이미지 생성
    
    Args:
        prompt: 이미지 생성 프롬프트 (영어)
    
    Returns:
        base64 인코딩된 이미지 문자열
    """
    try:
        client = get_hf_client_default()
        
        image = client.text_to_image(
            prompt,
            model="playgroundai/playground-v2.5-1024px-aesthetic"
        )
        
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
        
    except Exception as e:
        print(f"❌ Playground v2.5 이미지 생성 실패: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise Exception(f"Playground v2.5 이미지 생성 실패: {e}")


async def generate_image_sd15(prompt: str) -> str:
    """
    Stable Diffusion 1.5를 사용한 텍스트→이미지 생성
    
    Args:
        prompt: 이미지 생성 프롬프트 (영어)
    
    Returns:
        base64 인코딩된 이미지 문자열
    """
    try:
        client = get_hf_client_default()
        
        image = client.text_to_image(
            prompt,
            model="runwayml/stable-diffusion-v1-5"
        )
        
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
        
    except Exception as e:
        print(f"❌ SD 1.5 이미지 생성 실패: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise Exception(f"SD 1.5 이미지 생성 실패: {e}")


async def generate_image_realistic_vision(prompt: str) -> str:
    """
    Realistic Vision을 사용한 텍스트→이미지 생성 (사실적인 이미지)
    
    Args:
        prompt: 이미지 생성 프롬프트 (영어)
    
    Returns:
        base64 인코딩된 이미지 문자열
    """
    try:
        client = get_hf_client_default()
        
        image = client.text_to_image(
            prompt,
            model="SG161222/Realistic_Vision_V5.1_noVAE"
        )
        
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
        
    except Exception as e:
        print(f"❌ Realistic Vision 이미지 생성 실패: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise Exception(f"Realistic Vision 이미지 생성 실패: {e}")


async def generate_image_dreamshaper(prompt: str) -> str:
    """
    DreamShaper를 사용한 텍스트→이미지 생성
    
    Args:
        prompt: 이미지 생성 프롬프트 (영어)
    
    Returns:
        base64 인코딩된 이미지 문자열
    """
    try:
        client = get_hf_client_default()
        
        image = client.text_to_image(
            prompt,
            model="Lykon/DreamShaper"
        )
        
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
        
    except Exception as e:
        print(f"❌ DreamShaper 이미지 생성 실패: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise Exception(f"DreamShaper 이미지 생성 실패: {e}")


async def generate_image_flux_image_to_image(base_image: bytes, prompt: str) -> str:
    """
    FLUX.2-dev를 사용한 이미지→이미지 변환
    공식 문서 예제 패턴: fal-ai provider 사용
    
    Args:
        base_image: 기본 이미지 바이트
        prompt: 수정 프롬프트 (영어)
    
    Returns:
        base64 인코딩된 이미지 문자열
    """
    try:
        client = get_hf_client_fal()
        
        # output is a PIL.Image object (공식 문서 예제와 동일)
        image = client.image_to_image(
            base_image,
            prompt=prompt,
            model="black-forest-labs/FLUX.2-dev"
        )
        
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
        
    except Exception as e:
        print(f"❌ FLUX 이미지→이미지 변환 실패: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise Exception(f"FLUX 이미지→이미지 변환 실패: {e}")

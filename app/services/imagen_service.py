"""
Imagen 이미지 생성 서비스
공식 문서: https://ai.google.dev/gemini-api/docs/imagen
"""
import base64
from io import BytesIO
from PIL import Image
from google import genai
from google.genai import types
from app.core.config import GEMINI_API_KEY

# Imagen 모델명
# 사용자 요청: imagen-3.0-generate-002
# 사용 가능한 모델: imagen-4.0-generate-001, imagen-4.0-ultra-generate-001 등
# 일단 사용자 요청 모델명 사용, 오류 시 사용 가능한 모델 목록 표시
IMAGEN_MODEL = "imagen-3.0-generate-002"  # Imagen 3.0 (사용자 요청 모델)


async def generate_image_imagen(
    prompt: str,
    number_of_images: int = 4,
    image_size: str = "1K",  # "1K" or "2K"
    aspect_ratio: str = "1:1",  # "1:1", "3:4", "4:3", "9:16", "16:9"
    person_generation: str = "allow_adult"  # "dont_allow", "allow_adult", "allow_all"
) -> list[str]:
    """
    Imagen을 사용한 이미지 생성 (text-to-image)
    
    Args:
        prompt: 이미지 생성 프롬프트 (영어, 최대 480 토큰)
        number_of_images: 생성할 이미지 수 (1~4, 기본값: 4)
        image_size: 이미지 크기 ("1K" 또는 "2K", 기본값: "1K")
        aspect_ratio: 가로세로 비율 ("1:1", "3:4", "4:3", "9:16", "16:9", 기본값: "1:1")
        person_generation: 사람 이미지 생성 허용 설정
            - "dont_allow": 사람 이미지 생성 차단
            - "allow_adult": 성인 이미지만 생성 (기본값)
            - "allow_all": 성인과 어린이 모두 포함
        use_ultra: True면 Imagen 4.0 Ultra 사용 (고품질, 한 번에 하나만 생성)
    
    Returns:
        base64 인코딩된 이미지 문자열 리스트
    """
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not configured in .env")
    
    try:
        # Imagen 클라이언트 초기화
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        # Imagen 3.0 모델 사용
        model = IMAGEN_MODEL
        
        # number_of_images 범위 확인 (1~4)
        number_of_images = max(1, min(4, number_of_images))
        
        print(f"🔍 Imagen 이미지 생성 요청:")
        print(f"   모델: {model}")
        print(f"   프롬프트: {prompt[:100]}...")
        print(f"   이미지 수: {number_of_images}")
        print(f"   크기: {image_size}")
        print(f"   가로세로 비율: {aspect_ratio}")
        print(f"   사람 생성: {person_generation}")
        
        # Imagen API 호출
        response = client.models.generate_images(
            model=model,
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=number_of_images,
                image_size=image_size,
                aspect_ratio=aspect_ratio,
                person_generation=person_generation
            )
        )
        
        print(f"✅ Imagen 응답 수신: {len(response.generated_images)}개 이미지")
        
        # 생성된 이미지들을 base64로 변환
        base64_images = []
        for i, generated_image in enumerate(response.generated_images):
            try:
                # generated_image.image는 PIL Image 객체
                image = generated_image.image
                
                # PIL Image를 base64로 변환
                img_buffer = BytesIO()
                image.save(img_buffer, format='PNG')
                img_bytes = img_buffer.getvalue()
                img_b64 = base64.b64encode(img_bytes).decode('utf-8')
                
                base64_images.append(f"data:image/png;base64,{img_b64}")
                print(f"✅ 이미지 {i+1}/{len(response.generated_images)} 변환 완료")
            except Exception as img_error:
                print(f"⚠️ 이미지 {i+1} 변환 실패: {img_error}")
                continue
        
        if not base64_images:
            raise ValueError("No images were successfully generated")
        
        return base64_images
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Imagen 이미지 생성 실패: {type(e).__name__}: {e}")
        
        # 모델을 찾을 수 없는 경우 사용 가능한 모델 목록 조회 시도
        if "not found" in error_msg.lower() or "404" in error_msg:
            try:
                models = client.models.list()
                imagen_models = [m.name.replace("models/", "") for m in models if 'imagen' in m.name.lower()]
                error_msg += f"\n사용 가능한 Imagen 모델: {', '.join(imagen_models)}"
                print(f"🔍 사용 가능한 Imagen 모델: {imagen_models}")
            except:
                pass
        
        import traceback
        traceback.print_exc()
        raise Exception(f"Imagen 이미지 생성 실패: {error_msg}")


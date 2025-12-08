"""
청첩장 이미지 생성 라우터
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import base64

from app.services.huggingface_service import (
    generate_image_sdxl, 
    generate_image_flux,
    generate_image_flux_schnell,
    generate_image_playground_v25,
    generate_image_sd15,
    generate_image_realistic_vision,
    generate_image_dreamshaper,
    generate_image_flux_image_to_image
)
from app.services.gemini_image_service import generate_image_gemini3, modify_image_gemini3

router = APIRouter(tags=["Image Generation"])


class ImageGenerateRequest(BaseModel):
    prompt: str  # 영어 프롬프트
    model: str = "sdxl"  # sdxl, flux, flux-schnell, playground, sd15, realistic-vision, dreamshaper, gemini
    base_image_b64: Optional[str] = None  # base64 인코딩된 이미지 (flux, gemini용)


class ImageModifyRequest(BaseModel):
    base_image_b64: str
    modification_prompt: str  # 수정 요청 (영어)
    model: str = "flux"  # flux 또는 gemini


@router.post("/image/generate")
async def generate_invitation_image(request: ImageGenerateRequest):
    """
    청첩장 이미지 생성
    
    Models (Text-to-Image):
    - sdxl: Stable Diffusion XL (무료, 텍스트만, nscale provider)
    - flux: FLUX.2-dev (무료, 텍스트 또는 이미지+텍스트, fal-ai provider)
    - flux-schnell: FLUX.1-schnell (무료, 빠른 생성, 텍스트만, fal-ai provider)
    - playground: Playground v2.5 (무료, 고품질, 텍스트만)
    - sd15: Stable Diffusion 1.5 (무료, 텍스트만)
    - realistic-vision: Realistic Vision V5.1 (무료, 사실적인 이미지, 텍스트만)
    - dreamshaper: DreamShaper (무료, 다양한 스타일, 텍스트만)
    - gemini: gemini-3-pro-image-preview (유료, 텍스트 기반 이미지 생성)
    
    Image-to-Image 지원 모델:
    - flux: FLUX.2-dev만 지원
    """
    try:
        base_image = None
        if request.base_image_b64:
            # base64 디코딩
            image_data = request.base_image_b64.split(",")[1] if "," in request.base_image_b64 else request.base_image_b64
            base_image = base64.b64decode(image_data)
        
        if request.model == "sdxl":
            # Stable Diffusion XL (텍스트만)
            if base_image:
                raise HTTPException(
                    status_code=400,
                    detail="SDXL model does not support image-to-image"
                )
            image_b64 = await generate_image_sdxl(request.prompt)
            
        elif request.model == "flux":
            # FLUX.2-dev (텍스트 또는 이미지+텍스트)
            image_b64 = await generate_image_flux(request.prompt, base_image)
            
        elif request.model == "flux-schnell":
            # FLUX.1-schnell (텍스트만, 빠른 생성)
            if base_image:
                raise HTTPException(
                    status_code=400,
                    detail="FLUX Schnell model does not support image-to-image. Use 'flux' model instead."
                )
            image_b64 = await generate_image_flux_schnell(request.prompt)
            
        elif request.model == "playground":
            # Playground v2.5 (텍스트만)
            if base_image:
                raise HTTPException(
                    status_code=400,
                    detail="Playground v2.5 model does not support image-to-image"
                )
            image_b64 = await generate_image_playground_v25(request.prompt)
            
        elif request.model == "sd15":
            # Stable Diffusion 1.5 (텍스트만)
            if base_image:
                raise HTTPException(
                    status_code=400,
                    detail="SD 1.5 model does not support image-to-image"
                )
            image_b64 = await generate_image_sd15(request.prompt)
            
        elif request.model == "realistic-vision":
            # Realistic Vision (텍스트만)
            if base_image:
                raise HTTPException(
                    status_code=400,
                    detail="Realistic Vision model does not support image-to-image"
                )
            image_b64 = await generate_image_realistic_vision(request.prompt)
            
        elif request.model == "dreamshaper":
            # DreamShaper (텍스트만)
            if base_image:
                raise HTTPException(
                    status_code=400,
                    detail="DreamShaper model does not support image-to-image"
                )
            image_b64 = await generate_image_dreamshaper(request.prompt)
            
        elif request.model == "gemini":
            # gemini-3-pro-image-preview (유료, text-to-image 지원)
            try:
                image_b64 = await generate_image_gemini3(request.prompt, base_image)
            except ValueError as e:
                # API 키 등 설정 오류
                raise HTTPException(
                    status_code=400,
                    detail=f"Gemini 이미지 생성 설정 오류: {str(e)}"
                )
            except Exception as e:
                # 기타 오류
                error_msg = str(e)
                print(f"❌ Gemini 이미지 생성 실패: {type(e).__name__}: {error_msg}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Gemini 이미지 생성 실패: {error_msg}"
                )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown model: {request.model}. Available models: sdxl, flux, flux-schnell, playground, sd15, realistic-vision, dreamshaper, gemini"
            )
        
        return {
            "message": "image_generated",
            "data": {
                "image_b64": image_b64,
                "model": request.model
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/image/modify")
async def modify_invitation_image(request: ImageModifyRequest):
    """
    청첩장 이미지 수정 (Image-to-Image)
    
    Models:
    - flux: FLUX.2-dev (무료, fal-ai provider)
    - gemini: gemini-3-pro-image-preview (유료, 텍스트 기반 이미지 생성)
    """
    try:
        # base64 디코딩
        image_data = request.base_image_b64.split(",")[1] if "," in request.base_image_b64 else request.base_image_b64
        base_image = base64.b64decode(image_data)
        
        if request.model == "flux":
            # FLUX.2-dev를 사용한 이미지 수정
            image_b64 = await generate_image_flux_image_to_image(base_image, request.modification_prompt)
        elif request.model == "gemini":
            # gemini-3-pro-image-preview (유료, image-to-image는 프롬프트 기반으로 대체)
            try:
                # gemini-3-pro-image-preview는 image-to-image를 직접 지원하지 않으므로 프롬프트 기반 생성
                image_b64 = await modify_image_gemini3(base_image, request.modification_prompt)
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Gemini 이미지 수정 실패: {str(e)}"
                )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown model: {request.model}. Available models for modification: flux, gemini"
            )
        
        return {
            "message": "image_modified",
            "data": {
                "image_b64": image_b64,
                "model": request.model
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/image/models")
async def get_available_models():
    """
    사용 가능한 이미지 생성 모델 목록 조회
    """
    return {
        "message": "models_listed",
        "data": {
            "text_to_image": [
                {
                    "id": "sdxl",
                    "name": "Stable Diffusion XL",
                    "provider": "nscale",
                    "supports_image_to_image": False,
                    "description": "고품질 텍스트→이미지 생성"
                },
                {
                    "id": "flux",
                    "name": "FLUX.2-dev",
                    "provider": "fal-ai",
                    "supports_image_to_image": True,
                    "description": "최신 FLUX 모델, 텍스트 및 이미지→이미지 지원"
                },
                {
                    "id": "flux-schnell",
                    "name": "FLUX.1-schnell",
                    "provider": "fal-ai",
                    "supports_image_to_image": False,
                    "description": "빠른 생성 속도의 FLUX 모델"
                },
                {
                    "id": "playground",
                    "name": "Playground v2.5",
                    "provider": "default",
                    "supports_image_to_image": False,
                    "description": "고품질 미학적 이미지 생성"
                },
                {
                    "id": "sd15",
                    "name": "Stable Diffusion 1.5",
                    "provider": "default",
                    "supports_image_to_image": False,
                    "description": "기본 SD 모델, 빠른 생성"
                },
                {
                    "id": "realistic-vision",
                    "name": "Realistic Vision V5.1",
                    "provider": "default",
                    "supports_image_to_image": False,
                    "description": "사실적인 이미지 생성에 특화"
                },
                {
                    "id": "dreamshaper",
                    "name": "DreamShaper",
                    "provider": "default",
                    "supports_image_to_image": False,
                    "description": "다양한 스타일의 이미지 생성"
                }
            ],
            "image_to_image": [
                {
                    "id": "flux",
                    "name": "FLUX.2-dev",
                    "provider": "fal-ai",
                    "description": "이미지→이미지 변환 지원"
                }
            ],
            "premium": [
                {
                    "id": "gemini",
                    "name": "Gemini 3 Pro Image Preview",
                    "provider": "google",
                    "supports_image_to_image": False,
                    "description": "유료 서비스, gemini-3-pro-image-preview 모델 사용"
                }
            ]
        }
    }

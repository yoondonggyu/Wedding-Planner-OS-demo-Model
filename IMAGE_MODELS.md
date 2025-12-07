# 이미지 생성 모델 가이드

## 사용 가능한 모델 목록

### Text-to-Image 모델 (텍스트→이미지)

#### 1. Stable Diffusion XL (sdxl)
- **Provider**: nscale
- **모델**: `stabilityai/stable-diffusion-xl-base-1.0`
- **특징**: 고품질 이미지 생성
- **Image-to-Image**: ❌ 지원 안 함
- **사용 예시**:
```python
# nscale provider 사용
client = InferenceClient(provider="nscale", api_key=os.environ["HF_TOKEN"])
image = client.text_to_image("Astronaut riding a horse", model="stabilityai/stable-diffusion-xl-base-1.0")
```

#### 2. FLUX.2-dev (flux)
- **Provider**: fal-ai
- **모델**: `black-forest-labs/FLUX.2-dev`
- **특징**: 최신 FLUX 모델, 최고 품질
- **Image-to-Image**: ✅ 지원
- **사용 예시**:
```python
# fal-ai provider 사용
client = InferenceClient(provider="fal-ai", api_key=os.environ["HF_TOKEN"])

# Text-to-Image
image = client.text_to_image("Elegant wedding invitation", model="black-forest-labs/FLUX.2-dev")

# Image-to-Image
with open("base_image.png", "rb") as f:
    input_image = f.read()
image = client.image_to_image(input_image, prompt="Turn into wedding invitation", model="black-forest-labs/FLUX.2-dev")
```

#### 3. FLUX.1-schnell (flux-schnell)
- **Provider**: fal-ai
- **모델**: `black-forest-labs/flux-schnell`
- **특징**: 빠른 생성 속도
- **Image-to-Image**: ❌ 지원 안 함
- **사용 예시**:
```python
client = InferenceClient(provider="fal-ai", api_key=os.environ["HF_TOKEN"])
image = client.text_to_image("Wedding invitation design", model="black-forest-labs/flux-schnell")
```

#### 4. Playground v2.5 (playground)
- **Provider**: default (HuggingFace)
- **모델**: `playgroundai/playground-v2.5-1024px-aesthetic`
- **특징**: 고품질 미학적 이미지
- **Image-to-Image**: ❌ 지원 안 함
- **사용 예시**:
```python
client = InferenceClient(token=os.environ["HF_TOKEN"])
image = client.text_to_image("Beautiful wedding card", model="playgroundai/playground-v2.5-1024px-aesthetic")
```

#### 5. Stable Diffusion 1.5 (sd15)
- **Provider**: default (HuggingFace)
- **모델**: `runwayml/stable-diffusion-v1-5`
- **특징**: 기본 SD 모델, 빠른 생성
- **Image-to-Image**: ❌ 지원 안 함
- **사용 예시**:
```python
client = InferenceClient(token=os.environ["HF_TOKEN"])
image = client.text_to_image("Wedding invitation", model="runwayml/stable-diffusion-v1-5")
```

#### 6. Realistic Vision V5.1 (realistic-vision)
- **Provider**: default (HuggingFace)
- **모델**: `SG161222/Realistic_Vision_V5.1_noVAE`
- **특징**: 사실적인 이미지 생성에 특화
- **Image-to-Image**: ❌ 지원 안 함
- **사용 예시**:
```python
client = InferenceClient(token=os.environ["HF_TOKEN"])
image = client.text_to_image("Realistic wedding photo", model="SG161222/Realistic_Vision_V5.1_noVAE")
```

#### 7. DreamShaper (dreamshaper)
- **Provider**: default (HuggingFace)
- **모델**: `Lykon/DreamShaper`
- **특징**: 다양한 스타일의 이미지 생성
- **Image-to-Image**: ❌ 지원 안 함
- **사용 예시**:
```python
client = InferenceClient(token=os.environ["HF_TOKEN"])
image = client.text_to_image("Artistic wedding invitation", model="Lykon/DreamShaper")
```

### Image-to-Image 모델 (이미지→이미지)

#### FLUX.2-dev (flux)
- **Provider**: fal-ai
- **모델**: `black-forest-labs/FLUX.2-dev`
- **특징**: 이미지 수정 및 변환
- **사용 예시**:
```python
client = InferenceClient(provider="fal-ai", api_key=os.environ["HF_TOKEN"])
with open("base_image.png", "rb") as f:
    input_image = f.read()
image = client.image_to_image(input_image, prompt="Modify the design", model="black-forest-labs/FLUX.2-dev")
```

### Premium 모델 (유료)

#### Gemini 3.0 Pro (gemini)
- **Provider**: Google
- **특징**: 고품질 이미지 생성 및 수정
- **Image-to-Image**: ✅ 지원 (미구현)
- **상태**: API 준비 대기 중

## API 사용법

### 모델 목록 조회
```bash
GET /api/image/models
```

### 이미지 생성
```bash
POST /api/image/generate
Content-Type: application/json

{
  "prompt": "Elegant wedding invitation card with pink flowers",
  "model": "flux",  # sdxl, flux, flux-schnell, playground, sd15, realistic-vision, dreamshaper
  "base_image_b64": null  # 선택사항 (flux만 지원)
}
```

### 이미지 수정
```bash
POST /api/image/modify
Content-Type: application/json

{
  "base_image_b64": "data:image/png;base64,...",
  "modification_prompt": "Make it more colorful",
  "model": "flux"  # flux 또는 gemini
}
```

## 모델 선택 가이드

### 고품질이 필요한 경우
- **FLUX.2-dev** (flux): 최고 품질, 이미지 수정 가능
- **Playground v2.5** (playground): 미학적 고품질

### 빠른 생성이 필요한 경우
- **FLUX.1-schnell** (flux-schnell): 빠른 생성
- **Stable Diffusion 1.5** (sd15): 기본 모델, 빠름

### 사실적인 이미지가 필요한 경우
- **Realistic Vision** (realistic-vision): 사실적인 스타일

### 다양한 스타일이 필요한 경우
- **DreamShaper** (dreamshaper): 다양한 스타일 지원

### 이미지 수정이 필요한 경우
- **FLUX.2-dev** (flux): 유일하게 Image-to-Image 지원

## 환경 변수 설정

`.env` 파일에 다음을 추가:
```env
HF_TOKEN=your_huggingface_token_here
```

HuggingFace 토큰은 [HuggingFace Settings](https://huggingface.co/settings/tokens)에서 발급받을 수 있습니다.


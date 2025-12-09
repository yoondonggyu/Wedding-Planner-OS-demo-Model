# AI Model Serving API

Wedding OS 프로젝트의 AI 모델 서빙 서버입니다. 청첩장 이미지 생성, 텍스트 감성 분석, LLM 채팅 등 다양한 AI 기능을 제공합니다.

## 📋 프로젝트 개요

Wedding OS Model Server는 FastAPI 기반으로 구축된 AI 모델 서빙 API입니다. 주요 기능은 다음과 같습니다:

1. **청첩장 이미지 생성**: Gemini 3 Pro Image Preview 및 HuggingFace 모델을 활용한 AI 이미지 생성
2. **이미지 수정**: 멀티모달 입력(인물 사진, 스타일 참고 사진)을 지원하는 이미지 수정 기능
3. **감성 분석**: Naive Bayes 기반 텍스트 감성 분석 (positive/negative)
4. **채팅 모델**: Ollama 기반 LLM 채팅 (gemma3:4b 등)

## 🛠 기술 스택

- **Framework**: FastAPI
- **AI Models**:
  - **Google Gemini 3 Pro Image Preview**: 유료 이미지 생성 모델 (일일 5회 제한, 테스트 계정 제한 해제)
  - **HuggingFace Models**: 무료 이미지 생성 모델 (FLUX.2-dev, Stable Diffusion XL 등)
  - **Ollama**: 로컬 LLM (gemma3:4b 등)
- **Python**: 3.10+
- **Package Manager**: pip

## 📁 프로젝트 구조

```
3.Wedding_OS_model/
├── app/
│   ├── main.py                     # FastAPI 앱 진입점
│   ├── routers/
│   │   ├── image_generation_routes.py  # 청첩장 이미지 생성/수정 API
│   │   ├── chat_routes.py          # 채팅 API 라우터
│   │   ├── sentiment_routes.py     # 감성 분석 API 라우터
│   │   ├── predict_routes.py       # 이미지 분류 API 라우터 (레거시)
│   │   └── gemini_routes.py        # Gemini API 라우터
│   ├── services/
│   │   ├── gemini_image_service.py     # Gemini 이미지 생성 서비스
│   │   ├── huggingface_service.py      # HuggingFace 이미지 생성 서비스
│   │   ├── chat_service.py         # 채팅 모델 서비스 (Ollama)
│   │   ├── sentiment_service.py    # 감성 분석 모델 서비스
│   │   └── model_service.py        # 이미지 분류 모델 서비스 (레거시)
│   └── schemas/
│       └── chat_schema.py           # Pydantic 스키마
├── models/
│   └── sentiment.py                # 감성 분석 모델 구현
├── assets/
│   └── labels.txt                  # 클래스 레이블 (레거시)
├── requirements.txt                # 의존성 패키지
├── GEMINI_SETUP.md                 # Gemini API 설정 가이드
└── IMAGE_MODELS.md                 # 이미지 생성 모델 상세 정보
```

## 🚀 시작하기

### 1. 가상환경 활성화

```bash
conda activate env_python310
```

### 2. 필요한 패키지 설치

```bash
# requirements.txt 사용 (권장)
pip install -r requirements.txt
```

**주요 의존성**:
- `fastapi`: FastAPI 프레임워크
- `uvicorn`: ASGI 서버
- `google-genai`: Google Gemini API SDK
- `huggingface-hub`: HuggingFace Inference API
- `httpx`: 비동기 HTTP 클라이언트
- `pillow`: 이미지 처리
- `ollama`: Ollama LLM 클라이언트

### 3. 환경 변수 설정

`.env` 파일 생성:

```env
# Google Gemini API (필수)
GOOGLE_API_KEY=your-google-api-key-here

# HuggingFace API (선택사항)
HF_TOKEN=your-huggingface-token-here
HUGGINGFACE_API_KEY=your-huggingface-api-key-here
```

### 4. 서버 실행

```bash
cd /Users/yoon-dong-gyu/kakao_bootcamp/1.Wedding_OS_Project/3.Wedding_OS_model

# 서버 실행 (기본 포트: 8102)
uvicorn app.main:app --host 0.0.0.0 --port 8102 --reload
```

**참고**:
- 기본 포트는 **8102**입니다
- Backend API (8101)와 통신하여 사용됩니다
- 서버가 `http://localhost:8102`에서 실행됩니다

## 🎨 주요 기능

### 1. 청첩장 이미지 생성

#### 지원 모델

**유료 모델**:
- `gemini`: Gemini 3 Pro Image Preview (Google)
  - 고품질 이미지 생성
  - 멀티모달 입력 지원 (인물 사진, 스타일 참고 사진)
  - 일일 5회 제한 (테스트 계정 제한 해제)

**무료 모델** (HuggingFace):
- `sdxl`: Stable Diffusion XL (nscale provider)
- `flux`: FLUX.2-dev (fal-ai provider, 이미지→이미지 지원)
- `flux-schnell`: FLUX.1-schnell (fal-ai provider, 빠른 생성)
- `playground`: Playground v2.5
- `sd15`: Stable Diffusion 1.5
- `realistic-vision`: Realistic Vision V5.1
- `dreamshaper`: DreamShaper

#### API 엔드포인트

**이미지 생성**:
```bash
POST /api/image/generate
{
  "prompt": "Elegant wedding invitation card design, romantic style",
  "model": "gemini",
  "person_image_b64": "data:image/jpeg;base64,...",  # 선택사항
  "style_images_b64": ["data:image/jpeg;base64,..."]  # 선택사항 (최대 3장)
}
```

**이미지 수정**:
```bash
POST /api/image/modify
{
  "base_image_b64": "data:image/jpeg;base64,...",
  "modification_prompt": "Make the colors brighter and add flowers",
  "model": "gemini",
  "person_image_b64": "data:image/jpeg;base64,...",  # 선택사항
  "style_images_b64": ["data:image/jpeg;base64,..."]  # 선택사항 (최대 3장)
}
```

**사용 가능한 모델 목록 조회**:
```bash
GET /api/image/models
```

### 2. 텍스트 감성 분석

Naive Bayes 기반 영어 텍스트 감성 분석 (positive/negative)

```bash
POST /api/sentiment
{
  "text": "I really love this product!",
  "explain": true  # 토큰별 영향도 포함 여부
}
```

### 3. 채팅 API (Ollama)

LLM 기반 대화형 채팅 (스트리밍 지원)

```bash
POST /api/chat
{
  "message": "Hello, how are you?",
  "model": "gemma3:4b"  # 선택사항
}
```

### 4. 이미지 분류 (레거시)

Keras 기반 강아지/고양이 분류 (레거시 기능)

```bash
POST /api/predict
# multipart/form-data
file: <image_file>
```

## 🔧 API 사용 예시

### 청첩장 이미지 생성 (Gemini)

```bash
curl -X POST "http://localhost:8102/api/image/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Elegant wedding invitation card with floral border, soft pastel colors",
    "model": "gemini"
  }'
```

**응답**:
```json
{
  "message": "image_generated",
  "data": {
    "image_b64": "data:image/jpeg;base64,...",
    "model": "gemini"
  }
}
```

### 멀티모달 이미지 생성 (인물 사진 + 스타일 참고)

```bash
curl -X POST "http://localhost:8102/api/image/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a beautiful wedding invitation",
    "model": "gemini",
    "person_image_b64": "data:image/jpeg;base64,...",
    "style_images_b64": [
      "data:image/jpeg;base64,...",
      "data:image/jpeg;base64,..."
    ]
  }'
```

### 이미지 수정 (커스텀)

```bash
curl -X POST "http://localhost:8102/api/image/modify" \
  -H "Content-Type: application/json" \
  -d '{
    "base_image_b64": "data:image/jpeg;base64,...",
    "modification_prompt": "Add more flowers and make colors brighter",
    "model": "gemini",
    "person_image_b64": "data:image/jpeg;base64,...",
    "style_images_b64": ["data:image/jpeg;base64,..."]
  }'
```

## 📚 API 문서

서버 실행 후 다음 URL에서 자동 생성된 API 문서를 확인할 수 있습니다:
- **Swagger UI**: http://localhost:8102/docs
- **ReDoc**: http://localhost:8102/redoc

## 🔐 인증 및 제한

### Gemini 모델 사용 제한

- **일반 계정**: 일일 5회 제한
- **테스트 계정**: 제한 없음
  - `boy@naver.com` (신랑테스트1)
  - `girl@naver.com` (신부테스트1)

### HuggingFace 모델

- 무료 크레딧 기반 (제한 시 402 Payment Required 에러 발생)
- 각 모델별로 다른 provider 사용 (nscale, fal-ai, nebius 등)

## 🎯 주요 기능 상세

### 이미지 생성 모델 (Keras) - 레거시
- ✅ Keras/TensorFlow 모델 로딩 (앱 시작 시)
- ✅ 이미지 파일 업로드 및 전처리
- ✅ 강아지/고양이 분류 예측
- ✅ 파일 형식 검증 (jpg, png, jpeg만 허용)

### 감성 분석 모델 (Naive Bayes)
- ✅ 메모리 기반 경량 모델 (즉시 로딩)
- ✅ 영어 텍스트 감성 분석 (positive/negative)
- ✅ 확률 분포 및 신뢰도 제공
- ✅ 토큰별 영향도 분석 (옵션)
- ✅ 입력 검증 (빈 텍스트, 알파벳 포함 여부)

### 채팅 모델 (Ollama)
- ✅ Ollama LLM 통합 (gemma3:4b 등)
- ✅ 스트리밍 응답 지원 (NDJSON 형식)
- ✅ Thinking 과정 포함 (모델 지원 시)
- ✅ 비동기 스트리밍 처리
- ✅ 다양한 모델 선택 가능

### 청첩장 이미지 생성 (Gemini & HuggingFace)
- ✅ Gemini 3 Pro Image Preview 지원
- ✅ 멀티모달 입력 지원 (인물 사진, 스타일 참고 사진)
- ✅ 이미지→이미지 변환 지원
- ✅ 다양한 HuggingFace 모델 지원
- ✅ 일일 사용 횟수 추적 (Gemini)

### 공통 기능
- ✅ 일관된 JSON 응답 포맷
- ✅ Pydantic 스키마 검증
- ✅ 포괄적인 예외 처리
- ✅ 자동 API 문서 생성 (Swagger UI)
- ✅ 앱 시작 시 모델 자동 로딩

## 🔍 트러블슈팅

### Gemini API 오류

**401 Unauthorized**:
- `.env` 파일에 `GOOGLE_API_KEY`가 올바르게 설정되었는지 확인
- API 키가 유효한지 확인: https://aistudio.google.com/app/apikey

**일일 제한 초과**:
- 일반 계정은 일일 5회 제한
- 테스트 계정(`boy@naver.com`, `girl@naver.com`)은 제한 없음

### HuggingFace API 오류

**402 Payment Required**:
- 무료 크레딧이 소진되었습니다
- 유료 플랜으로 업그레이드하거나 다른 모델 사용

**연결 오류**:
- `HF_TOKEN` 또는 `HUGGINGFACE_API_KEY`가 설정되었는지 확인
- 네트워크 연결 상태 확인

### 포트 충돌

**현재 포트 구성**:
- Backend API: 8101
- Model API: 8102
- Frontend: 5173

다른 포트로 변경하려면:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 원하는포트번호
```

Backend API가 Model API 포트를 자동 감지하므로, 포트 변경 시 Backend 재시작 필요

### Ollama 연결 오류

- Ollama 서버가 실행 중인지 확인: `curl http://localhost:11434/api/tags`
- 필요한 모델이 다운로드되었는지 확인: `ollama list`
- 모델이 없으면 다운로드: `ollama pull gemma3:4b`
- macOS에서 mutex lock 에러 발생 시: `export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES`

## 📖 추가 문서

- **Gemini 설정 가이드**: `GEMINI_SETUP.md`
- **이미지 모델 상세 정보**: `IMAGE_MODELS.md`
- **프로젝트 구조**: `PROJECT_STRUCTURE.md`
- **빠른 시작 가이드**: `QUICK_START.md`

## 🚀 향후 개선 계획

### 개인 맞춤 최적화를 위한 학습 계획

현재 프로젝트는 기본적인 AI 모델 서빙에 집중하고 있으며, 향후 다음과 같은 기술들을 학습하여 개인 맞춤형 최적화 기능을 추가할 예정입니다:

#### 1. **RAG (Retrieval-Augmented Generation)**
- 문서 기반 검색 및 생성 기능 구현
- 사용자별 맞춤 정보 제공을 위한 컨텍스트 검색
- 웨딩 플래너 도메인 특화 지식 베이스 구축

#### 2. **VectorDB (벡터 데이터베이스)**
- Chroma, Pinecone, Weaviate 등 벡터 DB 학습 및 적용
- 사용자 데이터 및 웨딩 관련 정보의 의미 기반 검색
- 유사도 검색을 통한 개인화된 추천 시스템

#### 3. **LangChain**
- LLM 애플리케이션 개발 프레임워크 학습
- 체인(Chain) 기반 복잡한 워크플로우 구현
- 메모리 관리 및 대화 컨텍스트 유지
- 도구(Tools) 및 에이전트(Agents) 활용

#### 4. **LangGraph**
- 상태 기반 LLM 애플리케이션 구축
- 복잡한 의사결정 흐름 및 멀티 스텝 프로세스 구현
- 웨딩 플래닝 워크플로우 자동화
- 조건부 분기 및 루프 처리

### 목표
- 사용자별 맞춤형 웨딩 플래닝 추천
- 대화형 AI 어시스턴트 고도화
- 지식 베이스 기반 정확한 정보 제공
- 복잡한 워크플로우 자동화

## 📄 라이선스

이 프로젝트는 교육 목적으로 개발되었습니다.

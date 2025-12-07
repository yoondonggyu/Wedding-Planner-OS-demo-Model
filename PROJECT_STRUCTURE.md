# 프로젝트 구조 문서

## 📁 디렉토리 구조

```
3.Wedding_OS_model/
├── app/                          # FastAPI 애플리케이션
│   ├── __init__.py
│   ├── main.py                   # FastAPI 앱 진입점
│   ├── core/                     # 핵심 설정 및 예외 처리
│   │   ├── config.py             # 환경 변수 및 설정 관리 (중앙화)
│   │   └── exceptions.py         # 예외 처리 핸들러
│   ├── routers/                  # API 라우터
│   │   ├── sentiment_routes.py   # 감성 분석 API
│   │   ├── chat_routes.py        # Ollama 채팅 API
│   │   ├── gemini_routes.py      # Gemini 채팅 API
│   │   ├── review_summary_routes.py  # 리뷰 요약 API
│   │   └── predict_routes.py     # 이미지 예측 API
│   ├── services/                 # 비즈니스 로직 서비스
│   │   ├── sentiment_service.py  # 감성 분석 서비스
│   │   ├── chat_service.py       # Ollama 채팅 서비스
│   │   ├── gemini_service.py     # Gemini 서비스
│   │   ├── review_summary_service.py  # 리뷰 요약 서비스
│   │   └── model_service.py      # 이미지 분류 모델 서비스
│   ├── schemas/                  # Pydantic 스키마
│   │   ├── chat_schema.py        # 채팅 요청/응답 스키마
│   │   └── prediction.py         # 예측 요청/응답 스키마
│   └── static/                   # 정적 파일
│       └── index.html            # API 문서 페이지
├── models/                       # ML 모델 구현
│   ├── __init__.py
│   └── sentiment.py             # Naive Bayes 감성 분석 모델
├── assets/                      # 모델 파일 및 리소스
│   ├── keras_model.h5          # 이미지 분류 모델 (Git에 포함 안됨)
│   └── labels.txt               # 모델 레이블
├── .env                         # 환경 변수 (Git에 포함 안됨)
├── .env.example                 # 환경 변수 예제
├── .gitignore                   # Git 무시 파일
├── Dockerfile                   # Docker 이미지 빌드 파일
├── requirements.txt             # Python 의존성
├── runtime.txt                  # Python 버전 명시
├── README.md                    # 프로젝트 메인 문서
├── GEMINI_SETUP.md             # Gemini API 설정 가이드
├── QUICK_START.md              # 빠른 시작 가이드
└── PROJECT_STRUCTURE.md        # 이 문서

```

## 🔧 주요 컴포넌트

### 1. 환경 변수 관리 (`app/core/config.py`)
- **중앙화된 설정 관리**: 모든 환경 변수를 한 곳에서 관리
- **자동 검증**: 애플리케이션 시작 시 환경 변수 검증
- **디버깅 지원**: 누락된 환경 변수에 대한 명확한 오류 메시지

**사용 예시:**
```python
from app.core.config import GEMINI_API_KEY, GEMINI_MODEL

# 환경 변수 사용
client = genai.Client(api_key=GEMINI_API_KEY)
```

### 2. API 라우터 (`app/routers/`)
- **sentiment_routes.py**: 텍스트 감성 분석 API
- **chat_routes.py**: Ollama 기반 채팅 API
- **gemini_routes.py**: Gemini 기반 채팅 API (스트리밍 지원)
- **review_summary_routes.py**: 리뷰 요약 및 감성 분석 API
- **predict_routes.py**: 이미지 분류 예측 API

### 3. 서비스 레이어 (`app/services/`)
- **비즈니스 로직 분리**: 라우터는 HTTP 요청/응답만 처리
- **재사용 가능**: 여러 라우터에서 동일한 서비스 사용 가능
- **테스트 용이**: 서비스 로직을 독립적으로 테스트 가능

### 4. 예외 처리 (`app/core/exceptions.py`)
- **통일된 에러 응답**: 모든 API에서 일관된 에러 형식
- **자동 로깅**: 에러 발생 시 자동으로 로그 기록

## 🔑 환경 변수 설정

`.env` 파일에 다음 변수들을 설정하세요:

```env
# Google Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# 애플리케이션 설정 (선택적)
APP_NAME=AI Model Serving API
APP_VERSION=1.0.0
DEBUG=False

# 서버 설정 (선택적)
HOST=0.0.0.0
PORT=8502

# 모델 설정 (선택적)
GEMINI_MODEL=gemini-2.5-flash
```

## 🚀 실행 방법

### 로컬 개발 환경
```bash
# 1. 가상환경 활성화
conda activate env_python310

# 2. 의존성 설치
pip install -r requirements.txt

# 3. .env 파일 설정
cp .env.example .env
# .env 파일에 GEMINI_API_KEY 추가

# 4. 서버 실행
uvicorn app.main:app --host 0.0.0.0 --port 8502 --reload
```

### Docker 사용
```bash
# 개발 환경
docker build --target dev -t wedding-os-model:dev .
docker run -p 8502:8001 --env-file .env wedding-os-model:dev

# 프로덕션 환경
docker build --target prod -t wedding-os-model:prod .
docker run -p 8502:8001 --env-file .env wedding-os-model:prod
```

## 📝 주요 변경 사항

### 환경 변수 관리 중앙화
- **이전**: 각 서비스 파일에서 개별적으로 `load_dotenv()` 호출
- **현재**: `app/core/config.py`에서 중앙 관리
- **장점**: 
  - 중복 코드 제거
  - 환경 변수 검증 통합
  - 유지보수 용이

### 코드 정리
- 중복된 `load_dotenv()` 호출 제거
- `.gitignore` 중복 항목 정리
- 불필요한 디버깅 코드 정리

## 🐛 문제 해결

### API Key 오류
1. `.env` 파일이 프로젝트 루트에 있는지 확인
2. `GEMINI_API_KEY=your_key` 형식인지 확인 (공백 없음)
3. 애플리케이션 재시작

### 모듈 import 오류
```bash
# 프로젝트 루트에서 실행하는지 확인
cd /Users/yoon-dong-gyu/kakao_bootcamp/1.Wedding_OS_Project/3.Wedding_OS_model
python -m uvicorn app.main:app --reload
```

## 📚 추가 문서
- [README.md](README.md) - 프로젝트 개요 및 설치 가이드
- [GEMINI_SETUP.md](GEMINI_SETUP.md) - Gemini API 설정 상세 가이드
- [QUICK_START.md](QUICK_START.md) - 빠른 시작 가이드






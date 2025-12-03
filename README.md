# AI Model Serving API

두 가지 AI 모델을 FastAPI로 서빙하는 프로젝트입니다:
1. **감성 분석 모델**: Naive Bayes 기반 텍스트 감성 분석 (positive/negative)
2. **채팅 모델**: Ollama 기반 LLM 채팅 (gemma3:4b 등) 및 Gemini 2.5 Flash

## 프로젝트 구조

```
3.Wedding_OS_model/
├── app/
│   ├── main.py                     # FastAPI 앱 진입점
│   ├── routers/
│   │   ├── sentiment_routes.py     # 감성 분석 API 라우터
│   │   ├── chat_routes.py          # 채팅 API 라우터 (Ollama)
│   │   └── gemini_routes.py        # Gemini API 라우터
│   ├── services/
│   │   ├── sentiment_service.py    # 감성 분석 모델 서비스
│   │   ├── chat_service.py         # 채팅 모델 서비스 (Ollama)
│   │   └── gemini_service.py       # Gemini 서비스
│   ├── schemas/
│   │   └── chat_schema.py          # 채팅 스키마
│   └── core/
│       └── exceptions.py           # 예외 처리
├── models/
│   └── sentiment.py                # 감성 분석 모델 구현
└── requirements.txt                # 의존성 패키지
```

## 실행 방법

### 1. 가상환경 활성화
```bash
conda activate env_python310
```

### 2. 필요한 패키지 설치
```bash
# requirements.txt 사용 (권장)
pip install -r requirements.txt

# 또는 개별 설치
pip install fastapi uvicorn ollama python-multipart python-dotenv google-genai
```

**참고**: 
- Python 3.10 환경 사용 (`env_python310`)
- Ollama는 별도로 설치 및 실행되어야 합니다 (https://ollama.ai)
- Gemini API 키는 `.env` 파일에 설정해야 합니다

### 3. 환경 변수 설정
`.env` 파일 생성:
```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

### 4. 서버 실행
```bash
cd /Users/yoon-dong-gyu/kakao_bootcamp/1.Wedding_OS_Project/3.Wedding_OS_model

# 서버 실행 (기본 포트: 8502)
conda run -n env_python310 python -m uvicorn app.main:app --host 0.0.0.0 --port 8502
```

**참고**:
- 기본 포트는 **8502**입니다
- 서버가 `http://localhost:8502`에서 실행됩니다

## API 테스트

### 1. 헬스 체크
```bash
curl http://localhost:8502/
```

### 2. 텍스트 감성 분석

#### curl로 테스트
```bash
# 기본 감성 분석 (토큰 영향도 제외)
curl -X POST "http://localhost:8502/api/sentiment" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "I really love this camera, the picture quality is amazing!",
    "explain": false
  }'

# 토큰 영향도 포함
curl -X POST "http://localhost:8502/api/sentiment" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This is the worst product ever, totally disappointed",
    "explain": true
  }'
```

**정상 응답 예시 (긍정):**
```json
{
  "label": "positive",
  "confidence": 0.9876543,
  "probabilities": {
    "positive": 0.9876543,
    "negative": 0.0123457
  },
  "top_tokens": [
    {"token": "love", "impact": 2.5},
    {"token": "great", "impact": 1.8},
    {"token": "absolutely", "impact": 1.2}
  ]
}
```

### 3. 채팅 API (Ollama)

#### 사전 요구사항
1. **Ollama 설치 및 실행**
   ```bash
   # Ollama 설치 (https://ollama.ai)
   # 모델 다운로드
   ollama pull gemma3:4b
   ```

2. **Ollama 서버 실행 확인**
   ```bash
   # 기본 포트: 11434
   curl http://localhost:11434/api/tags
   ```

#### curl로 테스트
```bash
curl -X POST "http://localhost:8502/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, how are you?",
    "model": "gemma3:4b"
  }'
```

**응답 형식 (NDJSON 스트리밍):**
```json
{"type": "thinking_start"}
{"type": "thinking", "content": "..."}
{"type": "thinking_end"}
{"type": "content", "content": "Hello"}
{"type": "content", "content": "!"}
{"type": "content", "content": " I"}
...
```

### 4. Gemini API

#### WebSocket 엔드포인트
```bash
# WebSocket 연결 (wscat 등 사용)
wscat -c "ws://localhost:8502/api/gemini/ws"
```

#### HTTP Streaming 엔드포인트
```bash
curl -X POST "http://localhost:8502/api/gemini/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, how are you?",
    "chat_history": []
  }'
```

## API 문서

서버 실행 후 다음 URL에서 자동 생성된 API 문서를 확인할 수 있습니다:
- Swagger UI: http://localhost:8502/docs
- ReDoc: http://localhost:8502/redoc

## 주요 기능

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
- ✅ 한글 답변 프롬프트 강화

### Gemini 2.5 Flash
- ✅ Google Gemini API 통합
- ✅ WebSocket 기반 실시간 스트리밍
- ✅ HTTP Streaming Response 지원
- ✅ 채팅 히스토리 관리
- ✅ 한글 답변 지원

### 공통 기능
- ✅ 일관된 JSON 응답 포맷
- ✅ Pydantic 스키마 검증
- ✅ 포괄적인 예외 처리
- ✅ 자동 API 문서 생성 (Swagger UI)
- ✅ 앱 시작 시 모델 자동 로딩

## 트러블슈팅

### 포트 충돌
- **현재 포트 구성**:
  - Backend API: 8101
  - Model API: 8502
- 다른 포트로 변경하려면: `uvicorn app.main:app --host 0.0.0.0 --port 원하는포트번호`
- Backend API가 Model API 포트를 자동 감지하므로, 포트 변경 시 Backend 재시작 필요

### Ollama 연결 오류
- Ollama 서버가 실행 중인지 확인: `curl http://localhost:11434/api/tags`
- 필요한 모델이 다운로드되었는지 확인: `ollama list`
- 모델이 없으면 다운로드: `ollama pull gemma3:4b`

### Gemini API 오류
- `.env` 파일에 `GEMINI_API_KEY`가 설정되어 있는지 확인
- API 키가 유효한지 확인
- `GEMINI_SETUP.md` 참고

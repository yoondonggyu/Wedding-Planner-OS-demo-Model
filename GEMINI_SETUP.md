# Gemini 2.5 Flash 설정 가이드

## 1. Google AI Studio에서 API 키 발급

1. [Google AI Studio](https://aistudio.google.com/)에 접속
2. Google 계정으로 로그인
3. "Get API Key" 버튼 클릭
4. 새 프로젝트 생성 또는 기존 프로젝트 선택
5. API 키 생성 및 복사

## 2. 환경 변수 설정

프로젝트 루트 디렉토리(`3.Wedding_OS_model/`)에 `.env` 파일을 생성하고 다음 내용을 추가:

```env
GEMINI_API_KEY=your_api_key_here
```

**⚠️ 보안 주의사항:**
- `.env` 파일은 절대 Git에 커밋하지 마세요
- `.gitignore`에 `.env`가 포함되어 있는지 확인하세요

## 3. 패키지 설치

```bash
cd 3.Wedding_OS_model
pip install google-genai==1.52.0
```

또는 전체 requirements.txt 설치:

```bash
pip install -r requirements.txt
```

## 4. API 엔드포인트

### WebSocket 엔드포인트
- **URL**: `ws://localhost:8102/api/gemini/ws`
- **프로토콜**: WebSocket
- **메시지 형식**:
  ```json
  {
    "type": "message",
    "content": "사용자 메시지",
    "model": "gemini-2.5-flash",
    "chat_history": []  // 선택적
  }
  ```

### HTTP 스트리밍 엔드포인트
- **URL**: `POST /api/gemini/chat`
- **Content-Type**: `application/json`
- **Request Body**:
  ```json
  {
    "message": "사용자 메시지",
    "model": "gemini-2.5-flash"
  }
  ```

### HTTP 단순 응답 엔드포인트
- **URL**: `POST /api/gemini/chat/simple`
- **Content-Type**: `application/json`
- **Request Body**:
  ```json
  {
    "message": "사용자 메시지",
    "model": "gemini-2.5-flash"
  }
  ```

## 5. 사용 가능한 모델

- `gemini-2.5-flash` (기본값) - 빠른 응답 속도
- `gemini-2.0-flash-exp` - 실험적 버전
- 기타 Google AI Studio에서 제공하는 모델

## 6. 테스트

서버 실행 후 다음 명령으로 테스트:

```bash
# HTTP 스트리밍 테스트
curl -X POST http://localhost:8102/api/gemini/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "안녕하세요!", "model": "gemini-2.5-flash"}'

# HTTP 단순 응답 테스트
curl -X POST http://localhost:8102/api/gemini/chat/simple \
  -H "Content-Type: application/json" \
  -d '{"message": "안녕하세요!", "model": "gemini-2.5-flash"}'
```

## 7. 문제 해결

### API 키 오류
- `.env` 파일이 올바른 위치에 있는지 확인
- API 키가 정확히 복사되었는지 확인 (공백 없이)
- Google AI Studio에서 API 키가 활성화되어 있는지 확인

### 모듈 오류
```bash
pip install --upgrade google-genai
```

### 연결 오류
- 인터넷 연결 확인
- 방화벽 설정 확인
- Google AI Studio 서비스 상태 확인


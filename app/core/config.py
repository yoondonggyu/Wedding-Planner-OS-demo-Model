"""
환경 변수 및 설정 관리 모듈
프로젝트 전체에서 사용하는 환경 변수를 중앙에서 관리합니다.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 프로젝트 루트 디렉토리 찾기 (app/core/에서 상위로 2단계)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"

# .env 파일 명시적으로 로드
load_dotenv(dotenv_path=ENV_FILE)

# ============================================
# API Keys
# ============================================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ============================================
# 애플리케이션 설정
# ============================================
APP_NAME = os.getenv("APP_NAME", "AI Model Serving API")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# ============================================
# 서버 설정
# ============================================
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8502"))

# ============================================
# 모델 설정
# ============================================
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# ============================================
# 검증 및 디버깅
# ============================================
def validate_config():
    """환경 변수 설정 검증"""
    errors = []
    warnings = []
    
    if not GEMINI_API_KEY:
        warnings.append("⚠️  GEMINI_API_KEY가 설정되지 않았습니다.")
        warnings.append(f"   .env 파일 경로: {ENV_FILE}")
        warnings.append(f"   .env 파일 존재 여부: {ENV_FILE.exists()}")
        if ENV_FILE.exists():
            warnings.append("   .env 파일 내용 확인 필요: GEMINI_API_KEY=your_key 형식인지 확인하세요.")
    else:
        print(f"✅ GEMINI_API_KEY가 로드되었습니다. (길이: {len(GEMINI_API_KEY)} 문자)")
    
    if errors:
        for error in errors:
            print(f"❌ {error}")
    
    if warnings:
        for warning in warnings:
            print(warning)
    
    return len(errors) == 0

# 애플리케이션 시작 시 자동 검증
if __name__ != "__main__":
    validate_config()






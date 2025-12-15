from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.routers import predict_routes, sentiment_routes, chat_routes, gemini_routes, invitation_routes, image_generation_routes
from app.core.exceptions import APIError, api_error_handler, RequestValidationError, validation_error_handler, global_exception_handler
from app.services.model_service import load_ai_model
from app.services.sentiment_service import get_sentiment_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    # TensorFlow/Keras 모델 로딩 (Python 3.13 호환성 이슈로 선택적 로딩)
    import sys
    if sys.version_info < (3, 13):
        # Load image classification model on startup
        try:
            load_ai_model()
            print("✅ Image classification model loaded")
        except Exception as e:
            print(f"⚠️  WARNING: Failed to load image classification model: {e}")
        
        # Load sentiment analysis model on startup
        try:
            get_sentiment_service()
            print("✅ Sentiment analysis model loaded")
        except Exception as e:
            print(f"⚠️  WARNING: Failed to load sentiment analysis model: {e}")
    else:
        print("⚠️ Python 3.13 감지: TensorFlow 호환성 문제로 모델 로딩 건너뜀")
        print("   이미지 분류/감성 분석 기능은 비활성화됩니다.")
        print("   청첩장 이미지 생성(Gemini/FLUX) 기능은 정상 작동합니다.")
    
    yield
    # Clean up if needed

app = FastAPI(
    title="AI Model Serving API",
    version="1.0.0",
    description="Keras 이미지 분류 모델과 감성 분석 모델을 서빙하는 FastAPI 애플리케이션",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "http://127.0.0.1:5173", "http://127.0.0.1:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(predict_routes.router, prefix="/api", tags=["Image Classification"])
app.include_router(sentiment_routes.router, prefix="/api", tags=["Sentiment Analysis"])
app.include_router(chat_routes.router, prefix="/api", tags=["Chat"])
app.include_router(gemini_routes.router, prefix="/api", tags=["Gemini Chat"])
app.include_router(invitation_routes.router, prefix="/api", tags=["Invitation"])
app.include_router(image_generation_routes.router, prefix="/api", tags=["Image Generation"])

app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Register Exception Handlers
app.add_exception_handler(APIError, api_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(Exception, global_exception_handler)

@app.get("/", tags=["System"])
async def root():
    return FileResponse('app/static/index.html')

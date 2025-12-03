from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from app.routers import sentiment_routes, chat_routes, gemini_routes
from app.core.exceptions import APIError, api_error_handler, RequestValidationError, validation_error_handler, global_exception_handler
from app.services.sentiment_service import get_sentiment_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load sentiment analysis model on startup
    try:
        get_sentiment_service()
        print("✅ Sentiment analysis model loaded")
    except Exception as e:
        print(f"⚠️  WARNING: Failed to load sentiment analysis model: {e}")
    
    yield
    # Clean up if needed

app = FastAPI(
    title="AI Model Serving API",
    version="1.0.0",
    description="감성 분석 모델과 LLM 채팅 모델을 서빙하는 FastAPI 애플리케이션",
    lifespan=lifespan
)

# Register Routers
app.include_router(sentiment_routes.router, prefix="/api", tags=["Sentiment Analysis"])
app.include_router(chat_routes.router, prefix="/api", tags=["Chat"])
app.include_router(gemini_routes.router, prefix="/api", tags=["Gemini Chat"])

app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Register Exception Handlers
app.add_exception_handler(APIError, api_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(Exception, global_exception_handler)

@app.get("/", tags=["System"])
async def root():
    return FileResponse('app/static/index.html')

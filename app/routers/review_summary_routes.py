"""
리뷰 요약 API 라우터
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.services.review_summary_service import summarize_reviews_with_sentiment

router = APIRouter(tags=["Review Summary"])


class ReviewSummaryRequest(BaseModel):
    reviews: List[str]
    vendor_name: Optional[str] = None
    vendor_type: Optional[str] = None


@router.post("/review-summary")
async def summarize_reviews(request: ReviewSummaryRequest):
    """
    리뷰 목록을 감성 분석하고 Gemini로 요약
    
    요청:
    {
        "reviews": ["리뷰1", "리뷰2", ...],
        "vendor_name": "업체명" (선택적),
        "vendor_type": "업체 타입" (선택적)
    }
    
    응답:
    {
        "summary": "요약 텍스트",
        "sentiment_analysis": {
            "positive_count": int,
            "negative_count": int,
            "positive_percentage": float,
            "negative_percentage": float,
            "overall_sentiment": "positive" | "negative" | "neutral"
        },
        "detailed_sentiments": [...]
    }
    """
    if not request.reviews:
        raise HTTPException(status_code=400, detail="리뷰 목록이 비어있습니다.")
    
    try:
        result = await summarize_reviews_with_sentiment(
            reviews=request.reviews,
            vendor_name=request.vendor_name,
            vendor_type=request.vendor_type
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"리뷰 요약 중 오류 발생: {str(e)}")

"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.services.review_summary_service import summarize_reviews_with_sentiment

router = APIRouter(tags=["Review Summary"])


class ReviewSummaryRequest(BaseModel):
    reviews: List[str]
    vendor_name: Optional[str] = None
    vendor_type: Optional[str] = None


@router.post("/review-summary")
async def summarize_reviews(request: ReviewSummaryRequest):
    """
    리뷰 목록을 감성 분석하고 Gemini로 요약
    
    요청:
    {
        "reviews": ["리뷰1", "리뷰2", ...],
        "vendor_name": "업체명" (선택적),
        "vendor_type": "업체 타입" (선택적)
    }
    
    응답:
    {
        "summary": "요약 텍스트",
        "sentiment_analysis": {
            "positive_count": int,
            "negative_count": int,
            "positive_percentage": float,
            "negative_percentage": float,
            "overall_sentiment": "positive" | "negative" | "neutral"
        },
        "detailed_sentiments": [...]
    }
    """
    if not request.reviews:
        raise HTTPException(status_code=400, detail="리뷰 목록이 비어있습니다.")
    
    try:
        result = await summarize_reviews_with_sentiment(
            reviews=request.reviews,
            vendor_name=request.vendor_name,
            vendor_type=request.vendor_type
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"리뷰 요약 중 오류 발생: {str(e)}")

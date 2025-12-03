"""
리뷰 요약 서비스 - 감성 분석 + Gemini 요약
"""
import os
from typing import Dict, Any, List
from dotenv import load_dotenv
from google import genai
from app.services.sentiment_service import get_sentiment_service

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


async def summarize_reviews_with_sentiment(
    reviews: List[str],
    vendor_name: str = None,
    vendor_type: str = None
) -> Dict[str, Any]:
    """
    리뷰 목록을 감성 분석하고 Gemini로 요약
    
    Args:
        reviews: 리뷰 텍스트 리스트
        vendor_name: 업체명 (선택적)
        vendor_type: 업체 타입 (선택적)
    
    Returns:
        {
            "summary": "요약 텍스트",
            "sentiment_analysis": {
                "positive_count": int,
                "negative_count": int,
                "positive_percentage": float,
                "negative_percentage": float,
                "overall_sentiment": "positive" | "negative" | "neutral"
            },
            "detailed_sentiments": [
                {
                    "review": str,
                    "sentiment": "positive" | "negative",
                    "confidence": float
                }
            ]
        }
    """
    if not reviews or len(reviews) == 0:
        return {
            "summary": "리뷰가 없습니다.",
            "sentiment_analysis": {
                "positive_count": 0,
                "negative_count": 0,
                "positive_percentage": 0.0,
                "negative_percentage": 0.0,
                "overall_sentiment": "neutral"
            },
            "detailed_sentiments": []
        }
    
    # 1. 감성 분석 수행 (한글 리뷰는 Gemini로 감성 분석)
    sentiment_service = get_sentiment_service()
    detailed_sentiments = []
    positive_count = 0
    negative_count = 0
    
    for review in reviews:
        sentiment_label = "neutral"
        confidence = 0.0
        
        # 영어 리뷰인 경우 기존 감성 분석 모델 사용
        try:
            if any(ord(c) < 128 for c in review):  # ASCII 문자가 포함된 경우
                sentiment_result = sentiment_service.predict(review)
                sentiment_label = sentiment_result.get("label", "neutral")
                confidence = sentiment_result.get("confidence", 0.0)
        except Exception as e:
            # 감성 분석 실패 시 Gemini로 대체하거나 neutral로 처리
            print(f"⚠️ 감성 분석 실패 (Gemini로 대체): {e}")
            sentiment_label = "neutral"
            confidence = 0.5
        
        # 한글 리뷰는 Gemini 요약에서 감성 분석 포함
        detailed_sentiments.append({
            "review": review[:200] + "..." if len(review) > 200 else review,  # 요약용으로 일부만
            "sentiment": sentiment_label,
            "confidence": confidence
        })
        
        if sentiment_label == "positive":
            positive_count += 1
        elif sentiment_label == "negative":
            negative_count += 1
    
    total_reviews = len(reviews)
    
    # 한글 리뷰의 경우 키워드 기반 감성 분석 (감성 분석이 실패한 경우)
    if positive_count == 0 and negative_count == 0:
        # 한글 키워드 기반 감성 분석
        positive_keywords = ["좋", "만족", "추천", "훌륭", "최고", "완벽", "친절", "깔끔", "예쁘", "멋", "감동", "훌륭한", "좋은"]
        negative_keywords = ["아쉽", "불만", "별로", "나쁜", "최악", "실망", "불친절", "더러", "시설", "문제", "아쉬운", "별로인"]
        
        # detailed_sentiments도 업데이트
        for i, review in enumerate(reviews):
            review_lower = review.lower()
            pos_score = sum(1 for keyword in positive_keywords if keyword in review_lower)
            neg_score = sum(1 for keyword in negative_keywords if keyword in review_lower)
            
            if pos_score > neg_score:
                positive_count += 1
                detailed_sentiments[i]["sentiment"] = "positive"
                detailed_sentiments[i]["confidence"] = min(0.9, 0.5 + (pos_score / 10))
            elif neg_score > pos_score:
                negative_count += 1
                detailed_sentiments[i]["sentiment"] = "negative"
                detailed_sentiments[i]["confidence"] = min(0.9, 0.5 + (neg_score / 10))
    
    positive_percentage = (positive_count / total_reviews) * 100 if total_reviews > 0 else 0.0
    negative_percentage = (negative_count / total_reviews) * 100 if total_reviews > 0 else 0.0
    
    # 전체 감성 판단
    if positive_percentage >= 60:
        overall_sentiment = "positive"
    elif negative_percentage >= 60:
        overall_sentiment = "negative"
    else:
        overall_sentiment = "neutral"
    
    # 2. Gemini로 요약 생성 (한글 리뷰의 감성 분석도 포함)
    summary = await _generate_summary_with_gemini(
        reviews=reviews,
        sentiment_analysis={
            "positive_count": positive_count,
            "negative_count": negative_count,
            "positive_percentage": positive_percentage,
            "negative_percentage": negative_percentage,
            "overall_sentiment": overall_sentiment
        },
        vendor_name=vendor_name,
        vendor_type=vendor_type
    )
    
    return {
        "summary": summary,
        "sentiment_analysis": {
            "positive_count": positive_count,
            "negative_count": negative_count,
            "positive_percentage": round(positive_percentage, 2),
            "negative_percentage": round(negative_percentage, 2),
            "overall_sentiment": overall_sentiment
        },
        "detailed_sentiments": detailed_sentiments
    }


async def _generate_summary_with_gemini(
    reviews: List[str],
    sentiment_analysis: Dict[str, Any],
    vendor_name: str = None,
    vendor_type: str = None
) -> str:
    """
    Gemini를 사용하여 리뷰 요약 생성
    """
    if not GEMINI_API_KEY:
        return "Gemini API 키가 설정되지 않았습니다."
    
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        # 프롬프트 구성
        vendor_info = ""
        if vendor_name:
            vendor_info += f"업체명: {vendor_name}\n"
        if vendor_type:
            vendor_info += f"업체 타입: {vendor_type}\n"
        
        reviews_text = "\n".join([f"- {review}" for review in reviews])
        
        # 한글 리뷰의 경우 Gemini가 감성도 분석하도록 프롬프트 구성
        sentiment_info = ""
        if sentiment_analysis['positive_count'] > 0 or sentiment_analysis['negative_count'] > 0:
            sentiment_info = f"""
감성 분석 결과 (영어 리뷰 기준):
- 긍정 리뷰: {sentiment_analysis['positive_count']}개 ({sentiment_analysis['positive_percentage']:.1f}%)
- 부정 리뷰: {sentiment_analysis['negative_count']}개 ({sentiment_analysis['negative_percentage']:.1f}%)
- 전체 감성: {sentiment_analysis['overall_sentiment']}
"""
        
        prompt = f"""다음은 웨딩 관련 리뷰 목록입니다. 리뷰들을 분석하여 한글로 요약해주세요.

{vendor_info}{sentiment_info}
리뷰 목록:
{reviews_text}

**중요 지시사항:**
1. 각 리뷰의 감성을 분석하여 긍정/부정을 판단해주세요 (한글 리뷰 포함)
2. 전체적인 평가를 긍정/부정 비율로 요약해주세요
3. 주요 긍정 포인트를 2-3개 나열해주세요
4. 주요 부정 포인트나 개선 사항이 있으면 나열해주세요
5. 종합 의견을 제시해주세요

요약은 200자 이내로 간결하게 작성해주세요. 한글로만 답변해주세요."""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        
        # 응답에서 텍스트 추출
        if hasattr(response, 'text'):
            summary = response.text
        elif hasattr(response, 'candidates') and len(response.candidates) > 0:
            # candidates에서 텍스트 추출
            candidate = response.candidates[0]
            if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                parts = candidate.content.parts
                if parts and len(parts) > 0:
                    summary = parts[0].text if hasattr(parts[0], 'text') else str(parts[0])
                else:
                    summary = str(response)
            else:
                summary = str(response)
        else:
            summary = str(response)
        
        return summary.strip()
        
    except Exception as e:
        print(f"❌ Gemini 요약 생성 오류: {e}")
        return f"요약 생성 중 오류가 발생했습니다: {str(e)}"

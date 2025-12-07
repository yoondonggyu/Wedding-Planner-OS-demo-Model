"""
청첩장 문구 추천 라우터 - Gemini 2.5 Flash 사용
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.services.gemini_service import generate_gemini_simple
import json
import re

router = APIRouter(tags=["Invitation"])


class InvitationTextRecommendReq(BaseModel):
    groom_name: str
    bride_name: str
    groom_father_name: Optional[str] = None  # 신랑 부 성함
    groom_mother_name: Optional[str] = None  # 신랑 모 성함
    bride_father_name: Optional[str] = None  # 신부 부 성함
    bride_mother_name: Optional[str] = None  # 신부 모 성함
    wedding_date: str  # YYYY-MM-DD
    wedding_time: Optional[str] = None  # HH:MM
    wedding_location: Optional[str] = None
    style: Optional[str] = None  # CLASSIC, MODERN, VINTAGE 등
    additional_info: Optional[str] = None  # 추가 정보
    additional_message: Optional[str] = None  # 추가 멘트
    requirements: Optional[str] = None  # 청첩장 만들 때 요구사항 (멘트 만들 때)


@router.post("/invitation/text-recommend")
async def recommend_invitation_text(request: InvitationTextRecommendReq):
    """
    Gemini 2.5 Flash를 사용한 청첩장 문구 추천
    
    Args:
        request: 청첩장 문구 추천 요청 (신랑/신부 이름, 예식 정보, 스타일 등)
    
    Returns:
        구조화된 JSON (main_text, groom_parents, bride_parents 등)
    """
    style_map = {
        "CLASSIC": "전통적이고 우아한",
        "MODERN": "현대적이고 세련된",
        "VINTAGE": "빈티지하고 로맨틱한",
        "MINIMAL": "미니멀하고 깔끔한",
        "LUXURY": "고급스럽고 화려한",
        "NATURE": "자연스럽고 따뜻한",
        "ROMANTIC": "로맨틱하고 감성적인"
    }
    
    style_desc = style_map.get(request.style, "따뜻하고 정중한") if request.style else "따뜻하고 정중한"
    
    prompt = f"""다음 정보를 바탕으로 {style_desc} 톤의 청첩장 문구를 5가지 다른 스타일로 작성해주세요.

신랑: {request.groom_name}
신부: {request.bride_name}
예식일: {request.wedding_date}"""
    
    if request.wedding_time:
        prompt += f"\n예식 시간: {request.wedding_time}"
    if request.wedding_location:
        prompt += f"\n예식 장소: {request.wedding_location}"
    if request.additional_info:
        prompt += f"\n추가 정보: {request.additional_info}"
    
    prompt += """

각 옵션은 서로 다른 톤과 스타일을 가져야 합니다:
- 옵션 1: 전통적이고 정중한 톤
- 옵션 2: 감성적이고 로맨틱한 톤
- 옵션 3: 현대적이고 세련된 톤
- 옵션 4: 따뜻하고 친근한 톤
- 옵션 5: 우아하고 고급스러운 톤

다음 형식의 JSON으로 응답해주세요:
{
  "options": [
    {
      "main_text": "주요 문구 옵션 1",
      "groom_father": "신랑 부 성함 (없으면 빈 문자열)",
      "groom_mother": "신랑 모 성함 (없으면 빈 문자열)",
      "bride_father": "신부 부 성함 (없으면 빈 문자열)",
      "bride_mother": "신부 모 성함 (없으면 빈 문자열)",
      "wedding_info": "예식 정보를 다음 형식으로 작성: 첫 줄에 예식일, 둘째 줄에 예식 시간, 셋째 줄에 예식 장소를 각각 작성하세요.",
      "reception_info": "식장 정보 (있으면 작성, 없으면 빈 문자열)",
      "closing_text": "마무리 문구"
    },
    {
      "main_text": "주요 문구 옵션 2",
      ...
    },
    ... (총 5개 옵션)
  ]
}

중요: 
- wedding_info에는 반드시 예식일, 시간, 장소를 각각 별도 줄에 작성하세요.
- 각 옵션의 main_text는 서로 완전히 다른 표현이어야 합니다.
- 옵션은 반드시 5개를 제공해야 합니다.

JSON만 응답해주세요. 다른 설명 없이 JSON만 반환해주세요."""
    
    try:
        # Gemini 2.5 Flash를 사용하여 문구 생성
        response = await generate_gemini_simple(
            prompt,
            model="gemini-2.5-flash"
        )
        
        # JSON 추출
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            try:
                recommended_data = json.loads(json_match.group())
                
                # options 배열이 있는 경우 (새 형식)
                if "options" in recommended_data and isinstance(recommended_data["options"], list) and len(recommended_data["options"]) > 0:
                    print(f"✅ {len(recommended_data['options'])}개의 문구 옵션 생성 완료")
                    return {
                        "message": "text_recommended",
                        "data": {
                            "options": recommended_data["options"]
                        }
                    }
                # 기존 단일 옵션 형식인 경우 (하위 호환성)
                elif "main_text" in recommended_data:
                    # 단일 옵션을 배열로 변환
                    print("⚠️ 단일 옵션 형식으로 받음. 배열로 변환합니다.")
                    return {
                        "message": "text_recommended",
                        "data": {
                            "options": [recommended_data]
                        }
                    }
                else:
                    raise ValueError("올바른 형식이 아닙니다")
                    
            except (json.JSONDecodeError, ValueError) as e:
                print(f"⚠️ JSON 파싱 실패: {e}")
                print(f"응답 내용: {response[:500]}")
        
        # JSON 파싱 실패 시 기본 문구 반환 (options 배열 형식)
        default_options = [
            {
                "main_text": f"{request.groom_name} · {request.bride_name} 두 사람이 하나가 되어\n새로운 인생을 시작합니다.",
                "groom_father": "",
                "groom_mother": "",
                "bride_father": "",
                "bride_mother": "",
                "wedding_info": f"{request.wedding_date}\n{request.wedding_time or ''}\n{request.wedding_location or ''}",
                "reception_info": request.wedding_location or "",
                "closing_text": "바쁘시겠지만 참석해 주시면 감사하겠습니다."
            },
            {
                "main_text": f"{request.groom_name}님과 {request.bride_name}님이\n사랑으로 하나가 되어\n새로운 가정을 이룹니다.",
                "groom_father": "",
                "groom_mother": "",
                "bride_father": "",
                "bride_mother": "",
                "wedding_info": f"{request.wedding_date}\n{request.wedding_time or ''}\n{request.wedding_location or ''}",
                "reception_info": request.wedding_location or "",
                "closing_text": "소중한 분들을 모시고 싶어\n이렇게 초대의 말씀을 드립니다."
            },
            {
                "main_text": f"{request.groom_name} · {request.bride_name}\n두 사람이 만나\n하나의 가정을 이루려 합니다.",
                "groom_father": "",
                "groom_mother": "",
                "bride_father": "",
                "bride_mother": "",
                "wedding_info": f"{request.wedding_date}\n{request.wedding_time or ''}\n{request.wedding_location or ''}",
                "reception_info": request.wedding_location or "",
                "closing_text": "바쁘시겠지만 참석해 주시면 감사하겠습니다."
            }
        ]
        return {
            "message": "text_recommended",
            "data": {
                "options": default_options
            }
        }
        
    except Exception as e:
        print(f"⚠️ AI 문구 추천 실패: {e}")
        # 에러 발생 시 기본 문구 옵션들 반환
        default_options = [
            {
                "main_text": f"{request.groom_name} · {request.bride_name} 두 사람이 하나가 되어\n새로운 인생을 시작합니다.",
                "groom_father": "",
                "groom_mother": "",
                "bride_father": "",
                "bride_mother": "",
                "wedding_info": f"{request.wedding_date}\n{request.wedding_time or ''}\n{request.wedding_location or ''}",
                "reception_info": "",
                "closing_text": "바쁘시겠지만 참석해 주시면 감사하겠습니다."
            },
            {
                "main_text": f"{request.groom_name}님과 {request.bride_name}님이\n사랑으로 하나가 되어\n새로운 시작을 합니다.",
                "groom_father": "",
                "groom_mother": "",
                "bride_father": "",
                "bride_mother": "",
                "wedding_info": f"{request.wedding_date}\n{request.wedding_time or ''}\n{request.wedding_location or ''}",
                "reception_info": "",
                "closing_text": "소중한 시간 함께해 주시면 더욱 기쁘겠습니다."
            }
        ]
        return {
            "message": "text_recommended",
            "data": {
                "options": default_options
            }
        }


@router.post("/invitation/tone-recommend")
async def recommend_invitation_tones(request: InvitationTextRecommendReq):
    """
    Gemini 2.5 Flash를 사용하여 5가지 톤의 청첩장 문구 생성
    
    Returns:
        {
            "message": "tones_recommended",
            "data": {
                "tones": [
                    {
                        "tone": "affectionate",
                        "description": "다정한",
                        "main_text": "...",
                        "parents_greeting": "...",
                        "wedding_info": "...",
                        "closing": "..."
                    },
                    ... (5 items total)
                ]
            }
        }
    """
    # 부모님 성함 정보
    parents_info = ""
    if request.groom_father_name or request.groom_mother_name:
        parents_info += f"\n신랑 부: {request.groom_father_name or '미지정'}"
        parents_info += f"\n신랑 모: {request.groom_mother_name or '미지정'}"
    if request.bride_father_name or request.bride_mother_name:
        parents_info += f"\n신부 부: {request.bride_father_name or '미지정'}"
        parents_info += f"\n신부 모: {request.bride_mother_name or '미지정'}"
    
    # 요구사항 정보 추가
    requirements_text = ""
    if request.requirements:
        requirements_text = f"\n**User Requirements:** {request.requirements}"
    
    # Enhanced English prompt for better tone generation
    prompt = f"""You are a professional wedding invitation writer. Generate 5 different Korean wedding invitation texts with distinct tones based on the following information:

**Wedding Information:**
- Groom's Name: {request.groom_name}
- Bride's Name: {request.bride_name}
- Wedding Date: {request.wedding_date}
- Wedding Time: {request.wedding_time or 'Not specified'}
- Wedding Location: {request.wedding_location or 'Not specified'}
{parents_info}
- Additional Message: {request.additional_message or 'None'}
{requirements_text}

**Required Tones (5 different styles):**
1. **Affectionate (다정한)** - Create a warm, tender, and loving tone. Use gentle and caring language that expresses deep affection between the couple. Make it feel intimate and heartfelt.

2. **Cheerful (밝고 명랑한)** - Create a bright, joyful, and energetic tone. Use upbeat and positive language that conveys happiness and excitement. Make it feel lively and celebratory.

3. **Polite (예의 있는)** - Create a respectful, courteous, and traditional tone. Use formal Korean honorifics and respectful expressions. Make it feel dignified and proper, following Korean wedding invitation conventions.

4. **Formal (격식 있는)** - Create a dignified, elegant, and ceremonial tone. Use very formal language with traditional Korean wedding expressions. Make it feel prestigious and ceremonial.

5. **Emotional (감성적인)** - Create a touching, heartfelt, and sentimental tone. Use poetic and emotional language that moves the heart. Make it feel deeply meaningful and touching.

**Output Format:**
Return ONLY a valid JSON object in this exact structure (no additional text, no markdown, just pure JSON):
{{
  "tones": [
    {{
      "tone": "affectionate",
      "description": "다정한",
      "main_text": "Main invitation text in Korean (2-4 lines, expressing the couple's love and invitation)",
      "parents_greeting": "Greeting from parents in Korean (1-2 lines, expressing gratitude and invitation)",
      "wedding_info": "{request.wedding_date}\\n{request.wedding_time or ''}\\n{request.wedding_location or ''}",
      "closing": "Closing message in Korean (1-2 lines, final invitation and gratitude)"
    }},
    {{
      "tone": "cheerful",
      "description": "밝고 명랑한",
      "main_text": "...",
      "parents_greeting": "...",
      "wedding_info": "{request.wedding_date}\\n{request.wedding_time or ''}\\n{request.wedding_location or ''}",
      "closing": "..."
    }},
    {{
      "tone": "polite",
      "description": "예의 있는",
      "main_text": "...",
      "parents_greeting": "...",
      "wedding_info": "{request.wedding_date}\\n{request.wedding_time or ''}\\n{request.wedding_location or ''}",
      "closing": "..."
    }},
    {{
      "tone": "formal",
      "description": "격식 있는",
      "main_text": "...",
      "parents_greeting": "...",
      "wedding_info": "{request.wedding_date}\\n{request.wedding_time or ''}\\n{request.wedding_location or ''}",
      "closing": "..."
    }},
    {{
      "tone": "emotional",
      "description": "감성적인",
      "main_text": "...",
      "parents_greeting": "...",
      "wedding_info": "{request.wedding_date}\\n{request.wedding_time or ''}\\n{request.wedding_location or ''}",
      "closing": "..."
    }}
  ]
}}

**Important Guidelines:**
- Each tone must be distinctly different in style, vocabulary, and emotional impact
- Use appropriate Korean honorifics and formal language for polite and formal tones
- Make the texts natural, authentic, and culturally appropriate for Korean weddings
- Ensure all 5 tones are complete and ready to use
- wedding_info must follow the exact format: date on first line, time on second line, location on third line
- Return ONLY the JSON object, no explanations or additional text"""
    
    try:
        response = await generate_gemini_simple(prompt, model="gemini-2.5-flash")
        
        # JSON 파싱
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
            if "tones" in result and len(result["tones"]) >= 5:
                return {
                    "message": "tones_recommended",
                    "data": result
                }
        
        # 실패 시 기본 톤 5개 반환
        return generate_default_tones(request)
        
    except Exception as e:
        print(f"⚠️ 톤 제안 실패: {e}")
        return generate_default_tones(request)


def generate_default_tones(request):
    """기본 5가지 톤 생성"""
    base_info = f"{request.wedding_date}\n{request.wedding_time or ''}\n{request.wedding_location or ''}"
    
    return {
        "message": "tones_recommended",
        "data": {
            "tones": [
                {
                    "tone": "affectionate",
                    "description": "다정한",
                    "main_text": f"{request.groom_name}과 {request.bride_name}이\n서로를 향한 마음을 담아\n평생의 동반자가 되려 합니다.",
                    "parents_greeting": "두 사람의 시작을 축복해주세요.",
                    "wedding_info": base_info,
                    "closing": "소중한 분들을 모시고 싶어\n이렇게 초대합니다."
                },
                {
                    "tone": "cheerful",
                    "description": "밝고 명랑한",
                    "main_text": f"{request.groom_name} ♥ {request.bride_name}\n우리 결혼해요!",
                    "parents_greeting": "함께 축하해주세요!",
                    "wedding_info": base_info,
                    "closing": "행복한 출발을 함께해요!"
                },
                {
                    "tone": "polite",
                    "description": "예의 있는",
                    "main_text": f"{request.groom_name} · {request.bride_name}\n두 사람이 혼인하오니\n귀한 걸음 하시어\n자리를 빛내주시면 감사하겠습니다.",
                    "parents_greeting": "두 집안의 경사를 함께하시길 청합니다.",
                    "wedding_info": base_info,
                    "closing": "부디 참석하시어 축복해주시기 바랍니다."
                },
                {
                    "tone": "formal",
                    "description": "격식 있는",
                    "main_text": f"{request.groom_name} · {request.bride_name}\n두 사람의 결혼을 알리오니\n부디 참석하시어\n축복해 주시기 바랍니다.",
                    "parents_greeting": "삼가 청첩드립니다.",
                    "wedding_info": base_info,
                    "closing": "귀한 시간 내어 주시면\n더없는 영광이겠습니다."
                },
                {
                    "tone": "emotional",
                    "description": "감성적인",
                    "main_text": f"서로를 향한 마음이 모여\n하나의 사랑이 되었습니다.\n{request.groom_name}과 {request.bride_name}의 시작을\n함께 지켜봐 주세요.",
                    "parents_greeting": "두 사람이 만들어갈 아름다운 이야기에\n소중한 한 페이지가 되어주세요.",
                    "wedding_info": base_info,
                    "closing": "여러분의 축복이\n두 사람에게 큰 힘이 되겠습니다."
                }
            ]
        }
    }


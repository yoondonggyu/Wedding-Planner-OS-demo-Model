from ollama import chat
import json
from typing import AsyncGenerator

async def generate_chat_response(message: str, model: str = "gemma3:4b") -> AsyncGenerator[str, None]:
    # 한글로 답변하라는 시스템 프롬프트 추가 (간단하고 명확하게)
    system_prompt = """You are a Korean AI assistant. You MUST respond ONLY in Korean (한글). 
Never use English, Chinese, Japanese, or any other language. Always use Korean only.

당신은 한국어로만 답변하는 AI입니다. 모든 답변은 한글로만 작성하세요."""
    
    # 사용자 메시지에 한글 답변 지시 추가 (간단하게)
    user_message_with_instruction = f"""{message}

위 질문에 한글로만 답변해주세요."""
    
    stream = chat(
        model=model,
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_message_with_instruction}
        ],
        stream=True,
    )
    
    in_thinking = False
    thinking = ''
    content = ''

    for chunk in stream:
        # Handle thinking (thinking과 content가 동시에 올 수 있음)
        if chunk.message.thinking:
            if not in_thinking:
                in_thinking = True
                yield json.dumps({'type': 'thinking_start'}) + "\n"
            
            thinking += chunk.message.thinking
            yield json.dumps({
                'type': 'thinking',
                'content': chunk.message.thinking
            }) + "\n"
        
        # Handle content (thinking과 독립적으로 처리)
        if chunk.message.content:
            if in_thinking:
                in_thinking = False
                yield json.dumps({'type': 'thinking_end'}) + "\n"
            
            content += chunk.message.content
            yield json.dumps({
                'type': 'content',
                'content': chunk.message.content
            }) + "\n"
    
    # 응답이 한글이 아닌 경우 경고 (로깅용)
    if content and len(content) > 10:
        has_korean = any(ord(c) >= 0xAC00 and ord(c) <= 0xD7A3 for c in content[:200])
        if not has_korean:
            print(f"⚠️ 모델 {model}이 한글이 아닌 응답을 생성했습니다: {content[:100]}")

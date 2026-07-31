"""sample_01_chat.py - vllm_serv 일반 채팅 API 호출 예제

vllm_serv 메인 인퍼런스 서버(기본 포트: 8081)의 OpenAI 호환 API(/v1/chat/completions)를
사용하여 대화형 LLM 모델과 텍스트를 주고받는 표준 예제 스크립트입니다.

실행 명령어:
    uv run python samples/sample_01_chat.py
"""

import json
import httpx
from common import check_server_health, get_server_host, print_section_header

# 1. 동적 서버 호스트 및 설정 정의 (IP 하드코딩 제거)
SERVER_HOST = get_server_host()
MAIN_PORT = 8081
API_URL = f"{SERVER_HOST}:{MAIN_PORT}/v1/chat/completions"
MODEL_NAME = "qwen3.5-4b"


def run_chat_sample():
    print_section_header("vllm_serv 01. 일반 대화(Chat Completions) 호출 예제")

    # 2. 서버 연결 상태 사전 점검
    if not check_server_health(SERVER_HOST, MAIN_PORT, "LLM 메인 서버"):
        print("💡 서버 구동 후 스크립트를 재실행해 주세요.")
        return False

    # 3. 대화 메시지 작성 (OpenAI API 메시지 규격 준수)
    messages = [
        {"role": "system", "content": "당신은 IT 및 AI 기술 전문 어시스턴트입니다. 친절하고 명확하게 답변해 주세요."},
        {"role": "user", "content": "안녕하세요! vllm_serv 서버의 주요 장점을 1문장으로 요약해 주세요."}
    ]

    # 4. HTTP POST 요청 페이로드 구성
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 250,
        "stream": False
    }

    print(f"📡 [POST] {API_URL} 요청 전송 중... (모델: {MODEL_NAME})")

    # 5. API 호출 및 응답 처리 (LLM 생성을 고려하여 타임아웃 120초 지정)
    try:
        transport = httpx.HTTPTransport(retries=1)
        with httpx.Client(transport=transport, timeout=120.0) as client:
            response = client.post(API_URL, json=payload, headers={"Connection": "close"})
            response.raise_for_status()

            # 응답 데이터 파싱
            result = response.json()
            choice = result["choices"][0]
            answer_content = choice["message"]["content"]
            finish_reason = choice.get("finish_reason", "completed")

            # think 태스크 텍스트 분리 파싱 (Qwen3.5 계열 생각 체인 처리)
            if "</think>" in answer_content:
                parts = answer_content.split("</think>")
                answer_content = parts[-1].strip()
            elif answer_content.startswith("<think>"):
                answer_content = answer_content.replace("<think>", "").strip()

            # 사용량 지표 파싱 (토큰 소비 정보)
            usage = result.get("usage", {})

            print("\n✅ [응답 성공]")
            print(f"------------------------------------------------------------")
            print(f"{answer_content}")
            print(f"------------------------------------------------------------")
            print(f"📊 완료 사유: {finish_reason}")
            if usage:
                print(f"📊 토큰 사용량: 프롬프트 {usage.get('prompt_tokens', 0)}토큰 | 생성 {usage.get('completion_tokens', 0)}토큰 | 총합 {usage.get('total_tokens', 0)}토큰")

            return True

    except httpx.HTTPStatusError as err:
        print(f"❌ [HTTP 에러 발생]: {err.response.status_code} - {err.response.text}")
        return False
    except Exception as err:
        print(f"❌ [요청 실패]: {err}")
        return False


if __name__ == "__main__":
    run_chat_sample()

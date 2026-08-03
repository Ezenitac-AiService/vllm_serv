"""sample_01_chat.py - [비전공자 초급] OpenAI 호환 일반 대화(Chat Completions) HTTP 요청 예제

본 스크립트는 AI 서비스 개발자 양성과정 훈련생을 위해 작성된 표준 예제입니다.
복잡한 클래스나 추상화 없이 파이썬 기본 HTTP 라이브러리(httpx) 및 딕셔너리(dict)를 사용해
vllm_serv 대화형 AI 모델과 주고받는 직관적인 코드를 보여줍니다.

실행 명령어:
    uv run python samples/sample_01_chat.py
"""

import os
import json
import httpx
from common import check_server_health, load_sample_config, print_section_header

# 1. 동적 서빙 포트, IP 및 모델명 구성 (config.json / .env / 환경변수 자동 파싱)
config = load_sample_config()
SERVER_HOST = config["server_host"]
MAIN_PORT = config["main_port"]
MODEL_NAME = config["default_model"]


def run_chat_sample():
    print_section_header("01. 비전공자용 httpx REST API 규격 일반 대화 호출 예제")

    # 2. 서버 구동 상태 점검 (연결 실패 시 친절 안내 메시지 출력)
    if not check_server_health(SERVER_HOST, MAIN_PORT, "vllm_serv 메인 API"):
        print("💡 서버 데몬을 켜신 후 스크립트를 재실행해 주세요 (./start_server.sh)")
        return False

    # 3. OpenAI API 표준 메시지 배열 작성 (파이썬 기본 list & dict 사용)
    messages = [
        {"role": "system", "content": "당신은 IT 및 AI 기술 전문 어시스턴트입니다. 친절하게 답변해 주세요."},
        {"role": "user", "content": "안녕하세요! vllm_serv 서버의 주요 장점을 1문장으로 요약해 주세요."}
    ]

    # 4. HTTP POST 요청 페이로드 구성 (표준 파이썬 dict 사용)
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": config.get("default_temperature", 0.3),
        "max_tokens": config.get("default_max_tokens", 250),
        "stream": False
    }

    target_url = f"{SERVER_HOST}:{MAIN_PORT}/v1/chat/completions"
    print(f"📡 [요청 전송] {target_url} (모델: {MODEL_NAME})")

    # 5. HTTP 통신 수행 (타임아웃 120초 지정)
    try:
        with httpx.Client(timeout=120.0) as client:
            response = client.post(target_url, json=payload, headers={"Connection": "close"})
            response.raise_for_status()

            # 6. JSON 응답 파싱 및 결과 추출
            result = response.json()
            choice = result["choices"][0]
            answer_content = choice["message"]["content"]
            finish_reason = choice.get("finish_reason", "completed")

            # Qwen3.5 모델 생각 체인(<think> 태그) 정제
            if "</think>" in answer_content:
                answer_content = answer_content.split("</think>")[-1].strip()

            usage = result.get("usage", {})

            # 7. 훈련생이 직관적으로 알아볼 수 있는 터미널 결과 출력
            print("\n✅ [응답 성공]")
            print("-" * 65)
            print(f"💬 AI 답변: {answer_content}")
            print("-" * 65)
            print(f"📊 정지 사유: {finish_reason}")
            if usage:
                print(f"📊 토큰 사용량: 프롬프트 {usage.get('prompt_tokens', 0)}토큰 | 생성 {usage.get('completion_tokens', 0)}토큰 | 총 {usage.get('total_tokens', 0)}토큰")

            return True

    except Exception as err:
        print(f"❌ [요청 실패]: {err}")
        return False


if __name__ == "__main__":
    run_chat_sample()

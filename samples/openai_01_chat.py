"""openai_01_chat.py - [비전공자 초급] OpenAI 공식 파이썬 라이브러리 기반 일반 대화 예제

본 스크립트는 AI 서비스 개발자 양성과정 훈련생을 위해 작성된 표준 SDK 실습 예제입니다.
low-level HTTP 요청(httpx) 대신 파이썬 공식 OpenAI SDK(from openai import OpenAI)를 사용해
vllm_serv 대화형 AI 모델과 통신하는 글로벌 표준 개발 방식을 보여줍니다.

실행 명령어:
    uv run python samples/openai_01_chat.py
"""

import os
from openai import OpenAI
from common import check_server_health, load_sample_config, print_section_header

# 1. 동적 서빙 포트, IP 및 모델명 구성 (config.json / .env 동적 파싱)
config = load_sample_config()
SERVER_HOST = config["server_host"]
MAIN_PORT = config["main_port"]
MODEL_NAME = config["default_model"]


def run_chat_sample():
    print_section_header("01. 비전공자용 OpenAI 공식 SDK 규격 일반 대화 호출 예제")

    # 2. 서버 구동 상태 점검 (연결 실패 시 친절 안내 메시지 출력)
    if not check_server_health(SERVER_HOST, MAIN_PORT, "vllm_serv 메인 API"):
        print("💡 서버 데몬을 켜신 후 스크립트를 재실행해 주세요 (./start_server.sh)")
        return False

    # 3. OpenAI 공식 SDK 클라이언트 초기화 (api_key는 EMPTY 지정)
    base_url = f"{SERVER_HOST}:{MAIN_PORT}/v1"
    api_key = os.environ.get("OPENAI_API_KEY", "EMPTY")
    
    print(f"📡 [SDK 클라이언트 초기화] {base_url} (모델: {MODEL_NAME})")
    client = OpenAI(base_url=base_url, api_key=api_key)

    # 4. OpenAI API 표준 메시지 배열 작성
    messages = [
        {"role": "system", "content": "당신은 IT 및 AI 기술 전문 어시스턴트입니다. 친절하게 답변해 주세요."},
        {"role": "user", "content": "안녕하세요! vllm_serv 서버의 주요 장점을 1문장으로 요약해 주세요."}
    ]

    # 5. OpenAI SDK 메서드 호출 (client.chat.completions.create)
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=config.get("default_temperature", 0.3),
            max_tokens=config.get("default_max_tokens", 250)
        )

        # 6. SDK 응답 객체 파싱 및 결과 추출
        choice = completion.choices[0]
        answer_content = choice.message.content or ""
        finish_reason = choice.finish_reason or "completed"

        # Qwen3.5 모델 생각 체인(<think> 태그) 정제
        if "</think>" in answer_content:
            answer_content = answer_content.split("</think>")[-1].strip()

        usage = completion.usage

        # 7. 훈련생 터미널 결과 출력
        print("\n✅ [SDK 응답 성공]")
        print("-" * 65)
        print(f"💬 AI 답변: {answer_content}")
        print("-" * 65)
        print(f"📊 정지 사유: {finish_reason}")
        if usage:
            print(f"📊 토큰 사용량: 프롬프트 {usage.prompt_tokens}토큰 | 생성 {usage.completion_tokens}토큰 | 총 {usage.total_tokens}토큰")

        return True

    except Exception as err:
        print(f"❌ [SDK 요청 실패]: {err}")
        return False


if __name__ == "__main__":
    run_chat_sample()

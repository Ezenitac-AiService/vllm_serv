"""sample_01_chat.py - [비전공자 초급] OpenAI 공식 규격 일반 대화(Chat Completions) 호출 예제

본 스크립트는 AI 서비스 개발자 양성과정 훈련생을 위해 작성된 표준 예제입니다.
복잡한 파이덴틱(Pydantic) 모델이나 추상화 클래스 없이,
OpenAI 공식 파이썬 라이브러리(from openai import OpenAI) 및 기본 HTTP 요청을 사용해
vllm_serv 대화형 AI 모델과 주고받는 가장 직관적인 코드를 보여줍니다.

실행 명령어:
    uv run python samples/sample_01_chat.py
"""

import os
import json
import httpx
from common import check_server_health, get_server_host, print_section_header

# 1. 서빙 호스트 주소 및 기본 포트(8081) 정의
SERVER_HOST = get_server_host()
MAIN_PORT = 8081
MODEL_NAME = "qwen3.5-4b"


def run_chat_sample():
    print_section_header("01. 비전공자용 OpenAI 규격 일반 대화 API 호출 예제")

    # 2. 서버 구동 상태 점검 (연결 실패 시 친절 안내 메시지 출력)
    if not check_server_health(SERVER_HOST, MAIN_PORT, "vllm_serv 메인 API"):
        print("💡 서버 데몬을 켜신 후 스크립트를 재실행해 주세요 (./start_server.sh)")
        return False

    # 3. OpenAI API 표준 메시지 배열 작성 (파이썬 기본 list & dict 사용)
    #    role 종류: "system" (역할 부여), "user" (사용자 질문), "assistant" (AI 답변)
    messages = [
        {"role": "system", "content": "당신은 IT 및 AI 기술 전문 어시스턴트입니다. 친절하게 답변해 주세요."},
        {"role": "user", "content": "안녕하세요! vllm_serv 서버의 주요 장점을 1문장으로 요약해 주세요."}
    ]

    # 4. HTTP POST 요청 페이로드 구성 (표준 파이썬 dict 사용 - Pydantic 배제)
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": 0.3,  # 답변 무작위성 조절 (0.0~2.0)
        "max_tokens": 250,   # 생성할 최대 토큰 수
        "stream": False      # 스트리밍 여부 (기본값: False)
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

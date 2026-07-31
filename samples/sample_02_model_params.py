"""sample_02_model_params.py - vllm_serv 모델 및 추론 파라미터 제어 예제

vllm_serv 메인 서버(8081 포트)로 다양한 생성 파라미터(temperature, top_p, max_tokens, stop)를
동적으로 전달하여 LLM 생성 결과를 비교 제어하는 예제 스크립트입니다.

실행 명령어:
    uv run python samples/sample_02_model_params.py
"""

import json
import httpx
from common import check_server_health, print_section_header

SERVER_HOST = "http://127.0.0.1"
MAIN_PORT = 8081
API_URL = f"{SERVER_HOST}:{MAIN_PORT}/v1/chat/completions"
MODEL_NAME = "qwen3.5-4b"


def send_completion_request(prompt: str, param_config: dict) -> dict:
    """지정된 파라미터 구성으로 chat completion API 호출."""
    messages = [
        {"role": "system", "content": "당신은 유용한 AI 어시스턴트입니다."},
        {"role": "user", "content": prompt}
    ]
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": False,
        **param_config
    }

    transport = httpx.HTTPTransport(retries=1)
    with httpx.Client(transport=transport, timeout=120.0) as client:
        response = client.post(API_URL, json=payload, headers={"Connection": "close"})
        response.raise_for_status()
        return response.json()


def run_params_sample():
    print_section_header("vllm_serv 02. 모델 파라미터 제어(Temperature/Top_P/Stop) 예제")

    if not check_server_health(SERVER_HOST, MAIN_PORT, "LLM 메인 서버"):
        print("💡 서버 구동 후 스크립트를 재실행해 주세요.")
        return False

    # 실험 케이스 1: 결정론적 답변 (Temperature = 0.0)
    print("\n🔹 [테스트 1] Low Temperature (0.0) - 정확하고 일관된 답변")
    config_low_temp = {
        "temperature": 0.0,
        "max_tokens": 150
    }
    result_1 = send_completion_request("대한민국의 수도는 어디이고 인구는 대략 얼마인가요?", config_low_temp)
    content_1 = result_1["choices"][0]["message"]["content"]
    if "</think>" in content_1:
        content_1 = content_1.split("</think>")[-1].strip()
    print(f"👉 답변 1: {content_1[:120]}...")

    # 실험 케이스 2: 정지 문자열(Stop Sequence) 지정
    print("\n🔹 [테스트 2] Stop Sequence 지정 - 특정 단어/줄바꿈 생성 중단 ('\n' 중단)")
    config_stop = {
        "temperature": 0.3,
        "max_tokens": 100,
        "stop": ["\n", "."]
    }
    result_2 = send_completion_request("인공지능의 3대 핵심 요소를 번호 리스트로 작성하세요:", config_stop)
    content_2 = result_2["choices"][0]["message"]["content"]
    if "</think>" in content_2:
        content_2 = content_2.split("</think>")[-1].strip()
    finish_reason_2 = result_2["choices"][0].get("finish_reason", "")
    print(f"👉 답변 2: {content_2}")
    print(f"📊 정지 원인: {finish_reason_2}")

    print("\n✅ 모든 파라미터 제어 테스트 완료!")
    return True


if __name__ == "__main__":
    run_params_sample()

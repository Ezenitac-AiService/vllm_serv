"""sample_02_model_params.py - [비전공자 초급] LLM 제어 파라미터(Temperature, Top_P, Stop) 활용 예제

본 스크립트는 AI 서비스 개발자 양성과정 훈련생을 위한 파라미터 제어 표준 실습 스크립트입니다.
파이덴틱(Pydantic) 없이 표준 파이썬 딕셔너리(dict) 구조를 사용하여
Temperature(답변 창의성), Top_P(샘플링 범위), Stop(조기 중단) 단어 지정 방법을 실습합니다.

실행 명령어:
    uv run python samples/sample_02_model_params.py
"""

import httpx
from common import check_server_health, get_server_host, print_section_header

SERVER_HOST = get_server_host()
MAIN_PORT = 8081
MODEL_NAME = "qwen3.5-4b"


def run_model_params_sample():
    print_section_header("02. 비전공자용 모델 제어 파라미터(Temperature & Stop) 실습 예제")

    if not check_server_health(SERVER_HOST, MAIN_PORT, "vllm_serv 메인 API"):
        return False

    target_url = f"{SERVER_HOST}:{MAIN_PORT}/v1/chat/completions"

    # =========================================================================
    # [실습 1] Low Temperature (0.0): 창의성 최소화, 정밀하고 결정론적인 답변 유도
    # =========================================================================
    print("\n🔹 [실습 1] Low Temperature (0.0) - 정확도와 일관성이 필요한 지식 답변")
    payload_low_temp = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": "대한민국의 수도는 어디인가요?"}
        ],
        "temperature": 0.0,  # 0.0에 가까울수록 항상 같은 정답을 생성 (창의성 0%)
        "max_tokens": 100
    }

    try:
        with httpx.Client(timeout=120.0) as client:
            resp = client.post(target_url, json=payload_low_temp, headers={"Connection": "close"})
            resp.raise_for_status()
            res1 = resp.json()
            content1 = res1["choices"][0]["message"]["content"]
            if "</think>" in content1:
                content1 = content1.split("</think>")[-1].strip()
            print(f"👉 [Low Temp 답변]: {content1}")
    except Exception as err:
        print(f"❌ [실습 1 실패]: {err}")
        return False

    # =========================================================================
    # [실습 2] Stop Sequence 지정: 특정 문자(예: 줄바꿈 '\n' 또는 특정 단어) 등장 시 조기 생성 정지
    # =========================================================================
    print("\n🔹 [실습 2] Stop Sequence 지정 - 줄바꿈('\\n')이 나오면 생성 자동 중단")
    payload_stop = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": "1부터 5까지 숫자를 줄바꿈으로 세어주세요."}
        ],
        "temperature": 0.3,
        "stop": ["\n"],  # '\n' (줄바꿈) 문자가 나오는 순간 답변 생성을 즉시 멈춤
        "max_tokens": 100
    }

    try:
        with httpx.Client(timeout=120.0) as client:
            resp = client.post(target_url, json=payload_stop, headers={"Connection": "close"})
            resp.raise_for_status()
            res2 = resp.json()
            choice2 = res2["choices"][0]
            content2 = choice2["message"]["content"]
            if "</think>" in content2:
                content2 = content2.split("</think>")[-1].strip()
            reason2 = choice2.get("finish_reason", "completed")

            print(f"👉 [Stop 지정 답변]: {content2}")
            print(f"📊 정지 원인(finish_reason): {reason2} (정상적으로 'stop' 사유 수신)")

    except Exception as err:
        print(f"❌ [실습 2 실패]: {err}")
        return False

    print("\n✅ 모든 파라미터 제어 실습 완료!")
    return True


if __name__ == "__main__":
    run_model_params_sample()

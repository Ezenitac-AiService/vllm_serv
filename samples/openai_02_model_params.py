"""openai_02_model_params.py - [비전공자 초급] OpenAI 공식 파라미터(Temperature, Stop) 제어 실습 예제

본 스크립트는 AI 서비스 개발자 양성과정 훈련생을 위한 파라미터 제어 표준 SDK 실습 스크립트입니다.
OpenAI SDK(from openai import OpenAI)의 temperature 및 stop 매개변수를 활용한 제어 기법을 실습합니다.

실행 명령어:
    uv run python samples/openai_02_model_params.py
"""

import os
from openai import OpenAI
from common import check_server_health, load_sample_config, print_section_header

config = load_sample_config()
SERVER_HOST = config["server_host"]
MAIN_PORT = config["main_port"]
MODEL_NAME = config["default_model"]


def run_model_params_sample():
    print_section_header("02. 비전공자용 OpenAI 공식 SDK 모델 제어 파라미터(Temperature & Stop) 실습 예제")

    if not check_server_health(SERVER_HOST, MAIN_PORT, "vllm_serv 메인 API"):
        return False

    base_url = f"{SERVER_HOST}:{MAIN_PORT}/v1"
    api_key = os.environ.get("OPENAI_API_KEY", "EMPTY")
    client = OpenAI(base_url=base_url, api_key=api_key)

    # =========================================================================
    # [실습 1] Low Temperature (0.0): 창의성 최소화, 정밀하고 결정론적인 답변 유도
    # =========================================================================
    print("\n🔹 [실습 1] Low Temperature (0.0) - 정확도와 일관성이 필요한 지식 답변")
    try:
        completion1 = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": "대한민국의 수도는 어디인가요?"}],
            temperature=0.0,
            max_tokens=100
        )
        content1 = completion1.choices[0].message.content or ""
        if "</think>" in content1:
            content1 = content1.split("</think>")[-1].strip()
        print(f"👉 [Low Temp 답변]: {content1}")
    except Exception as err:
        print(f"❌ [실습 1 실패]: {err}")
        return False

    # =========================================================================
    # [실습 2] Stop Sequence 지정: 특정 문자(예: 줄바꿈 '\n') 등장 시 조기 생성 정지
    # =========================================================================
    print("\n🔹 [실습 2] Stop Sequence 지정 - 줄바꿈('\\n')이 나오면 생성 자동 중단")
    try:
        completion2 = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": "1부터 5까지 숫자를 줄바꿈으로 세어주세요."}],
            temperature=0.3,
            stop=["\n"],
            max_tokens=100
        )
        choice2 = completion2.choices[0]
        content2 = choice2.message.content or ""
        if "</think>" in content2:
            content2 = content2.split("</think>")[-1].strip()
        reason2 = choice2.finish_reason or "completed"

        print(f"👉 [Stop 지정 답변]: {content2}")
        print(f"📊 정지 원인(finish_reason): {reason2} (정상적으로 'stop' 사유 수신)")

    except Exception as err:
        print(f"❌ [실습 2 실패]: {err}")
        return False

    print("\n✅ 모든 파라미터 제어 SDK 실습 완료!")
    return True


if __name__ == "__main__":
    run_model_params_sample()

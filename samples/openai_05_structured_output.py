"""openai_05_structured_output.py - [비전공자 초급] OpenAI 공식 파라미터 기반 Pydantic 단일 구조화된 출력(Structured Output) 예제

Pydantic 데이터 모델과 OpenAI SDK(from openai import OpenAI)의 response_format={"type": "json_object"} 규격을 활용하여
LLM 응답을 엄격한 JSON 데이터 객체로 파싱하고 검증하는 예제 스크립트입니다.

실행 명령어:
    uv run python samples/openai_05_structured_output.py
"""

import os
import json
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List

from common import check_server_health, load_sample_config, print_section_header

config = load_sample_config()
SERVER_HOST = config["server_host"]
MAIN_PORT = config["main_port"]
MODEL_NAME = config["default_model"]


# 1. Pydantic 구조화 출력 데이터 모델 정의
class StockCommentItem(BaseModel):
    speaker: str = Field(description="작성자 닉네임")
    category: str = Field(description="실적/재무, 매수/매도 의도, 차트/기술분석, 뉴스/호재·악재, 경영진/주주가치 중 하나")
    sentiment: str = Field(description="매수/긍정, 매도/부정, 중립 중 하나")
    target: str = Field(description="복원된 정식 종목명 (예: 삼성전자, SK하이닉스)")
    sentence: str = Field(description="댓글 원문 문장")
    refined_sentence: str = Field(description="정제된 문장")


class StockAnalysisResponse(BaseModel):
    results: List[StockCommentItem]


def run_structured_output_sample():
    print_section_header("05. 비전공자용 OpenAI 공식 SDK Pydantic 단일 구조화된 출력 예제")

    # 2. 서버 구동 상태 점검
    if not check_server_health(SERVER_HOST, MAIN_PORT, "LLM 메인 서버"):
        print("💡 서버 구동 후 스크립트를 재실행해 주세요.")
        return False

    # 3. OpenAI SDK 클라이언트 초기화
    base_url = f"{SERVER_HOST}:{MAIN_PORT}/v1"
    api_key = os.environ.get("OPENAI_API_KEY", "EMPTY")
    client = OpenAI(base_url=base_url, api_key=api_key)

    print("\n🔹 Pydantic `StockAnalysisResponse` 모델 기반 JSON 스키마 주석 및 파싱")
    json_schema_prompt = json.dumps(StockAnalysisResponse.model_json_schema(), ensure_ascii=False, indent=2)
    messages = [
        {
            "role": "system",
            "content": f"다음 JSON Schema 규격에 맞춰 JSON 객체로만 응답하세요.\n\nJSON Schema:\n{json_schema_prompt}"
        },
        {
            "role": "user",
            "content": "개미왕 (14:03): 삼전이랑 하닉 둘 다 시외 거래에서 급등하길래 바로 줍줍 했습니다."
        }
    ]

    print(f"📡 [SDK 클라이언트 요청] {base_url} (모델: {MODEL_NAME})")

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.1,
            max_tokens=300,
            response_format={"type": "json_object"}
        )

        raw_json = completion.choices[0].message.content or ""
        if "</think>" in raw_json:
            raw_json = raw_json.split("</think>")[-1].strip()

        # Pydantic model_validate_json 으로 엄격 검증 파싱
        parsed_obj = StockAnalysisResponse.model_validate_json(raw_json)
        print("\n✅ [SDK Pydantic 검증 객체 파싱 성공]:")
        for idx, item in enumerate(parsed_obj.results):
            print(f"  [{idx+1}] 화자: {item.speaker} | 대상: {item.target} | 감성: {item.sentiment} | 정제문: {item.refined_sentence}")

        return True

    except Exception as err:
        print(f"❌ [SDK Pydantic 파싱 실패]: {err}")
        return False


if __name__ == "__main__":
    run_structured_output_sample()

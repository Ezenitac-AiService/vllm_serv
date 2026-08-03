"""sample_06_structured_output_batch.py - [비전공자 초급] Pydantic 배치(Batch) 구조화된 출력 httpx 예제

다수의 비정형 문장(여러 개의 주식 댓글 목록)을 단 한 번의 HTTP 요청 배치(Batch)로 LLM에 전송하고,
수신된 JSON 배열을 Pydantic StockAnalysisResponse 모델로 일괄 검증 및 객체 파싱하는 예제 스크립트입니다.

실행 명령어:
    uv run python samples/sample_06_structured_output_batch.py
"""

import json
import httpx
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
    target: str = Field(description="복원된 정식 종목명 (예: 삼성전자, SK하이닉스, 현대차)")
    sentence: str = Field(description="댓글 원문 문장")
    refined_sentence: str = Field(description="정제된 문장")


class StockAnalysisResponse(BaseModel):
    results: List[StockCommentItem]


def run_structured_output_batch_sample():
    print_section_header("06. 비전공자용 Pydantic 배치(Batch) 구조화된 출력 httpx 예제")

    # 2. 서버 구동 상태 점검
    if not check_server_health(SERVER_HOST, MAIN_PORT, "LLM 메인 서버"):
        print("💡 서버 구동 후 스크립트를 재실행해 주세요.")
        return False

    # 3. 다중 비정형 댓글 원문 배치 입력 데이터 구성
    batch_comments = [
        "개미왕 (14:03): 삼전이랑 하닉 둘 다 시외 거래에서 급등하길래 바로 줍줍 했습니다.",
        "차트신 (14:05): 현대차 20일 이동평균선 돌파하면서 거래량 실리는 모습이 긍정적입니다.",
        "네이버보이 (14:08): 네이버 실적 발표 앞두고 목표가 하향 뉴스 나와서 풀매도 쳤습니다."
    ]

    print("\n🔹 Pydantic 배치 `StockAnalysisResponse` 모델 기반 다중 데이터 분석 요청")
    print(f"📝 입력 배치 댓글 수: {len(batch_comments)}개")

    json_schema_prompt = json.dumps(StockAnalysisResponse.model_json_schema(), ensure_ascii=False, indent=2)
    
    comments_payload_text = "\n".join([f"- {c}" for c in batch_comments])
    messages = [
        {
            "role": "system",
            "content": f"다음 JSON Schema 규격에 맞춰 입력된 모든 댓글에 대해 results 배열 객체로 일괄 응답하세요.\n\nJSON Schema:\n{json_schema_prompt}"
        },
        {
            "role": "user",
            "content": f"다음 주식 댓글들을 분석하여 결과를 JSON 배열로 반환하세요:\n{comments_payload_text}"
        }
    ]

    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": 0.1,
        "max_tokens": 600,
        "stream": False,
        "response_format": {"type": "json_object"}
    }

    target_url = f"{SERVER_HOST}:{MAIN_PORT}/v1/chat/completions"
    print(f"📡 [POST] {target_url} 요청 전송 중... (모델: {MODEL_NAME})")

    try:
        with httpx.Client(timeout=120.0) as client:
            response = client.post(target_url, json=payload, headers={"Connection": "close"})
            response.raise_for_status()

            raw_json = response.json()["choices"][0]["message"]["content"]
            if "</think>" in raw_json:
                raw_json = raw_json.split("</think>")[-1].strip()

            # Pydantic model_validate_json 으로 배치 일괄 파싱 및 엄격 검증
            parsed_obj = StockAnalysisResponse.model_validate_json(raw_json)
            print("\n✅ [Pydantic 배치 검증 객체 일괄 파싱 성공]:")
            print("-" * 65)
            for idx, item in enumerate(parsed_obj.results):
                print(f"  [{idx+1}] 화자: {item.speaker} | 대상: {item.target} | 감성: {item.sentiment}")
                print(f"      원문: \"{item.sentence}\"")
                print(f"      정제: \"{item.refined_sentence}\"")
            print("-" * 65)

            return True

    except Exception as err:
        print(f"❌ [Pydantic 배치 파싱 실패]: {err}")
        return False


if __name__ == "__main__":
    run_structured_output_batch_sample()

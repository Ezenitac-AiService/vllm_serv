"""sample_04_reranking.py - vllm_serv BGE Reranker v2 M3 리랭킹 모델 호출 예제

BGE Reranker v2 M3 Cross-Encoder 서빙(기본 포트: 8091)을 사용하여 쿼리 문장과
검색된 문서들 간의 교차 벡터 표현 및 관련도 연동을 수행하는 예제 스크립트입니다.

실행 명령어:
    uv run python samples/sample_04_reranking.py
"""

import httpx
from common import check_server_health, get_server_host, print_section_header

SERVER_HOST = get_server_host()
RERANK_PORT = 8091
API_URL = f"{SERVER_HOST}:{RERANK_PORT}/v1/embeddings"
MODEL_NAME = "bge-reranker-v2-m3"


def run_reranking_sample():
    print_section_header("vllm_serv 04. BGE Reranker v2 M3 Cross-Encoder 호출 예제")

    # 1. 리랭크 전용 서빙 포트(8091) 연결 상태 점검
    if not check_server_health(SERVER_HOST, RERANK_PORT, "BGE Reranker v2 M3 서빙"):
        print("💡 리랭킹 서버가 8091 포트에 구동 중인지 확인해 주세요.")
        return False

    # 2. 쿼리 문장 및 관련도 평가 대상 문서 배치 정의
    query = "반도체 수혜 가능성이 가장 높은 기업"
    documents = [
        "삼성전자 3분기 메모리 반도체 실적 전망 및 수혜 분석",
        "오늘 서울 날씨는 맑고 기온은 25도입니다.",
        "SK하이닉스 고대역폭 메모리(HBM) 공급 확대로 인한 수혜 가능성 극대화"
    ]

    payload = {
        "model": MODEL_NAME,
        "input": [query] + documents
    }

    print(f"📡 [POST] {API_URL} 요청 전송 중... (모델: {MODEL_NAME})")
    print(f"🔍 검색 쿼리: \"{query}\"")
    print(f"📚 대상 문서 개수: {len(documents)}개")

    # 3. HTTP POST 요청 및 응답 처리
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(API_URL, json=payload, headers={"Connection": "close"})
            response.raise_for_status()

            result = response.json()
            data = result.get("data", [])
            print("\n✅ [Cross-Encoder 리랭킹 벡터/응답 수신 성공]")
            print(f"------------------------------------------------------------")
            for idx, item in enumerate(data):
                vec = item.get("embedding", [])
                print(f"  📄 문서 batch #{idx} Vector Dimension: {len(vec)}차원 | 샘플: {vec[:3]}")
            print(f"------------------------------------------------------------")

            return True

    except httpx.HTTPStatusError as err:
        print(f"❌ [HTTP 에러 발생]: {err.response.status_code} - {err.response.text}")
        return False
    except Exception as err:
        print(f"❌ [요청 실패]: {err}")
        return False


if __name__ == "__main__":
    run_reranking_sample()

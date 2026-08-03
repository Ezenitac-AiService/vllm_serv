"""sample_04_reranking.py - [비전공자 초급] BGE Reranker v2 M3 검색 문서 재순위화 httpx 예제

본 스크립트는 AI 서비스 개발자 양성과정 훈련생을 위한 RAG(검색 증강 생성) 문서 재순위화(Reranking) 실습 스크립트입니다.
httpx 라이브러리를 사용하여 질문(Query)과 후보 문서(Documents) 간의 의미적 관련도 점수(Relevance Score)를 측정하고 재정렬합니다.

실행 명령어:
    uv run python samples/sample_04_reranking.py
"""

import httpx
from common import check_server_health, load_sample_config, print_section_header

config = load_sample_config()
SERVER_HOST = config["server_host"]
MAIN_PORT = config["main_port"]
MODEL_NAME = config.get("rerank_model", "bge-reranker-v2-m3")


def run_reranking_sample():
    print_section_header("04. 비전공자용 BGE Reranker v2 M3 문서 관련도 재순위화 httpx 예제")

    # 1. 메인 서빙 데몬(8081 포트) 구동 점검
    if not check_server_health(SERVER_HOST, MAIN_PORT, "vllm_serv 메인 API"):
        return False

    # 2. 질문(Query) 및 후보 문서 목록(Documents) 구성
    query = "vllm_serv 서버의 주요 장점과 사용법은 무엇인가요?"
    documents = [
        "오늘 서울의 날씨는 맑고 기온은 25도입니다.",
        "vllm_serv는 llama.cpp 기반으로 Qwen3.5 및 Gemma4 모델을 GPU VRAM 100% 오프 로딩하여 빠른 속도로 서빙하는 서버입니다.",
        "파이썬 기초 문법에는 변수, 리스트, 딕셔너리, 조건문, 반복문 등이 있습니다."
    ]

    # 3. HTTP 요청 페이로드 구성 (표준 파이썬 dict 사용)
    payload = {
        "model": MODEL_NAME,
        "query": query,
        "documents": documents
    }

    target_url = f"{SERVER_HOST}:{MAIN_PORT}/v1/rerank"
    print(f"📡 [요청 전송] {target_url} (모델: {MODEL_NAME})")
    print(f"❓ 질문 (Query): \"{query}\"")
    print(f"📚 후보 문서 수: {len(documents)}개")

    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(target_url, json=payload, headers={"Connection": "close"})
            resp.raise_for_status()

            # 4. JSON 응답 파싱 및 재순위 결과 추출
            result = resp.json()
            rerank_results = result.get("results", [])

            # 5. 결과 시각적 출력 (관련도 점수 높은 순으로 표시)
            print("\n✅ [문서 재순위화(Reranking) 성공]")
            print("-" * 65)
            for idx, item in enumerate(rerank_results, 1):
                doc_idx = item["index"]
                score = item["relevance_score"]
                doc_text = documents[doc_idx]
                print(f"🥇 [{idx}위] (문서 인덱스: {doc_idx} | 관련도 점수: {score:.4f})")
                print(f"   내용: \"{doc_text}\"")
            print("-" * 65)

            return True

    except Exception as err:
        print(f"❌ [Reranking 실패]: {err}")
        return False


if __name__ == "__main__":
    run_reranking_sample()

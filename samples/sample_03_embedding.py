"""sample_03_embedding.py - [비전공자 초급] BGE M3 단일 및 배치(Batch) 임베딩 수치 벡터 추출 httpx 예제

본 스크립트는 AI 서비스 개발자 양성과정 훈련생을 위한 수치 벡터(Embedding) 추출 표준 실습 스크립트입니다.
httpx 라이브러리를 사용하여 단일 문장 및 다중 문장 묶음(Batch)을 1024차원의 수치 벡터(Vector)로 변환합니다.

실행 명령어:
    uv run python samples/sample_03_embedding.py
"""

import httpx
from common import check_server_health, load_sample_config, print_section_header

config = load_sample_config()
SERVER_HOST = config["server_host"]
EMBEDDING_PORT = config.get("embedding_port", 8090)
MODEL_NAME = config.get("embedding_model", "bge-m3")


def run_embedding_sample():
    print_section_header("03. 비전공자용 BGE M3 단일/배치(Batch) 임베딩 벡터 추출 httpx 예제")

    # 1. 임베딩 서빙 데몬(8090 포트) 구동 점검
    if not check_server_health(SERVER_HOST, EMBEDDING_PORT, "BGE M3 임베딩 서빙"):
        return False

    # 2. 단일 및 배치(Batch) 임베딩 추출 대상 텍스트 리스트 정의
    batch_texts = [
        "vllm_serv는 고성능 LLM 및 임베딩/리랭킹 다중 모델 동시 서빙 플랫폼입니다.",
        "파이썬 기반 AI 서비스 개발자 양성과정 실습 코드 수트입니다.",
        "벡터 데이터베이스 검색 증강 생성(RAG) 파이프라인 구축 기법을 배웁니다."
    ]

    # 3. HTTP 요청 페이로드 구성 (배치 텍스트 배열 전달)
    payload = {
        "model": MODEL_NAME,
        "input": batch_texts
    }

    target_url = f"{SERVER_HOST}:{EMBEDDING_PORT}/v1/embeddings"
    print(f"📡 [요청 전송] {target_url} (모델: {MODEL_NAME})")
    print(f"📝 배치 입력 문장 수: {len(batch_texts)}개")

    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(target_url, json=payload, headers={"Connection": "close"})
            resp.raise_for_status()

            # 4. JSON 응답 파싱 및 벡터 수치 확인
            result = resp.json()
            data_items = result.get("data", [])

            # 5. 배치 수신 결과 출력
            print("\n✅ [배치 임베딩 추출 성공]")
            print("-" * 65)
            for idx, item in enumerate(data_items):
                vector = item["embedding"]
                text_sample = batch_texts[idx] if idx < len(batch_texts) else ""
                print(f"📐 [{idx+1}번 문장] \"{text_sample[:25]}...\"")
                print(f"   - 차원 (Dimension): {len(vector)}차원 | 상위 5개 수치: {vector[:5]}")
            print("-" * 65)
            if "usage" in result:
                print(f"📊 프롬프트 총 토큰: {result['usage'].get('prompt_tokens', 0)}토큰")

            return True

    except Exception as err:
        print(f"❌ [임베딩 추출 실패]: {err}")
        return False


if __name__ == "__main__":
    run_embedding_sample()

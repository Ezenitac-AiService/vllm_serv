"""sample_03_embedding.py - [비전공자 초급] BGE M3 임베딩(Embedding) 추출 예제

본 스크립트는 AI 서비스 개발자 양성과정 훈련생을 위한 수치 벡터(Embedding) 추출 표준 실습 스크립트입니다.
파이덴틱(Pydantic) 모델 대신 표준 파이썬 딕셔너리(dict)를 사용해
텍스트를 1024차원의 의미 수치 벡터(Vector)로 변환하는 방법을 실습합니다.

실행 명령어:
    uv run python samples/sample_03_embedding.py
"""

import httpx
from common import check_server_health, get_server_host, print_section_header

SERVER_HOST = get_server_host()
EMBEDDING_PORT = 8090  # BGE M3 임베딩 서빙 포트
MODEL_NAME = "bge-m3"


def run_embedding_sample():
    print_section_header("03. 비전공자용 BGE M3 임베딩(Embedding) 벡터 추출 예제")

    # 1. 임베딩 서빙 데몬(8090 포트) 구동 점검
    if not check_server_health(SERVER_HOST, EMBEDDING_PORT, "BGE M3 임베딩 서빙"):
        return False

    # 2. 임베딩 추출 대상 텍스트 정의
    input_text = "vllm_serv는 고성능 LLM 및 임베딩/리랭킹 다중 모델 동시 서빙 플랫폼입니다."

    # 3. HTTP 요청 페이로드 구성 (표준 파이썬 dict 사용)
    payload = {
        "model": MODEL_NAME,
        "input": [input_text]
    }

    target_url = f"{SERVER_HOST}:{EMBEDDING_PORT}/v1/embeddings"
    print(f"📡 [요청 전송] {target_url} (모델: {MODEL_NAME})")
    print(f"📝 입력 텍스트: \"{input_text}\"")

    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(target_url, json=payload, headers={"Connection": "close"})
            resp.raise_for_status()

            # 4. JSON 응답 파싱 및 벡터 수치 확인
            result = resp.json()
            embedding_data = result["data"][0]
            vector = embedding_data["embedding"]

            # 5. 결과 시각적 출력 (상위 5개 수치 샘플링)
            print("\n✅ [임베딩 추출 성공]")
            print("-" * 65)
            print(f"📐 임베딩 벡터 차원 (Dimension): {len(vector)}차원")
            print(f"🔢 벡터 수치 샘플 (상위 5개): {vector[:5]}")
            print("-" * 65)
            if "usage" in result:
                print(f"📊 프롬프트 토큰: {result['usage'].get('prompt_tokens', 0)}토큰")

            return True

    except Exception as err:
        print(f"❌ [임베딩 추출 실패]: {err}")
        return False


if __name__ == "__main__":
    run_embedding_sample()

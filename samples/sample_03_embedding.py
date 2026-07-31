"""sample_03_embedding.py - vllm_serv BGE M3 임베딩 모델 호출 예제

BGE M3 임베딩 서버(기본 포트: 8090)의 OpenAI 규격 API(/v1/embeddings)를 사용하여
텍스트 문장을 1024차원 수치 둥둥소수점 벡터 배열로 변환하는 예제 스크립트입니다.

실행 명령어:
    uv run python samples/sample_03_embedding.py
"""

import httpx
from common import check_server_health, print_section_header

SERVER_HOST = "http://127.0.0.1"
EMBEDDING_PORT = 8090
API_URL = f"{SERVER_HOST}:{EMBEDDING_PORT}/v1/embeddings"
MODEL_NAME = "bge-m3"


def run_embedding_sample():
    print_section_header("vllm_serv 03. BGE M3 임베딩(Embedding) 모델 호출 예제")

    # 1. 임베딩 전용 서빙 포트(8090) 연결 상태 점검
    if not check_server_health(SERVER_HOST, EMBEDDING_PORT, "BGE M3 임베딩 서버"):
        print("💡 임베딩 서버가 8090 포트에 구동 중인지 확인해 주세요.")
        return False

    # 2. 임베딩 대상 문장 정의
    input_text = "vllm_serv는 고성능 LLM 및 임베딩/리랭킹 다중 모델 동시 서빙 플랫폼입니다."

    payload = {
        "model": MODEL_NAME,
        "input": input_text
    }

    print(f"📡 [POST] {API_URL} 요청 전송 중... (모델: {MODEL_NAME})")
    print(f"📝 입력 텍스트: \"{input_text}\"")

    # 3. HTTP POST 요청 및 응답 처리
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(API_URL, json=payload, headers={"Connection": "close"})
            response.raise_for_status()

            result = response.json()
            data = result.get("data", [])
            if not data:
                print("❌ [오류]: 응답 데이터에 embedding 벡터가 없습니다.")
                return False

            vector = data[0].get("embedding", [])
            vector_dim = len(vector)

            print("\n✅ [임베딩 추출 성공]")
            print(f"------------------------------------------------------------")
            print(f"📐 임베딩 벡터 차원 (Dimension): {vector_dim}차원")
            print(f"🔢 벡터 값 샘플 (상위 5개 수치): {vector[:5]}")
            print(f"------------------------------------------------------------")
            if "usage" in result:
                print(f"📊 프롬프트 토큰: {result['usage'].get('prompt_tokens', 0)}토큰")

            return True

    except httpx.HTTPStatusError as err:
        print(f"❌ [HTTP 에러 발생]: {err.response.status_code} - {err.response.text}")
        return False
    except Exception as err:
        print(f"❌ [요청 실패]: {err}")
        return False


if __name__ == "__main__":
    run_embedding_sample()

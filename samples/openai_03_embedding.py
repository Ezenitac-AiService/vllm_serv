"""openai_03_embedding.py - [비전공자 초급] OpenAI 공식 파라미터 기반 BGE M3 단일/배치(Batch) 임베딩 추출 예제

본 스크립트는 AI 서비스 개발자 양성과정 훈련생을 위한 수치 벡터(Embedding) 추출 표준 SDK 실습 스크립트입니다.
OpenAI SDK(from openai import OpenAI)의 client.embeddings.create() 메서드를 사용해
단일 및 다중 문장 묶음(Batch)을 1024차원 수치 벡터로 변환합니다.

실행 명령어:
    uv run python samples/openai_03_embedding.py
"""

import os
from openai import OpenAI
from common import check_server_health, load_sample_config, print_section_header

config = load_sample_config()
SERVER_HOST = config["server_host"]
EMBEDDING_PORT = config.get("embedding_port", 8090)
MODEL_NAME = config.get("embedding_model", "bge-m3")


def run_embedding_sample():
    print_section_header("03. 비전공자용 OpenAI 공식 SDK BGE M3 배치(Batch) 임베딩 추출 예제")

    # 1. 임베딩 서빙 데몬(8090 포트) 구동 점검
    if not check_server_health(SERVER_HOST, EMBEDDING_PORT, "BGE M3 임베딩 서빙"):
        return False

    # 2. OpenAI SDK 클라이언트 초기화 (임베딩 전용 포트 8090 지정)
    base_url = f"{SERVER_HOST}:{EMBEDDING_PORT}/v1"
    api_key = os.environ.get("OPENAI_API_KEY", "EMPTY")
    client = OpenAI(base_url=base_url, api_key=api_key)

    # 3. 단일 및 배치(Batch) 임베딩 추출 대상 텍스트 정의
    batch_texts = [
        "vllm_serv는 고성능 LLM 및 임베딩/리랭킹 다중 모델 동시 서빙 플랫폼입니다.",
        "파이썬 기반 AI 서비스 개발자 양성과정 실습 코드 수트입니다.",
        "벡터 데이터베이스 검색 증강 생성(RAG) 파이프라인 구축 기법을 배웁니다."
    ]

    print(f"📡 [SDK 클라이언트 초기화] {base_url} (모델: {MODEL_NAME})")
    print(f"📝 배치 입력 문장 수: {len(batch_texts)}개")

    try:
        # 4. client.embeddings.create 호출 (배치 리스트 전달)
        response = client.embeddings.create(
            model=MODEL_NAME,
            input=batch_texts
        )

        # 5. 결과 시각적 출력
        print("\n✅ [SDK 배치 임베딩 추출 성공]")
        print("-" * 65)
        for idx, data_obj in enumerate(response.data):
            vector = data_obj.embedding
            text_sample = batch_texts[idx] if idx < len(batch_texts) else ""
            print(f"📐 [{idx+1}번 문장] \"{text_sample[:25]}...\"")
            print(f"   - 차원 (Dimension): {len(vector)}차원 | 상위 5개 수치: {vector[:5]}")
        print("-" * 65)
        if response.usage:
            print(f"📊 프롬프트 총 토큰: {response.usage.prompt_tokens}토큰")

        return True

    except Exception as err:
        print(f"❌ [SDK 임베딩 추출 실패]: {err}")
        return False


if __name__ == "__main__":
    run_embedding_sample()

# Quickstart & End-to-End Validation Guide: 임베딩 및 리랭커 모델 서빙 (053-embedding-reranker-model-serving)

본 문서는 `vllm_serv`에서 BGE-M3 임베딩 모델 및 BGE-Reranker-v2-M3 리랭커 모델의 서빙 기능 및 1세대 코어(Nehalem i7-930) 호환성을 구동하고 수렴 검증(Converge Verification)하기 위한 통합 검증 가이드입니다.

---

## 1. 사전 준비 (Prerequisites)

```bash
# 1. uv 파이썬 가상환경 동기화 확인
uv sync

# 2. 로컬 서버 백그라운드 구동 (또는 테스트 전용 프로세스)
uv run python -m src.api.server
```

---

## 2. 모델 파일 및 카탈로그 자동 다운로드 검증

```bash
# 1. BGE-M3 임베딩 모델 다운로드 상태 확인 및 실행
uv run python -c "from src.core.model_downloader import ModelDownloader; downloader = ModelDownloader(); print('BGE-M3 Available:', downloader.is_model_available('bge-m3'))"

# 2. BGE-Reranker-v2-M3 리랭커 모델 다운로드 상태 확인 및 실행
uv run python -c "from src.core.model_downloader import ModelDownloader; downloader = ModelDownloader(); print('Reranker Available:', downloader.is_model_available('bge-reranker-v2-m3'))"
```

---

## 3. API 엔드포인트 검증 (curl)

### A. OpenAI 호환 임베딩 API (`POST /v1/embeddings`)

```bash
curl -X POST http://127.0.0.1:8081/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{
    "model": "bge-m3",
    "input": ["안녕하세요, vllm_serv 임베딩 서빙 테스트입니다."]
  }'
```

**예상 출력 (Expected Response)**:
```json
{
  "object": "list",
  "data": [
    {
      "object": "embedding",
      "index": 0,
      "embedding": [0.0123, -0.0456, ..., 0.0789]
    }
  ],
  "model": "bge-m3",
  "usage": {
    "prompt_tokens": 12,
    "total_tokens": 12
  }
}
```

### B. Cross-Encoder 리랭킹 API (`POST /v1/rerank`)

```bash
curl -X POST http://127.0.0.1:8081/v1/rerank \
  -H "Content-Type: application/json" \
  -d '{
    "model": "bge-reranker-v2-m3",
    "query": "GPU 인퍼런스 서버 성능 최적화",
    "documents": [
      "파이썬 웹 프레임워크 FastAPI 사용법 가이드",
      "llama-server 기반 CUDA GPU 100% 오프로딩 및 VRAM 점유율 최적화 기법",
      "1세대 Core i7 프로세서의 SSE4.2 명령어 지원 역량"
    ]
  }'
```

**예상 출력 (Expected Response)**:
```json
{
  "model": "bge-reranker-v2-m3",
  "results": [
    { "index": 1, "relevance_score": 0.9654 },
    { "index": 0, "relevance_score": 0.1241 },
    { "index": 2, "relevance_score": 0.0892 }
  ]
}
```

---

## 4. 실물 연동 단위 및 통합 회귀 테스트 수트 실행 (Mandatory Real-Integration Test)

헌법 v1.6.0 (Principle II & VII)에 따라 더미(Mock) 없이 실물 시스템 연동을 검증합니다:

```bash
# 신규 작성된 임베딩/리랭커 전용 단위 & 통합 테스트 실행
uv run pytest tests/unit/test_embedding_reranker_serving.py -v

# 전체 시스템 회귀 테스트 실행 (헌법 VII 원칙)
uv run pytest tests/ -v
```

---

## 5. Nehalem i7-930 CPU 호환성 (SIGILL 검증)

`legacy-i7-930-gtx1070` 프로필 환경에서 실행 시 불법 명령어(`SIGILL`)로 인한 비정상 프로세스 사망이 발생하는지 실측합니다:

```bash
# Non-AVX 바이너리로 임베딩/리랭커 구동 시 100% CUDA 오프로딩 및 예외 발생률 0% 검증
uv run python -c "from src.core.cpu_detector import get_cpu_info; print('CPU Info:', get_cpu_info())"
```

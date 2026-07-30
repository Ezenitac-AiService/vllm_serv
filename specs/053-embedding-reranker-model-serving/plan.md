# Implementation Plan: 임베딩(Embedding) 및 리랭커(Reranker) 모델 서빙 지원 및 1세대 코어(Nehalem) CPU 호환성 검증 (053-embedding-reranker-model-serving)

**Branch**: `053-embedding-reranker-model-serving` | **Date**: 2026-07-30 | **Spec**: [spec.md](file:///home/dev/storage/vllm_serv/specs/053-embedding-reranker-model-serving/spec.md)

**Input**: Feature specification from `/specs/053-embedding-reranker-model-serving/spec.md`

---

## Summary

`vllm_serv` 서빙 시스템에 **BGE-M3 밀집 벡터 임베딩 모델**(`ggml-org/bge-m3-Q8_0-GGUF`)과 **BGE-Reranker-v2-M3 크로스 인코더 리랭킹 모델**(`klnstpr/bge-reranker-v2-m3-Q8_0-GGUF`)의 멀티 프로세스 서빙 아키텍처를 도입합니다.
`ProcessManager`가 LLM(8089 포트) 인스턴스와 함께 임베딩(8090 포트) 및 리랭커(8091 포트) 전용 `llama-server` 백엔드 프로세스를 동시 자동 기동하고 상주시키며, `inference_api.py` 프록시를 통해 OpenAI 호환 `POST /v1/embeddings` 및 표준 `POST /v1/rerank` 엔드포인트를 투명 포워딩합니다.
또한, 1세대 코어(Nehalem i7-930, AVX/AVX2 미지원) CPU 프로필 하에서 Non-AVX 타겟 바이너리와 CUDA 100% 오프로딩(`-ngl 99`)을 결합하여 불법 명령어(`SIGILL`) 충돌 없는 레거시 CPU 호환 구동을 실체적으로 보장합니다.

---

## Technical Context

**Language/Version**: Python 3.11+ (C++20 for `llama.cpp` native binaries)

**Primary Dependencies**: FastAPI, Pydantic v2, httpx, llama-server (`llama.cpp` CUDA build)

**Storage**: Local GGUF Model Directory (`models/bge-m3/`, `models/bge-reranker-v2-m3/`), SQLite (`data/metrics.db`)

**Testing**: `pytest`, `pytest-asyncio`, `uv run pytest`

**Target Platform**: Linux x86_64 (GTX 1070 8GB / GTX 1080 Ti 11GB / RTX 3060 12GB), Nehalem i7-930 Non-AVX Legacy CPU Server

**Project Type**: Python Web Service & C++ Inference Engine Reverse-Proxy Server

**Performance Goals**: `POST /v1/embeddings` 응답 지연시간 < 50ms (단일 문장), `POST /v1/rerank` 응답 지연시간 < 100ms (3개 문서 재정렬), CUDA GPU 100% 오프로드

**Constraints**: 전 플랫폼 Q8_0 단일 양자화 적용, 임베딩+리랭커+LLM 동시 상주 시 VRAM 합계 예산 준수 (GTX 1070 8GB 기준 VRAM 여유 > 1.2GB 보장)

**Scale/Scope**: 3개 독립 프로세스 상주, 2개 전용 API 엔드포인트 (`/v1/embeddings`, `/v1/rerank`), 카탈로그 엔트리 2개 추가

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] 계획서가 한국어로 작성되었는가? (언어 정책)
- [x] 테스트 코드 작성 계획이 포함되어 있는가? (`tests/unit/test_embedding_reranker_serving.py` 작성 계획 수록) (테스트 필수 원칙)
- [x] 목업은 유료/제한 API로 엄격히 제한하고 실물 시스템/소켓/OS 인자 및 실제 호출 플래그(REAL_API_CALL=1) 기반 실측 검증 계획이 포함되어 있는가? (실체적 테스트 및 수렴 검증 원칙)
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (종료 조건 명확화 원칙)
- [x] 비파괴적 문서 수정 원칙을 준수하는가? (비파괴적 문서 수정 원칙)
- [x] uv 패키지 매니저 및 가상환경 격리 표준(uv run)을 준수하는가? (uv 패키지 및 환경 관리 원칙)
- [x] 전체 회귀 테스트 수트 및 Playwright 기반 E2E 브라우저 실측 검증 계획이 포함되어 있는가? (의무적 회귀 테스트 및 브라우저 E2E 검증 원칙)

---

## Project Structure

### Documentation (this feature)

```text
specs/053-embedding-reranker-model-serving/
├── plan.md              # Implementation Plan (/speckit-plan command output)
├── research.md          # Phase 0 research output
├── data-model.md        # Phase 1 data model specification
├── quickstart.md        # Phase 1 quickstart validation guide
├── contracts/           # Phase 1 API contract specifications
│   ├── embeddings-api.json
│   └── rerank-api.json
└── tasks.md             # Phase 2 tasks breakdown (/speckit-tasks command output)
```

### Source Code (repository root)

```text
src/
├── core/
│   ├── config_manager.py        # TaskTypeEnum 및 ModelCatalogEntry 스키마 확장
│   ├── model_downloader.py      # BGE-M3 & Reranker GGUF 카탈로그 연동
│   ├── process_manager.py       # 멀티 인스턴스 (LLM/Embedding/Reranker) 프로세스 생주 관리
│   └── llama_manager.py         # 임베딩/리랭커 전용 포트 헬스체크 및 기동 헬퍼
├── api/
│   ├── routes/
│   │   ├── inference_api.py     # POST /v1/embeddings & POST /v1/rerank 다이렉트 프록시 라우팅
│   │   └── dashboard_api.py   # 대시보드 상태 모니터링 연동
│   └── server.py                # lifespan 멀티 인스턴스 자동 기동 및 커넥션 풀 초기화
config/
├── model_catalog.json           # bge-m3 (task_type: embedding) & bge-reranker-v2-m3 (task_type: rerank) 추가
└── server_config.json          # embedding_backend_port(8090) 및 rerank_backend_port(8091) 설정

tests/
├── unit/
│   └── test_embedding_reranker_serving.py # 단위 & 통합 실체 검증 테스트 수트
└── e2e/
    └── test_dashboard_e2e.py    # Playwright E2E 대시보드 검증
```

**Structure Decision**: Single project layout with Python FastAPI proxy layer, Pydantic v2 core managers, and llama-server multi-instance backend orchestration.

---

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| 백엔드 프로세스 3개 동시 기동 (포트 8089, 8090, 8091) | RAG 연속 요청(검색->리랭크->생성) 시 디스크 I/O 및 로딩 지연 없이 실시간 처리 | 모델 온디맨드 스왑 방식은 요청당 2~5초 지연 유발하여 서빙 불가능 |

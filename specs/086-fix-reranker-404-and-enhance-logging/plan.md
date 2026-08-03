# Implementation Plan: 리랭커 모델 404 오류 원인 해결 및 프록시/Auxiliary 상세 로깅 고도화

**User Specs Reference**: `/specs/086-fix-reranker-404-and-enhance-logging/`  
**Target Branch**: `main` / `086-fix-reranker-404-and-enhance-logging`  

---

## 1. Technical Context & Scope

- **Affected Components**:
  - `src/api/routes/inference_api.py` (POST /v1/rerank 프록시 시도 및 백엔드 404 수신 시 8091 백엔드 /v1/embeddings 벡터 추출 + Cosine Similarity 재순위화 어댑터 처리 및 [RerankerProxyError] 다중 행 로깅 추가)
  - `src/core/auxiliary_manager.py` (Reranker 8091 스폰 전 `_cleanup_zombie_on_port(8091)` 포트 소켓 가드 추가)
  - `src/core/client_logger.py` (구조화된 `[RerankerProxyError]` 로깅 포맷터 및 `logs/error.log`, `logs/server.log` 다중 핸들러 기록 지원)
  - `config/model_catalog.json` (Reranker 모델 `bge-reranker-v2-m3` 포트 8091 카탈로그 바인딩 검증)
  - `tests/integration/test_sample_scripts_and_reranker.py` (Reranker 프록시 200 OK 통합 테스트)

---

## 2. Constitution Check

- **Principle I (Korean Language)**: All docs in Korean -> PASS
- **Principle II & III (Zero Mock)**: Real HTTP socket & reranker endpoint execution -> PASS
- **Principle VII (Full Regression Testing)**: Run pytest after edits -> PASS

---

## 3. Planned Touch-Points & Work Phases

### Phase 0: Research & Requirements (Complete)
- Created `research.md` (FastAPI /v1/rerank 프록시 어댑터 및 RerankerProxyError 로깅 설계).

### Phase 1: Design & Contracts (Complete)
- Created `data-model.md`, `contracts/rerank-api-contract.json`, `quickstart.md`.

### Phase 2: Implementation (To be generated via `/speckit-tasks`)
- Task 1: `src/core/auxiliary_manager.py` 스폰 전 `_cleanup_zombie_on_port(8091)` 포트 소켓 정리
- Task 2: `src/api/routes/inference_api.py` /v1/rerank 프록시 시도 후 404 시 8091 백엔드 `/v1/embeddings` 벡터 추출 및 Cosine Similarity 재순위화 어댑터 처리 및 `[RerankerProxyError]` 로깅 추가
- Task 3: `tests/integration/test_sample_scripts_and_reranker.py` 통합 테스트 갱신
- Task 4: `uv run samples/sample_04_reranking.py` 및 pytest 검증

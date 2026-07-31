# Research & Architecture Decisions: 보조 모델(임베딩/리랭킹) 구동 및 벤치마크 개선

**Feature**: `062-fix-aux-models-benchmark`
**Created**: 2026-07-31

## 1. Technical Context & Investigation Summary

### 1.1 Root Cause 1: BGE M3 (`bge-m3`) 실측 추론 실패 (`Step 4: ⚠️ 실측 추론 실패`)
- **원인 분석**: `scripts/benchmark_quality.py`의 `request_live_inference()`는 모든 모델에 대해 `/v1/chat/completions` 엔드포인트에 대화형 프롬프트 패킷을 전송함. 그러나 `bge-m3`는 임베딩 전용 모델(`--embedding` 모드로 구동)이므로 대화 생성 API 호출 시 400/500 에러를 반환하여 추론 실패로 처리됨.
- **해결 방안**: `model_catalog.json`의 `task_type`이 `embedding`인 경우, `/v1/embeddings` 엔드포인트로 JSON 패킷(`{"input": "...", "model": "bge-m3"}`)을 전송하고 벡터 배열(`data[0].embedding`) 수신 여부 및 처리 지연 시간을 측정하도록 벤치마크 분기 처리.

### 1.2 Root Cause 2: BGE Reranker v2 M3 (`bge-reranker-v2-m3`) 헬스체크 타임아웃 (`Step 3: ❌ 헬스체크 타임아웃`)
- **원인 분석**: Cross-Encoder Reranker 모델은 `llama-server` 백엔드 구동 시 `--reranking` 및 적절한 컨텍스트 인자(`--embedding` / `--reranking`)가 지정되어야 정상 로딩됨. 또한 일반 LLM 대비 로딩 시 소요 시간과 `/v1/models` 혹은 `/health` 응답 특성이 다르며, 프로세스 스폰 시 CLI 인자 미전달로 인해 백엔드가 로딩 중 멈춤.
- **해결 방안**: `ProcessManager.spawn_process()` 실행 시 `task_type == "rerank"`일 경우 `llama-server` 인자에 `--reranking` 및 `--embedding` 플래그를 정확히 전달하고, 헬스체크 대기 시간을 적응형(최대 30초)으로 보장함.

### 1.3 Root Cause 3: 벤치마크 종료 후 메인 서버 프로세스 종료 (`UNLOADED`)
- **원인 분석**: `benchmark_quality.py` 종료 직전 `finally` 블록에서 `llama_manager.ensure_default_model_resident()`를 비동기 호출하였으나, 벤치마크 파이썬 프로세스가 종료되면서 asyncio 이벤트 루프와 자식 프로세스 소켓/파이프가 함께 닫혀 서빙 프로세스가 SIGHUP/SIGTERM으로 종료됨.
- **해결 방안**:
  1. 벤치마크 스크립트 복원 단계에서 파이썬 자식 프로세스 형태 대신, 디태치(detached background process / `nohup` 또는 `start_server.sh` 유틸리티) 방식으로 메인 API 서버 및 보조 모델(Co-loading)을 복원 스폰함.
  2. `./status_server.sh` 및 `start_server.sh` 연동을 보장하여 스크립트가 완전히 종료된 후에도 `qwen3.5-4b`, `bge-m3`, `bge-reranker-v2-m3` 메인/보조 프로세스가 GPU VRAM 상주 구동(`RUNNING`) 상태를 지속 유지하도록 구현.

### 1.4 Root Cause 4: 대시보드 API 프록시 무한 타임아웃 에러
- **원인 분석**: 메인 API 서버(8081)가 실행된 직후, 백엔드 LLM 엔진(8089)이 로딩 중이거나 아직 소켓 바인딩을 안 끝낸 상태에서 대시보드 프론트엔드가 `/v1/chat/completions` 혹은 `/dashboard/api/playground`를 호출하면 `httpx.AsyncClient` 프록시 요청이 무한 대기 후 타임아웃에 진입함.
- **해결 방안**:
  1. `src/api/routes/inference_api.py` 역방향 프록시 레이어에 백엔드 엔진 소켓/헬스 프리플라이트 가드(Preflight Guard)를 수록.
  2. 백엔드가 미준비 상태일 때 무한 대기를 차단하고 `503 Service Unavailable` ("LLM Backend Engine Initializing") 응답을 1초 내 즉시 반환하여 대시보드 UI에 초기화 상태 메시지를 표시.

---

## 2. Research Decisions & Alternatives Considered

| Technical Choice | Selected Option | Rationale | Alternatives Considered |
|------------------|-----------------|-----------|-------------------------|
| **Embedding Verification** | `/v1/embeddings` API 호출 | OpenAI 호환 규격 표준 응답 검증 및 차원 크기 수신 확인 | 더미 응답 수신 (헌법 위반으로 기각) |
| **Reranker Verification** | `/rerank` / `/v1/rerank` 및 OpenAI 호환 검증 | Cross-Encoder 백엔드 구동 검증 | 미검증 스킵 (기각) |
| **Post-Benchmark Restoration** | 디태치 백그라운드 멀티 모델 데몬 구동 (`start_server.sh` / subprocess detach) | 파이썬 이벤트 루프 종료 시 프로세스 종료 방지 | 단순 파이썬 자식 프로세스 로딩 (이벤트 루프 종료 시 죽음으로 기각) |
| **Proxy Timeout Prevention** | Preflight Health Check Guard & 503 Immediate Response | 대시보드 무한 타임아웃 방지 및 사용자 UX 직관성 제공 | 무한 타임아웃 수동 폴링 대기 (기각) |

---

## 3. Architecture Impact

1. `scripts/benchmark_quality.py`:
   - 모델별 `task_type` (`llm`, `embedding`, `rerank`) 감지 로직 추가
   - Task별 맞춤형 HTTP 추론 함수 (`request_live_embedding`, `request_live_rerank`) 분기 수록
   - `Post-Benchmark` 복원 시 독립 디태치 서빙 실행 함수 호출
2. `src/core/process_manager.py`:
   - `bge-m3` 및 `bge-reranker-v2-m3` 스폰 시 `--embedding` 및 `--reranking` 백엔드 CLI 인자 주입
3. `src/core/auxiliary_manager.py`:
   - `ensure_embedding_resident`, `ensure_rerank_resident` 백그라운드 수렴 및 복원 로직 보강
4. `src/api/routes/inference_api.py` & `dashboard_api.py`:
   - 백엔드 LLM 엔진(8089) 헬스체크 프리플라이트 가드 도입 (미준비 시 503 즉시 반환)

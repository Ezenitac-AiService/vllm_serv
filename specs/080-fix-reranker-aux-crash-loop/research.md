# Phase 0 Research: 보조 모델 크래시 루프 방지 및 프록시 503 게이트 (`080-fix-reranker-aux-crash-loop`)

## Research Topics & Decisions

### 1. 보조 모델 무한 크래시 루프 차단 (Crash Recovery Circuit Breaker)

- **선택된 방안**: `AuxiliaryModelManager` 내부 각 보조 모델(`embedding`, `rerank`)별로 `consecutive_crashes` 카운터를 도입하고, 최대 허용 연속 크래시 횟수(기본값: 3회) 초과 시 상태를 `ProcessStatusEnum.DISABLED`로 전환하여 `_crash_recovery_loop`에서 재시작 시도를 즉시 중단합니다.
- **채택 사유**: VRAM OOM으로 인해 백엔드 프로세스가 계속 크래시할 때 5초마다 무한 재시작을 시도하면 CPU/GPU 자원이 낭비되고 로그가 오염됩니다. Circuit Breaker 패턴을 적용하여 일정 횟수 실패 후 안전하게 비활성화하는 것이 안정적입니다.
- **카운터 리셋 조건**: 모델 헬스체크 성공 시(`ProcessStatusEnum.READY` 도달 시) `consecutive_crashes = 0`으로 초기화하여 간헐적 크래시에 대한 정상 자동 복구 능력을 유지합니다.
- **기용된 대안 검토**:
  - *무한 재시작 유지 + 지연시간(backoff)증가*: 백엔드가 성공할 가능성이 없는 VRAM 부족 상태에서 로그 오염만 지속되므로 기각.
  - *첫 실패 시 즉시 중단*: 간헐적 네트워크/타임아웃 일시 오류 시 복구 기회를 상실하므로 3회 연속 실패 기준 선택.

### 2. 보조 모델 순차 초기화 (Sequential Initialization)

- **선택된 방안**: `AuxiliaryModelManager.start_auto_startup_and_recovery()`에서 Embedding과 Reranker를 `asyncio.create_task`로 동시 비동기 생성하던 방식을 **순차(Sequential) 생성**으로 변경합니다 (Embedding `ensure_resident` 완료 후 Reranker `ensure_resident` 시작).
- **채택 사유**: GTX 1070 (8,192MB VRAM) 환경에서 메인 LLM(qwen3.5-4b, 5,500MB) 상주 후 남은 VRAM은 2,692MB입니다. Embedding(605MB)과 Reranker(606MB)의 정적 합계는 1,211MB로 여유(1,481MB) 내에 있지만, 두 프로세스가 **동시에** CUDA 그래픽 맥락 및 메모리를 초기화할 때 피크 VRAM이 8GB를 초과하여 OOM 크래시가 발생합니다. 순차 초기화를 적용하면 초기화 피크 오버헤드가 분산되어 8GB VRAM 내에서 두 보조 모델이 모두 정상 상주할 수 있게 됩니다.
- **기용된 대안 검토**:
  - *동시 초기화 유지*: GTX 1070 플랫폼에서 OOM 크래시가 100% 재현되므로 기각.

### 3. 역방향 프록시 READY 게이트 및 DISABLED 503 즉시 반환

- **선택된 방안**: `src/api/routes/inference_api.py`의 `reverse_proxy` 함수에서 보조 모델 엔드포인트(`rerank`, `reranking`, `embeddings`, `embedding`) 요청 수신 시 `ensure_*_resident`의 반환 상태(`ProcessState.status`)를 검사합니다.
  - `status == ProcessStatusEnum.READY`: 정상 백엔드 포트로 HTTP 프록시 포워딩
  - `status == ProcessStatusEnum.DISABLED`: on-demand 재시도 없이 즉시 `HTTP 503 Service Unavailable` 반환
  - `status in (ERROR, LOADING, UNLOADED)`: `ensure_*_resident` 호출 후에도 READY 상태가 아니면 즉시 `HTTP 503 Service Unavailable` 반환
- **채택 사유**: 기존 코드는 `ensure_*_resident`를 `await`만 하고 결과 상태를 검증하지 않아, 백엔드가 로딩에 실패하거나 크래시된 상태에서도 백엔드 포트(8091)로 프록시 포워딩을 시도하여 404 Not Found 또는 Connection Refused 에러가 발생했습니다. 게이트를 둠으로써 404를 원천 차단하고 503과 정확한 원인 메시지("Reranker model is not available. The model may have failed to load due to insufficient VRAM.")를 제공합니다.

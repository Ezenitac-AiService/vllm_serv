# Feature Specification: 보조 모델(Embedding/Reranker) 크래시 루프 및 `/v1/rerank` 404 근본 해결 (`080-fix-reranker-aux-crash-loop`)

**Feature Directory**: [`specs/080-fix-reranker-aux-crash-loop`](file:///home/dev/storage/vllm_serv/specs/080-fix-reranker-aux-crash-loop)  
**Created**: 2026-08-03  
**Status**: Draft  

---

## Clarifications

### Session 2026-08-03

- Q: DISABLED 상태인 보조 모델에 `/v1/rerank` 요청 도착 시 on-demand 재구동을 시도해야 하는가? → A: DISABLED이면 즉시 503 반환 (서버 재시작 또는 명시적 API 호출로만 복구)
- Q: 보조 모델 동시 초기화 vs 순차 초기화? → A: 보조 모델 순차 초기화 (Embedding 완료 후 Reranker 시작) + 크래시 루프 차단 병행

---

## 1. Overview & Business Value

`vllm_serv` 서버 구동 시 보조 모델(Embedding `bge-m3`, Reranker `bge-reranker-v2-m3`)이 구동 직후 반복적으로 크래시(Crash)하면서 무한 재시작 루프에 빠지는 근본 문제를 해결합니다.

### 근본 원인 (`server.log` 증거 기반)

1. **VRAM 부족에 의한 보조 프로세스 즉시 OOM 크래시**: GTX 1070 (VRAM 8,192MB) 환경에서 메인 LLM(`qwen3.5-4b`, 5,500MB) + Embedding(`bge-m3`, 605MB) + Reranker(`bge-reranker-v2-m3`, 606MB) 3개 모델의 정적 합계는 6,711MB로 8,192MB 이내이나 여유가 **1,481MB**에 불과합니다. `start_auto_startup_and_recovery()`에서 Embedding과 Reranker를 `asyncio.create_task()`로 **동시에** spawn하여 CUDA 임시 버퍼·KV 캐시·런타임 오버헤드가 합산되면 피크 VRAM이 8GB를 초과하여 OOM 크래시가 발생합니다. GTX 1080 Ti (11,264MB) 및 RTX 3060 (12,288MB) 플랫폼에서는 VRAM 여유분이 4,500MB 이상으로 이 문제가 발생하지 않습니다.
2. **무한 크래시 재시작 루프**: `_crash_recovery_loop`(5초 간격)가 크래시를 감지하고 즉시 `ensure_rerank_resident` / `ensure_embedding_resident`를 호출하지만, 동일한 VRAM 부족 조건에서 다시 크래시하는 무한 루프가 발생합니다.
3. **프록시 경로 폴백으로도 404 미해결**: 079 기능에서 구현한 `reverse_proxy` 후보 경로 자동 탐색(Path Fallback)이 동작하더라도, 8091 포트 백엔드 자체가 READY 상태에 도달하지 못하므로 모든 후보 경로에서 404 또는 Connection Refused가 반환됩니다.

### `server.log` 핵심 증거

```
[AuxiliaryManager] Spawning reranker instance (bge-reranker-v2-m3) on port 8091...
[AuxiliaryManager] FR-007: Reranker process crash detected! Auto-restarting...
[AuxiliaryManager] Spawning reranker instance (bge-reranker-v2-m3) on port 8091...
[AuxiliaryManager] FR-007: Reranker process crash detected! Auto-restarting...
...
INFO: 192.168.0.80:52032 - "POST /v1/rerank HTTP/1.1" 404 Not Found
```

→ Reranker 프로세스가 spawn → crash → re-spawn → crash 무한 반복 중 `/v1/rerank` 요청이 도착하여 404 반환.

---

## 2. User Personas & Scenarios

- **Persona**: AI 애플리케이션 개발자 / RAG 파이프라인 운영자
- **Scenario**:
  1. 서버 구동 후 `sample_04_reranking.py` 및 `sample_03_embedding.py`를 호출할 때, 보조 모델 프로세스가 안정적으로 READY 상태에 도달하고 HTTP 200 OK 응답을 수신합니다.
  2. VRAM 부족 환경에서 보조 모델 중 하나가 구동 실패 시, 시스템이 무한 크래시 루프에 빠지지 않고 최대 재시작 횟수 초과 후 안정적으로 DISABLED 상태로 전환되며 메인 LLM 서비스에 영향을 주지 않습니다.

---

### User Story 1 - 보조 모델 크래시 무한 루프 차단 및 재시작 횟수 제한 (Priority: P1)

보조 모델(Embedding/Reranker) 프로세스가 `spawn` 직후 반복 크래시 시, `_crash_recovery_loop`가 **최대 재시작 횟수(Max Restart Count)**를 초과하면 해당 모델을 DISABLED 상태로 전환하여 무한 루프를 차단해야 합니다.

**Why this priority**: 무한 크래시 루프는 CPU/GPU 자원을 낭비하고, 로그를 오염시키며, 메인 LLM 서비스 성능에 간접적으로 영향을 줄 수 있습니다.

**Independent Test**: 보조 모델이 연속 3회 크래시 시 자동으로 DISABLED 상태로 전환되고, 이후 재시작 시도가 중단되는지 검증합니다.

**Acceptance Scenarios**:

1. **Given** 보조 모델이 VRAM 부족 등의 이유로 `spawn` 직후 크래시할 때, **When** `_crash_recovery_loop`가 3회 연속 크래시를 감지하면, **Then** 해당 모델은 DISABLED 상태로 전환되고 추가 재시작 시도가 중단됩니다.
2. **Given** 보조 모델이 DISABLED 상태일 때, **When** 클라이언트가 `/v1/rerank` 요청을 전송하면, **Then** on-demand 재구동을 시도하지 않고 즉시 503 응답과 안내 메시지를 반환합니다. 서버 전체 재시작 또는 명시적 관리 API 호출로만 DISABLED 상태를 복구할 수 있습니다.

---

### User Story 2 - 보조 모델 READY 대기 후 프록시 전달 보장 (Priority: P1)

`reverse_proxy`가 `/v1/rerank` 또는 `/v1/embeddings` 요청을 수신했을 때, `ensure_rerank_resident` / `ensure_embedding_resident` 호출 결과 해당 모델이 READY 상태인 경우에만 백엔드에 프록시 전달하고, READY가 아닌 경우(ERROR, DISABLED, LOADING 타임아웃) 명확한 503 에러와 안내 메시지를 반환해야 합니다.

**Why this priority**: 현재 코드는 `ensure_*_resident`를 호출만 하고 결과 상태를 확인하지 않아, 백엔드가 READY가 아닌 상태에서도 프록시 전달을 시도하여 404가 발생합니다.

**Independent Test**: 보조 모델이 ERROR/DISABLED 상태일 때 `/v1/rerank` 요청 시 404 대신 503과 명확한 안내 메시지가 반환되는지 검증합니다.

**Acceptance Scenarios**:

1. **Given** 8091 Reranker 백엔드가 ERROR 또는 DISABLED 상태일 때, **When** 클라이언트가 `POST /v1/rerank`를 전송하면, **Then** 404가 아닌 503 Service Unavailable과 "Reranker model is not available. The model may have failed to load due to insufficient VRAM." 안내 메시지를 수신합니다.
2. **Given** 8091 Reranker 백엔드가 정상 READY 상태일 때, **When** 클라이언트가 `POST /v1/rerank`를 전송하면, **Then** HTTP 200 OK와 재순위화 결과를 정상 수신합니다.

---

### Edge Cases

- **VRAM 충분 환경**: 보조 모델이 정상 구동되면 크래시 카운터가 0으로 리셋되어 이후 간헐적 크래시에도 정상 복구됩니다.
- **모든 보조 모델 DISABLED**: 메인 LLM 서비스(`/v1/chat/completions`)는 영향 없이 정상 동작하며, 대시보드에 보조 모델 상태가 DISABLED로 표시됩니다.
- **`ensure_*_resident` 호출 중 타임아웃**: 30초 헬스체크 타임아웃 후 ERROR 상태로 전환되며, 프록시는 503을 반환합니다.
- **동시 요청 경쟁 조건**: 여러 `/v1/rerank` 요청이 동시에 도착해도 `ensure_rerank_resident`가 중복 spawn을 방지해야 합니다.

---

## 3. Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `_crash_recovery_loop`에 최대 연속 재시작 횟수 제한(기본값: 3회)이 구현되어 무한 루프가 차단되어야 함.
- **DoD-002**: `reverse_proxy`에서 `ensure_*_resident` 호출 결과를 검증하여 READY가 아닌 경우 503 에러와 명확한 안내 메시지를 반환해야 함.
- **DoD-003**: `sample_04_reranking.py` 호출 시 보조 모델이 READY 상태이면 200 OK, 아니면 503과 안내 메시지를 수신해야 함 (404 에러 0건).
- **DoD-004**: 통합 테스트 수트 작성 및 통과.

---

## 4. Requirements *(mandatory)*

### Functional Requirements

- **FR-001 (크래시 루프 차단)**: `auxiliary_manager.py`의 `_crash_recovery_loop`는 각 보조 모델에 대해 연속 크래시 카운터를 유지하고, 최대 재시작 횟수(기본값: 3회) 초과 시 해당 모델을 DISABLED 상태로 전환하여 추가 재시작을 중단해야 한다.
- **FR-002 (READY 상태 게이트)**: `inference_api.py`의 `reverse_proxy`는 `ensure_*_resident` 호출 후 반환된 `ProcessState.status`를 검증하여 READY가 아닌 경우(ERROR, DISABLED, LOADING 타임아웃) 백엔드 프록시 전달 없이 즉시 503 응답과 안내 메시지를 반환해야 한다. 특히 DISABLED 상태에서는 on-demand 재구동을 시도하지 않고 즉시 503을 반환하여 매 요청마다 spawn → crash 지연이 발생하는 것을 방지한다.
- **FR-003 (정상 구동 시 카운터 리셋)**: 보조 모델이 성공적으로 READY 상태에 도달하면 연속 크래시 카운터를 0으로 초기화하여, 이후 간헐적 크래시에 대해 정상 복구가 가능하도록 해야 한다.
- **FR-004 (보조 모델 순차 초기화)**: `start_auto_startup_and_recovery()`에서 Embedding과 Reranker를 동시(`asyncio.create_task`)가 아닌 순차적(Embedding READY 확인 후 Reranker 시작)으로 초기화하여, VRAM이 제한된 플랫폼(GTX 1070 등)에서 동시 초기화 피크 VRAM 초과에 의한 OOM 크래시를 방지해야 한다.

---

## 5. Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 보조 모델 크래시 시 무한 재시작 루프 발생 건수 0회.
- **SC-002**: `/v1/rerank` 요청 시 404 Not Found 응답 발생 건수 0회 (READY 상태이면 200 OK, 아니면 503).
- **SC-003**: 보조 모델이 READY 상태에서 `/v1/rerank` 호출 시 200 OK 성공률 100%.

---

## 6. Assumptions

- GTX 1070 (VRAM 8,192MB) 환경에서 메인 LLM(`qwen3.5-4b`, 5,500MB) + 보조 모델(605+606=1,211MB) 합계 6,711MB는 정적으로 8GB 이내이나, 동시 초기화 피크 VRAM 및 CUDA 런타임 오버헤드로 보조 모델 구동이 실패할 수 있습니다. 순차 초기화로 피크 VRAM을 줄여 해결합니다.
- 최대 연속 재시작 횟수 기본값 3회는 프로젝트 설정(`server_config.json`)에서 조정 가능하도록 합니다.
- 서버 재시작 시 크래시 카운터는 자동으로 0으로 초기화됩니다.

# Feature Specification: 동적 모델 스위칭(Model Switching) 정상화 및 샘플 연동 개선 (Fix & Enhance Dynamic Model Switching in Server & Samples)

**Feature Name**: `fix-model-switching`  
**Feature Directory**: `specs/116-fix-model-switching`  
**Status**: Draft  
**Created**: 2026-08-08  

## User Value & Business Need

사용자 및 SDK 클라이언트가 `POST /v1/chat/completions` 요청 시 `model` 파라미터로 카탈로그 상의 다른 LLM 모델(예: `gemma4-e4b`, `qwen3.5-2b` 등)을 요청하거나, `sample_04_model_switch.py` 및 `openai_04_model_switch.py` 예제 스크립트를 구동할 때, 서버가 해당 모델을 VRAM에 실제로 핫스왑(Hot-Swap) 로드하여 요청한 모델로 추론이 수행되도록 보장합니다.

---

## Clarifications

### Session 2026-08-08
- Q: 동적 모델 핫스왑(Model Hot-Swap) 진행 중 동일/다른 모델에 대한 동시 요청(Concurrent Requests) 처리 방식 → A: `llama_manager` 내 `asyncio.Lock`을 활용하여 핫스왑 작업을 직렬화하고 동시 요청을 순차 큐잉하여 핫스왑 완료 후 응답 처리.

---

## User Stories & Acceptance Scenarios

### Story 1: POST /v1/chat/completions 자동 모델 핫스왑 지원 (Priority: P1) 🎯 MVP

**User Role**: OpenAI SDK / API 사용자 및 클라이언트 애플리케이션  

**As a** API 서비스 이용자  
**I want** `POST /v1/chat/completions` 요청 payload에 현재 서빙 중인 모델과 다른 `model` ID(예: `gemma4-e4b`)를 지정하여 호출할 때, 서버가 백엔드 LLM 엔진을 자동으로 해당 모델로 스위칭/로드하기를 원한다.  
**So that** 서버를 수동 재시작하거나 별도의 핫스왑 API를 따로 호출하지 않고도 표준 OpenAI SDK 호출만으로 원하는 모델로 전환하여 추론 결과를 받을 수 있다.

#### Acceptance Scenarios

1. **Scenario 1.1: 다른 모델 요청 시 자동 핫스왑 로드**:
   - **Given**: 서버에서 `qwen3.5-4b`가 VRAM 상주 서빙 중인 상태
   - **When**: 클라이언트가 `POST /v1/chat/completions` 요청으로 `model: "qwen3.5-2b"` 전달
   - **Then**: 서버가 기존 모델을 VRAM에서 안전 해제(Unload) 후 `qwen3.5-2b`를 핫스왑 로드(Load)하여 해당 모델의 응답을 반환한다.

2. **Scenario 1.2: 동일 모델 연속 요청 시 핫스왑 생략**:
   - **Given**: 서버에서 `qwen3.5-2b`가 이미 VRAM 상주 서빙 중인 상태
   - **When**: 클라이언트가 `POST /v1/chat/completions` 요청으로 동일한 `model: "qwen3.5-2b"` 전달
   - **Then**: 모델 재로딩 없이 즉시 기존 서빙 프로세스로 고속 추론을 수행한다.

3. **Scenario 1.3: 동시 모델 핫스왑 요청 시 큐잉 처리**:
   - **Given**: 모델 핫스왑 로드가 진행 중인 상태
   - **When**: 다른 클라이언트가 동시 요청 전송
   - **Then**: 요청이 `asyncio.Lock` 큐에 대기한 후 핫스왑 완료 및 서버 준비(`READY`) 완료 시 안전하게 순차 처리된다.

---

## Functional Requirements (FR-###)

- **FR-001**: `POST /v1/chat/completions` 라우트(`src/api/routes/inference_api.py`)에서 요청 payload의 `model` ID가 현재 서빙 중인 `llama_manager.process_manager.state.model_id`와 다를 경우, 백엔드 `llama_manager.load_model_with_download(requested_model)`를 자동 호출하여 원자적 핫스왑을 수행해야 한다.
- **FR-002**: 모델 핫스왑 시 `asyncio.Lock`을 통해 핫스왑 전 과정을 비동기 수동 lock 처리하여 동시 요청 충돌을 방지하고, 기존 VRAM 점유 메모리를 완전 해제(`nvidia-smi` 검증)한 후 신규 모델을 VRAM 100% 오프로드하여 헬스체크(`is_ready()`) 완료 후 요청을 처리해야 한다.
- **FR-003**: `sample/sample_04_model_switch.py` 및 `sample/openai_04_model_switch.py` 스크립트는 모델 전환에 필요한 타임아웃 마진(180초 이상) 및 핫스왑 응답 처리를 올바르게 수행해야 한다.
- **FR-004**: 모델 전환 실패 시(예: 가중치 미존재, VRAM 초과) 명확한 503/400 HTTP 에러 응답 및 이유를 클라이언트에 반환해야 한다.

---

## Success Criteria (SC-###)

- **SC-001**: `POST /v1/chat/completions`로 다른 모델 ID 전송 시 100% 실제 백엔드 모델 핫스왑 구동 및 해당 모델 응답 반환.
- **SC-002**: `uv run sample/openai_04_model_switch.py` 및 `uv run sample/sample_04_model_switch.py` 에러 없이 100% 정상 완진.
- **SC-003**: 모델 전환 시 VRAM 메모리 누수 0건.

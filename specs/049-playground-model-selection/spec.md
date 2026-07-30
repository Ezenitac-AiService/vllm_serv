# Feature Specification: AI Playground 동적 모델 선택 및 서버 온로드 모델 자동 동기화 (049-playground-model-selection)

**Feature Branch**: `049-playground-model-selection`  
**Created**: 2026-07-30  
**Status**: Draft  
**Input**: User request: "서버 온로드 모델 변경 시 Playground 기본 선택 모델 자동 동기화 및 드롭다운 선택 기능 추가, 대시보드 TTFT/Latency/Token 카운트 메트릭 복구"

---

## Clarifications

### Session 2026-07-30

- Q: Playground 모델 선택 드롭다운 전환 시 서버 연동 방식 → A: 서버에서 온로드 모델 변경 시 Playground 기본 모델이 자동 동기화되며, 사용자가 Playground 드롭다운에서 선택한 모델은 질문 보내기(Send Message) 버튼 클릭 시 추론 요청 파라미터로 즉시 적용
- Q: Playground 지표 카드(TTFT, 총 소요시간, 토큰 수) 실시간 표시 및 모델 선택 드롭다운 갱신 → A: Option A (SSE 메트릭 파싱 교정 - TTFT, Latency, Token Count 실시간 표출 + 모델 선택 드롭다운 및 서버 온로드 모델 완벽 연동)

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 서버 온로드 모델 자동 기본 선택 및 Playground 드롭다운 전환 (Priority: P1) 🎯 MVP

AI Playground의 설정 패널에 모델 선택 드롭다운(`Select Model`)을 제공하고, 서버가 온로드 중인 현재 활성 모델(`current_model`)을 기본값으로 자동 선택합니다.

- **서버 온로드 모델 동기화**: 대시보드 로딩 시 `GET /dashboard/api/capabilities`를 조회하여 현재 온로드된 모델을 드롭다운 기본값으로 자동 선택하고 활성 모델 배지(`Model: <name>`)를 즉시 갱신합니다.
- **모델 변경 제어**: 사용자가 드롭다운에서 이용 가능한 모델 중 원하는 모델을 선택하고 "🚀 Send Message" 클릭 시 선택된 모델명으로 추론이 전송됩니다.

**Why this priority**: 관리자가 서버의 로딩 모델을 변경하였을 때 Playground에서 이전 모델명이나 잘못된 기본값이 사용되는 문제를 방지하고 직관적인 모델 테스트 환경을 제공합니다.

**Independent Test**:
1. 대시보드 진입 시 `#pg-model-select` 드롭다운에 서버의 실제 온로드 모델명이 자동 선택되는지 확인.
2. 드롭다운 선택 변경 후 전송 시, 선택한 모델명이 API 요청 바디 및 SSE 스트리밍 헤더에 정상 반영되는지 확인.

---

### User Story 2 - 실시간 추론 지표 표출 (TTFT, TPS, Latency, Tokens) (Priority: P1)

Playground 추론 완료 시 TTFT(ms), 초당 토큰 생성 속도(tok/s), 총 소요시간(s), 및 입력/출력 토큰 카운트를 메트릭 카드로 정확히 표출합니다.

- **메트릭 표시**: `ttft_ms`, `token_speed_tok_s`, `total_latency_s`, `prompt_tokens / completion_tokens` 실시간 갱신.

**Why this priority**: 모델 성능(응답 속도 및 비용 측정)을 한눈에 파악할 수 있어야 합니다.

**Independent Test**:
1. 추론 완료 후 TTFT, 총 소요시간, 입력/출력 토큰 수가 화면에 정상 표시되는지 확인.

---

## Functional Requirements *(mandatory)*

- **FR-001**: `src/api/static/index.html` Playground 패널에 모델 선택 드롭다운 요소(`<select id="pg-model-select">`)를 추가해야 한다.
- **FR-002**: `src/api/static/app.js`에서 `GET /dashboard/api/capabilities` 응답을 처리할 때, `available_models` 목록으로 `#pg-model-select` 드롭다운 옵션을 생성하고 `current_model`을 기본 선택값으로 자동 지정해야 한다.
- **FR-003**: 관리자 모드에서 모델 적용(`applyPreset`) 또는 언로드 완료 시 Playground의 모델 선택 드롭다운 및 활성 모델 배지(`Model: <name>`)를 실시간으로 자동으로 업데이트해야 한다.
- **FR-004**: Playground 추론 요청 시 사용자가 선택한 `#pg-model-select` 값을 요청 객체의 `model` 필드로 전송해야 한다.
- **FR-005**: 헌법 v1.5.2에 따라 모델 동적 선택 및 온로드 연동 단위 테스트 수트(`tests/unit/test_playground_model_selection.py`)를 수록해야 한다.
- **FR-006**: 서버에서 모델이 온로드/변경되면 Playground의 선택 드롭다운 기본값이 자동으로 갱신되며, 사용자가 드롭다운에서 선택한 모델은 질문 전송(Send Message) 버튼을 클릭할 때 해당 요청의 `model` 파라미터로 즉시 적용되어야 한다.
- **FR-007**: SSE 스트리밍 연동 시 `metrics` 이벤트의 `ttft_ms`, `total_latency_s`, `prompt_tokens`, `completion_tokens` 데이터를 정상 파싱하여 UI 메트릭 바에 실시간으로 표시해야 한다.

---

## Success Criteria *(mandatory)*

- **SC-001**: 서버 모델 변경 시 Playground 기본 모델 자동 동기화 성공률 **100%**.
- **SC-002**: 드롭다운 모델 변경 후 추론 및 메트릭 표출 성공률 **100%**.

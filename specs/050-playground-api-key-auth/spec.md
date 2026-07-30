# Feature Specification: API Key 필수 모드 시 Playground 인증 처리 및 API Key 입력 지원 (050-playground-api-key-auth)

**Feature Branch**: `050-playground-api-key-auth`  
**Created**: 2026-07-30  
**Status**: Draft  
**Input**: User request: "API 키 필수 옵션을 켰을 때 플레이그라운드 호출 처리 로직 및 인증 인터페이스 추가"

---

## Clarifications

### Session 2026-07-30

- Q: API Key Required 모드가 OFF(퍼블릭 모드)일 때 Playground API Key 입력 필드 동작 방식 → A: Option A (OFF일 때는 선택 입력 Optional, ON일 때만 필수 검증 Required & 401 차단)

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - API Key 필수 모드(`api_key_enabled`) 활성화 시 Playground 인증 처리 (Priority: P1) 🎯 MVP

대시보드의 보안 설정에서 "API Key Required Mode"가 활성화(ON)되었을 때, Playground 추론 테스트 시 사용자 API Key를 검증하여 인증된 요청만 허용합니다.

- **API Key 입력 필드 제공**: Playground 설정 패널에 API Key 입력 항목(`API Key (Optional / Required)`)을 제공하여 사용자가 자신의 API Key(`sk-vllm-...`)를 지정할 수 있도록 합니다.
- **필수 모드 검증 및 401 오류 처리**: `api_key_enabled`가 `true`일 때, Playground 추론 요청에 유효한 API Key가 포함되지 않으면 401 Unauthorized 오류 메시지를 안전하게 반환하고 UI에 "🔑 API Key required in Security Mode" 경고 안내를 표시합니다.
- **자동 키 동기화 지원**: 사용자가 관리자 탭에서 발급한 유효한 API Key가 존재하는 경우, Playground의 API Key 입력란에 자동 채움/선택 옵션을 제공합니다.

**Why this priority**: API Key 필수 보안 모드가 켜져 있음에도 Playground가 무인증으로 무제한 추론을 수행할 수 있는 보안 우회 허점을 방지합니다.

**Independent Test**:
1. API Key 필수 모드 ON 설정 후 API Key 없이 Playground 추론 시도 시 401 경고 및 차단 확인.
2. 유효한 API Key(`sk-vllm-...`) 입력 후 추론 시 정상 SSE 스트리밍 및 해당 API Key로 지표 DB 기재 확인.

---

## Functional Requirements *(mandatory)*

- **FR-001**: `src/api/routes/dashboard_api.py`의 `GET /dashboard/api/capabilities` 응답에 현재 보안 설정 상태인 `api_key_enabled: bool` 필드를 추가해야 한다.
- **FR-002**: `src/api/static/index.html` Playground 설정 패널에 API Key 입력 필드(`<input id="pg-api-key" placeholder="sk-vllm-...">`)를 추가해야 한다.
- **FR-003**: `/dashboard/api/playground` 및 `/dashboard/api/playground/stream` 엔드포인트는 `api_key_enabled`가 `true`일 때, 요청 헤더(`X-API-Key` / `Authorization`) 또는 페이로드의 `api_key` 값을 검증하여 유효하지 않거나 미입력 시 401 Unauthorized 에러를 반환해야 한다.
- **FR-004**: API Key 인증 성공 시 `metrics_db` 및 로깅 시스템에 해당 `api_key` 식별자로 추론 기록을 로깅해야 한다.
- **FR-005**: 헌법 v1.5.2에 따라 API Key 필수 모드 연동 및 Playground 401 인증 처리 단위 테스트 수트(`tests/unit/test_playground_api_key_auth.py`)를 수록해야 한다.
- **FR-006**: 보안 모드가 OFF(Disabled)일 경우 Playground의 API Key 입력 필드는 선택 사항(Optional)으로 작동하며, 키를 입력 시 해당 키 식별자로 로그를 기록하고 비워둘 경우 anonymous로 기록해야 한다.

---

## Success Criteria *(mandatory)*

- **SC-001**: API Key 필수 모드 상태에서 미인증 Playground 호출 401 차단 성공률 **100%**.
- **SC-002**: 유효한 API Key 입력 시 추론 및 메트릭 기록 정상 작동 성공률 **100%**.

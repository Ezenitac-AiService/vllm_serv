# Feature Specification: 대시보드 UI 회귀 버그 원인 분석, 근본 수리 및 Playwright E2E 테스트 수트 구축 (052-fix-dashboard-ui-regressions-and-playwright-e2e)

**Feature Branch**: `052-fix-dashboard-ui-regressions-and-playwright-e2e`  
**Created**: 2026-07-30  
**Status**: Draft  
**Input**: User report & Root Cause Analysis: "관리자 모달 버튼, 서버 설정 폼 제출 시 탭 리셋 버그 등 UI 회귀 결함에 대한 원인 분석, 방어 코드 적용 및 Playwright 기반 E2E 자동화 테스트 수트 구축"

---

## Clarifications

### Session 2026-07-30

- Q: UI 회귀 원인 분석 및 Playwright E2E 방침 → A: Option A (pytest-playwright 브라우저 E2E 테스트 수트 구축 + app.js DOM 바인딩 전체 Optional Chaining ?. 방어 수리)

---

## Root Cause Analysis (원인 분석)

1. **Python API 단위 테스트와 JS DOM 실행 환경의 분리 한계**:
   - 기존 `pytest` 테스트 수트는 FastAPI 백엔드 HTTP JSON 응답만 검증하였으며, 실제 웹 브라우저 내 Vanilla JS 이벤트 핸들러 바인딩 및 DOM 조작을 검증하는 E2E 테스트 체계가 부재했습니다.
2. **단일 DOM 바인딩 오류로 인한 전체 JS 스크립트 중단**:
   - `app.js`에서 `elements.modalCloseBtn` 프로퍼티가 누락되었을 때, `elements.modalCloseBtn.addEventListener` 호출부에서 `TypeError: Cannot read properties of undefined` 예외가 발생하여 **이후 모든 이벤트 리스너(관리자 모달 로그인/취소, 폼 제출 preventDefault) 등록이 중단**되었습니다.
3. **Form 기본 제출 동작(Native Page Reload) 발생**:
   - `manualForm` 리스너가 등록되지 않음으로 인해 "Apply Configuration" 클릭 시 브라우저 기본 Form 제출(새로고침)이 실행되어 페이지가 초기 탭(Live Metrics)으로 리셋되는 증상이 발생하였습니다.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - UI 회귀 버그 근본 수리 및 방어 프로그래밍 (Priority: P1) 🎯 MVP

대시보드에서 🔒 Admin Login 버튼 클릭 시 모달이 닫히거나 로그인 검증이 정상 동작하며, "Apply Configuration" Form 제출 시 페이지 새로고침 없이 비동기로 설정이 변경되고 현재 탭 위치가 안전하게 유지됩니다.

- **관리자 인증 모달 정상화**: "Authentication" 버튼 클릭 시 비밀키 검증 후 모달이 닫히고, "Cancel" 버튼 클릭 시 예외 없이 모달이 닫힙니다.
- **Form 제출 새로고침 차단 (`e.preventDefault()`)**: 수동 설정 Form 제출 시 브라우저 기본 제출 동작을 차단하고 탭 위치를 유지합니다.
- **Optional Chaining (`?.`) 방어 프로그래밍**: `app.js` 내 모든 DOM 이벤트 바인딩 시 `?.addEventListener` 방어 프로그래밍을 적용하여 개별 요소 결함 시에도 전체 스크립트가 죽지 않도록 수리합니다.

**Why this priority**: 관리자 기능 접근 불가능 및 설정 적용 시 탭 리셋 현상을 해결하고 프론트엔드의 구조적 내구성을 확보합니다.

**Independent Test**:
1. 🔒 Admin Login 버튼 클릭 후 인증 모달에서 "Cancel" 및 "Authentication" 버튼이 정상 작동하는지 확인.
2. "Model & Config" 탭에서 설정 변경 후 "Apply Configuration" 클릭 시 페이지 새로고침 없이 비동기 적용 및 탭 위치 유지 검증.

---

### User Story 2 - Playwright E2E 자동화 회귀 테스트 수트 구축 (Priority: P1) 🎯 MVP

실제 헤드리스 브라우저 환경에서 대시보드의 4개 탭, 모달, 폼 제출, 버튼 기능이 정상 동작하는지 검증하는 Playwright E2E 테스트 수트(`tests/e2e/test_dashboard_ui.py`)를 구축합니다.

- **4개 탭 전환 검증**: Live Metrics → Model & Config → AI Playground → Audit 탭 클릭 시 화면 전환 및 데이터 로드 검증.
- **모달 및 폼 인터랙션 검증**: 관리자 인증 모달 열기/닫기/인증, 수동 설정 Form 제출 시 새로고침 방지 검증.
- **자동화 실행 검증**: `uv run pytest tests/e2e/test_dashboard_ui.py` 명령으로 실제 브라우저 내 100% 성공 검증.

**Why this priority**: 자동화된 브라우저 E2E 검증 체계를 통해 차후 UI 회귀 버그 재발을 원천 차단합니다.

**Independent Test**:
1. `uv run pytest tests/e2e/test_dashboard_ui.py -v` 명령으로 Playwright E2E 수트 실행 시 전체 시나리오 통과 확인.

---

## Functional Requirements *(mandatory)*

- **FR-001**: `src/api/static/app.js`의 `elements` 객체에 누락된 `modalCloseBtn: document.getElementById('modal-close-btn')`을 복원하고, 모든 이벤트 리스너 바인딩에 Optional Chaining(`elements.modalCloseBtn?.addEventListener`) 및 null 방어 프로그래밍을 적용하여 단일 요소 누락으로 전체 스크립트 실행이 중단되는 현상을 근본 방지해야 한다.
- **FR-002**: `manualForm` 폼 제출 이벤트 리스너 첫 줄에 `e.preventDefault()`를 필수 실행하고, 폼 제출 시 페이지가 새로고침되어 첫 번째 탭으로 리셋되는 결함을 차단해야 한다.
- **FR-003**: 관리자 로그인 버튼, 취소 버튼, Unload 버튼, 코드 내보내기 버튼 등 대시보드 내 모든 뷰 버튼의 클릭 이벤트가 정상 렌더링 및 핸들링되도록 보충해야 한다.
- **FR-004**: `pytest-playwright` 기반의 실제 Headless 브라우저 E2E 회귀 테스트 수트(`tests/e2e/test_dashboard_ui.py`)를 수록하여 4개 탭 전환, 관리자 로그인/취소 모달, 폼 제출 및 페이지 새로고침 방지 동작을 자동 검증해야 한다.

---

## Success Criteria *(mandatory)*

- **SC-001**: 관리자 인증 모달 (로그인/취소 버튼) 동작 성공률 **100%**.
- **SC-002**: 서버 설정 적용 폼 제출 시 탭 리셋 현상 발생률 **0%** (페이지 새로고침 방지).
- **SC-003**: Playwright E2E 회귀 테스트 수트 성공률 **100%**.

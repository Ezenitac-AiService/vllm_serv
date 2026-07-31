# Tasks: AI Playground 생각 태그 UI 제어(보이기/접기/끄기), 마크다운 렌더링 및 대화 이력 사이드바 (048-think-tag-ui-markdown)

**Input**: `/specs/048-think-tag-ui-markdown/` 디자인 문서 (`plan.md`, `spec.md`, `research.md`, `data-model.md`, `quickstart.md`)  
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `quickstart.md`

---

## Phase 1: Setup (공통 기반 작업)

**목적**: 프로젝트 static HTML 및 CDN 라이브러리 추가

- [x] T001 [P] `src/api/static/index.html`에 `marked.js`, `DOMPurify`, `highlight.js` CDN 스크립트 및 CSS 링크 주입

---

## Phase 2: Foundational (선행 블로킹 전제조건)

**목적**: 대화 이력 영구 저장을 위한 SQLite DB 테이블 및 세션 CRUD API 구축

- [x] T002 `src/core/metrics_db.py`에 `playground_sessions` 및 `playground_messages` SQLite 테이블 마이그레이션 구현
- [x] T003 `src/api/routes/dashboard_api.py`에 세션 목록 조회/생성/삭제 및 메시지 내역 조회 REST API 구현

---

## Phase 3: User Story 1 - AI Playground 3단 생각 태그 UI 모드 (보이기/접기/끄기) (Priority: P1) 🎯 MVP

**목적**: 컨트롤 패널 3단 토글 버튼 (`👁️ Show`, `📁 Collapse`, `🚫 Off`) 구축 및 생각 블록 독립 분리 & 아코디언 접기/펼침

**독립 테스트**: 3단 모드 토글 클릭 시 기존 및 신규 생각 블록의 렌더링 상태가 실시간으로 동적 전환되는지 검증

### User Story 1 테스트

- [x] T004 [P] [US1] `tests/unit/test_think_tag_ui_markdown.py`에 3단 토글 모드 처리 단위 테스트 수트 작성

### User Story 1 구현

- [x] T005 [US1] `src/api/static/index.html`에 생각 표시 모드 3단 토글 버튼 그룹 추가 및 `src/api/static/style.css`에 생각 전용 블록/아코디언 스타일 정의
- [x] T006 [US1] `src/api/static/app.js`에 `ThinkDisplayMode` 상태 관리, 스트리밍 중 노출 및 `</think>` 수신 시 아코디언 자동 접힘 로직 구현

---

## Phase 4: User Story 2 - LLM 응답 본문 2026 최신 웹 마크다운 렌더링 (Priority: P1)

**목적**: `marked.js` + `DOMPurify` + `highlight.js` 기반으로 코드 블록, 표, 리스트 실시간 포맷팅 렌더링

**독립 테스트**: 마크다운 텍스트 및 코드 블록 생성 시 안전한 HTML 구문 강조 포맷팅 렌더링 검증

### User Story 2 테스트

- [x] T007 [P] [US2] `tests/unit/test_think_tag_ui_markdown.py`에 마크다운 이스케이프 및 XSS 필터링 검증 테스트 작성

### User Story 2 구현

- [x] T008 [US2] `src/api/static/app.js`에 `marked.parse()`, `DOMPurify.sanitize()`, `hljs.highlightAll()` 마크다운 렌더링 파이프라인 연동

---

## Phase 5: User Story 3 - Google AI Studio 스타일 좌측 대화 이력 사이드바 (Priority: P1)

**목적**: 좌측 접이식 대화 이력 사이드바(`+ New Chat`, 세션 목록, 클릭 복원, 🗑️ 세션 삭제) 구축 및 DB 영구 저장

**독립 테스트**: 세션 전환 및 새로고침 후 과거 대화 복원/삭제 정상 작동 검증

### User Story 3 테스트

- [x] T009 [P] [US3] `tests/unit/test_think_tag_ui_markdown.py`에 대화 세션 CRUD REST API 엔드포인트 단위 테스트 작성

### User Story 3 구현

- [x] T010 [US3] `src/api/static/index.html`에 좌측 접이식 사이드바 HTML 구조(`+ New Chat`, 세션 목록) 추가 및 `src/api/static/style.css` 레이아웃 디자인 적용
- [x] T011 [US3] `src/api/static/app.js`에 세션 목록 불러오기, 세션 선택 전환, 세션 삭제(🗑️), `+ New Chat` 신규 세션 생성 및 새로고침 시 자동 복원 핸들러 연동

---

## Phase 6: Polish & Cross-Cutting Concerns (다듬기 및 마무리)

**목적**: 전체 회귀 테스트 검증 및 문서 업데이트

- [x] T012 [P] `uv run pytest tests/unit/test_think_tag_ui_markdown.py tests/unit/test_think_tag_stripping.py tests/unit/test_real_llm_playground_payload.py tests/unit/test_llm_payload_viewer.py -v` 전체 회귀 검증 수행
- [x] T013 [P] `specs/048-think-tag-ui-markdown/quickstart.md`에 최종 테스트 결과 및 UI 검증 기록 갱신

---

## Dependencies & Execution Order (의존성 및 실행 순서)

### Phase Dependencies

- **Setup (Phase 1)**: 의존성 없음 - 즉시 시작 가능
- **Foundational (Phase 2)**: Phase 1 완료 후 시작 가능 - US3 세션 API 전제조건
- **User Stories (Phase 3+)**: Phase 1 & 2 완료 후 진행 (US1, US2, US3 독립 수행 가능)
- **Polish (Phase 6)**: 모든 사용자 스토리 완료 후 진행

---

## Implementation Strategy (구현 전략)

### MVP First (User Story 1 & 2)

1. Phase 1: Setup 완료 (CDN 라이브러리 주입)
2. Phase 2: Foundational 완료 (DB 세션 테이블)
3. Phase 3 & 4: User Story 1 & 2 구현 (3단 토글 모드 + 마크다운 렌더링)
4. 독립 검증: `uv run pytest tests/unit/test_think_tag_ui_markdown.py` 실행

### Full Delivery

1. User Story 3 완료 (Google AI Studio 스타일 좌측 대화 이력 사이드바)
2. Phase 6 Polish 전체 회귀 검증 완료

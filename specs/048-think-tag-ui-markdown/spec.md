# Feature Specification: AI Playground 생각 태그 UI 제어(보이기/접기/끄기), 마크다운 렌더링 및 대화 이력 사이드바 (048-think-tag-ui-markdown)

**Feature Branch**: `048-think-tag-ui-markdown`  
**Created**: 2026-07-30  
**Status**: Draft  
**Input**: User feedback: "think 태그 스트리밍 완료 시 접기, 보이기/접기/끄기 3단 모드 버튼 구현, 별도 블럭 분리, 최종 대답 마크다운 렌더링(2026 최신 최적화 규격), 좌측 대화 이력 목록 사이드바(+ New Chat, 세션 선택, 삭제, 영구 저장)"

---

## Clarifications

### Session 2026-07-30

- Q: 생각 표시 모드(보이기/접기/끄기) 변경 시 기존 대화 스레드 메시지의 동적 전환 방식 → A: Option A (패널의 토글 버튼 클릭 시 대화 스레드 내 기존 모든 메시지의 생각 블록 상태가 실시간으로 일괄 동적 전환)
- Q: AI Playground 좌측 대화 이력(Chat Sessions History) 사이드바 및 영구 저장/복원 제어 → A: Option A (Google AI Studio 스타일 좌측 접이식 사이드바 추가 - + New Chat, 세션 이동, 세션 삭제, SQLite DB 영구 저장 및 새로고침 후 복원)

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - AI Playground 3단 생각 태그 UI 모드 (보이기/접기/끄기) (Priority: P1) 🎯 MVP

AI Playground 사용자 인터페이스 컨트롤 패널에 생각 태그 표시 모드 선택 토글 버튼 그룹("👁️ 보이기", "📁 접기", "🚫 끄기")을 제공합니다.

- **👁️ 보이기 (Show)**: `<think>...</think>` 사고과정 텍스트를 메시지 상단에 항상 펼쳐진 상태의 전용 시각적 블록으로 표시합니다.
- **📁 접기 (Collapse - 기본값)**: 스트리밍 출력 도중에는 사고과정을 실시간으로 노출하고, `</think>` 닫는 태그 수신 완료 시 자동으로 아코디언 블록으로 접으며, 사용자가 클릭하여 언제든 펼치거나 접을 수 있습니다.
- **🚫 끄기 (Off)**: 사고과정 블록을 UI에서 완전히 숨기고 정제된 대답만 표출합니다.

**Why this priority**: 스트리밍 답변 시 실시간 사유 현황을 눈으로 확인하면서, 작성이 끝난 후 대답 본문의 가독성을 깨끗하게 유지하기 위해 필수적입니다.

**Independent Test**:
1. "📁 접기" 모드 선택 후 스트리밍 답변 실행 시, 생성 중에는 사유 과정이 노출되다가 `</think>` 수신 시 아코디언으로 자동 접히는지 확인.
2. 아코디언 헤더("🧠 Thinking Process (0.8s)") 클릭 시 접힘/펼침이 정상 동작하는지 확인.
3. "🚫 끄기" 모드 선택 시 생각 블록이 전혀 출력되지 않는지 확인.

---

### User Story 2 - LLM 응답 본문 2026 최신 웹 마크다운 렌더링 (Priority: P1)

AI Playground 대화 스레드의 최종 대답 텍스트를 단순 평문(Plaintext)이 아닌 표준 마크다운(Markdown) 및 코드 구문 강조(Syntax Highlighting)로 실시간/완료 렌더링합니다.

- **기술 규격**: `marked.js` + `DOMPurify` (XSS 보안 검증) + `highlight.js` (코드 블록 하이라이팅).
- **렌더링 요소**: 제목(`h1`~`h3`), 볼드/이탈릭, 순서 있는/없는 목록, 코드 블록(복사 버튼 포함), 테이블, 인용구.

**Why this priority**: LLM 출력에는 표, 코드 블록, 목록 등의 구조화된 마크다운 텍스트가 다수 포함되므로 가독성 향상에 결정적입니다.

**Independent Test**:
1. 코드 블록(```python ... ```) 및 마크다운 표가 포함된 답변 수신 시 깔끔한 포맷팅 및 구문 강조로 표시되는지 확인.

---

### User Story 3 - Google AI Studio 스타일 좌측 대화 이력 사이드바 (Priority: P1)

AI Playground 좌측에 접이식 대화 이력 사이드바를 구축하여 `+ New Chat` 버튼, 과거 대화 세션 목록, 세션별 클릭 복원 및 삭제 기능을 제공합니다.

- **`+ New Chat`**: 기존 스레드를 비우고 신규 대화 세션을 생성합니다.
- **세션 목록 및 복원**: 사용자의 첫 프롬프트 문구로 생성된 세션 제목 목록을 표출하고 클릭 시 과거 대화 내용과 `thinking_process`를 즉시 복원합니다.
- **세션 삭제**: 세션 아이템 오른쪽 삭제(🗑️) 버튼 클릭 시 해당 대화 세션을 DB에서 안전하게 삭제합니다.
- **사이드바 접기/펼치기**: 좌측 상단 햄버거/토글 버튼으로 사이드바를 접어 작업 영역을 넓힐 수 있습니다.

**Why this priority**: 브라우저 새로고침이나 재접속 시에도 과거 연구 대화 이력이 사라지지 않고 복원되어 연속적인 작업이 가능해야 합니다.

**Independent Test**:
1. 프롬프트 전송 후 새로고침 시 좌측 사이드바 대화 목록에 세션이 보존되어 있으며 클릭 시 전체 대화 및 생각 블록이 복원되는지 확인.
2. `+ New Chat` 클릭 시 새 대화 화면이 열리고, 🗑️ 클릭 시 해당 세션이 삭제되는지 확인.

---

## Functional Requirements *(mandatory)*

- **FR-001**: `src/api/static/index.html` 및 `app.js`에 생각 태그 표시 모드 선택 토글 버튼 그룹(`Show` / `Collapse` / `Off`)을 추가해야 한다.
- **FR-002**: 스트리밍 수신 중에는 `<think>` 내용이 들어오는 대로 실시간 생각 전용 블록(`div.think-block`)에 출력해야 한다.
- **FR-003**: `Collapse` 모드에서 `</think>` 닫는 태그 수신 완료 시 생각 전용 블록을 `<details><summary>` 아코디언 스타일로 자동 접기 처리해야 한다.
- **FR-004**: `marked.js` 및 `DOMPurify` 라이브러리를 동적으로 안전하게 적용하여 최종 답변 텍스트를 마크다운 HTML로 안전하게 렌더링해야 한다.
- **FR-005**: 헌법 v1.5.2에 따라 3단 UI 모드 및 마크다운 렌더링 실측 검증 테스트 수트(`tests/unit/test_think_tag_ui_markdown.py`)를 수록해야 한다.
- **FR-006**: 컨트롤 패널에서 생각 표시 모드(보이기/접기/끄기)를 변경하는 즉시 대화 스레드 내 이미 생성된 모든 메시지의 생각 블록에 신규 모드 스타일 및 접힘/펼침 상태가 즉시 일괄 적용되어야 한다.
- **FR-007**: `data/metrics.db` 스키마에 `playground_sessions` 및 `playground_messages` 테이블을 추가하여 세션별 대화 메시지 및 `thinking_process`를 영구 저장해야 한다.
- **FR-008**: AI Playground UI 좌측에 Google AI Studio 스타일 접이식 대화 이력 사이드바(`+ New Chat`, 세션 목록, 세션 복원, 세션 삭제)를 구현하고 새로고침 시에도 내역이 유지되어야 한다.

---

## Success Criteria *(mandatory)*

- **SC-001**: 생각 태그 3단 모드 토글 전환 및 아코디언 자동 접힘/펼침 동작 성공률 **100%**.
- **SC-002**: 마크다운 렌더링 및 XSS 보안 필터링 적용 성공률 **100%**.
- **SC-003**: 새로고침 후 대화 세션 복원 및 삭제 동작 성공률 **100%**.
- **SC-004**: 스트리밍 마크다운 렌더링 오버헤드 지연시간 **<2ms**.

# Implementation Plan: AI Playground 생각 태그 UI 제어(보이기/접기/끄기), 마크다운 렌더링 및 대화 이력 사이드바 (048-think-tag-ui-markdown)

**Branch**: `048-think-tag-ui-markdown` | **Date**: 2026-07-30 | **Spec**: [spec.md](file:///home/dev/storage/vllm_serv/specs/048-think-tag-ui-markdown/spec.md)

**Input**: Feature specification from `/specs/048-think-tag-ui-markdown/spec.md`

## Summary

AI Playground UI에 생각 태그 3단 모드 토글(`Show` / `Collapse` / `Off`), `marked.js` + `DOMPurify` + `highlight.js` 기반 2026 최신 웹 마크다운/코드 하이라이팅 렌더링, 및 Google AI Studio 스타일의 접이식 좌측 대화 이력 사이드바(`+ New Chat`, 세션 선택 복원, 세션 삭제)를 구현하고 SQLite DB(`playground_sessions`, `playground_messages`)에 영구 보존합니다.

## Technical Context

**Language/Version**: Python 3.12 (FastAPI), Vanilla JavaScript ES6+, HTML5/CSS3

**Primary Dependencies**: marked.js (v12+ CDN), DOMPurify (v3+ CDN), highlight.js (v11+ CDN), sqlite3

**Storage**: SQLite (`data/metrics.db`)

**Testing**: pytest (`uv run pytest`)

**Target Platform**: Linux server (vllm_serv web dashboard)

**Project Type**: web-service (FastAPI + Static UI)

**Performance Goals**: 마크다운 렌더링 및 생각 상태 전환 지연시간 <2ms

**Constraints**: Zero Mock Policy in Implementation Code (Constitution v1.5.2)

**Scale/Scope**: AI Playground Dashboard (`index.html`, `app.js`, `style.css`, `dashboard_api.py`, `metrics_db.py`)

## Constitution Check

- [x] 계획서가 한국어로 작성되었는가? (언어 정책)
- [x] 테스트 코드 작성 계획이 포함되어 있는가? (테스트 필수 원칙)
- [x] 목업은 유료/제한 API로 엄격히 제한하고 실물 시스템/소켓/OS 인자 및 실제 호출 플래그(REAL_API_CALL=1) 기반 실측 검증 계획이 포함되어 있는가? (실체적 테스트 및 수렴 검증 원칙)
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (종료 조건 명확화 원칙)
- [x] 비파괴적 문서 수정 원칙을 준수하는가? (비파괴적 문서 수정 원칙)
- [x] uv 패키지 매니저 및 가상환경 격리 표준(uv run)을 준수하는가? (uv 패키지 및 환경 관리 원칙)

## Project Structure

### Documentation (this feature)

```text
specs/048-think-tag-ui-markdown/
├── plan.md              # Implementation Plan
├── research.md          # Technical research & choices
├── data-model.md        # Data models & DB schemas
├── quickstart.md        # Validation & verification guide
├── contracts/           # API contracts
│   └── playground_session_api_contract.md
└── checklists/
    └── requirements.md
```

### Source Code Touchpoints

```text
src/
├── core/
│   └── metrics_db.py         # SQLite tables for playground_sessions & playground_messages
├── api/
│   ├── static/
│   │   ├── index.html        # Add CDN scripts, left sidebar HTML, toggle button group
│   │   ├── style.css         # Sidebar, accordion, think block & markdown CSS styles
│   │   └── app.js            # 3-way toggle state, marked.js render, session fetch/restore/delete
│   └── routes/
│       └── dashboard_api.py  # Session REST API endpoints (GET/POST/DELETE)

tests/unit/
└── test_think_tag_ui_markdown.py # Anti-mock unit test suite
```

**Structure Decision**: Single project layout under `src/` and `tests/unit/`.

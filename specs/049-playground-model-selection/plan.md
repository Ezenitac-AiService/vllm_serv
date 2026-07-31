# Implementation Plan: AI Playground 동적 모델 선택 및 서버 온로드 모델 자동 동기화 (049-playground-model-selection)

**Branch**: `049-playground-model-selection` | **Date**: 2026-07-30 | **Spec**: [spec.md](file:///home/dev/storage/vllm_serv/specs/049-playground-model-selection/spec.md)

**Input**: Feature specification from `/specs/049-playground-model-selection/spec.md`

## Summary

AI Playground UI에 모델 선택 드롭다운(`<select id="pg-model-select">`)을 추가하고, 대시보드 로딩 시 `GET /dashboard/api/capabilities`를 조회하여 현재 서버에서 실제 온로드/서비스 중인 모델(`current_model`)을 드롭다운의 기본 선택값으로 자동 지정합니다. 또한 SSE 파싱 로직의 `JSON.parse` 교정을 통해 TTFT(ms), Latency(s), Token Count 등의 메트릭 지표가 대시보드 및 카드에 정상 표시되도록 구현합니다.

## Technical Context

**Language/Version**: Python 3.12 (FastAPI), Vanilla JavaScript ES6+, HTML5/CSS3

**Primary Dependencies**: FastAPI, sqlite3

**Testing**: pytest (`uv run pytest`)

**Target Platform**: Linux server (vllm_serv web dashboard)

**Project Type**: web-service (FastAPI + Static UI)

**Performance Goals**: 대시보드 로딩 및 동기화 지연시간 오버헤드 미미

**Constraints**: Zero Mock Policy in Implementation Code (Constitution v1.5.2)

**Scale/Scope**: AI Playground Dashboard (`index.html`, `app.js`, `dashboard_api.py`)

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
specs/049-playground-model-selection/
├── plan.md              # Implementation Plan
├── research.md          # Technical research & choices
├── data-model.md        # Data models & DB schemas
├── quickstart.md        # Validation & verification guide
├── contracts/           # API contracts
│   └── playground_model_selection_contract.md
└── checklists/
    └── requirements.md
```

### Source Code Touchpoints

```text
src/
├── api/
│   ├── static/
│   │   ├── index.html        # Add Model Select dropdown HTML
│   │   └── app.js            # Auto-populate pg-model-select, fix SSE JSON.parse, pass selected model
│   └── routes/
│       └── dashboard_api.py  # Handle model parameter in PlaygroundRequest

tests/unit/
└── test_playground_model_selection.py # Anti-mock unit test suite
```

**Structure Decision**: Single project layout under `src/` and `tests/unit/`.

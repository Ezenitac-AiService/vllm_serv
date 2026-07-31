# Implementation Plan: 대시보드 UI 회귀 버그 원인 분석, 근본 수리 및 Playwright E2E 테스트 수트 구축 (052-fix-dashboard-ui-regressions-and-playwright-e2e)

**Branch**: `052-fix-dashboard-ui-regressions-and-playwright-e2e` | **Date**: 2026-07-30 | **Spec**: [spec.md](file:///home/dev/storage/vllm_serv/specs/052-fix-dashboard-ui-regressions-and-playwright-e2e/spec.md)

**Input**: Feature specification from `/specs/052-fix-dashboard-ui-regressions-and-playwright-e2e/spec.md`

## Summary

`src/api/static/app.js`의 `modalCloseBtn` 프로퍼티 복원 및 전체 DOM 리스너에 Optional Chaining(`?.`) 방어 프로그래밍을 전면 적용하여 단일 요소 누락으로 전체 스크립트가 죽는 결함을 근본 수리하고, 폼 제출 시 `e.preventDefault()`를 보장하여 탭 리셋 현상을 차단합니다. 또한, 헌법 v1.6.0 원칙 VII에 따라 `pytest-playwright` 기반의 E2E 웹 브라우저 자동 검증 수트(`tests/e2e/test_dashboard_ui.py`)를 구축합니다.

## Technical Context

**Language/Version**: Python 3.12, Vanilla JavaScript ES6+, HTML5

**Primary Dependencies**: FastAPI, Playwright (`pytest-playwright`), ConfigManager

**Testing**: pytest (`uv run pytest tests/e2e/test_dashboard_ui.py`)

**Target Platform**: Linux server (vllm_serv web dashboard)

**Project Type**: web-service (FastAPI + Static UI + E2E Playwright)

**Performance Goals**: E2E 브라우저 검증 100% 그린 패스 및 JS 스크립트 예외 발생률 0%

**Constraints**: Zero Mock Policy in Implementation Code & Mandatory Regression Testing (Constitution v1.6.0)

**Scale/Scope**: `src/api/static/app.js`, `tests/e2e/test_dashboard_ui.py`

## Constitution Check

- [x] 계획서가 한국어로 작성되었는가? (언어 정책)
- [x] 테스트 코드 작성 계획이 포함되어 있는가? (테스트 필수 원칙)
- [x] 목업은 유료/제한 API로 엄격히 제한하고 실물 시스템/소켓/OS 인자 및 실제 호출 플래그(REAL_API_CALL=1) 기반 실측 검증 계획이 포함되어 있는가? (실체적 테스트 및 수렴 검증 원칙)
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (종료 조건 명확화 원칙)
- [x] 비파괴적 문서 수정 원칙을 준수하는가? (비파괴적 문서 수정 원칙)
- [x] uv 패키지 매니저 및 가상환경 격리 표준(uv run)을 준수하는가? (uv 패키지 및 환경 관리 원칙)
- [x] 전체 회귀 테스트 수트 및 Playwright 기반 E2E 브라우저 실측 검증 계획이 포함되어 있는가? (의무적 회귀 테스트 및 브라우저 E2E 검증 원칙)

## Project Structure

### Documentation (this feature)

```text
specs/052-fix-dashboard-ui-regressions-and-playwright-e2e/
├── plan.md              # Implementation Plan
├── research.md          # Technical research & choices
├── data-model.md        # Data models & UI Element Contracts
├── quickstart.md        # Validation & verification guide
├── contracts/           # API & E2E contracts
│   └── ui_regression_e2e_contract.md
└── checklists/
    └── requirements.md
```

### Source Code Touchpoints

```text
src/
└── api/
    └── static/
        └── app.js           # Restore modalCloseBtn & apply optional chaining to all event listeners

tests/e2e/
└── test_dashboard_ui.py     # Playwright E2E test suite for tab switching, modals, form submits
```

**Structure Decision**: Standard project structure under `src/` and `tests/e2e/`.

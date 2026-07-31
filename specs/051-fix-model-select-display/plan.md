# Implementation Plan: 대시보드 및 플레이그라운드 동적 서비스 모델 선택 드롭다운 목록 미표시 근본 원인 버그 수정 (051-fix-model-select-display)

**Branch**: `051-fix-model-select-display` | **Date**: 2026-07-30 | **Spec**: [spec.md](file:///home/dev/storage/vllm_serv/specs/051-fix-model-select-display/spec.md)

**Input**: Feature specification from `/specs/051-fix-model-select-display/spec.md`

## Summary

`src/core/config_manager.py`의 `_model_catalog_cache` 캐시 고착 결함을 근본적으로 수리하여 `config/model_catalog.json` 카탈로그에 등록된 동적 지원 모델 목록을 백엔드가 항상 정확하게 반환하고, 대시보드 및 AI Playground 드롭다운에서 가변적인 모델 개수에 맞추어 바인딩되도록 수리합니다.

## Technical Context

**Language/Version**: Python 3.12, Vanilla JavaScript ES6+, HTML5

**Primary Dependencies**: FastAPI, ConfigManager

**Testing**: pytest (`uv run pytest`)

**Target Platform**: Linux server (vllm_serv web dashboard)

**Project Type**: web-service (FastAPI + Static UI)

**Performance Goals**: `ConfigManager` 동적 카탈로그 조회의 0ms 즉시 응답성 및 무결성 보장

**Constraints**: Zero Mock Policy in Implementation Code (Constitution v1.5.2). 특정 모델 개수 하드코딩 금지.

**Scale/Scope**: `src/core/config_manager.py`, `src/api/routes/dashboard_api.py`, `src/api/static/app.js`

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
specs/051-fix-model-select-display/
├── plan.md              # Implementation Plan
├── research.md          # Technical research & choices
├── data-model.md        # Data models & DB schemas
├── quickstart.md        # Validation & verification guide
├── contracts/           # API contracts
│   └── model_select_display_fix_contract.md
└── checklists/
    └── requirements.md
```

### Source Code Touchpoints

```text
src/
├── core/
│   └── config_manager.py    # Fix _model_catalog_cache empty dict sticking bug & add robust loader
├── api/
│   ├── static/
│   │   └── app.js           # Ensure model options binding in #model-select and #pg-model-select
│   └── routes/
│       └── dashboard_api.py # Ensure capabilities response carries dynamic catalog model keys

tests/unit/
└── test_model_select_display_fix.py # Unit test suite verifying ConfigManager and capabilities
```

**Structure Decision**: Standard project structure under `src/` and `tests/unit/`.

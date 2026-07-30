# Implementation Plan: API Key 필수 모드 시 Playground 인증 처리 및 API Key 입력 지원 (050-playground-api-key-auth)

**Branch**: `050-playground-api-key-auth` | **Date**: 2026-07-30 | **Spec**: [spec.md](file:///home/dev/storage/vllm_serv/specs/050-playground-api-key-auth/spec.md)

**Input**: Feature specification from `/specs/050-playground-api-key-auth/spec.md`

## Summary

대시보드에서 API Key 필수 보안 모드가 ON으로 활성화되었을 때 Playground 엔드포인트(`/dashboard/api/playground/stream`)에서도 유효한 API Key를 필수적으로 검증하여 무인증 우회를 차단하고, UI 설정 패널에 API Key 입력 필드(`#pg-api-key`)를 제공하여 인증된 호출을 수행할 수 있도록 구현합니다.

## Technical Context

**Language/Version**: Python 3.12 (FastAPI), Vanilla JavaScript ES6+, HTML5/CSS3

**Primary Dependencies**: FastAPI, sqlite3

**Testing**: pytest (`uv run pytest`)

**Target Platform**: Linux server (vllm_serv web dashboard)

**Project Type**: web-service (FastAPI + Static UI)

**Performance Goals**: API Key 검증 오버헤드 미미

**Constraints**: Zero Mock Policy in Implementation Code (Constitution v1.5.2)

**Scale/Scope**: AI Playground Dashboard (`index.html`, `app.js`, `dashboard_api.py`, `ApiKeyManager`)

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
specs/050-playground-api-key-auth/
├── plan.md              # Implementation Plan
├── research.md          # Technical research & choices
├── data-model.md        # Data models & DB schemas
├── quickstart.md        # Validation & verification guide
├── contracts/           # API contracts
│   └── playground_api_key_auth_contract.md
└── checklists/
    └── requirements.md
```

### Source Code Touchpoints

```text
src/
├── api/
│   ├── static/
│   │   ├── index.html        # Add API Key input element in Playground settings
│   │   └── app.js            # Handle api_key_enabled state, pass api_key header/payload, show 401 alert
│   └── routes/
│       └── dashboard_api.py  # Return api_key_enabled in capabilities, validate API key in playground endpoints

tests/unit/
└── test_playground_api_key_auth.py # Anti-mock unit test suite
```

**Structure Decision**: Single project layout under `src/` and `tests/unit/`.

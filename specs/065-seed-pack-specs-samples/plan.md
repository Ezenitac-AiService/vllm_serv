# Implementation Plan: 시드팩(Seed Pack) 패키징 시 명세서(specs/) 및 샘플 파일(samples/) 수록 포함 개선

**Branch**: `065-seed-pack-specs-samples` | **Date**: 2026-07-31 | **Spec**: [spec.md](file:///home/dev/storage/vllm_serv/specs/065-seed-pack-specs-samples/spec.md)

**Input**: Feature specification from `specs/065-seed-pack-specs-samples/spec.md`

## Summary

본 계획서는 `vllm_serv` 이관 패키징 스크립트(`scripts/make_seed_pack.sh`)의 아카이브 제외 규칙을 수정하여 기능 명세서(`specs/`), API 연동 예제 스크립트(`samples/`), 및 레거시 스키마 모듈(`.legacy/`)을 시드팩 아카이브(`dist/vllm_serv_seed.tar.gz` / `.zip`)에 포함시키고, Post-Build 검증 로직 및 `tests/unit/test_seed_pack.py` 회귀 테스트 수트를 강화하는 작업을 다룹니다.

## Technical Context

**Language/Version**: Bash, Python 3.11+, tar, gzip, zip

**Primary Dependencies**: tar, gzip, zip, pytest

**Storage**: Local tar.gz / zip archives in `dist/`

**Testing**: Pytest (`uv run pytest tests/unit/test_seed_pack.py`) & Shell execution (`./make_seed_pack.sh`)

**Target Platform**: Linux Server (Target Migration Package)

**Project Type**: Migration Packaging & Deployment Automation Scripts

**Performance Goals**: 시드팩 생성시간 < 5초, 아카이브 전체 용량 < 15MB

**Constraints**: 대용량 모델 가중치(`models/`), 가상환경(`.venv/`), 빌드 아티팩트(`build/`, `.bin/`)는 엄격히 제외 유지

**Scale/Scope**: `scripts/make_seed_pack.sh` + `tests/unit/test_seed_pack.py`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

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
specs/065-seed-pack-specs-samples/
├── spec.md              # Feature specification
├── plan.md              # Implementation plan (/speckit-plan command output)
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── seed-pack-contract.json
└── checklists/
    └── requirements.md  # Specification quality checklist
```

### Source Code (repository root)

```text
scripts/
└── make_seed_pack.sh    # Packaging script with updated inclusion rules for specs/ and samples/

make_seed_pack.sh        # Root symlink to scripts/make_seed_pack.sh

tests/
└── unit/
    └── test_seed_pack.py# Seed pack unit test verifying specs/ and samples/ archive inclusion
```

**Structure Decision**: Single project layout updating `scripts/make_seed_pack.sh` and `tests/unit/test_seed_pack.py`.

## Complexity Tracking

*No violations.*

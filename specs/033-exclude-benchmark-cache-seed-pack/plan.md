# Implementation Plan: 시드 팩 호스트 독립성 및 경량화 - 기기 특정 벤치마크 캐시 및 레거시 파일 배제 (033-exclude-benchmark-cache-seed-pack)

**Branch**: `033-exclude-benchmark-cache-seed-pack` | **Date**: 2026-07-30 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/033-exclude-benchmark-cache-seed-pack/spec.md`

## Summary

`scripts/make_seed_pack.sh` 실행 시 호스트 특정 GPU VRAM 벤치마크 실측 캐시 파일(`config/model_context_profiles.json`), 레거시 아카이브 디렉터리(`.legacy/`), 벤치마크 결과 파일(`benchmark_results.json` 및 `*.jsonl`)을 tar/zip 배제 패턴(`--exclude`)에 명시 추가합니다.

이를 통해 타겟 서비스 서버에서 시드 팩 복원 및 `./setup.sh` 실행 시 이전 장비 캐시 간섭 없이 타겟 장비 하드웨어 특성에 맞는 벤치마크를 온디맨드로 정상 구동하도록 보장하고, unit 테스트를 통해 배제 검증을 자동화합니다.

## Technical Context

**Language/Version**: Bash 4.4+, Python 3.12+

**Primary Dependencies**: `tar`, `zip`, `pytest`

**Storage**: Archiving targets (`scripts/make_seed_pack.sh`, `dist/vllm_serv_seed.tar.gz`)

**Testing**: `pytest`, `tests/unit/test_seed_pack.py`

**Target Platform**: Linux (Ubuntu Server 24.04 LTS), Target Service Server & Development Workstations

**Project Type**: Archive Packaging & Setup Pipeline

**Performance Goals**: 시드 팩 아카이브 용량 최소화, 타겟 장비 `./setup.sh` 시 신규 벤치마크 100% 정상 가동

**Constraints**: `config/model_catalog.json`, `config/server_config.json`, `config/platform_profiles.json` 등 공용 필수 규격 설정 파일은 정상 수록 보장

**Scale/Scope**: `scripts/make_seed_pack.sh`, `tests/unit/test_seed_pack.py`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] 계획서가 한국어로 작성되었는가? (언어 정책)
- [x] 테스트 코드 작성 계획이 포함되어 있는가? (테스트 필수 원칙 - 벤치마크 캐시 배제 검증 단위 테스트)
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (종료 조건 명확화 원칙 - DoD-001 ~ DoD-003 준수)
- [x] 비파괴적 문서 수정 원칙을 준수하는가? (비파괴적 문서 수정 원칙)
- [x] uv 패키지 매니저 및 가상환경 격리 표준(uv run)을 준수하는가? (uv 패키지 및 환경 관리 원칙)

## Project Structure

### Documentation (this feature)

```text
specs/033-exclude-benchmark-cache-seed-pack/
├── spec.md              # Feature specification
├── plan.md              # Implementation Plan (/speckit-plan output)
├── research.md          # Phase 0 output (/speckit-plan output)
├── data-model.md        # Phase 1 output (/speckit-plan output)
├── quickstart.md        # Phase 1 output (/speckit-plan output)
├── contracts/           # Phase 1 Contract output
│   └── seed-pack-exclusion-contract.md
└── tasks.md             # Phase 2 output (/speckit-tasks output - pending)
```

### Source Code (repository root)

```text
scripts/
└── make_seed_pack.sh   # FR-001: config/model_context_profiles.json, .legacy, benchmark_results.json, *.jsonl 배제 패턴 추가

tests/
└── unit/
    └── test_seed_pack.py # FR-003: 시드 팩 배제 항목 (model_context_profiles.json, .legacy) 자동 검증 추가
```

**Structure Decision**: Single project layout updating existing packaging script and unit test suite.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

*violations: None. Packaging script exclusion enhancement.*

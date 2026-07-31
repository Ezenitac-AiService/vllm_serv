# Implementation Plan: Seed Pack Archiver & Migration Pipeline

**Branch**: `019-seed-pack-generator` | **Date**: 2026-07-30 | **Spec**: [spec.md](file:///home/dev/storage/vllm_serv/specs/019-seed-pack-generator/spec.md)

**Input**: Feature specification from `/specs/019-seed-pack-generator/spec.md`

## Summary

본 구현 계획은 `vllm_serv` LLM 모델 서빙 파이프라인을 타 GPU 서버로 신속하고 용이하게 이관(Migration)할 수 있도록, 대용량 가중치(`models/`), 가상환경(`.venv/`), C++ 바이너리(`.bin/`)를 제외한 핵심 소스 코드, 서버 설정, 쉘 스크립트만을 선택적으로 압축 패키징하는 `scripts/make_seed_pack.sh` 파이프라인 스크립트를 구축합니다. 기본 POSIX `.tar.gz` 및 선택적 `.zip` 포맷 지원, 커스텀 출력 경로 지정(`-o/--output`), 그리고 타겟 시스템 복원 파이프라인(`./setup.sh` -> `./start_server.sh`) 검증 테스트 수트를 수립합니다.

## Technical Context

**Language/Version**: Bash (POSIX compliance), Python 3.12

**Primary Dependencies**: POSIX tar, gzip, zip (optional), uv package manager

**Storage**: File system archive (`dist/vllm_serv_seed.tar.gz`)

**Testing**: Pytest (`uv run pytest tests/unit/test_seed_pack.py -v`)

**Target Platform**: Linux (Ubuntu 22.04 LTS), NVIDIA GPU Server

**Project Type**: Infrastructure & CLI Scripting / System Migration Tooling

**Performance Goals**: Archive file size < 10MB, Seed pack generation time < 2 seconds

**Constraints**: Strict exclusion of large models and virtual environments; block CPU-only fallback on target system

**Scale/Scope**: 1 CLI shell script (`scripts/make_seed_pack.sh`), 1 root symlink (`./make_seed_pack.sh`), unit/integration test suite

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] 계획서가 한국어로 작성되었는가? (언어 정책)
- [x] 테스트 코드 작성 계획이 포함되어 있는가? (테스트 필수 원칙)
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (종료 조건 명확화 원칙)
- [x] 파괴적 문서 수정을 금지하고 명시적 항목만 업데이트하는가? (비파괴적 문서 수정 원칙)
- [x] uv 환경 및 패키지 관리 규칙(`uv run`, `uv sync`)을 준수하는가? (uv 패키지 및 환경 관리 원칙)

## Project Structure

### Documentation (this feature)

```text
specs/019-seed-pack-generator/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── contracts/           # Phase 1 output
    └── seed_pack_cli_contract.md
```

### Source Code (repository root)

```text
scripts/
├── make_seed_pack.sh    # Seed pack generator CLI script
├── setup.sh             # Target environment bootstrap & CUDA build
├── start_server.sh      # Daemon startup & auto model downloader
├── status_server.sh     # Server & GPU monitoring
└── stop_server.sh      # Safe shutdown

tests/
├── unit/
│   └── test_seed_pack.py# Seed pack archive generation & exclusion unit test
└── integration/
    └── test_migration_pipeline.py # Sandbox extraction & setup verification test
```

**Structure Decision**: Single project layout matching repository shell script and test suite architecture.

## Complexity Tracking

> **Constitution Check: No violations. Standard architecture.**

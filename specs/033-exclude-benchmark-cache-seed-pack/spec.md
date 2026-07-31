# Feature Specification: 시드 팩 호스트 독립성 및 경량화 - 기기 특정 벤치마크 캐시 및 레거시 파일 배제 (033-exclude-benchmark-cache-seed-pack)

**Feature Branch**: `033-exclude-benchmark-cache-seed-pack`

**Created**: 2026-07-30

**Status**: Draft

**Input**: User feedback: 시드 팩 생성 시 기기 특정 벤치마크 캐시(`config/model_context_profiles.json`), 레거시 폴더(`.legacy/`), 벤치마크 로그(`*.jsonl`, `benchmark_results.json`)가 포함되어 타겟 장비 하드웨어 측정을 건너뛰거나 불필요한 아티팩트가 포함되는 문제 전수 검증 및 배제 정제.

## Clarifications

### Session 2026-07-30

- Q: 시드 팩 생성 시 배제(`--exclude`)할 호스트 특정/레거시 파일 항목 정의 → A: Option A (`config/model_context_profiles.json` (기기 벤치마크 캐시), `.legacy/` (구형 아카이브 폴더), `benchmark_results.json` 및 모든 `*.jsonl` 벤치마크 로그를 시드 팩 배제 목록(`--exclude`)에 명시 추가하고, 필수 소스(`src/`), 기본 설정(`config/model_catalog.json`, `server_config.json`, `platform_profiles.json`), 스크립트(`scripts/`), 사전 휠(`wheels/legacy_i7_930/`), 명세(`specs/`), 테스트(`tests/`)만 수록)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 타겟 서버 이관 시 개발 머신 벤치마크 파일 및 레거시 아티팩트 배제 보장 (Priority: P1) 🎯 MVP

엔지니어가 개발 머신에서 `make_seed_pack.sh`를 실행하여 생성한 시드 팩을 타겟 서비스 플랫폼 장비(i7 930 + GTX 1070 등)에 설치할 때, 개발 머신의 특정 GPU 벤치마크 결과 파일(`config/model_context_profiles.json`, `benchmark_results.json`, `*.jsonl`) 및 구형 아카이브 폴더(`.legacy/`)가 완전히 제외되어, 타겟 서버의 `./setup.sh`가 신규 서비스 장비 하드웨어 특성에 맞는 컨텍스트 윈도우 스케일링 벤치마크를 건너뛰지 않고 정상 수행합니다.

**Why this priority**: 개발 서버(GTX 1080 Ti 11GB)의 VRAM 및 컨텍스트 측정 캐시나 불필요한 레거시 파일이 서비스 서버(GTX 1070 8GB)로 잔재되면 OOM 예측 오차가 발생하고 시드 팩 용량이 낭비되므로 호스트 독립성이 필수적입니다.

**Independent Test**: `make_seed_pack.sh` 실행으로 생성된 `dist/vllm_serv_seed.tar.gz` 아카이브 내부에 `config/model_context_profiles.json`, `.legacy/`, `benchmark_results.json`, `*.jsonl` 항목이 전혀 존재하지 않음을 검증합니다.

**Acceptance Scenarios**:

1. **Given** 개발 머신에 `config/model_context_profiles.json`, `.legacy/`, `benchmark_results.json` 파일이 존재하는 상태에서, **When** `./scripts/make_seed_pack.sh`를 실행하여 시드 팩을 생성하면, **Then** 생성된 아카이브에 해당 기기 특정 캐시 및 레거시 항목들이 완전히 배제되어야 한다.
2. **Given** 벤치마크 캐시가 제거된 시드 팩을 타겟 서비스 플랫폼에 해제한 후, **When** `./setup.sh`를 실행하면, **Then** 이전 기기의 벤치마크 스킵 없이 타겟 장비용 `config/model_context_profiles.json`이 신규 생성되어야 한다.

---

### User Story 2 - 시드 팩 생성 스크립트 아카이브 검증 테스트 강화 (Priority: P2)

개발자가 단위 테스트(`tests/unit/test_seed_pack.py`)를 실행할 때, 시드 팩 아카이브 검증 로직이 필수 소스코드/휠 항목의 포함 여부뿐만 아니라 벤치마크 캐시 및 레거시 파일(`.legacy/`, `model_context_profiles.json`)의 제외 여부까지 자동으로 통과하는지 확인합니다.

**Why this priority**: 추후 벤치마크 캐시 및 레거시 파일이 시드 팩에 재유입되는 회귀 버그를 방지하기 위함입니다.

**Independent Test**: `uv run pytest tests/unit/test_seed_pack.py` 실행 시 배제 검증 테스트가 100% 통과합니다.

**Acceptance Scenarios**:

1. **Given** `tests/unit/test_seed_pack.py` 테스트 실행 시, **When** 생성된 tarball 내 아카이브 파일 목록을 검사하면, **Then** `config/model_context_profiles.json` 및 `.legacy/` 항목이 미포함 상태임을 검증해야 한다.

---

### Edge Cases

- `config/` 디렉터리의 필수 설정 파일(`config/model_catalog.json`, `config/server_config.json`, `config/platform_profiles.json`)은 배제되지 않고 정상 아카이브에 수록되는가?
- `specs/` 하위 디렉터리의 개별 벤치마크 로그 파일(`specs/*/results.jsonl`)이 시드 팩에서 정확히 스킵되는가?

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `scripts/make_seed_pack.sh` 내 tar/zip 배제 패턴(`--exclude`)에 `config/model_context_profiles.json`, `.legacy`, `benchmark_results.json`, `*.jsonl` 추가 완료
- **DoD-002**: `tests/unit/test_seed_pack.py`에 벤치마크 캐시 및 레거시 제외 검증 테스트 케이스 수록 완료
- **DoD-003**: 시드 팩 재생성 테스트 및 전체 pytest 수트 100% 통과

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 (기기 특정 벤치마크 캐시 및 레거시 파일 배제)**: `scripts/make_seed_pack.sh` 실행 시 호스트 특정 GPU VRAM 측정 파일인 `config/model_context_profiles.json`, `.legacy/` 디렉터리, `benchmark_results.json`, `*.jsonl` 항목을 tar 및 zip 배제 패턴(`--exclude`)에 명시적으로 추가하여 시드 팩 번들링에서 제외해야 한다.
- **FR-002 (타겟 장비 벤치마크 온디맨드 수행 보장)**: 시드 팩 해제 후 타겟 장비에서 `./setup.sh` 실행 시 이관 전 머신의 캐시 파일 간섭 없이 타겟 플랫폼 하드웨어에 대한 컨텍스트 스케일링 벤치마크가 정상 실행되도록 보장해야 한다.
- **FR-003 (시드 팩 캐시 배제 회귀 테스트 수록)**: `tests/unit/test_seed_pack.py`에 시드 팩 내 `config/model_context_profiles.json` 및 `.legacy/` 미존재 여부를 확인하는 자동화 검증 단위를 수록해야 한다.

### Key Entities

- **SeedPackExclusionRule**: `make_seed_pack.sh` 내 아카이브 생성 시 배제되는 머신 특정 및 레거시 아티팩트 목록 (`models/`, `.venv/`, `.legacy/`, `config/model_context_profiles.json`, `benchmark_results.json`, `*.jsonl`).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 생성된 `dist/vllm_serv_seed.tar.gz` 내 `config/model_context_profiles.json` 및 `.legacy/` 존재 건수 0건
- **SC-002**: 전체 pytest 수트 100% 통과

## Assumptions

- `config/model_context_profiles.json`은 호스트 GPU의 VRAM 및 성능 벤치마크 실측 캐시 파일임.
- `.legacy/`는 구형 히스토리 아카이브 디렉터리로 운영 서빙 시드 팩에는 불필요함.
- `config/server_config.json` 및 `config/platform_profiles.json`은 공용 규격 설정 파일이므로 시드 팩에 유지되어야 함.

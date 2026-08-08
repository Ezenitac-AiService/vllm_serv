# Feature Specification: 시드 팩 마이그레이션 파이프라인 및 ProcessManager 호환성 전수 검증 (Fix Seed Pack Migration Pipeline & ProcessManager Compatibility)

**Feature Branch**: `113-fix-seed-pack-migration-scripts`

**Created**: 2026-08-08

**Status**: Draft

**Input**: User description: "지금 프로젝트를 시드 팩을 만들고 tar 파일과 unpack_seed.sh를 다른 플렛폼으로 이전해서 언팩->setup->벤치마크 하는 흐름에 문제가 없는지 make_seed_pack.sh / 구성 내용 검증 / unpack_seed.sh / setup.sh / scripts 폴더의 .py와 .sh 들 검증, 검토해서 스펙에 반영해"

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 타 플랫폼 마이그레이션 언팩->setup->벤치마크 원스톱 무결성 보장 (Priority: P1) 🎯 MVP

운영자 및 인프라 관리자는 현재 환경에서 `make_seed_pack.sh`로 시드 팩 아카이브를 생성하고, 타 서버/플랫폼으로 `vllm_serv_seed.tar.gz`(또는 `.zip`) 및 `unpack_seed.sh`를 이관하여 `unpack_seed.sh` -> `./setup.sh` -> `benchmark_context_window.py` / `benchmark_quality.py` 실행 흐름을 구동할 때 스크립트 누락이나 `AttributeError` 예외 없이 100% 정상 완수되기를 원합니다.

**Why this priority**: 플랫폼 간 백업 및 원클릭 복원/배포 파이프라인의 안정성을 보장하는 핵심 기능입니다.

**Independent Test**:
1. `./scripts/make_seed_pack.sh -o dist/test_seed.tar.gz`로 시드 팩 아카이브 생성.
2. 임시 목적지 디렉토리로 이관 후 `./scripts/unpack_seed.sh -i dist/test_seed.tar.gz --verify-only` 및 압축 해제 실행.
3. `./setup.sh --skip-build --skip-benchmark` 실행 후 `uv run python scripts/benchmark_context_window.py --skip-benchmark` 및 `uv run python scripts/benchmark_quality.py` 구동 시 에러 0건 검증.

**Acceptance Scenarios**:

1. **Given** `make_seed_pack.sh` 및 `unpack_seed.sh`가 구동될 때, **When** 아카이브 수록/해제 검증을 진행하면, **Then** 핵심 제어 스크립트(`process_manager.py`, `model_downloader.py`, `benchmark_quality.py`, `benchmark_context_window.py`, `setup.sh`, `unpack_seed.sh`, `make_seed_pack.sh`) 전수가 필수 수록 항목으로 검증되어야 한다.
2. **Given** `./setup.sh`가 구동될 때, **When** 필수 프로젝트 기본 파일 검증(Step 1)을 수행하면, **Then** `model_downloader.py`, `benchmark_context_window.py`, `unpack_seed.sh`를 포함한 필수 스크립트 전수의 존재 여부를 검사해야 한다.
3. **Given** 벤치마크 스크립트가 `ProcessManager` 헬퍼 메서드(`calculate_base_vram_mb`, `force_kill_zombie_llama_servers`)를 클래스/정적/인스턴스 어느 방식으로 호출하더라도, **When** 메서드가 실행되면, **Then** `AttributeError` 예외 없이 하위 호환 동작해야 하며, `getattr`/`try-except` 이중 폴백 코드가 가동되어야 한다.

---

### User Story 2 - 시드 팩 패키징 제외/수록 규칙 및 루트 심볼릭 링크 안전 재구성 (Priority: P2)

개발자는 시드 팩 생성 시 대용량 모델 가중치(`models/`), 가상환경(`.venv`), 로그 및 빌드 아티팩트가 정확히 제외되고, 복원 시 루트 심볼릭 링크(`start_server.sh`, `stop_server.sh`, `status_server.sh`)가 비파괴적으로 안전하게 재설정되기를 원합니다.

**Why this priority**: 시드 팩 용량을 최소화(경량화)하면서도 이관 후 실행 진입점 심볼릭 링크가 깨지지 않도록 보장합니다.

**Independent Test**: `make_seed_pack.sh` 생성물 아카이브의 용량이 모델 가중치 제외 기준(<50MB)을 유지하고, `unpack_seed.sh` 후 `./setup.sh` 실행 시 루트 심볼릭 링크가 정상 연결되는지 검증.

**Acceptance Scenarios**:

1. **Given** `make_seed_pack.sh` 구동 시, **When** `.tar.gz` 및 `.zip` 아카이브를 생성하면, **Then** `models/`, `.venv/`, `.bin/`, `logs/`, `build/`, `dist/`, `.git/`, `.specify/` 디렉터리가 정확히 제외되어야 한다.
2. **Given** `setup.sh`가 구동될 때, **When** `start_server.sh`, `stop_server.sh`, `status_server.sh` 쉘 스크립트를 생성/연결하면, **Then** 루트 디렉토리 심볼릭 링크가 기존 깨진 링크를 안전하게 대체(force relink)해야 한다.

---

### Edge Cases

- 타겟 플랫폼에 `unzip`이나 `tar`가 누락된 경우 `python3 -m zipfile` 모듈 폴백 동작 검증.
- `ProcessManager` 클래스 메서드가 외부 스크립트에서 인스턴스 미생성 상태로 `ProcessManager.calculate_base_vram_mb(...)`로 호출되거나 인스턴스로 `pm.force_kill_zombie_llama_servers()`로 호출되는 이중 패턴 처리.
- `make_seed_pack.sh` 실행 시 `wheels/legacy_i7_930` 사전 빌드 휠 디렉터리가 있을 경우와 없을 경우 모두 검증 통과 처리.

---

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `make_seed_pack.sh` 및 `unpack_seed.sh` 필수 파일 검증 목록에 `process_manager.py`, `model_downloader.py`, `benchmark_quality.py`, `benchmark_context_window.py`, `setup.sh`, `unpack_seed.sh`, `make_seed_pack.sh` 전수 반영.
- **DoD-002**: `setup.sh` 필수 파일 검증 목록(Step 1) 동기화 완료.
- **DoD-003**: `ProcessManager` 정적/인스턴스 하위 호환 및 `benchmark_context_window.py` 방어 코드 완납.
- **DoD-004**: 전체 단위 테스트 `pytest tests/unit/` 100% PASS 검증.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `scripts/make_seed_pack.sh`는 아카이브 생성 후 수록 검증 단계(`verify_archive_entry`)에서 `process_manager.py`, `model_downloader.py`, `benchmark_quality.py`, `benchmark_context_window.py`, `setup.sh`, `unpack_seed.sh`, `make_seed_pack.sh` 파일의 수록 여부를 필수 검증해야 한다.
- **FR-002**: `scripts/unpack_seed.sh`는 사전/사후 무결성 검증 단계(`REQUIRED_ENTRIES`)에서 `process_manager.py`, `model_downloader.py`, `benchmark_quality.py`, `benchmark_context_window.py`, `setup.sh`, `make_seed_pack.sh` 파일의 복원 여부를 필수 확인해야 한다.
- **FR-003**: `scripts/setup.sh`는 Step 1 필수 파일 존재 검증 목록(`REQUIRED_FILES`)에 `src/core/model_downloader.py`, `scripts/benchmark_context_window.py`, `scripts/unpack_seed.sh`를 포함하여 마이그레이션 스크립트 누락을 사전 차단해야 한다.
- **FR-004**: `src/core/process_manager.py`는 `calculate_base_vram_mb` 및 `force_kill_zombie_llama_servers` 메서드를 `@staticmethod` 및 인스턴스 메서드 양쪽 모두로 바인딩하여 `ProcessManager.method()` 및 `pm.method()` 호출에서 `AttributeError`가 발생하지 않도록 이중 하위 호환성을 보장해야 한다.
- **FR-005**: `scripts/benchmark_context_window.py` 및 `scripts/benchmark_quality.py`는 `ProcessManager` 헬퍼 메서드 호출 시 `getattr` 및 `try-except` 폴백 코드를 적용하여 레거시 환경에서도 런타임 크래시 없이 안전하게 실행되어야 한다.
- **FR-006**: `scripts/setup.sh`는 `scripts/start_server.sh`, `scripts/stop_server.sh`, `scripts/status_server.sh` 생성 후 프로젝트 루트 심볼릭 링크 연결 시 깨진 링크나 일반 파일 존재 시 안전하게 원자적 갱신(`ln -sf`)을 수행해야 한다.

---

## Clarifications

### Session 2026-08-08

- Q: ProcessManager 헬퍼 메서드(calculate_base_vram_mb, force_kill_zombie_llama_servers)의 하위 호환성 복원 시 어떤 방식을 사용할까요? → A: ProcessManager 내부 staticmethod/classmethod 장식자 보강과 함께, benchmark_context_window.py 호출부에도 getattr/try-except 폴백 방어 코드를 적용하여 이중 하위 호환성 보장.
- Q: 시드 팩 파이프라인(make_seed_pack.sh, unpack_seed.sh) 검토 및 검증 요구사항은 어떻게 반영할까요? → A: make_seed_pack.sh 및 unpack_seed.sh의 필수 아카이브 구성 요소 무결성 검사 항목에 process_manager.py, model_downloader.py, benchmark_quality.py, benchmark_context_window.py를 추가하여 마이그레이션 시 핵심 스크립트 누락 방지.
- Q: 언팩->setup->벤치마크 전 파이프라인(make_seed_pack.sh, unpack_seed.sh, setup.sh, scripts/*.py, scripts/*.sh) 전수 무결성 검증 추가 방식은? → A: setup.sh 필수 검증 목록(REQUIRED_FILES) 및 pack/unpack 검증 스크립트 리스트를 동기화하고, ProcessManager 정적/인스턴스 호출과 benchmark_context_window.py 예외 처리에 2중 방어망 적용.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `make_seed_pack.sh` -> `unpack_seed.sh` -> `./setup.sh` -> `benchmark_context_window.py` / `benchmark_quality.py` 전 파이프라인 런타임 구동 시 에러 0건.
- **SC-002**: `tests/unit/test_seed_pack.py`, `tests/unit/test_process_manager.py`, `tests/unit/test_benchmark_context.py` 포함 전체 단위 테스트 수트 100% PASS 유지.

---

## Assumptions

- 타겟 플랫폼 환경(GTX 1070, GTX 1080 Ti, RTX 3060 등)에서 Python 3.12 및 Linux bash 환경이 제공됨.
- `make_seed_pack.sh` 생성 아카이브는 소스코드 및 스크립트 전수를 포함하며 대용량 모델 가중치(`models/`)는 배제하여 경량 이관을 보장함.

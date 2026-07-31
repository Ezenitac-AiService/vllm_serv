# Feature Specification: make_seed_pack.sh 사전 휠 빌드 시 scikit-build-core 빌드 백엔드 누락 오류 해결 (058-fix-make-seed-pack-build-backend)

**Feature Branch**: `058-fix-make-seed-pack-build-backend`  
**Created**: 2026-07-31  
**Status**: Draft  
**Input**: User error log: `BackendUnavailable: Cannot import 'scikit_build_core.build'` in `make_seed_pack.sh` during legacy prebuilt wheel compilation.

---

## Clarifications

### Session 2026-07-31

- Q: `make_seed_pack.sh` 사전 휠 빌드 시 `scikit-build-core` 백엔드 오류 해결 방식 → A: Option C (`make_seed_pack.sh`에서 `--no-build-isolation` 제거 및 `pyproject.toml` / 빌드 환경에 `scikit-build-core` 및 `cmake` 의존성 보강 적용)

---

## Overview & Background

`make_seed_pack.sh` 실행 시 레거시 서비스 타깃(`legacy-i7-930-gtx1070`, Nehalem CPU, GTX 1070)용 사전 컴파일 휠(`wheels/legacy_i7_930/*.whl`)을 빌드할 때 `--no-build-isolation` 옵션이 적용되어 있어 `pip`가 조립 환경의 빌드 백엔드인 `scikit_build_core.build`를 임포트하지 못하고 `pip._vendor.pyproject_hooks._impl.BackendUnavailable: Cannot import 'scikit_build_core.build'` 예외가 발생하며 사전 휠 빌드가 중단되는 현상이 규명되었습니다.

본 명세는 `make_seed_pack.sh` 사전 휠 빌드 파이프라인에서 빌드 백엔드(`scikit-build-core`) 미설치 격리 오류를 근본적으로 해결하여 100% 정상 작동하는 레거시 사전 휠을 생성하도록 개선합니다.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - make_seed_pack.sh 빌드 백엔드 격리 해제 및 정상 사전 휠 생성 (Priority: P1) 🎯 MVP

개발 머신 또는 이관 준비 시스템에서 `./scripts/make_seed_pack.sh`를 실행할 때, `BackendUnavailable: Cannot import 'scikit_build_core.build'` 오류 없이 `scikit-build-core` 백엔드를 통해 `wheels/legacy_i7_930/*.whl` 사전 휠을 성공적으로 컴파일하고 검증합니다.

**Why this priority**: 레거시 타깃 서버 마이그레이션 시 수 분이 소요되는 소스 컴파일 없이 수 초 만에 서버를 즉시 복원하기 위해 사전 휠 완결성이 필수적입니다.

**Independent Test**: `./scripts/make_seed_pack.sh --build-legacy` 실행 시 `BackendUnavailable` 에러 없이 `wheels/legacy_i7_930/llama_cpp_python-*.whl` 휠이 생성되고 Post-Build 검증을 통과합니다.

**Acceptance Scenarios**:

1. **Given** `make_seed_pack.sh` 실행 시, **When** 사전 휠 컴파일 단계에 진입하면, **Then** `--no-build-isolation` 옵션 제거 및 빌드 의존성 보강으로 `scikit_build_core.build` 백엔드 누락 예외가 발생하지 않고 휠이 정상 빌드되어야 한다.
2. **Given** 빌드된 `wheels/legacy_i7_930/*.whl` 휠 파일이 존재할 때, **Then** `verify_wheel_binary.py` 검증을 거쳐 `vllm_serv_seed.tar.gz` 아카이브에 수록되어야 한다.

---

### User Story 2 - setup.sh 및 pyproject.toml / 빌드 환경 의존성 완결성 (Priority: P2)

가상환경 및 빌드 파이프라인에서 `scikit-build-core` 및 `cmake` 등 C++ 휠 컴파일 필요 백엔드 패키지 선언을 보강하여 어떠한 환경에서도 온디맨드 컴파일 및 사전 빌드가 안정적으로 구동되도록 합니다.

**Why this priority**: 패키지 매니저 버전 변화 및 격리 플래그 동작 변화에도 강건한 빌드 수명주기를 보장합니다.

**Independent Test**: `uv run pytest tests/unit/test_seed_pack.py` 실행 시 사전 빌드 및 빌드 백엔드 검증 테스트가 100% 성공합니다.

**Acceptance Scenarios**:

1. **Given** 가상환경 또는 uv 빌드 격리 모드에서, **When** `llama-cpp-python` 휠을 빌드하면, **Then** 필요한 `scikit-build-core` 백엔드가 자동 해제/공급되어 빌드가 완결되어야 한다.

---

### Edge Cases

- `uv` 패키지 매니저가 미설치된 환경에서는 빌드 스킵 로그를 남기고 기존 사전 휠 아티팩트를 보존한다.
- 네트워크가 차단된 오프라인 환경에서 빌드 시도 시 설치되어 있는 가상환경 내 빌드 백엔드를 활용하거나 온디맨드 소스 컴파일 Fallback을 안전하게 안내한다.

---

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `./scripts/make_seed_pack.sh` 실행 시 `BackendUnavailable: Cannot import 'scikit_build_core.build'` 예외가 100% 제거된다.
- **DoD-002**: `wheels/legacy_i7_930/*.whl` 사전 휠이 성공적으로 생성되고 `verify_wheel_binary.py` 3중 검증을 통과한다.
- **DoD-003**: `tests/unit/test_seed_pack.py` 단위 및 회귀 테스트 수트가 100% 통과한다.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `scripts/make_seed_pack.sh`의 휠 빌드 구문에서 `--no-build-isolation` 옵션을 제거하고 `pyproject.toml` 및 빌드 환경에 `scikit-build-core` / `cmake` 의존성을 보강하여 빌드 백엔드 임포트 오류를 원천 차단해야 한다.
- **FR-002**: 생성된 `wheels/legacy_i7_930/*.whl` 휠 파일에 대해 `verify_wheel_binary.py` Post-Build 3중 실측 검증(AVX=0, CUDA=1)을 수행해야 한다.
- **FR-003**: `tests/unit/test_seed_pack.py`에 `make_seed_pack.sh` 빌드 백엔드 정상 구동 및 휠 생성 검증 테스트 단정을 수록해야 한다.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `make_seed_pack.sh` 사전 휠 빌드 성공률 100% (BackendUnavailable 오류 0건).
- **SC-002**: 생성된 Seed Pack 아카이브 내 유효 사전 휠 수록률 100%.
- **SC-003**: `uv run pytest` 단위 테스트 Pass율 100%.

---

## Assumptions

- `uv` 및 `pip` 빌드 시스템은 PEP 517/PEP 518 규격을 준수하여 빌드 격리 모드에서 pyproject.toml 선언 백엔드(`scikit-build-core`)를 정상 다운로드/사용할 수 있다.
- 기존 개발 머신 및 레거시 서비스 플랫폼 설정(`config/platform_profiles.json`)과의 호환성을 유지한다.

# Feature Specification: Seed Pack Wheel Validation & Setup Failure Diagnostics (시드 팩 사전 빌드 휠 정밀 검증 기반 재빌드 및 Fast-Track 진단 강화)

**Feature Branch**: `035-seed-pack-wheel-diagnostics`

**Created**: 2026-07-30

**Status**: Draft

**Input**: User description: "/home/dev/storage/vllm_serv/log.txt 널 믿는게 아니었는데" (기존 휠을 무조건 삭제하고 매번 컴파일하는 대신, 기존 휠의 AVX 유입 여부를 정밀 검증하여 통과 시 재사용하고 실패 시에만 재컴파일하여 불필요한 빌드 시간 낭비를 방지함)

## Clarifications

### Session 2026-07-30

- Q: `make_seed_pack.sh`에서의 사전 빌드 휠 검증 및 재빌드 정책 → A: `wheels/legacy_i7_930/*.whl`이 존재할 때 무조건 삭제하지 않고, 휠 내부 `.so` 아티팩트의 AVX 명령어 포함 여부(0개) 및 CUDA 지원 여부를 먼저 정밀 검증한다. 검증 통과 시 기존 휠을 즉시 재사용하고, 검증 실패 시에만 휠을 삭제 및 재컴파일하여 빌드 시간을 최적화한다.
- Q: 외부 도구(`objdump`) 미설치 환경 대비 휠 바이너리 AVX 검증 방식 → A: 파이썬 내장 바이너리 스캐너(zipfile + .so ELF 디코딩/AVX 바이트코드 정밀 스캔)를 구현하여 외부 CLI 도구 의존 없이 휠 내부의 모든 `.so` 바이너리를 100% 전수 검증한다.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 기존 사전 빌드 휠 파이썬 내장 스캐너 정밀 검증 및 조건부 재컴파일 (Priority: P1) 🎯 MVP

엔지니어가 `scripts/make_seed_pack.sh`를 실행할 때, `wheels/legacy_i7_930/` 디렉터리에 휠이 이미 존재하면 파이썬 내장 바이너리 스캐너(외부 `objdump` 도구 불필요)로 휠 ZIP 패키지 내 **모든 `.so` 바이너리 전체를 스캔**하여 AVX 명령어 포함 여부(0개) 및 CUDA 지원 여부를 검증한다. 검증을 통과하면 무거운 C++ 재컴파일 없이 기존 휠을 즉시 사용하고, AVX 유입 등으로 검증 실패 시에만 해당 휠을 깨끗이 삭제하고 SSE4.2 / CUDA sm_61 전용 휠로 새로 빌드한다.

**Why this priority**: 검증된 바이너리가 존재함에도 불필요하게 15~30분 소요되는 C++ 소스 재컴파일을 반복하지 않으면서, 외부 시스템 CLI 도구 의존성 없이 오염된 휠(AVX 포함 휠)의 유입을 원천 차단하기 위함이다.

**Independent Test**: `wheels/legacy_i7_930/`에 정상 휠 및 AVX 오염 휠을 각각 배치한 후 `make_seed_pack.sh` 실행 시 파이썬 바이너리 스캐너가 정상 휠은 즉시 재사용하고 오염 휠은 자동 감지/삭제 후 재컴파일하는지 검증한다.

**Acceptance Scenarios**:

1. **Given** AVX가 유입된 구형/오류 휠이 존재할 때, **When** `scripts/make_seed_pack.sh`를 실행하면, **Then** 파이썬 바이너리 스캐너가 검증 실패를 감지하여 해당 휠을 삭제하고 `-DGGML_AVX=OFF` 인자로 휠을 새로 컴파일한다.
2. **Given** AVX 명령어가 0개이고 CUDA 지원이 확인된 정상 휠이 존재할 때, **When** `scripts/make_seed_pack.sh`를 실행하면, **Then** 재컴파일을 스킵하고 기존 휠을 즉시 시드 팩에 패키징한다.

---

### User Story 2 - `setup.sh` 사전 빌드 휠 검증 실패 원인 진단 및 에러 가독성 표출 (Priority: P2)

타겟 머신에서 `scripts/setup.sh` 실행 중 사전 빌드 휠 Fast-Track 복원 후 `llama_supports_gpu_offload()` 검증이 실패하는 경우, `2>/dev/null`로 파이썬 오류를 숨기지 않고 실패 원인을 구조화된 1줄 핵심 진단 로그(예: `SIGILL Illegal Instruction`, `CUDA Driver Mismatch`, `Missing Shared Library`)와 함께 상세 예외 Traceback을 명시적으로 화면 및 로그에 출력한다.

**Why this priority**: Fast-Track 실패 원인이 AVX 명령어 미지원(SIGILL)인지, CUDA 드라이버 라이브러리 로드 실패인지 현장에서 즉시 명확히 식별할 수 있게 하기 위함이다.

**Independent Test**: Fast-Track 검증 구문 실행 시 에러 발생 시 `2>/dev/null` 억제 없이 핵심 진단 사유와 상세 예외 텍스트가 표출되는지 확인한다.

**Acceptance Scenarios**:

1. **Given** `scripts/setup.sh`에서 사전 빌드 휠 GPU 검증을 수행할 때, **When** 검증 명령이 실패하면, **Then** `2>/dev/null`로 억제되지 않은 핵심 실패 분류 메시지 및 상세 Traceback이 화면에 표출되어야 한다.

---

### User Story 3 - 휠 정밀 검증 및 진단 출력 회귀 테스트 수록 (Priority: P3)

`tests/unit/test_seed_pack_legacy.py` 및 `tests/unit/test_shell_scripts.py`에 파이썬 내장 휠 AVX 정밀 검증 로직 및 setup.sh 진단 에러 출력 검증 구문 테스트를 추가하여 회귀를 예방한다.

**Why this priority**: 향후 시드 팩 빌드 스크립트 수정 시 휠 무조건 삭제나 검증 스킵, 에러 은폐 구문이 재유입되는 것을 방지한다.

**Independent Test**: `uv run pytest tests/unit/test_seed_pack_legacy.py` 실행 시 해당 테스트 케이스들이 100% 통과한다.

**Acceptance Scenarios**:

1. **Given** 테스트 수트를 실행할 때, **When** `test_seed_pack_legacy.py` 및 `test_shell_scripts.py`를 수행하면, **Then** 휠 AVX 정밀 검증 조건 및 setup.sh 진단 로그 출력이 성공적으로 검증된다.

---

### Edge Cases

- `make_seed_pack.sh` 실행 환경에 외부 `objdump` 도구가 설치되지 않은 환경에서도 파이썬 순수 모듈로 100% 바이너리 스캔 정상 동작.
- `setup.sh` 파이썬 출력 메시지가 매우 길 때 1줄 요약 진단 메시지와 함께 Traceback 구분 출력.

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `scripts/make_seed_pack.sh`에 파이썬 내장 바이너리 스캐너 기반 휠 정밀 검증(AVX 0개 확인) 통과 시 재사용 & 실패 시 삭제 후 `-DGGML_AVX=OFF` 재빌드 로직 구현 완료
- **DoD-002**: `scripts/setup.sh`에서 Fast-Track 휠 검증 구문의 `2>/dev/null` 제거 및 실패 원인 분류 핵심 로그 및 stderr 상세 출력 구현
- **DoD-003**: `tests/unit/test_seed_pack_legacy.py` 및 `tests/unit/test_shell_scripts.py` 회귀 테스트 작성 및 100% 통과

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `make_seed_pack.sh`는 기존 `wheels/legacy_i7_930/*.whl` 존재 시 파이썬 내장 스캐너로 휠 패키지 내 모든 `.so` 바이너리의 AVX 명령어 수(0개) 및 CUDA 지원 여부를 외부 도구 의존 없이 검증하여, 검증 통과 시 기존 휠을 즉시 재사용하고 검증 실패 또는 미존재 시에만 삭제 후 `-DGGML_AVX=OFF -DGGML_AVX2=OFF -DGGML_F16C=OFF -DGGML_FMA=OFF -DGGML_NATIVE=OFF` 인자로 새로 컴파일해야 한다.
- **FR-002**: `setup.sh`는 사전 빌드 휠 복원 후 `llama_supports_gpu_offload()` 검증 실패 시 에러를 은폐하지 않고 구조화된 진단 사유와 실제 파이썬 오류 원인 메시지(stderr)를 출력 및 로그로 기록해야 한다.
- **FR-003**: 단위 테스트 수트는 `make_seed_pack.sh`의 휠 AVX 정밀 검증 로직과 `setup.sh`의 에러 노출 구문을 자동 검증해야 한다.

### Key Entities

- **SeedPackBuildOptions**: 시드 팩 구성 시 휠 검증 규칙(`verify_wheels`), 파이썬 AVX 스캐너, CMAKE AVX 비활성화 인자 및 조건부 클린 정책을 제어하는 설정 개체.
- **SetupValidationDiagnostic**: Fast-Track 휠 검증 시도 결과, 반환 코드, 분류된 실패 사유 및 표준 오류(stderr) 캡처 텍스트를 기록하는 진단 개체.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 정상 휠 감지 시 C++ 재컴파일 시간 0초 (즉시 재사용).
- **SC-002**: 외부 CLI 도구(`objdump`) 설치 여부와 무관하게 파이썬 자체 스캐너로 100% 휠 바이너리 검증 수행.
- **SC-003**: AVX 오염 휠 감지 시 100% 자동으로 기존 휠 삭제 후 안전한 휠로 재컴파일.
- **SC-004**: `setup.sh` 실행 중 Fast-Track 휠 검증 실패 시 분류된 원인 에러 메시지 100% 출력.
- **SC-005**: 전체 `uv run pytest` 수트 100% 통과.

## Assumptions

- `i7-930` CPU는 Nehalem 아키텍처로 AVX를 지원하지 않으며 SSE4.2까지 지원한다.
- `make_seed_pack.sh`는 외부 CLI 도구 없이 파이썬 내장 모듈로 휠 바이너리를 정밀 스캔할 수 있다.

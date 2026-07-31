# Feature Specification: 플랫폼 프로필 매칭 정교화 및 출력 메시지 다듬기

**Feature Branch**: `022-refine-platform-profile-matching`

**Created**: 2026-07-30

**Status**: Draft

**Input**: User description: "다듬기를 하면 될거 같아. 현재 플렛폼은 i7 930이 아니고 e3 1231v3인데, 출력이 저렇네, 명령어 지원 플래그는 잘 체크한거 같긴 한데, CMake 인자 공백 및 프로필 매칭 정교화 필요"

## Clarifications

### Session 2026-07-30

- Q: 타 플랫폼으로 Seed Pack 이관 후 `setup.sh` 실행 시 기존/CPU 전용 `llama.cpp` 아티팩트를 기존 상태에서 지우고 새로 빌드하는가? → A: 예, `setup.sh`는 `uv pip install --force-reinstall --no-cache-dir` 옵션을 사용하여 타겟 하드웨어의 감지 결과(`CMAKE_ARGS`)를 바탕으로 이전 빌드 아티팩트를 강제 재설치(Clean Rebuild)합니다.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - CMake 빌드 인자 띄어쓰기 서식 버그 수정 (Priority: P1)

운영자가 `./status_server.sh` 또는 `./setup.sh`를 실행할 때, 생성된 CMake 인자 문자열에서 `-DGGML_F16C=ON`과 `-DGGML_FMA=ON` 사이에 공백이 누락되는 버그(`-DGGML_F16C=ON-DGGML_FMA=ON`)를 수정하여 파싱 에러 없는 정확한 공백 구분 문자열을 출력한다.

**Why this priority**: CMake 빌드 플래그 서식 오류는 네이티브 빌드 컴파일 시 인자 파싱 에러를 유발할 수 있으므로 최우선으로 해결해야 한다.

**Independent Test**: `uv run python -m src.core.cpu_detector --format cmake` 실행 시 반환된 문자열의 인자 간 공백 구분을 확인한다.

**Acceptance Scenarios**:

1. **Given** 하드웨어 감지 수행, **When** CMake 플래그 문자열 생성 시, **Then** 모든 인자(특히 `-DGGML_F16C`와 `-DGGML_FMA`) 사이에 정확히 하나의 공백이 포함된다.

---

### User Story 2 - 하드웨어 프로필 매칭 로직 정교화 (Priority: P1)

운영자가 하드웨어 정보 및 상태를 확인할 때, 단순 GPU Compute Capability(`sm_61`) 단일 기준이 아니라 CPU SIMD 지원 여부(Nehalem i7 930: AVX 미지원 vs Haswell Xeon E3-1231 v3: AVX2 지원)와 조합하여 정교하게 프로필을 판별하고 매칭된 프로필명을 정확히 표기한다.

**Why this priority**: Xeon E3-1231 v3(Haswell) 시스템에서 AVX/AVX2/FMA 지원이 정상 감지되었음에도 레거시 `legacy-i7-930-gtx1070` 프로필로 오인 표기되는 현상을 바로잡기 위함이다.

**Independent Test**: Xeon E3-1231 v3 + GTX 1080 Ti 환경에서 `cpu_detector --match-profile` 실행 시 `pascal-avx2-gtx1080ti` 또는 정확히 매칭된 프로필명이 출력되는지 확인한다.

**Acceptance Scenarios**:

1. **Given** Xeon E3-1231 v3 (AVX2 지원) + GTX 1080 Ti (sm_61) 시스템, **When** `--match-profile`을 실행하면, **Then** `legacy-i7-930-gtx1070` 대신 AVX2 가속이 반영된 매칭 프로필명(예: `pascal-avx2-gtx1080ti`)이 반환된다.
2. **Given** i7 930 (AVX 미지원) + GTX 1070 시스템, **When** `--match-profile`을 실행하면, **Then** 기존 레거시 프로필(`legacy-i7-930-gtx1070`)이 매칭된다.

---

### User Story 3 - 쉘 스크립트 출력 문구 및 안내 메시지 다듬기 (Priority: P2)

운영자가 `./make_seed_pack.sh`, `./status_server.sh`, `./setup.sh`를 실행할 때, 예시 및 안내문에서 특정 하드웨어명(`i7-930`)에 치우치지 않고 범용적이거나 실시간 감지된 타겟 서버 하드웨어를 다듬어 가독성 높은 리포트를 제공한다.

**Why this priority**: 안내문 및 예시 문구가 실제 운영 환경 하드웨어 정보와 부합하도록 다듬어 운영자 혼선을 방지한다.

**Independent Test**: `./make_seed_pack.sh` 실행 시 안내되는 타겟 서버 예시 문구가 정돈되어 표시되는지 확인한다.

**Acceptance Scenarios**:

1. **Given** Seed Pack 생성 실행, **When** 마이그레이션 안내문 출력 시, **Then** 타겟 서버 예시 문구가 정돈되어 명료하게 출력된다.

---

### Edge Cases

- `config/platform_profiles.json`에 정의되지 않은 신규 GPU/CPU 조합일 경우 `custom-avx2-sm61` 형태의 동적 하드웨어 라벨이 표시되는가?

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: CMake 플래그 생성 문자열에서 공백 누락 버그가 전면 수정된다.
- **DoD-002**: `config/platform_profiles.json`에 Xeon E3-1231 v3 / Haswell + Pascal 호환 프로필이 수록되고 CPU AVX2 지원 여부가 고려된 프로필 매칭 로직이 반영된다.
- **DoD-003**: `make_seed_pack.sh`, `status_server.sh`, `setup.sh` 출력 안내 문구가 정돈된다.
- **DoD-004**: 단위 및 통합 테스트가 추가/수정되고 100% 통과한다.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `src/core/cpu_detector.py`의 `get_llama_build_flags()`에서 생성하는 `cmake_args_list` 및 `cmake_args_str` 문자열의 각 옵션 사이에 반드시 하나의 공백이 포함되도록 수정해야 한다 (MUST).
- **FR-002**: `config/platform_profiles.json`에 Haswell CPU (AVX2 지원) + Pascal GPU 타겟 프로필(`pascal-avx2-gtx1080ti`)을 추가하고, `match_platform_profile()` 함수는 GPU Compute Capability뿐만 아니라 CPU의 AVX/AVX2 지원 여부를 복합 평가하여 프로필을 결정해야 한다 (MUST).
- **FR-003**: `make_seed_pack.sh` 및 관련 제어 스크립트의 안내 출력 메시지에서 예시 타겟 서버 문구를 다듬어 가독성을 높여야 한다 (MUST).
- **FR-004**: `setup.sh` 실행 시 `--force-reinstall --no-cache-dir` 인자를 통해 이전 하드웨어의 빌드 아티팩트를 무효화하고 현 하드웨어 기반으로 100% 강제 재설치(Clean Rebuild)하여 이관 시 바이너리 충돌을 방지해야 한다 (MUST).

### Key Entities

- **Platform Profile Entry**: `config/platform_profiles.json`에 저장되는 하드웨어 아키텍처 및 SIMD/CUDA 사양 프로필
- **CMake Flags String**: `src.core.cpu_detector`에서 생성하는 공백 구분 CMake 컴파일 인자 리스트

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `uv run python -m src.core.cpu_detector --format cmake` 출력값에 `-DGGML_F16C=ON -DGGML_FMA=ON` 형태로 공백이 정확히 포함된다.
- **SC-002**: Xeon E3-1231 v3 + GTX 1080 Ti 환경에서 `cpu_detector --match-profile` 실행 시 `pascal-avx2-gtx1080ti` 프로필이 100% 매칭된다.
- **SC-003**: 전체 pytest 테스트 수트 실행 시 100% 통과를 유지한다.

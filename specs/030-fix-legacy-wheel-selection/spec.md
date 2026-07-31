# Feature Specification: 구형 i7-930 타겟 패키지 설치 시 llama_cpp_python 사전 빌드 휠 정확한 선택 및 복원 오류 수정 (030-fix-legacy-wheel-selection)

**Feature Branch**: `030-fix-legacy-wheel-selection`

**Created**: 2026-07-30

**Status**: Draft

**Input**: User log analysis (`/home/dev/storage/vllm_serv/log.txt`): `scripts/setup.sh` 실행 시 `wheels/legacy_i7_930/*.whl` 대상 `head -n 1` 알파벳 정렬에 의해 `llama_cpp_python` 휠 대신 `annotated_doc-0.0.5-py3-none-any.whl`이 선택 및 설치되어 CUDA GPU 오프로드 검증(`llama_supports_gpu_offload()`)이 실패하는 문제 해결.

## Clarifications

### Session 2026-07-30

- Q: 사전 빌드 휠 복원 시 로컬 패키지 고속 주입(오프라인 모드) 및 휠 버전 탐색 정책 → A: Option A (`--no-index --find-links wheels/legacy_i7_930` 플래그 적용 및 `ls -v wheels/legacy_i7_930/llama_cpp_python*.whl | tail -n 1`을 이용한 정확한 버전 정렬 탐색으로 외부 인덱스 연결 없이 로컬 오프라인 고속 설치)
- Q: 사전 빌드 휠 훼손/아키텍처 불일치로 인한 GPU 오프로드 검증 실패 시 대응 정책 → A: Option A (`llama_supports_gpu_offload()` 검증 실패 시 Fast-Track 설치 실패로 간주하고, 경고 로그 출력 후 소스 컴파일 파이프라인으로 자동 Fallback 수행)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - i7-930 타겟 플랫폼의 llama_cpp_python 사전 컴파일 휠 명시적 탐색 및 고속 설치 (Priority: P1) 🎯 MVP

구형 i7-930 머신(Platform C: `legacy-i7-930-gtx1070`)에서 `scripts/setup.sh`를 실행할 때, `wheels/legacy_i7_930/` 디렉터리에 존재하는 여러 종속성 휠 파일들 중 `llama_cpp_python` 전용 사전 빌드 휠(`.whl`) 및 관련 패키지들을 명시적으로 탐색 및 설치하여 C++ 소스 재컴파일 없이 GPU 가속이 활성화된 `llama-cpp-python` 환경을 정상 구축합니다.

**Why this priority**: 잘못된 휠 파일(`annotated_doc`) 선택으로 인해 Fast-Track 휠 복원 후 CUDA GPU 가속 검증이 실패하는 치명적 오류를 해결하여 i7-930 머신의 3분 이내 구축을 보장하기 위함입니다.

**Independent Test**: `wheels/legacy_i7_930/` 디렉터리에 알파벳순으로 앞선 종속성 휠(`annotated_doc`, `anyio` 등)과 `llama_cpp_python-*.whl`이 함께 존재하는 상태에서 `scripts/setup.sh` 실행 시 `llama_cpp_python` 사전 빌드 휠이 정확히 선택·설치되고 `llama_supports_gpu_offload()` GPU 가속 검증이 통과하는지 검증합니다.

**Acceptance Scenarios**:

1. **Given** `wheels/legacy_i7_930/` 디렉터리에 `annotated_doc-*.whl` 및 `llama_cpp_python-*.whl` 등 다수의 휠 파일이 수록된 상태에서, **When** `scripts/setup.sh`를 실행하여 Fast-Track 복원을 수행하면, **Then** 시스템은 `head -n 1`로 인한 잘못된 휠 선택 없이 `ls -v wheels/legacy_i7_930/llama_cpp_python*.whl | tail -n 1` 구문으로 최신 `llama_cpp_python` 휠을 선택하고 `--no-index --find-links wheels/legacy_i7_930` 오프라인 옵션으로 고속 설치하여 CUDA GPU 가속 활성화 검증을 성공적으로 통과해야 한다.
2. **Given** `wheels/legacy_i7_930/` 내에 `llama_cpp_python*.whl` 아티팩트가 명시적으로 존재하는지 검증하는 로직에서, **When** `llama_cpp_python` 타겟 휠이 존재할 때, **Then** Fast-Track 휠 복원 성공 로그를 출력하고 CUDA 오프로드 지원 상태(`llama_supports_gpu_offload()`)를 참(True)으로 반환해야 한다.

---

### User Story 2 - llama_cpp_python 사전 빌드 휠 부재 또는 검증 실패 시 안정적 소스 컴파일 Fallback (Priority: P2)

i7-930 머신 구축 시 `wheels/legacy_i7_930/` 디렉터리에 타겟 휠(`llama_cpp_python*.whl`)이 누락되었거나, Fast-Track 휠 설치 후 GPU 가속 검증(`llama_supports_gpu_offload()`)에 실패한 경우, 시스템이 중단되지 않고 경고 메시지와 함께 C++ 소스 컴파일 파이프라인으로 안전하게 Fallback됩니다.

**Why this priority**: 사전 빌드 아티팩트 손상/유실 및 아키텍처 불일치 상황에서도 시스템이 멈추지 않고 대체 컴파일 경로로 구축을 완수할 수 있는 안전성을 보장하기 위함입니다.

**Independent Test**: `wheels/legacy_i7_930/` 디렉터리에 `llama_cpp_python` 휠이 없거나 휠 설치 후 GPU 가속 검증이 실패하는 환경에서 `scripts/setup.sh` 실행 시 Fallback 경고 로그가 출력되고 `CMAKE_ARGS` 소스 컴파일 파이프라인으로 전환되어 정상 설치되는지 검증합니다.

**Acceptance Scenarios**:

1. **Given** `wheels/legacy_i7_930/` 디렉터리에 `llama_cpp_python*.whl` 파일이 미존재하거나 Fast-Track 설치 후 GPU 오프로드 검증이 실패할 때, **When** `scripts/setup.sh` 파이프라인을 구동하면, **Then** 경고 로그를 출력하고 `INSTALLED_VIA_FAST_TRACK=0` 상태로 전환되어 기존 C++ 소스 컴파일 파이프라인을 수행해야 한다.

---

### Edge Cases

- `wheels/legacy_i7_930/` 디렉터리에 다른 `.whl` 파일들만 존재하고 `llama_cpp_python` 휠만 누락된 경우 `head -n 1` 패턴 매칭이 엉뚱한 패키지를 선택하지 않고 타겟 패키지 미존재로 정확히 인지하는가?
- `wheels/legacy_i7_930/` 디렉터리 내 모든 `.whl` 파일(종속성 포함)을 `uv pip install` 할 때 네트워크 미연결 시에도 `--no-index --find-links` 옵션으로 패키지 충돌 없이 오프라인 정상 설치되는가?
- Fast-Track 휠 설치 후 `llama_supports_gpu_offload()` 검증에 실패할 경우 에러로 setup.sh가 중단되지 않고 소스 컴파일 파이프라인으로 자동 재시도 Fallback 되는가?

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `scripts/setup.sh` 스크립트에서 `legacy-i7-930` 타겟 Fast-Track 휠 탐색 로직을 `ls -v wheels/legacy_i7_930/llama_cpp_python*.whl | tail -n 1` 및 `uv pip install "$LEGACY_WHEEL" --no-index --find-links wheels/legacy_i7_930` 명시적 오프라인 고속 설치 구문으로 개정 완료
- **DoD-002**: `annotated_doc` 등 타 종속성 휠이 함께 존재하는 환경에서 `llama_cpp_python` 사전 빌드 휠이 정상 선택 설치되고 CUDA GPU 가속 검증(`llama_supports_gpu_offload()`) 100% 통과 확인
- **DoD-003**: `llama_cpp_python` 휠 누락 또는 Fast-Track 후 GPU 가속 검증 실패 시 소스 컴파일 파이프라인 Fallback 동작 검증 완료
- **DoD-004**: 개정된 `setup.sh` 탐색/복원/Fallback 로직에 대한 단위 테스트(`tests/unit/test_seed_pack_legacy.py`) 100% 통과

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 (llama_cpp_python 휠 명시적 매칭 및 버전 정렬 탐색)**: `scripts/setup.sh` 실행 시 `legacy-i7-930` 타겟 프로필 감지 구문에서 휠 탐색 대상을 임의의 `*.whl` 1번째 파일이 아닌 `ls -v wheels/legacy_i7_930/llama_cpp_python*.whl 2>/dev/null | tail -n 1` 패턴으로 명시적 지정하여 최신 타겟 휠을 정확히 선택해야 한다.
- **FR-002 (오프라인 로컬 패키지 고속 복원)**: `wheels/legacy_i7_930/` 디렉터리에서 Fast-Track 휠 복원 시 `uv pip install "$LEGACY_WHEEL" --force-reinstall --no-index --find-links wheels/legacy_i7_930` 구문을 사용하여 외부 PyPI 인덱스 연결 없이 로컬 의존성 패키지와 함께 오프라인 고속 주입을 완료해야 한다.
- **FR-003 (패키지 검증 및 GPU 오프로드 검증 보장)**: Fast-Track 휠 설치 직후 `llama_cpp_python` 패키지 정상 설치 여부를 확인하고, 이어지는 `llama_supports_gpu_offload()` 검증에서 GPU 가속이 활성화되었음을 보장해야 한다.
- **FR-004 (타겟 휠 미존재 및 검증 실패 시 Fallback 보호)**: `wheels/legacy_i7_930/llama_cpp_python*.whl` 파일이 감지되지 않거나, Fast-Track 휠 설치 후 GPU 가속 검증(`llama_supports_gpu_offload()`)에 실패하는 경우, 경고 로그를 출력하고 `INSTALLED_VIA_FAST_TRACK=0` 상태로 자동 전환하여 C++ 소스 컴파일 파이프라인으로 안전하게 Fallback해야 한다.

### Key Entities

- **LegacyPrebuiltWheelSet**: `wheels/legacy_i7_930/` 디렉터리에 보관된 `llama_cpp_python` C++ 사전 컴파일 휠 및 관련 의존성 휠 패키지 아티팩트 집합.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `wheels/legacy_i7_930/` 디렉터리에 다종 휠이 존재하는 상황에서 `scripts/setup.sh` 실행 시 `llama_cpp_python` 휠 선택 오류 0건 및 100% 정상 설치
- **SC-002**: i7-930 타겟 머신에서 setup.sh Fast-Track 실행 후 `llama_supports_gpu_offload()` 검증 100% 통과 (실패 시 100% 소스 컴파일 Fallback 수행)
- **SC-003**: `tests/unit/test_seed_pack_legacy.py` 및 전체 pytest 수트 100% 통과

## Assumptions

- `wheels/legacy_i7_930/` 디렉터리에는 `make_seed_pack.sh` 실행 결과로 `llama_cpp_python-*.whl` 파일 및 관련 파이썬 의존성 휠이 함께 저장될 수 있음.
- `uv pip install` 명령에서 `--no-index --find-links wheels/legacy_i7_930` 옵션을 지정하면 외부 인터넷 연결 없이 디렉터리 내 사전 빌드 휠들만으로 의존성 해결 및 설치가 가능함.

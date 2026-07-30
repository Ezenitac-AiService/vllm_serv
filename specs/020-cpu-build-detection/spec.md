# Feature Specification: CPU 빌드 감지 및 다중 플랫폼 지원

**Feature Branch**: `020-cpu-build-detection`

**Created**: 2026-07-30

**Status**: Draft

**Input**: User description: "타겟 플랫폼이 하나 늘었어. i7 930, 24GB RAM, GTX 1070, Ubuntu Server 24.04 LTS. llama.cpp 빌드할때에 CPU 정보를 검출하고 지원하지 않는 명령에 대응한 플래그를 선택할 필요성이 생겼어."

## Clarifications

### Session 2026-07-30

- Q: CPU 감지 로직이 네이티브 `llama-server` CMake 빌드에만 적용되는가, `llama-cpp-python` pip 빌드에도 적용되는가? → A: 양쪽 모두 적용 (네이티브 CMake 빌드 + `llama-cpp-python` pip 빌드 시 `CMAKE_ARGS` 전파)
- Q: GTX 1070 (sm_61)과 RTX 3060 (sm_86) 두 GPU를 동시에 지원하는 CUDA 빌드 방식은? → A: 호스트 GPU 자동 감지하여 해당 아키텍처만 타겟 (빌드 머신 = 타겟 머신)
- Q: GTX 1070 VRAM 8GB 제약에 따른 모델 카탈로그 조정을 본 기능에 포함하는가? → A: 범위 외 — 실제 플랫폼별 사용할 모델은 `scripts/benchmark_quality.py` 품질/성능 벤치마크 보고서를 기반으로 선택하고 `config/` 설정 파일에서 관리함
- Q: GPU 감지 실패 시(`nvidia-smi` 없음, 드라이버 미설치) 빌드 동작은? → A: 빌드 중단 (기존 fail-fast 정책 유지, CPU-only 빌드 불허)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 레거시 CPU 환경에서 llama.cpp 자동 빌드 (Priority: P1)

운영자가 i7 930 (Nehalem 아키텍처) 기반 서버에서 llama.cpp를 빌드할 때, 빌드 시스템이 해당 CPU가 AVX, AVX2, F16C, FMA 등 최신 명령어 세트를 지원하지 않음을 자동으로 감지하여, 호환 가능한 빌드 플래그를 선택하고 정상적으로 빌드를 완료한다.

**Why this priority**: llama.cpp가 기본 빌드 옵션으로 최신 SIMD 명령어(AVX/AVX2)를 사용하도록 컴파일되면, i7 930과 같은 구세대 CPU에서는 `Illegal instruction` 오류로 바이너리가 실행 불가능해진다. 이는 새 타겟 플랫폼에서의 핵심 기능을 완전히 차단하므로 최우선 해결 과제이다.

**Independent Test**: i7 930 (또는 동등한 SSE4.2 only 환경)에서 빌드 스크립트를 실행하여 llama.cpp가 정상 컴파일되고, 생성된 바이너리가 `Illegal instruction` 없이 실행되는지 확인한다.

**Acceptance Scenarios**:

1. **Given** i7 930 CPU가 장착된 Ubuntu Server 24.04 LTS 시스템, **When** 빌드 스크립트를 실행하면, **Then** CPU 기능 감지가 수행되고 AVX/AVX2/F16C/FMA가 비활성화된 상태로 llama.cpp가 성공적으로 빌드된다.
2. **Given** AVX/AVX2를 지원하지 않는 CPU 환경, **When** 빌드된 llama.cpp 바이너리를 실행하면, **Then** `Illegal instruction` 오류 없이 정상 동작한다.
3. **Given** i7 930 시스템에 GTX 1070이 장착된 상태, **When** CUDA 백엔드를 활성화하여 빌드하면, **Then** GPU 가속이 정상적으로 활성화되면서 CPU 측 코드는 SSE4.2 범위 내에서만 컴파일된다.
4. **Given** i7 930 환경에서 `llama-cpp-python` 패키지를 설치할 때, **When** `setup.sh`가 실행되면, **Then** CPU 감지 결과가 `CMAKE_ARGS`에 반영되어 호환 가능한 바이너리가 빌드된다.

---

### User Story 2 - 기존 플랫폼과의 빌드 호환성 유지 (Priority: P1)

운영자가 기존 개발 장비(최신 CPU, RTX 3060)에서 동일한 빌드 스크립트를 실행할 때, CPU 감지 로직이 AVX2/FMA 등 최신 명령어 세트의 지원을 확인하고, 기존과 동일한 최적화 수준의 빌드를 생성한다.

**Why this priority**: 새 플랫폼 지원을 추가하면서 기존 환경의 성능이 저하되면 안 된다. 두 환경 모두 각자의 CPU 역량을 최대한 활용해야 한다.

**Independent Test**: 기존 개발 장비에서 빌드 스크립트를 실행하여 AVX2/FMA 등이 활성화된 빌드가 이전과 동일한 성능으로 생성되는지 확인한다.

**Acceptance Scenarios**:

1. **Given** AVX2/FMA를 지원하는 최신 CPU 시스템, **When** 빌드 스크립트를 실행하면, **Then** 해당 명령어 세트가 활성화된 상태로 llama.cpp가 빌드되어 최적 성능을 유지한다.
2. **Given** 기존 RTX 3060 환경, **When** 빌드 후 추론 성능을 측정하면, **Then** CPU 감지 로직 도입 전과 동등한 성능 수준을 달성한다.

---

### User Story 3 - CPU 기능 감지 결과 리포트 (Priority: P2)

운영자가 빌드 스크립트를 실행할 때, 감지된 CPU 정보와 선택된 빌드 플래그가 명확하게 로그로 출력되어, 어떤 최적화가 활성화/비활성화되었는지 한눈에 파악할 수 있다.

**Why this priority**: 디버깅과 문제 해결을 위해 빌드 과정의 투명성이 필요하다. CPU 감지 결과를 명시적으로 보여주면 빌드 실패 시 원인 파악이 용이하다.

**Independent Test**: 빌드 스크립트 실행 후 출력 로그에서 CPU 모델명, 지원/미지원 명령어 세트 목록, 최종 선택된 빌드 플래그를 확인한다.

**Acceptance Scenarios**:

1. **Given** 임의의 타겟 시스템, **When** 빌드 스크립트를 실행하면, **Then** 로그에 CPU 모델명, 아키텍처, 지원되는 명령어 세트(SSE4.2, AVX, AVX2, F16C, FMA 등) 목록이 출력된다.
2. **Given** 빌드 로그 출력, **When** 운영자가 로그를 확인하면, **Then** 최종적으로 CMake/컴파일러에 전달된 빌드 플래그 목록을 명확히 확인할 수 있다.

---

### User Story 4 - 타겟 플랫폼 프로필 관리 (Priority: P3)

운영자가 새로운 타겟 플랫폼의 하드웨어 정보(CPU, RAM, GPU, OS)를 프로젝트의 플랫폼 프로필 목록에 등록하여, 향후 빌드 및 테스트 시 참조 기준으로 활용한다.

**Why this priority**: 플랫폼이 증가함에 따라 각 타겟의 하드웨어 역량을 체계적으로 관리할 필요가 있다. 당장의 빌드 문제 해결보다는 장기적 운영 편의성에 기여한다.

**Independent Test**: 플랫폼 프로필 설정 파일에 새 타겟 플랫폼 정보를 등록하고, 빌드 시스템이 해당 프로필을 올바르게 참조하는지 확인한다.

**Acceptance Scenarios**:

1. **Given** 프로젝트에 플랫폼 프로필 정의가 존재하는 상태, **When** 새 타겟 플랫폼(i7 930, 24GB RAM, GTX 1070, Ubuntu Server 24.04 LTS) 정보를 등록하면, **Then** 빌드 시스템이 해당 프로필의 CPU 제약 조건을 인식하고 적절한 빌드 플래그를 적용한다.

---

### Edge Cases

- i7 930에서 컴파일러가 SSE4.2를 기본 타겟으로 인식하지 못하는 경우 어떻게 대응하는가?
- CPU 감지에서 `/proc/cpuinfo`가 읽기 불가능하거나 예상 형식이 아닌 경우 안전한 기본값으로 폴백하는가?
- GTX 1070 (Pascal, sm_61)에 대한 CUDA 컴파일 호환성은 사용 중인 CUDA 툴킷 버전으로 보장되는가?
- 크로스 컴파일 시나리오(빌드 머신 ≠ 타겟 머신)에서 CPU 감지가 빌드 머신의 CPU를 감지하여 잘못된 플래그를 적용하는 문제를 어떻게 방지하는가?
- GPU 드라이버가 설치되어 있지만 `nvidia-smi`가 GPU 정보를 반환하지 못하는 경우(예: GPU 하드웨어 오류) 빌드 시스템이 적절히 중단하는가?

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: CPU 명령어 세트를 자동으로 감지하는 로직이 빌드 스크립트에 통합되고, 단위 테스트를 통과한다.
- **DoD-002**: i7 930 (SSE4.2 only) 환경에서 llama.cpp가 `Illegal instruction` 없이 빌드 및 실행 가능하다.
- **DoD-003**: 기존 환경(AVX2/FMA 지원 CPU)에서의 빌드가 기존 최적화 수준을 유지한다.
- **DoD-004**: 빌드 로그에 감지된 CPU 기능과 선택된 빌드 플래그가 명확히 출력된다.
- **DoD-005**: 새 타겟 플랫폼(i7 930 + GTX 1070) 프로필이 프로젝트 설정에 등록된다.
- **DoD-006**: 모든 변경 사항에 대한 단위 테스트 및 통합 테스트가 작성되고 통과한다.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 빌드 시스템은 빌드 실행 시점에 호스트 CPU의 명령어 세트 지원 여부(SSE4.2, AVX, AVX2, F16C, FMA)를 자동으로 감지해야 한다 (MUST).
- **FR-002**: 감지 결과에 따라 llama.cpp 네이티브 CMake 빌드(`llama-server`) 및 `llama-cpp-python` pip 패키지 빌드(`CMAKE_ARGS` 전파) 양쪽 모두에 적절한 비활성화 플래그(`-DGGML_AVX=OFF`, `-DGGML_AVX2=OFF`, `-DGGML_F16C=OFF`, `-DGGML_FMA=OFF` 등)를 자동으로 적용해야 한다 (MUST).
- **FR-003**: CPU가 특정 명령어 세트를 지원하는 경우, 해당 명령어 세트에 대한 최적화 플래그를 활성화하여 최대 성능을 보장해야 한다 (MUST).
- **FR-004**: CPU 감지 실패 시 가장 보수적인 플래그 조합(모든 확장 명령어 비활성화)으로 안전하게 폴백해야 한다 (MUST).
- **FR-005**: 빌드 과정에서 감지된 CPU 모델명, 지원 명령어 세트 목록, 최종 적용된 빌드 플래그를 사람이 읽기 쉬운 형태로 로그에 출력해야 한다 (MUST).
- **FR-006**: 타겟 플랫폼별 하드웨어 프로필(CPU, RAM, GPU, OS)을 설정 파일로 관리할 수 있어야 한다 (MUST).
- **FR-007**: 빌드 시스템은 호스트에 장착된 GPU의 compute capability를 자동 감지하여 해당 아키텍처만을 CUDA 빌드 타겟으로 설정해야 한다 (MUST). GTX 1070의 경우 sm_61, RTX 3060의 경우 sm_86이 자동으로 선택된다.
- **FR-008**: 기존 타겟 플랫폼(RTX 3060 환경)의 빌드 설정 및 성능에 영향을 주지 않아야 한다 (MUST).
- **FR-009**: GPU 감지 실패 시(드라이버 미설치, `nvidia-smi` 부재 등) 빌드를 즉시 중단하고 명확한 오류 메시지를 출력해야 한다 (MUST). CPU-only 빌드는 허용하지 않으며, 기존 프로젝트의 fail-fast 정책과 일관된다.

### Key Entities

- **타겟 플랫폼 프로필**: 각 배포 대상 시스템의 하드웨어 사양(CPU, RAM, GPU, OS)과 CPU 기능 제약 조건을 정의하는 개체
- **CPU 기능 맵**: 호스트 CPU에서 감지된 명령어 세트 지원 여부를 키-값 쌍으로 표현하는 데이터 구조
- **빌드 플래그 세트**: CPU 기능 맵에 기반하여 결정된 CMake 빌드 옵션의 집합

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: i7 930 시스템에서 빌드 스크립트 실행 시 100% 성공률로 llama.cpp가 빌드되고 실행된다.
- **SC-002**: 기존 최신 CPU 환경에서의 빌드 성능이 CPU 감지 로직 도입 전 대비 동등하다 (성능 저하 없음).
- **SC-003**: 빌드 로그에서 CPU 감지 결과와 적용된 플래그를 30초 이내에 확인할 수 있다.
- **SC-004**: 새로운 타겟 플랫폼 추가 시 프로필 등록부터 정상 빌드까지의 전체 과정이 10분 이내에 완료된다.
- **SC-005**: CPU 감지 실패 시에도 빌드가 중단되지 않고 안전한 폴백 옵션으로 정상 완료된다.

## Assumptions

- i7 930은 SSE4.2까지만 지원하며, AVX/AVX2/F16C/FMA를 지원하지 않는다 (Intel Nehalem 마이크로아키텍처의 알려진 제약).
- 빌드는 타겟 머신에서 직접 수행된다 (크로스 컴파일은 본 기능의 범위 밖).
- GTX 1070은 CUDA compute capability 6.1을 지원하며, 프로젝트에서 사용하는 CUDA 툴킷 버전이 이를 지원한다.
- CUDA 빌드는 fat binary가 아닌 호스트 GPU의 단일 아키텍처만 타겟하며, 빌드 머신과 타겟 머신이 동일하다는 전제와 일관된다.
- `/proc/cpuinfo` 파일이 리눅스 환경에서 CPU 기능 정보를 제공하는 표준 인터페이스로 활용 가능하다.
- 기존 개발 환경의 CPU는 AVX2, FMA 등 최신 명령어 세트를 지원한다.
- llama.cpp의 CMake 빌드 시스템은 `GGML_AVX`, `GGML_AVX2`, `GGML_F16C`, `GGML_FMA` 등의 플래그를 통해 개별 명령어 세트의 활성화/비활성화를 제어할 수 있다.
- Ubuntu Server 24.04 LTS는 빌드에 필요한 기본 개발 도구(gcc, cmake, make 등)를 패키지 관리자를 통해 설치할 수 있다.
- GTX 1070의 VRAM 8GB 제약 환경에서 구동할 모델 선택은 `scripts/benchmark_quality.py` 벤치마크 평가 보고서를 통해 수행하며, 선택된 모델 설정은 기존 `config/` 설정 파일(`model_catalog.json`, `server_config.json` 등)을 통해 관리된다.

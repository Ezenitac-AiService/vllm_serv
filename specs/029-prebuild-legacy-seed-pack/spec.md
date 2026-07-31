# Feature Specification: 구형 i7-930 플랫폼 전용 사전 컴파일 라이브러리 시드 팩(Seed Pack) 번들링 및 고속 구축 명세 (029-prebuild-legacy-seed-pack)

**Feature Branch**: `029-prebuild-legacy-seed-pack`

**Created**: 2026-07-30

**Status**: Draft

**Input**: User description: "시드 팩 생성 스크립트로 핵심 파일들로 마이그레이션 하는데, 이때 i7 930용 라이브러리 파일을 미리 빌드해서 포함시켜야 할것 같아. i7 930에서 빌드가 오래 걸려, 나머지 두 플렛폼에서는 감당할만한 빌드 속도야"

## Clarifications

### Session 2026-07-30

- Q: setup.sh 사전 빌드 라이브러리 파이프라인 적용 방식 → A: Option A - 시드 팩 내 번들링된 사전 컴파일 휠(`.whl`) 아티팩트를 `uv pip install`로 설치하여 C++ 소스 재컴파일 없이 가상환경(`.venv`)에 고속 주입.
- Q: i7-930 사전 빌드 휠의 격리 및 교차 컴파일 방식 → A: Option B - 동일 Ubuntu 24.04 OS 환경 전제 하에, 호스트 uv 환경에서 `CMAKE_ARGS="-DGGML_CUDA=ON -DGGML_AVX=OFF -DGGML_AVX2=OFF -DGGML_F16C=OFF -DGGML_FMA=OFF"` 및 `CFLAGS="-march=x86-64"` 플래그를 명시 주입하여 호스트 CPU 벡터 명령어 누출(Illegal Instruction)을 차단하고 휠(`.whl`)을 사전 빌드/번들링.
- Q: 시드 팩 기반 구축 시 사전 빌드 휠 적용 대상 범위 → A: 오직 구형 i7-930 (Platform C: `legacy-i7-930`) 타겟 머신 감지 시에만 사전 빌드 휠을 복원/설치하며, Platform A/B (AVX2 탑재 고성능 머신) 구축 시에는 오버헤드가 없으므로 대상 장비 전용 최적화 소스 컴파일 파이프라인을 그대로 유지.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 구형 i7-930 장비 시드 팩 기반 C++ 컴파일 생략 및 Instant 구축 (Priority: P1) 🎯 MVP

시스템 엔지니어 및 운영자가 구형 i7-930 머신(Platform C: Core i7 930 + GTX 1070)에서 `scripts/setup.sh`를 실행할 때, 긴 시간이 소요되는 C++ 라이브러리(`llama-cpp-python` / `libllama`) 소스 컴파일을 거치지 않고 시드 팩에 사전 빌드/번들링된 라이브러리 바이너리를 자동 복원하여 **수분 이내(3분 이내)**에 서버 구축을 완료합니다.

**Why this priority**: i7-930 CPU의 낮은 단일 코어 성능으로 인해 온디맨드 소스 컴파일 시 15~30분 이상 소요되는 병목 현상을 제거하고 구축 시간을 90% 이상 단축하기 위함입니다.

**Independent Test**: i7-930 프로필 감지 환경에서 `scripts/setup.sh` 실행 시 소스 재컴파일 과정(`uv pip install --no-binary ...`) 없이 사전 빌드 패키지가 즉시 로드되고 GPU 가속 테스트가 통과하는지 검증합니다.

**Acceptance Scenarios**:

1. **Given** i7-930 하드웨어 환경(AVX/AVX2 미지원, CUDA 활성)에서, **When** `scripts/setup.sh` 파이프라인을 실행하면, **Then** C++ 소스 재컴파일을 건너뛰고 시드 팩 내 사전 빌드된 `legacy-i7-930` 바이너리가 동기화되어 즉시 서빙 준비 상태가 되어야 한다.
2. **Given** `scripts/make_seed_pack.sh` 스크립트 실행 시, **When** 시드 팩 아카이브를 생성하면, **Then** `legacy-i7-930` 전용 CMAKE 옵션(`-DGGML_CUDA=ON -DGGML_AVX=OFF -DGGML_AVX2=OFF`)이 적용된 사전 컴파일 바이너리/휠 파일이 시드 팩 디렉터리에 자동으로 패키징되어야 한다.

---

### User Story 2 - 현대적 CPU 플랫폼(Platform A/B)과의 빌드/복원 호환성 유지 (Priority: P2)

고성능 개발용 머신(Platform A: Xeon E3-1231v3, Platform B: Core i7-4770)에서는 시드 팩 생성 스크립트 실행 시 쾌적한 빌드 속도로 시드 팩을 즉시 생성하고, 설치 시 머신 프로필을 판별하여 해당 장비에 최적화된 빌드/복원 경로를 적용합니다.

**Why this priority**: 구형 플랫폼 지원 추가로 인해 현대적 하드웨어의 AVX2 최적화 성능 및 기존 원스톱 빌드 파이프라인이 저해되지 않도록 보장하기 위함입니다.

**Independent Test**: Platform A/B 환경에서 시드 팩 생성 및 `setup.sh` 실행 시 기존 AVX2 최적화 컴파일 옵션이 정상 동작함을 pytest 및 build test로 검증합니다.

**Acceptance Scenarios**:

1. **Given** Platform A 또는 B 프로필 환경에서, **When** `scripts/setup.sh`를 실행하면, **Then** i7-930 전용 미지원 바이너리가 아닌 해당 플랫폼 맞춤 CMAKE 옵션(AVX/AVX2 활성)으로 정상 컴파일/복원되어야 한다.

---

### Edge Cases

- 시드 팩 아카이브 내 i7-930 사전 빌드 라이브러리가 유실되거나 손상된 경우 시스템은 파손되지 않고 경고 후 기존 소스 컴파일 방식으로 자동 Fallback되는가?
- i7-930 머신에서 사전 빌드된 바이너리 로드 후 `llama_supports_gpu_offload()` GPU 가속 지원 검증이 정상 통과하는가?

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `scripts/make_seed_pack.sh` 스크립트에 i7-930 전용 사전 컴파일 라이브러리(`legacy-i7-930` 전용 아티팩트) 자동 번들링 로직 구현 완료
- **DoD-002**: `scripts/setup.sh` 실행 시 i7-930 타겟 플랫폼 감지 시 소스 재컴파일을 건너뛰고 사전 빌드 시드 팩 바이너리를 즉시 추출/설치하는 파이프라인 적용 완료
- **DoD-003**: 사전 빌드 라이브러리 미존재 시 소스 컴파일로 자동 Fallback하는 안전 장치 검증 완료
- **DoD-004**: i7-930 사전 빌드 포함 시드 팩 생성 및 복원 기능에 대한 통합/단위 pytest 테스트 100% 통과

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 (i7-930 사전 빌드 휠 아티팩트 번들링)**: `scripts/make_seed_pack.sh` 실행 시 `legacy-i7-930` 프로필 전용 C++ 컴파일 휠(`.whl`) 아티팩트를 명시적 컴파일 인자(`CMAKE_ARGS="-DGGML_CUDA=ON -DGGML_AVX=OFF -DGGML_AVX2=OFF -DGGML_F16C=OFF -DGGML_FMA=OFF"` 및 `CFLAGS="-march=x86-64"`)로 사전 빌드/번들링하여 시드 팩 아카이브에 포함해야 한다.
- **FR-002 (Platform C 타겟 감지 및 uv pip install Fast-Track 복원)**: `scripts/setup.sh` 파이프라인 실행 시 감지된 타겟 프로필이 `legacy-i7-930`인 경우, 시간 소모가 큰 C++ 소스 re-compile 과정을 건너뛰고 시드 팩 내 번들링된 사전 빌드 휠(`.whl`) 아티팩트를 `uv pip install`로 가상환경(`.venv`)에 고속 주입하여 즉시 설치를 완료해야 한다.
- **FR-003 (Platform A/B 컴파일 경로 유지)**: Platform A (`pascal-avx2-gtx1080ti`) 및 Platform B (`dev-rtx3060`) 장비에서는 기존과 동일하게 AVX/AVX2 동적 컴파일 또는 해당 플랫폼에 맞는 최적화 복원 경로를 수행해야 한다.
- **FR-004 (사전 빌드 유실 시 Fallback)**: 시드 팩 내 i7-930 사전 빌드 라이브러리가 미존재하거나 추출 실패 시, `setup.sh`는 경고 메시지를 출력하고 기존 소스 컴파일 파이프라인으로 안전하게 Fallback되어야 한다.
- **FR-005 (GPU 가속 검증 보장)**: i7-930 사전 빌드 라이브러리 설치 후 `llama_supports_gpu_offload()` 호출을 통해 GTX 1070 GPU 가속 오프로드가 정상 작동하는지 자동 검증해야 한다.

### Key Entities

- **SeedPackArchive**: 시드 패키지 압축 파일(`seed_pack.tar.gz`). 모델 카탈로그, 설정 파일 및 i7-930 사전 빌드 C++ 라이브러리 바이너리를 포함.
- **LegacyPrebuiltLibrary**: i7-930 전용으로 컴파일된 `llama-cpp-python` / `libllama` 바이너리 패키지 아티팩트.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 구형 i7-930 머신에서 `scripts/setup.sh` 전체 실행 시간 기존 15~30분에서 **3분 이내**로 90% 이상 단축
- **SC-002**: 시드 팩 생성 스크립트(`scripts/make_seed_pack.sh`)의 성공적인 실행 및 i7-930 전용 사전 빌드 아티팩트 포함 여부 100% 검증
- **SC-003**: i7-930 사전 빌드 라이브러리 적용 후 전체 pytest 테스트 수트 100% 통과 및 CUDA GPU 가속 검증 통과

## Assumptions

- i7-930 머신은 Intel Core i7 930 CPU와 NVIDIA GTX 1070 GPU를 탑재하고 있으며, CPU 명령어 세트는 AVX/AVX2를 지원하지 않음.
- 시드 팩을 생성하는 머신(Platform A/B 등)은 i7-930 전용 CMAKE 인자(`-DGGML_CUDA=ON -DGGML_AVX=OFF -DGGML_AVX2=OFF`)를 지정하여 구형 호환 바이너리를 미리 크로스/사전 컴파일할 수 있음.

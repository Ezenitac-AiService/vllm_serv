# Feature Specification: Tier 4 uv 휠 캐시 실측 검증 및 불일치 시 조건부 --no-cache-dir C++ 소스 재컴파일 파이프라인 (057-fix-uv-no-cache-source-compilation)

**Feature Branch**: `057-fix-uv-no-cache-source-compilation`

**Created**: 2026-07-31

**Status**: Draft

**Input**: Migration log analysis from `/home/dev/storage/vllm_serv/log.txt` (Lines 181-267)

## Clarifications

### Session 2026-07-31
- Q: Tier 4 C++ 재컴파일 단계에서의 uv 캐시 휠 검증 및 조건부 재컴파일 방식 → A: Option A (캐시 휠 설치 후 3중 가속 검증 수행 → 성공 시 기존 휠 즉시 재사용, 실패 시에만 캐시 무효화 `--no-cache-dir` 및 C++ 소스 재컴파일)
- Q: Seed Pack 아카이브 내 사전 빌드 휠 수록 범위 및 플랫폼별 운영 의도 → A: Seed Pack(`vllm_serv_seed.tar.gz`)에는 레거시 서비스 플랫폼 전용 바이너리(`wheels/legacy_i7_930/*.whl`)만 수록함. 개발 머신은 현지 개발용 휠을 별도 유지하고, 학습용 타겟은 교육 목적의 C++ 컴파일 시연을 유도하며, 레거시 서비스 플랫폼은 0.05s Fast-Track 고속 이관을 달성함.
- Q: 3개 플랫폼 GPU 세대 검출 및 동적 CMake/CUDA 플래그 바인딩 방식 → A: `setup.sh` 구동 시 `src.core.cpu_detector`가 `nvidia-smi --query-gpu=compute_cap`을 통해 GPU 세대/Compute Capability(RTX 3060 `sm_86`, GTX 1080 Ti/1070 `sm_61` 등)와 CPU SIMD를 100% 자동 정밀 검출하여 `DETECTED_CMAKE_ARGS`(`-DCMAKE_CUDA_ARCHITECTURES=86` 또는 `61`)를 동적 주입함.
- Q: GTX 1080 Ti(GP102)와 GTX 1070(GP104) 하드웨어 및 빌드 호환성 리서치 결과 → A: 리서치 결과 두 카드는 CUDA 아키텍처 버전(Compute Capability 6.1, `sm_61`)은 동일하지만 실시간 GPU 칩셋(1080 Ti=GP102 11GB VRAM/3584 코어 vs 1070=GP104 8GB VRAM/1920 코어)이 다름. 결정적으로 플랫폼 프로필상 1080 Ti 머신(`pascal-avx2-gtx1080ti`)은 Haswell CPU(AVX2 지원)를 사용하고, 1070 레거시 머신(`legacy-i7-930-gtx1070`)은 Nehalem CPU(AVX 미지원)를 사용하므로, GPU 플래그(`sm_61`)가 같아도 **호스트 CPU SIMD 플래그(`-DGGML_AVX=OFF`) 차이** 때문에 1080 Ti 머신 캐시 휠을 1070 머신에서 실행하면 `Illegal Instruction` 에러가 발생함이 검증됨.
- Q: 타깃 머신 Seed Pack 압축 해제 및 복원 시 기존 유효 바이너리 보존 원칙 → A: 복원/셋업(`setup.sh`) 구동 시 해당 머신(개발/서비스/학습)에 이미 존재하고 실측 검증(`llama_supports_gpu_offload()`)을 통과한 정상 바이너리가 있는 경우, Seed Pack 압축 해제 시 기존 휠/바이너리를 덮어쓰지(Overwrite) 않고 최우선적으로 보존 재사용함.
- Q: Seed Pack 압축 해제 덮어쓰기 방지 헬퍼 스크립트 제공 여부 → A: `scripts/unpack_seed.sh` 스크립트를 신규 제공하여 복잡한 수동 `tar` 옵션 입력 없이 기존 검증 통과 바이너리 보존(`--skip-old-files` / `-k`) 및 압축 해제를 원클릭 자동화함.
- Q: unpack_seed.sh 및 vllm_serv_seed.tar.gz 파일의 작동 디렉터리 위치 → A: `unpack_seed.sh` 스크립트 및 `vllm_serv_seed.tar.gz` 아카이브 파일은 프로젝트 루트 디렉터리(`vllm_serv/`)에 배치하여 구동하며, 실행 시 `vllm_serv/` 루트 하위의 기존 유효 바이너리를 덮어쓰지 않고 최우선적으로 보존 재사용함.
- Q: 공격적 비판론자 심층 보고서 기반 개선사항 수용 및 스펙 반영 조치 → A: 1) nvidia-smi 실행 실패 시 platform_profiles.json 호스트 프로필 기반 기본값 Fallback 안전망을 FR-001에 명시함. 2) unpack_seed.sh 실행 시 인자 유연성($1 또는 vllm_serv_seed.tar.gz) 및 퍼미션 보존(-p / --same-permissions) 옵션을 FR-005에 수록함. 3) Tier 4 C++ 재컴파일 중단 시 가상환경 오염 방지 원자적 cleanup 방어망을 FR-001에 수록함.

---

## Technical Context & Scope Analysis (기술적 맥락 및 로그 분석)

서비스 플랫폼 타겟 서버(Intel i7-930 + GTX 1070)에 이관 후 `./setup.sh`를 실행한 3차 실측 로그(`log.txt` 181~267행) 분석 결과, 다음과 같은 **uv 패키지 매니저 휠 캐시 재사용 결함 및 Seed Pack 아카이브 사전 휠 검증 결함**이 규명되었습니다:

1. **uv 휠 캐시(`~/.cache/uv`) 재사용에 의한 C++ 소스 컴파일 우회 결함 (Root Cause)**:
   - `scripts/setup.sh` 313행: 사전 휠 검증 실패 후 Tier 4로 정상 전이되어 `CMAKE_ARGS="$DETECTED_CMAKE_ARGS" uv pip install "llama-cpp-python[server]" --no-binary llama-cpp-python` 명령이 구동되었습니다 (255행).
   - 그러나 `uv` 패키지 매니저가 캐시 디렉터리(`~/.cache/uv/wheels`)에 사전에 존재하던 `llama-cpp-python==0.3.34` 휠 패키지를 감지하고, 실제 C++ 소스 재컴파일 과정(수십 초~수 분 소요)을 스킵한 채 단 **5ms 만에 캐시 휠로 즉시 재설치**하는 현상이 발생했습니다 (258행 `Installed 1 package in 5ms`).
   - 이 캐시 휠은 CUDA 가속이 적용되지 않은 이전 패키지였기 때문에, 동적 `CMAKE_ARGS`(`-DGGML_CUDA=ON -DGGML_AVX=OFF...`)가 전달되었음에도 소스코드가 재컴파일되지 못하고 CPU 전용 패키지가 가상환경에 다시 주입되었습니다.
   - 이로 인해 264행 `AssertionError: GPU offload not supported` 예외가 발생하며 `setup.sh`가 즉시 중단되었습니다.

2. **조건부 휠 캐시 검증 및 무효화 재컴파일 해결 방안 (Option A)**:
   - 무조건 캐시를 무효화하여 불필요하게 C++ 소스를 재컴파일하는 낭비를 막기 위해, Tier 4 진입 시 다음과 같이 **2단계 조건부 휠 캐시 검증 파이프라인**을 구축합니다:
     1. **1단계 (캐시 휠 정상 동작 실측 검증)**: 먼저 `uv pip install "llama-cpp-python[server]" --no-binary llama-cpp-python`을 통해 설치된 휠이 `llama_supports_gpu_offload() == True`로 정상 동작하는지 실측 검증합니다.
     2. **2단계 (성공 시 즉시 재사용)**: 1단계 검증 통과 시 C++ 소스 재컴파일을 스킵하고 고속으로 설치를 완성합니다.
     3. **3단계 (실패 시 조건부 캐시 무효화 및 재컴파일)**: 1단계 검증 실패(CPU 전용 휠 감지) 시 `⚠️ [UV CACHE INVALID] uv 캐시 휠이 CPU 전용으로 감지되었습니다. 캐시 무효화(--no-cache-dir) 및 C++ 소스 재컴파일을 수행합니다...` 로그를 출력하고, `uv pip uninstall llama-cpp-python` 후 `CMAKE_ARGS="$DETECTED_CMAKE_ARGS" uv pip install --no-cache-dir "llama-cpp-python[server]" --no-binary llama-cpp-python`을 실행하여 휠 캐시를 무효화하고 실제 C++ 소스코드를 동적 컴파일합니다.

3. **make_seed_pack.sh 휠 생성 시 타겟 서비스 플랫폼 명시 및 Post-Build 3중 검증 보강**:
   - `scripts/make_seed_pack.sh`에서 `uv run pip wheel --no-cache-dir ...` 구문을 강제 부여하여 호스트 개발 머신의 캐시 오염을 막고, 타겟 서비스 플랫폼(`legacy-i7-930-gtx1070`) 플래그(`CFLAGS=-march=x86-64`, `-DGGML_AVX=OFF`, `-DCMAKE_CUDA_ARCHITECTURES=61`)에 100% 맞춘 사전 휠(`wheels/legacy_i7_930/*.whl`)을 순수 동적 빌드합니다.
   - 빌드 직후 `scripts/verify_wheel_binary.py`로 생성된 바이너리를 즉시 검증(AVX=0, CUDA=1)하여, 검증 실패 시 생성된 결함 휠을 `rm -f`로 삭제함으로써 결함 있는 CPU 전용 휠이 `vllm_serv_seed.tar.gz` 아카이브에 포함되지 않도록 원천 차단합니다.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Tier 4 uv 휠 캐시 실측 검증 및 조건부 `--no-cache-dir` 소스 재컴파일 (Priority: P1) 🎯 MVP

사용자나 DevOps 관리자가 이관 타겟 서버에서 `./setup.sh`를 실행할 때, Tier 4 파이프라인에서 uv 캐시 휠의 정상 동작 여부를 실측 검증하여, 정상 CUDA 휠이면 불필요한 빌드 없이 고속 재사용하고, CPU 전용 휠로 확인될 경우에만 `--no-cache-dir` 옵션으로 캐시를 무효화한 뒤 C++ 소스 재컴파일을 수행하여 100% CUDA 가속 패키지를 안전하게 설치합니다.

- **조건부 캐시 무효화 및 C++ 재컴파일**: `uv pip install --no-cache-dir ...` 조건부 적용.

---

### User Story 2 - 이관 타겟 머신에서의 100% CUDA 가속 완결 및 status_server.sh 정상 검증 (Priority: P1) 🎯 MVP

`./setup.sh` 완료 후 `./start_server.sh` 및 `./status_server.sh` 조율 시 `llama-cpp-python GPU: ✓ CUDA 가속 활성` 리포트가 출력되고, `llama-server` 백엔드 프로세스 PID 및 GPU VRAM 오프로드가 정상 확인됩니다.

---

### User Story 3 - make_seed_pack.sh 타겟 서비스 플랫폼 맞춤 빌드 & Post-Build 검증 및 결함 휠 패키징 원천 차단 (Priority: P1) 🎯 MVP

개발 머신에서 `make_seed_pack.sh`를 실행하여 아카이브를 패키징할 때, 타겟 서비스 플랫폼(`legacy-i7-930-gtx1070`) 사양에 100% 맞춰 `--no-cache-dir` 로 사전 빌드 휠(`wheels/legacy_i7_930/*.whl`)을 생성하고, 실제 CUDA 가속 라이브러리를 포함하는지 `scripts/verify_wheel_binary.py`로 Post-Build 검증을 수행하여, 결함 있는 휠은 즉시 자동 삭제(Clean)하고 유효한 휠만 아카이브에 패키징합니다.

---

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `scripts/setup.sh` 내 Tier 4 2단계 조건부 uv 휠 캐시 검증 및 실패 시 `--no-cache-dir` 소스 재컴파일 파이프라인 적용 완료.
- **DoD-002**: `tests/unit/test_seed_pack.py`에 조건부 `--no-cache-dir` 및 캐시 무효화 로직 단정 검증 테스트 수록.
- **DoD-003**: `./status_server.sh` 실행 시 `llama-cpp-python GPU: ✓ CUDA 가속 활성` 및 PID 상주 실측 보장.
- **DoD-004**: `scripts/make_seed_pack.sh` 및 `scripts/unpack_seed.sh` 스크립트 작성 (안전 해제, 기존 휠 보존, Post-Build 검증 포함).
- **DoD-005**: 단위 및 회귀 테스트 수트 pass.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `scripts/setup.sh` 내 Tier 4 동적 빌드 구문에서 `src.core.cpu_detector`가 `nvidia-smi`를 통해 해당 플랫폼의 GPU 세대 및 Compute Capability(RTX 3060 `sm_86`, GTX 1080 Ti/1070 `sm_61` 등)와 CPU SIMD를 자동 검출(`nvidia-smi` 구동 실패 시 `platform_profiles.json` 기본 프로필로 안전 Fallback)하여 `-DCMAKE_CUDA_ARCHITECTURES=86` 또는 `61` 인자를 생성해야 하고, 먼저 uv 캐시 휠 설치 후 3중 가속 검증(`llama_supports_gpu_offload()`)을 수행하고, 검증 성공 시 기존 캐시 휠을 고속 재사용하며, 검증 실패(CPU 전용 감지) 시에만 `uv pip uninstall` 후 `CMAKE_ARGS="$DETECTED_CMAKE_ARGS" uv pip install --no-cache-dir "llama-cpp-python[server]" --no-binary llama-cpp-python` 옵션으로 휠 캐시를 무효화하고 C++ 소스 재컴파일을 강제해야 한다. C++ 재컴파일 도중 중단 또는 실패 시에는 `uv pip uninstall`을 호출하여 오염된 결함 상태 바이너리가 잔류하지 않도록 원자적(Atomic) cleanup을 수행해야 한다.
- **FR-002**: 헌법 v1.6.0에 따라 Tier 4 조건부 휠 캐시 검증 및 실패 시 `--no-cache-dir` 수록 여부를 검증하는 단위 테스트(`tests/unit/test_seed_pack.py` 내 추가)를 작성하고 Green 통과를 보장해야 한다.
- **FR-003**: `scripts/make_seed_pack.sh`에서 `--build-legacy` 구문으로 사전 휠 패키징 시, 기존 `wheels/legacy_i7_930/*.whl`이 이미 존재하고 `scripts/verify_wheel_binary.py` 검증(AVX=0, CUDA=1)을 통과하면 **기존 사전 휠을 즉시 고속 재사용(재컴파일 스킵)**해야 한다. 기존 휠이 없거나 검증에 실패한 경우에만 개발 머신의 오염된 캐시 영향을 무효화하기 위해 `uv run pip wheel --no-cache-dir` 구문과 함께 `CFLAGS=-march=x86-64` 및 `CMAKE_ARGS="-DGGML_CUDA=ON -DGGML_AVX=OFF -DGGML_AVX2=OFF -DGGML_F16C=OFF -DGGML_FMA=OFF -DGGML_NATIVE=OFF -DCMAKE_CUDA_ARCHITECTURES=61"` 인자를 부여하여 타겟 서비스 플랫폼(`legacy-i7-930-gtx1070`) 전용 휠을 신규 생성하고, 생성 직후 다시 3중 검증을 수행하여 검증 실패 시 `rm -f`로 결함 휠을 자동 삭제해야 한다.
- **FR-004**: `scripts/make_seed_pack.sh`는 아카이브 경량화 및 서비스 마이그레이션 속도 최적화를 위하여 Seed Pack(`vllm_serv_seed.tar.gz`) 내에 레거시 서비스 플랫폼 전용 사전 빌드 휠(`wheels/legacy_i7_930/*.whl`, AVX=0)만 수록해야 한다. (개발 머신은 현지 스펙 휠을 가상환경에서 유지하고, 학습용 고성능 플랫폼은 교육용 C++ 컴파일 시연을 수행함).
- **FR-005**: `scripts/unpack_seed.sh` 스크립트(및 `vllm_serv/` 프로젝트 루트 단축 실행 `./unpack_seed.sh`)를 신규 작성하여 프로젝트 루트(`vllm_serv/`)에서 지정된 아카이브 파일(기본값 `vllm_serv_seed.tar.gz`, 인자 유연 지정 가능) 압축 해제 시 수동 옵션 입력 없이 기존 검증(`llama_supports_gpu_offload()`)을 통과한 유효 바이너리를 자동 보존(`-k` / `--skip-old-files`) 및 퍼미션 보존(`-p` / `--same-permissions`)하고 덮어쓰기(Overwrite)를 원천 방지해야 한다.


---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 이관 타겟 레거시 서버에서 정상 CUDA 캐시 휠 존재 시 고속 완료, 결함 휠 존재 시 캐시 무효화 후 100% C++ 소스 재컴파일 및 setup.sh 완결 성공률 **100%**.
- **SC-002**: `./status_server.sh` 실행 시 `llama-cpp-python GPU: ✓ CUDA 가속 활성` 확인율 **100%**.
- **SC-003**: `make_seed_pack.sh` 실행 시 Post-Build 검증을 통과한 유효한 CUDA 휠만 Seed Pack 아카이브에 포함률 **100%**.
- **SC-004**: 관련 단위 및 회귀 테스트 수트 100% Pass.

---

## Assumptions

- `uv pip install --no-cache-dir` 옵션은 `uv`가 디스크 휠 캐시(`~/.cache/uv`)를 읽거나 쓰는 과정을 생략하도록 만듭니다.

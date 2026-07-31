# Feature Specification: 레거시 사전 휠 Post-Build AVX 검증도구 `objdump -d` 어셈블리 디스어셈블러 정밀 스캐너 전환 및 빌드 플래그 완결 명세

**Feature ID**: `060-fix-wheel-avx-objdump-scanner`  
**Created**: 2026-07-31  
**Status**: Draft / Analysis Complete  

---

## 1. Context & Root Cause Analysis (원인 분석)

### 1.1 현상
사용자가 `./scripts/make_seed_pack.sh --build-legacy` 실행 시 Post-Build 실측 검증 단계에서 다음과 같이 휠 검증에 실패하고 결함 휠로 오인하여 자동 삭제(`rm -f wheels/legacy_i7_930/*.whl`)되는 현상이 재발함:
```text
[SEED-PACK INFO] Post-Build 3중 실측 검증 수행 중 (wheels/legacy_i7_930/llama_cpp_python-0.3.34-py3-none-linux_x86_64.whl)...
❌ Wheel INVALID: Found issues across .so files (cuda_enabled=True, total_avx=79530, avx_clean_required=True)
  - lib/libggml-base.so.0.16.0: 1246 AVX instructions
  - lib/libmtmd.so.0: 1891 AVX instructions
  - lib/libggml-cpu.so.0.16.0: 1424 AVX instructions
  - lib/libllama-common.so.0.0.1: 6724 AVX instructions
  - lib/libllama.so.0: 5269 AVX instructions
[SEED-PACK ERROR] ❌ [POST-BUILD FAIL] 생성된 i7-930 휠 검증 실패 (AVX 유입 또는 CUDA 미지원). 결함 휠을 자동 삭제(rm -f)합니다.
```

### 1.2 근본 원인 (Root Cause)
1. **바이트 스캐너의 허위 감지 (False Positive)**:
   - `scripts/verify_wheel_binary.py`의 `scan_so_with_python_bytes()`는 단순 16진수 바이트 `0xC4` 및 `0xC5`를 VEX 프리픽스(AVX 명령어 시작)로 판단함.
   - 그러나 x86_64 가변 길이 어셈블리 명령어 스트림에서는 비-AVX 일반 명령어(e.g. `mov`, `add`, `cmp`, `les`)의 **ModRM 바이트, Displacement 상대주소 오프셋 바이트, Immediate 상숫값 바이트**에 `0xC4` 및 `0xC5` 16진수 데이터 값이 자연스럽게 다수 존재함.
   - 이로 인해 C/C++ 컴파일러가 AVX 명령어를 단 1개도 사용하지 않고 strict SSE4.2로 정상 컴파일한 `libllama.so` 및 `libggml-cpu.so` 바이너리에 대해서도 `total_avx = 79,530`건의 허위 AVX 명령어가 존재하는 것으로 잘못 판정함.
2. **`make_seed_pack.sh`의 빌드 및 검증 연동 결함**:
   - `verify_wheel_binary.py`가 허위 감지로 인해 Exit Code 2(SIMD mismatch)를 리턴하면, `make_seed_pack.sh`가 올바르게 생성된 휠 패키지를 `rm -f wheels/legacy_i7_930/*.whl`로 자동 삭제하여 아카이브 수록에 실패함.
   - `scikit-build-core` 백엔드에 전달하는 CMake 플래그에 `-DGGML_AVX512=OFF -DGGML_BMI2=OFF -DGGML_FMA=OFF -DCMAKE_C_FLAGS=-march=x86-64 -DCMAKE_CXX_FLAGS=-march=x86-64` 등 C/C++ 타겟 아키텍처 명시적 제한이 완전하게 통합되어야 함.

---

## 2. User Stories & Acceptance Scenarios

### User Story 1 (P1 - MVP): `objdump -d` 기반 기계어 디스어셈블러 스캐너 전환
As a platform engineer building migration seed packs for legacy Nehalem i7-930 non-AVX CPUs,  
I want `verify_wheel_binary.py` to inspect shared libraries (.so) using `objdump -d` instruction disassembly,  
So that false-positive byte matches (`0xC4`/`0xC5`) inside non-AVX machine code are 100% eliminated and valid compiled wheels are correctly verified as `✓ [POST-BUILD SUCCESS]`.

- **Acceptance Scenario 1.1**:
  - Given valid compiled shared libraries (`libggml-cpu.so`, `libllama.so`) built with `-march=x86-64 -DGGML_AVX=OFF`,
  - When `verify_wheel_binary.py` runs,
  - Then `objdump -d` disassembly checks instruction mnemonics matching `^\s*[0-9a-f]+:\s+(v[a-z0-9]+)\b` (excluding `verr`, `verw`, `vmread`, `vmwrite`, `vmmcall`),
  - And returns `total_avx = 0`, `avx_clean = True`, and Exit Code `0`.

- **Acceptance Scenario 1.2**:
  - Given an environment where `objdump` is not installed,
  - When `verify_wheel_binary.py` falls back to pure-Python scanner,
  - Then it inspects ELF section headers for executable code (`SHF_EXECINSTR`) AND validates 3-byte VEX map select bits (`(byte1 & 0x1F) in (1, 2, 3)`), returning zero false positives on standard x86_64 code.

---

### User Story 2 (P2): `make_seed_pack.sh` C/C++ SIMD 차단 옵션 완결 보강
As a build automation engineer,  
I want `make_seed_pack.sh` to explicitly declare all AVX/AVX2/AVX512/FMA/BMI2 disabling flags and C/CXX flags in `SKBUILD_CMAKE_ARGS` and `CMAKE_ARGS`,  
So that `scikit-build-core` strictly compiles `llama-cpp-python` C/C++ binaries for the `-march=x86-64` SSE4.2 baseline.

- **Acceptance Scenario 2.1**:
  - Given `./scripts/make_seed_pack.sh --build-legacy` is executed on a modern dev machine with AVX2/AVX512 support,
  - When `uv run pip wheel` compiles `llama-cpp-python`,
  - Then `SKBUILD_CMAKE_ARGS` and `CMAKE_ARGS` contain `-DGGML_CUDA=ON -DGGML_NATIVE=OFF -DGGML_AVX=OFF -DGGML_AVX2=OFF -DGGML_AVX512=OFF -DGGML_AVX512_VBMI=OFF -DGGML_AVX512_VNNI=OFF -DGGML_AVX512_BF16=OFF -DGGML_AVX_VNNI=OFF -DGGML_F16C=OFF -DGGML_FMA=OFF -DGGML_BMI2=OFF -DCMAKE_CUDA_ARCHITECTURES=61 -DCMAKE_C_FLAGS=-march=x86-64 -DCMAKE_CXX_FLAGS=-march=x86-64`.

---

## 3. Functional Requirements (기능 요구사항)

- **FR-001**: `scripts/verify_wheel_binary.py`의 `scan_so_with_python_bytes()` 함수는 우선적으로 `objdump -d --no-show-raw-insn <so_file>` 명령을 수행하여 어셈블리 기계어 디스어셈블리 텍스트를 추출해야 함.
- **FR-002**: 디스어셈블리 분석 시 정규표현식 `^\s*[0-9a-f]+:\s+(v[a-z0-9]+)\b` 패턴에 매칭되는 니모닉 중 특수 시스템 명령어(`verr`, `verw`, `vmread`, `vmwrite`, `vmmcall`, `vptr`)를 제외한 실제 AVX/VEX/EVEX 벡터 니모닉(`vmov...`, `vadd...`, `vpxor...` 등)만을 AVX 명령어 카운트로 산출해야 함.
- **FR-003**: `objdump` 부재 시 순수 Python 폴백 스캐너는 ELF 헤더 파싱을 통해 `SHF_EXECINSTR` 섹션만 스캔하고, 3바이트 VEX 프리픽스 판단 시 Map Select 필드(`(byte1 & 0x1F) in (1, 2, 3)`) 검증을 필수 수행해야 함.
- **FR-004**: `scripts/make_seed_pack.sh`의 사전 컴파일 명령어는 `SKBUILD_CMAKE_ARGS` 및 `CMAKE_ARGS`에 모든 AVX 변종 차단 플래그와 `-DCMAKE_C_FLAGS=-march=x86-64 -DCMAKE_CXX_FLAGS=-march=x86-64`를 포함해야 함.
- **FR-005**: Post-Build 검증 통과 시 `wheels/legacy_i7_930/` 디렉터리에 `llama_cpp_python-*.whl` 파일이 보존되어야 하며, 생성된 `dist/vllm_serv_seed.tar.gz` 아카이브 수록 검증을 100% 통과해야 함.

---

## 4. Success Criteria (성공 기준)

- **SC-001**: `./scripts/make_seed_pack.sh --build-legacy` 실행 시 `✓ [POST-BUILD SUCCESS] 생성된 i7-930 휠 검증 통과 (AVX=0, CUDA=1)` 메시지와 함께 Exit Code 0으로 정상 완료됨.
- **SC-002**: 생성된 `dist/vllm_serv_seed.tar.gz` 내부 파일 검증 시 `wheels/legacy_i7_930/llama_cpp_python-*.whl`이 정상 포함됨.
- **SC-003**: `uv run pytest tests/unit/test_seed_pack.py` 실행 시 100% Green Pass를 달성함.

---

## 5. Assumptions & Boundaries (가정 및 범위)

- **Assumptions**:
  - 개발 머신 및 서비스 타겟 머신에는 Linux 표준 `binutils` 패키지의 `objdump` 유틸리티가 기본 설치되어 있음.
  - Python 실행 환경은 `uv` 패키지 매니저로 구성되어 있음.
- **Boundaries**:
  - `libggml-cuda.so` 등 CUDA 디바이스 전용 공유 라이브러리는 CPU AVX 스캔 대상에서 이미 분리되어 있으므로 본 명세의 CPU 호스트 바이너리 스캔 정밀화 범위에 포함됨.

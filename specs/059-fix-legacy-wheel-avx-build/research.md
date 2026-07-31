# Research: make_seed_pack.sh 레거시 사전 휠 Post-Build AVX 실측 검증 로직 및 빌드 플래그 정밀화 (059-fix-legacy-wheel-avx-build)

**Feature Branch**: `059-fix-legacy-wheel-avx-build`  
**Date**: 2026-07-31  
**Spec Link**: [`spec.md`](file:///home/dev/storage/vllm_serv/specs/059-fix-legacy-wheel-avx-build/spec.md)

---

## Technical Decisions & Rationale

### Decision 1: CUDA 디바이스 전용 공유 라이브러리(`libggml-cuda.so`)와 CPU 호스트 공유 라이브러리(`ggml-cpu.so`, `libllama.so` 등)의 바이너리 스캔 분리

- **Decision**: `scripts/verify_wheel_binary.py` 검증 도구의 `verify_wheel()` 및 `scan_so_with_python_bytes()` 함수에서 `.whl` 내 공유 라이브러리 중 `cuda` 포함 바이너리(`ggml-cuda.so`)를 CUDA GPU 가속 활성화(CUDA Enabled=True) 검증용으로 분류하고, CPU 호스트에서 실행되는 공유 라이브러리(`ggml-cpu.so`, `libllama.so`, `libggml-base.so` 등)에 대해서만 AVX VEX 바이트 오코드 무결성(AVX Clean=True, total_avx=0)을 정밀 스캔한다.
- **Rationale**: `libggml-cuda.so`는 NVIDIA GPU 디바이스 커널(NVPTX/SASS 디바이스 바이너리 및 CUDA 가속 테이블)을 포함하여 0xC4/0xC5 바이트 패턴이 바이너리 데이터로 48만 건 이상 정당하게 존재하나, 호스트 CPU의 AVX 직접 명령 실행과 무관하다. 반면 Nehalem i7-930과 같은 구형 호스트 CPU는 AVX 명령어가 없으므로 `ggml-cpu.so` 및 `libllama.so` 등 호스트 실행 파일의 AVX 0건 통과가 필수적이다.
- **Alternatives Considered**:
  - *대안 A*: `.whl` 패키지 내 모든 `.so` 파일에 일괄 AVX 바이트 스캔 수행 (현행 방식) → CUDA 디바이스 커널 데이터 패턴이 AVX 바이트로 오감지(False Positive)되어 정상 휠이 무단 삭제되는 문제 발생.
  - *대안 B*: `verify_wheel_binary.py` 검증 도구에서 AVX 검사를 전면 제외 → Nehalem i7-930 레거시 서버에서 SIGILL(Illegal Instruction) 발생 위험을 사전에 검증할 수 없음.

---

### Decision 2: `make_seed_pack.sh` 빌드 환경 변수에 `SKBUILD_CMAKE_ARGS` 및 `CMAKE_ARGS` 동시 전달

- **Decision**: `scripts/make_seed_pack.sh`의 휠 컴파일 실행 구문에서 `scikit-build-core` 표준 규격 환경 변수인 `SKBUILD_CMAKE_ARGS`와 기존 `CMAKE_ARGS`, `CFLAGS`, `CXXFLAGS`를 동시에 명시한다.
- **Rationale**: `llama-cpp-python`은 `scikit-build-core` 백엔드를 사용하므로 공식 환경 변수인 `SKBUILD_CMAKE_ARGS`를 함께 지정함으로써, PEP 517/518 격리 컴파일 시 CMake 인자(`-DGGML_CUDA=ON -DGGML_AVX=OFF -DGGML_AVX2=OFF -DGGML_F16C=OFF -DGGML_FMA=OFF -DGGML_NATIVE=OFF -DCMAKE_CUDA_ARCHITECTURES=61`)가 100% 전달되도록 전파 보장한다.
- **Alternatives Considered**:
  - *대안 A*: `CMAKE_ARGS`만 단독 사용 → `scikit-build-core` 버전에 따라 CMake 플래그 전달 누락 가능성 존재.

---

### Decision 3: `verify_wheel_binary.py` 투명한 검증 결과 리포팅 및 CLI 리턴 코드 규격

- **Decision**: 검증 결과 리포트 출력 시 `[CPU Host SO Files Checked]`와 `[CUDA Device SO Files Validated]`를 명확히 구분 표시하고, 호스트 라이브러리 AVX 오염 시 Exit Code 2, CUDA 미지원 시 Exit Code 1, 정상 성공 시 Exit Code 0을 리턴하도록 정밀화한다.
- **Rationale**: 개발 머신에서 빌드 및 검증을 구동할 때 스캔 과정과 결과를 명확하게 파악할 수 있으며 CI/CD 및 `make_seed_pack.sh`에서 정확한 예외 핸들링이 가능해진다.

---

## Verification Strategy

1. **단위 테스트 (`tests/unit/test_seed_pack.py`)**:
   - `verify_wheel_binary.py`가 CUDA 디바이스 `.so` 라이브러리와 CPU 호스트 `.so` 라이브러리를 바르게 분리하여 검증하는지 테스트 단정 추가.
   - `make_seed_pack.sh` 내 `SKBUILD_CMAKE_ARGS` 수록 여부 테스트 단정 추가.
2. **실체적 E2E 스크립트 실행 검증**:
   - `./scripts/make_seed_pack.sh --build-legacy` 실행 시 `❌ [POST-BUILD FAIL]` 오검출 없이 `✓ [POST-BUILD SUCCESS]` 100% 통과 실측.

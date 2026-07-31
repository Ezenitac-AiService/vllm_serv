# Technical Research & Decision Log: 060-fix-wheel-avx-objdump-scanner

## Decision 1: `objdump -d` 기계어 디스어셈블러 레벨 AVX 명령어 정밀 스캐너 전환

### Rationale (선택 이유)
- 순수 16진수 바이트 스캐너는 x86_64 가변 길이 명령어 스트림 내의 오프셋(Displacement), ModRM, Immediate 상숫값에 등장하는 `0xC4`/`0xC5` 바이트를 AVX VEX 프리픽스로 오판단함. (실제로 AVX가 100% 없는 `libllama.so` 및 `libggml-cpu.so`에 대해 79,530건의 허위 AVX 감지 발생).
- Linux 표준 `binutils` 패키지의 `objdump -d --no-show-raw-insn` 명령어를 활용하여 유효한 어셈블리 명령어 경계(Instruction Boundary)를 추출하고, `^\s*[0-9a-f]+:\s+(v[a-z0-9]+)\b` 정규표현식으로 기계어 니모닉을 분석함.
- 특수 시스템 명령어(`verr`, `verw`, `vmread`, `vmwrite`, `vmmcall`, `vptr`)를 제외한 실제 VEX/EVEX 벡터 니모닉만 산출함으로써 **False Positive(허위 감지)를 100% 제거**하고 결정론적 0건(`total_avx=0`) 실측을 달성함.

### Alternatives Considered (기각된 대안들)
- **대안 A: 바이트 3바이트 VEX 프리픽스 조건 조여서 스캔하기**
  - **기각 사유**: 바이트 스트림 스캔은 명령어 경계를 파싱하지 않으므로 오프셋 바이트가 무작위로 `0xC4 0x01` 패턴을 형성하는 현상을 근본적으로 차단할 수 없음.
- **대안 B: 외부 Python Disassembler 라이브러리(`capstone`) 도입**
  - **기각 사유**: C-extension 서드파티 라이브러리 의존성을 추가하게 되어 씨드 팩 빌드 및 실행 환경 복잡도가 증가함. 표준 Linux 유틸리티인 `objdump` 사용이 가장 가볍고 확실함.

---

## Decision 2: `make_seed_pack.sh` C/C++ SIMD 차단 옵션 완결 보강

### Rationale (선택 이유)
- `scikit-build-core` 백엔드를 통한 PEP 517/518 컴파일 시 `SKBUILD_CMAKE_ARGS` 및 `CMAKE_ARGS`에 `-DGGML_CUDA=ON -DGGML_NATIVE=OFF -DGGML_AVX=OFF -DGGML_AVX2=OFF -DGGML_AVX512=OFF -DGGML_AVX512_VBMI=OFF -DGGML_AVX512_VNNI=OFF -DGGML_AVX512_BF16=OFF -DGGML_AVX_VNNI=OFF -DGGML_F16C=OFF -DGGML_FMA=OFF -DGGML_BMI2=OFF -DCMAKE_CUDA_ARCHITECTURES=61 -DCMAKE_C_FLAGS=-march=x86-64 -DCMAKE_CXX_FLAGS=-march=x86-64`를 명시함.
- C/C++ 컴파일러가 호스트 머신의 아키텍처 옵션을 사용하지 않고 strict `-march=x86-64` SSE4.2 베이스라인으로 C++ 코드(`g++`)를 빌드하도록 보장함.

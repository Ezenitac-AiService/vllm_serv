# Research: i7-930/GTX 1070 사전 빌드 휠 CMAKE_CUDA_ARCHITECTURES 및 GGML_NATIVE 결정사항 (031-fix-seed-pack-cuda-arch)

## Research Topic 1: CMAKE_CUDA_ARCHITECTURES 및 GGML_NATIVE 지정 필수성

### Decision
`scripts/make_seed_pack.sh`에서 `legacy-i7-930` 휠 사전 빌드 시 다음 환경 변수 및 CMake 인자를 명시적으로 결합하여 전달한다:
```bash
FORCE_CMAKE=1 CFLAGS="-march=x86-64" CMAKE_ARGS="-DGGML_CUDA=ON -DGGML_AVX=OFF -DGGML_AVX2=OFF -DGGML_F16C=OFF -DGGML_FMA=OFF -DGGML_NATIVE=OFF -DCMAKE_CUDA_ARCHITECTURES=61" uv run pip wheel "llama-cpp-python[server]" --no-binary llama-cpp-python --wheel-dir wheels/legacy_i7_930
```

### Rationale
1. **`-DCMAKE_CUDA_ARCHITECTURES=61`**: GTX 1070 GPU의 Compute Capability는 `6.1` (sm_61)입니다. CMake에서 이 플래그를 지정하지 않으면 빌드 수행 호스트 장비(Xeon E3/GTX 1080 Ti)의 아키텍처 코드로 결정되어 타겟 GTX 1070 머신에 전달되었을 때 CUDA 커널 이진 코드가 부재하여 `llama_supports_gpu_offload()` 검증이 실패합니다.
2. **`-DGGML_NATIVE=OFF`**: CMake의 기본 빌드 스크립트는 `-DGGML_NATIVE=ON` 상태에서 컴파일 호스트의 최적화 인자(`-march=native`)를 컴파일러에 전달합니다. Haswell/Xeon 호스트에서 빌드 시 AVX2 명령어 코드가 생기므로, `-DGGML_NATIVE=OFF`를 선언해야만 Nehalem i7-930(AVX 미지원) CPU에서 `SIGILL` (Illegal Instruction) crash를 완벽히 예방할 수 있습니다.
3. **`FORCE_CMAKE=1`**: `llama-cpp-python` 파이썬 패키지 세팅 스크립트가 PEP 517 빌드 환경에서도 C++ CMake 빌드를 강제 수행하도록 제어합니다.

### Alternatives Considered
- **CMake 기본 아키텍처 자동 감지 사용**: 호스트 장비의 GPU에 고정된 아키텍처로 컴파일되어 다른 종류의 타겟 GPU(GTX 1070)에 적용할 경우 GPU 오프로드 실패 유발 (기각).
- **타겟 머신에서 항시 C++ 소스 재컴파일**: 구축 시간이 15~30분 이상 소요되어 3분 이내 Instant 서빙 설치 요구사항(FR-002)에 위배됨 (기각).

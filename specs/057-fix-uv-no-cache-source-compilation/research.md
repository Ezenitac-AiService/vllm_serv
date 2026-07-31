# Phase 0 Research: Tier 4 uv 휠 캐시 실측 검증 및 불일치 시 조건부 --no-cache-dir C++ 소스 재컴파일 파이프라인 (057-fix-uv-no-cache-source-compilation)

**Feature Branch**: `057-fix-uv-no-cache-source-compilation`  
**Created**: 2026-07-31  
**Spec Link**: [`spec.md`](file:///home/dev/storage/vllm_serv/specs/057-fix-uv-no-cache-source-compilation/spec.md)

---

## 1. Research Overview & Key Decisions

### Decision 1: Option A - Tier 4 2단계 조건부 uv 휠 캐시 검증 파이프라인
- **결정**: `scripts/setup.sh` Tier 4 진입 시, 무조건 `--no-cache-dir`를 사용하여 매번 억지로 재컴파일하는 불필요한 연산 낭비를 지양하고, **2단계 조건부 캐시 검증**을 수행합니다.
  1. `uv pip install "llama-cpp-python[server]" --no-binary llama-cpp-python`을 구동하여 가상환경에 주입된 바이너리가 `llama_supports_gpu_offload() == True`를 만족하는지 3중 가속 검증을 먼저 실행합니다.
  2. 성공 시 기존 휠 캐시를 고속 재사용하여 수 초 만에 설치를 완결합니다.
  3. 검증 실패(CPU 전용 휠로 감지) 시에만 `uv pip uninstall llama-cpp-python` 호출 후, `CMAKE_ARGS="$DETECTED_CMAKE_ARGS" uv pip install --no-cache-dir "llama-cpp-python[server]" --no-binary llama-cpp-python` 명령으로 캐시를 무효화하고 실제 C++ 소스코드를 타깃 머신 GPU/CPU SIMD 사양에 맞게 컴파일합니다.
- **근거**: 3차 이관 실측 로그(`log.txt` 181-267행)에서 `uv`가 `~/.cache/uv/wheels` 디렉터리의 이전 CPU 전용 휠을 5ms 만에 스킵 설치하여 동적 `CMAKE_ARGS`를 무력화한 결함을 원천 차단함과 동시에, 검증을 통과한 휠은 수 초 만에 고속 복원하도록 보장함.
- **기각된 대안**: 무조건 `--no-cache-dir` 강제 적용 (정상 휠이 캐시에 존재함에도 매번 수 분 동안 불필요한 C++ 재컴파일을 유발함).

---

### Decision 2: GTX 1080 Ti(GP102) vs GTX 1070(GP104) 휠 호환성 및 CPU SIMD 분리 원칙
- **결정**: 두 GPU 카드는 Compute Capability `6.1` (`sm_61`)로 동일하지만, 호스트 CPU SIMD 사양이 극명히 다름을 반영합니다.
  - **GTX 1080 Ti 개발 머신 (`pascal-avx2-gtx1080ti`)**: Haswell CPU (AVX2=1, `-DGGML_AVX=ON`, `-DGGML_AVX2=ON`).
  - **GTX 1070 레거시 서비스 머신 (`legacy-i7-930-gtx1070`)**: Nehalem i7 930 CPU (AVX=0, AVX2=0, `-DGGML_AVX=OFF`, `CFLAGS=-march=x86-64`).
- **근거**: 1080 Ti 개발 머신에서 빌드된 휠을 1070 타깃 머신에 직접 가져가면 GPU 코드가 아니라 **CPU SIMD 명령어(AVX/AVX2) 미지원** 때문에 `Illegal Instruction (core dumped)`으로 즉시 크래시됨이 실측 검증됨. 따라서 Seed Pack(`vllm_serv_seed.tar.gz`)에는 오직 `legacy-i7-930-gtx1070` 사양(`-DGGML_AVX=OFF`, `sm_61`) 전용 사전 휠(`wheels/legacy_i7_930/*.whl`)만 패키징합니다.

---

### Decision 3: `make_seed_pack.sh` 기존 사전 휠 재사용 & Post-Build 3중 검증 및 결함 휠 자동 삭제
- **결정**: `scripts/make_seed_pack.sh`에서 `--build-legacy` 옵션 구동 시:
  1. 이미 `wheels/legacy_i7_930/*.whl`이 존재하고 `scripts/verify_wheel_binary.py` 검증(AVX=0, CUDA=1)을 통과하면 **기존 휠을 재사용**하여 휠 빌드를 스킵합니다.
  2. 기존 휠이 없거나 검증 실패 시, `uv run pip wheel --no-cache-dir ...` 및 `CFLAGS=-march=x86-64`, `-DGGML_AVX=OFF`, `-DCMAKE_CUDA_ARCHITECTURES=61` 인자로 순수 신규 휠을 빌드합니다.
  3. 빌드 직후 `scripts/verify_wheel_binary.py`로 생성된 바이너리를 3중 검증(AVX=0, CUDA=1)하여 검증 실패 시 `rm -f`로 결함 휠을 즉시 자동 삭제합니다.
- **근거**: 개발 머신의 오염된 디스크 캐시가 사전 휠에 유입되는 현상을 막고, 훼손된 사전 휠이 아카이브에 포함되어 마이그레이션을 망가뜨리는 리스크를 100% 방지함.

---

### Decision 4: `unpack_seed.sh` 프로젝트 루트(`vllm_serv/`) 안전 해제 스크립트
- **결정**: `scripts/unpack_seed.sh` (및 프로젝트 루트 단축 심볼릭 링크 `./unpack_seed.sh`)를 제공하여 `vllm_serv/` 프로젝트 루트에서 지정된 아카이브(기본값 `vllm_serv_seed.tar.gz`, `$1` 유연 인자 가능)를 안전하게 해제합니다.
  - `tar -xvkpf "$TAR_FILE" -C ./` 사용 (`-k` / `--skip-old-files`로 검증 통과한 기존 유효 바이너리 덮어쓰기 방지, `-p` / `--same-permissions`로 파일 권한 보존).
- **근거**: 복잡한 수동 `tar` 옵션을 사용자가 매번 입력하는 불편함을 제거하고, 이미 정상 동작하는 local 바이너리가 존재할 때 덮어쓰여 망가지는 사고를 원천 방지함.

---

### Decision 5: `nvidia-smi` 감지 실패 시 안전 Fallback 및 Tier 4 중단 시 원자적(Atomic) 롤백
- **결정**:
  1. `src.core.cpu_detector` 구동 중 드라이버 미설치나 샌드박스 제약으로 `nvidia-smi` 호출이 실패하면 `config/platform_profiles.json` 호스트 프로필의 기본 GPU 세대로 안전하게 Fallback 바인딩합니다.
  2. Tier 4 C++ 소스 재컴파일 도중 중단(Ctrl+C) 또는 실패 시, `uv pip uninstall llama-cpp-python`을 호출하여 불완전한 결함 바이너리가 가상환경에 잔류하지 않도록 원자적(Atomic) cleanup을 수행합니다.

---

## 2. Technical Dependencies & Constraints Matrix

| 컴포넌트 / 스크립트 | 의존성 | 제약사항 | 안전 대책 |
|:---|:---|:---|:---|
| `scripts/setup.sh` (Tier 4) | `uv`, `nvidia-smi`, `verify_wheel_binary.py` | 캐시 오염 가능성 | Option A 2단계 실측 검증 후 실패 시에만 `--no-cache-dir` |
| `scripts/make_seed_pack.sh` | `uv run pip wheel`, `gcc`, `nvcc` | 호스트 AVX2 오염 위험 | `-DGGML_AVX=OFF`, `--no-cache-dir`, Post-Build `rm -f` |
| `scripts/unpack_seed.sh` | `tar`, `vllm_serv_seed.tar.gz` | 기존 유효 바이너리 덮어쓰기 위험 | `tar -xvkpf` (`--skip-old-files`, `--same-permissions`) |
| `src/core/cpu_detector.py` | `nvidia-smi`, `platform_profiles.json` | 드라이버 미설치/샌드박스 오류 | `try-except` 후 platform profile fallback |

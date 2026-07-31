# Interface Contract: 시드 팩 사전 빌드 휠 CMAKE 인자 명세 (031-fix-seed-pack-cuda-arch)

## 1. `scripts/make_seed_pack.sh` 사전 컴파일 빌드 명세

### CLI 실행 계약 (Execution Contract)

```bash
FORCE_CMAKE=1 \
CFLAGS="-march=x86-64" \
CMAKE_ARGS="-DGGML_CUDA=ON -DGGML_AVX=OFF -DGGML_AVX2=OFF -DGGML_F16C=OFF -DGGML_FMA=OFF -DGGML_NATIVE=OFF -DCMAKE_CUDA_ARCHITECTURES=61" \
uv run pip wheel "llama-cpp-python[server]" --no-binary llama-cpp-python --wheel-dir wheels/legacy_i7_930
```

### 파라미터 규격 (Parameter Specification)

| Parameter / Env | Value | Requirement Level | Purpose |
|-----------------|-------|-------------------|---------|
| `FORCE_CMAKE` | `1` | **MANDATORY** | PEP 517 분리 환경에서 CMake 빌드 강제 선언 |
| `CFLAGS` | `"-march=x86-64"` | **MANDATORY** | x86-64 기본 베이스라인 코드 생성 |
| `-DGGML_CUDA` | `ON` | **MANDATORY** | CUDA GPU 오프로딩 엔진 활성화 |
| `-DGGML_AVX` | `OFF` | **MANDATORY** | i7-930 Nehalem CPU 호환성 (AVX 차단) |
| `-DGGML_AVX2` | `OFF` | **MANDATORY** | i7-930 Nehalem CPU 호환성 (AVX2 차단) |
| `-DGGML_NATIVE` | `OFF` | **MANDATORY** | 호스트 CPU 최적화(`-march=native`) 명령어 누출 방지 |
| `-DCMAKE_CUDA_ARCHITECTURES` | `61` | **MANDATORY** | GTX 1070 GPU Compute Capability 6.1 (sm_61) 명시 지정 |

---

## 2. `scripts/setup.sh` 복원 검증 계약 (Verification Contract)

### 검증 구문 (Post-Install Assertion)

```bash
uv run python -c "
import llama_cpp
fn = getattr(llama_cpp, 'llama_supports_gpu_offload', None) or getattr(llama_cpp, 'llama_supports_gpu', None)
assert fn is not None, 'No GPU check function found'
assert fn(), 'GPU offload not supported'
"
```

### 반환 조건 계약

- **Success**: Return Code `0` (소스 컴파일 스킵, `INSTALLED_VIA_FAST_TRACK=1`)
- **Failure**: Return Code `!= 0` (경고 로그 출력 후 `INSTALLED_VIA_FAST_TRACK=0` 소스 컴파일 파이프라인 전환)

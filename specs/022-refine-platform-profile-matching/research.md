# Research & Technical Decisions: 플랫폼 프로필 매칭 정교화 및 출력 메시지 다듬기

## 1. CMake 인자 공백 서식 버그 원인 분석 및 해결 방안

- **문제점**: `src/core/cpu_detector.py`의 `get_llama_build_flags()`에서 `args_list` 항목들 중 `f"-DGGML_F16C={f16c_flag}"`과 `f"-DGGML_FMA={fma_flag}"` 사이 또는 리스트 결합 시 공백이 누락되어 `-DGGML_F16C=ON-DGGML_FMA=ON` 형태로 출력되는 문제 발생.
- **원인**: `args_list` 구성 코드에서 f-string 조합 시 `-DGGML_F16C=ON` 뒤에 스페이스 공백이 누락되었거나 리스트 합치기 시 발생함.
- **해결 방안**:
  `args_list` 요소를 각각 명확한 원소로 분리하여 `"-DGGML_CUDA=ON"`, `f"-DGGML_AVX={avx_flag}"`, `f"-DGGML_AVX2={avx2_flag}"`, `f"-DGGML_F16C={f16c_flag}"`, `f"-DGGML_FMA={fma_flag}"`, `f"-DCMAKE_CUDA_ARCHITECTURES={arch_code}"`로 독립 리스트를 만들고, `" ".join(args_list)`로 안전하게 조인함.

## 2. 하드웨어 프로필 매칭(`match_platform_profile`) 정교화

- **기존 방식**: `compute_capability` (`6.1`) 단일 값으로 프로필을 매칭하여 GTX 1070(Nehalem i7 930)과 GTX 1080 Ti(Haswell Xeon E3-1231 v3)가 동일하게 `legacy-i7-930-gtx1070`으로 매칭되는 한계 존재.
- **개선 방식**:
  `config/platform_profiles.json`에 `pascal-avx2-gtx1080ti` 프로필 항목을 추가하고:
  ```json
  "pascal-avx2-gtx1080ti": {
      "profile_id": "pascal-avx2-gtx1080ti",
      "name": "Haswell Xeon E3-1231 v3 + GTX 1080 Ti Server",
      "cpu_model": "Intel(R) Xeon(R) CPU E3-1231 v3 @ 3.40GHz",
      "ram_gb": 32,
      "gpu_name": "NVIDIA GeForce GTX 1080 Ti",
      "vram_mb": 11264,
      "compute_capability": "6.1",
      "os_name": "Ubuntu 24.04 LTS",
      "expected_avx": true,
      "expected_avx2": true
  }
  ```
  `match_platform_profile()` 함수에서 GPU `compute_capability`와 CPU `supports_avx2` 플래그를 조합하여:
  - `compute_capability == "6.1"`이고 `supports_avx2 == True` → `pascal-avx2-gtx1080ti` 매칭
  - `compute_capability == "6.1"`이고 `supports_avx2 == False` → `legacy-i7-930-gtx1070` 매칭
  - `compute_capability == "8.6"` → `dev-rtx3060` 매칭
  - 미정의 하드웨어인 경우 `custom-avx2-sm61` 또는 `custom-cpu-smXX` 형태의 동적 디스크립터 반환

## 3. 스크립트 출력 문구 다듬기

- **개선점**:
  `make_seed_pack.sh`, `status_server.sh`, `setup.sh` 내 예시 타겟 서버 표현을 특정 구형 하드웨어 모델명에 국한하지 않고 `예: 레거시 i7-930 / Xeon E3 서버 또는 개발 머신`으로 범용성과 명료성을 가질 수 있도록 문구 다듬기 수행.

# Phase 1: Data Model & CLI Interface Specification - 운영 쉘 스크립트 멀티 플랫폼 고도화

**Feature Branch**: `021-enhance-shell-scripts`
**Created**: 2026-07-30

## Data Models & Key Entities

### 1. Platform Profile Match Result (Entity / CLI Output)

`src/core/cpu_detector.py --match-profile` 및 internal 파이썬 API의 반환 데이터 엔티티.

```json
{
  "profile_id": "legacy-i7-930-gtx1070",
  "profile_name": "Legacy i7-930 + GTX 1070 Server",
  "matched": true,
  "hardware_summary": {
    "cpu_model": "Intel(R) Core(TM) i7 CPU 930 @ 2.80GHz",
    "simd_avx": false,
    "simd_avx2": false,
    "gpu_name": "NVIDIA GeForce GTX 1070",
    "compute_capability": "6.1"
  },
  "cmake_flags": {
    "GGML_AVX": "OFF",
    "GGML_AVX2": "OFF",
    "GGML_F16C": "OFF",
    "GGML_FMA": "OFF",
    "GGML_CUDA": "ON",
    "CMAKE_CUDA_ARCHITECTURES": "61"
  }
}
```

### 2. Pre-flight Check Status (Entity / Execution State)

`start_server.sh` 구동 직전 하드웨어 사전 점검 상태 데이터.

```json
{
  "cuda_available": true,
  "nvidia_smi_present": true,
  "nvcc_present": true,
  "gpu_count": 1,
  "gpu_compute_cap": "6.1",
  "status": "PASS",
  "error_code": null,
  "remediation_hint": null
}
```

## CLI Interface Specifications

### 1. `src/core/cpu_detector.py` CLI 확충

```bash
# 프로필 매칭 ID 단일 출력 (쉘 변수 저장용)
uv run python -m src.core.cpu_detector --match-profile
# Output: legacy-i7-930-gtx1070

# 프로필 매칭 상세 정보 (JSON 형식)
uv run python -m src.core.cpu_detector --match-profile --format json
```

### 2. 쉘 스크립트 인터페이스 고도화

- `status_server.sh`:
  - `uv run python -m src.core.cpu_detector --report` 호출하여 감지 리포트 통합 출력.
- `start_server.sh`:
  - `uv run python -m src.core.cpu_detector --check-preflight` 호출하여 사전 점검 수행. 실패 시 exit 1.
- `setup.sh`:
  - `uv run python -m src.core.cpu_detector --match-profile` 호출하여 감지 결과와 프로필 비교 출력.
- `scripts/make_seed_pack.sh`:
  - 아카이브 내 `config/platform_profiles.json` 포함 여부 검증 기능 추가.

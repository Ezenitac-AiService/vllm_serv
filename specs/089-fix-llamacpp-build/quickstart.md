# Quickstart Validation Guide: llama.cpp 빌드 검증 및 휠 컴파일 파이프라인 (089-fix-llamacpp-build)

본 문서는 llama.cpp 패키지의 CUDA 가속 활성화 검증, CPU-only 휠 자동 캐시 무효화 및 재컴파일, NVIDIA 드라이버/CUDA/cuDNN 검증 및 인라인 자동 업데이트 기능을 엔드투엔드로 검증하기 위한 가이드입니다.

---

## 사전 준비 사항 (Prerequisites)

1. NVIDIA GPU 및 드라이버가 설치된 Linux 호스트 (Ubuntu 22.04 LTS / 24.04 LTS 또는 RHEL/Rocky Linux)
2. NVIDIA CUDA Toolkit (`nvcc`) 설치 환경 (기본 버전 >= 12.0)
3. 파이썬 `uv` 패키지 관리자 설치 및 `.venv` 가상환경

---

## 시나리오 1: 라이브 파이썬 가상환경 CUDA 가속 휠 검증

라이브 가상환경 내 `llama-cpp-python` 패키지가 CUDA GPU 가속을 지원하는지 직접 검증합니다.

```bash
# 1. 라이브 환경 휠 검증 실행
uv run python scripts/verify_wheel_binary.py --check-live

# Expected Outcome:
# - GPU 가속 활성화 시: "✓ Live environment CUDA acceleration verified" (종료 코드 0)
# - CPU 전용 설치 시: "llama_supports_gpu_offload() returned False (CPU-only mode)" (종료 코드 1)
```

---

## 시나리오 2: CPU-Only 캐시 무효화 및 동적 C++ 소스 재컴파일 유발 (`setup.sh`)

기존 가상환경에 결함(CPU-only)이 있거나 캐시된 휠이 부적절할 때 `setup.sh`가 이를 감지하고 `--no-cache-dir`로 동적 재컴파일을 수행하는지 검증합니다.

```bash
# 1. setup.sh 스크립트 가동
./scripts/setup.sh

# Expected Outcome:
# - Step 2에서 nvcc 및 nvidia-smi 검증 완료
# - "⚠️ [UV CACHE INVALID] uv 캐시 휠이 CPU 전용으로 감지되었습니다." 경고 출력
# - "--no-cache-dir" 및 CMAKE_ARGS="-DGGML_CUDA=ON ..." 적용 후 C++ 소스 동적 재컴파일 실행
# - 재컴파일 후 "✓ CUDA GPU 가속 활성화 최종 확인 완료" 출력하며 검증 통과
```

---

## 시나리오 3: NVIDIA 드라이버 & CUDA Toolkit 버전 검증 및 업데이트 스크립트 실행

NVIDIA 드라이버 및 CUDA Toolkit/cuDNN 버전을 점검하고 업데이트 가이드를 검증합니다.

```bash
# 1. 하드웨어 및 CUDA 환경 검증 모듈 실행
uv run python -m src.core.cpu_detector --report

# 2. 독립 드라이버/CUDA 업데이트 헬퍼 스크립트 실행 (수동 업데이트 테스트)
sudo ./scripts/update_cuda_drivers.sh

# Expected Outcome:
# - OS 패키지 관리자(apt/dnf) 기반으로 최신 권장 NVIDIA 드라이버 및 CUDA Toolkit, cuDNN 패키지 상태 점검 및 갱신 완료
```

---

## 시나리오 4: 서버 상태 리포트 스크립트 확인 (`status_server.sh`)

`status_server.sh` 스크립트를 통해 CUDA 빌드 상태 및 nvcc, GPU VRAM 상태가 올바르게 표출되는지 검증합니다.

```bash
# 1. 서버 상태 조회
./scripts/status_server.sh

# Expected Outcome:
# - [CUDA 빌드 상태] 섹션에 nvcc 버전 및 llama_supports_gpu_offload() 결과가 "True"로 표시됨
```

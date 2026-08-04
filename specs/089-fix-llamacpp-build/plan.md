# Implementation Plan: llama.cpp 빌드 검증 및 휠 컴파일 파이프라인 수정 (fix-llamacpp-build)

**Branch**: `089-fix-llamacpp-build` | **Date**: 2026-08-04 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/089-fix-llamacpp-build/spec.md`

## Summary

`vllm_serv` 서빙 시스템의 `llama.cpp` (llama-cpp-python) 패키지 컴파일 시, CPU 전용(CPU-only) 캐시된 휠이 유입되는 문제를 차단하고 CUDA GPU 가속(`llama_supports_gpu_offload()`)을 100% 보장하는 컴파일/검증 파이프라인을 구축합니다. 또한 `setup.sh` 가동 시 NVIDIA Driver, CUDA Toolkit (`nvcc`), cuDNN 버전을 정밀 점검하고 대화형 TTY 환경 승인 시 인라인 패키지 자동 업데이트(`scripts/update_cuda_drivers.sh`)를 완수하도록 시스템을 강화합니다.

## Technical Context

**Language/Version**: Python 3.12, C++17 (nvcc CUDA Compiler 12.8)

**Primary Dependencies**: llama-cpp-python 0.3.34, uv 0.11.x, NVIDIA CUDA Toolkit 12.8, PyTorch / cuDNN

**Storage**: Local `.venv` environment, shared wheels (`wheels/`), `/usr/local/cuda`

**Testing**: Pytest (`tests/`), bash pipeline validation (`scripts/verify_wheel_binary.py`)

**Target Platform**: Linux x86_64 server (Ubuntu 22.04/24.04, RHEL/Rocky), NVIDIA GPU (RTX 3060 sm_86)

**Project Type**: Python Web Service + C++ Shared Library Binding & Infrastructure Automation Scripts

**Performance Goals**: 이미 검증된 GPU 휠 상주 시 0.1초 이내 setup 검증 스킵, GPU 오프로드 100% 달성

**Constraints**: CPU 전용 암묵적 폴백 엄금, C++ 컴파일 실패 시 100% 원자적 cleanup(uninstall)

**Scale/Scope**: `scripts/setup.sh`, `scripts/status_server.sh`, `scripts/verify_wheel_binary.py`, `scripts/update_cuda_drivers.sh`, `src/core/cpu_detector.py`, `src/core/gpu_detector.py`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle I: Library-First**: `cpu_detector`, `gpu_detector`, `verify_wheel_binary` 등 모듈화된 파이썬/쉘 라이브러리로 self-contained 구성. (PASS)
- **Principle II: CLI Interface**: `verify_wheel_binary.py`, `update_cuda_drivers.sh`, `cpu_detector` 모두 CLI 프로토콜(stdin/stdout/stderr, exit code) 준수. (PASS)
- **Principle III: Test-First**: 파라미터화된 파이썬 검증 모듈 및 쉘 파이프라인 자동 테스트 구성. (PASS)
- **Principle IV: Integration Testing**: GPU 가속 지원 및 C++ 소스 재컴파일, 빌드 롤백 통합 테스트 포함. (PASS)

## Project Structure

### Documentation (this feature)

```text
specs/089-fix-llamacpp-build/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── cuda_build_api.json # Interface contract
└── checklists/
    └── requirements.md  # Quality checklist
```

### Source Code Layout

```text
scripts/
├── setup.sh                   # 원스톱 환경 검증, 인라인 드라이버/CUDA 점검 및 휠 컴파일
├── status_server.sh          # CUDA 빌드 및 드라이버/nvcc 헬스체크 리포트
├── verify_wheel_binary.py    # AVX 스캔 & llama_supports_gpu_offload() 실측 검증
└── update_cuda_drivers.sh    # [NEW] OS 패키지 매니저 기반 NVIDIA 드라이버/CUDA/cuDNN 업데이트 헬퍼

src/core/
├── cpu_detector.py           # CPU SIMD 및 GPU Compute Capability, CMAKE_ARGS 매칭
├── gpu_detector.py           # NVIDIA Driver / CUDA Toolkit / cuDNN 버전 감지
└── process_manager.py        # llama-server 서빙 프로세스 및 VRAM 오프로드 제어

tests/
├── unit/
└── integration/
```

**Structure Decision**: 기존 `vllm_serv` 프로젝트 구조를 유지하며, 신규 헬퍼 스크립트(`scripts/update_cuda_drivers.sh`) 및 `src/core/gpu_detector.py` 버전 검증 강화 로직을 결합합니다.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

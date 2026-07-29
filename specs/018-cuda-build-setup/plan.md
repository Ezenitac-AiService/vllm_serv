# Implementation Plan: Automated CUDA-Enabled llama.cpp Build & Setup Pipeline

**Branch**: `018-cuda-build-setup` | **Date**: 2026-07-29 | **Spec**: [spec.md](file:///home/dev/storage/vllm_serv/specs/018-cuda-build-setup/spec.md)

**Input**: Feature specification from `/specs/018-cuda-build-setup/spec.md`

## Summary

본 구현 계획은 `./setup.sh` 파이프라인 및 `ProcessManager` 구동 시 `llama.cpp` 및 `llama-cpp-python` 서빙 모듈이 NVIDIA CUDA 가속 플래그(`GGML_CUDA=ON`)로 결함 없이 컴파일/동기화되도록 강형화하는 기술 설계를 규정합니다. `pyproject.toml` 의존성에 `llama-cpp-python[server]`를 명시하고 `setup.sh` 내 `uv pip install` 시 `CMAKE_ARGS="-DGGML_CUDA=on"`을 지정하여 `llama_supports_gpu()`가 `True`를 반환하도록 고정하며, CUDA 환경 누락 시 즉시 중단(Fail-Fast) 에러 처리를 적용합니다.

## Technical Context

**Language/Version**: Python 3.12, Bash (POSIX compliance)

**Primary Dependencies**: FastAPI, HTTPX, Pydantic v2, llama-cpp-python[server], cmake, ninja, nvcc (NVIDIA CUDA Toolkit)

**Storage**: Local GGUF Model weights (`models/`)

**Testing**: Pytest (`uv run pytest -v`)

**Target Platform**: Linux (Ubuntu 22.04 LTS), NVIDIA GPU (GTX 1080 Ti 11GB VRAM)

**Project Type**: AI Model Serving Infrastructure & Management API

**Performance Goals**: 100% GPU VRAM offloading, high throughput (>8 tok/s on GTX 1080 Ti), low latency TTFT (<1.0s)

**Constraints**: CPU-only fallback strictly blocked; Fail-fast on CUDA missing; Strict uv virtualenv isolation (`uv run`)

**Scale/Scope**: 6 Catalog Models (Gemma 4 2B/4B/12B, Qwen 3.5 2B/4B/9B)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] 계획서가 한국어로 작성되었는가? (언어 정책)
- [x] 테스트 코드 작성 계획이 포함되어 있는가? (테스트 필수 원칙)
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (종료 조건 명확화 원칙)
- [x] 파괴적 문서 수정을 금지하고 명시적 항목만 업데이트하는가? (비파괴적 문서 수정 원칙)
- [x] uv 환경 및 패키지 관리 규칙(`uv run`, `uv sync`)을 준수하는가? (uv 패키지 및 환경 관리 원칙)

## Project Structure

### Documentation (this feature)

```text
specs/018-cuda-build-setup/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── contracts/           # Phase 1 output
    └── cuda_build_api.md
```

### Source Code (repository root)

```text
src/
├── core/
│   ├── process_manager.py    # CMake -DGGML_CUDA=ON build & CUDA verification
│   ├── config_manager.py     # Server & catalog configuration
│   ├── gpu_detector.py       # nvcc & PyNVML CUDA GPU detector
│   └── llama_manager.py      # Life-cycle coordinator
└── api/
    └── server.py             # FastAPI entrypoint

scripts/
├── setup.sh                  # CUDA pip install & uv sync build pipeline
├── start_server.sh           # Daemon startup
├── status_server.sh          # Server & nvtop GPU status
└── stop_server.sh           # Safe shutdown

tests/
├── unit/
│   └── test_gpu_detector.py  # CUDA acceleration unit tests
└── integration/
    └── test_gpu_validation.py# Real GPU VRAM offload validation
```

**Structure Decision**: Single project layout matching repository architecture.

## Complexity Tracking

> **Constitution Check: No violations. Standard architecture.**

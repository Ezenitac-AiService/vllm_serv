# Implementation Plan: Codebase Structural Audit & Real-world Test Reliability Verification

**Branch**: `012-audit-test-reliability` | **Date**: 2026-07-29 | **Spec**: [spec.md](file:///home/dev/storage/vllm_serv/specs/012-audit-test-reliability/spec.md)

**Input**: Feature specification from `/specs/012-audit-test-reliability/spec.md`

## Summary

본 구현 계획은 단위/통합 테스트 수트(`pytest`)와 실측 런타임 스크립트(`scripts/benchmark_quality.py`) 간의 실행 불일치 및 거짓 성공(False Positive) 현상을 해소하기 위한 구조적 정밀 점검 및 리팩토링 계획이다. `ProcessManager` 내 프로세스 정방향 교체 순서(`stop_process` $\rightarrow$ `_wait_for_port_free` $\rightarrow$ `detect_zombie_collision`), Python 3.12 비동기 이벤트 루프 래핑(`_run_async`), CUDA 가속 파이프라인(FR-008 4단계 선형 순서) 및 테스트 Fixture 자원 해제(Tear-down) 계약을 표준화한다.

## Technical Context

**Language/Version**: Python 3.12.3 (`vllm-serv` virtual environment via `uv`)

**Primary Dependencies**: FastAPI, Uvicorn, httpx, llama-cpp-python (with CUDA acceleration), pynvml, pytest, pytest-asyncio, Antigravity Gemini 3.6 Flash SDK (Golden Dataset Synthesizer)

**Storage**: Local GGUF Model Artifacts in `models/` directory

**Testing**: Pytest with `pytest-asyncio` strict mode, custom Async/Sync test fixtures

**Target Platform**: Linux Server (Ubuntu 24.04 LTS), NVIDIA GeForce GTX 1080 Ti (11GB VRAM, CUDA 13.0)

**Project Type**: Python High-Performance LLM Serving Engine & Benchmark Suite

**Performance Goals**: 6개 모델 연속 서빙 및 품질/속도 비교 벤치마크 루프 100% 무에러 완주 (OOM 및 포트 충돌 0건)

**Constraints**: GTX 1080 Ti 11GB VRAM 용량 제한 내 100% GPU Layer Offloading, 포트 8081 단일 서빙 포트 고정

**Scale/Scope**: 6개 모델 카탈로그 (`gemma4-e2b`, `gemma4-e4b`, `gemma4-12b`, `qwen3.5-2b`, `qwen3.5-4b`, `qwen3.5-9b`), 74개 전체 단위/통합 테스트 수트

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] 계획서가 한국어로 작성되었는가? (언어 정책 원칙 I)
- [x] 테스트 코드 작성 및 검증 계획이 포함되어 있는가? (TDD 및 품질 보증 원칙 II)
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (종료 조건 명확화 원칙 III)

## Project Structure

### Documentation (this feature)

```text
specs/012-audit-test-reliability/
├── spec.md              # Feature Specification
├── plan.md              # Implementation Plan (this file)
├── research.md          # Phase 0 Research & Technical Decisions
├── data-model.md        # Phase 1 Data Model & Lifecycle Entities
├── quickstart.md        # Phase 1 Runnable Validation Guide
├── contracts/           # Phase 1 Interface Contracts
│   └── process-lifecycle-api.json
└── checklists/
    └── requirements.md  # Specification Quality Checklist
```

### Source Code (repository root)

```text
src/
├── api/
│   ├── main.py          # FastAPI application entrypoint & lifespan
│   └── server.py        # Health Liveness/Readiness endpoints
├── core/
│   ├── config_manager.py # Model configuration & presets
│   ├── gpu_detector.py   # PyNVML VRAM inspection & KV Cache estimator
│   ├── llama_manager.py # Residency management & dual health verification
│   └── process_manager.py # Subprocess lifecycle, port clearing & CUDA offload
scripts/
└── benchmark_quality.py # Real GPU benchmark execution loop & report generator
tests/
├── integration/
│   ├── test_dashboard.py
│   ├── test_dashboard_api.py
│   ├── test_gpu_validation.py
│   ├── test_quality_benchmark.py
│   ├── test_qwen_benchmark.py
│   └── test_serving_switch.py
└── unit/
    ├── test_config_manager.py
    ├── test_gpu_detector.py
    ├── test_llama_manager.py
    ├── test_model_downloader.py
    ├── test_process_manager.py
    └── test_quality_evaluator.py
```

**Structure Decision**: 기존 단일 Python 프로젝트 구조(`src/`, `scripts/`, `tests/`)를 그대로 유지하며, `src/core/process_manager.py` 및 `scripts/benchmark_quality.py`, `tests/` Fixture의 리소스 정리 계약을 명확히 강화한다.

## Complexity Tracking

*Constitution Check에 위반 사항이 없으므로 작성 불필요.*

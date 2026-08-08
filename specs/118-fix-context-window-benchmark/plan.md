# Implementation Plan: 마이그레이션 RTX 3060 플랫폼 컨텍스트 윈도우 벤치마크 전수 평가 및 동적 KV 캐시 VRAM 오탐 수정

**Branch**: `118-fix-context-window-benchmark` | **Date**: 2026-08-08 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/118-fix-context-window-benchmark/spec.md`

## Summary

`ProcessManager` 사전 검사 및 KV 캐시 추정기(`estimate_kv_cache_vram`)에서 모델별 실제 GQA 아키텍처 파라미터(`n_layers`, `n_heads`, `n_head_kv`, `head_dim`)를 동적으로 추출하도록 개편하여, 16K 컨텍스트 윈도우 스케일링에서 15.2GB 일률 오탐 VRAM 차단 결함을 근본적으로 해소한다. 또한 `scripts/benchmark_context_window.py` CLI에 `--all` 인자를 추가하여 카탈로그 내 전체 LLM 가용 모델 순차 평가 및 `config/model_context_profiles.json` 원자적 반영을 달성한다.

## Technical Context

**Language/Version**: Python 3.12 (via `uv`)  
**Primary Dependencies**: `llama-cpp-python`, `pynvml` (NVML GPU Telemetry), `httpx`, `asyncio`  
**Storage**: `config/model_catalog.json`, `config/model_context_profiles.json`, `config/server_config.json`  
**Testing**: `pytest`, `pytest-asyncio` (`uv run pytest tests/unit/`)  
**Target Platform**: Linux server with NVIDIA GeForce RTX 3060 (12GB VRAM, CUDA 12.8)  
**Project Type**: Python CLI & Async Background Inference Service  
**Performance Goals**: 소형/GQA 모델(Qwen 2B/4B, Gemma 2B/4B)의 16K 컨텍스트 VRAM 정밀 계산(1.5GB~2.5GB 내외), 벤치마크 오탐 스폰 실패 0건  
**Constraints**: RTX 3060 12GB VRAM 물리적 한도 준수, 120초 타임아웃 래퍼, 100% 비파괴적 변경  
**Scale/Scope**: 카탈로그 내 모든 LLM 후보 모델(Qwen, Gemma 라인업)  

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] 계획서가 한국어로 작성되었는가? (언어 정책)
- [x] 테스트 코드 작성 계획이 포함되어 있는가? (테스트 필수 원칙)
- [x] 목업은 유료/제한 API로 엄격히 제한하고 실물 시스템/소켓/OS 인자 및 실제 호출 플래그(REAL_API_CALL=1) 기반 실측 검증 계획이 포함되어 있는가? (실체적 테스트 및 수렴 검증 원칙)
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (종료 조건 명확화 원칙)
- [x] 비파괴적 문서 수정 원칙을 준수하는가? (비파괴적 문서 수정 원칙)
- [x] uv 패키지 매니저 및 가상환경 격리 표준(uv run)을 준수하는가? (uv 패키지 및 환경 관리 원칙)
- [x] 전체 회귀 테스트 수트 및 Playwright 기반 E2E 브라우저 실측 검증 계획이 포함되어 있는가? (의무적 회귀 테스트 및 브라우저 E2E 검증 원칙)

## Project Structure

### Documentation (this feature)

```text
specs/118-fix-context-window-benchmark/
├── plan.md              # Implementation plan (/speckit-plan output)
├── research.md          # Phase 0 technical research decisions
├── data-model.md        # Phase 1 data schema & estimation formulas
├── quickstart.md        # Phase 1 validation scenarios
├── contracts/           # Phase 1 CLI contract schema
│   └── cli_contract.json
└── tasks.md             # Phase 2 implementation tasks (/speckit-tasks output)
```

### Source Code (repository root)

```text
src/
├── core/
│   ├── process_manager.py        # GQA parameter extraction & estimate_kv_cache_vram update
│   ├── gpu_detector.py           # GQA KV cache calculator with n_head_kv
│   └── config_manager.py         # Catalog & Profile persistence
scripts/
├── benchmark_context_window.py   # CLI --all all-model evaluation flag
└── benchmark_quality.py          # Step 5.1 scaling loop VRAM estimation fix

tests/
└── unit/
    └── test_benchmark_context_window.py # Dynamic GQA estimation & CLI --all test suite
```

**Structure Decision**: Single project layout operating on `src/core/`, `scripts/`, and `tests/unit/`.

## Complexity Tracking

> **No violations. 100% compliant with constitution.**

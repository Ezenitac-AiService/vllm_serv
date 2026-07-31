# Implementation Plan: Real GPU Context Window Scaling Benchmark, Event Loop Cleanup & Config Externalization

**Branch**: `016-context-scaling-and-cleanup-fix` | **Date**: 2026-07-29 | **Spec**: [spec.md](file:///home/dev/storage/vllm_serv/specs/016-context-scaling-and-cleanup-fix/spec.md)

**Input**: Feature specification from `specs/016-context-scaling-and-cleanup-fix/spec.md`

---

## Summary

본 계획서는 실측 GPU 컨텍스트 윈도우 스케일링 (2K~32K) 벤치마크 루프 및 최적 모델 도출 리포트 생성, `BaseSubprocessTransport.__del__` 소멸자 예외 제거, OpenAI 표준 `GET /v1/models` 엔드포인트 구현, 그리고 파이썬 코드 내 모델 카탈로그 및 포트/URL 하드코딩의 외부 설정 파일 (`config/model_catalog.json`, `config/server_config.json`) 외부화 개정 계획을 수립합니다.

---

## Technical Context

**Language/Version**: Python 3.11 (`uv` managed)  
**Primary Dependencies**: `llama-server` (CUDA build), `llama_cpp.server`, `pydantic`, `fastapi`, `httpx`, `pytest`  
**Storage**: JSON configuration files (`config/model_config.json`, `config/model_catalog.json`, `config/server_config.json`)  
**Testing**: `uv run pytest` (Unit + Integration tests)  
**Target Platform**: Linux (Ubuntu 22.04), NVIDIA GeForce GTX 1080 Ti (11GB VRAM)  
**Project Type**: Python Async LLM Inference Microservice  
**Performance Goals**: `n_ctx` (2K, 4K, 8K, 16K, 32K) 실측 VRAM Peak, TTFT, TPOT 수집, 0 소멸자 경고 exit  
**Constraints**: GTX 1080 Ti VRAM 11GB limit, `n_seq_max=1` single inference queue  

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **언어 정책**: 계획서 및 제반 문서가 한국어로 작성되었는가? (원칙 I 준수)
- [x] **테스트 필수 원칙**: 기능 구현과 함께 검증용 단위/통합 테스트 코드 작성 계획이 수록되었는가? (원칙 II 준수)
- [x] **종료 조건 명확화**: 구체적이고 측정 가능한 Definition of Done이 정의되었는가? (원칙 III 준수)
- [x] **비파괴적 수정 원칙**: 기존 문서 내용 무단 삭제/축소 없이 필요한 요구사항만 명시하였는가? (원칙 IV 준수)
- [x] **uv 패키지 및 환경 관리 원칙**: 모든 실행 및 테스트 명령에 `uv run`을 사용하도록 명시하였는가? (원칙 V 준수)

---

## Project Structure

### Documentation (`specs/016-context-scaling-and-cleanup-fix/`)

```text
specs/016-context-scaling-and-cleanup-fix/
├── spec.md              # Feature specification
├── plan.md              # Implementation plan (this document)
├── research.md          # Phase 0 technical decisions
├── data-model.md        # Data models & JSON schemas
├── quickstart.md        # Runnable validation guide
└── contracts/           # Validation JSON schema
    └── openai_models_contract.json
```

### Source Code (`/home/dev/storage/vllm_serv/`)

```text
config/
├── model_catalog.json    # [NEW] Model catalog HF repository & file mappings
├── model_config.json     # Current active model & n_ctx configuration
└── server_config.json    # [NEW] Server port, host, timeout & pool configs

src/
├── api/
│   └── routes/
│       └── inference_api.py # [MODIFY] Add GET /v1/models dynamic handler
├── core/
│   ├── process_manager.py # [MODIFY] Transport close & load catalog from JSON
│   ├── model_downloader.py# [MODIFY] Load download catalog from JSON
│   ├── llama_manager.py   # [MODIFY] Load server configs dynamically
│   └── config_manager.py  # [MODIFY] Add ModelCatalog & ServerConfig loaders
└── eval/
    └── quality_evaluator.py # [MODIFY] Add Scaling Analysis Table & Recommender

scripts/
└── benchmark_quality.py # [MODIFY] Multi-context (2K~32K) real GPU benchmark loop

tests/
├── unit/
│   ├── test_process_manager.py
│   ├── test_model_downloader.py
│   └── test_openai_models.py # [NEW] Unit test for GET /v1/models
└── integration/
    └── test_context_scaling.py # [NEW] Real/Mock context scaling test
```

---

## Proposed Changes

### Component 1: Configuration Externalization (`config/model_catalog.json` & `config/server_config.json`)

1. **`config/model_catalog.json`**:
   - `gemma4-e2b`, `gemma4-e4b`, `gemma4-12b`, `qwen3.5-2b`, `qwen3.5-4b`, `qwen3.5-9b`에 대한 GGUF 경로, CLIP 경로, repo_id, vram_est_mb, chat_template 저장.
2. **`config/server_config.json`**:
   - `port` (`8081`), `host` (`127.0.0.1`), `healthcheck_timeout_s` (`120`), `connection_pool_max` (`100`) 설정.
3. **`ConfigManager` (`src/core/config_manager.py`)**:
   - `get_model_catalog()`, `get_server_config()` 함수 추가 및 환경변수(`LLAMA_PORT`, `LLAMA_HOST`) 오버라이드 지원.

---

### Component 2: `src/api/routes/inference_api.py` (OpenAI `GET /v1/models` API)

- `@router.get("/v1/models")` 동적 핸들러 구현:
  - `ConfigManager.get_model_catalog()`에서 전체 모델 카탈로그를 조회.
  - `ModelDownloader.is_model_available()`로 다운로드 여부 확인, `llama_manager.current_model_id`로 활성화 서빙 여부 판별.
  - OpenAI 규격 JSON (`{"object": "list", "data": [...]}`)으로 HTTP 200 OK 응답.

---

### Component 3: `src/core/process_manager.py` (Subprocess Transport Clean Exit)

- `stop_process()` 구현 고도화:
  - `if self.process and self.process._transport: self.process._transport.close()` 호출.
  - `await asyncio.sleep(0)`으로 이벤트 루프 마이크로태스크 소진.
  - 소멸자 호출 시 `RuntimeError: Event loop is closed` 발생 전파를 안전 차단.

---

### Component 4: Real GPU Multi-Context Scaling & Recommendation Engine (`scripts/benchmark_quality.py`)

- `benchmark_quality.py` 내의 곱셈 비례 정적 계산 제거.
- `n_ctx_list = [2048, 4096, 8192, 16384, 32768]` 순회하여 모델별 실측 GPU 벤치마크 수행.
- `QualityEvaluator.generate_markdown_report()`에서:
  - **컨텍스트 스케일링 분석표** (VRAM Peak, TTFT, TPOT) 작성.
  - **적정 모델 & 적정 컨텍스트 윈도우 크기 추천 매트릭스** (초저지연, 기본 상주 서빙, 고정밀 분석) 작성.

---

## Verification Plan

### Automated Tests

1. **Unit Tests**:
   ```bash
   uv run pytest tests/unit/test_process_manager.py tests/unit/test_model_downloader.py tests/unit/test_openai_models.py -v
   ```
2. **Integration Tests**:
   ```bash
   uv run pytest tests/integration/test_context_scaling.py -v
   ```
3. **Full Test Suite Validation**:
   ```bash
   uv run pytest -v
   ```

### Manual & Real GPU Verification

1. **OpenAI Models Endpoint Test**:
   ```bash
   curl -X GET http://127.0.0.1:8000/v1/models
   ```
2. **Real GPU Multi-Context Scaling Benchmark**:
   ```bash
   PYTHONUNBUFFERED=1 uv run python -u scripts/benchmark_quality.py --auto-download --real
   ```
3. **Success Indicators**:
   - `curl GET /v1/models` 성공 (6개 모델 리스트 200 OK).
   - 실측 벤치마크 완료 후 종료 시 `BaseSubprocessTransport.__del__` 경고 0건.
   - `data/reports/analysis_report_quality.md`에 스케일링 비교표 및 최적 추천 매트릭스 작성 완료.

# Implementation Plan: Gemma 4 Model Loading Fix & MMProj Vision Projector Binding

**Branch**: `015-gemma4-model-loading-fix` | **Date**: 2026-07-29 | **Spec**: [spec.md](file:///home/dev/storage/vllm_serv/specs/015-gemma4-model-loading-fix/spec.md)

**Input**: Feature specification from `specs/015-gemma4-model-loading-fix/spec.md`

---

## Summary

본 구현 계획은 `gemma4` 하이브리드 아키텍처 모델 (`gemma4-e2b`, `gemma4-e4b`) 서빙 시 MMProj 프로젝터를 필수 결합하여 VRAM 오프로드 0% 타임아웃 장애를 해결하고 `36/36 layers offloaded to GPU` 100% CUDA 가속을 달성하는 구체적 코드 변경 사항을 정의합니다.

---

## Technical Context

**Language/Version**: Python 3.11 (`uv` managed)  
**Primary Dependencies**: `llama-server` (CUDA build), `llama_cpp.server`, `pydantic`, `fastapi`, `httpx`, `pytest`  
**Storage**: Local model files (`models/gemma4-2b/`, `models/gemma4-4b/`)  
**Testing**: `uv run pytest` (Unit + Integration tests)  
**Target Platform**: Linux (Ubuntu 22.04), NVIDIA GeForce GTX 1080 Ti (11GB VRAM)  
**Project Type**: Python Async LLM Inference Microservice  
**Performance Goals**: `36/36 layers offloaded to GPU` (100% VRAM offload), Healthcheck READY < 120s  
**Constraints**: GTX 1080 Ti VRAM 11GB limit, `n_seq_max=1` single inference queue  

---

## Constitution Check

*GATE: All principles MUST pass before proceeding to execution.*

- [x] **언어 정책**: 계획서 및 관련 제반 문서가 한국어로 작성되었는가? (원칙 I 준수)
- [x] **테스트 필수 원칙**: 기능 구현과 함께 검증용 단위/통합 테스트 코드 작성 계획이 수록되었는가? (원칙 II 준수)
- [x] **종료 조건 명확화**: 구체적이고 측정 가능한 Definition of Done이 정의되었는가? (원칙 III 준수)
- [x] **비파괴적 수정 원칙**: 기존 문서 내용 무단 삭제/축소 없이 필요한 요구사항만 명시하였는가? (원칙 IV 준수)
- [x] **uv 패키지 및 환경 관리 원칙**: 모든 실행 및 테스트 명령에 `uv run`을 사용하도록 명시하였는가? (원칙 V 준수)

---

## Project Structure

### Documentation (`specs/015-gemma4-model-loading-fix/`)

```text
specs/015-gemma4-model-loading-fix/
├── spec.md              # Feature specification
├── plan.md              # Implementation plan (this document)
├── research.md          # Phase 0 technical decisions
├── data-model.md        # Data models & catalog preset extensions
├── quickstart.md        # Runnable validation guide
├── contracts/           # Validation JSON schema
│   └── gemma4_loading_contract.json
└── checklists/
    └── requirements.md  # Spec quality checklist
```

### Source Code (`/home/dev/storage/vllm_serv/`)

```text
src/
├── core/
│   ├── process_manager.py     # [MODIFY] Preset catalog & MMProj binding CLI logic
│   ├── model_downloader.py    # [MODIFY] One-stop MMProj auto-download logic
│   └── gpu_detector.py        # [MODIFY] Pre-flight VRAM estimator update
└── utils/
    └── config.py

tests/
├── unit/
│   ├── test_process_manager.py # [MODIFY] Add Gemma 4 MMProj CLI test
│   └── test_model_downloader.py# [MODIFY] Add Gemma 4 MMProj download test
└── integration/
    └── test_gemma4_serving.py  # [NEW] Real/Mock Gemma 4 serving test
```

---

## Proposed Changes

### Component 1: `src/core/process_manager.py` (Preset Catalog & MMProj Binding)

#### [MODIFY] `process_manager.py`

1. **Preset Catalog MMProj Binding**:
   - `PRESET_CATALOG` 데이터에 `gemma4-e2b`, `gemma4-e4b`의 `clip` 파일명 및 `requires_mmproj=True` 바인딩.
2. **MMProj CLI Argument Injection**:
   - `spawn_process()` 실행 시 `clip_file`을 프리셋에서 도출하여 로컬 경로 검증 후 standalone `llama-server`에는 `--mmproj <path>`, `llama_cpp.server`에는 `--clip_model_path <path>`를 필수 주입.

```python
# PRESET_CATALOG update
"gemma4-e2b": {
    "repo_id": "ggml-org/gemma-4-E2B-it-GGUF",
    "file": "gemma-4-E2B_q4_0-it.gguf",
    "clip": "gemma-4-E2B-it-mmproj.gguf",
    "vram_mb": 2500,
    "n_ctx": 2048,
    "chat_template": "gemma",
    "requires_mmproj": True
}

# spawn_process logic update
clip_filename = target_preset.get("clip")
if clip_filename:
    clip_file = os.path.join(model_dir, clip_filename)

if clip_file and os.path.exists(clip_file):
    if binary_info.build_source != "PYTHON_MODULE_FALLBACK":
        cmd.extend(["--mmproj", clip_file])
    else:
        cmd.extend(["--clip_model_path", clip_file])
```

---

### Component 2: `src/core/model_downloader.py` (One-Stop MMProj Auto-Download)

#### [MODIFY] `model_downloader.py`

- `download_model()` 수행 시 프리셋에 `clip` 프로젝터 경로가 정의된 경우, `hf_hub_download`를 호출하여 `.mmproj.gguf` 파일도 함께 다운로드 및 검증.

---

### Component 3: Test Suite Updates

#### [MODIFY] `tests/unit/test_process_manager.py`
- Gemma 4 모델 개설 시 `--mmproj` / `--clip_model_path` CLI 인자가 정상 전달되는지 검증하는 단위 테스트 추가.

#### [NEW] `tests/integration/test_gemma4_serving.py`
- Gemma 4 E2B 및 E4B 모델 스폰 시 `36/36 layers offloaded to GPU` 로그 검증 및 헬스체크 200 OK 통합 테스트.

---

## Verification Plan

### Automated Tests

1. **Unit Tests**:
   ```bash
   uv run pytest tests/unit/test_process_manager.py tests/unit/test_model_downloader.py -v
   ```
2. **Integration Tests**:
   ```bash
   uv run pytest tests/integration/test_gemma4_serving.py -v
   ```
3. **Full Test Suite Validation**:
   ```bash
   uv run pytest -v
   ```

### Manual Verification

1. **Real GPU Benchmark Verification**:
   ```bash
   uv run python scripts/benchmark_quality.py --auto-download --real
   ```
2. **Success Indicators**:
   - `gemma4-e2b` 및 `gemma4-e4b` 모델 36/36 layers offloaded 100% CUDA 가속 확인.
   - `analysis_report_quality.md` 리포트에 Gemma 4 평가 결과 100% 기재 완료.

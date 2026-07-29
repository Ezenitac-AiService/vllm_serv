# Data Model: Gemma 4 Model Loading Fix & MMProj Vision Projector Binding

**Feature Branch**: `specs/015-gemma4-model-loading-fix`
**Created**: 2026-07-29

---

## Data Models & Presets

### 1. Gemma4ModelPreset (Model Catalog Preset Extension)

`src/core/process_manager.py` 내 `PRESET_CATALOG` 데이터 구조를 확장하여 Gemma 4 아키텍처 모델에 MMProj 프로젝터 파일 경로를 바인딩합니다.

```python
{
    "gemma4-e2b": {
        "repo_id": "ggml-org/gemma-4-E2B-it-GGUF",
        "file": "gemma-4-E2B_q4_0-it.gguf",
        "clip": "gemma-4-E2B-it-mmproj.gguf",  # MMProj 프로젝터 파일 경로
        "vram_mb": 2500,
        "n_ctx": 2048,
        "chat_template": "gemma",
        "requires_mmproj": True  # Gemma 4 필수 MMProj 결합 플래그
    },
    "gemma4-e4b": {
        "repo_id": "ggml-org/gemma-4-E4B-it-GGUF",
        "file": "gemma-4-E4B_q4_0-it.gguf",
        "clip": "gemma-4-E4B-it-mmproj.gguf",  # MMProj 프로젝터 파일 경로
        "vram_mb": 4200,
        "n_ctx": 2048,
        "chat_template": "gemma",
        "requires_mmproj": True  # Gemma 4 필수 MMProj 결합 플래그
    }
}
```

---

### 2. VramOffloadStatus (VRAM 오프로드 검증 엔티티)

`ProcessManager._verify_vram_offload_from_line()`이 `llama-server` 로그에서 인스펙션하는 엔티티:

```python
class VramOffloadStatus(BaseModel):
    model_id: str
    total_layers: int = 0
    offloaded_layers: int = 0
    is_fully_offloaded: bool = False
    has_clip_offload: bool = False
    offloaded_vram_mb: int = 0
```

- **Validation Rules**:
  - `total_layers > 0` 일 때 `offloaded_layers == total_layers` 인 경우에만 `is_fully_offloaded = True`.
  - `offloaded_layers < total_layers` 일 경우 `VramOverflowError` 예외 발생.

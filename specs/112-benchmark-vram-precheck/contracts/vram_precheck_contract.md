# CLI & Internal Function Contract: VRAM 사전 검증 인터페이스

**Feature Directory**: `specs/112-benchmark-vram-precheck`

---

## 1. Python Utility API Contract

### Function Signature: `check_vram_feasibility`

```python
def check_vram_feasibility(
    model_id: str,
    file_size_bytes: int | None = None,
    n_ctx: int = 4096,
    ignore_vram_check: bool = False
) -> VRAMPrecheckResult:
    """
    대상 모델의 VRAM 요구량을 사전 산출하여 physical GPU VRAM 수용 여부를 판정합니다.

    Args:
        model_id (str): 모델 ID (예: 'gemma4-26b-a4b')
        file_size_bytes (int, optional): 가중치 파일 용량(바이트). 미지정 시 카탈로그에서 추정.
        n_ctx (int): Context Window 크기 (기본값 4096).
        ignore_vram_check (bool): VRAM 검사 우회 여부 (기본값 False).

    Returns:
        VRAMPrecheckResult: VRAM 수용 적합성 판정 객체.
    """
```

---

## 2. CLI Flags & Options

### `scripts/benchmark_quality.py`

| Flag | Value Type | Description |
|------|------------|-------------|
| `--auto-download` | NONE | 모델 미존재 시 HuggingFace 자동 다운로드 수행 |
| `--real` | NONE | 실체적 벤치마크 및 모델 서빙 구동 |
| `--ignore-vram-check` | NONE | 사전 VRAM 용량 검증 및 자동 스킵 동작을 강제 우회 |

### `scripts/model_downloader.py`

| Flag | Value Type | Description |
|------|------------|-------------|
| `--ignore-vram-check` | NONE | 사전 VRAM 용량 검증 및 자동 스킵 동작을 강제 우회 |

---

## 3. Log Output Format Contract

### Pre-download Skip Warning:
```text
[ModelDownloader] gemma4-26b-a4b: ⚠️ [SKIP VRAM OOM Risk] 예상 VRAM 사용량(19952MB)이 물리 GPU VRAM(11264MB)을 초과하므로 다운로드를 사전 스킵합니다.
```

### Pre-serve Skip Warning (Local File):
```text
[ProcessManager] gemma4-26b-a4b: ⚠️ [SKIP VRAM OOM Risk] 로컬 가중치가 존재하지만 예상 VRAM 사용량(19952MB)이 물리 GPU VRAM(11264MB)을 초과하므로 서빙 개설을 사전 스킵합니다.
```

### Summary Table Contract:
```text
================================================================================
📊 [VRAM SUMMARY] 벤치마크 전수 VRAM 수용 적합성 평가 요약 (GPU: GTX 1080 Ti / 11264MB)
================================================================================
  - Qwen 2.5 7B Instruct (qwen2.5-7b): 7450MB / 11264MB -> ✅ PASS
  - Gemma 4 26B Instruct (gemma4-26b-a4b): 19952MB / 11264MB -> ❌ SKIP (VRAM 초과)
  - Qwen 3.6 27B Instruct (qwen3.6-27b): 20480MB / 11264MB -> ❌ SKIP (VRAM 초과)
--------------------------------------------------------------------------------
요약: 총 14개 모델 중 12개 PASS, 2개 SKIP 예정
================================================================================
```

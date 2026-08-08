# Quickstart Validation Guide: Qwen 3.5 9B 멀티모달 모델 검증 및 카탈로그 등록

## 연관 문서
- [Feature Specification](file:///home/dev/storage/vllm_serv/specs/119-qwen35-multimodal-model/spec.md)
- [Data Model](file:///home/dev/storage/vllm_serv/specs/119-qwen35-multimodal-model/data-model.md)
- [Model Catalog Contract](file:///home/dev/storage/vllm_serv/specs/119-qwen35-multimodal-model/contracts/model_catalog_contract.md)

---

## 1. 사전 조건 (Prerequisites)

- Python 3.10+ 및 `uv` 패키지 매니저
- 저장소 루트 경로: `/home/dev/storage/vllm_serv`

---

## 2. 검증 절차 (Validation Steps)

### 검증 1: 카탈로그 JSON 구조 및 파싱 무결성 검증

`config/model_catalog.json`에 `qwen3.5-9b-vision` 신규 엔트리가 정확히 등록되었고, 기존 `qwen3.5-9b` 텍스트 모델 항목이 보존되었는지 검증합니다.

```bash
uv run python -c '
import json
with open("config/model_catalog.json") as f:
    catalog = json.load(f)

assert "qwen3.5-9b" in catalog, "기존 qwen3.5-9b 항목이 보존되어야 합니다."
assert catalog["qwen3.5-9b"]["requires_mmproj"] is False, "기존 항목은 텍스트 전용이어야 합니다."

assert "qwen3.5-9b-vision" in catalog, "신규 qwen3.5-9b-vision 항목이 존재해야 합니다."
v_item = catalog["qwen3.5-9b-vision"]
assert v_item["requires_mmproj"] is True, "신규 비전 항목은 requires_mmproj: true 이어야 합니다."
assert v_item["clip_filename"] == "mmproj-BF16.gguf", "비전 프로젝터 파일명이 올바라야 합니다."
assert v_item["clip_path"] == "models/qwen3.5-9b-vision/mmproj-BF16.gguf", "비전 프로젝터 경로가 올바라야 합니다."
print("✅ Catalog Validation Success!")
'
```

### 검증 2: 회귀 테스트 수트 실행 (Pytest)

프로젝트 내 전체 단위/통합 테스트 수트를 실행하여 기존 회귀 테스트가 100% 통과하는지 검증합니다.

```bash
uv run pytest
```

### 검증 3: 모델 다운로드 및 동기화 스크립트 파싱 검증

`scripts/ensure_models.py`가 `qwen3.5-9b-vision` 모델 파싱 시 `mmproj` 비전 프로젝터 가중치를 정상 인식하는지 드라이런 검증합니다.

```bash
uv run python scripts/ensure_models.py --model qwen3.5-9b-vision --dry-run
```

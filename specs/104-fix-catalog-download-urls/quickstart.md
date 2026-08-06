# Quickstart Validation Guide: `config/model_catalog.json` HF 다운로드 URL 원인 분석, 리팩토링 및 404 오류 수렴 검증 (104-fix-catalog-download-urls)

본 가이드는 `config/model_catalog.json` 내 14개 모델의 HuggingFace Hub 다운로드 URL이 404 Client Error 없이 정상 동작하는지 실측 검증하는 시나리오를 제공합니다.

---

## 1. Prerequisites

- Python 3.12 / `uv` 가상환경
- 인터넷 연결 (HuggingFace Hub HEAD/GET API 호출용)

---

## 2. Validation Scenarios

### Scenario A: 14개 전체 카탈로그 모델 HF Hub HEAD 200 OK 실측 검증
단위 테스트 수트를 가동하여 14개 카탈로그 모델의 URL이 모두 200 OK인지 검증합니다:

```bash
uv run pytest tests/unit/test_model_downloader.py -k test_model_catalog_hf_urls_valid
```
- **Expected Outcome**: 404 에러 0건, 테스트 100% Pass.

---

### Scenario B: `ensure_models.py` CLI 인자 검사 검증

```bash
# 점검 전용 검사
uv run scripts/ensure_models.py --all --check-only
```
- **Expected Outcome**: 404 실패 예외 없이 14개 카탈로그 모델 존재 유무가 깨끗하게 리포트됨.

---

### Scenario C: 전체 단위 테스트 수트 회귀 검증

```bash
uv run pytest tests/unit/
```
- **Expected Outcome**: 모든 단위 테스트 수트 100% Pass.

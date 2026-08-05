# Quickstart Validation Guide: `scripts/ensure_models.py` 전체/특정 모델 다운로드 CLI 옵션 확장 (102-catalog-full-download-cli)

본 가이드는 `scripts/ensure_models.py`에 새롭게 추가된 `--all` 및 `--model <MODEL_ID>` CLI 옵션의 작동 정합성을 실측 검증하는 시나리오를 제공합니다.

---

## 1. Prerequisites

- Python 3.12+ 및 `uv` 패키지 관리자 환경 (`uv run` 호환)
- 프로젝트 최상위 디렉토리 `/home/dev/storage/vllm_serv`

---

## 2. Validation Scenarios

### Scenario A: 카탈로그 전체 14개 모델 일괄 점검 리포트 (`--all --check-only`)

카탈로그에 등록된 전체 14개 모델의 로컬 존재 상태가 리포트되는지 확인합니다.

```bash
uv run scripts/ensure_models.py --all --check-only
```

- **Expected Output**:
  - `📦 vllm_serv 동적 필수 GGUF 모델 가중치 자동 점검 및 다운로드 파이프라인 (Target: 14 models)` 메시지 출력.
  - 카탈로그 내 14개 모델 식별자(`gemma4-e2b`, `qwen3.6-27b`, `gemma4-26b-a4b` 등)의 존재 여부 리포트 100% 표시.

---

### Scenario B: 특정 지정 모델 핀포인트 점검 리포트 (`--model qwen3.6-27b --check-only`)

지정한 특정 모델 1종만 핀포인트 점검되는지 확인합니다.

```bash
uv run scripts/ensure_models.py --model qwen3.6-27b --check-only
```

- **Expected Output**:
  - `qwen3.6-27b` 단일 모델의 존재 상태만 화면에 리포트됨.

---

### Scenario C: 옵션 상호 배타성 인자 에러 검증 (`--all` & `--model` 동시 지정)

`--all`과 `--model`이 동시 지정될 때 상호 배타적 에러 메시지와 함께 Exit Code 2로 즉시 종료되는지 검증합니다.

```bash
uv run scripts/ensure_models.py --all --model qwen3.6-27b
echo "Exit Code: $?"
```

- **Expected Output**:
  - `[ERROR] --all and --model options are mutually exclusive.` 메시지 출력.
  - `Exit Code: 2` 확인.

---

### Scenario D: 무효한 모델 ID 지정 시 에러 검증 (`--model invalid-model-xyz`)

카탈로그에 없는 무효한 모델 ID 지정 시 Exit Code 1로 즉시 차단되는지 검증합니다.

```bash
uv run scripts/ensure_models.py --model invalid-model-xyz
echo "Exit Code: $?"
```

- **Expected Output**:
  - `[ERROR] Unknown model_id: invalid-model-xyz` 메시지 출력.
  - `Exit Code: 1` 확인.

---

### Scenario E: 기본 인자 하위 호환성 검증 (`uv run scripts/ensure_models.py`)

인자 없이 구동할 때 기존 서빙/임베딩/리랭커 동적 필수 모델 점검이 정상 구동되는지 검증합니다.

```bash
uv run scripts/ensure_models.py --check-only
```

- **Expected Output**:
  - 기존 동적 필수 3종 모델 리포트 및 `✓ [PROVISIONING COMPLETE]` 메시지 정상 출력.

---

## 3. Unit Test Verification

단위 테스트 수트를 가동하여 CLI 옵션 해석 및 예외 처리를 자동 검증합니다:

```bash
uv run pytest tests/unit/test_ensure_models_cli.py
```

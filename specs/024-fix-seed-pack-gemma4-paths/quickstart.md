# Quickstart & Validation Guide: 코드베이스 전체 모델 경로 하드코딩 제거 및 Gemma 4 카탈로그 정합성 보장

**Feature Branch**: `024-fix-seed-pack-gemma4-paths`
**Date**: 2026-07-30
**Spec Reference**: [spec.md](file:///home/dev/storage/vllm_serv/specs/024-fix-seed-pack-gemma4-paths/spec.md) | [plan.md](file:///home/dev/storage/vllm_serv/specs/024-fix-seed-pack-gemma4-paths/plan.md)

---

## 1. 개요 (Overview)

본 문서는 하드코딩 교정 및 `ConfigManager` SSOT 일원화 작업 후, 전체 시스템의 정합성을 검증하기 위한 샐러드/엔드투엔드 검증 시나리오 가이드입니다.

---

## 2. 사전 준비 및 필수 환경 (Prerequisites)

- Python 가상환경 패키지 매니저 `uv`가 설치되어 있어야 합니다.
- 프로젝트 루트 디렉토리 `/home/dev/storage/vllm_serv`에서 실행합니다.

---

## 3. 검증 실행 절차 (Validation Execution Steps)

### Step 1: 단위 및 통합 테스트 실행 (Unit & Integration Tests)

하드코딩 제거 및 `ConfigManager` SSOT 연동 테스트 수트를 실행하여 전체 100% 통과를 확인합니다.

```bash
uv run pytest tests/unit/ -v
uv run pytest tests/integration/ -v
```

**기대 결과 (Expected Outcome)**:
- 모든 `test_config_manager.py`, `test_model_downloader.py`, `test_gemma4_serving.py` 테스트가 에러 없이 PASS 해야 합니다.

---

### Step 2: 모델 다운로드 스크립트 실행 검증 (Model Downloader Test)

```bash
uv run python src/scripts/download_models.py
```

**기대 결과 (Expected Outcome)**:
- `HF_TOKEN` 미설정 시에도 경고 없이 Hugging Face Public Repository(`lmstudio-community/gemma-4-E2B-it-GGUF` 등)로부터 정상 조회가 수행되거나 이미 존재하는 경우 성공 로그를 출력해야 합니다. 404 Not Found 에러가 단 1건도 없어야 합니다.

---

### Step 3: 원스톱 품질/실측 벤치마크 스크립트 검증 (Quality Benchmark Test)

```bash
uv run python scripts/benchmark_quality.py
```

**기대 결과 (Expected Outcome)**:
- `ConfigManager` 카탈로그 명세를 읽어 정적 프로파일링 또는 라이브 벤치마크 모드로 6개 모델 리포트 생성을 오류 없이 완료해야 합니다.

---

### Step 4: 소스코드 하드코딩 잔재 전수 검사 (Codebase Hardcoding Audit)

```bash
grep -rn "gemma4-2b" src/ scripts/
```

**기대 결과 (Expected Outcome)**:
- Legacy alias 테스트 코드를 제외하고 `src/core/config.py` 및 파이썬 스크립트 내에 하드코딩된 `gemma4-2b` 키나 `google/gemma-4-...` 잘못된 Repo ID 참조가 0건이어야 합니다.

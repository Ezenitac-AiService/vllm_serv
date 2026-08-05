# Quickstart & Validation Guide: 101-add-qwen-heavy-models-catalog

## 1. 개요 및 사전 조건 (Prerequisites)

본 가이드는 Qwen 3.6 (27B, 35B MoE) 및 Gemma 4 (26B A4B MoE, 2B/4B/12B 텍스트 전용) 모델 6종이 `config/model_catalog.json`에 정상 통합되고, `./setup.sh --force-benchmark` 구동 시 11GB VRAM 환경에서 해당 대형 모델들이 안전하게 배제(`is_supported: false`)되며 파이프라인이 정상 완납되는지 검증하는 절차를 다룹니다.

---

## 2. 검증 시나리오 및 명령 (Validation Commands)

### Step 1: 카탈로그 스키마 및 무결성 단위 테스트 검증
```bash
uv run pytest tests/unit/test_model_downloader.py tests/unit/test_seed_pack_legacy.py
```
**기대 결과**: 카탈로그 로더 및 다운로더 단위 테스트 100% Pass.

---

### Step 2: 벤치마크 모델 평가 동적 로드 검증
```bash
uv run python -c "from scripts.benchmark_context_window import get_candidate_llm_models; print('Candidate Models:', len(get_candidate_llm_models()))"
```
**기대 결과**: `Candidate Models: 12` (LLM 후보 모델 12개 출력).

---

### Step 3: setup.sh 파이프라인 대형 모델 안전 배제 실측 구동
```bash
./setup.sh --force-benchmark
```
**기대 결과**:
1. `qwen3.6-27b`, `qwen3.6-35b-a3b`, `gemma4-26b-a4b` 3개 대형 모델이 Pre-flight VRAM 차단으로 `is_supported: false` 및 `CUDA OOM Risk` 사유가 `config/model_context_profiles.json`에 기록됨.
2. 서빙 가능 최적 모델(예: `qwen3.5-4b`)이 자동 선택되어 `config/server_config.json`에 업데이트됨.
3. `./setup.sh` 파이프라인 정상 종료 (Exit Code 0).

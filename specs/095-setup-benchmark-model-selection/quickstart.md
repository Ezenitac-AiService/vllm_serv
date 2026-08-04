# Quickstart Validation Guide: `setup.sh` 4단계 모듈화 벤치마크 파이프라인 (`095-setup-benchmark-model-selection`)

**Feature**: [`spec.md`](file:///home/dev/storage/vllm_serv/specs/095-setup-benchmark-model-selection/spec.md)  
**Date**: 2026-08-04

---

## 🚀 실측 검증 시나리오

### 시나리오 1: 단위 테스트 수트 전체 검증
`uv run pytest tests/unit/test_setup_benchmark_integration.py`를 가동하여 4단계 모듈화 파이프라인 연동, 실측 컨텍스트 윈도우 계산, `--skip-benchmark` 플래그 및 `config/server_config.json` 원자적 업데이트 기능을 검증합니다.

```bash
uv run pytest tests/unit/test_setup_benchmark_integration.py -v
```
**기대 결과**: 5개 이상의 단위 테스트 수트 100% PASSED 통과.

---

### 시나리오 2: `setup.sh` 실행 시 Step 2.8 4단계 모듈 연동 실측
`./setup.sh` 구동 후 Step 2.8 단계에서 4단계 파이프라인이 정상 출력되는지 검증합니다.

```bash
./setup.sh
```
**기대 결과**:
1. Stage 1 (모델 다운로드) 및 Stage 2 (무결성 검증) 성공 로그 출력.
2. Stage 3 (임시 서빙 & 컨텍스트 윈도우 벤치마크) 수행 후 VRAM/TPS 측정.
3. Stage 4 (최적 서빙 모델 및 컨텍스트 크기 저장) 완료 후 `config/server_config.json` 업데이트 확인.

---

### 시나리오 3: `--skip-benchmark` 플래그 고속 셋업 검증
`./setup.sh --skip-benchmark` 옵션을 전달하여 Stage 3 벤치마크가 스킵되고 15초 이내 완료되는지 검증합니다.

```bash
./setup.sh --skip-benchmark
```
**기대 결과**: `[SETUP INFO] ⏩ --skip-benchmark 옵션 감지: 3단계 실측 벤치마크를 스킵합니다.` 로그와 함께 15초 이내 고속 완료.

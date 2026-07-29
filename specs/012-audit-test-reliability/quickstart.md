# Quickstart Validation Guide: Codebase Structural Audit & Real-world Test Reliability

**Feature**: Codebase Structural Audit & Real-world Test Reliability Verification (`012-audit-test-reliability`)

## Overview

본 가이드는 단위/통합 테스트 수트(`pytest`)와 실제 실측 런타임 벤치마크(`scripts/benchmark_quality.py`) 간 정합성을 검증하고 100% 무장애 완주를 입증하기 위한 검증 시나리오 문서이다.

---

## 1. Prerequisites (전제 조건)

- Python 3.12 Virtual Environment (`vllm-serv`) 활성화
- NVIDIA GeForce GTX 1080 Ti (11GB VRAM) GPU 장비 및 Driver 580.173.02 확인
- 로컬 GGUF 모델 가중치 준비 (`models/` 디렉토리)

```bash
# 가상환경 확인
uv run python --version
# Expected: Python 3.12.3

# GPU 및 CUDA 상태 확인
nvidia-smi
```

---

## 2. Validation Scenarios (검증 시나리오)

### Scenario 1: 전체 단위 및 통합 테스트 수트 검증 (Zero Teardown Leak)

74개 전체 단위 및 통합 테스트 수트를 구동하여 100% 통과 및 잔여 백그라운드 태스크 0건을 검증한다.

```bash
uv run pytest
```
- **Expected Outcome**: `74 passed in ~7.6s`, 에러 및 잔여 태스크 0개

---

### Scenario 2: 6개 모델 실측 GPU 벤치마크 연속 무중단 실행 (Real-world Execution)

자동 다운로드 및 실측 GPU 추론 벤치마크 스크립트를 구동하여 6개 카탈로그 모델 교체 완주를 검증한다.

```bash
uv run python scripts/benchmark_quality.py --auto-download --real
```
- **Expected Outcome**:
  - `[Step 2] llama-server 프로세스 개설 중...`
  - `[Step 3] ✅ 서빙 READY (/health JSON API 확인)`
  - `[Step 4] ✅ 추론 완료`
  - `[Step 6] ✅ VRAM 해제 완료`
  - 6개 모델 순차 완주 및 `[Post-Benchmark] ✅ 기본 모델 qwen3.5-4b VRAM 복원 완료` 출력
  - `PortCollisionError`, `DeprecationWarning`, `RuntimeError` 0건

---

### Scenario 3: nvtop 실시간 GPU VRAM 100% 오프로드 검증

별도 터미널 창에서 `nvtop`을 실행하여 벤치마크 구동 시 GPU VRAM 점유 및 해제를 모니터링한다.

```bash
nvtop
```
- **Expected Outcome**:
  - `llama-server` 또는 `python` 프로세스가 GPU 0에 할당되어 ~2.5GB~9.8GB VRAM 실시간 점유 확인
  - 모델 전환 간 VRAM 메모리가 즉시 해제(Drain)되는 것을 확인

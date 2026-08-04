# Implementation Plan: `setup.sh` 4단계 모듈화 벤치마크 파이프라인 연동 (`095-setup-benchmark-model-selection`)

**Branch**: `095-setup-benchmark-model-selection`  
**Feature Spec**: [`spec.md`](file:///home/dev/storage/vllm_serv/specs/095-setup-benchmark-model-selection/spec.md)  
**Created**: 2026-08-04

---

## Technical Context & Architectural Summary

`setup.sh` 구동 흐름 중 기존 모놀리식 스크립트 무조건 실행 방식을 대신하여 **4단계 모듈화 파이프라인 (Step 2.8)**을 수립합니다.
- **Stage 1 (모델 다운로드)**: `scripts/ensure_models.py`
- **Stage 2 (무결성 검증)**: GGUF 헤더 및 파일 무결성 체크
- **Stage 3 (임시 서빙 & 컨텍스트 윈도우 벤치마크)**: 신규 파이썬 전용 모듈 `scripts/benchmark_context_window.py`
- **Stage 4 (선정 & 설정 반영)**: `config/server_config.json` 원자적 반영

---

## Constitution Check

- **Principle I (Hardware Realism)**: ✅ **PASSED** (실측 GPU VRAM 및 TPS 벤치마크 기반 컨텍스트 선정)
- **Principle II (Strict Verification)**: ✅ **PASSED** (단위 테스트 수트 100% 검증)
- **Principle V (Script & CLI Quality)**: ✅ **PASSED** (`setup.sh` Step 2.8 모듈화 연동)

---

## Proposed Touch-points & File Modifications

1. `scripts/benchmark_context_window.py` (NEW): Stage 2 무결성 검증, Stage 3 임시 서빙 컨텍스트 윈도우(2K~16K) VRAM/TPS 측정 및 Stage 4 설정 반영 모듈 구현
2. `scripts/setup.sh` (EDIT): Step 2.8 4단계 모듈화 파이프라인 연동 및 `--skip-benchmark` 플래그 처리
3. `src/core/config_manager.py` (EDIT): `auto_benchmark_profile` 설정 원자적 업데이트 지원
4. `tests/unit/test_setup_benchmark_integration.py` (NEW): 4단계 파이프라인 및 설정 반영 단위/통합 테스트 수트

---

## Design Artifact Links

- **Research**: [`research.md`](file:///home/dev/storage/vllm_serv/specs/095-setup-benchmark-model-selection/research.md)
- **Data Model**: [`data-model.md`](file:///home/dev/storage/vllm_serv/specs/095-setup-benchmark-model-selection/data-model.md)
- **Contract Schema**: [`contracts/setup_benchmark_contract.json`](file:///home/dev/storage/vllm_serv/specs/095-setup-benchmark-model-selection/contracts/setup_benchmark_contract.json)
- **Quickstart Guide**: [`quickstart.md`](file:///home/dev/storage/vllm_serv/specs/095-setup-benchmark-model-selection/quickstart.md)

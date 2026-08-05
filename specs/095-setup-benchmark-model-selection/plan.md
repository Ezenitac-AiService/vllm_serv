# Implementation Plan: `setup.sh` 4단계 모듈화 벤치마크 파이프라인 연동 및 하드코딩 제거·이진 탐색 정밀 프로파일링 리팩토링 (`095-setup-benchmark-model-selection`)

**Branch**: `095-setup-benchmark-model-selection`  
**Feature Spec**: [`spec.md`](file:///home/dev/storage/vllm_serv/specs/095-setup-benchmark-model-selection/spec.md)  
**Created**: 2026-08-04 | **Last Amended**: 2026-08-05

---

## Technical Context & Architectural Summary

`setup.sh` 환경 구성 시 기존 모놀리식 벤치마크 호출 방식과 하드코딩·목업 의존 로직을 철저히 제거하고, **4단계 모듈화 파이프라인 (Step 2.8)** 및 **2단계 이진 탐색 정밀 프로파일링 모드 (`--fine-grained`)**를 수립합니다.

### 1. 4단계 모듈화 셋업 파이프라인 (Step 2.8)
- **Stage 1 (모델 다운로드)**: `scripts/ensure_models.py` (HF Hub GGUF 가중치 안전 fetch)
- **Stage 2 (무결성 검증)**: `scripts/benchmark_context_window.py` 내 `verify_model_integrity()` (GGUF magic bytes `GGUF` 4바이트 헤더 및 파일 크기 실체적 체크)
- **Stage 3 (임시 서빙 & 컨텍스트 윈도우 벤치마크)**:
  - **Pass 1 (기본 셋업 Fast Scan)**: 2배 간격(2048, 4096, 8192, 16384, 32768) 스캔으로 빠르게 VRAM 90% 한계치 $C_{pass}$ 산출
  - **Pass 2 (정밀 모드 `--fine-grained`)**: 1차 2배 스케일링으로 감지된 $[C_{pass}, C_{fail}]$ 구간(예: 8K~16K)에 대해 **이진 탐색(Binary Search, 512/1024 토큰 블록 얼라인먼트 & RoPE Cap `min(physical_max, model_max_rope)`)**을 수행하여 3회 이하 최소 실행으로 정밀 최적 수용 크기(예: 12288, 14336)에 수렴
- **Stage 4 (선정 & 설정 원자적 반영)**:
  - `ConfigManager.save_server_config()`를 통해 `config/server_config.json` 및 `config/model_context_profiles.json`에 원자적(`os.replace` + `chmod 0600`) 저장

### 2. 하드코딩 & 목업 제거 리팩토링 (FR-006)
- `scripts/benchmark_quality.py` 및 `scripts/benchmark_context_window.py` 내 정적 베이스라인 상수(`baselines` 딕셔너리 수치), 추정 비율 계산(`* 0.2` TTFT), 회피성 목업 로직을 전면 정단
- VRAM 스냅샷 측정 전 1회 웜업(Warmup) 추론을 우선 수행하여 Lazy Allocation에 의한 과소 수치 판정을 방지하는 실제 NVML GPU 텔레메트리(`get_nvml_vram_info()`) 및 HTTP/SSE 스트리밍 기반 실측 TTFT/TPOT 수집 로직으로 완전 전환

---

## Constitution Check

- **Principle I (Language Policy)**: ✅ **PASSED** (사용자 출력 및 보고서는 한국어, 내부 생각/사유는 영어 유지)
- **Principle II (Strict Real Verification & Zero Mock)**: ✅ **PASSED** (Stage 2 `verify_model_integrity` 실측 호출 및 하드코딩/가짜 통과 전면 금지)
- **Principle III (Parameterized Converge Validation)**: ✅ **PASSED** (`--skip-benchmark` 및 `--fine-grained` 실측 제어 플래그 지원)
- **Principle IV (Definition of Done)**: ✅ **PASSED** (DoD-001 ~ DoD-004 객관적 단정문 수립)
- **Principle V (Non-Destructive Documentation Edit)**: ✅ **PASSED** (기존 이력 및 스펙맥락 선택적 개정)
- **Principle VI (uv Environment & Package Management)**: ✅ **PASSED** (`uv run pytest` 및 `uv` 표준 격리 실행)
- **Principle VII (Mandatory Regression Testing)**: ✅ **PASSED** (전체 회귀 테스트 및 E2E 브라우저 검증 연동)

---

## Proposed Touch-points & File Modifications

1. **`scripts/benchmark_context_window.py` (EDIT/ENHANCE)**:
   - Stage 2 `verify_model_integrity()` 함수 실체적 호출 연동 (GGUF magic bytes 검증)
   - `--skip-benchmark` 시 `ConfigManager`의 기존 `context_window` 보존 로직 적용
   - `--fine-grained` 플래그 도입: 1차 2배 스케일링 후 $[C_{pass}, C_{fail}]$ 구간 1024 해상도 이진 탐색(Binary Search) 엔진 구현
   - 벤치마크 수행 예외/OOM 발생 시 `[BENCHMARK WARN]` 폴백 프로파일(`qwen3.5-4b`, `4096`) 적용

2. **`scripts/benchmark_quality.py` (EDIT/REFACTOR)**:
   - 하드코딩된 베이스라인 상수(`baselines`) 및 정적 비율 계산(`* 0.2`) 제거
   - NVML GPU 실시간 VRAM 스냅샷 및 SSE 스트리밍 기반 실측 TTFT/TPOT 텔레메트리 추출 전환
   - 정밀 이진 탐색 결과를 `config/model_context_profiles.json` 및 `data/reports/analysis_report_quality.md`에 반영

3. **`scripts/setup.sh` 및 연동 하위 스크립트 모듈 (EDIT/REFACTOR)** (FR-008):
   - `scripts/setup.sh`: Step 2.8에 `--skip-benchmark` 시 `scripts/benchmark_context_window.py --skip-benchmark` 전달 연동, 4단계 파이프라인(Stage 1~4) 및 정밀 모드 구동 로그 개선
   - `scripts/ensure_models.py`, `scripts/start_server.sh`, `scripts/stop_server.sh`, `scripts/status_server.sh`: 경로 분기 및 예외 처리 전면 폴리싱

4. **불용/만료 파일 정리 및 아카이빙** (FR-009):
   - 용도가 다한 임시 스크립트, 레거시 더미 파일 탐지 및 정돈

5. **`src/core/config_manager.py` (EDIT)**:
   - `auto_benchmark_profile` 및 `model_context_profiles` 원자적 저장 및 캐시 무효화 메소드 보완

5. **`tests/unit/test_setup_benchmark_integration.py` (EDIT/EXPAND)**:
   - Stage 2 실체적 `verify_model_integrity` 검증 테스트
   - `--skip-benchmark` CLI 플래그 호출, 기존 설정 보존 및 15초 이내 완수(`elapsed < 15.0`) assertion 테스트
   - `--fine-grained` 1024 해상도 이진 탐색 동작 검증 테스트

6. **`README.md` (EDIT)**:
   - Step 2.8 4단계 모듈식 셋업 파이프라인 흐름도 및 설명 반영
   - `--skip-benchmark` 및 `--fine-grained` CLI 사용법 수록
   - 3개 호스트 플랫폼(8GB / 11GB / 12GB VRAM) 벤치마크 프로파일 결과 요약 반영

---

## Design Artifact Links

- **Research & Decisions**: [`research.md`](file:///home/dev/storage/vllm_serv/specs/095-setup-benchmark-model-selection/research.md)
- **Data Model**: [`data-model.md`](file:///home/dev/storage/vllm_serv/specs/095-setup-benchmark-model-selection/data-model.md)
- **Contract Schema**: [`contracts/setup_benchmark_contract.json`](file:///home/dev/storage/vllm_serv/specs/095-setup-benchmark-model-selection/contracts/setup_benchmark_contract.json)
- **Quickstart Guide**: [`quickstart.md`](file:///home/dev/storage/vllm_serv/specs/095-setup-benchmark-model-selection/quickstart.md)

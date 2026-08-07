# Phase 0 Research: 컨텍스트 윈도우 크기 벤치마킹 고도화 및 헬스체크/초기화 진단 개선 (105-enhance-context-window-benchmark)

## Executive Summary

본 연구 문서에서는 11GB VRAM (GTX 1080 Ti) 환경에서 소형 및 중형 LLM 모델의 가용 컨텍스트 윈도우 크기(8192 ~ 16384)를 정확하게 탐색하지 못하고 `4096` 상한선에 강제 조기 종료되거나 헬스체크 타임아웃 오탐이 발생하는 구조적 원인을 해결하기 위한 아키텍처 및 알고리즘 방안을 다룹니다.

---

## Key Research Findings & Decisions

### 1. 헬스체크 타임아웃 적응형 동적 확대 (`poll_server_health`)

- **Decision**: `poll_server_health`의 폴링 타임아웃을 단일 15~30초 고정이 아닌, `n_ctx` 할당 크기와 모델 파일 크기(MB)에 기반하여 동적으로 확장하도록 개선합니다.
  - Formula: `dynamic_timeout = max(30.0, min(60.0, 15.0 + (file_size_mb / 500.0) * 5.0 + (n_ctx / 4096.0) * 10.0))`
- **Rationale**: `n_ctx`가 4096에서 7168, 10240, 16384로 증가함에 따라 CUDA KV 캐시 텐서 메모리 할당 및 `llama-server` 초기화에 15~30초 이상의 시간이 소요됩니다. 60초까지 비례 확장하여 억울한 타임아웃 오탐을 방지합니다.
- **Alternatives Considered**: 
  - 고정 120초 타임아웃: 이진 탐색 중 실제 붕괴/OOM 발생 시 전체 벤치마크 수행 시간이 지나치게 지연되므로 기각.

### 2. 이진 탐색 상한선 (`max_n_ctx`) 해제 및 탐색 정밀도 향상

- **Decision**: `scripts/benchmark_context_window.py` 내 `model_max_rope` 연산 시 `default_n_ctx` (4096) 캡을 제거하고 `max_n_ctx` (기본 16384)를 적용하며, 탐색 횟수를 5단계(`range(5)`)로 확장합니다.
  - Code Refactoring: `model_max_rope = model_cfg.get("max_n_ctx", 16384)`
- **Rationale**: 기존 코드는 `default_n_ctx`가 4096인 경우 `low=4096, high=4096`이 되어 상위 컨텍스트 탐색 시도 자체가 차단되었습니다. 상한선을 16384로 풀어 512 토큰 단위 정렬 이진 탐색을 5회 수행함으로써 최적 컨텍스트를 정확하게 탐색합니다.
- **Alternatives Considered**:
  - `model_catalog.json` 전체 모델 `default_n_ctx` 수정: 서빙 기본 설정값과 벤치마크 탐색 상한선 개념이 혼재하므로 스크립트 탐색 상한선 로직을 분리하는 방안을 채택.

### 3. 프로필 캐시 원자적 병합 (Atomic Cache Merge)

- **Decision**: `scripts/benchmark_quality.py`의 `save_context_profiles_cache` 및 `scripts/benchmark_context_window.py`의 프로필 저장소 업데이트 시, 파일 읽기/로드 후 기존 12개 모델 프로필과 원자적으로 병합(Merge)하여 보존합니다.
- **Rationale**: 벤치마크 결과가 비어 있거나 개별 모델 실패 시 `"profiles": {}`로 파일이 초기화되는 버그를 근본 차단합니다.
- **Alternatives Considered**:
  - 저장 전 단순 파일 백업: 백업 파일 관리 복잡도가 증가하므로 원자적 JSON Load -> Dict Update -> Atomic Temp Replace 방식을 채택.

### 4. 벤치마크 추적성 및 예외 캡처 (SIGKILL / Exit 137 / VRAM Threshold)

- **Decision**: VRAM 점유률 92% 초과 검증 외에 서브프로세스 SIGKILL/Exit Code 137 포착 로직을 강화하고, `binary_search_steps` 배열에 각 시도별 `tested_n_ctx`, `real_vram_mb`, `status`, `reason`을 명시 저장합니다.
- **Rationale**: SRE 및 개발자가 대시보드 API (`/api/dashboard/benchmark/profiles`) 또는 CLI를 통해 벤치마크 시도 과정과 실패 원인을 명확하게 진단할 수 있게 됩니다.

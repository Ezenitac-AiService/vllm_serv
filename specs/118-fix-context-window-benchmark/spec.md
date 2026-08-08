# Feature Specification: 마이그레이션 RTX 3060 플랫폼 컨텍스트 윈도우 벤치마크 전수 평가 및 동적 KV 캐시 VRAM 오탐 수정

**Feature Branch**: `118-fix-context-window-benchmark`  
**Created**: 2026-08-08  
**Status**: Draft  
**Input**: User description: "마이그레이션한 3060 플렛폼에서, 컨텍스트 윈도우 벤치마크를 모델 하나만 가지고 하는데? 분석하고 필요하면 스펙 작성"  

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 동적 KV 캐시 추정기(Dynamic KV Cache Estimator)의 모델별 GQA 아키텍처 정밀 반영 (Priority: P1) 🎯 MVP

사용자가 RTX 3060 플랫폼에서 카탈로그에 등록된 다양한 모델(Qwen 2B/4B/9B, Gemma 2B/4B/12B 등)의 컨텍스트 윈도우 스케일링을 측정할 때, 시스템이 각 모델의 실제 GQA(Grouped-Query Attention) 헤더 및 레이어 파라미터(`n_layers`, `n_heads`, `n_head_kv`, `head_dim`)를 반영하여 KV 캐시 VRAM 점유량을 동적으로 계산한다. 이를 통해 하드코딩된 대형 모델 기준 디폴트값(36 layers, 32 heads, 128 dim) 때문에 소형/GQA 모델이 `n_ctx=16384`에서 억울하게 15,216MB VRAM 오탐 계산으로 차단되는 문제를 근본적으로 해결한다.

**Why this priority**: 프로세스 스폰 및 벤치마크 사전 검사 시 모든 모델이 동일한 15.2GB 추정치로 판정되어 16K 이상의 대용량 컨텍스트 윈도우 스케일링 측정이 전면 차단되는 심각한 계산 오탐 결함이기 때문입니다.

**Independent Test**: Qwen 3.5 2B/4B 또는 Gemma 4 2B/4B 모델 대상으로 `estimate_vram_usage(model_id, n_ctx=16384)` 호출 시, 소형/GQA 아키텍처 특성이 반영된 실제 VRAM 사용량이 정확히 계산되어 사전 스폰이 허용되고 `n_ctx=16384` 테스트가 통과되는지 확인합니다.

**Acceptance Scenarios**:

1. **Given** 모델 카탈로그에 Qwen 3.5 2B (`n_layers=24`, `n_heads=16`, `n_head_kv=8`)가 등록되어 있을 때, **When** `n_ctx=16384`에 대한 VRAM 추정을 수행하면, **Then** 하드코딩된 9216MB가 아닌 정밀 계산된 소형 KV 캐시 용량이 산출되어 OOM Risk 차단 없이 프로세스가 스폰된다.
2. **Given** `ProcessManager.spawn_process()`가 가동될 때, **When** 모델 ID가 전달되면, **Then** 모델 카탈로그 또는 GGUF 메타데이터에서 `n_layers`, `n_heads`, `n_head_kv`, `head_dim`을 동적으로 추출하여 `estimate_kv_cache_vram()`에 전달한다.

---

### User Story 2 - 컨텍스트 윈도우 벤치마크 CLI 카탈로그 전수 모델 평가 모드 지원 (Priority: P1) 🎯 MVP

사용자가 `./setup.sh` 2.8단계 또는 CLI 독립 명령어(`benchmark_context_window.py`)를 실행할 때, 기본값 단일 모델(`--model qwen3.5-4b`) 측정에만 국한되지 않고, `--all` 또는 카탈로그 전수 LLM 후보 모델 대상 순차 벤치마킹을 실행할 수 있도록 명확한 평가 옵션과 자동 루프를 제공한다.

**Why this priority**: 마이그레이션된 3060 플랫폼에서 단 한 번의 실행으로 카탈로그에 정의된 모든 가용 LLM 모델의 컨텍스트 스케일링 한계를 실측 프로파일링하고 `config/model_context_profiles.json`을 완성하기 위함입니다.

**Independent Test**: `uv run python scripts/benchmark_context_window.py --fine-grained --all` 실행 시, 카탈로그 내 모든 LLM 모델(Qwen, Gemma 라인업)이 순차적으로 이진 탐색 평가되어 캐시 파일에 기록되는지 확인합니다.

**Acceptance Scenarios**:

1. **Given** 사용자가 `benchmark_context_window.py` CLI를 실행할 때, **When** `--all` 인자를 지정하면, **Then** 카탈로그 내 모든 LLM 후보 모델이 순차적으로 이진 탐색 스케일링 벤치마킹 평가된다.
2. **Given** 사용자가 특정 모델을 지정하고자 할 때, **When** `--model gemma4-e4b` 인자를 전달하면, **Then** 기존과 동일하게 지정된 단일 모델에 대한 핀포인트 벤치마크가 실행된다.

---

### User Story 3 - 품질-컨텍스트 종합 벤치마크(`benchmark_quality.py`) 스케일링 루프 정밀화 (Priority: P2)

사용자가 `benchmark_quality.py` 3D 종합 품질 리포트 생성을 구동할 때, [Step 5.1] 실측 GPU 컨텍스트 스케일링 측정 루프에서도 모델별 동적 KV 캐시 추정이 적용되어 16K 구간의 실제 성능 데이터(VRAM, TTFT, TPOT)가 리포트에 정밀 반영된다.

**Why this priority**: 최종 출력되는 `analysis_report_quality.md` 보고서의 컨텍스트 윈도우 스케일링 테이블에 실제 측정이 완료된 정밀 수치가 수록되도록 보장하기 위함입니다.

**Independent Test**: `uv run python scripts/benchmark_quality.py` 실행 시 [Step 5.1]에서 모든 모델이 15216MB 일률 실패 메시지 없이 모델 스펙에 맞게 16K 구간까지 측정되는지 확인합니다.

**Acceptance Scenarios**:

1. **Given** `benchmark_quality.py`의 [Step 5.1] 스케일링 측정이 실행될 때, **When** 각 모델별 `n_ctx=16384` 구간에 도달하면, **Then** 해당 모델의 실제 KV 캐시 계산에 따라 VRAM 오탐 스폰 실패 없이 측정이 정상 진행된다.

---

### Edge Cases

- **GGUF 파일 미존재 및 카탈로그 정보 미흡**: 모델 파일이 아직 다운로드되지 않았거나 카탈로그에 헤더 상세 정보가 없는 경우, 기본 안전 파라미터(`n_layers=28`, `n_heads=16`, `head_dim=128`)를 폴백으로 사용하되, 무조건 70B급 파라미터를 사용하지 않는다.
- **물리 VRAM 초과 모델 (27B, 35B 등)**: 물리 VRAM(12GB)을 초과하는 대형 모델은 Pre-flight 체크에서 유연하게 감지하여 사전 스킵 처리(SKIP)한다.

---

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `src/core/process_manager.py`의 `spawn_process()` 및 `estimate_vram_usage()`가 모델 카탈로그 및 GGUF 아키텍처 파라미터(`n_layers`, `n_heads`, `n_head_kv`, `head_dim`)를 100% 동적 읽기 연동.
- **DoD-002**: Qwen 3.5 2B/4B 및 Gemma 4 2B/4B 소형/GQA 모델이 `n_ctx=16384`에서 15.2GB 오탐 VRAM 차단 현상 없이 스폰 및 실측 평가 성공.
- **DoD-003**: `scripts/benchmark_context_window.py` CLI 인자에 `--all` 옵션 지원 및 카탈로그 전수 모델 순차 이진 탐색 벤치마크 완료.
- **DoD-004**: `scripts/benchmark_quality.py` [Step 5.1] 스케일링 측정 루프에서 일률적 15216MB 오탐 실패 제거.
- **DoD-005**: 단위 및 회귀 테스트 수트(`tests/unit/`) 100% PASS 통과.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `ProcessManager`는 `spawn_process()` 및 `estimate_vram_usage()` 실행 시 대상 모델의 `n_layers`, `n_heads`, `n_head_kv`, `head_dim` 파라미터를 `ConfigManager` 카탈로그 및 GGUF 헤더에서 동적으로 조회하여 `estimate_kv_cache_vram()`에 전달해야 한다.
- **FR-002**: `estimate_kv_cache_vram()` 함수는 하드코딩된 디폴트값 대신 전달받은 GQA 아키텍처 파라미터(`n_head_kv / n_heads` 비율)를 정확히 반영하여 KV 캐시 VRAM 점유량을 산출해야 한다.
- **FR-003**: `scripts/benchmark_context_window.py`는 `--all` CLI 인자를 신규 추가하여 지정 시 카탈로그 내 모든 후보 LLM 모델을 순차적으로 이진 탐색 평가하고 `config/model_context_profiles.json` 프로파일을 원자적으로 반영해야 한다.
- **FR-004**: `scripts/benchmark_quality.py`의 [Step 5.1] 컨텍스트 스케일링 측정이 `ProcessManager`의 동적 KV 캐시 계산기를 사용하여 16K 구간에서 일률적인 15216MB 오탐 실패를 방지하도록 개선되어야 한다.
- **FR-005**: `tests/unit/test_benchmark_context_window.py` 및 관련 단위 테스트 수트에 모델별 동적 KV 캐시 계산 및 CLI `--all` 평가 옵션에 대한 검증 케이스를 수록해야 한다.

### Key Entities *(data involved)*

- **ModelCatalogEntry**: `n_layers`, `n_heads`, `n_head_kv`, `head_dim`, `max_n_ctx`, `vram_est_mb` 메타데이터 속성 포함.
- **ModelContextProfile**: 모델별 `max_context_length`, `recommended_context_length`, `binary_search_steps`, `peak_vram_mb`, `tpot_tok_per_sec`, `is_supported` 결과 딕셔너리.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Qwen 3.5 2B/4B 및 Gemma 4 2B/4B 모델 실측 평가 시 `n_ctx=16384` 구간에서 오탐 OOM risk 차단 없이 실제 VRAM 용량(2GB~4GB 내외)으로 스폰 및 벤치마크 정상 완료.
- **SC-002**: `uv run python scripts/benchmark_context_window.py --fine-grained --all` 명령으로 카탈로그 내 전체 LLM 모델 순차 평가 및 `config/model_context_profiles.json` 갱신 완성.
- **SC-003**: `uv run pytest tests/unit/` 단위 테스트 수트 100% PASS 달성.

---

## Assumptions

- 대상 시스템은 RTX 3060 12GB VRAM 단일 GPU 및 CUDA 가속 환경에서 작동한다.
- GGUF 가중치 헤더 읽기를 위한 `read_gguf_metadata_architecture` 도구가 `src/core/gpu_detector.py`에 유효하게 준비되어 있다.
- 카탈로그 내 LLM 모델은 `task_type="llm"` 속성을 가지며, 임베딩(`bge-m3`) 및 리랭커(`bge-reranker-v2-m3`) 모델은 대화형 컨텍스트 스케일링 대상에서 제외된다.

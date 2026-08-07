# Feature Specification: 벤치마크 파이프라인 최적 모델 및 컨텍스트 윈도우 동적 선정 로직 정상화 (Fix Benchmark Model & Context Window Selection Logic)

**Feature Branch**: `110-benchmark-model-selection-fix`  
**Created**: 2026-08-07  
**Status**: Approved (2026 Industry Standard Validated)  
**Input**: User description: "/speckit-specify 컨텍스트 윈도우 벤치마크 잘 해놓고, 마지막에 모델과 컨텍스트 윈도우 선정이 왜 저꼴인데? 저거 하드코딩된 값 아냐? 아니면 로직이 이상하던지..."

---

## Clarifications & 2026 Industry Reference Evaluation

### Session 2026-08-07
- Q: 최적 모델 선정을 위한 정렬 및 우선순위 기준 → A: C-B-A 순서 혼합 적용 (1단계: 파라미터 품질 우대 C [`max_context_length >= 8192` 수용 시 대형 모델 우선], 2단계: 복합 점수 B [`Score = TPS * log2(max_context_length / 2048) / VRAM_GB`], 3단계: `max_context_length` 및 TPS 내림차순 A)
- Q: 8k(8192) 컨텍스트 윈도우를 달성하는 모델이 전혀 없을 경우 예외 처리 → A: 8k 이상 모델이 없을 경우 1단계 임계값을 4096 → 2048 순으로 자동 하향(Graceful Fallback)하여 전체 지원 가능 모델 중 2단계(B) 복합 점수 및 3단계(A) 정렬을 정상 평가.

### 2026년 8월 LLM 서빙 엔진 공식 레퍼런스 검토 및 평가 (vLLM / llama.cpp / NVIDIA Guide)
- **vLLM / llama.cpp KV Cache & Context Allocation 표준**: 2026년 최신 LLM 서빙 파이프라인은 고정형 static n_ctx 할당 대신 GPU VRAM 여유율 기반의 동적 이진 탐색 및 안전 마진 캡핑을 준수함. 본 명세의 `FR-001` 및 `FR-003`은 이진 탐색으로 실측된 `recommended_context_length`를 서버 설정에 동적 연동하여 100% 표준을 준수함.
- **다차원 복합 서빙 평가 지표 (Composite Serving Metric)**: 단순히 TPS 단일 지표 또는 디폴트 첫 번째 모델 선택 대신, 파라미터 퀄리티(C), 대용량 컨텍스트 가중 처리량($\text{TPS} \times \log_2(n_{\text{ctx}})$), VRAM 효율성(B)을 3축 종합 평가하는 C-B-A 알고리즘(`FR-002`)을 채택하여 최신 대규모 서빙 클러스터 자동 튜닝 가이드와 완벽 부합함.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 실측 벤치마크 기반 최적 모델 및 dynamic 컨텍스트 윈도우 동적 반영 (Priority: P1) 🎯 MVP

> **As a** LLM 서빙 시스템 관리자  
> **I want to** `./scripts/benchmark_context_window.py --force-benchmark` 실행 시 각 모델별 이진 탐색으로 실측된 최대 컨텍스트 윈도우 크기와 실측 TPS 지표가 Stage 4 최적 서빙 모델 선정 및 서버 설정(`config/server_config.json`)에 정확히 동적 반영되기를 원한다.  
> **So that** 벤치마크에서 16,896, 20,480 등의 대용량 컨텍스트 윈도우 수용 가능성을 성공적으로 탐색해두고도 final stage에서 하드코딩된 4,096이나 배열 첫 번째 모델로 잘못 낙점되는 결함을 예방한다.

**Why this priority**: 이진 탐색 벤치마크의 실측 탐색 결과가 최종 서버 서빙 설정에 온전히 연결되지 않으면 전체 벤치마크 기능의 가치가 상실됨.

**Independent Test**: `python scripts/benchmark_context_window.py --force-benchmark` 구동 후 Stage 4 출력 결과가 실측 탐색된 max context window 값과 정확한 최적 모델 지표를 가리키는지 확인.

**Acceptance Scenarios**:
1. **Given** 12개 후보 모델 실측 벤치마크 구동 시, **When** 특정 모델(예: `qwen3.5-2b` 또는 `gemma4-e2b`)이 20,480 이상의 context window를 검증 성공하면, **Then** Stage 4 최종 설정에 hardcoded `4096` 대신 실측된 `recommended_context_length` / `max_context_length` (예: 20480)가 온전히 저장된다.
2. **Given** 실측 벤치마크 결과 딕셔너리가 생성될 때, **When** 최적 모델 선정 루프가 실행되면, **Then** 딕셔너리 키 불일치(`benchmark_tps` 대신 `tpot_tok_per_sec`, `recommended_context_window` 대신 `recommended_context_length`) 없이 C-B-A 혼합 정렬 알고리즘에 따라 최고 성능 모델이 선택된다.

---

### User Story 2 - 딕셔너리 키 불일치 및 Fallback 하드코딩 결함 교정 (Priority: P2)

> **As a** 시스템 개발자  
> **I want to** 벤치마크 모듈 간 반환 딕셔너리 스키마(`tpot_tok_per_sec`, `max_context_length`, `recommended_context_length`, `peak_vram_mb`)가 단일화되고 Fallback 동률 시 첫 번째 모델 무조건 선택 결함이 개선되기를 원한다.  
> **So that** 모든 벤치마크 서브루틴 및 CLI 모듈이 일과된 데이터 구조를 dereference하여 안전하게 동작한다.

**Why this priority**: 모듈 간 키 매칭 오차 및 동률 처리 미비는 추후 신규 모델 카탈로그 추가 시 예기치 못한 하드코딩 Fallback을 유발함.

**Independent Test**: `tests/unit/test_benchmark_context.py` 수트 실행을 통해 반환 딕셔너리 키의 정합성 및 최적 모델 산출 로직 검증.

**Acceptance Scenarios**:
1. **Given** `evaluate_all_catalog_models` 함수 호출 시, **When** 반환 딕셔너리를 검사하면, **Then** `benchmark_tps` 및 `recommended_context_window` 등의 누락 키 참조 오류가 전혀 발생하지 않는다.

---

## Edge Cases

- **모든 후보 모델이 벤치마크 실패(OOM/미지원)할 경우**: 안전한 기본 Fallback 모델 및 안전 n_ctx(2048)로 예외 처리.
- **8K 이상 컨텍스트 달성 모델이 부재한 VRAM 제한 환경**: 1단계 8K 임계값을 4096 / 2048로 자동 완화(Graceful Fallback)하여 지원 가능한 모델 중 최고 복합 점수 모델을 차선책으로 안전 선택.
- **여러 모델의 TPS 및 지원 상태가 유사할 경우**: C-B-A 혼합 정렬 규칙(1차: 파라미터 퀄리티/n_ctx>=8192 보장 모델, 2차: 복합 점수 Score, 3차: raw n_ctx 및 TPS 내림차순)을 적용하여 특정 모델 고정 선택 현상 전면 방지.

---

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `--force-benchmark` 실행 후 Stage 4에서 이진 탐색으로 실측된 최고 context window 크기와 정확한 TPS 지표가 최적 서빙 모델 및 설정 파일(`config/server_config.json`, `config/model_context_profiles.json`)에 100% 동적 반영.
- **DoD-002**: `benchmark_context_window.py` 내 반환 딕셔너리 키 mismatch (`tpot_tok_per_sec` vs `benchmark_tps`, `recommended_context_length` vs `recommended_context_window`) 및 hardcoded 4096 Fallback 전면 수정 완료.
- **DoD-003**: 관련 단위 및 회귀 테스트 코드 작성 및 `uv run pytest tests/unit/test_benchmark_context.py` 100% Green 통과.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `scripts/benchmark_context_window.py`의 `evaluate_all_catalog_models` 함수는 `run_fine_grained_binary_search` 결과 딕셔너리의 키(`tpot_tok_per_sec`, `recommended_context_length`, `max_context_length`, `peak_vram_mb`)를 정확하게 Dereference하여 TPS 및 n_ctx를 추출해야 한다.
- **FR-002**: 최적 서빙 모델 선정 알고리즘은 **C-B-A 혼합 우선순위 정렬 규칙**을 준수하여 동적으로 모델을 선정해야 한다:
  1. **1단계 (C: 파라미터 품질 우대 & 8K Fallback)**: `max_context_length >= 8192`를 만족하는 지원 가능한 모델 중 대형 파라미터 모델(예: 9B > 4B > 2B)을 1차 우대한다. 만약 8K(8192) 이상을 달성한 모델이 전혀 없으면, 임계값을 4096 → 2048로 자동 하향(Graceful Fallback) 적용한다.
  2. **2단계 (B: 복합 점수 산출)**: 1단계 우대 등급 내 동률 후보 간에는 `Score = TPS * log2(max_context_length / 2048) / (vram_used_mb / 1024)` 공식을 적용하여 점수가 가장 높은 모델을 선택한다.
  3. **3단계 (A: 최대 컨텍스트/TPS 동률 해소)**: 2단계 점수 동률 발생 시 `max_context_length` 내림차순, `tpot_tok_per_sec` 내림차순, `vram_used_mb` 오름차순으로 순서를 결정한다.
- **FR-003**: Stage 4 최종 설정 반영 및 `save_benchmark_profile` 호출 시, 하드코딩된 `4096` 디폴트 Fallback 대신 이진 탐색으로 탐색 완료된 `recommended_context_length` (또는 `max_context_length`) 값을 동적으로 반영해야 한다.
- **FR-004**: 단위 테스트 수트 `tests/unit/test_benchmark_context.py`에 키 스키마 정합성, C-B-A 혼합 정렬 및 8K Fallback 알고리즘 검증, 그리고 `evaluate_all_catalog_models`의 dynamic context window 동적 반영 검증 케이스를 수록해야 한다.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `python scripts/benchmark_context_window.py --force-benchmark` 구동 시 Stage 4 출력 결과가 하드코딩 `4096`이 아닌 실측된 dynamic context window(예: 16896, 20480 등) 및 정밀 탐색 TPS로 100% 정확히 표시되어야 한다.
- **SC-002**: `uv run pytest tests/unit/test_benchmark_context.py` 포함 전체 단위 테스트 수트가 100% Green 통과해야 한다.

---

## Assumptions

- CUDA VRAM 11GB (GTX 1080 Ti 등) 환경에서 2B~4B 모델은 16K~32K 이상의 n_ctx 탐색이 가능하다.
- `model_catalog.json` 내 카탈로그 정의 구조는 변경하지 않으며 벤치마크 동적 산출 로직만 개정한다.

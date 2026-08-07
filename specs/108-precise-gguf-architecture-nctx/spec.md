# Feature Specification: GGUF 모델 메타데이터/카탈로그 파라미터 정밀 추출을 통한 경량 모델 상한선 자동 연산 정밀화 (Precise GGUF Architecture & Uncapped Model Range)

**Feature Identifier**: `108-precise-gguf-architecture-nctx`  
**Created**: 2026-08-07  
**Status**: DRAFT  

---

## Executive Summary & User Value

현재 벤치마크 시스템은 카탈로그 내 개별 모델의 아키텍처 파라미터(`n_layers`, `n_heads`, `head_dim`, `n_head_kv`)가 비어 있는 경우, 7B 표준 LLM 아키텍처 기준 폴백 수치(`n_layers=36`, `n_heads=32`, `head_dim=128`, 0.56 MB/token)를 일률적으로 적용합니다.

이로 인해 `gemma4-e2b` (2B 초경량 모델)와 같은 모델은 11GB VRAM 환경에서 실제 VRAM을 **2.5GB만 점유**함에도 불구하고, 7B 기준 계산식에 의해 사전 상한선이 **`11264`**로 조기 캡핑되는 문제가 발생합니다.

본 기능은 GGUF 모델 파일 헤더 메타데이터 및 `config/model_catalog.json`으로부터 **실제 아키텍처 파라미터를 정밀 추출**하고, VRAM이 여유로운 상태에서 이진 탐색이 멈추지 않도록 **실제 VRAM 여유분 기반 상한선 자동 재확장 로직**을 구현하는 것을 목표로 합니다.

---

## Clarifications

### Session 2026-08-07

- Q: 이진 탐색 상한선 `high` 동적 계산 및 VRAM 여유 시 자동 확장 방식 → A: Option A (GGUF/카탈로그 아키텍처 정밀 파싱 + 상한선 `high` 도달 후 VRAM >50% 여유 시 `high`를 2배씩 동적 자동 재확장하여 32K~128K까지 연장 탐색)
- Q: GGUF 헤더 파싱과 카탈로그 메타데이터 간의 폴백 처리 순서 → A: Option A (카탈로그 JSON 우선 ➔ GGUF 바이너리 헤더 파싱 폴백 ➔ 7B 안전 수식 최종 적용)
- Q: 1M (백만) 토큰 이상 초장문 대응 및 최대 캡 상한선 동적 파싱 정책 → A: Option A (최대 캡 상한선도 하드코딩 상수 `131072`/`1048576`가 아닌 GGUF RoPE 메타데이터/카탈로그 명세로부터 100% 동적 파싱하여 1M~10M까지 무제한 확장하며, 탐색 영역에 따른 가변 스텝(≤32K: 512, ≤128K: 2048, >128K: 16384) 및 KV 캐시 비트수(FP16/FP8/INT4) 수식 반영)

---

## User Stories & Acceptance Criteria

### User Story 1 (P1): GGUF 메타데이터 및 카탈로그 아키텍처 정밀 파싱 🎯 MVP

> **As a** LLM 서빙 관리자  
> **I want to** GGUF 파일 헤더 메타데이터(`block_count`, `head_count`, `head_count_kv`, `key_length`, `context_length`) 또는 카탈로그 파라미터를 정밀 파싱하여 모델별 실제 KV 캐시 크기를 정확히 계산하기를 원한다.  
> **So that** 2B/4B 경량 모델이 7B 폴백 공식에 의해 억울하게 컨텍스트 상한선이 캡핑되는 현상을 방지할 수 있다.

- **Acceptance Criteria 1 (AC 1.1)**: GGUF 파일 헤더 파싱 또는 카탈로그 명세 조회를 통해 `gemma4-e2b` (2B), `gemma4-e4b` (4B), `qwen3.5-2b` 등 개별 모델의 실제 `n_layers`, `n_heads`, `head_dim`, `n_head_kv` 수치 및 무제한 RoPE 컨텍스트 용량을 정확히 추출해야 한다.
- **Acceptance Criteria 2 (AC 1.2)**: 추출된 정밀 아키텍처 파라미터 및 KV 캐시 양자화 타입(FP16/FP8/INT4)을 기반으로 토큰당 KV 캐시 VRAM 크기(MB/token)를 동적 연산해야 한다.

---

### User Story 2 (P1): 가용 VRAM 여유 상태에서의 이진 탐색 구간 자동 재확장 🎯 MVP

> **As a** 시스템 엔지니어  
> **I want to** 이진 탐색 결과 VRAM 사용량이 가용 메모리보다 현저히 낮고(`PASS`), 탐색이 상한선에 도달한 경우 상한선을 모델 RoPE 최대 한계까지 자동으로 재확장하여 탐색하기를 원한다.  
> **So that** 11GB/24GB VRAM 환경에서 경량 모델이 VRAM을 충분히 활용하여 32K~1M 초장문 컨텍스트를 최대한 발굴하도록 보장한다.

- **Acceptance Criteria 1 (AC 2.1)**: 이진 탐색 상한선(`high`)에 도달하여 테스트가 통과(`PASS`)했으나 VRAM 사용량이 가용 VRAM의 50% 미만인 경우, 상한선 `high`를 2배로 확장하거나 모델의 최대 RoPE 한계(`max_n_ctx`)까지 재확장하여 이진 탐색을 연장 수행해야 한다.
- **Acceptance Criteria 2 (AC 2.2)**: `gemma4-e2b` 벤치마크 시 11GB VRAM 환경에서 11264 탐색에 머물지 않고 32768 또는 OOM 발생 시점까지 탐색을 자동 수행해야 한다.

---

### User Story 3 (P2): 카탈로그 명세 내 모델 아키텍처 정밀 파라미터 동기화

> **As a** 개발자  
> **I want to** `config/model_catalog.json` 내 대상 6개 지원 모델에 대해 `n_layers`, `n_heads`, `head_dim`, `n_head_kv` 명세를 사전 명시화하기를 원한다.  
> **So that** GGUF 헤더 파싱 없이도 카탈로그 파일만으로 100% 정밀 VRAM 예측이 가능해야 한다.

- **Acceptance Criteria 1 (AC 3.1)**: `config/model_catalog.json` 내 `gemma4-e2b`, `gemma4-e4b`, `gemma4-12b`, `qwen3.5-2b`, `qwen3.5-4b`, `qwen3.5-9b` 6개 모델에 대한 정확한 아키텍처 파라미터를 기록해야 한다.

---

## Functional Requirements

- **FR-001**: `src/core/gpu_detector.py` 내 `estimate_kv_cache_vram` 및 `calculate_max_allocatable_n_ctx` 함수가 GQA (Grouped Query Attention)의 `n_head_kv` 비율 및 KV 캐시 양자화 타입(FP16/FP8/INT4)을 지원하도록 연산식을 개정한다.
  $$\text{KV\_bytes\_per\_token} = 2 \times n_{\text{layers}} \times n_{\text{head\_kv}} \times head\_dim \times \text{bytes\_per\_elem}$$
- **FR-002**: `scripts/benchmark_context_window.py` 이진 탐색 루프에서, 상한선 `high` 지점 테스트가 `PASS`되고 잔여 VRAM 비율이 50% 이상 남아있을 경우 상한선 `high`를 동적으로 확대(`min(high * 2, model_max_rope)`)하는 구간 자동 재확장 알고리즘을 도입한다.
- **FR-003**: `config/model_catalog.json`에 6개 지원 모델 아키텍처 메타데이터 항목(`n_layers`, `n_heads`, `head_dim`, `n_head_kv`)을 추가 등록한다.
- **FR-004**: 이진 탐색 스텝 단위를 컨텍스트 용량 스케일에 따라 로그 기반 동적 연산식($\text{step} = \max(512, 2^{\lfloor \log_2(high / 64) \rfloor})$)으로 결정하여 하드코딩 매직 넘버 없이 가변 조율한다.
- **FR-005**: 최대 캡 상한선(`max_cap`)을 고정된 숫자(128K/1M)로 하드코딩하지 않고, GGUF RoPE 헤더 메타데이터(`llama.context_length`) 및 모델 명세로부터 100% 동적 파싱하여 1M~10M까지 무제한 확장 대응한다. (Constitution II *Strict Real Verification & Zero Hardcoding* 원칙 100% 준수)

---

## Success Criteria

- **SC-001**: 11GB VRAM 환경에서 `gemma4-e2b` 벤치마크 구동 시, 이전 11264 상한선 조기 캡핑이 해제되고 32768 토큰 또는 OOM 경계선까지 완전 동적 확장 탐색이 수행되어야 한다.
- **SC-002**: VRAM 점유율 50% 미만 상태에서의 조기 탐색 종료 건수가 0건이어야 한다.
- **SC-003**: 백만(1M+) 초장문 컨텍스트 탐색 시 하드코딩 캡핑에 의해 제한되지 않고 GGUF RoPE 상한선까지 자동 확장되어야 한다.
- **SC-004**: 기존 단위 테스트 수트 100% 회귀 통과를 유지해야 한다.

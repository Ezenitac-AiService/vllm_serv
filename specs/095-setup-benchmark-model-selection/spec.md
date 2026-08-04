# Feature Specification: `setup.sh` 4단계 모듈화 파이프라인(다운로드/검증/컨텍스트 윈도우 벤치마크/설정 반영)을 통한 최적 서비스 모델 및 컨텍스트 크기 자동 선정 (`095-setup-benchmark-model-selection`)

**Feature Branch**: `095-setup-benchmark-model-selection`

**Created**: 2026-08-04

**Status**: Draft

**Input**: User description: "setup.sh를 한단계 더 고도화 해야 할것 같아. 스크립트 중에, 벤치마크를 통해, 플렛폼에서 서비스할 모델 선정, 모델의 컨텍스트 윈도우 크기 기준을 선정하는 uv run python scripts/benchmark_quality.py --auto-download --real 이게 setup 과정에 있어야 타당하지 않나? 해당 스크립트를 그냥 호출하지 말고, 기능을 쪼개서, 모델 다운로드하는 로직, 검증하는 로직, 서비스를 시작하고 컨텍스트 윈도우 벤치마크를 통해 서비스할 모델 선정, 컨텍스트 윈도우 크기 결정 -> 설정 파일에 반영 하도록 분해 하는게 나을거 같아"

## Clarifications

### Session 2026-08-04

- Q: setup.sh 내 벤치마크 모듈화 4단계 파이프라인 분해 정책 → A: Option A (다운로드 / 검증 / 임시 서빙 & 컨텍스트 윈도우 벤치마크 / 선정 & 설정 반영 4단계 분해 파이프라인 spec.md 반영)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - `setup.sh` 4단계 모듈화 파이프라인을 통한 서빙 모델 및 컨텍스트 윈도우 자동 선정 (Priority: P1) 🎯 MVP

시스템 관리자 및 AI 엔지니어는 플랫폼 마이그레이션 또는 셋업을 위해 `./setup.sh`를 실행할 때, 통으로 통합된 벤치마크 스크립트를 무작정 호출하는 대신 4가지 명확한 모듈식 단계(1. 모델 다운로드, 2. 파일 무결성 검증, 3. 임시 서빙 가동 및 컨텍스트 윈도우 벤치마크, 4. 서비스 모델 및 컨텍스트 크기 결정 & 설정 반영)로 순차 실행되어 호스트 하드웨어(CPU/GPU/VRAM)에 최적화된 서빙 모델과 컨텍스트 윈도우 기준 크기를 정밀 판정·선정하여 `config/server_config.json`에 반영하기를 원한다.

**Why this priority**: 단순 통 스크립트 실행은 단계별 실패 원인 추적이 어렵고 VRAM 소모 파악이 불투명하므로, 프로비저닝/검증/컨텍스트 실측/설정 반영의 4단계로 분해하여 투명성과 디버깅 용이성을 확보해야 한다.

**Independent Test**: `./setup.sh` 구동 시 4개 모듈식 단계가 순차 호출되고, 3단계 임시 가동 컨텍스트 측정 결과에 따라 `config/server_config.json`에 최적 모델 및 컨텍스트 윈도우 크기가 자동 업데이트되는지 검증.

**Acceptance Scenarios**:

1. **Given** 플랫폼 호스트에서 `./setup.sh`를 실행할 때, **When** 컴파일 환경 준비가 완료되면, **Then** 1단계(모델 다운로드: `ensure_models.py`)와 2단계(GGUF 무결성 검증)가 완수된다.
2. **Given** 모델 무결성 검증이 완료되었을 때, **When** 3단계(임시 서빙 가동 및 컨텍스트 윈도우 벤치마크)가 구동되면, **Then** 후보 모델별 컨텍스트(2K, 4K, 8K, 16K) 단계적 오프셋 실측 VRAM 및 TPS가 측정된다.
3. **Given** 3단계 실측 측정이 완료되었을 때, **When** 4단계(선정 & 설정 반영)가 실행되면, **Then** 결정된 최적 모델과 컨텍스트 윈도우 크기가 `config/server_config.json`에 자동 저장된다.

---

### User Story 2 - 빠른 셋업 및 CI/CD를 위한 벤치마크 스킵 옵션 지원 (Priority: P2)

운영 관리자 및 자동화 파이프라인은 빠른 서버 가동 또는 CI/CD 테스트 환경에서 `./setup.sh --skip-benchmark` 플래그를 사용하여 벤치마크 실행 시간을 절약하고 기존 프로파일 기본 설정으로 고속 셋업을 완료하기를 원한다.

**Independent Test**: `./setup.sh --skip-benchmark` 구동 시 3단계 벤치마크 수행을 스킵하고 15초 이내에 셋업이 완수되는지 검증.

**Acceptance Scenarios**:

1. **Given** 개발자나 자동화 파이프라인이 `./setup.sh --skip-benchmark`를 구동할 때, **When** 셋업 단계에 도달하면, **Then** 3단계 벤치마크 측정을 스킵하고 기존 설정값을 유지한 채 고속 완료한다.

---

## Edge Cases & Error Handling *(mandatory)*

- 3단계 벤치마크 도중 GPU 메모리 부족(OOM) 또는 오류 발생 시: log_warn 경고를 출력하고 안전 기본 프로파일(qwen3.5-4b, 4096 context)로 안전 폴백하여 `setup.sh` 실행 중단 방지.
- 비대화형(CI/CD) 환경에서 벤치마크 실행 시: 자동 타임아웃(예: 120초)을 설정하여 무한 대기 방지.

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `setup.sh` 내 4단계 모듈화 파이프라인(1. 다운로드, 2. 검증, 3. 임시 서빙 & 컨텍스트 벤치마크, 4. 선정 & 설정 반영) 구현 완료
- **DoD-002**: 실측 컨텍스트 윈도우 결과 기반 서빙 모델 및 컨텍스트 윈도우 크기 자동 결정 및 `config/server_config.json` 업데이트 연동 완료
- **DoD-003**: `--skip-benchmark` 플래그 및 4단계 모듈식 셋업 연동 단위/통합 테스트 수트 (`tests/unit/test_setup_benchmark_integration.py`) 100% 통과 입증

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST `./setup.sh` 실행 흐름을 4단계 모듈식 파이프라인(Stage 1: 모델 다운로드, Stage 2: 무결성 검증, Stage 3: 임시 서빙 가동 및 컨텍스트 윈도우 벤치마크, Stage 4: 선정 & 설정 반영)으로 분해 연동해야 한다.
- **FR-002**: System MUST Stage 3 실행 시 임시 인퍼런스 서버를 구동하여 후보 모델 및 컨텍스트 윈도우(2K, 4K, 8K, 16K 등) 확대에 따른 실측 VRAM 소모량과 토큰 생성 속도(TPS)를 정밀 측정해야 한다.
- **FR-003**: System MUST Stage 4 실행 시 벤치마크 결과를 분석하여 VRAM 안전 한계 내 최적 서빙 모델명과 컨텍스트 윈도우 크기(예: 4096, 8192)를 `config/server_config.json`에 원자적 업데이트해야 한다.
- **FR-004**: System MUST `./setup.sh --skip-benchmark` 플래그를 지원하여 Stage 3 벤치마크 단계를 건너뛰고 빠른 기본 프로파일 설정으로 셋업을 완수하도록 해야 한다.
- **FR-005**: System MUST 4단계 모듈식 연동 및 설정 자동 반영을 검증하는 단위 테스트 수트(`tests/unit/test_setup_benchmark_integration.py`)를 작성하고 100% 통과시켜야 한다.

### Key Entities

- **ModularSetupPipeline**: 4단계 모듈식 셋업 파이프라인 엔티티 (`stage_status`, `download_ok`, `integrity_ok`, `recommended_model`, `recommended_context_window`, `benchmark_tps`, `vram_used_mb`).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `./setup.sh` 실행 시 4단계 모듈식 파이프라인 순차 수행 및 최적 서빙 모델/컨텍스트 크기 선정 성공률 100%.
- **SC-002**: `--skip-benchmark` 실행 시 Stage 3 스킵 및 15초 이내 고속 셋업 완수율 100%.
- **SC-003**: 4단계 셋업 모듈 연동 테스트 수트 통과율 100%.

## Assumptions

- 모델 다운로드(Stage 1)는 `scripts/ensure_models.py`를 통해 연동되며, 무결성 검증(Stage 2) 및 컨텍스트 측정(Stage 3)은 모듈식 파이썬 스크립트(`scripts/benchmark_context_window.py`)로 분해 실행됨.

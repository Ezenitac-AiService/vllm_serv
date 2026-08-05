# Tasks: `setup.sh` 4단계 모듈화 벤치마크 파이프라인 연동 및 이진 탐색 정밀 프로파일링 (`095-setup-benchmark-model-selection`)

**Input**: Design documents from `/specs/095-setup-benchmark-model-selection/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/setup_benchmark_contract.json, quickstart.md

**Tests**: 모든 과제는 `uv run pytest` 기반의 실측 및 검증을 거칩니다.

**Organization**: 각 User Story별로 태스크가 분류되어 있어 독립적인 구현 및 검증이 가능합니다.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 병렬 수행 가능 (다른 파일, 의존성 없음)
- **[Story]**: 해당 태스크가 속한 사용자 시나리오 (예: US1, US2, US3)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: 벤치마크 셋업 계약 및 데이터 인프라 준비

- [X] T001 `specs/095-setup-benchmark-model-selection/contracts/setup_benchmark_contract.json` 계약 스키마 검증 및 fine-grained 1024 단위 지원 확장

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: 4단계 모듈화 파이프라인 핵심 백엔드 모듈 구현

**⚠️ CRITICAL**: 이 단계가 완료되기 전에는 User Story 작업을 시작할 수 없습니다.

- [X] T002 [P] `scripts/benchmark_context_window.py` 파이썬 모듈 신규 구현 (Stage 2: GGUF 무결성 검증, Stage 3: 컨텍스트 윈도우 2K~16K 실측 VRAM/TPS 측정 및 Stage 4: 추천 모델/컨텍스트 산출)
- [X] T003 [P] `src/core/config_manager.py`에 `auto_benchmark_profile` 및 `model_context_profiles` 원자적 `config/server_config.json` / `config/model_context_profiles.json` 업데이트 메소드 지원

**Checkpoint**: 4단계 벤치마크 모듈 구축 완료 - User Story 작업 시작 가능

---

## Phase 3: User Story 1 - `setup.sh` 4단계 모듈화 파이프라인 연동 (Priority: P1) 🎯 MVP

**Goal**: `./setup.sh` 실행 시 Step 2.8을 통해 4단계 파이프라인(다운로드 → 무결성 실측 검증 → 컨텍스트 측정 → 설정 반영)을 원스톱 가동

**Independent Test**: `./setup.sh` 구동 시 Step 2.8의 4개 모듈식 단계가 순차 실행되고 `verify_model_integrity` 헤더 검증 통과 후 `config/server_config.json`에 최적 모델/컨텍스트가 자동 반영되는지 검증

### Tests for User Story 1

- [X] T004 [P] [US1] 4단계 파이프라인 셋업 연동 단위/통합 테스트 수트 구현 (`tests/unit/test_setup_benchmark_integration.py`)

### Implementation for User Story 1

- [X] T005 [US1] `scripts/setup.sh`에 Step 2.8 (4단계 모듈식 파이프라인 연동: `ensure_models.py` → `verify_model_integrity` → `benchmark_context_window.py` → `save_benchmark_profile`) 구현 (FR-001, FR-002, FR-003)

**Checkpoint**: User Story 1 (4단계 모듈식 벤치마크 셋업 파이프라인) 연동 완료

---

## Phase 4: User Story 2 - `--skip-benchmark` 및 비대화형 CI/CD 지원 (Priority: P2)

**Goal**: `--skip-benchmark` 플래그 및 비대화형 환경 자동 타임아웃/폴백 처리 구현

**Independent Test**: `./setup.sh --skip-benchmark` 구동 시 Stage 3 실측 벤치마크를 건너뛰고 기존 설정을 보존한 채 15초 이내 완료되는지 검증

### Implementation for User Story 2

- [X] T006 [P] [US2] `scripts/setup.sh`에 `--skip-benchmark` CLI 플래그 파싱 및 `scripts/benchmark_context_window.py --skip-benchmark` 호출 연동 (FR-004)
- [X] T007 [P] [US2] `scripts/benchmark_context_window.py`에 `--skip-benchmark` 구동 시 기존 `context_window` 설정값 보존 및 예외 발생 시 안전 기본 프로파일(qwen3.5-4b, 4096 context) 폴백 처리 추가
- [X] T008 [US2] `tests/unit/test_setup_benchmark_integration.py`에 `--skip-benchmark` CLI 및 15초 이내 수행 시간 검증(`elapsed < 15.0`) 단정문 추가

**Checkpoint**: User Story 1 & 2 완료

---

## Phase 5: User Story 3 - 벤치마크 하드코딩/목업 제거 리팩토링 및 2단계 이진 탐색 정밀 프로파일링 (Priority: P3)

**Goal**: 벤치마크 스크립트 내 하드코딩/목업/회피 로직을 전면 제거하고 2단계 이진 탐색(Binary Search, 최소 1024 해상도) 정밀 프로파일링을 구동하여 `config/model_context_profiles.json` 및 `data/reports/analysis_report_quality.md`에 실측 텔레메트리 기록

**Independent Test**: `python scripts/benchmark_context_window.py --fine-grained` 구동 시 하드코딩 값 없이 NVML/API 실측 텔레메트리로 2단계 이진 탐색을 구동하여 1024 단위 정밀 한계 컨텍스트 크기를 `config/model_context_profiles.json`에 저장하는지 검증

### Implementation for User Story 3

- [X] T009 [P] [US3] `scripts/benchmark_quality.py` 내 베이스라인 딕셔너리(`baselines`), 가짜 비율 수치(`* 0.2`) 제거 및 웜업(Warmup) 추론 후 NVML GPU VRAM 스냅샷, SSE 스트리밍 기반 실측 TTFT/TPOT 텔레메트리 추출 전환 (FR-006)
- [X] T010 [P] [US3] `scripts/benchmark_context_window.py`에 정밀 프로파일링 모드(`--fine-grained`) 도입 및 1차 2배 스케일링 판정 구간 $[C_{pass}, C_{fail}]$에 대해 512/1024 토큰 블록 얼라인먼트 및 RoPE Cap(`min(physical_max, model_max_rope)`)을 준수하는 이진 탐색(Binary Search) 엔진 구현 및 `config/model_context_profiles.json` 원자적 보존 (FR-007)
- [X] T011 [US3] `tests/unit/test_setup_benchmark_integration.py`에 `--fine-grained` 1024 해상도 이진 탐색 및 하드코딩 0% 의존 검증 테스트 케이스 추가 (SC-004)

**Checkpoint**: User Story 3 (벤치마크 하드코딩 제거 및 이진 탐색 정밀 프로파일링) 완료

---

## Phase 6: User Story 4 - `setup.sh` 연동 하위 스크립트 전면 폴리싱 및 불용 파일 정리 (Priority: P3)

**Goal**: `setup.sh`가 호출하는 연동 하위 스크립트들(`ensure_models.py`, `benchmark_context_window.py`, `start_server.sh`, `stop_server.sh`, `status_server.sh` 등)의 예외 처리, 비대화형 동작 및 100% 경로 분기를 전면 폴리싱하고, 만료된 불용 파일들을 정돈

**Independent Test**: `setup.sh` 구동 시 연동 하위 스크립트들이 예외 없이 완료되고, 불용 파일 없이 깨끗이 정리되는지 검증

### Implementation for User Story 4

- [X] T018 [P] [US4] `scripts/ensure_models.py`, `scripts/start_server.sh`, `scripts/stop_server.sh`, `scripts/status_server.sh` 경로 분기 및 비대화형 예외 처리 전면 폴리싱 (FR-008)
- [X] T019 [P] [US4] 용도가 상실되었거나 만료된 불용 스크립트 및 더미 파일 정리 및 아카이빙 (FR-009)

**Checkpoint**: User Story 4 완료

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: 최종 문서화 및 DoD 검증 수행

- [X] T012 [P] `specs/095-setup-benchmark-model-selection/quickstart.md` 가이드 문서 업데이트 (시나리오 4 포함)
- [X] T013 [Quickstart 실측] Quickstart 시나리오 1~4 전체 수행 및 DoD(DoD-001~006) 달성 최종 검증
- [X] T017 [P] `README.md` 메인 문서 업데이트 (Step 2.8 4단계 파이프라인, `--skip-benchmark`, `--fine-grained` 이진 탐색 및 3개 플랫폼 매트릭스 수록)

---

## Phase 7: Convergence

- [X] T014 Stage 2 무결성 검증(`verify_model_integrity`) 실체적 호출 연동 per FR-001, Constitution II (contradicts)
- [X] T015 `scripts/setup.sh` 내 `--skip-benchmark` 플래그 전달 시 `benchmark_context_window.py --skip-benchmark` 호출 연동 per FR-004 (partial)
- [X] T016 `tests/unit/test_setup_benchmark_integration.py` 내 `--skip-benchmark` CLI 동작 및 15초 이내 완수 assertion 추가 per FR-004, SC-002 (partial)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: 즉시 시작 가능
- **Foundational (Phase 2)**: Setup 완료 후 실행
- **User Stories (Phase 3+)**: Foundational 완료 후 시작 (US1 → US2 → US3)
- **Polish (Phase 6)**: 모든 User Story 완료 후 실행

### Parallel Opportunities

- T002, T003 (Foundational) 병렬 수행 가능
- T004, T006, T007 (User Story 1, 2) 병렬 수행 가능
- T009, T010 (User Story 3 리팩토링 및 이진 탐색 스크립트) 병렬 수행 가능

---

## Implementation Strategy

### MVP First (User Story 1 Only)
1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Test User Story 1 independently

### Incremental Delivery
1. User Story 1 (4단계 모듈식 파이프라인 연동)
2. User Story 2 (`--skip-benchmark` 고속 셋업 지원)
3. User Story 3 (벤치마크 하드코딩 제거 및 이진 탐색 정밀 프로파일링)

---

## Phase 8: Convergence (연동 스크립트 모듈별 정밀 폴리싱 & 불용 파일 정리)

- [X] T020 `scripts/setup.sh` 4단계 파이프라인(Stage 1~4) 호출부, non-blocking subshell 및 예외 트랩 전면 폴리싱 per FR-008, US4 (partial)
- [X] T021 `scripts/ensure_models.py` 상대/절대 경로 자동 분기 및 모델 다운로드 예외 핸들링 폴리싱 per FR-008, US4 (partial)
- [X] T022 `scripts/start_server.sh` 백그라운드 데몬 시그널 처리, 8081/8082 Readiness & 원자적 롤백 폴리싱 per FR-008, US4 (partial)
- [X] T023 `scripts/stop_server.sh` SIGTERM->SIGKILL 2단계 종료 및 NVML VRAM 해제 검증 폴리싱 per FR-008, US4 (partial)
- [X] T024 `scripts/status_server.sh` 메인/대시보드 PID 점유 및 GPU 메모리 실시간 조회 폴리싱 per FR-008, US4 (partial)
- [X] T025 `scripts/configure_firewall.sh` 및 `scripts/common.sh` OS 방화벽 패키지 감지 및 로깅 헬퍼 폴리싱 per FR-008, US4 (partial)
- [X] T026 `scripts/verify_wheel_binary.py` 및 `scripts/update_cuda_drivers.sh` CUDA 하드웨어 검증 스크립트 폴리싱 per FR-008, US4 (partial)
- [X] T027 `scripts/seed_db.py` 및 `scripts/diagnose_server_health.py` DB 시드 초기화 및 헬스 진단 모듈 폴리싱 per FR-008, US4 (partial)
- [X] T028 `scripts/audit_assets.py` 자산 감사 및 프로젝트 레거시 탐지 모듈 폴리싱 per FR-008, US4 (partial)
- [X] T029 불용/만료된 레거시 스크립트 및 더미 임시 파일 전면 탐지 및 아카이빙 정리 per FR-009, US4 (missing)

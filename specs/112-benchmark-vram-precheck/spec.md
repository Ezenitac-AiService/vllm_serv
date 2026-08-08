# Feature Specification: 벤치마크 품질 평가 스크립트 VRAM 용량 사전 검증 및 자동 스킵 (Benchmark VRAM Pre-check & Auto-Skip)

**Feature Branch**: `112-benchmark-vram-precheck`

**Created**: 2026-08-08

**Status**: Draft

**Input**: User description: "uv run python scripts/benchmark_quality.py --auto-download --real 명령으로 모델 다운로드 시 gemma4-26b-a4b(16.9GB) 다운로드 완료 후 VRAM 초과(Estimated 19952MB exceeds 11264MB)로 프로세스 개설 실패 발생. 이후 qwen3.6-27b 다운로드를 계속 시도하여 시간/대역폭 낭비 발생"

---

## Clarifications

### Session 2026-08-08

- Q: 로컬에 이미 다운로드된 가중치 파일이 존재하는 경우의 VRAM 검증 및 벤치마크 평가 처리 방식 → A: Option A (로컬 디렉터리에 가중치 파일이 이미 존재하더라도 물리 GPU VRAM 용량을 초과하면 CUDA OOM 런타임 크래시 방지를 위해 벤치마크 평가 및 서빙 프로세스 개설 시도에서 자동으로 사전 스킵)

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 모델 다운로드 및 서빙 전 VRAM 용량 사전 검증 및 자동 스킵 (Priority: P1) 🎯 MVP

사용자가 `benchmark_quality.py --auto-download` 명령을 실행할 때, 대용량 GGUF 모델 가중치를 다운로드하거나 기존 로컬 파일로 서빙을 개설하기 전 타겟 서버 GPU의 물리 VRAM 용량과 모델 추정 VRAM 요구량(GGUF 파일 크기 + KV Cache)을 사전에 산출하여, 현재 GPU VRAM 용량을 초과하는 모델은 다운로드 및 서빙 프로세스 개설을 시도하기 전에 자동으로 스킵(Skip)해야 합니다.

**Why this priority**: 16GB 이상의 대용량 모델 파일 다운로드(십여 분 이상 소요) 완료 후 또는 이미 존재하는 로컬 파일 서빙 개설 단계에서 CUDA OOM으로 실패하는 문제를 사전 차단하여 대역폭, 디스크 공간 및 대기 시간을 획기적으로 절약합니다.

**Independent Test**: GPU VRAM 11GB(GTX 1080 Ti 등) 환경에서 26B/27B 모델(VRAM 요구량 > 19GB)에 대해 `--auto-download` 구동 시, 원격 다운로드는 물론 이미 로컬에 존재하는 가중치에 대해서도 서빙을 개설하지 않고 `[SKIP VRAM OOM Risk]` 경고 로그와 함께 다음 모델로 즉시 넘어감을 확인.

**Acceptance Scenarios**:

1. **Given** 타겟 서버의 물리 VRAM 용량이 11,264MB이고 대상 모델(gemma4-26b-a4b)의 추정 VRAM 요구량이 19,952MB인 상태에서, **When** `benchmark_quality.py --auto-download`를 실행하면, **Then** 모델 가중치 원격 다운로드 시도를 차단함은 물론 로컬 파일이 존재하더라도 서빙 개설을 시도하지 않고 "VRAM 용량 초과 예상으로 스킵" 메세지를 출력 후 즉시 다음 모델로 진행합니다.
2. **Given** 현재 GPU VRAM 용량으로 구동 가능한 모델(예: 8B/Q4_K_M 등, VRAM 요구량 8,000MB)에 대해서는, **When** 스크립트를 실행하면, **Then** VRAM 사전 검증을 정상 통과하여 가중치 다운로드 및 서빙 프로세스를 개설합니다.

---

### User Story 2 - 벤치마크 구동 시 전수 모델 VRAM 적합성 사전 요약 리포트 (Priority: P2)

벤치마크 평가 구동 시작 단계에서 평가 대상 전체 모델 목록에 대해 GPU VRAM 수용 가능 여부를 전수 판정하고, 실행 가능한 모델과 사전 스킵될 모델의 요약 리포트를 사용자에게 먼저 제시합니다.

**Why this priority**: 실행 중 예쇄적인 실패나 무의미한 대기 없이 사용자가 어떤 모델이 실제로 평가될지 한눈에 파악할 수 있도록 편의성을 제공합니다.

**Independent Test**: `benchmark_quality.py` 실행 직후 출력되는 초기 요약 로그에 현재 GPU 스펙 및 모델별 VRAM 수용 적합성(Pass / Skip) 테이블이 표시됨을 확인.

**Acceptance Scenarios**:

1. **Given** 총 14개의 평가 대상 모델이 지정된 환경에서, **When** 벤치마크 평가를 시작하면, **Then** 벤치마크 최상단에 현재 GPU VRAM(예: 11,264MB) 대비 각 모델별 추정 VRAM 및 사전 판정 결과(PASS: N개, SKIP: M개)를 요약 출력합니다.

---

### User Story 3 - CLI 실행 옵션으로 VRAM 사전 검증 강제 제어 (Priority: P3)

개발자나 시스템 관리자가 테스트 목적이나 CPU 오프로딩/대용량 가상 메모리 테스트를 위해 VRAM 사전 스킵 검증을 비활성화하거나 강제 다운로드/서빙 옵션(`--ignore-vram-check`)을 지정할 수 있어야 합니다.

**Why this priority**: 특수 환경(System RAM 수와오프로드 모드)에서의 디버깅 및 고도화 테스트 유연성을 확보합니다.

**Independent Test**: `benchmark_quality.py --auto-download --ignore-vram-check` 실행 시 VRAM 용량을 초과하더라도 스킵하지 않고 다운로드 및 서빙을 강제 진행함을 확인.

**Acceptance Scenarios**:

1. **Given** `--ignore-vram-check` 플래그가 부여되었을 때, **When** 벤치마크를 구동하면, **Then** VRAM 초과 경고만 출력하고 다운로드 및 서빙 시도를 강제 수행합니다.

---

### Edge Cases

- **GPU 디텍터 미작동 / CPU 전용 환경**: CUDA GPU가 감지되지 않거나 CPU 모드일 경우 VRAM 스킵 대신 시스템 RAM 용량을 기준으로 사전 검증.
- **분할 GGUF 또는 원격 메타데이터 미수신**: HuggingFace 메타데이터 수신 실패 시 GGUF 헤더 최소 추정치(모델 파라미터 수 기반)로 예비 VRAM 평가 수행.

---

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `model_downloader.py` 및 `benchmark_quality.py`에 다운로드 및 로컬 서빙 개설 실행 전 물리 VRAM 대비 모델 VRAM 요구량 사전 검증 및 자동 스킵(Pre-download/Pre-serve VRAM check & skip) 기능 구현 완료.
- **DoD-002**: `tests/unit/test_benchmark_context.py` 및 `test_model_downloader.py` 수트에 VRAM 용량 초과 모델 사전 스킵(원격 및 로컬 파일 포함) 단정 단위 테스트 수록 및 100% PASS 통과.
- **DoD-003**: `uv run python scripts/benchmark_quality.py --auto-download` 구동 시 11GB VRAM 환경에서 26B/27B 대형 모델의 16GB+ 다운로드 및 로컬 서빙 개설 시도가 사전에 안전 차단됨을 실측 검증.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 다운로더 스크립트(`model_downloader.py`)는 모델 가중치 네트워크 다운로드를 개시하기 전, 대상 모델의 예상 VRAM 사용량(가중치 크기 + KV Cache 기본 할당량)과 물리 GPU VRAM 용량을 비교하여 사전 호환성 검사를 수행해야 합니다.
- **FR-002**: 물리 VRAM 용량을 초과하는 모델 판정 시 원격 다운로드 및 로컬 파일 서빙 개설 시도를 즉시 중단 및 스킵 처리하고 명확한 경고 메세지(`[SKIP VRAM OOM Risk]`)를 출력해야 합니다.
- **FR-003**: 벤치마크 평가 스크립트(`benchmark_quality.py`)는 평가 시작 전 전체 대상 모델의 VRAM 적합성 예비 판정 결과를 요약 출력해야 합니다.
- **FR-004**: `--ignore-vram-check` 플래그를 통해 사전 VRAM 검사 및 스킵 동작을 사용자가 강제 우회할 수 있는 CLI 옵션을 제공해야 합니다.
- **FR-005**: VRAM 사전 검사 결과는 기존 `ProcessManager`의 VRAM 안전 평가 공식(GGUF 파일 용량 + Context Window KV Cache 계산식)과 100% 동일한 로직을 공유해야 합니다.
- **FR-006**: 로컬 디렉터리에 모델 가중치 파일이 이미 존재하더라도, 물리 GPU VRAM 용량을 초과하는 모델인 경우 `--ignore-vram-check`가 지정되지 않았다면 `llama-server` 프로세스 개설 시도를 사전에 차단하고 스킵해야 합니다.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: GPU VRAM 용량을 초과하는 대형 모델 평가 시 불필요한 10GB+ 다운로드 및 실패할 로컬 서빙 개설로 인한 시간 낭비가 0초로 감소합니다 (사전 즉시 스킵).
- **SC-002**: 벤치마크 실행 중 VRAM 부족으로 인한 런타임 CUDA OOM 프로세스 개설 실패 발생 빈도가 0건으로 감소합니다.

---

## Assumptions

- 타겟 서버의 GPU VRAM 정보는 기존 `gpu_detector.py` 또는 `torch.cuda` / `nvidia-smi` 인터페이스를 통해 정상 취득 가능합니다.
- 모델 다운로드 메타데이터 또는 카탈로그(`model_catalog.json`)에는 GGUF 가중치의 예상 용량 또는 파라미터 수 정보가 포함되어 있습니다.

# Feature Specification: `setup.sh` 실행 시 필수 GGUF 모델 자동 점검 및 자동 다운로드 통합 (`092-setup-auto-model-download`)

**Feature Branch**: `092-setup-auto-model-download`

**Created**: 2026-08-04

**Status**: Draft

**Input**: User description: "마이그레이션 작업을 해보니, setup.sh 가 해야 할 일들이 많더라고, 089 스펙에서 추가했지만, 아직 추가가 안된 작업이 있는데, uv run python scripts/benchmark_quality.py --auto-download --real 를 하지 않으면, 어떤 모델도 없어서 start_server.sh가 제대로 동작을 안해, 저 벤치마크 스크립트의 일부를 이용해서, setup.sh 의 진행중에, 모델이 있는지 확인하고 없으면 다운로드 받는 과정이 있어야 할거 같아"

## Clarifications

### Session 2026-08-04

- Q: `setup.sh` 실행 시 자동 다운로드 대상 기본 모델 범위 → A: Option A (3종 필수 모델 세트: `qwen3.5-4b` + `bge-m3` + `bge-reranker-v2-m3` 모두 점검 및 다운로드하여 3개 데몬 동시 가동 보장)
- Q: PCI 레벨 하드웨어 탐지 및 드라이버/CUDA 자동 설치 진입 방식 → A: Option A (`lspci` 기반 물리 GPU 탐지 + `install_cuda_env.sh` 자동 설치 연동으로 드라이버/CUDA/cuDNN/컴파일러 미구성 시 자동 설치/업데이트 지원 후 llama.cpp 바이너리 빌드 및 모델 원스톱 프로비저닝 완료)
- Q: `scripts/` 전수 동원 및 `setup.sh` 원스톱 통합 리팩토링 범위 → A: Option A (`scripts/` 내 전체 스크립트를 `setup.sh` 단계별 모듈식 체이닝으로 연동 및 전수 리팩토링 진행: PCI/드라이버 자동점검/업데이트(`update_cuda_drivers.sh`) -> DB 초기화(`seed_db.py`) -> 자산 정돈(`audit_assets.py`) -> 휠 검증(`verify_wheel_binary.py`) -> 모델 프로비저닝(`ensure_models.py`) -> 방화벽 개방(`configure_firewall.sh`) -> 헬스 진단(`diagnose_server_health.py`))

## User Scenarios & Testing *(mandatory)*

### User Story 1 - `setup.sh` 가동 시 필수 GGUF 모델 유무 자동 검사 및 다운로드 연동 (Priority: P1) 🎯 MVP

시스템 운영자 및 신규 훈련생이 `./setup.sh`를 실행할 때, 시스템은 `models/` 디렉토리를 자동으로 정밀 탐색하여 서비스에 필요한 기본 GGUF 모델 파일(LLM 대화 모델, 임베딩 모델, 리랭커 모델 등)의 존재 여부를 검사하고, 미존재 시 자동 다운로드 파이프라인을 구동하여 별도의 수동 명령어 입력 없이 환경 구축을 완료할 수 있어야 한다.

**Why this priority**: 마이그레이션 후 `./setup.sh`만 실행하고 바로 `./start_server.sh`를 구동할 때 모델 부재로 인해 데몬이 비정상 종료(Crash)되는 치명적 사용자 경험 결함을 예방하기 위함이다.

**Independent Test**: 모델 디렉토리(`models/`)가 비어있는 상태에서 `./setup.sh`를 실행 시, 필수 모델 검사 단계가 발동하여 `models/`에 올바른 GGUF 모델 파일이 자동 다운로드되고 저장되는지 검증한다.

**Acceptance Scenarios**:

1. **Given** `models/` 디렉토리에 기본 GGUF 모델 파일이 존재하지 않는 신규/마이그레이션 환경에서, **When** `./setup.sh`를 실행할 때, **Then** 시스템은 모델 부재를 자동 감지하고 `ModelDownloader` 파이프라인을 호출하여 필요한 모델을 받아 `models/`에 배치한다.
2. **Given** 모델 자동 다운로드가 성공적으로 완료된 후, **When** `./start_server.sh`를 실행할 때, **Then** LLM, 임베딩, 리랭커 데몬이 모델 파일 로딩 실패 없이 즉시 가동된다.

---

### User Story 2 - 스마트 스킵(Smart Skip) 및 다운로드 진행률 명시 (Priority: P2)

엔지니어 및 훈련생은 이미 필요한 GGUF 모델 파일이 `models/` 디렉토리에 정상적으로 존재하는 경우, 불필요한 재다운로드 없이 다운로드 과정을 즉시 스킵(Skip)하고 빠른 설치를 완료할 수 있어야 하며, 다운로드 진행 시 진행 상태와 다운로드 결과를 명확히 확인할 수 있어야 한다.

**Why this priority**: 이미 모델이 다운로드되어 있는 환경에서 `./setup.sh`를 재실행할 때 불필요한 대용량 트래픽 발생 및 무한 대기를 방지하기 위함이다.

**Independent Test**: 이미 모델이 배치된 상태에서 `./setup.sh`를 재실행 시 "기존 모델 감지됨, 다운로드 스킵" 메시지가 출력되고 즉시 다음 설치 단계로 넘어가는지 검증한다.

**Acceptance Scenarios**:

1. **Given** `models/` 디렉토리에 이미 `qwen3.5-4b` 등 필수 GGUF 파일이 존재하는 환경에서, **When** `./setup.sh`를 실행할 때, **Then** 다운로드를 스킵하고 설치 절차를 수초 이내에 완료한다.

---

### User Story 3 - CLI 옵션 및 헬퍼 스크립트 결합 (`scripts/ensure_models.py`) (Priority: P3)

개발자는 쉘 스크립트 `setup.sh`와 파이썬 모듈 `src/core/model_downloader.py` 간의 결합도를 낮추기 위해 전용 파이썬 헬퍼 스크립트(`scripts/ensure_models.py`)를 통해 독립적으로도 모델 점검 및 다운로드를 수행할 수 있어야 한다.

**Why this priority**: 단일 책임 원칙(SRP)에 따라 쉘 스크립트 내부에 복잡한 파이썬 로직을 직접 포함하지 않고 유지보수가 쉬운 모듈식 헬퍼로 분리하기 위함이다.

**Independent Test**: `uv run python scripts/ensure_models.py`를 독립 실행하여 모델 유무 검사 및 필요시 다운로드가 독립 수행되는지 검증한다.

**Acceptance Scenarios**:

1. **Given** 독립 터미널 환경에서, **When** `uv run python scripts/ensure_models.py` 명령을 직접 호출할 때, **Then** 필수 모델 존재 검사 및 자동 다운로드가 올바르게 작동한다.

---

### Edge Cases

- 네트워크 연결이 차단된 인트라넷 환경에서 다운로드 실패 시: 명확한 에러 메시지를 출력하고 수동 모델 배치 경로 안내.
- 다운로드 중 중단(Timeout/Ctrl+C)되어 부분 파일(.tmp)이 남은 경우: 해시/크기 검사 후 깨진 파일 자동 제거 및 재시도.

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `scripts/ensure_models.py` 헬퍼 스크립트 작성 및 `src/core/model_downloader.py` 연동 완료
- **DoD-002**: `scripts/setup.sh`에 모델 자동 점검 및 다운로드 단계 추가 완료
- **DoD-003**: `./setup.sh` 실행 후 `./start_server.sh` 가동 시 모델 미존재로 인한 서버 구동 실패 0건 입증

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST `setup.sh` 실행 과정에서 `models/` 디렉토리 내 필수 GGUF 모델 파일(기본 LLM 및 임베딩/리랭커 모델)의 존재 여부를 정밀 검사해야 한다.
- **FR-002**: System MUST 필수 모델이 존재하지 않을 경우 파이썬 헬퍼 스크립트(`scripts/ensure_models.py`)를 통해 HuggingFace/ModelScope 등 지정 소스로부터 자동 다운로드를 수행해야 한다.
- **FR-003**: System MUST 이미 검증된 모델 파일이 `models/`에 존재하는 경우 재다운로드를 스킵(Skip)하여 신속하게 환경 구축을 완료해야 한다.
- **FR-004**: System MUST 다운로드 실패 또는 오프라인 환경일 경우 명확한 가이드 메시지(수동 모델 다운로드 및 `models/` 배치 안내)를 출력하고 적절한 종료 상태를 반환해야 한다.
- **FR-005**: System MUST `uv run python scripts/ensure_models.py` 명령을 독립 실행 가능하도록 제공하여 다른 벤치마크나 셋업 도구에서도 재사용할 수 있게 해야 한다.
- **FR-006**: System MUST 자동 다운로드 검증을 포함한 단위/통합 테스트 수트(`tests/test_ensure_models.py`)를 작성하고 100% 통과시켜야 한다.
- **FR-007**: System MUST `setup.sh` 파이프라인에서 `lspci` 기반 PCI 버스 탐지로 NVIDIA 물리 GPU 장비를 인식하고, 드라이버/CUDA/cuDNN/컴파일러 미구성 시 자동 설치/업데이트 헬퍼 스크립트(`scripts/install_cuda_env.sh`) 연동 안내 및 원스톱 파이프라인을 지원해야 한다.
- **FR-008**: System MUST `scripts/` 내 기존 스크립트 모듈들(`common.sh`, `update_cuda_drivers.sh`, `seed_db.py`, `audit_assets.py`, `verify_wheel_binary.py`, `ensure_models.py`, `configure_firewall.sh`, `diagnose_server_health.py`)을 `setup.sh` 파이프라인 단계별로 유기적으로 체이닝하고 종합 원스톱 리팩토링을 완성해야 한다.

### Key Entities

- **ModelDownloadStatus**: 모델 다운로드 상태 엔티티 (`model_id`, `file_path`, `is_present`, `download_status`).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `./setup.sh` 완료 후 모델 미존재로 인한 `./start_server.sh` 구동 실패 0건.
- **SC-002**: 이미 모델이 배치된 환경에서 `./setup.sh` 실행 시 다운로드 스킵 시간 < 2초.
- **SC-003**: `uv run pytest tests/test_ensure_models.py` 성공률 100% 달성.

## Assumptions

- 파이썬 환경이 `setup.sh`의 이전 단계(`uv sync`)에서 먼저 구축되어 `uv run python` 호출이 가능함.
- `src/core/model_downloader.py` 기존 다운로더 모듈을 활용함.

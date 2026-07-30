# Feature Specification: Seed Pack Archiver & Migration Pipeline

**Feature Branch**: `specs/019-seed-pack-generator`

**Created**: 2026-07-30

**Status**: Draft

**Input**: User description: "이 llm 모델 서비스 프로젝트를 다른 시스템에 마이그레이션 할수 있는 구조인데, 핵심 파일들과 쉘 파일들만 모아서, 다른 시스템으로 갔을때에, setup.sh를 실행해서 프로젝트를 구성하고, llama.cpp를 빌드하고, 모델을 받고, 모델을 서비스하는 seed 팩을 생성, 구조는 일반적인 압축파일로 하면 될거 같아"

---

## Executive Summary & User Value

본 피처는 `vllm_serv` LLM 인퍼런스 서빙 시스템을 타 GPU 서버 환경으로 신속하고 경량화된 방식으로 이관(Migration)할 수 있도록, 시스템 재구성에 필요한 핵심 소스 코드, 설정 파일, 그리고 제어 쉘 스크립트만을 선택적으로 묶은 Seed Pack 압축 아카이브(`vllm_serv_seed.tar.gz`) 자동 생성 파이프라인을 구축합니다.

개발자 및 시스템 운영자는 수십 GB에 달하는 모델 가중치(`models/`)와 무거운 가상환경(`.venv`), 빌드 부산물(`.bin/`, `__pycache__`)을 제거한 수 MB 수준의 Seed Pack만 새 서버로 복사한 뒤, `./setup.sh` 및 `./start_server.sh` 실행만으로 의존성 설치, CUDA llama.cpp 컴파일, 모델 자동 다운로드 및 100% VRAM 서빙 개설을 원스톱으로 완료할 수 있습니다.

---

## Clarifications

### Session 2026-07-30

- Q: make_seed_pack.sh 실행 시 압축 포맷 및 CLI 옵션 구체화 → A: 기본 .tar.gz 포맷 생성, `--zip` 전환 옵션 지원, `-o/--output` 출력 파일 경로 지정 옵션 제공.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 마이그레이션용 경량 Seed Pack 압축 생성 스크립트 실행 (Priority: P1) 🎯 MVP

**User Story**: 개발자는 프로젝트 루트에서 `./make_seed_pack.sh` (또는 `scripts/make_seed_pack.sh`) 스크립트를 실행하여 대용량 모델 파일과 불필요한 가상환경/빌드 결과물을 제외하고, 타 서버 이관에 필수적인 핵심 소스 및 쉘 파일만 묶은 표준 압축 아카이브(`dist/vllm_serv_seed.tar.gz`)를 자동으로 생성하길 원한다.

**Why this priority**: 수십 GB 모델 파일 및 중복 빌드 결과물 없이 신속하게 시스템 코드를 타 환경으로 전달하기 위한 최우선 기본 기능입니다.

**Independent Test**: `./make_seed_pack.sh` 실행 후 `dist/vllm_serv_seed.tar.gz` 파일이 생성되고 용량이 10MB 미만인지 검증.

**Acceptance Scenarios**:

1. **Given** 프로젝트 루트에서, **When** `./make_seed_pack.sh`를 실행할 때, **Then** `dist/` 디렉토리에 `vllm_serv_seed.tar.gz` 압축 파일이 생성된다.
2. **Given** 프로젝트 내에 수십 GB의 `models/*.gguf` 파일 및 `.venv/` 가상환경이 존재하는 상태에서, **When** Seed Pack이 생성될 때, **Then** 압축 아카이브 내부 목록에서 `models/`, `.venv/`, `.bin/`, `logs/`, `__pycache__/`, `.git/` 등의 디렉토리가 엄격히 제외되어 파일 크기가 10MB 미만으로 생성된다.

---

### User Story 2 - 타 시스템에서 Seed Pack 압축 해제 및 setup.sh 프로젝트 구성 (Priority: P2)

**User Story**: 운영자는 신규 GPU 서버에서 `vllm_serv_seed.tar.gz` 압축을 풀고 `./setup.sh`를 실행하여 `uv` 의존성 설치 및 CUDA 가속 `llama-cpp-python` / `llama-server` 컴파일을 결함 없이 자동으로 완료하길 원한다.

**Why this priority**: 타 시스템에서 추가 수동 작업 없이 프로젝트 가상환경과 CUDA 인퍼런스 빌드 환경을 재구성하기 위함입니다.

**Independent Test**: 빈 임시 디렉토리에 Seed Pack 압축 해제 후 `./setup.sh` 실행 시 `llama_supports_gpu()` 검증 성공.

**Acceptance Scenarios**:

1. **Given** 신규 서버 임시 디렉토리에 Seed Pack 압축이 해제되었을 때, **When** `./setup.sh`가 실행되면, **Then** 필수 파일 검증, `uv sync`, `nvcc` 및 CUDA 라이브러리 검증, CUDA 지원 `llama-cpp-python` 설치 및 `start_server.sh`, `stop_server.sh`, `status_server.sh` 제어 스크립트 링크 생성이 정상 처리된다.

---

### User Story 3 - 복원된 시스템의 start_server.sh 구동 및 모델 자동 서비스 개설 (Priority: P3)

**User Story**: 운영자는 `./setup.sh` 복원 완료 후 `./start_server.sh`를 구동할 때, 서버가 기본 서빙 모델(`qwen3.5-4b`)을 자동으로 다운로드받아 GPU VRAM에 100% 탑재하고 READY 상태로 서비스를 개설하길 원한다.

**Why this priority**: 압축 이관 시 대용량 가중치 파일을 포함하지 않더라도, 첫 구동 시 허브에서 가중치를 자율 복구하여 서비스를 개설하기 위함입니다.

**Independent Test**: `./start_server.sh` 실행 시 `models/qwen3.5-4b/` 가중치가 자동 받쳐지고 REST API 헬스체크 `200 OK` 및 VRAM 탑재 확인.

**Acceptance Scenarios**:

1. **Given** `models/` 디렉토리에 가중치가 없는 초기 이관 상태에서, **When** `./start_server.sh`를 실행할 때, **Then** `ProcessManager` / `ModelDownloader`가 기본 모델을 자동 다운로드한 후 서빙 프로세스를 백그라운드로 띄운다.

---

### Edge Cases

- **압축 저장 디렉토리 미존재 시**: `dist/` 디렉토리가 없으면 자동으로 생성 후 압축 파일 배포.
- **이미 `vllm_serv_seed.tar.gz` 파일이 존재하는 경우**: 덮어쓰기 전 덮어쓴다는 메시지를 안내하고 기존 아카이브를 안전하게 갱신.
- **타 시스템에 `tar` / `gzip` 패키지가 미존재할 경우**: 스크립트 실행 시 `tar` 및 `gzip` 커맨드 존재 여부를 사전 검증하고 미설치 시 명확한 에러 메시지 출력.

---

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `scripts/make_seed_pack.sh` (및 루트 `./make_seed_pack.sh` 링크) 실행 시 `dist/vllm_serv_seed.tar.gz` 파일이 10MB 미만 용량으로 생성됨을 검증.
- **DoD-002**: Seed Pack 내에 `src/`, `config/`, `scripts/`, `tests/`, `pyproject.toml`, `README.md` 등 필수 자산이 정상 포함되고 `models/`, `.venv/`, `.bin/`이 배제됨을 검증.
- **DoD-003**: 독립된 임시 테스트 디렉토리에서 Seed Pack 압축 해제 후 `./setup.sh` 실행 및 `uv run pytest -v` 전체 수트 100% 통과 확인.
- **DoD-004**: 전체 `pytest` 수트 (`uv run pytest -v`) 100% 통과 보장.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 (Seed Pack 생성 스크립트 구축)**: 프로젝트 루트 및 `scripts/`에 `make_seed_pack.sh`를 제공하여 마이그레이션에 필요한 파일만 타르볼(`vllm_serv_seed.tar.gz`)로 패키징해야 한다.
- **FR-002 (대용량/부산물 제외 규칙 명시)**: `models/`, `.venv/`, `.bin/`, `logs/`, `build/`, `__pycache__/`, `.git/`, `.pytest_cache/`, `*.tar.gz`, `*.zip` 등을 상시 제외(`--exclude`) 규칙으로 등록해야 한다.
- **FR-003 (핵심 파일 포함 보장)**: `pyproject.toml`, `README.md`, `src/`, `config/`, `scripts/`, `tests/`, `.specify/` 항목이 압축본에 반드시 포함되어야 한다.
- **FR-004 (마이그레이션 실행 검증)**: 생성된 Seed Pack 아카이브를 풀어 새로운 환경에서 `./setup.sh` -> `./start_server.sh` 파이프라인이 정상 작동함을 검증하는 단위/통합 테스트를 제공해야 한다.
- **FR-005 (압축 포맷 및 CLI 옵션)**: 기본 포맷은 표준 POSIX `.tar.gz`로 생성하며, `--zip` 플래그로 `.zip` 파일 생성을 전환할 수 있고 `-o`/`--output` 인수를 통해 커스텀 파일 저장 경로를 지정할 수 있어야 한다.

### Key Entities

- **SeedPackArchive**: 마이그레이션용 핵심 소스코드, 설정, 스크립트만으로 구성된 POSIX `tar.gz` 아카이브 파일 (`dist/vllm_serv_seed.tar.gz`).
- **SeedPackGenerator**: 압축 대상을 수집하고 대용량 가중치 및 임시 빌드 아티팩트를 제외한 후 아카이브를 패키징하는 쉘 파이프라인 스크립트 (`scripts/make_seed_pack.sh`).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001 (Seed Pack 경량화)**: 생성된 `vllm_serv_seed.tar.gz` 파일 크기가 10MB 미만 달성.
- **SC-002 (마이그레이션 성공률)**: 클린 디렉토리에서 Seed Pack 압축 해제 후 `./setup.sh` 실행 시 100% 환경 구성 및 CUDA 빌드 성공.
- **SC-003 (테스트 통과율)**: `uv run pytest -v` 전체 수트 100% 통과.

---

## Assumptions

- 타겟 마이그레이션 서버는 Linux POSIX 환경이며, NVIDIA GPU, GPU 드라이버 및 `nvcc`가 준비되어 있음.
- 대용량 GGUF 모델 가중치는 이관 파일 용량 절감을 위해 패키지에서 제외하며, 이관 후 최초 서버 구동 시 온라인(HuggingFace)에서 자동 다운로드하도록 설계함.

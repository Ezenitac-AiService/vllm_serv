# Feature Specification: 샘플 실습 디렉토리 이중화(`sample` & `samples`) 분석 및 표준 통합 (`091-unify-sample-directories`)

**Feature Branch**: `091-unify-sample-directories`

**Created**: 2026-08-04

**Status**: Draft

**Input**: User description: "샘플 파일을 훈련 플렛폼에 맞춰서 고도화 했어, 그런데, 폴더가 두개가 생겼네? /home/dev/storage/vllm_serv/sample /home/dev/storage/vllm_serv/samples 분석해서 정리해줘,"

## Clarifications

### Session 2026-08-04

- Q: 주 표준 물리 디렉토리 명칭 선택 및 심볼릭 링크 방향 → A: Option A (`sample`을 주 표준 물리 디렉토리로 지정)
- Q: 시드팩 패키징(`make_seed_pack.sh`) 시 심볼릭 링크 처리 방침 → A: Option A (`sample/` 물리 디렉토리 전용 번들링 수행)
- Q: `samples` 심볼릭 링크 영구 삭제 여부 및 하위 호환성 보존 방침 → A: Option B (`samples` 심볼릭 링크를 영구 삭제하고, `sample/` 단일 물리 디렉토리만 사용하는 깔끔한 구조로 정돈)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 샘플 디렉토리 이중화 원인 분석 및 단일 표준 경로 지정 (Priority: P1)

시스템 운영자 및 훈련생은 훈련 플랫폼용으로 고도화된 실습 샘플 코드 수트(`sample_01`~`11`, `openai_01`~`11`, `common.py`, `config.json` 등)가 저장된 표준 실습 디렉토리 경로를 명확히 단일화하고, `sample` 및 `samples` 경로가 이중 생성되어 발생하던 참조 혼선을 근본적으로 해소할 수 있어야 한다.

**Why this priority**: 두 개의 서로 다른 이름의 디렉토리가 존재하면 패키지 압축, 환경 설정, 훈련생 전달 시 어떤 폴더를 참조해야 하는지 혼란을 유발하므로 주/부 경로 표준 확립이 가장 최우선 과제이다.

**Independent Test**: 실습 샘플 디렉토리 구조를 검사하여 실물 소스 파일이 존재하는 표준 물리 경로(Primary Real Directory)와 호환 경로(Compatibility Link/Target)의 관계를 명확히 확립하고, 두 경로 모두에서 동일한 최신 실습 코드가 100% 동일하게 접근 가능함을 입증한다.

**Acceptance Scenarios**:

1. **Given** `sample`과 `samples` 두 경로가 존재하는 프로젝트 환경에서, **When** 디렉토리 구조 분석 및 표준 경로 정의 프로세스가 실행될 때, **Then** 고도화된 실습 스크립트 22종 및 설정 파일이 포함된 표준 물리 디렉토리가 확정된다.
2. **Given** 훈련생 및 기존 스크립트가 `sample` 또는 `samples` 명칭을 혼용하여 참조할 때, **When** 경로 접근 시도가 일어날 때, **Then** 두 디렉토리 경로 모두에서 단 하나의 일관된 동일 자산 세트에 접근 가능하도록 통합 보장한다.

---

### User Story 2 - 빌드, 패키징 및 시드팩 파이프라인과의 정합성 통합 (Priority: P2)

엔지니어 및 배포 시스템은 시드팩 생성 스크립트(`make_seed_pack.sh`), 서버 구축 스크립트(`setup.sh`), README 안내 문서가 단일화된 샘플 디렉토리 표준 규칙에 맞춰 오류 없이 동작하도록 통합할 수 있어야 한다.

**Why this priority**: 시드팩(`vllm_serv_seed.tar.gz`) 번들링 시 샘플 폴더가 누락되거나 이중으로 포함되어 압축 용량이 불필요하게 증가하는 문제를 방지하기 위함이다.

**Independent Test**: `scripts/make_seed_pack.sh`를 실행하여 아카이브 생성 시 샘플 디렉토리가 정확히 1개 세트로 번들링되는지 검증한다.

**Acceptance Scenarios**:

1. **Given** 시드팩 생성 스크립트 실행 시, **When** `make_seed_pack.sh`가 수행될 때, **Then** `sample`/`samples` 중복 저장 없이 최신 고도화 샘플 1개 세트만 깨끗하게 타르볼에 포함된다.

---

### User Story 3 - 샘플 수트 자동화 테스트 수트 정합성 검증 (Priority: P3)

QA 엔지니어는 `pytest` 테스트 수트(`tests/test_sample_scripts.py`)가 통합된 샘플 디렉토리 구조를 올바르게 탐색하고 22종 샘플 스크립트의 구문 및 동적 바인딩을 부작용 없이 검증하는지 입증할 수 있어야 한다.

**Why this priority**: 경로 통합으로 인해 기존 테스트 수트의 모듈 임포트 실패나 회귀 오류가 발생하지 않음을 테스트로 증명해야 한다.

**Independent Test**: `uv run pytest tests/test_sample_scripts.py`를 실행하여 100% Green Pass를 확인한다.

**Acceptance Scenarios**:

1. **Given** 통합 정리된 샘플 디렉토리에 대해, **When** `uv run pytest tests/test_sample_scripts.py`를 실행할 때, **Then** 모든 테스트 케이스가 오류 없이 100% 통과한다.

---

### Edge Cases

- 기존 훈련생이나 레거시 가이드에서 `samples/` 경로 접근을 시도하는 경우: `sample/` 표준 경로를 사용하도록 가이드 문서(README.md) 업데이트 및 정돈.

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `sample` 및 `samples` 디렉토리 분석 완료 및 `samples` 심볼릭 링크 삭제 후 `sample/` 단일 물리 디렉토리로 통합
- **DoD-002**: `make_seed_pack.sh`, `setup.sh` 등 빌드/배포 스크립트에서 `sample/` 경로 참조 정합성 완료
- **DoD-003**: `uv run pytest tests/test_sample_scripts.py` 실행 시 전체 테스트 100% Pass 입증

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST `sample`과 `samples` 디렉토리의 이중화 원인을 분석하고 최신 고도화 실습 파일 22종이 수록된 `sample/` 물리 디렉토리를 유일한 표준 경로로 확정해야 한다.
- **FR-002**: System MUST 이중화 혼선을 제거하기 위해 임시 생성되었던 `samples` 심볼릭 링크를 안전하게 영구 삭제하고 `sample/` 단일 경로로 코드베이스를 정돈해야 한다.
- **FR-003**: System MUST `make_seed_pack.sh` 시드팩 생성 시 `sample/` 물리 디렉토리만 번들링에 포함시켜 이중 압축 오염을 방지해야 한다.
- **FR-004**: System MUST `sample/common.py` 및 `sample/config.json` 등 설정 파일이 `sample/` 단일 경로에서 정상 작동하도록 모듈 탐색 경로를 보장해야 한다.
- **FR-005**: System MUST `tests/test_sample_scripts.py` 테스트 수트가 `sample/` 경로를 탐지하여 구문 검증 및 IP 하드코딩 여부를 검사하도록 해야 한다.

### Key Entities

- **SampleDirectoryStructure**: 샘플 디렉토리 구조 엔티티 (표준 물리 경로 `primary_path`: `sample/`, 존재 상태 `is_unified`).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `samples` 심볼릭 링크 삭제 및 `sample/` 단일 물리 디렉토리 통합 완료 (중복 디렉토리/링크 0건).
- **SC-002**: `make_seed_pack.sh` 실행 시 생성되는 시드팩 타르볼 내 단일 `sample/` 디렉토리만 존재.
- **SC-003**: `uv run pytest tests/test_sample_scripts.py` 실행 성공률 100% 달성.

## Assumptions

- 훈련 플랫폼용 고도화 파일 22종(`sample_01`~`11`, `openai_01`~`11`)은 `sample/` 물리 디렉토리에 온전히 보존됨.
- 소스 코드(`src/`, `scripts/`) 내에는 `samples` 디렉토리를 직접 참조하는 부작용 코드가 없음.

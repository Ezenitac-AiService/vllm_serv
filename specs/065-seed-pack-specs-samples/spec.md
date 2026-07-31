# Feature Specification: 시드팩(Seed Pack) 패키징 시 명세서(specs/) 및 샘플 파일(samples/) 수록 포함 개선

**Feature Branch**: `065-seed-pack-specs-samples`

**Created**: 2026-07-31

**Status**: Draft

**Input**: User description: "시드팩에 추가되고 수정된 스펙들을 포함시키고, 샘플 파일도 포함"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Seed Pack 생성 시 `specs/`, `samples/`, `.legacy/` 디렉터리 아카이브 수록 (`scripts/make_seed_pack.sh`) (Priority: P1) 🎯 MVP

개발자 및 타 서버 이관 사용자는 `./make_seed_pack.sh` 스크립트를 통해 시드팩을 생성할 때, 대용량 가중치(`models/`)와 가상환경(`.venv/`)은 제외하면서도, 기능 명세서 문서(`specs/`), API 연동 샘플 코드(`samples/`), 그리고 레거시 스키마 모듈(`.legacy/`)이 아카이브 내에 빠짐없이 포함되어 타 시스템으로 이관 및 검증이 가능하도록 하길 원합니다.

**Why this priority**: 이관 대상 서버에서 최신 기능 명세서 및 5종 예제 파이썬 스크립트(`sample_01` ~ `sample_05`)를 바로 참조하고 즉시 구동 검증할 수 있도록 하는 시드팩 이관의 필수 요구사항입니다.

**Independent Test**: `./make_seed_pack.sh` 실행 후 아카이브(`dist/vllm_serv_seed.tar.gz`) 목록 조회 시 `specs/`, `samples/common.py`, `samples/sample_01_chat.py`, `.legacy/` 파일들이 포함되어 있는지 독립 검증합니다.

**Acceptance Scenarios**:

1. **Given** 프로젝트 루트에서 `./make_seed_pack.sh`를 실행할 때, **When** 패키징이 완료되면, **Then** 생성된 아카이브(`dist/vllm_serv_seed.tar.gz`)에 `specs/`, `samples/`, `.legacy/` 디렉터리 및 하위 파일이 올바르게 수록되어야 합니다.
2. **Given** 생성된 아카이브 검증 단계에서, **When** 아카이브 파일 목록을 탐색할 때, **Then** `samples/common.py` 및 `specs/` 파일 수록 여부를 자동 검증하고 성공 메시지를 표출해야 합니다.

---

### User Story 2 - 시드팩 검증 수트(`tests/unit/test_seed_pack.py`) 수록 항목 검증 보강 (Priority: P2)

QA 및 개발자는 단위/통합 테스트 수트 (`tests/unit/test_seed_pack.py`)를 통해 시드팩 생성 시 `samples/` 및 `specs/` 디렉터리가 정확히 포함되는지 자동 검증하길 원합니다.

**Why this priority**: 패키징 스크립트 변경 시 예제 코드 및 문서 누락을 테스트 단계에서 사전에 차단합니다.

**Independent Test**: `uv run pytest tests/unit/test_seed_pack.py` 실행 시 100% Pass 통과.

**Acceptance Scenarios**:

1. **Given** 단위 테스트 실행 시, **When** `test_seed_pack.py`의 아카이브 내용 검증 테스트가 수행되면, **Then** `samples/` 및 `specs/` 포함 여부를 검증하고 성공해야 합니다.

---

### Edge Cases

- 명세서(`specs/`)와 샘플(`samples/`)이 추가되어도 전체 시드팩 압축 용량이 경량(15MB 이내) 수준을 유지하는가?
- `--zip` 및 `.tar.gz` 두 포맷 모두에서 `specs/`, `samples/`, `.legacy/` 디렉터리가 동일하게 포함되는가?

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `scripts/make_seed_pack.sh`에서 `--exclude="specs"` 및 `--exclude=".legacy"` 제거 및 `samples/`, `specs/`, `.legacy/` 수록 보장
- **DoD-002**: `scripts/make_seed_pack.sh` 내 `samples/common.py` 및 `specs/` 아카이브 수록 검증 로직 추가
- **DoD-003**: `./make_seed_pack.sh` 실측 실행 및 `dist/vllm_serv_seed.tar.gz` 아카이브 내 `specs/`, `samples/` 포함 100% 검증
- **DoD-004**: 전체 pytest 회귀 테스트 수트(`uv run pytest tests/unit/test_seed_pack.py`) 100% Green Pass 통과

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `scripts/make_seed_pack.sh`는 아카이브 패키징 시 `specs/`, `samples/`, `.legacy/` 디렉터리를 제외 대상(`--exclude`)에서 완전히 제외하여 타르볼 및 ZIP 아카이브에 포함시켜야 합니다.
- **FR-002**: `scripts/make_seed_pack.sh`는 아카이브 생성 후 Post-Build 검증 단계에서 `samples/common.py` 및 `specs/` 수록 여부를 확인하고 수록 성공 로그를 출력해야 합니다.
- **FR-003**: `tests/unit/test_seed_pack.py` 수트는 시드팩 아카이브 내 `samples/` 및 `specs/` 디렉터리 및 하위 파일이 올바르게 존재하는지 검증해야 합니다.

### Key Entities

- **Seed Pack Archive Package**: `dist/vllm_serv_seed.tar.gz` (소스코드, 쉘스크립트, platform_profiles.json, wheels/legacy_i7_930, samples/, specs/, .legacy/ 수록)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `./make_seed_pack.sh` 실행 시 `dist/vllm_serv_seed.tar.gz` 내 `samples/` (6개 파일) 및 `specs/` (기능 명세 65종) 100% 수록
- **SC-002**: 시드팩 생성 단위 테스트 통과율 100%

## Assumptions

- `specs/` 및 `samples/` 포함 후에도 아카이브 전체 용량이 15MB 미만으로 유지됨.

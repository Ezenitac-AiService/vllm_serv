# Feature Specification: 코드베이스 리팩토링 및 레거시 파일 .legacy 디렉토리 격리 정돈 (026-archive-legacy-files)

**Feature Branch**: `026-archive-legacy-files`

**Created**: 2026-07-30

**Status**: Draft

**Input**: User description: "리펙토링과, 레거시 파일들 정리 / .legacy 폴더를 생성하고, 더이상 용도가 사라진 파일들을 이동"

## Clarifications

### Session 2026-07-30

- Q: 리팩토링 요구사항의 세부 대상 및 범위 → A: `src/` 및 `scripts/` 디렉토리 내 사용하지 않는 데드 코드(Dead Code), 미사용 임포트, 중복 유틸리티/헬퍼 로직을 깔끔히 정돈하고 모듈 구조의 가독성과 유지보수성을 높이는 코드 리팩토링 포함

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 프로젝트 루트 레거시 및 임시 파일 .legacy 아카이브 격리 (Priority: P1) 🎯 MVP

개발자 및 유지관리자가 루트 디렉토리를 탐색할 때, 더 이상 활성 파이프라인에서 직접 호출되지 않는 1회성 추출 스크립트(`ATEAM_ExtractionItem.py`, `BTEAM_ExtractionItem.py`), 불필요한 설치 파일(`get-pip.py`), 구형 벤치마크 결과(`benchmark_results.json`), 루트 스텁 셸 스크립트들을 루트 디렉토리에서 프로젝트 루트 `.legacy/` 디렉토리로 이동하여 루트 구조를 깔끔하게 정돈합니다.

**Why this priority**: 루트 디렉토리에 혼재된 레거시 스크립트와 임시 파일들을 격리하여 신규 개발자의 코드 탐색성을 높이고 프로젝트 진입점을 명확히 합니다.

**Independent Test**: `.legacy/` 디렉토리에 대상 레거시 파일들이 모두 안전하게 이동되었으며, `uv run pytest tests/` 실행 결과 기존 소스코드 및 테스트 수트 구동에 영향이 없음을 검증합니다.

**Acceptance Scenarios**:

1. **Given** 루트 디렉토리에 사용되지 않는 `ATEAM_ExtractionItem.py`, `BTEAM_ExtractionItem.py`, `get-pip.py`, `benchmark_results.json` 및 루트 셸 스텁 스크립트가 존재할 때, **When** 레거시 정리 작업이 수행되면, **Then** 해당 파일들이 `.legacy/` 경로로 안전하게 이동되어야 한다.
2. **Given** 레거시 파일들이 `.legacy/` 디렉토리로 이동된 후, **When** 파이썬 및 쉘 테스트 수트(`uv run pytest tests/`)가 실행되면, **Then** 100% 통과하여 레거시 이동이 시스템 동작을 저해하지 않아야 한다.

---

### User Story 2 - 소스코드 모듈화 및 코드베이스 리팩토링 (Priority: P1)

개발자가 코드를 읽거나 확장할 때, `src/` 및 `scripts/` 내의 미사용 임포트, 사용되지 않는 함수/클래스(Dead Code), 중복되거나 비효율적인 유틸리티 로직을 모듈화하여 정돈하고 코드 가독성 및 유지보수성을 극대화합니다.

**Why this priority**: 사용자 요청의 2가지 핵심 축 중 하나로, 아카이빙 정리와 더불어 소스코드 품질 및 아키텍처 정합성을 향상시키기 위한 필수 과제입니다.

**Independent Test**: `src/` 및 `scripts/` 내 중복/미사용 로직 정돈 후 `uv run pytest tests/` 실행 시 기능 손실 없이 테스트 100% 통과 가능합니다.

**Acceptance Scenarios**:

1. **Given** `src/` 및 `scripts/` 내에 미사용 임포트나 중복 헬퍼 로직이 존재할 때, **When** 리팩토링이 수행되면, **Then** 하위 호환성을 유지하면서 깔끔하게 모듈화 및 제거되어야 한다.
2. **Given** 리팩토링이 완료된 후, **When** 전체 단위 및 통합 테스트 수트가 실행되면, **Then** 회귀 오류(Regression Failure) 없이 100% 정상 작동해야 한다.

---

### User Story 3 - Git 및 .gitignore 아카이브 경로 보존 규정 적용 (Priority: P2)

`.legacy/` 디렉토리에 격리된 파일들이 Git 버전 관리에 정상적으로 포함되거나 필요 시 이력이 보존될 수 있도록 `.gitignore` 및 모듈 임포트 의존성 체크를 정비합니다.

**Why this priority**: 레거시 파일 보존 시 헌장 IV원칙(비파괴적 문서 및 코드 관리)을 준수하여 이력을 안전하게 아카이빙합니다.

**Independent Test**: `git status`에서 `.legacy/` 내 아카이빙된 파일들이 제대로 추적되는지 확인 가능합니다.

---

### Edge Cases

- `.legacy/` 디렉토리가 이미 존재하거나 중복 생성 시 무중단 연동
- 레거시 모듈을 간접 참조하는 코드가 존재할 경우 임포트 경로 깨짐 방지 사전 스캔
- 리팩토링 중 필요한 모듈/함수가 오삭제되지 않도록 pytest 검증 병행

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: 프로젝트 루트 경로에 `.legacy/` 디렉토리 생성 및 대상 파일(`ATEAM_ExtractionItem.py`, `BTEAM_ExtractionItem.py`, `get-pip.py`, `benchmark_results.json`, 루트 스텁 스크립트 등) 이동 완료
- **DoD-002**: `src/` 및 `scripts/` 소스코드 내 미사용 임포트, 중복/비효율 헬퍼 로직 리팩토링 및 모듈화 완료
- **DoD-003**: 레거시 파일 이동 및 소스코드 리팩토링 후 테스트 수트(`uv run pytest tests/`) 100% 통과
- **DoD-004**: `.gitignore` 및 프로젝트 빌드/실행 환경에서 `.legacy/` 디렉토리 및 소스 구조 정합성 검증

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 (.legacy 디렉토리 아카이브 체계 구축)**: 프로젝트 루트 위치에 `.legacy/` 디렉토리를 생성하고 용도가 다한 스크립트 및 더미/임시 파일들을 이동시켜 아카이빙해야 한다.
- **FR-002 (루트 레거시 파일 선택적 격리)**: `ATEAM_ExtractionItem.py`, `BTEAM_ExtractionItem.py`, `get-pip.py`, `benchmark_results.json` 및 루트 1줄 스텁 셸 스크립트들을 `.legacy/` 디렉토리 하위로 이동해야 한다.
- **FR-003 (코드베이스 리팩토링 및 중복/미사용 로직 정돈)**: `src/` 및 `scripts/` 디렉토리 내 사용하지 않는 헬퍼 코드, 미사용 임포트, 중복 유틸리티 함수를 정돈하고 모듈화하여 코드 구조를 슬림화해야 한다.
- **FR-004 (비파괴적 보존 및 파이프라인 정합성 보장)**: 레거시 이동 및 리팩토링 후 핵심 시스템(`src/`, `config/`, `scripts/`, `tests/`) 내의 임포트나 셸 스크립트 참조가 깨지지 않음을 보장해야 한다.

### Key Entities

- **LegacyArchiveDirectory**: `.legacy/` 아카이브 디렉토리 및 보존 파일 목록.
- **RefactoredCodebaseModule**: `src/` 및 `scripts/` 내 리팩토링된 모듈 구조.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 프로젝트 루트 핵심 파일 청결도 향상 (루트 혼잡 파일 7개 이상 아카이빙 격리)
- **SC-002**: 소스코드 리팩토링 및 미사용 임포트/코드 정돈 (코드베이스 가독성 및 유지보수성 향상)
- **SC-003**: 레거시 파일 이동 및 리팩토링 후 전체 테스트 수트 통과율 **100%**

## Assumptions

- `.legacy/` 디렉토리는 Git 버전 관리에 보존하여 이력을 누락하지 않는 비파괴적 방식으로 관리함.
- `src/` 내 핵심 애플리케이션 코드는 `ATEAM_ExtractionItem.py` 및 `get-pip.py`에 직접적인 런타임 의존성이 없음.

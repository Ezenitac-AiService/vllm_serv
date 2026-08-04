# Feature Specification: `scripts/` 디렉토리 스크립트 모듈화 및 결합도 완화 대대적 리팩토링 (`093-refactor-scripts-architecture`)

**Feature Branch**: `093-refactor-scripts-architecture`

**Created**: 2026-08-04

**Status**: Draft

**Input**: User description: "scripts/ 폴더의 스크립트들을 대대적인 리펙토링 진행하는 스펙 작성. 기존의 파일들을 나누거나, 혹은 병합하거나, 모듈화 하거나 하는 리펙토링을 진행하기 위해 분석을 시작해줘, 특히, 다른 폴더의 파일들을 참조하거나 호출하는 부분이 없는지 확인하고 있다면 연결성을 낮춰"

## Clarifications

### Session 2026-08-04

- Q: `scripts/` 하드코딩·중복·회피 로직 전수 정밀 리팩토링 범위 및 정책 → A: Option A (하드코딩 포트/경로 `config/` 단일 소스화 + 회피성 `|| true`/`2>/dev/null` 오염 정돈 + 중복 로직 `common.sh` 모듈화 종합 적용)
- Q: 다중 페르소나 분석 결과(SRE 안전 래퍼 & 설정 Cascade 우선순위)의 명세 통합 방식 → A: Option A (`try_optional_step` 안전 래퍼(FR-007) 및 포트 Cascade 우선순위(FR-008)를 명세서에 공식 추가 반영)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - `scripts/` 내 쉘/파이썬 스크립트의 외부 폴더 직결합 완화 및 모듈화 (Priority: P1) 🎯 MVP

시스템 관리자 및 프로젝트 개발자는 `scripts/` 하위의 유틸리티 및 제어 스크립트들이 외부 폴더(`src/`, `config/`, `data/`) 내부 파일 구성을 하드코딩 방식으로 결합하지 않고, 명확한 수식 파라미터화, 표준화된 믹스인(`common.sh`), 설정 객체를 통하도록 리팩토링되어 스크립트 단위 분리 및 재사용성이 크게 향상되기를 원한다.

**Why this priority**: 스크립트가 타 폴더 내부 구현 상세에 과도하게 의존할 경우 레포지토리 구조 변경 시 스크립트가 파손되거나 유지보수가 어려워지므로 결합도를 대폭 낮추어야 한다.

**Independent Test**: `scripts/` 내 각 스크립트를 독립 검사할 때 타 폴더 하드코딩 참조 경로가 제거되고, 파라미터화된 인터페이스나 믹스인을 통해 호출되는지 정적/동적 검증을 수행한다.

**Acceptance Scenarios**:

1. **Given** `scripts/` 디렉토리 내 유틸리티 스크립트들이 타 디렉토리(`src/`, `config/`)의 특정 내부 구현 파일에 직접 결합되어 있을 때, **When** 구조적 리팩토링을 적용하면, **Then** 공통 인터페이스 믹스인(`common.sh`) 또는 파라미터 주입 방식으로 결합도가 감소하고 가독성이 개선된다.
2. **Given** 분할/병합 및 모듈화 조치가 완료된 후, **When** 기존의 셋업 및 제어 명령어(`./setup.sh`, `./start_server.sh`, `./stop_server.sh`, `./status_server.sh`)를 가동하면, **Then** 기존 CLI 인터페이스의 변경 없이 동일하게 100% 정상 작동한다.

---

### User Story 2 - 비대 스크립트 모듈 분할 및 중복 코드 병합 (Priority: P2)

프로젝트 유지보수자는 800줄 이상으로 비대해진 `setup.sh` 등 주요 스크립트 내의 기능별 로직(방화벽 개방, 휠 검증, DB 초기화 등)이 단일 책임 원칙에 맞추어 깔끔한 서브 모듈 스크립트로 분리되거나 중복 로직이 믹스인으로 통합되어 유지보수성이 극대화되기를 원한다.

**Independent Test**: `setup.sh` 로직이 서브 헬퍼 함수/모듈로 명확히 분리되고 중복된 로깅 및 상태 검사 로직이 `common.sh`로 통일되었는지 검증한다.

**Acceptance Scenarios**:

1. **Given** 800줄 이상의 비대한 스크립트 로직에서, **When** 기능 단위(방화벽, CUDA 빌드, DB, 모델)별 서브 모듈화 및 믹스인 통합을 진행하면, **Then** 메인 스크립트의 코드 길이가 단축되고 가독성이 향상된다.

---

## Edge Cases & Error Handling *(mandatory)*

- 외부 소스 코드가 없는 미니멀 환경에서 스크립트 단독 실행 시: 명확한 파라미터 기본값 및 가이드 에러 메시지를 출력하고 예외 없이 종료.
- 기존 스크립트 호출 명령어과의 하위 호환성 유지: 루트 심볼릭 링크 및 기존 인자(`--skip-build`, `--wheel-path` 등)가 100% 정상 작동.

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `scripts/` 내 14개 전체 스크립트에 대한 외부 결합도 정밀 분석 리포트 수립 및 리팩토링 완료
- **DoD-002**: `common.sh` 쉘 공통 믹스인 강화 및 비대 로직 모듈 분할 완료
- **DoD-003**: 기존 셋업, 서버 가동, 시드팩 빌드 명령어 전체 100% 호환성 및 테스트 수트 통과 입증

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST `scripts/` 디렉토리 내의 모든 스크립트를 정밀 스캔하여 타 디렉토리(`src/`, `config/`, `data/`)와의 참조 결합도를 전수 분석해야 한다.
- **FR-002**: System MUST 외부 폴더 파일 직접 참조 로직 중 하드코딩된 결합을 파라미터화, 표준화된 믹스인(`common.sh`), 또는 명확한 구성 관리 인터페이스로 추상화하여 결합도를 대폭 낮추어야 한다.
- **FR-003**: System MUST `setup.sh` 등 비대해진 스크립트의 단일 책임 로직을 서브 모듈 스크립트/함수로 분할하고, 중복 로깅/에러 처리 코드를 `common.sh`로 통합해야 한다.
- **FR-004**: System MUST 기존 CLI 사용자 인터페이스(`./setup.sh`, `./start_server.sh`, `./stop_server.sh`, `./status_server.sh`, `make_seed_pack.sh`)의 인자, 동작 방식 및 서빙 호환성을 100% 보존해야 한다.
- **FR-005**: System MUST 리팩토링된 스크립트 구조 및 결합도 감소 검증을 위한 단위/통합 테스트 수트(`tests/test_script_architecture.py`)를 수립하고 100% 통과시켜야 한다.
- **FR-006**: System MUST `scripts/` 내 하드코딩된 포트 번호(8081, 8082, 8089, 8090, 8091) 및 경로를 `config/` 단일 진실 소스로 통일하고, 에러를 무작정 무시하는 회피성 로직(`|| true`, `2>/dev/null`)을 정밀 에러 반환 및 믹스인 핸들러로 치환해야 한다.
- **FR-007**: System MUST 방화벽 설정 및 옵셔널 패키지 헬퍼 구동 시 SRE 관점의 안전 래퍼 함수(`try_optional_step`)를 `common.sh`에 구현하여 non-fatal 에러 시 불필요한 전체 파이프라인 폭사를 방지해야 한다.
- **FR-008**: System MUST 포트 및 네트워크 구성을 조회할 때 DevSecOps Cascade 우선순위 (`CLI flag > Environment Variable (LLAMA_PORT) > config/server_config.json > Default`)를 엄격히 준수해야 한다.

### Key Entities

- **ScriptModuleDependency**: 스크립트 모듈 간 의존성 및 외부 폴더 결합도 상태 엔티티 (`script_name`, `external_refs`, `coupling_level`, `refactored_status`).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `scripts/` 내 스크립트들의 타 폴더 하드코딩 참조 건수 80% 이상 감소.
- **SC-002**: `setup.sh` 메인 스크립트 라인 수 및 복잡도 40% 이상 감소 (모듈화 분단 적용).
- **SC-003**: 기존 서빙 제어 스크립트 및 시드팩 빌드 호환성 테스트 성공률 100% 달성.

## Assumptions

- 기존 파이썬 런타임 환경(`uv`)이 정상 작동하며, 리팩토링 대상은 `scripts/` 내 쉘 스크립트 및 파이썬 헬퍼 스크립트임.

# Feature Specification: 학습 플랫폼 이관 코드 정밀 검토, 종합 테스트 및 구조적 리팩토링 (`090-audit-test-refactor`)

**Feature Branch**: `090-audit-test-refactor`

**Created**: 2026-08-04

**Status**: Draft

**Input**: User description: "새로운 스펙을 작성하는데, 테스트, 검증, 리펙토링이야 이 개발 플렛폼에서 088번까지 스펙 진행을 했는데, 학습 플렛폼에서 088번 스펙을 진행해서 그걸 가져왔어, 파일들이 혼재되어있는데, 상황을 정리, 검토,검증해야 해"

## Clarifications

### Session 2026-08-04

- Q: 학습 플랫폼 이관 중복/레거시 파일 처리 방침 → A: Option A (레거시/중복 파일을 `.legacy/` 아카이브 디렉토리로 안전하게 격리 이동 및 이력 보존)
- Q: 검증 테스트 수트의 GPU/CPU 하드웨어 환경 실행 방침 → A: Option B (엄격한 GPU 전용 환경 요구: CUDA GPU가 없는 플랫폼은 배제하며, GPU/CUDA 미장착 호스트인 경우 테스트 수트 즉시 Fail-Fast 실패 처리)
- Q: 파편화된 유틸리티 로직의 리팩토링 통합 구조 → A: Option A (이중 공통 모듈화: `src/utils/cuda_env.py` 파이썬 통합 모듈 + `scripts/common.sh` 쉘 공통 믹스인 구성을 통한 분리 및 중복 제거)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 학습 플랫폼 이관 코드 및 혼재된 자산 전수 조사/정리 (Priority: P1)

개발자 및 시스템 운영자는 학습 플랫폼에서 가져온 088번 스펙(llama.cpp 빌드 및 드라이버/CUDA 검증 설정, 샘플 코드 등)으로 인해 현재 개발 플랫폼 코드베이스에 혼재된 파이썬 모듈, 쉘 스크립트, 패키지 설정 파일, 빌드 아티팩트를 전수 조사하고, 정상 자산과 중복/임시 자산을 분류하여 체계적으로 정리할 수 있어야 한다.

**Why this priority**: 두 플랫폼 간 스펙 수행 결과물과 파일들이 충돌/혼재되면 런타임 오류나 빌드 비결정성이 발생하므로 자산 현황 파악 및 정리가 가장 최우선 과제이다.

**Independent Test**: `scripts/`, `src/`, `samples/`, `tests/`, `wheels/` 디렉토리 내 생성된 신규/변경 파일 목록 목록표(Inventory)를 작성하고, 무효하거나 이중 정의된 파일 및 불일치 요소를 100% 식별 및 격리 검증한다.

**Acceptance Scenarios**:

1. **Given** 학습 플랫폼에서 이관된 다양한 빌드 스크립트 및 모듈 파일들이 존재하는 환경에서, **When** 코드베이스 정밀 감사(Audit) 프로세스가 실행될 때, **Then** 각 파일의 출처, 정상 작동 여부, 중복 정의 여부를 정리한 전수 감사 리포트가 생성된다.
2. **Given** 동일하거나 충돌하는 역할을 수행하는 이중화된 파일(예: 구 버전 패키지 빌드 스크립트 vs 신규 스크립트)이 발견되었을 때, **When** 자산 정리 단계가 수행될 때, **Then** 레거시/중복 파일은 `.legacy/` 또는 적절한 아카이브 경로로 안전하게 이동 또는 통합된다.

---

### User Story 2 - 혼재 코드 검증 및 자동화 테스트 수트 구축 (Priority: P2)

엔지니어는 이관 및 정리된 모듈(llama.cpp GPU 가속 컴파일, CUDA/cuDNN 버전을 검증하는 `setup.sh`, `verify_wheel_binary.py`, OpenAI/httpx 샘플 코드 등)이 현재 개발 플랫폼 환경에서 부작용(Regression) 없이 정상 구동되는지 자동화 테스트를 통해 검증할 수 있어야 한다.

**Why this priority**: 코드 정리를 마친 후 기능 정상 동작(특히 GPU 오프로딩, 휠 바이너리 호환성, API 서빙)을 신뢰 가능한 단위/통합 테스트로 입증해야 안정적 서비스를 담보할 수 있다.

**Independent Test**: `pytest` 기반 종합 테스트 수트를 실행하여 드라이버/CUDA 버전 탐지, 휠 컴파일 검증, 샘플 스크립트 실행성 테스트가 100% 통과하는지 검증한다.

**Acceptance Scenarios**:

1. **Given** 이관된 CUDA/cuDNN 및 llama.cpp 관련 검증 로직에 대해, **When** 자동화 테스트(`pytest tests/`)를 실행할 때, **Then** 드라이버 버전 파싱, nvcc 호환성 체크, llama.cpp GPU 오프로드 검증 함수가 모두 성공 패스한다.
2. **Given** `samples/` 내 12종 실습 샘플 스크립트에 대해, **When** 구문 검사 및 동적 바인딩 테스트를 실행할 때, **Then** 하드코딩된 IP나 런타임 수신 오류 없이 설정(`config.json` / `.env`)을 정상 참조하여 실행 가능한 상태임을 입증한다.

---

### User Story 3 - 모듈 구조 개선 및 리팩토링 (Priority: P3)

시스템 아키텍트는 중복된 헬퍼 로직(예: GPU 탐지, 프로세스 제어, 환경 변수 로딩 등)을 파이썬 공통 모듈(`src/utils/cuda_env.py`) 및 쉘 믹스인(`scripts/common.sh`)으로 이중 추상화하고, 모듈 간 결합도를 낮추어 유지보수성을 극대화할 수 있어야 한다.

**Why this priority**: 파일 파편화를 방지하고 향후 새로운 스펙 추가 시 안정적으로 확장 가능한 깨끗한 구조(Clean Architecture)를 유지하기 위함이다.

**Independent Test**: 공통 모듈로 재구성된 코드베이스에 대해 린터(ruff/flake8) 및 타입 검사, 단위 테스트를 재실행하여 단 하나의 오류나 린트 경고 없이 깔끔하게 리팩토링되었음을 검증한다.

**Acceptance Scenarios**:

1. **Given** 여러 쉘 스크립트 및 파이썬 모듈에 파편화된 GPU/CUDA 버전에 관한 검사 로직이 존재할 때, **When** 리팩토링을 적용할 때, **Then** `src/utils/cuda_env.py` 및 `scripts/common.sh` 단일 공통 진입점 모듈로 유통 구조가 통합되고 기존 호출부들이 일관되게 치환된다.

---

### Edge Cases

- 학습 플랫폼에서 생성된 파일 중 기존 개발 플랫폼의 핵심 파일과 이름은 같으나 내용은 다른 충돌 파일이 존재하는 경우: 자동 덮어쓰기를 금지하고 차이점(diff) 분석 후 병합 정책 수립.
- CUDA GPU가 장착되지 않은 미지원 환경에서 검증 스크립트 실행 시: 타겟 플랫폼 요구사항 미달로 판단하여 안내 메시지 출력 후 테스트 수트 즉시 Fail-Fast 중단.

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: 학습 플랫폼에서 들여온 파일들에 대한 전수 Audit 결과 문서(혼재 목록, 이관/폐기 목록) 작성 완료
- **DoD-002**: `pytest`를 포함한 자동화 검증 수트 작성 및 전체 테스트 케이스 100% 통과 확인
- **DoD-003**: 중복 및 불필요 파일 정리, 공통 모듈화 리팩토링 적용 완료 및 코드 스타일/린트 검사 통과

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST 이관된 파일 및 디렉토리 구조에 대한 전수 감사(Audit)를 수행하고 혼재 상황 리포트를 생성해야 한다.
- **FR-002**: System MUST 충돌하거나 무효한 레거시/임시 파일들을 식별하고 정상 자산과 분리하여 `.legacy/` 디렉토리로 아카이빙해야 한다.
- **FR-003**: System MUST NVIDIA GPU 드라이버, CUDA Toolkit, cuDNN 버전을 정밀 탐지하는 로직 및 llama.cpp 휠 검증 로직에 대해 CUDA GPU 환경을 단정하는 단위/통합 테스트를 제공해야 한다.
- **FR-004**: System MUST `samples/` 디렉토리 내 12종의 샘플 코드(`sample_01`~`06`, `openai_01`~`06`)의 정상 작동 여부를 자동 검증하는 테스트 시나리오를 구비해야 한다.
- **FR-005**: System MUST 파편화된 유틸리티 함수(CUDA 탐지, 휠 스캔, 환경 설정 로딩)를 `src/utils/cuda_env.py` 및 `scripts/common.sh`로 이중 모듈화하여 리팩토링해야 한다.
- **FR-006**: System MUST 리팩토링 완료 후 기존 기능과의 하위 호환성(Regression)이 없음을 신규 통합 테스트 수트로 입증해야 한다.

### Key Entities

- **AuditInventoryItem**: 감사 대상 파일/모듈 엔티티 (파일명, 이관 출처, 검증 상태, 정리 조치 방향: Preserve/Archive/Refactor).
- **VerificationSuite**: 검증 항목 엔티티 (테스트 대상 모듈, 테스트 유형: Unit/Integration/E2E, 통과 여부).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 혼재된 이관 파일 중 검증되지 않거나 불필요한 레거시 자산을 100% 식별하고 정리 완료.
- **SC-002**: 새로 구축된 `pytest` 검증 수트 실행 시 전체 테스트 성공률 100% 달성.
- **SC-003**: 코드 중복 제거 및 리팩토링을 통해 중복 CUDA/시스템 탐지 함수 수를 50% 이상 감축하고 단일 진입점으로 통합.
- **SC-004**: 전체 테스트 수트 수행 시간이 30초 이내로 신속하게 완료되어 개발 생산성 유지.

## Assumptions

- 학습 플랫폼에서 가져온 코드 중 주요 기능(llama.cpp 빌드 수정, 드라이버/CUDA 검증 등)의 기본 소스코드는 가용 상태임.
- 검증 및 테스트는 NVIDIA CUDA GPU가 장착된 서빙/개발 호스트 환경에서 수행됨.
- 프로젝트 내 `pytest` 및 `uv` 도구가 이미 설치되어 가상환경 검증이 가능함.

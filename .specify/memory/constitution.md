<!--
Sync Impact Report:
- Version Change: 1.3.1 -> 1.4.0 (Enhanced Principles III, IV, V & Materialized Governance Framework for strict compliance, DoD criteria, and non-destructive editing)
- Modified Principles:
  - Principle III: Real-Execution & Parameterized Converge Validation (reordered for logical flow after TDD)
  - Principle IV: Definition of Done (expanded with explicit, testable DoD criteria)
  - Principle V: Non-Destructive Documentation Edit (clarified context preservation and append rules)
  - Principle VI: uv Environment & Package Management (reordered and reinforced strict `uv run` usage)
- Added Sections: Governance subsections (1. 개정 절차 및 버저닝 정책, 2. 준수성 검토 게이트, 3. 예외 관리 및 복잡도 추적)
- Removed Sections: None
- Templates Requiring Updates: .specify/templates/plan-template.md (✅ aligned)
- Follow-up TODOs: None
-->

# vllm_serv Constitution

## Core Principles

### I. 언어 정책: 한국어 출력 및 영어 추론 (Language Policy)
사용자와의 대화, 질문, 답변, 그리고 모든 작성 문서(작업 계획, 명세서, 과제 목록 등)는 반드시 한국어로 작성해야 합니다. 반면 시스템 내부의 생각(thought), 추론 및 사고 과정은 영어로 유지합니다.

### II. 실체적 테스트 주도 개발 및 품질 보증 (Strict Real Verification & Anti-Mock Discipline)
테스트 코드 없는 기능 구현은 엄격히 금지됩니다. 모든 코드 구현은 이를 검증할 수 있는 단위 테스트 혹은 통합 테스트와 함께 작성되어야 합니다. 목업(Mock) 테스트는 유료 외부 API 호출이 발생하거나 무료 티어의 제공량(Quota) 제한이 존재하는 경우에 한하여 제한적으로 예외 허용합니다. 그 외의 로컬 서비스, OS 방화벽, 소켓 바인딩, 프로세스 제어 테스트에서 가짜 더미 단정이나 무조건 성공 시뮬레이션으로 실체적 오류를 은폐하는 행위는 엄격히 금지합니다.

### III. 수렴 검증 시 실측 파라미터 및 실제 호출 플래그 준수 원칙 (Real-Execution & Parameterized Converge Validation)
예외적으로 목업이 허용되는 유료/제한적 API 테스트의 경우라도, 해당 테스트 코드에는 반드시 실제 호출 모드를 지정할 수 있는 매개변수 플래그(예: `REAL_API_CALL=1`, `--real-call`)가 포함되어야 합니다. 사용자가 실제 호출을 통한 테스트를 요청하거나 `converge` 및 최종 수렴 검증을 수행할 때에는 반드시 실제 호출 플래그를 활성화하여 물리 시스템, 커널 룰셋(`ufw/iptables`), 소켓 연결, 실제 모델 인스턴스 동작을 100% 실측 검증해야 합니다.

### IV. 작업 종료 조건 명확화 (Definition of Done)
작업의 세부 계획을 세우기 전, 반드시 작업의 종료(Done)에 대한 구체적이고 객관적이며 측정 가능한 정의를 먼저 확립해야 합니다. 종료 조건(DoD)은 단위/통합 테스트 통과, 스크립트 구문 검증(`bash -n`), 빌드 및 오프라인 호환성 검증 등 검증 가능한 단정 형태로 기술되어야 하며, 모호한 "구현 완료" 또는 단정문 없는 체크리스트는 인정되지 않습니다.

### V. 비파괴적 문서 수정 원칙 (Non-Destructive Documentation Edit)
모든 기존 문서(명세서, 계획서, 헌장, 과제 목록 등)의 수정 작업 시에는 명시적인 개정 대상 항목만을 선택적으로 수정해야 합니다. 기존의 배경 설명, 관련 문맥, 승인된 수순 및 기록을 무단으로 요약, 축소, 생략, 누락, 삭제하는 파괴적 편집(Destructive Edit)을 엄격히 금지하며, 변경 이력 및 정당성을 명확히 보존해야 합니다.

### VI. uv 패키지 및 환경 관리 원칙 (uv Environment & Package Management)
본 프로젝트는 `uv` 패키지 및 파이썬 가상환경 관리자를 표준 환경으로 사용합니다. 패키지 추가, 설치 및 환경 동기화 시에는 `pip`이나 임의의 패키지 매니저 대신 `uv add`, `uv sync`를 사용해야 하며, 모든 파이썬 스크립트 실행, 모듈 호출, pytest 테스트 수행 시에는 임의의 `PYTHONPATH` 지정 대신 `uv run` (예: `uv run pytest`, `uv run python ...`) 명령을 사용하여 격리된 가상환경 경로 및 패키지 정합성을 보장해야 합니다.

## Governance

본 헌장(Constitution)은 vllm_serv 프로젝트 내 모든 작업의 기반이 되는 최상위 헌법 규정입니다.

### 1. 개정 절차 및 버저닝 정책 (Amendment & Versioning Procedure)
- 헌장 개정 시 시맨틱 버저닝 규칙을 엄격히 적용합니다:
  - **MAJOR (x.0.0)**: 하위 호환성을 깨뜨리는 핵심 원칙의 폐지, 재정의 또는 개발 방침의 근본적 전환.
  - **MINOR (1.x.0)**: 새로운 원칙/섹션 추가, 기존 원칙의 실질적 지침 확장 및 거버넌스 절차 명시화.
  - **PATCH (1.3.x)**: 자구 수정, 오탈자 정정, 문맥 명확화 등 비실질적 다듬기.
- 헌장을 개정할 때에는 문서 최상단에 변경 이력(Sync Impact Report)을 주석으로 명시하고, 연관 템플릿 및 가이드 문서와의 정합성을 보장해야 합니다.

### 2. 준수성 검토 게이트 (Compliance Review Gates)
- 모든 기능 제안(spec), 계획(plan), 과제(tasks), 수렴 검증(converge) 단계에서 헌장 원칙을 필수 검토 항목(Gate)으로 평가해야 합니다.
- 헌장 게이트를 통과하지 못한 계획이나 구현은 다음 단계로 진행할 수 없습니다.

### 3. 예외 관리 및 복잡도 추적 (Exception Management & Complexity Tracking)
- 부득이한 사유로 헌장 원칙에 미치지 못하거나 예외 처리가 필요한 경우, 무단 적용을 금지하며 구현 계획서(`plan.md`)의 복잡도 추적(Complexity Tracking) 섹션에 위반 사유와 대안 기각 사유를 명시적으로 정당화해야 합니다.

**Version**: 1.4.0 | **Ratified**: 2026-07-09 | **Last Amended**: 2026-07-30

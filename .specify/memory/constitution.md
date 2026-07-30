<!--
Sync Impact Report:
- Version Change: 1.5.1 -> 1.5.2 (Formatting & Non-Destructive Wording Polish)
- Modified Principles:
  - Principle I ~ VI: Refined typography, bullet alignments, and section formatting with 100% content & detail preservation.
- Added Sections: None
- Removed Sections: None
- Templates Requiring Updates: .specify/templates/plan-template.md (✅ aligned)
- Follow-up TODOs: None
-->

# vllm_serv Constitution

## Core Principles

### I. 언어 정책: 한국어 출력 및 영어 추론 (Language Policy)
- **사용자 소통 및 문서화**: 사용자와의 대화, 질문, 답변, 그리고 모든 작성 문서(작업 계획서, 기능 명세서, 과제 목록 등)는 반드시 한국어로 작성해야 합니다.
- **내부 사유 과정**: 시스템 내부의 생각(thought), 추론 및 사고 과정은 영어(English)로 유지합니다.

### II. 실체적 연동 및 Real-Integration TDD 원칙 (Strict Real Verification & Real-Integration TDD Discipline)
1. **Fake Green(가짜 통과) 전면 금지**: TDD의 핵심인 Red-Green-Refactor 과정에서 테스트 코드나 구현 코드 어느 한쪽이라도 더미(Mock), 하드코딩된 시뮬레이션 응답, 조건 없는 가짜 데이터 반환을 사용하여 통과(Green) 상태를 만들어내는 행위는 TDD의 본질을 훼손하는 심각한 위반으로 간주합니다.
2. **구현 코드 더미 금지 (Zero Mock in Implementation Code)**: 대시보드 API, 인퍼런스 역방향 프록시, 플레이그라운드 등 애플리케이션 및 시스템 프로덕션 코드(`src/` 하위 포함) 내에서 하드코딩된 시뮬레이션 더미 텍스트, 가짜 응답(Dummy Payload/Mock String), 무조건 성공 처리된 임의의 데이터 리턴 행위는 엄격히 금지됩니다. 모든 비즈니스 로직 및 API 엔드포인트는 실제 C++ 백엔드 인퍼런스 엔진(`llama-server`), 실제 데이터베이스(`data/metrics.db`), 실제 소켓/프로세스 파이프라인과 100% 비동기 결합되어 실체적 결과를 전달해야 합니다.
3. **테스트 코드 실측 결합 (Real Verification in Test Code)**: 모든 코드 구현은 실제 로컬 서비스, OS 방화벽, 소켓 바인딩, DB 및 C++ 백엔드 파이프라인을 검증할 수 있는 통합 테스트 및 단위 테스트와 함께 작성되어야 합니다. 유료 외부 API 결제나 엄격한 Quota 제한이 존재하는 특수 케이스 외에는 로컬 자원을 가짜 더미 단정으로 은폐하는 행위를 금지하며, 오직 실제 연동 통과(Real Green)만을 완납 기준으로 인정합니다.

### III. 수렴 검증 시 실측 파라미터 및 실제 호출 플래그 준수 원칙 (Real-Execution & Parameterized Converge Validation)
- **매개변수 플래그 수록**: 예외적으로 목업이 허용되는 유료/제한적 API 테스트의 경우라도, 해당 테스트 코드에는 반드시 실제 호출 모드를 지정할 수 있는 매개변수 플래그(예: `REAL_API_CALL=1`, `--real-call`)가 포함되어야 합니다.
- **수렴 검증 실측 필수**: 사용자가 실제 호출을 통한 테스트를 요청하거나 `converge` 및 최종 수렴 검증을 수행할 때에는 반드시 실제 호출 플래그를 활성화하여 물리 시스템, 커널 룰셋(`ufw/iptables`), 소켓 연결, 실제 모델 인스턴스 동작을 100% 실측 검증해야 합니다.

### IV. 작업 종료 조건 명확화 (Definition of Done)
- **DoD 사전 확립**: 작업의 세부 계획을 세우기 전, 반드시 작업의 종료(Done)에 대한 구체적이고 객관적이며 측정 가능한 정의를 먼저 확립해야 합니다.
- **검증 가능한 단정 기술**: 종료 조건(DoD)은 단위/통합 테스트 통과, 스크립트 구문 검증(`bash -n`), 빌드 및 오프라인 호환성 검증 등 검증 가능한 단정 형태로 기술되어야 하며, 모호한 "구현 완료" 또는 단정문 없는 체크리스트는 인정되지 않습니다.

### V. 비파괴적 문서 수정 원칙 (Non-Destructive Documentation Edit)
- **선택적 이력 수정**: 모든 기존 문서(명세서, 계획서, 헌장, 과제 목록 등)의 수정 작업 시에는 명시적인 개정 대상 항목만을 선택적으로 수정해야 합니다.
- **맥락 및 기록 보존**: 기존의 배경 설명, 관련 문맥, 승인된 수순 및 기록을 무단으로 요약, 축소, 생략, 누락, 삭제하는 파괴적 편집(Destructive Edit)을 엄격히 금지하며, 변경 이력 및 정당성을 명확히 보존해야 합니다.

### VI. uv 패키지 및 환경 관리 원칙 (uv Environment & Package Management)
- **표준 가상환경 패키저**: 본 프로젝트는 `uv` 패키지 및 파이썬 가상환경 관리자를 표준 환경으로 사용합니다. 패키지 추가, 설치 및 환경 동기화 시에는 `pip`이나 임의의 패키지 매니저 대신 `uv add`, `uv sync`를 사용해야 합니다.
- **격리 명령어 지정**: 모든 파이썬 스크립트 실행, 모듈 호출, pytest 테스트 수행 시에는 임의의 `PYTHONPATH` 지정 대신 `uv run` (예: `uv run pytest`, `uv run python ...`) 명령을 사용하여 격리된 가상환경 경로 및 패키지 정합성을 보장해야 합니다.

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

**Version**: 1.5.2 | **Ratified**: 2026-07-09 | **Last Amended**: 2026-07-30

<!--
Sync Impact Report:
- Version Change: 1.3.0 -> 1.3.1 (Refined Principles II & VI: Restricted mock usage exclusively to paid/quota-limited APIs with mandatory real-call flags & user-requested real execution enforcement)
- Modified Principles: Principle II, Principle VI
- Added Sections: None
- Removed Sections: None
- Templates Requiring Updates: .specify/templates/plan-template.md (✅ updated)
- Follow-up TODOs: None
-->

# vllm_serv Constitution

## Core Principles

### I. 언어 정책: 한국어 출력 및 영어 추론
대화, 질문, 답변, 그리고 모든 문서 작성(작업 계획, 명세서 등)은 반드시 한국어로 작성해야 합니다. 반면 시스템 내부의 생각(thought), 추론, 사고 과정은 영어로 유지합니다.

### II. 실체적 테스트 주도 개발 및 품질 보증 (Strict Real Verification & Anti-Mock Discipline)
테스트 코드 없는 기능 구현은 엄격히 금지됩니다. 모든 코드 구현은 이를 검증할 수 있는 단위 테스트 혹은 통합 테스트와 함께 작성되어야 합니다. 목업(Mock) 테스트는 유료 외부 API 호출이 발생하거나 무료 티어의 제공량(Quota) 제한이 존재하는 경우에 한하여 제한적으로 예외 허용합니다. 그 외의 로컬 서비스, OS 방화벽, 소켓 바인딩, 프로세스 제어 테스트에서 가짜 더미 단정이나 무조건 성공 시뮬레이션으로 실체적 오류를 은폐하는 행위는 엄격히 금지합니다.

### III. 작업 종료 조건 명확화
작업의 세부 내용 계획을 세우기 전, 반드시 작업의 종료(Done)에 대한 구체적이고 측정 가능한 정의를 먼저 확립해야 합니다.

### IV. 비파괴적 문서 수정 원칙 (Non-Destructive Documentation Edit)
모든 기존 문서(명세서, 계획서, 헌장, 과제 목록 등)의 수정 작업 시에는 명시적인 수정 대상 항목만을 선택적으로 개정해야 하며, 기존 내용이나 문맥을 무단으로 요약, 축소, 생략, 누락, 삭제하는 파괴적 편집(Destructive Edit)을 엄격히 금지합니다.

### V. uv 패키지 및 환경 관리 원칙 (uv Environment & Package Management)
본 프로젝트는 `uv` 패키지 및 파이썬 가상환경 관리자를 표준 환경으로 사용합니다. 패키지 추가, 설치 및 환경 동기화 시에는 `pip`이나 임의의 패키지 매니저 대신 `uv add`, `uv sync`를 사용해야 하며, 모든 파이썬 스크립트 실행, 모듈 호출, pytest 테스트 수행 시에는 임의의 `PYTHONPATH` 지정 대신 `uv run` (예: `uv run pytest`, `uv run python ...`) 명령을 사용하여 격리된 가상환경 경로 및 패키지 정합성을 보장해야 합니다.

### VI. 수렴 검증 시 실측 파라미터 및 실제 호출 플래그 준수 원칙 (Real-Execution & Parameterized Converge Validation)
예외적으로 목업이 허용되는 유료/제한적 API 테스트의 경우라도, 해당 테스트 코드에는 반드시 실제 호출 모드를 지정할 수 있는 매개변수 플래그(예: `REAL_API_CALL=1`, `--real-call`)가 포함되어야 합니다. 사용자가 실제 호출을 통한 테스트를 요청하거나 `converge` 및 최종 수렴 검증을 수행할 때에는 반드시 실제 호출 플래그를 활성화하여 물리 시스템, 커널 룰셋(`ufw/iptables`), 소켓 연결, 실제 모델 인스턴스 동작을 100% 실측 검증해야 합니다.

## Governance

본 헌장(Constitution)은 프로젝트 내 모든 작업의 기반이 되는 최상위 규칙입니다.
- 모든 기능 제안, 명세, 계획, 구현 과정에서 위 원칙들을 검토하고 준수해야 합니다.
- 헌장 업데이트 시에는 문서 내의 버전 규칙을 따르며, 연관된 템플릿의 정합성을 보장해야 합니다.

**Version**: 1.3.1 | **Ratified**: 2026-07-09 | **Last Amended**: 2026-07-30

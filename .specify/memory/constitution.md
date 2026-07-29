<!--
Sync Impact Report:
- Version Change: 1.1.0 -> 1.2.0 (added Principle V: uv Environment & Package Management)
- Modified Principles:
  - V. uv 패키지 및 환경 관리 원칙 (New)
- Added Sections: None
- Removed Sections: None
- Templates Requiring Updates: None
- Follow-up TODOs: None
-->

# vllm_serv Constitution

## Core Principles

### I. 언어 정책: 한국어 출력 및 영어 추론
대화, 질문, 답변, 그리고 모든 문서 작성(작업 계획, 명세서 등)은 반드시 한국어로 작성해야 합니다. 반면 시스템 내부의 생각(thought), 추론, 사고 과정은 영어로 유지합니다.

### II. 테스트 주도 개발 및 품질 보증
테스트 코드 없는 기능 구현은 엄격히 금지됩니다. 모든 코드 구현은 이를 검증할 수 있는 단위 테스트 혹은 통합 테스트와 함께 작성되어야 합니다.

### III. 작업 종료 조건 명확화
작업의 세부 내용 계획을 세우기 전, 반드시 작업의 종료(Done)에 대한 구체적이고 측정 가능한 정의를 먼저 확립해야 합니다.

### IV. 비파괴적 문서 수정 원칙 (Non-Destructive Documentation Edit)
모든 기존 문서(명세서, 계획서, 헌장, 과제 목록 등)의 수정 작업 시에는 명시적인 수정 대상 항목만을 선택적으로 개정해야 하며, 기존 내용이나 문맥을 무단으로 요약, 축소, 생략, 누락, 삭제하는 파괴적 편집(Destructive Edit)을 엄격히 금지합니다.

### V. uv 패키지 및 환경 관리 원칙 (uv Environment & Package Management)
본 프로젝트는 `uv` 패키지 및 파이썬 가상환경 관리자를 표준 환경으로 사용합니다. 패키지 추가, 설치 및 환경 동기화 시에는 `pip`이나 임의의 패키지 매니저 대신 `uv add`, `uv sync`를 사용해야 하며, 모든 파이썬 스크립트 실행, 모듈 호출, pytest 테스트 수행 시에는 임의의 `PYTHONPATH` 지정 대신 `uv run` (예: `uv run pytest`, `uv run python ...`) 명령을 사용하여 격리된 가상환경 경로 및 패키지 정합성을 보장해야 합니다.

## Governance

본 헌장(Constitution)은 프로젝트 내 모든 작업의 기반이 되는 최상위 규칙입니다.
- 모든 기능 제안, 명세, 계획, 구현 과정에서 위 원칙들을 검토하고 준수해야 합니다.
- 헌장 업데이트 시에는 문서 내의 버전 규칙을 따르며, 연관된 템플릿의 정합성을 보장해야 합니다.

**Version**: 1.2.0 | **Ratified**: 2026-07-09 | **Last Amended**: 2026-07-29

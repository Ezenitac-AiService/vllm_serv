# Feature Specification: README.md 전면 재작성 (Rewrite README.md for LLM/Web Server & Operational Scripts)

**Feature Name**: `rewrite-readme-documentation`  
**Feature Directory**: `specs/115-rewrite-readme-documentation`  
**Status**: Draft  
**Created**: 2026-08-08  

## User Value & Business Need

기존 README.md에 포함되어 있던 에이전트 전용 도구/개발 프로세스 설명(Speckit 슬래시 커맨드, specs/ 폴더 구조 등)을 완전히 제거하고, `vllm_serv` 프로젝트 본연의 LLM 및 Web 서버 사용자/운영자를 위한 가이드로 전면 재작성합니다. 프로젝트 루트의 핵심 제어 쉘 스크립트 6종, `scripts/` 폴더 내의 주요 파이썬/쉘 유틸리티, 그리고 `src/` 아키텍처(LLM 서빙 엔진 및 웹 서비스/대시보드)에 대한 명확하고 실용적인 사용법과 문서화를 제공합니다.

---

## User Stories & Acceptance Scenarios

### Story 1: 에이전트 내부 개발 내용 제거 및 핵심 개요 정립 (Priority: P1) 🎯 MVP

**User Role**: `vllm_serv` 서버 운영자 및 개발자  

**As a** 서버 사용자 및 개발자  
**I want** README.md에서 에이전트 개발용 internal 기술(Speckit 워크플로우 등)이 제거되고, `vllm_serv` 프로젝트의 목적과 전체 기능 개요만 명확히 설명되기를 원한다.  
**So that** LLM 및 웹 서버 운영에 필요한 핵심 정보에 빠르게 집중할 수 있다.

#### Acceptance Scenarios

1. **Scenario 1.1: 에이전트 도구 설명 완전 제거**:
   - **Given**: 기존 README.md 파일
   - **When**: 새 README.md로 개편
   - **Then**: Speckit 명령어 사용법, agent 서브에이전트 가이드, specs 내부 폴더 구조 설명이 완전히 삭제된다.

2. **Scenario 1.2: vllm_serv 프로젝트 개요 명시**:
   - **Given**: 새로 작성된 README.md
   - **When**: 문서 상단 개요 읽기
   - **Then**: OpenAI 호환 LLM 서버, Web UI 대시보드, C++ CUDA 휠 자동 최적화 서빙 엔진의 핵심 가치가 명확히 전달된다.

---

### Story 2: 루트 제어 쉘 스크립트 6종 가이드 작성 (Priority: P1) 🎯 MVP

**User Role**: 타겟 플랫폼 마이그레이션 엔지니어 및 서버 관리자  

**As a** 서버 관리자  
**I want** 프로젝트 루트에 배치된 6대 핵심 쉘 스크립트의 역할과 사용 옵션이 상세히 서술되기를 원한다.  
**So that** 설치, 실행, 상태 확인, 중지, 마이그레이션 아카이브 생성을 손쉽게 수행할 수 있다.

#### Acceptance Scenarios

1. **Scenario 2.1: 루트 쉘 스크립트 6종 명세 수록**:
   - **Given**: README.md 문서를 참조
   - **When**: 루트 제어 스크립트 섹션 확인
   - **Then**: `make_seed_pack.sh`, `setup.sh`, `start_server.sh`, `status_server.sh`, `stop_server.sh`, `unpack_seed.sh` 각각의 역할, 실행 방법, 주요 CLI 인자(예: `--force-build`, `--wheel-path`, `--skip-benchmark` 등)가 표준 가이드로 포함된다.

---

### Story 3: scripts/ 유틸리티 및 src/ 아키텍처 설명 수록 (Priority: P2)

**User Role**: 시스템 개발자 및 아키텍트  

**As a** 서버 아키텍트  
**I want** `scripts/` 폴더 내 보조 스크립트들과 `src/` 아키텍처 구조가 체계적으로 설명되기를 원한다.  
**So that** 백엔드 LLM 엔진 연동 및 벤치마크/품질 측정 도구를 정확하게 이해하고 활용할 수 있다.

#### Acceptance Scenarios

1. **Scenario 3.1: scripts/ 보조 유틸리티 문서화**:
   - **Given**: `scripts/` 디렉터리 내 스크립트들 (`benchmark_context_window.py`, `benchmark_quality.py`, `verify_wheel_binary.py`, `ensure_models.py` 등)
   - **When**: README.md의 `scripts/` 설명 섹션 참조
   - **Then**: 각 스크립트의 기능과 실행 명령어 예시가 수록된다.

2. **Scenario 3.2: src/ 아키텍처 및 웹/LLM 서버 구조 문서화**:
   - **Given**: `src/` 디렉터리 구조 (`src/core/`, `src/api/`, `src/eval/`)
   - **When**: README.md의 System Architecture 섹션 참조
   - **Then**: LLM 프로세스 관리자, GPU/CPU 지원 자동 탐지기, FastAPI 기반 OpenAI 호환 엔드포인트 및 Web 대시보드 구조가 직관적으로 설명된다.

## Clarifications

### Session 2026-08-08

- Q: 새로 재작성할 README.md 상단에 3단계 빠른 시작 가이드(Quick Start) 섹션을 포함할까요? → A: README.md 상단에 3단계 Quick Start 가이드(setup.sh -> start_server.sh -> OpenAI API cURL 호출)를 명시하여 사용자 진입 장벽을 낮춘다.

---

## Functional Requirements (FR-###)

- **FR-001**: README.md에서 에이전트/Speckit 개발 워크플로우 및 `/speckit-*` 명령어 가이드를 완전히 제거해야 한다.
- **FR-002**: README.md에 루트 제어 쉘 스크립트 6종 (`make_seed_pack.sh`, `setup.sh`, `start_server.sh`, `status_server.sh`, `stop_server.sh`, `unpack_seed.sh`)의 구체적 설명, 사용법, 옵션 가이드를 작성해야 한다.
- **FR-003**: README.md에 `scripts/` 디렉터리의 보조 유틸리티 파이썬/쉘 파일들 (`benchmark_context_window.py`, `benchmark_quality.py`, `verify_wheel_binary.py`, `ensure_models.py` 등)의 역할 및 실행 방법을 수록해야 한다.
- **FR-004**: README.md에 `src/` 폴더 구조 기반의 LLM 서빙 엔진 (`src/core/`), 웹 API 및 대시보드 (`src/api/`), 품질 평가 (`src/eval/`)의 아키텍처 개요와 엔드포인트 가이드를 수록해야 한다.
- **FR-005**: README.md 상단에 3단계 Quick Start 가이드(setup -> start -> API cURL)를 수록하고 마크다운 표준 구문 및 아키텍처 다이어그램을 적용해야 한다.

---

## Success Criteria (SC-###)

- **SC-001**: README.md 내 에이전트/Speckit 관련 언급 0건 달성 (100% 서버/운영 가이드화).
- **SC-002**: 루트 스크립트 6종 및 주요 `scripts/` 유틸리티의 실행 명령 예시가 실제 작동하는 스크립트 경로 및 옵션과 100% 일치.
- **SC-003**: 마크다운 문법 오류 및 파손된 파일 링크 0건.

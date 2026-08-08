# Implementation Plan: README.md 전면 재작성 (Rewrite README.md for LLM/Web Server & Operational Scripts)

**Branch**: `115-rewrite-readme-documentation` | **Date**: 2026-08-08 | **Spec**: [specs/115-rewrite-readme-documentation/spec.md](spec.md)

**Input**: Feature specification from `/specs/115-rewrite-readme-documentation/spec.md`

## Summary

기존 README.md의 에이전트 전용 슬래시 커맨드/specs 내역을 완전히 제거하고, `vllm_serv` 프로젝트의 목적, 루트 6대 핵심 제어 쉘 스크립트, `scripts/` 디렉터리 유틸리티, 그리고 `src/` 아키텍처(LLM 서빙 엔진 & Web API/대시보드)에 관한 직관적이고 완성도 높은 운영 가이드로 전면 재작성합니다.

## Technical Context

**Language/Version**: Markdown (GFM Compliant), Mermaid  
**Primary Dependencies**: None (Standard Documentation)  
**Storage**: N/A  
**Testing**: `grep` check & `pytest` unit test suite  
**Target Platform**: GitHub / Markdown renderers  
**Project Type**: Server Documentation  
**Performance Goals**: N/A  
**Constraints**: Zero agent/speckit mentions, 100% Constitution v1.6.0 compliance  
**Scale/Scope**: 1 file (`README.md`) & test cases  

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] 계획서가 한국어로 작성되었는가? (언어 정책)
- [x] 테스트 코드 작성 계획이 포함되어 있는가? (테스트 필수 원칙)
- [x] 목업은 유료/제한 API로 엄격히 제한하고 실물 시스템/소켓/OS 인자 및 실제 호출 플래그(REAL_API_CALL=1) 기반 실측 검증 계획이 포함되어 있는가? (실체적 테스트 및 수렴 검증 원칙)
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (종료 조건 명확화 원칙)
- [x] 비파괴적 문서 수정 원칙을 준수하는가? (비파괴적 문서 수정 원칙)
- [x] uv 패키지 매니저 및 가상환경 격리 표준(uv run)을 준수하는가? (uv 패키지 및 환경 관리 원칙)
- [x] 전체 회귀 테스트 수트 및 Playwright 기반 E2E 브라우저 실측 검증 계획이 포함되어 있는가? (의무적 회귀 테스트 및 브라우저 E2E 검증 원칙)

## Project Structure

### Documentation (this feature)

```text
specs/115-rewrite-readme-documentation/
├── spec.md              # Feature specification with clarifications
├── plan.md              # Implementation plan (this file)
├── research.md          # Technical research & decisions (Phase 0)
├── data-model.md        # Document layout schema (Phase 1)
├── quickstart.md        # Integration & verification guide (Phase 1)
└── checklists/
    └── requirements.md  # Specification quality checklist
```

### Source Code (repository root)

```text
README.md                # Completely rewritten operational & architecture guide
```

**Structure Decision**: Single project layout updating `README.md`.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |

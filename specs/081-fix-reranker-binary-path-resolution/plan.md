# Implementation Plan: `llama-server` 네이티브 바이너리 경로 바인딩 (`081-fix-reranker-binary-path-resolution`)

**Branch**: `081-fix-reranker-binary-path-resolution` | **Date**: 2026-08-03 | **Spec**: [`spec.md`](file:///home/dev/storage/vllm_serv/specs/081-fix-reranker-binary-path-resolution/spec.md)

**Input**: Feature specification from `/specs/081-fix-reranker-binary-path-resolution/spec.md`

## Summary

서비스 플랫폼 서버에서 `ProcessManager.verify_and_build_llama_server()`가 `/usr/local/lib/ollama/llama-server` 경로를 감지하지 못해 파이썬 모듈(`llama_cpp.server`)로 폴백하고, 이에 따라 `/v1/rerank` 요청 시 404 Not Found가 발생하는 원인을 해결합니다. `candidates` 목록에 Ollama 네이티브 C++ 바이너리 경로를 추가하여 빌드 없이 기존 네이티브 바이너리로 즉시 연결합니다.

## Technical Context

**Language/Version**: Python 3.10+ (uv managed)

**Primary Dependencies**: subprocess, shutil, os, pytest

**Storage**: Local Filesystem (`/usr/local/lib/ollama/llama-server`)

**Testing**: pytest (`uv run pytest`)

**Target Platform**: Linux (x86_64, NVIDIA GPU: GTX 1070 8GB, GTX 1080 Ti 11GB, RTX 3060 12GB)

**Project Type**: Python Infrastructure Logic (Subprocess Binary Path Resolution)

**Performance Goals**: 바이너리 탐지 오버헤드 < 5ms, `/v1/rerank` 처리 성공률 100%

**Constraints**: Zero Mock 프로덕션 코드, 100% Real Verification, 빌드 없이 기존 네이티브 바이너리 활용

**Scale/Scope**: `src/core/process_manager.py` 바이너리 감지 함수 1곳 수정

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
specs/081-fix-reranker-binary-path-resolution/
├── spec.md              # Feature Specification
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 research artifact
├── data-model.md        # Phase 1 data model artifact
├── quickstart.md        # Phase 1 validation guide
├── contracts/           # Phase 1 API contract artifact
│   └── reranker-binary-contract.json
└── checklists/
    └── requirements.md  # Spec quality checklist
```

### Source Code (repository root)

```text
src/
└── core/
    └── process_manager.py     # verify_and_build_llama_server() 바이너리 경로 확장

tests/
└── unit/
    └── test_process_manager_binary_path.py   # 네이티브 바이너리 감지 단위 테스트
```

**Structure Decision**: 기존 Python 단일 서비스 구조(`src/core/process_manager.py`)의 `verify_and_build_llama_server()` 함수에 탐지 경로를 추가합니다.

## Complexity Tracking

> **Violations**: 없음 (모든 헌법 원칙 준수)

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| 없음 | N/A | N/A |

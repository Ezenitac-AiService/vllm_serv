# Implementation Plan: vllm_serv API 예제 샘플 스크립트 작성 (sample_01 ~ sample_05)

**Branch**: `063-sample-server-api-examples` | **Date**: 2026-07-31 | **Spec**: [spec.md](file:///home/dev/storage/vllm_serv/specs/063-sample-server-api-examples/spec.md)

**Input**: Feature specification from `specs/063-sample-server-api-examples/spec.md`

## Summary

본 계획서는 vllm_serv 개발 서버 백엔드(8081: 메인 LLM, 8090: BGE M3 임베딩, 8091: BGE Reranker v2 M3)에 대한 5대 대표 호출 시나리오(`sample_01_chat.py` ~ `sample_05_structured_output.py`) 예제 스크립트 모음을 `samples/` 디렉터리에 신설하고, `.legacy/ATEAM_ExtractionItem.py` 및 `.legacy/BTEAM_ExtractionItem.py` Pydantic 도메인 스키마를 재활용하여 정밀 구조화 데이터 추출까지 실측 검증하는 파이프라인 수립을 다룹니다.

## Technical Context

**Language/Version**: Python 3.11+, HTML5/JavaScript

**Primary Dependencies**: httpx, pydantic, pytest, vllm_serv (llama-server C++ backend)

**Storage**: SQLite (`data/metrics.db`), Local `.legacy/` schemas

**Testing**: pytest (`uv run pytest`) & python script direct execution (`uv run python samples/sample_XX.py`)

**Target Platform**: Linux (Ubuntu 22.04 LTS), NVIDIA GeForce GTX 1070 / GTX 1080 Ti

**Project Type**: Web Service & LLM/Auxiliary Inference Platform Client Examples

**Performance Goals**: 예제 스크립트 로컬 호출 응답 성공률 100%, 신규 개발자 가독성 100%

**Constraints**: `uv run` 파이썬 가상환경 격리 표준 준수, 한국어 문서화 및 주석 적용

**Scale/Scope**: 5개 예제 파일 모음 (`samples/sample_01_chat.py` ~ `sample_05_structured_output.py`)

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
specs/063-sample-server-api-examples/
├── spec.md              # Feature specification
├── plan.md              # Implementation plan (/speckit-plan command output)
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── sample-api-contract.json
└── checklists/
    └── requirements.md  # Specification quality checklist
```

### Source Code (repository root)

```text
samples/
├── sample_01_chat.py              # 01. 일반 채팅 호출 예제 (8081 /v1/chat/completions)
├── sample_02_model_params.py      # 02. 모델 & 파라미터(temperature, max_tokens, stop 등) 변경 예제
├── sample_03_embedding.py         # 03. BGE M3 임베딩 모델 호출 예제 (8090 /v1/embeddings)
├── sample_04_reranking.py         # 04. BGE Reranker v2 M3 호출 예제 (8091 /v1/embeddings 및 /rerank)
└── sample_05_structured_output.py # 05. ATEAM/BTEAM Pydantic 스키마 기반 구조화된 출력 파싱 예제

tests/
├── unit/
│   └── test_sample_scripts.py     # 5개 예제 스크립트 구문 및 서빙 연동 회귀 테스트 수트
```

**Structure Decision**: Single project layout with root `samples/` directory for executable example scripts and `tests/unit/` for regression validation.

## Complexity Tracking

*No violations.*

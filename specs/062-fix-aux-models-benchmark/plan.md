# Implementation Plan: 보조 모델(임베딩/리랭킹) 구동 및 품질 벤치마크 평가 개선

**Branch**: `062-fix-aux-models-benchmark` | **Date**: 2026-07-31 | **Spec**: [spec.md](file:///home/dev/storage/vllm_serv/specs/062-fix-aux-models-benchmark/spec.md)

**Input**: Feature specification from `specs/062-fix-aux-models-benchmark/spec.md`

## Summary

본 계획서는 BGE M3(`bge-m3`) 임베딩 모델의 `/v1/embeddings` 전용 추론 호환성 보장, BGE Reranker v2 M3(`bge-reranker-v2-m3`) Cross-Encoder 백엔드 인자(`--reranking`) 및 타임아웃 개선, 품질 벤치마크(`scripts/benchmark_quality.py`) 종료 후 독립 디태치 백그라운드 프로세스로 기본 다중 모델 그룹(`qwen3.5-4b`, `bge-m3`, `bge-reranker-v2-m3`) 서빙 상주(`RUNNING`) 복원, 백엔드 로딩 시 503 프리플라이트 응답 가드, 대시보드 API 호출 주소의 `window.location.origin` 동적 상대 경로 전환을 다룹니다.

## Technical Context

**Language/Version**: Python 3.11, C++ (llama.cpp / llama-server backend), HTML5/JavaScript (Vanilla JS Dashboard)

**Primary Dependencies**: FastAPI, httpx, llama-cpp-python, pydantic, pytest, pytest-playwright

**Storage**: SQLite (`data/metrics.db`), Local GGUF models (`models/`)

**Testing**: pytest (`uv run pytest`) & Playwright E2E browser tests

**Target Platform**: Linux (Ubuntu 22.04 LTS), NVIDIA GeForce GTX 1070 (8GB VRAM, CUDA 12.0)

**Project Type**: Web Service & LLM/Auxiliary Inference Platform

**Performance Goals**: BGE M3 임베딩 추론 성공률 100%, Reranker 서빙 READY 15초 이내, 벤치마크 후 메인/보조 상주 복원 100%, 대시보드 API 프록시 타임아웃 0%

**Constraints**: GPU VRAM 8192MB 환경 내 메인 LLM + 보조 모델 2종 Co-loading 총 메모리 점유 < 7500MB 유지

**Scale/Scope**: Catalog 8개 모델 수용, 3개 상주 서빙 모델 독립 복원 관리

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
specs/062-fix-aux-models-benchmark/
├── spec.md              # Feature specification
├── plan.md              # Implementation plan (/speckit-plan command output)
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── auxiliary-api-contract.json
└── checklists/
    └── requirements.md  # Specification quality checklist
```

### Source Code (repository root)

```text
src/
├── api/
│   ├── server.py
│   └── routes/
│       └── inference_api.py   # Preflight guard & proxy handling
├── core/
│   ├── process_manager.py     # llama-server CLI flags (--embedding, --reranking)
│   ├── auxiliary_manager.py   # Embedding/Reranker background residency & crash recovery
│   └── llama_manager.py       # LLM resident process management & detached restore
├── static/                    # Dashboard UI static HTML/JS assets (window.location.origin API paths)
scripts/
├── benchmark_quality.py       # 3D benchmark evaluation & task-specific inference
├── start_server.sh            # Main & auxiliary server daemon start script
└── status_server.sh           # Server liveness & hardware status report

tests/
├── unit/                      # ProcessManager & AuxiliaryModelManager unit tests
├── integration/               # Multi-model co-loading & endpoint integration tests
└── e2e/                       # Playwright browser E2E tests for dashboard UI
```

**Structure Decision**: Single project layout with `src/`, `scripts/`, `tests/` directories.

## Complexity Tracking

*No violations.*

# Implementation Plan: Codebase Refactoring, Modularity & Architecture Optimization

**Branch**: `specs/017-codebase-refactoring-cleanup` | **Date**: 2026-07-29 | **Spec**: [spec.md](file:///home/dev/storage/vllm_serv/specs/017-codebase-refactoring-cleanup/spec.md)

**Input**: Feature specification from `specs/017-codebase-refactoring-cleanup/spec.md`

---

## Summary

본 계획서는 `vllm_serv` 전체 파이썬 소스 코드 및 인프라의 하드코딩 완전 제거, Pydantic v2 기반 강타입 설정 관리 구축, `192.168.0.0/24` 사설 내부망 CIDR 접근제어 미들웨어 적용, 비동기 HTTP 싱글톤 커넥션 풀 일원화 및 `src/api` ➔ `src/core` ➔ `src/eval` 계층 간 모듈화를 달성하기 위한 구체적인 아키텍처 및 작업 설계를 정의합니다.

---

## Technical Context

**Language/Version**: Python 3.12+ (uv 가상환경)  
**Primary Dependencies**: FastAPI, Uvicorn, Pydantic v2, HTTPX, Pytest  
**Storage**: JSON 외부 설정 파일 (`config/model_catalog.json`, `config/server_config.json`) 및 local GGUF weights  
**Testing**: `uv run pytest -v` (단위, 통합, 인프라 서빙 테스트 수트)  
**Target Platform**: Linux Server (NVIDIA GPU GTX 1080 Ti 11GB VRAM)  
**Project Type**: High-Performance LLM Inference Serving Engine (OpenAI API Standard)  
**Performance Goals**: TTFT < 150ms, TPOT > 35 tok/s, 하드코딩 제거율 100%, 순환 참조 0건  
**Constraints**: VRAM 100% 오프로딩 검증 유지, 기존 OpenAI REST API 규격 100% 호환, 사설 내부망 CIDR (`192.168.0.0/24`) 접근 허용  
**Scale/Scope**: 6개 카탈로그 모델 (Gemma 4 3종, Qwen 3.5 3종), RAG 및 Agent 마이크로서비스 병렬 서빙  

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] 계획서가 한국어로 작성되었는가? (언어 정책)
- [x] 테스트 코드 작성 계획이 포함되어 있는가? (테스트 필수 원칙)
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (종료 조건 명확화 원칙)
- [x] 모든 파이썬 실행 및 테스트 구문이 `uv run`을 사용하는가? (uv 환경 및 패키지 관리 원칙)

---

## Project Structure

### Documentation (this feature)

```text
specs/017-codebase-refactoring-cleanup/
├── plan.md              # 본 구현 계획서
├── research.md          # Phase 0 리서치 문서 (Pydantic v2, CIDR Middleware, Singleton Pool)
├── data-model.md        # Phase 1 엔티티 및 클래스 다이어그램 (ServerConfig, IpSubnetGuard)
├── quickstart.md        # Phase 1 검증 가이드
└── contracts/           # Phase 1 스키마 계약 파일
    ├── config_api_contract.json
    └── subnet_filter_contract.json
```

### Source Code (repository root)

```text
config/
├── model_catalog.json
└── server_config.json

src/
├── api/
│   ├── routes/
│   │   └── inference_api.py
│   ├── middleware/
│   │   └── subnet_filter.py
│   └── server.py
├── core/
│   ├── config_manager.py
│   ├── gpu_detector.py
│   ├── llama_manager.py
│   ├── model_downloader.py
│   └── process_manager.py
└── eval/
    └── quality_evaluator.py

scripts/
├── setup.sh
├── start_server.sh
├── status_server.sh
└── stop_server.sh

tests/
├── unit/
├── integration/
└── infrastructure/
```

**Structure Decision**: Single Python project structure with modular layers (`src/api`, `src/core`, `src/eval`), external JSON configs (`config/`), and automated control scripts (`scripts/`).

---

## Complexity Tracking

*Constitution Check passed with zero violations.*

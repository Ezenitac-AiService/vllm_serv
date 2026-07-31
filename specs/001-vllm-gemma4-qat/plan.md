# Implementation Plan: llama.cpp 기반 Gemma4 모델군(2B/4B/12B) 양자화 서비스

**Branch**: `001-vllm-gemma4-qat` | **Date**: 2026-07-09 | **Spec**: [spec.md](file:///home/dev/vllm_serv/specs/001-vllm-gemma4-qat/spec.md)

**Input**: Feature specification from `/specs/001-vllm-gemma4-qat/spec.md`

## Summary

이 프로젝트는 11GB VRAM을 가진 GTX 1080 Ti 단일 하드웨어 환경에서 작동하는 텍스트 생성 서비스입니다. Gemma4의 2B, 4B, 12B 세 가지 양자화 모델(GGUF)을 기반으로 성능(VRAM, 응답 속도)을 실측하는 자동화 벤치마크 툴을 제공하고, 그 결과를 바탕으로 런타임에 모델을 로드하고 동적으로 전환(Switch)할 수 있는 llama-cpp-python 기반의 FastAPI 서버를 구축합니다. 단일 사용자 접속 최우선이며 최대 4K 컨텍스트를 지원하여 OOM을 방지합니다.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: `llama-cpp-python` (inference engine), `fastapi`, `uvicorn` (server wrapper), `huggingface_hub` (model downloading)

**Storage**: Local Filesystem (GGUF file storage)

**Testing**: `pytest`, `requests` (API integration tests)

**Target Platform**: Linux server (Ubuntu/Debian) with NVIDIA GTX 1080 Ti (Pascal, Compute Capability 6.1, 11GB VRAM)

**Project Type**: API web-service & CLI benchmark tool

**Performance Goals**: 
- 단일 유저 기준 OOM 방지 (에러율 0%)
- 벤치마크 스크립트를 통한 2B, 4B, 12B 성능 데이터 확보 및 TPOT 측정

**Constraints**: 
- GTX 1080 Ti 하드웨어 종속 (Tensor Core 없음, GGUF 필수)
- 최대 11GB VRAM 제한
- 컨텍스트 크기 최대 4096 토큰 제한

**Scale/Scope**: 
- 1 server (FastAPI wrapper)
- 3 models (Gemma4 2B/4B/12B GGUF)
- 단일 사용자 세션 보장

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] 계획서가 한국어로 작성되었는가? (언어 정책)
- [x] 테스트 코드 작성 계획이 포함되어 있는가? (테스트 필수 원칙)
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (종료 조건 명확화 원칙)

## Project Structure

### Documentation (this feature)

```text
specs/001-vllm-gemma4-qat/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (to be generated)
```

### Source Code (repository root)

```text
src/
├── core/
│   ├── llama_manager.py     # Llama 모델 인스턴스 래퍼 및 교체 로직
│   └── config.py            # 환경 변수 및 모델 설정
├── api/
│   ├── routes.py            # FastAPI 엔드포인트 (/v1/chat/completions, /api/models/switch)
│   └── server.py            # FastAPI 앱 초기화 및 서버 구동
└── scripts/
    ├── download_models.py   # 허깅페이스 GGUF 다운로드
    └── benchmark.py         # 3개 모델 VRAM/TPOT 측정 스크립트

tests/
├── integration/
│   └── test_api.py          # 모델 전환 및 텍스트 생성 테스트
└── unit/
    └── test_manager.py      # llama_manager 로직 테스트
```

**Structure Decision**: Option 1 (Single project) 패턴에 기반하여, FastAPI와 llama-cpp-python을 결합한 서버 아키텍처와 독립적인 벤치마크 스크립트 디렉토리를 분리 구성했습니다.

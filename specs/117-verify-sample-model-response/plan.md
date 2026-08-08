# Implementation Plan: sample 예제 스크립트 호출 모델 대 응답 모델 일치성 검증 및 하드코딩 제거 (Verify Sample Scripts Model Parity & Remove Hardcoded Values)

**Branch**: `117-verify-sample-model-response` | **Date**: 2026-08-08 | **Spec**: [`spec.md`](spec.md)

**Input**: Feature specification from `/specs/117-verify-sample-model-response/spec.md`

## Summary

`/home/dev/storage/vllm_serv/sample` 폴더 내의 모든 예제 및 공통 헬퍼 스크립트(`sample/common.py`, `sample_*.py`, `openai_*.py` 등)에서 요청 전송한 LLM 모델 ID와 API 서버 응답 페이로드 내 `model` 필드가 100% 일치함을 시각적·프로그램적으로 교차 검증하는 시스템을 구축합니다. 또한 소스 코드 상에 하드코딩되어 있던 IP 주소(`192.168.0.175`, `192.168.0.80`), 포트, 가용 모델 리스트, 더미 목업 텍스트를 전면 제거하고 `sample/config.json`을 단일 진실 출처(SSOT)로 수립하여 개발 플랫폼(`10.0.0.41`), 배포 환경(`192.168.0.175`), 로컬(`127.0.0.1`) 간 자동 탐색 및 동적 구성을 보장합니다.

## Technical Context

**Language/Version**: Python 3.12 (uv 패키지 환경)  
**Primary Dependencies**: FastAPI, Uvicorn, httpx, openai, llama-cpp-python  
**Storage**: Local GGUF Model Artifacts (`/models/`), Config JSON (`sample/config.json`)  
**Testing**: pytest (`uv run pytest tests/unit/`)  
**Target Platform**: Linux server (NVIDIA GPU CUDA 12.0+ / GTX 1080 Ti / RTX 3060 / Dev platform IP `10.0.0.41` / Prod IP `192.168.0.175`)  
**Project Type**: Web service (FastAPI Gateway) & Educational Sample Scripts (`sample/`)  
**Performance Goals**: 요청 모델 대 응답 모델 100% 일치 검증; `sample/` 내 파이썬 코드 하드코딩 매직 넘버/IP/목업 0건  
**Constraints**: `sample/config.json` 단일 진실 출처 준수, `sample/*.py` 내 하드코딩/더미 목업 전면 제거, IP 자동 탐색  
**Scale/Scope**: `sample/` 내 모든 예제 및 헬퍼 파일, `src/api/routes/inference_api.py`, `tests/unit/test_sample_model_switch.py`  

## Constitution Check

*GATE: Passed Phase 0 research & Phase 1 design.*

- [x] 계획서가 한국어로 작성되었는가? (언어 정책 준수)
- [x] 테스트 코드 작성 계획이 포함되어 있는가? (단위 테스트 `tests/unit/test_sample_model_switch.py` 수록)
- [x] 목업은 유료/제한 API로 엄격히 제한하고 실물 시스템/소켓/OS 인자 및 실제 호출 플래그 기반 실측 검증 계획이 포함되어 있는가? (하드코딩 더미 목업 전면 제거 및 실측 결합 원칙)
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (`sample/` 실행 시 모델 일치 검증 출력 및 하드코딩 0건 단정 테스트 통과)
- [x] 비파괴적 문서 수정 원칙을 준수하는가?
- [x] uv 패키지 매니저 및 가상환경 격리 표준(uv run)을 준수하는가?
- [x] 전체 회귀 테스트 수트 검증 계획이 포함되어 있는가?

## Project Structure

### Documentation (this feature)

```text
specs/117-verify-sample-model-response/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── chat_completions_model_contract.json
└── tasks.md             # Phase 2 output (to be created by /speckit-tasks)
```

### Source Code (repository root)

```text
src/
└── api/
    └── routes/
        └── inference_api.py    # MOCK 및 프록시 응답 내 requested model 반영

sample/
├── config.json                 # 단일 진실 출처 (IP 후보 목록, 포트, 모델 카탈로그, 타임아웃)
├── common.py                   # 동적 호스트 탐색 및 print_performance_summary 모델 일치 검증
├── sample_04_model_switch.py   # httpx 모델 스위칭 실측 및 응답 모델 일치 검증
└── openai_04_model_switch.py   # OpenAI SDK 모델 스위칭 실측 및 응답 모델 일치 검증

tests/
└── unit/
    └── test_sample_model_switch.py # 하드코딩 0건 검사 및 모델 일치성 단정 단위 테스트
```

**Structure Decision**: 단일 프로젝트 구조로서 기존 `src/api/routes/inference_api.py`, `sample/` 모듈군, `tests/unit/test_sample_model_switch.py`를 정제하여 구축함.

## Complexity Tracking

> **No violations**. Standard Asyncio, HTTPX, and Config JSON pattern used.

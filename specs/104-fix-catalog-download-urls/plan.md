# Implementation Plan: `config/model_catalog.json` HF 다운로드 URL 원인 분석, 리팩토링 및 404 오류 수렴 검증 (104-fix-catalog-download-urls)

**Branch**: `104-fix-catalog-download-urls` | **Date**: 2026-08-06 | **Spec**: [spec.md](file:///home/dev/storage/vllm_serv/specs/104-fix-catalog-download-urls/spec.md)

**Input**: Feature specification from `/specs/104-fix-catalog-download-urls/spec.md`

## Summary

`config/model_catalog.json` 내 404 Client Error가 발생하던 3개 모델(`gemma4-26b-a4b`, `qwen3.6-27b`, `qwen3.6-35b-a3b`)의 HuggingFace Hub `repo_id` 및 `filename` 경로를 실측 검증된 200 OK 경로로 리팩토링합니다. 모든 카탈로그 서빙 모델은 **Instruct (`it` / `Instruct`) 튜닝 `Q4_K_M` 양자화 GGUF 모델**이어야 하며, Gemma 4 텍스트 라인업 모델들(`gemma4-2b-text`, `gemma4-4b-text`, `gemma4-12b-text`, `gemma4-26b-a4b`)은 **비전 프로젝터가 제외된 텍스트 전용 (`requires_mmproj: false`, `clip_filename: null`)** 명세를 준수합니다. 또한 `tests/unit/test_model_downloader.py`에 14개 카탈로그 모델의 실체적 HF Hub HEAD HTTP 200 OK 무결성을 검증하는 TDD 수트를 추가하여 가짜 통과(Fake Pass)를 완벽히 차단합니다.

## Technical Context

**Language/Version**: Python 3.12.3

**Primary Dependencies**: `huggingface_hub`, `pytest`, `requests`/`urllib`

**Storage**: `config/model_catalog.json`

**Testing**: `pytest` (`uv run pytest tests/unit/`)

**Target Platform**: Linux (Ubuntu 22.04 LTS) / Python CLI

**Project Type**: Data Model Refactoring & TDD Verification Suite

**Performance Goals**: 14개 모델 HF Hub URL 조회 시 404 Error 0건 (100% 200 OK)

**Constraints**: `config/model_catalog.json` 기존 스키마 구조 100% 보존 및 Instruct 튜닝 `Q4_K_M` 양자화 규격 준수

**Scale/Scope**: 14개 모델 카탈로그 전체 메타데이터 및 테스트 수트

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
specs/104-fix-catalog-download-urls/
├── spec.md              # Feature specification
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   └── catalog-url-schema.json
└── checklists/
    └── requirements.md  # Spec quality checklist
```

### Source Code (repository root)

```text
config/model_catalog.json                   # 14개 카탈로그 모델 메타데이터 (repo_id, filename, Instruct & text-only 리팩토링)
scripts/ensure_models.py                    # 카탈로그 모델 다운로드 및 검사 CLI
src/core/model_downloader.py               # ModelDownloader 핵심 클래스

tests/unit/
├── test_model_downloader.py                # 실체적 HF Hub HEAD HTTP 200 OK TDD 검증 수트
└── test_ensure_models_cli.py               # CLI 옵션 및 --check-only 검증 수트
```

**Structure Decision**: `config/model_catalog.json` 내 HF 경로 및 Instruct/텍스트 전용 명세를 리팩토링한 후 `tests/unit/test_model_downloader.py`에 실체적 HTTP 200 OK 테스트를 추가합니다.

## Complexity Tracking

*Constitution Check violations: None.*

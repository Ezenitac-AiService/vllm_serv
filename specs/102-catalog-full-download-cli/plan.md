# Implementation Plan: `scripts/ensure_models.py` 전체/특정 모델 다운로드 CLI 옵션 확장 (102-catalog-full-download-cli)

**Branch**: `102-catalog-full-download-cli` | **Date**: 2026-08-05 | **Spec**: [spec.md](file:///home/dev/storage/vllm_serv/specs/102-catalog-full-download-cli/spec.md)

**Input**: Feature specification from `/specs/102-catalog-full-download-cli/spec.md`

## Summary

`scripts/ensure_models.py` CLI 옵션에 `--all` (전체 카탈로그 14개 모델 점검/다운로드) 및 `--model <MODEL_ID>` (특정 지정 모델 핀포인트 점검/다운로드) 옵션을 추가합니다.
`--all`과 `--model`이 동시 지정된 경우 상호 배타적 에러 메시지와 함께 exit code `2`로 즉시 종료하며, 존재하지 않는 무효한 모델 ID가 전달될 경우 exit code `1`로 프로세스를 차단합니다. 인자 없이 구동할 경우에는 기존 서빙/임베딩/리랭커 동적 필수 3종 모델 점검 파이프라인의 100% 하위 호환성을 보장합니다.

## Technical Context

**Language/Version**: Python 3.12.3 / Bash 5.2+

**Primary Dependencies**: `argparse`, `huggingface_hub`, `pydantic`

**Storage**: `config/model_catalog.json`, `config/server_config.json`

**Testing**: `pytest` (`uv run pytest tests/unit/`)

**Target Platform**: Linux (Ubuntu 22.04 LTS), NVIDIA GPU 타깃 서빙 파이프라인

**Project Type**: Python CLI Tool & Model Provisioning Pipeline

**Performance Goals**: CLI 옵션 해석 및 모델 타깃 리졸빙 < 50ms, 다운로드 진행률 콘솔 실시간 표시

**Constraints**: `--all` & `--model` 상호 배타적 에러 시 exit code 2, 무효 모델 ID 지정 시 exit code 1, 무인자 구동 시 기존 필수 모델 점검 100% 하위 호환

**Scale/Scope**: 14개 전체 모델 카탈로그 점검 및 개별/일괄 다운로드 관리

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
specs/102-catalog-full-download-cli/
├── spec.md              # Feature specification
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   └── ensure-models-cli-schema.json
└── checklists/
    └── requirements.md  # Spec quality checklist
```

### Source Code (repository root)

```text
config/
└── model_catalog.json               # 14개 전체 모델 메타데이터 정의

scripts/
└── ensure_models.py                 # CLI 파서 및 resolve_target_models 확장 구현

src/core/
└── model_downloader.py              # Single Source of Truth 카탈로그 및 다운로드 엔진

tests/
└── unit/
    └── test_ensure_models_cli.py    # CLI 옵션 파싱, 상호 배타성, 무효 ID 및 --all 유닛 테스트
```

**Structure Decision**: 기존 `scripts/ensure_models.py` CLI 및 리졸버 모듈을 모듈화 확장하며 `tests/unit/test_ensure_models_cli.py` 단위 테스트 수트를 신규 추가하여 기능 검증을 완납합니다.

## Complexity Tracking

*Constitution Check violations: None.*

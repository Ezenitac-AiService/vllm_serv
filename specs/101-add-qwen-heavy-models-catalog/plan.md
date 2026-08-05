# Implementation Plan: Qwen 및 Gemma 4 대형/양자화 모델 카탈로그 확장 및 제외 파이프라인 검증 (101-add-qwen-heavy-models-catalog)

**Branch**: `101-add-qwen-heavy-models-catalog` | **Date**: 2026-08-05 | **Spec**: [spec.md](file:///home/dev/storage/vllm_serv/specs/101-add-qwen-heavy-models-catalog/spec.md)

**Input**: Feature specification from `/specs/101-add-qwen-heavy-models-catalog/spec.md`

## Summary

`config/model_catalog.json`에 Qwen 3.6 (27B, 35B-A3B MoE), Gemma 4 (26B-A4B MoE), 및 Gemma 4 텍스트 전용 3종(2B/4B/12B) 등 총 6개 신규 모델 메타데이터를 추가하여 전체 카탈로그를 14개(LLM 12개 + Aux 2개)로 확장합니다.
또한, 11GB VRAM GTX 1080 Ti 하드웨어 환경에서 `./setup.sh --force-benchmark` 파이프라인 실행 시 18GB~24GB Base VRAM을 요구하는 3종의 대형 모델이 사전 Pre-flight VRAM 검증에 의해 `is_supported: false` 및 `CUDA OOM Risk`로 안전히 배제되고, 가용한 유효 최적 모델이 서빙 모델로 선택되어 파이프라인이 차질 없이 완료되는지 자동 검증합니다.

## Technical Context

**Language/Version**: Python 3.12.3 / Bash 5.2+

**Primary Dependencies**: `llama-cpp-python`, `huggingface_hub`, `pynvml`, `pytest`

**Storage**: `config/model_catalog.json`, `config/model_context_profiles.json`, `config/server_config.json`

**Testing**: `pytest` (`uv run pytest tests/unit/`)

**Target Platform**: Linux (Ubuntu 22.04 LTS), NVIDIA GPU (GTX 1080 Ti 11GB VRAM) & 차세대 24GB+ VRAM GPU 타깃

**Project Type**: Python CLI & Model Serving System

**Performance Goals**: 대형 모델 배제 진단 100ms 이내 완료, 유효 모델 TPS 평가 및 자동 서빙 선택 파이프라인 정상 보장

**Constraints**: Usable VRAM (Total VRAM - 500MB) 초과 시 사전 차단(`is_supported: false`), 프로세스 OOM/SIGKILL-9 예외 전이 방지

**Scale/Scope**: 14개 모델 카탈로그 관리, 12개 LLM 후보 모델 동적 로드 및 벤치마크 평가

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
specs/101-add-qwen-heavy-models-catalog/
├── spec.md              # Feature specification
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   └── model-catalog-schema.json
└── checklists/
    └── requirements.md  # Spec quality checklist
```

### Source Code (repository root)

```text
config/
├── model_catalog.json               # 14개 모델 정의 메타데이터 (6개 신규 추가)
├── model_context_profiles.json      # 벤치마크 진단 프로파일 결과
└── server_config.json               # 서빙 설정 파일

scripts/
├── benchmark_context_window.py      # LLM 12종 동적 로드 및 pre-flight OOM 배제 벤치마크
├── ensure_models.py                 # 카탈로그 무결성 검증 및 동적 모델 처리
└── setup.sh                         # 전체 환경 설정 및 --force-benchmark 파이프라인

src/
├── core/
│   ├── model_downloader.py          # HuggingFace Hub 다운로드 및 경로 매핑
│   └── process_manager.py           # Base VRAM 계산 및 가용 VRAM 한계 점검

tests/
└── unit/
    ├── test_model_downloader.py     # 카탈로그 매핑 단위 테스트
    └── test_benchmark_context_window.py
```

**Structure Decision**: 기존 단일 Python/Bash 서비스 구조를 그대로 준수하며 `config/model_catalog.json` 메타데이터 확장을 기반으로 `scripts/benchmark_context_window.py` 및 `src/core/model_downloader.py`가 동적 수용할 수 있도록 구성합니다.

## Complexity Tracking

*Constitution Check violations: None.*

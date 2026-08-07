# Implementation Plan: 컨텍스트 윈도우 크기 벤치마킹 고도화 및 헬스체크/초기화 진단 개선 (105-enhance-context-window-benchmark)

**Branch**: `105-enhance-context-window-benchmark` | **Date**: 2026-08-07 | **Spec**: [specs/105-enhance-context-window-benchmark/spec.md](spec.md)

**Input**: Feature specification from `/specs/105-enhance-context-window-benchmark/spec.md`

## Summary

본 구현 계획은 11GB VRAM (GTX 1080 Ti) 환경에서 소형/중형 LLM 모델의 컨텍스트 윈도우 한계가 `default_n_ctx` (4096) 캡과 헬스체크 타임아웃 오탐으로 인해 4096 이하로 저평가되는 문제를 해결합니다. 탐색 상한선을 `max_n_ctx` (기본 16384)로 상향하고, 헬스체크 폴링 타임아웃을 `n_ctx` 크기 및 GGUF 용량에 비례하여 동적으로 연장하며, 프로필 캐시 유실 방지를 위한 원자적 병합(Merge) 로직을 적용합니다.

## Technical Context

**Language/Version**: Python 3.12, C++20 (`llama-server`)

**Primary Dependencies**: `llama-cpp-python`, `httpx`, `asyncio`, `pydantic` v2, `uv`

**Storage**: `config/model_context_profiles.json`, `config/server_config.json`, `config/model_catalog.json`

**Testing**: `pytest`, `pytest-asyncio` (`uv run pytest`)

**Target Platform**: Linux server (Ubuntu 22.04 LTS), NVIDIA GeForce GTX 1080 Ti (11,264MB VRAM)

**Project Type**: Python backend service & CLI benchmarking module

**Performance Goals**: `n_ctx` 최대 16384 확장 탐색, 이진 탐색 오탐률 0%, 프로필 캐시 유실률 0%

**Constraints**: Usable VRAM (`total_vram - 500MB`), VRAM 사용률 92% 미만 트래핑, 60초 최대 헬스체크 타임아웃

**Scale/Scope**: 카탈로그 내 12개 후보 LLM 모델 실측 프로파일링

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
specs/105-enhance-context-window-benchmark/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── cli-contract.md
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
src/
├── core/
│   ├── process_manager.py        # poll_server_health 동적 타임아웃 계산
│   └── config_manager.py         # load/save_model_context_profiles 원자적 갱신
scripts/
├── benchmark_context_window.py   # 이진 탐색 max_n_ctx 캡 해제 및 range(5) 확장
└── benchmark_quality.py          # save_context_profiles_cache 원자적 병합 보존

tests/
├── unit/
│   ├── test_config_manager.py
│   └── test_process_manager.py
└── integration/
    └── test_benchmark_context.py
```

**Structure Decision**: 단일 파이프라인 리포지토리 구조로 `scripts/`와 `src/core/` 내 관련 모듈의 보완 및 관련 테스트 작성으로 구성합니다.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |

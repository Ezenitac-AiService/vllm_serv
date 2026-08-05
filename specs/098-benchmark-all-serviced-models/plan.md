# Implementation Plan: 서비스 대상 전체 LLM 모델 기반 컨텍스트 윈도우 스케일링 벤치마크 확장 (Step 4.5 Multi-Model Context Benchmark)

**Branch**: `098-benchmark-all-serviced-models` | **Date**: 2026-08-05 | **Spec**: [`spec.md`](file:///home/dev/storage/vllm_serv/specs/098-benchmark-all-serviced-models/spec.md)

**Input**: Feature specification from [`specs/098-benchmark-all-serviced-models/spec.md`](file:///home/dev/storage/vllm_serv/specs/098-benchmark-all-serviced-models/spec.md)

## Summary

본 구현 계획서는 `config/model_catalog.json`에 등록된 모든 서비스 대상 LLM 후보 모델에 대해 실제 GPU 프로세스를 스폰하여 실측 TPS 측정(Step 2.8) 및 2단계 이진 탐색 컨텍스트 윈도우 스케일링(Step 4.5)을 통합 수행하도록 벤치마크 파이프라인(`scripts/benchmark_context_window.py` 및 `scripts/setup.sh`)을 확장하는 아키텍처 및 구현 수순을 정의합니다.

주요 구현 요소:
1. `evaluate_all_catalog_models` 내에서 전체 LLM 후보 모델을 대상으로 실제 GPU 프로세스를 스폰하는 Real GPU Benchmark 및 이진 탐색 스케일링 통합 수행.
2. 개별 모델 벤치마크 시 120초 제한 타임아웃 적용 및 OOM/스폰 실패 시 `is_supported=False` 마킹.
3. 기존 캐시 파일(`config/model_context_profiles.json`) 대비 미등록 신규 모델 감지 시 부분 캐시 미스(Partial Cache Miss) 핀포인트 벤치마크 동기화.
4. `--force-benchmark` 미지정 시 캐시 파일 정합성 검증 후 5초 이내 고속 스킵 보존 처리.

## Technical Context

**Language/Version**: Python 3.11+, Bash (Linux Shell)

**Primary Dependencies**: `llama-cpp-python`, `httpx`, `asyncio`, `uv`, `pynvml` (NVIDIA Management Library)

**Storage**: SQLite (`data/metrics.db`), JSON Configuration Files (`config/model_catalog.json`, `config/model_context_profiles.json`, `config/server_config.json`)

**Testing**: `pytest`, `pytest-asyncio`, `pytest-playwright`, `bash -n`

**Target Platform**: Linux Server (NVIDIA GPU CUDA 가속 환경)

**Project Type**: Python & Shell Web Inference Service Pipeline

**Performance Goals**: `--force-benchmark` 미지정 시 캐시 스킵 5초 이내 완료, `--force-benchmark` 지정 시 개별 모델당 최대 120초 이내 안전 벤치마킹 완수

**Constraints**: GPU VRAM 안전 한계 92% 초과 시 OOM 감지, 비정상 멈춤 방지를 위한 프로세스 원자적 SIGKILL

**Scale/Scope**: `model_catalog.json` 내 전체 LLM 후보 모델(6종 이상) 대상 100% 실측 지원 및 100% 회귀 테스트 통과

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] 계획서가 한국어로 작성되었는가? (언어 정책: Constitution Principle I)
- [x] 테스트 코드 작성 계획이 포함되어 있는가? (테스트 필수 원칙: Constitution Principle II)
- [x] 목업은 유료/제한 API로 엄격히 제한하고 실물 시스템/소켓/OS 인자 및 실제 호출 플래그(REAL_API_CALL=1) 기반 실측 검증 계획이 포함되어 있는가? (실체적 테스트 및 수렴 검증 원칙: Constitution Principle II, III)
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (종료 조건 명확화 원칙: Constitution Principle IV)
- [x] 비파괴적 문서 수정 원칙을 준수하는가? (비파괴적 문서 수정 원칙: Constitution Principle V)
- [x] uv 패키지 매니저 및 가상환경 격리 표준(uv run)을 준수하는가? (uv 패키지 및 환경 관리 원칙: Constitution Principle VI)
- [x] 전체 회귀 테스트 수트 및 Playwright 기반 E2E 브라우저 실측 검증 계획이 포함되어 있는가? (의무적 회귀 테스트 및 브라우저 E2E 검증 원칙: Constitution Principle VII)

## Project Structure

### Documentation (this feature)

```text
specs/098-benchmark-all-serviced-models/
├── spec.md              # Feature specification
├── plan.md              # Implementation plan (this file)
├── research.md          # Phase 0 technical research output
├── data-model.md        # Phase 1 data model & state transition output
├── quickstart.md        # Phase 1 runnable validation guide
├── contracts/
│   └── cli-contract.md  # CLI interface schema & execution flow contract
└── checklists/
    └── requirements.md  # Spec quality checklist
```

### Source Code (repository root)

```text
scripts/
├── benchmark_context_window.py  # 4단계 모듈화 벤치마크 및 설정 반영 핵심 모듈 (다중 모델 실측 확장)
├── setup.sh                     # 원스톱 환경 구축 스크립트 (Step 2.8 및 4.5 다중 모델 실측 연동)
├── ensure_models.py             # 필수 GGUF 모델 가중치 검증 모듈
└── common.sh                    # 쉘 스크립트 공통 유틸리티

src/
├── core/
│   ├── process_manager.py       # LLM 백엔드 GPU 프로세스 라이프사이클 관리자
│   ├── config_manager.py        # 원자적 설정 및 프로필 JSON 입출력 관리자
│   └── gpu_detector.py          # NVML 기반 GPU VRAM 실시간 모니터링 모듈
└── api/
    └── server.py                # FastAPI 서빙 백엔드 엔드포인트

tests/
├── unit/                        # 단위 테스트
├── integration/                 # 실제 백엔드/GPU/프로세스 통합 테스트
└── e2e/                         # Playwright 기반 대시보드 브라우저 E2E 테스트
```

**Structure Decision**: 기존 `vllm_serv` 단일 시스템 및 스크립트 구조를 보존하며, `scripts/benchmark_context_window.py` 및 `scripts/setup.sh`를 중심으로 리팩토링 및 다중 모델 실측 파이프라인을 구축합니다.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| 없음 (None) | 헌법 원칙 100% 준수 | N/A |

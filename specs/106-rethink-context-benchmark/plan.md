# Implementation Plan: 컨텍스트 윈도우 벤치마킹 로직 전면 재검토 및 가용성 보장 (Rethink Context Benchmark Logic)

**Branch**: `106-rethink-context-benchmark` | **Date**: 2026-08-07 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/106-rethink-context-benchmark/spec.md`

## Summary

본 계획은 백그라운드 서버 구동 중 벤치마크 시 발생하는 OOM 크래시, 메인 서빙 프로세스 사살, 프로파일 전면 파괴(Destructive Overwrite) 및 `llama_cpp.server` 헬스체크 404 타임아웃 결함을 전면 해결하기 위한 결합 구조 재설계 계획입니다.

주요 해결 수단:
1. **실시간 NVML Free VRAM 동적 연산**: 고정 H/W 용량이 아닌 실시간 NVML 기반 가용 메모리(`free_vram_mb`)로 `usable_vram` 계산 및 OOM 사전 차단.
2. **`poll_server_health` 엔드포인트 폴백**: `/health` 조회 시 HTTP 404 응답을 받으면 즉시 `/v1/models` 엔드포인트를 폴백 조회하여 C++ `llama-server` 및 Python `llama_cpp.server` 양쪽 백엔드 호환 100% Readiness 보장.
3. **핀포인트 프로세스 정리 (Zero `pkill`)**: 와일드카드 `pkill -9 -f llama-server`를 전면 제거하고 8081 벤치마크 바인딩 포트 및 특정 자식 PID 기반 정밀 소켓/프로세스 정리로 전환.
4. **비파괴적(Non-destructive) 원자적 프로파일 저장**: 기존 정상 검증 프로파일이 존재하는 경우 벤치마크 실패 시 덮어쓰지 않고 안전 보존하며 원자적 파일 쓰기(`os.replace`) 적용.

## Technical Context

**Language/Version**: Python 3.11+ (`uv` 패키지 관리 환경)

**Primary Dependencies**: `httpx`, `asyncio`, `pynvml`, `llama-cpp-python` (`llama_cpp.server`)

**Storage**: `config/model_context_profiles.json`, `config/server_config.json` (원자적 JSON 저장)

**Testing**: `pytest`, `pytest-asyncio` (`uv run pytest`)

**Target Platform**: Linux Server (NVIDIA GPU / CUDA 12+ / GTX 1080 Ti 등)

**Project Type**: Python CLI & Async Subprocess Lifecycle Pipeline

**Performance Goals**: 백그라운드 서버 구동 중 벤치마크 실행 시 메인 서버 Downtime 0초, 헬스체크 폴링 지연시간 < 1초

**Constraints**: GPU VRAM 안전 마진 500MB 준수, 백그라운드 메인 서버(포트 8089/8090/8091) 프로세스 보호, 기존 검증 프로파일 파괴 금지

**Scale/Scope**: `config/model_catalog.json` 내 12개 후보 LLM 모델 실측 지원

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
specs/106-rethink-context-benchmark/
├── plan.md              # 본 현황 및 구현 계획서
├── research.md          # Phase 0 아키텍처 결함 분석 및 기술 결정서
├── data-model.md        # Phase 1 데이터 모델 및 스키마 검증 규칙
├── quickstart.md        # Phase 1 검증 및 E2E 테스트 실행 가이드
├── contracts/           # Phase 1 JSON 스키마 계약 파일
│   └── model_context_profiles_contract.json
└── tasks.md             # Phase 2 구현 과제 목록 (/speckit-tasks 생성)
```

### Source Code (repository root)

```text
src/
├── core/
│   ├── process_manager.py     # poll_server_health 폴백 및 핀포인트 프로세스 정리 수정
│   ├── gpu_detector.py        # NVML 실시간 free_vram_mb 스냅샷 연동
│   └── config_manager.py     # 원자적 프로파일 저장 로직
scripts/
└── benchmark_context_window.py # 실시간 가용 VRAM 동적 체크 및 비파괴적 프로파일 보존 수정

tests/
├── unit/
│   ├── test_process_manager.py
│   └── test_benchmark_context_window.py
└── integration/
    └── test_real_gpu_benchmark.py
```

**Structure Decision**: 기존 단일 프로젝트 가상환경 구조(`src/`, `scripts/`, `tests/`)를 유지하며 `ProcessManager` 및 `benchmark_context_window.py` 로직을 모듈화 개선한다.

## Complexity Tracking

*위반 항목 없음 (모든 헌장 원칙 100% 준수)*

# Implementation Plan: 동적 모델-KV 메모리 기반 벤치마크 탐색 구간 자동 산정 및 하드코딩 수치 전면 제거 (Dynamic Benchmark Range)

**Branch**: `107-dynamic-benchmark-range` | **Date**: 2026-08-07 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/107-dynamic-benchmark-range/spec.md`

## Summary

본 계획은 벤치마크 탐색 파이프라인 내 하드코딩 상수 수치(`16384`, `4096`, `3000MB`, `45.0 TPS`, `3000.0MB`)를 100% 제거하고, NVML 실시간 Free VRAM과 모델 아키텍처 명세(`max_n_ctx`)에 연동된 동적 탐색 상한선 연산엔진을 구축하며, `./stop_server.sh` 및 프로세스 정리 시 Python `llama_cpp.server` 및 백엔드 포트(8089, 8090, 8091) 핀포인트 사살을 통해 100% VRAM 완전 해제를 보장하는 구현 계획입니다.

주요 구현 전략:
1. **동적 상한선 연산 엔진 구축**:
   - `max_allocatable_n_ctx_from_real_vram`: NVML Free VRAM에서 `base_vram` 및 Dynamic Scratchpad safety margin ($\text{safety\_margin\_mb} = 500 + \lfloor n_{\text{ctx}} \times 0.05 \rfloor$)을 차감한 가용 용량으로 수용 가능한 512-알라인 최대 블록 컨텍스트 연산.
   - `high = min(model_max_n_ctx, max_allocatable_n_ctx_from_real_vram)` 적용.
2. **`stop_server.sh` & 소켓 사살 보강**:
   - `pgrep -f "llama_cpp.server"` 및 `fuser -k -9 8089/tcp 8090/tcp 8091/tcp` 추가로 Python 서빙 프로세스 및 포트 점유 100% 강제 해제.
   - TCP TIME_WAIT 소켓 해제 수렴 검증 및 NVML Free VRAM Settling Loop (연속 2회 Delta < 10MB 수렴 대기) 추가.
3. **실측 TPS 연산**:
   - 웜업 인퍼런스 API 응답 시간과 실제 토큰 반환 수를 기반으로 $TPS = \frac{\text{completion\_tokens}}{\text{elapsed\_seconds}}$ 연산 및 기록.

## Technical Context

**Language/Version**: Python 3.11+ (`uv` 패키지 관리 가상환경)

**Primary Dependencies**: `pynvml`, `httpx`, `asyncio`, `llama-cpp-python` (`llama_cpp.server`)

**Storage**: `config/model_context_profiles.json`, `config/server_config.json` (원자적 JSON 저장)

**Testing**: `pytest`, `pytest-asyncio` (`uv run pytest`)

**Target Platform**: Linux Server (NVIDIA GPU / CUDA 12+ / GTX 1080 Ti ~ H100)

**Project Type**: Python CLI & Async Subprocess Pipeline

**Performance Goals**: 100% 동적 상한선 산정 오차 0건, 서버 종료 시 VRAM 잔여 점유 0MB, 128K 컨텍스트 타임아웃 오진율 0%

**Constraints**: Constitution Principle II (Zero Hardcoding & Strict Real Verification) 100% 준수

**Scale/Scope**: `config/model_catalog.json` 내 12개 LLM 모델 실측 호환

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
specs/107-dynamic-benchmark-range/
├── plan.md              # 본 현황 및 구현 계획서
├── research.md          # Phase 0 기술 연구 및 동적 수식 검증서
├── data-model.md        # Phase 1 데이터 엔티티 명세
├── quickstart.md        # Phase 1 E2E 실측 검증 가이드
├── contracts/           # Phase 1 JSON 스키마 계약 파일
│   └── dynamic_range_contract.json
└── tasks.md             # Phase 2 구현 과제 목록 (/speckit-tasks 생성 대상)
```

### Source Code (repository root)

```text
src/
├── core/
│   ├── gpu_detector.py        # 동적 max_allocatable_n_ctx 역산식 및 NVML Settling Loop
│   ├── process_manager.py     # llama_cpp.server 및 8089/8090/8091 fuser 정밀 정리
│   └── config_manager.py     # 원자적 프로파일 저장
scripts/
├── benchmark_context_window.py # 하드코딩 매직 넘버전면 제거 및 동적 상한선 이진 탐색
└── stop_server.sh              # llama_cpp.server 및 8089/8090/8091 백엔드 포트 강제 사살 추가

tests/
├── unit/
│   ├── test_gpu_detector.py   # 동적 상한선 계산 파라메트릭 단위 테스트
│   ├── test_benchmark_context_window.py # 하드코딩 제거 및 실측 TPS 연산 단위 테스트
│   ├── test_process_manager_cleanup.py  # llama_cpp.server 및 포트 사살 단위 테스트
│   └── test_process_manager_health.py   # 헬스체크 폴백 단위 테스트
```

**Structure Decision**: 기존 단일 프로젝트 가상환경 구조(`src/`, `scripts/`, `tests/`)를 준수하며 하드코딩 수치를 100% 제거하는 리팩토링 및 모듈성을 적용한다.

## Complexity Tracking

*위반 항목 없음 (모든 헌장 원칙 100% 준수)*

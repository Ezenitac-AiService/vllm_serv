# Implementation Plan: setup.sh 폴리싱 및 GPU 모델 로드 실측 벤치마크 파이프라인 리팩토링 (099-fix-setup-gpu-benchmark)

**Branch**: `099-fix-setup-gpu-benchmark` | **Date**: 2026-08-05 | **Spec**: [`spec.md`](file:///home/dev/storage/vllm_serv/specs/099-fix-setup-gpu-benchmark/spec.md)

**Input**: Feature specification from `/specs/099-fix-setup-gpu-benchmark/spec.md`

## Summary

`./setup.sh --force-benchmark` 구동 시 백그라운드 `llama-server` 백엔드 프로세스의 GPU 오프로딩(`-ngl 99`) 스폰 실패, 포트 충돌, 또는 Ready 검증 미비로 인해 **nvtop 상에서 VRAM 할당 및 GPU 로드가 0%로 스킵되고 전체 후보 모델이 TPS: 0.0, Supported: False 처리되는 오동작을 근본 해결**합니다.
이를 위해 (1) `setup.sh` 초기 원자적 사전 서버 정돈(FR-006), (2) `ProcessManager` 내 `/health` 비동기 Polling 기반 Ready 검증(FR-002), (3) `--host 127.0.0.1` 보안 루프백 바인딩 및 SIGINT/Ctrl+C 자가 회수 데몬(FR-001, FR-003), (4) `setup.sh` Step 4.5 중복 강제 벤치마크 제거 및 스마트 스킵(FR-004), (5) Step 5 완료 후 서빙 자동 복구(FR-007)를 구현합니다.

## Technical Context

**Language/Version**: Python 3.12, Bash 5.2

**Primary Dependencies**: `src/core/process_manager.py`, `src/core/config_manager.py`, `scripts/benchmark_context_window.py`, `scripts/setup.sh`, `httpx` (비동기 HTTP 클라이언트), `llama-server` (C++ 백엔드 인퍼런스 엔진)

**Storage**: `config/model_context_profiles.json`, `config/server_config.json` (원자적 파일 교체: NamedTemporaryFile + `fsync` + `chmod 0o600` + `os.replace`)

**Testing**: `pytest`, `pytest-asyncio`, `bash -n` (셸 구문 검증)

**Target Platform**: Linux server (Ubuntu/Debian) with NVIDIA GPU (GeForce GTX 1080 Ti) & CUDA acceleration (`-ngl 99`)

**Project Type**: CLI / Web Service / Model Infrastructure Automation Pipeline

**Performance Goals**:
- 후보 LLM 모델 실측 TPS > 0.0 측정 및 nvtop상 GPU Util 100% / VRAM 상승 실측 관측
- `./setup.sh --force-benchmark` 구동 시간 40% 이상 단축 (Step 4.5 중복 구동 제거)

**Constraints**:
- 포트 8081 안전 해제 및 120초 비동기 타임아웃 준수
- 비파괴적 문서 수정 원칙 및 헌법 1~7조 원칙 준수

**Scale/Scope**: 6개 후보 LLM 모델 전수 실측 벤치마킹 및 전체 회귀 테스트 통과

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
specs/099-fix-setup-gpu-benchmark/
├── plan.md              # Implementation plan (this file)
├── research.md          # Phase 0 technical research & decisions
├── data-model.md        # Phase 1 data schema & entity definitions
├── quickstart.md        # Phase 1 runnable validation scenarios
├── contracts/           # Phase 1 interface specifications
│   └── cli-contract.md  # CLI, process & API interface contract
└── tasks.md             # Phase 2 task list (generated via /speckit-tasks)
```

### Source Code (repository root)

```text
src/
├── core/
│   ├── process_manager.py     # llama-server 스폰, -ngl 99, /health polling, signal/atexit cleanup
│   └── config_manager.py      # 원자적 프로필 저장 및 스키마 검증

scripts/
├── benchmark_context_window.py # 카탈로그 전체 모델 실측 벤치마크 & 웜업 파이프라인
└── setup.sh                    # Step 0 사전 서버 정돈, Step 2.8/4.5 스마트 스킵 및 Step 5 서빙 복구

tests/
├── unit/
│   ├── test_config_manager_profiles.py
│   ├── test_partial_cache_miss.py
│   └── test_setup_benchmark_integration.py
└── integration/
    ├── test_multi_model_benchmark.py
    ├── test_benchmark_timeout_fallback.py
    └── test_setup_benchmark_integration.py
```

**Structure Decision**: 기존 단일 모듈화 프로젝트 구조(`src/core/`, `scripts/`, `tests/`)를 활용하여 최소 침습 방식으로 개선합니다.

## Complexity Tracking

> 위반 사항 없음 (모든 헌법 규정 100% 준수)

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| 없음 | 해당 없음 | 해당 없음 |

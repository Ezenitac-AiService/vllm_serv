# Implementation Plan: 메인 서버-대시보드 프로세스 생명주기 원자적 동기화 (`077-sync-server-dashboard-lifecycle`)

**Branch**: `077-sync-server-dashboard-lifecycle` | **Date**: 2026-08-03 | **Spec**: [`spec.md`](spec.md)

**Input**: Feature specification from `/specs/077-sync-server-dashboard-lifecycle/spec.md`

## Summary

`vllm_serv` 시스템 구동/종료 제어 스크립트(`start_server.sh`, `stop_server.sh`, `status_server.sh`) 및 `scripts/setup.sh` 내 템플릿을 리팩토링하여 8081 메인 API 서버와 8082 웹 대시보드 서버의 생명주기를 완벽히 동기화합니다. 
Dual PID 파일(`vllm_serv.pid`, `vllm_dashboard.pid`), 30초 동시 Readiness 체크 및 실패 시 원자적 SIGKILL 롤백(Clean Exit), `stop_server.sh` 시 3중 잔여 프로세스(`src.api.server`, `uvicorn`, `llama-server`) 100% 강제 청소를 구현합니다.

## Technical Context

**Language/Version**: Python 3.12, Bash (POSIX Shell compatible)

**Primary Dependencies**: `uv`, `uvicorn`, `httpx`, Linux standard tools (`pgrep`, `ps`, `kill`, `curl`, `nvidia-smi`)

**Storage**: PID Files (`vllm_serv.pid`, `vllm_dashboard.pid`), Log Files (`logs/server.log`, `logs/dashboard.log`)

**Testing**: `pytest`, `pytest-asyncio`, `pytest-playwright`, `bash -n`

**Target Platform**: Linux server (Ubuntu/Debian/CentOS) with NVIDIA GPU & CUDA

**Project Type**: Model Serving & Web Control Dashboard System

**Performance Goals**: Readiness check timeout within 30s; Process termination within 5s

**Constraints**: Zero-mock real execution verification; `uv run` isolation compliance

**Scale/Scope**: Target scripts (`start_server.sh`, `stop_server.sh`, `status_server.sh`, `scripts/setup.sh`) and tests (`tests/integration/`, `tests/unit/`, `tests/e2e/`)

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
specs/077-sync-server-dashboard-lifecycle/
├── plan.md              # Implementation plan
├── research.md          # Technical research & design decisions
├── data-model.md        # Process control entities & state transitions
├── quickstart.md        # Runnable validation guide
├── contracts/           # Interface contracts (process-lifecycle-contract.json)
└── checklists/          # Specification quality checklists (requirements.md)
```

### Target Source Code Layout

```text
scripts/
├── start_server.sh      # Dual PID tracking & 30s atomic readiness rollback
├── stop_server.sh       # 3-tier process cleanup & VRAM release
├── status_server.sh     # Separated process & DOM health reporting
└── setup.sh             # Synchronized HEREDOC templates & chmod +x enforcement

start_server.sh -> scripts/start_server.sh (root symlink)
stop_server.sh -> scripts/stop_server.sh (root symlink)
status_server.sh -> scripts/status_server.sh (root symlink)

tests/
├── integration/
│   └── test_dual_port_readiness.py  # Dual-port readiness & atomic rollback tests
├── unit/
│   └── test_shell_scripts.py        # Shell script syntax & process control tests
└── e2e/
    └── test_dashboard_e2e.py        # Playwright E2E browser & Port 8082 tests
```

**Structure Decision**: Standard single project layout for `vllm_serv` control scripts and test suite.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

*(No constitution violations. All core principles satisfied.)*

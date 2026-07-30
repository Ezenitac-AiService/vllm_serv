# Implementation Plan: ufw 방화벽 권한 점검, 바이너리 재빌드 스킵 및 컨텍스트 스케일링 캐싱 (040-ufw-sudo-detection-fix)

**Branch**: `040-ufw-sudo-detection-fix` | **Date**: 2026-07-30 | **Spec**: [spec.md](file:///home/dev/storage/vllm_serv/specs/040-ufw-sudo-detection-fix/spec.md)

**Input**: Feature specification from `specs/040-ufw-sudo-detection-fix/spec.md`

## Summary

1. `setup.sh`, `configure_firewall.sh`, `FirewallManager`에서 `sudo ufw status` 및 `sudo -n ufw status` fallback 기반 2단계 상태 조회 시스템을 구축하여 권한 부족으로 인한 ufw 방화벽 오감지/타 엔진 분기를 방지.
2. `setup.sh` 소스 컴파일 실행 직전단계(Pre-Check)에서 `.venv` 내 CUDA 가속 바이너리(`llama_supports_gpu_offload()`)를 사전 점검하여, 정상 작동 시 8분 컴파일 구문 자체를 100% Bypass하고 3초 내 완납.
3. `make_seed_pack.sh` & `verify_wheel_binary.py` 내 shared library(`.so`) zip entry 경로 탐색 개선 및 `config/model_context_profiles.json` 타겟 서버 하드웨어 독립성 보장을 위한 압축 제외(`--exclude`) 수록.
4. CLI(`scripts/benchmark_quality.py`, `setup.sh`) 및 웹 UI (Port 8089 대시보드 `POST /api/benchmark/rerun`) 양쪽 모두에서 차분/전수 컨텍스트 윈도우 스케일링 벤치마킹 재측정 지원 Dual 인터페이스 구현.

## Technical Context

**Language/Version**: Python 3.10+, Bash (POSIX compatible)  
**Primary Dependencies**: uv, llama-cpp-python, FastAPI/Starlette (Web Dashboard), pytest  
**Storage**: JSON file cache (`config/model_context_profiles.json`, `config/model_catalog.json`)  
**Testing**: pytest (Strict Anti-Mock real execution verification)  
**Target Platform**: Linux server (Ubuntu/Debian, CentOS/RHEL/Rocky)  
**Project Type**: CLI scripts + Web service  
**Performance Goals**: `setup.sh` 2회차 연속 구동 소요시간 <3초, 방화벽 감지 오인율 0%  
**Constraints**: 헌법 v1.4.0 (Strict `uv run`, Anti-Mock discipline, Non-destructive edits)  
**Scale/Scope**: Multi-OS firewall support (ufw, firewalld, nftables, iptables)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] 계획서가 한국어로 작성되었는가? (언어 정책)
- [x] 테스트 코드 작성 계획이 포함되어 있는가? (테스트 필수 원칙)
- [x] 목업은 유료/제한 API로 엄격히 제한하고 실물 시스템/소켓/OS 인자 및 실제 호출 플래그(REAL_API_CALL=1) 기반 실측 검증 계획이 포함되어 있는가? (실체적 테스트 및 수렴 검증 원칙)
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (종료 조건 명확화 원칙)
- [x] 비파괴적 문서 수정 원칙을 준수하는가? (비파괴적 문서 수정 원칙)
- [x] uv 패키지 매니저 및 가상환경 격리 표준(uv run)을 준수하는가? (uv 패키지 및 환경 관리 원칙)

## Project Structure

### Documentation (this feature)

```text
specs/040-ufw-sudo-detection-fix/
├── spec.md              # Feature specification
├── plan.md              # Implementation plan (this file)
├── research.md          # Phase 0 research decisions
├── data-model.md        # Phase 1 entity & cache definitions
├── quickstart.md        # Phase 1 validation guide
├── contracts/           # Phase 1 contracts
│   └── benchmark-api.json # OpenAPI spec for Port 8089 web benchmark endpoint
└── checklists/
    └── requirements.md  # Requirements checklist (100% passing)
```

### Source Code (repository root)

```text
scripts/
├── setup.sh                 # Multi-OS firewall detection, Pre-check build bypass, Context benchmark cache check
├── configure_firewall.sh    # Sudo-aware firewall helper script
├── make_seed_pack.sh        # Archive creation with --exclude="config/model_context_profiles.json"
├── verify_wheel_binary.py   # Improved .so shared library path pattern inspection
└── benchmark_quality.py     # Context window scaling benchmark engine & incremental update logic

src/
├── core/
│   └── firewall_manager.py  # Python FirewallManager with sudo -n ufw status fallback
└── web/
    └── dashboard.py         # Port 8089 Web Dashboard API endpoints (GET/POST benchmark profiles & rerun)

tests/
├── unit/
│   ├── test_firewall_manager.py
│   ├── test_firewall_manager_real.py
│   └── test_shell_scripts.py
```

**Structure Decision**: Single project layout with Python backend core (`src/`), management scripts (`scripts/`), pytest test suite (`tests/`), and feature specification directory (`specs/040-ufw-sudo-detection-fix/`).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

*No violations. All principles and gates pass.*

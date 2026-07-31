# Implementation Plan: 이관 서버 환경 setup.sh Fast-Track 검증 예외 안전성 및 소스 컴파일 Fallback 보장 (055-fix-migration-setup-fallback)

**Branch**: `055-fix-migration-setup-fallback` | **Date**: 2026-07-31 | **Spec**: [spec.md](file:///home/dev/storage/vllm_serv/specs/055-fix-migration-setup-fallback/spec.md)

**Input**: Feature specification from `specs/055-fix-migration-setup-fallback/spec.md` & log analysis from `log.txt`

---

## Summary

서비스 플랫폼 타겟 서버(Intel i7-930 + GTX 1070) 마이그레이션 중 `setup.sh` 실행 시 Fast-Track 사전 빌드 휠 GPU 가속 검증 서브쉘(`GPU_CHECK_OUTPUT=$(uv run python ...)`)에서 발생한 `set -e` 파이프라인 강제 종료 버그를 수정합니다. `|| true` 파이프라인 가드를 적용하여 검증 실패 시에도 스크립트 중단 없이 원인을 캡처하고, 결정론적 4단계 우선순위(CLI `--wheel-path` → `.venv` 캐시 → `wheels/` 번들 → C++ 소스 컴파일)와 3중 하드웨어 정합성 검증(CPU SIMD, CUDA 오프로드, Compute Capability)을 거쳐 100% CUDA 가속 서빙과 루트 제어 심볼릭 링크(`./start_server.sh` 등) 생성을 완결합니다.

---

## Technical Context

**Language/Version**: Python 3.11, Bash 5.x, C++17 (GGML CUDA)

**Primary Dependencies**: `uv` 패키지 매니저, `llama-cpp-python[server]`, `pytest`

**Storage**: SQLite3 (`data/metrics.db`), Local File System (Wheels, Logs)

**Testing**: Pytest (`tests/unit/test_seed_pack.py`, `tests/integration/test_migration_pipeline.py`)

**Target Platform**: Linux x86_64 (Nehalem i7-930 CPU + NVIDIA GTX 1070 GPU, Compute Cap sm_61)

**Project Type**: Subshell Bash Automation & Python Core Infrastructure

**Performance Goals**: Fast-Track 복원 시 0.5초 이내 완료, 가상환경 재사용 시 0.05초 리턴, 서브쉘 에러 시 exit 0 중단 방지 100%

**Constraints**: `set -eo pipefail` 정책 준수, CPU 전용 오프로딩 저하 허용 금지 (100% CUDA 가속 필수)

**Scale/Scope**: `scripts/setup.sh`, `scripts/make_seed_pack.sh`, `tests/unit/test_seed_pack.py`

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] 계획서가 한국어로 작성되었는가? (언어 정책)
- [x] 테스트 코드 작성 계획이 포함되어 있는가? (테스트 필수 원칙)
- [x] 목업은 유료/제한 API로 엄격히 제한하고 실물 시스템/소켓/OS 인자 및 실제 호출 플래그(REAL_API_CALL=1) 기반 실측 검증 계획이 포함되어 있는가? (실체적 테스트 및 수렴 검증 원칙)
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (종료 조건 명확화 원칙)
- [x] 비파괴적 문서 수정 원칙을 준수하는가? (비파괴적 문서 수정 원칙)
- [x] uv 패키지 매니저 및 가상환경 격리 표준(uv run)을 준수하는가? (uv 패키지 및 환경 관리 원칙)
- [x] 전체 회귀 테스트 수트 및 Playwright 기반 E2E 브라우저 실측 검증 계획이 포함되어 있는가? (의무적 회귀 테스트 및 브라우저 E2E 검증 원칙)

---

## Project Structure

### Documentation (this feature)

```text
specs/055-fix-migration-setup-fallback/
├── spec.md              # Feature specification
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   └── fallback-pipeline-api.json
└── checklists/
    └── requirements.md
```

### Source Code (repository root)

```text
scripts/
├── setup.sh               # Modified: 서브쉘 set -e 가드, 4단계 휠 감지 & 3중 정합성 검증, --wheel-path CLI 지원
├── make_seed_pack.sh      # Modified: --wheel-path 파라미터 지원 및 사전 검증 강화
├── start_server.sh        # Controlled symlink target
└── status_server.sh       # Controlled symlink target

tests/
├── unit/
│   └── test_seed_pack.py  # Modified: 서브쉘 예외 가드 및 4단계 휠 감지 테스트 추가
└── integration/
    └── test_migration_pipeline.py
```

**Structure Decision**: 단일 프로젝트 구조 (Single project structure)

---

## Complexity Tracking

> Violation 및 예외 사항 없음 (Constitution 100% 준수)

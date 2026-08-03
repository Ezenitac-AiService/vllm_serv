# Implementation Plan: 서버 현황 모니터링 불일치 해소 및 헬스체크 통일

**User Specs Reference**: `/specs/085-unify-monitoring-healthchecks/`  
**Target Branch**: `main` / `085-unify-monitoring-healthchecks`  

---

## 1. Technical Context & Scope

- **Affected Components**:
  - `scripts/status_server.sh` (8082 대시보드 curl 탐색 시 LAN IP 및 `-sL --max-time 5` 적용)
  - `scripts/diagnose_server_health.py` (동일한 후보 IP 및 DOM 키워드 패턴)
  - `tests/integration/test_server_health_diagnostics.py` (두 도구의 헬스체크 정합성 테스트 추가)

---

## 2. Constitution Check

- **Principle I (Korean Language)**: All docs in Korean -> PASS
- **Principle II & III (Zero Mock)**: Real HTTP socket probing against live daemons -> PASS
- **Principle VII (Full Regression Testing)**: Run pytest after edits -> PASS

---

## 3. Planned Touch-Points & Work Phases

### Phase 0: Research & Requirements (Complete)
- Created `research.md` (curl -sL, LAN IP detection, multi-IP probe).

### Phase 1: Design & Contracts (Complete)
- Created `data-model.md`, `contracts/health-probe-contract.json`, `quickstart.md`.

### Phase 2: Implementation (To be generated via `/speckit-tasks`)
- Task 1: `scripts/status_server.sh` curl 대시보드 탐색 옵션 고도화 (`-sL`, LAN IP 추가)
- Task 2: `tests/integration/test_server_health_diagnostics.py`에 status_server.sh vs diagnose_server_health.py 정합성 테스트 추가
- Task 3: 실측 실행 및 검증 (`./status_server.sh`, `uv run scripts/diagnose_server_health.py`)

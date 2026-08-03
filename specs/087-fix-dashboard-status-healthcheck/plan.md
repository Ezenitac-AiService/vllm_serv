# Implementation Plan: status_server.sh 대시보드 헬스체크 307 리다이렉트 처리 및 상태 진단 정확도 정상화

**Branch**: `087-fix-dashboard-status-healthcheck` | **Date**: 2026-08-03 | **Spec**: [spec.md](file:///home/dev/storage/vllm_serv/specs/087-fix-dashboard-status-healthcheck/spec.md)

**Input**: Feature specification from `/specs/087-fix-dashboard-status-healthcheck/spec.md`

---

## 1. Summary

8082 대시보드가 구동 중일 때 `./status_server.sh` 스크립트 실행 시 루트 `/` 엔드포인트의 `HTTP 307 Temporary Redirect` 응답(본문 0바이트)을 수신하여 `Port 8082 CLOSED`로 거짓 음성(False Negative) 오진하던 문제를 해결합니다.
`status_server.sh` 내 curl 탐색 시 `-L` (Location Follow) 플래그를 추가하고, `127.0.0.1`, `localhost`, LAN IP 순으로 다중 프로브를 수행하여 8082 대시보드의 HTML DOM 키워드 검증 및 헬스체크 정확도를 100% 보장합니다.

---

## 2. Technical Context

- **Language/Version**: Bash, Python 3.12, Pytest 9.1
- **Primary Dependencies**: `curl`, FastAPI/Uvicorn, Starlette TestClient
- **Storage**: N/A (CLI & Shell script healthcheck logic)
- **Testing**: Pytest (`tests/integration/test_server_health_diagnostics_consistency.py`)
- **Target Platform**: Linux (Ubuntu 24.04 LTS / Debian)
- **Project Type**: Shell script & Python FastAPI Reverse Proxy / Dashboard
- **Performance Goals**: `status_server.sh` 실행 시 대시보드 탐색 지연시간 < 3초
- **Constraints**: 거짓 음성(False Negative `Port 8082 CLOSED`) 발생률 0%
- **Scale/Scope**: `scripts/status_server.sh`, `tests/integration/test_server_health_diagnostics_consistency.py`

---

## 3. Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] 계획서가 한국어로 작성되었는가? (언어 정책 준수)
- [x] 테스트 코드 작성 계획이 포함되어 있는가? (의무적 회귀 테스트)
- [x] 목업은 유료/제한 API로 엄격히 제한하고 실물 시스템/소켓/OS 인자 및 실제 호출 플래그(REAL_API_CALL=1) 기반 실측 검증 계획이 포함되어 있는가? (실체적 테스트 및 수렴 검증 원칙)
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (DoD-001, DoD-002)
- [x] 비파괴적 문서 수정 원칙을 준수하는가?
- [x] uv 패키지 매니저 및 가상환경 격리 표준(uv run)을 준수하는가?
- [x] 전체 회귀 테스트 수트 및 실측 검증 계획이 포함되어 있는가?

---

## 4. Project Structure

### Documentation (this feature)

```text
specs/087-fix-dashboard-status-healthcheck/
├── spec.md              # Feature specification
├── plan.md              # Implementation plan (this file)
├── research.md          # Research findings (Phase 0 output)
├── data-model.md        # State schema & probe flow (Phase 1 output)
├── quickstart.md        # Runnable validation guide (Phase 1 output)
├── contracts/           # Interface contracts (Phase 1 output)
│   └── dashboard-health-contract.json
└── checklists/
    └── requirements.md  # Quality validation checklist
```

### Source Code Touch-Points

```text
scripts/
└── status_server.sh     # Fixed curl -sL and multi-host probe logic for Port 8082

tests/integration/
└── test_server_health_diagnostics_consistency.py # Regression test suite for status_server.sh
```

**Structure Decision**: Single repository component touch-point. Edits confined to `scripts/status_server.sh` and integration regression test suite.

---

## 5. Phase 1 Design Summary

- **data-model.md**: 대시보드 상태 진단 코드 (`RUNNING_VERIFIED`, `RUNNING_KEYWORD_MISSING`, `STOPPED_OR_CLOSED`) 정의.
- **contracts/dashboard-health-contract.json**: curl `-sL --max-time 3` 옵션 및 expected DOM keywords (`vLLM`, `Dashboard`, `vllm_serv`, `대시보드`) 제약 정의.
- **quickstart.md**: `./status_server.sh` 실측 테스트 및 pytest 회귀 시나리오 가이드 제공.

---

## 6. Complexity Tracking

> Violation / Complexity: None. No architectural complexity added.

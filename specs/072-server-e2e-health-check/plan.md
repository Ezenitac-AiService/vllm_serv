# Implementation Plan: LLM 서버 서비스 모델, API 엔드포인트, E2E 대시보드, 방화벽 및 LAN 접속 통합 진단 (072-server-e2e-health-check)

**Branch**: `main` (또는 `072-server-e2e-health-check`)
**Spec**: [`specs/072-server-e2e-health-check/spec.md`](spec.md)
**Created**: 2026-08-03

---

## Technical Context & Strategy

### Objective
LLM 서버가 서비스 중인 모델 목록, API 엔드포인트(`/v1/models`, `/v1/chat/completions`, `/health`) 응답성, 웹 대시보드 브라우저 E2E 검증, 방화벽 포트 개방 상태, 동적 LAN IP 기반 접속 통신 가능성을 통합 진단하는 스크립트(`scripts/diagnose_server_health.py`) 및 테스트 수트 구축.

### Architecture Overview
1. **IP & Firewall Diagnostics Module (`src/core/network_detector.py` 확장 활용)**
   - `NetworkDetector`를 통해 실제 바인딩된 LAN IP(`10.0.0.x` / `192.168.0.x`)를 동적 추출.
   - 소켓 연결 바인딩 테스트로 8081(LLM 메인 포트) 및 8082(대시보드 포트) 방화벽/개방 상태 점검.
2. **LLM API Diagnostics Module (`scripts/diagnose_server_health.py`)**
   - GET `/v1/models` API 호출로 모델 목록 수집.
   - POST `/v1/chat/completions` 및 GET `/health` 핑 전송으로 API 엔드포인트 정상 작동성 검증.
3. **Web Dashboard E2E Test Suite (`tests/unit/test_server_health_diagnostics.py`)**
   - Playwright 기반 웹 브라우저 E2E 검증 및 HTTP 응답 점검.

---

## Phase 0: Research & Analysis
- [x] **Research Completed**: [`research.md`](research.md)

---

## Phase 1: Design & Artifacts
- [x] **Data Model**: [`data-model.md`](data-model.md)
- [x] **Contracts**: [`contracts/health_report_contract.json`](contracts/health_report_contract.json)
- [x] **Quickstart Validation Guide**: [`quickstart.md`](quickstart.md)

---

## Phase 2: Task Planning & Execution Roadmap
1. `scripts/diagnose_server_health.py` CLI 통합 진단 스크립트 개발
2. `tests/unit/test_server_health_diagnostics.py` 테스트 수트 구현
3. 전체 진단 및 pytest 실행으로 100% Pass 검증

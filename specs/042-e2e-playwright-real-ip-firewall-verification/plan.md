# Implementation Plan: 실할당 LAN IP 접속 및 Playwright E2E 브라우저 실측 검증 (042-e2e-playwright-real-ip-firewall-verification)

**Branch**: `042-e2e-playwright-real-ip-firewall-verification` | **Date**: 2026-07-30 | **Spec**: [spec.md](file:///home/dev/storage/vllm_serv/specs/042-e2e-playwright-real-ip-firewall-verification/spec.md)

**Input**: Feature specification from `specs/042-e2e-playwright-real-ip-firewall-verification/spec.md`

## Summary

1. `src/core/config_manager.py` 및 서버 구동 런처(`scripts/start_server.sh`)에서 기본 host 바인딩을 `0.0.0.0`으로 설정하고 포트 8081 LLM 서버와 포트 8089 웹 대시보드 서버를 원자적 자동 동시 기동.
2. `scripts/benchmark_quality.py` 종료 시(`finally` 구문) 8089 포트 웹 대시보드가 죽어있을 경우 자동 백그라운드 재기동 안전망 수록.
3. `tests/e2e/test_dashboard_playwright_real.py` 수트를 작성하여 Playwright 브라우저 엔진으로 실할당 IP `http://10.0.0.41:8089/dashboard` 접속, DOM 요소 표출 및 증적 스크린샷 캡처를 실측 검증.

## Technical Context

**Language/Version**: Python 3.10+, Bash  
**Dependencies**: FastAPI, uvicorn, pytest, pytest-playwright  
**Target Platform**: Linux (10.0.0.41 LAN Host)  
**Testing**: Playwright Headless Browser E2E (`tests/e2e/test_dashboard_playwright_real.py`)

## Constitution Check

- [x] 계획서가 한국어로 작성되었는가? (언어 정책)
- [x] 테스트 코드 작성 계획이 포함되어 있는가? (테스트 필수 원칙)
- [x] 목업은 유료/제한 API로 엄격히 제한하고 실물 시스템/소켓/OS 인자 및 실제 호출 플래그(REAL_API_CALL=1) 기반 실측 검증 계획이 포함되어 있는가? (실체적 테스트 및 수렴 검증 원칙)
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (종료 조건 명확화 원칙)
- [x] 비파괴적 문서 수정 원칙을 준수하는가? (비파괴적 문서 수정 원칙)
- [x] uv 패키지 매니저 및 가상환경 격리 표준(uv run)을 준수하는가? (uv 패키지 및 환경 관리 원칙)

## Project Structure

```text
src/
└── core/
    └── config_manager.py         # Ensure default host is 0.0.0.0 for external LAN listening

scripts/
├── start_server.sh               # Spawn both port 8081 LLM and port 8089 Dashboard API
└── benchmark_quality.py          # Auto-restore port 8089 Dashboard API in finally block

tests/
└── e2e/
    └── test_dashboard_playwright_real.py # Playwright E2E browser test connecting to http://10.0.0.41:8089/dashboard
```

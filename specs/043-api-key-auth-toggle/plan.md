# Implementation Plan: API 키 필수 인증 토글, SQLite 메트릭 DB, Enterprise LLM 쿼터 & 비용/성능 모니터링 구현 (043-api-key-auth-toggle)

**Feature Branch**: `043-api-key-auth-toggle`  
**Specification**: [spec.md](file:///home/dev/storage/vllm_serv/specs/043-api-key-auth-toggle/spec.md)  
**Created**: 2026-07-30  
**Status**: In Progress  

---

## Technical Context

- **Language / Framework**: Python 3.12, FastAPI, Pydantic v2, SQLite 3 (`aiosqlite`)
- **Frontend UI**: Vanilla JS, Glassmorphism CSS, Chart.js / Canvas Micro-charts
- **Storage**: `config/server_config.json` (원자적 파일 교체), `data/metrics.db` (SQLite WAL 모드)
- **Middleware**: `SubnetFilterMiddleware`, `ClientAccessLogMiddleware`, `APIKeyAuthMiddleware`
- **Testing**: `pytest`, `httpx` (Strict Anti-Mock real execution per Constitution v1.4.0)

---

## Constitution Check

- [x] **Principle I (Language Policy)**: All technical documentation and comments written in clear Korean/English per constitution rules.
- [x] **Principle II & III (Strict Anti-Mock & Real Execution)**: Unit/E2E test suites must run real FastAPI server and SQLite DB queries without dummy fallbacks.
- [x] **Principle IV (Definition of Done)**: Complete spec DoD and verifiable test assertions.
- [x] **Principle V (Non-Destructive Edit)**: Atomic file replace with `chmod 0600`.
- [x] **Principle VI (Strict `uv run`)**: `uv run pytest` execution enforced.

---

## Architecture & Touch-Points

```
 ┌───────────────────────────┐      ┌─────────────────────────────┐      ┌─────────────────────────────┐
 │ Web Dashboard (index.html)│      │ FastAPI Router              │      │ Core Infrastructure         │
 │ • API Key Toggle Switch   │      │ • POST /dashboard/api/config│      │ • ConfigManager             │
 │ • Top 5 Ranking Chart     │ ────▶│ • GET /dashboard/api/keys/  │ ────▶│ • MetricsDB (aiosqlite WAL) │
 │ • Key Table & Masking     │      │   metrics & export/csv      │      │ • APIKeyAuthMiddleware      │
 └───────────────────────────┘      └─────────────────────────────┘      └─────────────────────────────┘
```

### Primary Files Affected:
1. `src/core/config_manager.py`: `api_key_enabled` 스위치 연동
2. `src/core/metrics_db.py`: SQLite `data/metrics.db` WAL 모드 모듈 (신규)
3. `src/api/middleware/api_key_auth.py`: API 키 인증/차단 및 쿼터/Rate Limit 검사 미들웨어 (신규)
4. `src/api/routes/dashboard_api.py`: `/dashboard/api/config`, `/dashboard/api/keys/metrics`, `/dashboard/api/keys/export/csv` REST API 수록
5. `src/api/static/index.html` & `app.js`: API 키 토글 스위치, 랭킹 차트, 보안 마스킹, CSV 다운로드 UI 추가
6. `tests/unit/test_api_key_auth_toggle.py`: 실측 401/429/200 및 DB/CSV 테스트 수트

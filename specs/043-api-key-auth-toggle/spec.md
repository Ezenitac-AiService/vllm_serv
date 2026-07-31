# Feature Specification: API 키 필수 인증 토글, SQLite 메트릭 DB, Enterprise LLM 쿼터 & 비용/성능 모니터링 구현 (043-api-key-auth-toggle)

**Feature Branch**: `043-api-key-auth-toggle`  
**Created**: 2026-07-30  
**Status**: Draft  
**Input**: User report: "2026 Enterprise LLM Serving 최신 표준(OWASP LLM Top 10, Portkey/LiteLLM 2026 Reference)에 맞춰 API 키 필수/선택 토글, 키별 통계(오류 수, Prompt/Completion 토큰, Peak RPM, ⚠️ 경고 뱃지, Top 5 랭킹, Quota Limit, Rate Limiting, CSV Export), 키 즉시 폐기/만료일(Expiry/Revoke), 추정 비용 달러($) 계산, TTFT/TPS 레이턴시 메트릭을 SQLite DB(data/metrics.db) 기반으로 구축."

---

## Clarifications

### Session 2026-07-30

- Q: API 키별 사용 통계 시각화 및 대시보드 렌더링 방식 → A: Option A - API 키 목록 테이블에 [호출 횟수, 마지막 사용 시각, 상태] 열 추가 및 키별 호출 비중 시각화 프로그레스 바 제공
- Q: API 키별 심층 통계 메트릭(에러, Prompt/Completion 토큰, peak RPM) 및 이상 징후 시각화 → A: Option A + B 결합 적용 (테이블 [오류 수, Prompt 토큰, Completion 토큰, Peak RPM] 열 확장 + 이상 징후 키 ⚠️ 경고 뱃지 + Top 5 랭킹 시각 차트 카드 동시 수록)
- Q: API 키별 통계 수집 및 저장 메커니즘 → A: Option A - 경량 SQLite DB (`data/metrics.db`) 수립하여 미들웨어에서 호출 이력을 원자적 축적하고 SQL 인덱스 쿼리로 대시보드 시각화 정보 고속 공급
- Q: 다중 페르소나 1차 심층 검토(DBA/보안/운영/AI Agent) 수렴 사항 → A: Option A - SQLite WAL (Write-Ahead Logging) 모드 적용, API 키 마스킹 (`sk-vllm-****-8f3a`) 렌더링 및 30일 경과 메트릭 자동 아카이빙 정제 수록
- Q: 다중 페르소나 2차 심층 검토(DevOps/FinOps/UX) 수렴 사항 → A: Option A - API 키별 토큰 쿼터(Max Tokens) 차단 + Rate Limiting(HTTP 429) 제어 + 대시보드 메트릭 CSV 내보내기 지원
- Q: 2026 Enterprise LLM Serving 표준 (OWASP Top 10, FinOps, Observability) → A: Option A - API 키 즉시 폐기/만료일(Expiry/Revoke) + 누적 달러($) 비용 계산 + TTFT/TPS 레이턴시 메트릭 종합 수록

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 웹 대시보드 API 키 필수/선택 토글 및 인증 강제화 (Priority: P1) 🎯 MVP

웹 대시보드 관리자("API 보안 및 키 관리" 화면)에서 서비스 운영자가 버튼 클릭 하나로 "API 키 필수 인증 모드(API Key Required)"와 "API 키 선택/무인증 모드(Public Access)"를 자유롭게 전환할 수 있도록 합니다.

**Why this priority**: API 키를 발급받더라도 서버 전체에 키 필수가 강제되지 않던 문제를 해결하여 사설망 보안 운영과 유연한 공개 개발 환경을 모두 지원합니다.

**Independent Test**:
1. 대시보드에서 `API 키 인증 필수` 토글을 활성화(`api_key_enabled: true`)하면, 헤더 없이 `/v1/chat/completions` 호출 시 HTTP 401 Unauthorized 오류가 반환되는지 확인.
2. 토글을 비활성화(`api_key_enabled: false`)하면 키 없이도 HTTP 200 OK와 함께 인퍼런스가 성공하는지 확인.

**Acceptance Scenarios**:

1. **Given** 관리자가 대시보드 보안 토글을 `API 키 필수(ON)`로 변경하면, **When** 헤더(`Authorization: Bearer <KEY>` 또는 `X-API-Key`) 없이 인퍼런스 API를 호출할 때, **Then** HTTP 401 Unauthorized 및 "API key is required" 메시지가 반환된다.
2. **Given** 관리자가 대시보드 보안 토글을 `API 키 필수(OFF)`로 변경하면, **When** 헤더 없이 인퍼런스 API를 호출할 때, **Then** 정상적으로 HTTP 200 OK 인퍼런스가 수행된다.
3. **Given** `API 키 필수(ON)` 상태에서, **When** 대시보드에서 발급한 유효한 API 키를 헤더에 포함하여 호출하면, **Then** 인증이 통과하고 성공 응답이 반환되며 `data/metrics.db`에 이력이 기록된다.

---

### User Story 2 - Enterprise LLM 키 관리, 비용($) 계산 및 성능 시각화 (Priority: P2)

웹 대시보드의 API 키 관리 탭에서 [API 키 즉시 비활성화/폐기(Revoke)], [만료일자 설정], [키별 누적 추정 비용($)], [TTFT(초당 첫 토큰 응답속도) 및 TPS(초당 생성 토큰 수)], [Max Token Quota], [Rate Limit(RPM)], [Top 5 랭킹 차트], [CSV 내보내기] 기능을 대시보드에서 한눈에 시각 모니터링할 수 있게 합니다.

**Why this priority**: OWASP LLM 보안 표준 준수, FinOps 비용 통제 및 SRE SLO 성능 측정을 완납합니다.

**Independent Test**:
1. 대시보드에서 특정 키를 [Revoke] 시 해당 키를 사용한 모든 호출이 HTTP 401로 즉시 거부되는지 확인.
2. 인퍼런스 호출 발생 후 대시보드에서 해당 키의 누적 달러($) 비용 및 TTFT/TPS 레이턴시 수치가 실시간 갱신 표출되는지 확인.

---

## Functional Requirements *(mandatory)*

- **FR-001**: `src/api/routes/inference_api.py` 및 인증 미들웨어에서 `config_manager.get_server_config().get("api_key_enabled", False)` 값을 검사하여, True인 경우 유효한 API 키가 없는 모든 `/v1/*` 인퍼런스 요청에 대해 HTTP 401 Unauthorized 거부 로직을 완납해야 한다.
- **FR-002**: 웹 대시보드 UI(`src/api/static/index.html` 및 `app.js`)에 "API 키 필수 인증 토글 (API Key Authentication Required)" 스위치를 추가하고, 현재 `api_key_enabled` 상태를 실시간 시각 표출해야 한다.
- **FR-003**: `POST /dashboard/api/config` REST API 엔드포인트를 제공하여 `api_key_enabled` 토글 변경 요청을 수신하고 `config/server_config.json`에 원자적 업데이트를 수행해야 한다.
- **FR-004**: 경량 SQLite 데이터베이스 관리 모듈(`src/core/metrics_db.py`, DB 파일 `data/metrics.db`)을 수립하여 API 키별 요청 이력(`api_key_logs` 테이블)을 비동기 원자적 기록/저장해야 한다.
- **FR-005**: SQLite DB 동시성 안정성을 위해 WAL (Write-Ahead Logging) 모드(`PRAGMA journal_mode=WAL;`)를 적용하고 30일 경과 이력을 자동 정제해야 한다.
- **FR-006**: 웹 대시보드 API 키 관리 탭 테이블에 [키 이름, API 키(마스킹 `sk-****-8f3a`), 생성일, 만료일, 호출 수, 오류 수, 입력 토큰, 출력 토큰, Peak RPM, 추정 비용($), TTFT/TPS, 이상 징후 뱃지(⚠️), 폐기(Revoke) 버튼, 사용 비중 프로그레스 바] 시각화 UI 요소를 추가해야 한다.
- **FR-007**: 웹 대시보드 상단에 **[Top 5 토큰/호출 키 랭킹 시각 차트 카드]**를 신설하고 SQLite DB SQL Aggregation 쿼리(`GET /dashboard/api/keys/metrics`)로 대시보드에 고속 데이터 공급을 완납해야 한다.
- **FR-008**: API 키별 **Max Token Quota (최대 토큰 쿼터)** 및 **Rate Limiting (RPM)**을 설정할 수 있게 하고 초과 시 HTTP 429 차단 응답을 반환해야 한다.
- **FR-009**: API 키 **즉시 폐기/비활성화 (`POST /dashboard/api/keys/revoke`)** 및 만료일자 검증 기능을 완납해야 한다.
- **FR-010**: 대시보드 API 키 탭에 **[CSV 내보내기 (Export CSV)]** 버튼을 추가하고 `GET /dashboard/api/keys/export/csv` 엔드포인트를 제공해야 한다.
- **FR-011**: Anti-Mock 헌법 v1.4.0에 따라 토글 ON/OFF, Revoke 키 차단, 쿼터 초과 HTTP 429 및 CSV 다운로드 실측 테스트 수트(`tests/unit/test_api_key_auth_toggle.py`)를 수록해야 한다.

---

## Success Criteria *(mandatory)*

- **SC-001**: 대시보드 보안 토글 ON 시 키 없는 요청의 HTTP 401 차단율 **100%**.
- **SC-002**: 폐기(Revoke) 처리된 키의 호출 즉시 차단율 **100%**.
- **SC-003**: 설정된 키별 토큰 쿼터 초과 시 HTTP 429 차단율 **100%**.
- **SC-004**: SQLite DB (`data/metrics.db` WAL 모드) 기반 키별 통계, 비용($), TTFT/TPS 및 Top 5 랭킹 차트 쿼리 속도 **<10ms**.
- **SC-005**: 대시보드 API 키 표출 시 보안 마스킹(`sk-****-8f3a`) 적용률 **100%**.
- **SC-006**: 대시보드 CSV 리포트 내보내기 정상 다운로드 및 데이터 일치율 **100%**.

---

## Key Entities *(optional)*

- **Enterprise API Key Entity with Observability Metrics**:
  ```json
  {
    "key": "sk-vllm-...",
    "name": "Production Client",
    "status": "active",
    "created_at": "2026-07-30T15:00:00Z",
    "expires_at": "2026-10-30T15:00:00Z",
    "last_used_at": "2026-07-30T15:06:00Z",
    "max_tokens_quota": 1000000,
    "max_rpm_limit": 60,
    "prompt_tokens": 15420,
    "completion_tokens": 4200,
    "estimated_cost_usd": 0.042,
    "avg_ttft_ms": 185.4,
    "avg_tps": 48.2,
    "request_count": 142,
    "error_count": 2
  }
  ```

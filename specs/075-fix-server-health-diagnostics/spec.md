# Feature Specification: 서버 헬스진단 스크립트 정밀화 및 8082 대시보드 연동 복구 (075-fix-server-health-diagnostics)

**Feature Directory**: `specs/075-fix-server-health-diagnostics`
**Status**: DRAFT
**Created**: 2026-08-03

## Executive Summary

실물 서비스 플랫폼 배포 후 `./status_server.sh` 및 `diagnose_server_health.py` 진단 결과, Port 8082 웹 대시보드 차단/미구동(CLOSED/BLOCKED) 및 `/v1/chat/completions` 프로브 미도달(UNREACHABLE) 경고가 확인되었습니다. 본 명세서는 대시보드 포트(8082) 서비스 자동 가동 및 `diagnose_server_health.py` 진단 프로브의 정밀화를 통해 시스템 진단 상태를 100% HEALTHY(ALL GREEN)로 전환하는 요구사항을 정의합니다.

## Clarifications

### Session 2026-08-03

- Q: `start_server.sh`가 대시보드 서버(8082), REST API 서버(8081), LLM 백엔드 서버(llama-server)를 모두 켜는 것이 맞는가? → A: 네, 맞습니다. `./start_server.sh` 구동 시 1) LLM 백엔드 서빙 데몬(8081, 8090, 8091), 2) REST API 게이트웨이(FastAPI), 3) 웹 대시보드 모니터링 서버(Port 8082) 3대 서비스가 원스톱으로 모두 백그라운드 시작되도록 보장해야 합니다.
- Q: `scripts/setup.sh` 실행 시 Port 8081 및 Port 8082 방화벽 규칙도 자동 등록되는가? → A: 네, 맞습니다. `scripts/setup.sh` 실행 시 OS 방화벽(ufw / iptables)에 Port 8081(REST API)과 Port 8082(웹 대시보드) 허용 규칙(`ufw allow 8081/tcp`, `ufw allow 8082/tcp`)이 자동으로 개방 등록되도록 인프라 요구사항을 포함합니다.
- Q: 통합 헬스체크 진단에서 Port 8082가 CLOSED/BLOCKED되고 `/v1/chat/completions`가 UNREACHABLE로 나오는 원인은 무엇인가? → A: 1) Port 8082 대시보드 프로세스가 구동되지 않았거나 UFW 규칙 미등록/바인딩 IP 불일치로 소켓 타임아웃 발생, 2) `/v1/chat/completions` 프로브 검증 시 파이덴틱 스키마 잔재 또는 유효한 기본 모델명(`qwen3.5-4b`) 미지정으로 HTTP 응답 수신에 실패했기 때문입니다. 이를 해결하기 위해 대시보드 구동 자동화 및 진단 프로브 파이썬 dict 호환성을 구현합니다.

---

## User Stories & Acceptance Criteria

### User Story 1 (Priority: P1) - `/v1/chat/completions` API 헬스 프로브 정밀화 🎯 MVP

**User Persona**: 시스템 관리자 및 개발자

**As a** 시스템 관리자  
**I want** `diagnose_server_health.py` 실행 시 `/v1/chat/completions` API 진단 프로브가 정상적으로 200 OK 응답을 수신하는 것  
**So that** 인퍼런스 서버의 실제 대화 서비스 제공 가능 상태를 정확하게 확인할 수 있다.

#### Acceptance Criteria

1. **AC-1.1**: `diagnose_server_health.py` 내 `/v1/chat/completions` 프로브 요청 시 Pydantic 의존성 없이 표준 파이썬 dict 페이로드(`model: "qwen3.5-4b"`, `messages: [...]`)를 사용한다.
2. **AC-1.2**: 타임아웃 및 Connection 헤더를 적절히 설정하여 서버 가동 중 false positive (UNREACHABLE) 경고를 완전히 제거한다.
3. **AC-1.3**: 실행 진단 결과에서 `/v1/chat/completions: ✅ 200 OK`가 출력된다.

---

### User Story 2 (Priority: P2) - Port 8082 웹 대시보드 구동 및 E2E 렌더링 정상화

**User Persona**: 운영자 및 인프라 평가자

**As a** 운영자  
**I want** `./start_server.sh` 및 백그라운드 서비스 시작 시 Port 8082 웹 대시보드가 자동으로 함께 구동되는 것  
**So that** 대시보드 E2E 렌더링 및 모니터링 기능이 ✅ OPEN / ✅ ON 상태로 활성화된다.

#### Acceptance Criteria

1. **AC-2.1**: `./start_server.sh` 가동 시 Port 8082 웹 대시보드 프로세스가 정상 시작된다.
2. **AC-2.2**: `diagnose_server_health.py` 진단 시 `Port 8082_dashboard: ✅ OPEN` 및 `🖥️ 웹 대시보드 E2E 렌더링 : ✅ ON`으로 표시된다.
3. **AC-2.3**: `status_server.sh` 리포트에 대시보드 포트 8082 바인딩 상태가 정상 표시된다.

---

## Functional Requirements (FR-###)

- **FR-001**: `scripts/diagnose_server_health.py` 스크립트의 `/v1/chat/completions` 진단 프로브를 파이썬 기본 dict 페이로드 기반으로 리팩토링하여 200 OK 수신을 정밀 검증해야 한다.
- **FR-002**: `./start_server.sh` 구동 스크립트에 Port 8082 웹 대시보드 모듈(FastAPI/Streamlit/Dashboard) 바인딩 및 프로세스 생명주기 관리를 포함시켜야 한다.
- **FR-003**: `status_server.sh` 리포트에 Port 8081 메인 API 및 Port 8082 웹 대시보드 헬스 상태를 함께 포함하여 출력해야 한다.
- **FR-004**: 진단 결과 최종 상태가 `STATUS: 🎉 SYSTEM HEALTHY` 및 모든 세부 항목 그린(PASS) 상태로 수렴해야 한다.

---

## Success Criteria (SC-###)

- **SC-001**: `python scripts/diagnose_server_health.py` 실행 시 0건의 UNREACHABLE 또는 CLOSED/BLOCKED 경고 발생.
- **SC-002**: Port 8081 및 Port 8082 동시 헬스체크 성공률 100%.
- **SC-003**: 기존 의무적 회귀 테스트 수트(`uv run pytest`) 100% 통과 유지.

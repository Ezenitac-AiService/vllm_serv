# Feature Specification: Service Platform Parity & Health Diagnostics Fix (`076-fix-service-platform-parity`)

**Feature Directory**: [`specs/076-fix-service-platform-parity`](file:///home/dev/storage/vllm_serv/specs/076-fix-service-platform-parity)  
**Created Date**: 2026-08-03  
**Status**: IN_REVIEW (Adversarial Audit Complete)  

---

## 1. Overview & Business Value

개발 머신과 실제 서비스 플랫폼(운영 서버) 간의 네트워크 인터페이스 설정(`127.0.1.1` vs `127.0.0.1`), OS 방화벽(UFW) 정책 및 백그라운드 프로세스 실행 환경의 차이로 인해 시드 팩 배포 후 서비스 플랫폼에서 대시보드가 `CLOSED/BLOCKED`로 판정되는 문제를 근본적으로 해결합니다.

---

## 2. User Personas & Scenarios

- **Persona**: 운영 엔지니어 / 훈련 과정 교육생 / SRE 감사관
- **Scenario**:
  1. 개발 머신에서 최신 시드 팩(`vllm_serv_seed.tar.gz`)을 생성하여 서비스 플랫폼으로 이관합니다.
  2. 서비스 플랫폼에서 `./setup.sh`를 실행하여 방화벽 규칙(`8081/tcp`, `8082/tcp`), 파일 실행 권한(`chmod +x`), 파이썬 가상환경을 원스톱으로 구성합니다.
  3. `./start_server.sh`를 실행하여 8081 API 서버와 8082 웹 대시보드 서버를 백그라운드로 동시에 가동하고, 동시 readiness 헬스체크를 검증합니다.
  4. `python scripts/diagnose_server_health.py`를 실행하여 다중 루프백 및 대시보드 DOM 키워드 수신 기반 `STATUS: 🎉 SYSTEM HEALTHY (ALL GREEN)` 상태를 확정합니다.

---

## 3. Functional Requirements (FR)

- **FR-001 (다중 IP/루프백 통합 프로빙)**: `scripts/diagnose_server_health.py`는 단일 LAN IP에 의존하지 않고 `127.0.0.1`, `localhost`, `127.0.1.1`, active LAN IP 전체를 순회 탐색하여 소켓 연결 및 렌더링 상태를 진단해야 한다.
- **FR-002 (원스톱 대시보드 백그라운드 가동, Readiness 및 상태 리포트)**: `start_server.sh`는 `uv run` 환경 하에서 8081 메인 API 서버와 Port 8082 웹 대시보드 Uvicorn 데몬을 백그라운드로 원스톱 동시 구동하고 8082 포트 수신 대기를 검증해야 하며, `status_server.sh`는 Port 8081/8082 LISTEN 상태 및 대시보드 HTML DOM 내용 건전성을 정확히 진단·리포트해야 한다.
- **FR-003 (서비스 포트 OS 방화벽 및 실행 권한 자동 보장)**: `scripts/setup.sh`는 `8081/tcp` 및 `8082/tcp` 서비스 포트를 UFW, firewalld, iptables 규칙에 원스톱 등록하고 모든 제어 스크립트에 대해 `chmod +x` 실행 권한을 강제해야 한다.
- **FR-004 (서비스 플랫폼 ALL GREEN 및 DOM 키워드 검증)**: 서비스 플랫폼에서 진단 스크립트 실행 시 `Port 8081_llm_main: ✅ OPEN`, `Port 8082_dashboard: ✅ OPEN`, 웹 대시보드 HTML 키워드 검증을 포함한 `웹 대시보드 E2E: ✅ ON`, `STATUS: 🎉 SYSTEM HEALTHY`를 달성해야 한다.

---

## 4. Success Criteria (SC)

- **SC-001**: 서비스 플랫폼 환경에서 `diagnose_server_health.py` 실행 시 8081 및 8082 포트 오탐 없는 ALL GREEN 리포트 달성.
- **SC-002**: `./start_server.sh` 1회 실행으로 8081 및 8082 두 포트가 모두 정상 LISTEN 상태로 수렴.
- **SC-003**: 의무적 전체 회귀 테스트 수트 준수.

---

## 5. Adversarial Audit & Hardening Requirements (공격적 비판론자 다중 페르소나 심층 검증)

### 🥊 Persona 1: SRE/DevOps Architect (프로세스 생명주기 및 붕괴 방지)
- **비판**: 8082 대시보드 데몬만 켜지고 8081 메인 API 서버가 비정상 종료되거나, 그 반대의 경우 프로세스가 파편화됨.
- **보강 규격**: `start_server.sh`에 8081 및 8082 포트에 대한 동시 Readiness Check 타임아웃(최대 30초)을 수록하고, 하나라도 실패 시 생성된 프로세스를 원자적으로 롤백/종료(Clean Exit)하도록 보강한다.

### 🛡️ Persona 2: Security & Infrastructure Auditor (네트워크 노출 보안)
- **비판**: `0.0.0.0` 바인딩 시 관리 콘솔 무단 노출 위험 및 소켓 타임아웃으로 인한 서버 자원 고갈(Slowloris) 위험.
- **보강 규격**: `diagnose_server_health.py` 프로브 소켓 연결 시 `timeout=3.0` 및 `Connection: close` 헤더를 명시하여 소켓 자원 누수를 차단하고, 포트 바인딩 설정을 환경 변수로 제어 가능하게 안전화한다.

### 🧪 Persona 3: QA Architect (허위 양성/오탐 방지)
- **비판**: 포트 8082만 열려있거나 HTTP 500 에러 페이지가 리턴되어도 단순 200/307 수신 시 `✅ ON`으로 오탐될 위험.
- **보강 규격**: `check_dashboard_e2e()`는 HTTP 응답 본문에 대시보드 고유 식별 키워드(예: `vllm_serv` 또는 `Dashboard`)가 실제 포함되었는지 내용 검증(Content Verification)까지 포함한다.

### 📦 Persona 4: Release & Deployment Engineer (권한 및 마이그레이션 안전성)
- **비판**: 시드 팩 압축해제 후 타겟 서버의 `chmod` 권한 미비로 스크립트 실행 불가 또는 구형 링크 참조 위험.
- **보강 규격**: `setup.sh` 완결 단계에서 심볼릭 링크 및 `scripts/*.sh` 전역에 `chmod +x`를 강제 갱신하여 권한 거부 오류를 물리적으로 차단한다.

---

## 6. Clarifications & Session History

### Session 2026-08-03
- **Q**: 서비스 플랫폼의 `/etc/hosts` 및 `127.0.1.1` 바인딩 환경에서도 8082 포트 진단이 정상 동작하는가? → **A**: 다중 루프백 순회 탐색 프로빙으로 오탐을 방지한다.
- **Q**: 공격적 다중 페르소나 검증을 통해 도출된 핵심 허점 대응 방안은? → **A**: 섹션 5의 4대 비판론자 보강 규격(원자적 프로세스 롤백, 소켓 자원 세션 차단, HTML DOM 키워드 검증, chmod 권한 강제)을 적용한다.

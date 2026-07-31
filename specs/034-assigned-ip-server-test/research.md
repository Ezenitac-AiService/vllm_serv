# Phase 0 Research: Assigned IP Server Verification Test

## Overview

본 연구는 서버 구동 확인 테스트 시 `localhost` (`127.0.0.1`) 뿐만 아니라, 듀얼랜(Dual LAN) 환경을 포함하여 시스템에 할당된 모든 비-루프백(Non-loopback) IP 주소를 통한 서버 접속, API 호출 및 응답 정합성 검증 방안을 설계하기 위한 조사를 수행합니다.

## Research Findings

### 1. 호스트 할당 IP 탐지 방식

- **Decision**: 기존 `src/core/network_detector.py` 모듈의 `NetworkDetector.get_active_lan_ips()` 및 `scan_interfaces()` 메서드를 활용.
- **Rationale**:
  - 이미 프로젝트 표준 네트워크 감지 모듈로 구축되어 있으며 `psutil` 기반으로 물리 NIC/가상 NIC 구분 및 링크 활성화 상태(`isup`), 비-루프백(`is_usable_lan`) 판정이 구현되어 있음.
  - 듀얼랜(Dual LAN) 환경에서 `eth0`, `eth1` 등의 모든 활성 물리 LAN 포트 IPv4 주소를 정확히 수집함.
- **Alternatives Considered**:
  - `socket.gethostbyname(socket.gethostname())`: 기본 라우팅 경로의 IP 1개만 반환하므로 듀얼랜 환경의 두 번째 LAN 포트를 누락함.
  - 하드코딩된 IP 목록: 테스트 환경 변경 시 유연성 부족.

### 2. 접속, 호출 및 응답 검증 기법 (Connection & Call/Response Verification)

- **Decision**: HTTP/REST 엔드포인트(예: `/health` 또는 `/v1/models`)에 대한 HTTP GET 요청 수행 및 응답 상태 코드(200 OK), 라우팅 지연 시간, 본문 정합성을 개별 IP별로 타임아웃(3초) 내 검증.
- **Rationale**:
  - 단순 TCP 소켓 바인딩 확인만으로는 HTTP 웹 서버/vLLM 서비스의 실제 요청 수용 및 응답 생성 기능을 보장할 수 없음.
  - HTTP 클라이언트(`urllib.request` 또는 `httpx`/`requests`)를 통해 `http://<assigned_ip>:<port>/...` 형식으로 직접 호출해야 진정한 서버 구동 검증이 이루어짐.

### 3. 검증 모듈 구조 (Server Connectivity Verifier Design)

- **Decision**: `ServerConnectivityVerifier` 클래스를 설계하여 `127.0.0.1` 및 모든 할당 LAN IP 목록에 대해 검증을 수행하고, 결과를 `IPTestVerdict` 및 `ConnectivityReport` 개체로 반환.
- **Rationale**:
  - 테스트 코드(`pytest`) 및 서버 구동 후 초기화 진단 스크립트 양쪽에서 재사용할 수 있는 모듈화된 구조 제공.
  - 특정 IP 접속 실패 시 개별 IP별 접속 거부(Connection Refused), 타임아웃, 5xx 에러 등의 상세 진단 정보 제공 가능.

## Summary of Architectural Decisions

1. `NetworkDetector` 모듈을 통한 루프백 외 듀얼랜 포트 포함 모든 활성 LAN IP 자동 감지.
2. `ServerConnectivityVerifier` 개체 도입을 통한 `127.0.0.1` + 할당 IP 전체 대상 HTTP 헬스체크 및 응답 검증.
3. IP별 응답 결과 정밀 기록 (`IPTestVerdict`) 및 `uv run pytest` 검증 체계 구축.

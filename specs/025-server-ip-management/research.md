# Technical Research: 듀얼 랜포트 다중 NIC 환경 서버 IP 바인딩 및 네트워크 관리 로직 고도화 (025-server-ip-management)

## Overview

본 문서는 듀얼 랜포트 서버(i7 930) 등 다중 NIC 환경에서 외부 LAN IP(`192.168.0.80`) 접근을 허용하고, 미할당 이더넷 포트 탐지 예외를 방지하며, OS 방화벽(`ufw`/`iptables`) 포트 개방 자동화를 지원하기 위한 연구 조사 결과를 정리합니다.

---

## Research Items & Decisions

### 1. 활성 네트워크 인터페이스(NIC) 및 IP 자동 탐지 메커니즘

- **Decision**: Python 표준 라이브러리 `socket` 및 `psutil` (또는 `netifaces`)을 결합하여 로컬 네트워크 인터페이스 목록을 스캔합니다.
- **Rationale**:
  - 루프백 주소(`127.0.0.1`), 미연결/비활성화 포트(`Link Down`, IP 미할당 포트)를 자동으로 필터링합니다.
  - 듀얼 랜포트 중 IP가 할당된 유효 이더넷 포트(예: `192.168.0.80`)만을 감지하여 바인딩 주소 목록 및 헬스체크 메타데이터로 활용합니다.
- **Alternatives Considered**:
  - `socket.gethostbyname(socket.gethostname())` 단독 사용: 듀얼 NIC 환경에서 첫 번째 미할당 포트의 127.0.0.1이나 잘못된 인터페이스를 반환할 위험이 있어 부적합.

---

### 2. 서버 소켓 호스트 바인딩 및 프로세스 전파

- **Decision**: `config/server_config.json`의 `host` 기본값을 `0.0.0.0`으로 설정하고, `ProcessManager`에서 `llama-server` 하위 프로세스 스폰 시 `--host 0.0.0.0` 인자를 전파합니다.
- **Rationale**:
  - `0.0.0.0` 바인딩을 통해 모든 활성 네트워크 인터페이스(LAN IP `192.168.0.80` 포함)에서 소켓 수신이 가능해집니다.
  - 미할당 랜포트가 존재하더라도 소켓 바인딩 에러가 발생하지 않습니다.
- **Alternatives Considered**:
  - 특정 감지된 IP(`192.168.0.80`)에 개별 고정 바인딩: DHCP IP 변경 시 재설정이 필요하므로 `0.0.0.0`과 동적 IP 탐지를 병행하는 것이 우수함.

---

### 3. OS 방화벽 (`ufw` / `iptables`) 포트 자동 개방 및 권한 예외 처리

- **Decision**: `src/core/firewall_manager.py` 모듈을 신설하여 Linux 환경에서 `ufw` 또는 `iptables` 지원 여부를 확인하고 서비스 포트(`8081`, `8089` 등) 개방을 시도합니다.
- **Rationale**:
  - `ufw status` 및 `ufw allow <port>/tcp` 실행을 시도합니다.
  - non-root 환경으로 인해 `sudo` 권한 부족 또는 명령어실패 시 예외를 포획하여 시스템을 다운시키지 않고, 명확한 가이드 메시지(`"⚠️ 방화벽 개방 필요: sudo ufw allow 8081/tcp"`)를 로그에 출력합니다.
- **Alternatives Considered**:
  - `sudo` 명령어 강제 실행: 비인가 환경에서 대기(Hang) 현상 발생 위험이 있으므로 non-blocking 시도 및 안내 가이드 출력이 안전함.

---

### 4. 서브넷 접근 제어 (`SubnetFilter`) 및 CORS 동적 라우팅

- **Decision**: `SubnetFilter`에 `192.168.0.0/16`, `10.0.0.0/8`, `172.16.0.0/12` 등 사설 IP 대역(Private Subnets)을 기본 허용 목록으로 수용하고, Fast API CORS `allow_origins`에 활성 감지 LAN IP 주소를 자동 추가합니다.
- **Rationale**: 훈련생 외부 클라이언트 단말기(`192.168.0.x`)에서 접속 시 HTTP 403 Forbidden 및 CORS 정책 거부를 완전 방지합니다.

---

### 5. 플랫폼 프로필 연동 (`platform_profiles.json`)

- **Decision**: `config/platform_profiles.json` 내 3종 프로필(`e3-1231v3`, `i7-4770`, `i7-930`)에 `network` 구성 블록(`bind_host`, `allowed_subnets`, `firewall_auto_allow`)을 연동합니다.
- **Rationale**: 개발 플랫폼, 학습/프로젝트 플랫폼, 서비스 플랫폼별 네트워크 허용 범위를 명시적으로 구분 관리합니다.

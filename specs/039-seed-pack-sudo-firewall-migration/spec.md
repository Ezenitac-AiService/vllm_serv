# Feature Specification: 시드 팩 마이그레이션 및 setup.sh 관리자 권한·방화벽 자동화 (039-seed-pack-sudo-firewall-migration)

**Feature Branch**: `039-seed-pack-sudo-firewall-migration`  
**Created**: 2026-07-30  
**Status**: Draft  
**Input**: User description: "시드 팩으로 마이그레이션 해서 서버 셋팅할때에, setup.sh로 서버 셋팅할때 관리자 권한을 어떻게 확보하고, 방화벽 설정을 잘 할수 있는가, 2026년 7월 최신 기준으로 리서치를 진행하고, 스펙 작성"

---

## Clarifications

### Session 2026-07-30

- Q: `setup.sh` 전체 루트(`sudo ./setup.sh`) 실행 시 소유권 자동 보정 정책 → A: 일반 계정 실행 기본 + 방화벽 부분 승격. 만약 `sudo ./setup.sh` 직접 실행 시 `$SUDO_USER` 계정으로 `.venv`, `logs`, `config` 소유권 자동 보정(`chown -R $SUDO_USER:$SUDO_USER`) (Option A)

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 시드 팩 타겟 서버 마이그레이션 시 sudo 관리자 권한 대화형 승격 및 유효성 유지 (Priority: P1) 🎯 MVP

엔지니어가 오프라인 타겟 서버로 시드 팩(`vllm_serv_seed_pack.tar.gz`)을 이관하여 `./setup.sh`를 실행할 때, 스크립트 최전단에서 sudo 타임스탬프 유효성을 검증(`sudo -v`)하고 대화형 비밀번호를 1회 입력받아 설치 파이프라인 진행 동안 권한 만료 없이 관리자 작업을 완납합니다.

**Why this priority**: 시드 팩 오프라인 서버 설치 과정에서 포트 개방 및 패키지 셋팅 시 권한이 중간에 끊기거나 `sudo -n` 비대화형 실패로 방화벽 개방이 누락되는 현상을 근본적으로 차단합니다.

**Independent Test**: 방화벽이 닫히고 sudo 비밀번호가 설정된 타겟 Linux 서버에서 시드 팩 압축 해제 후 `./setup.sh` 구동 시, 최전단 `sudo -v` 승격 후 백그라운드 타임스탬프 갱신 루프가 작동하여 방화벽 포트(`8081/tcp`, `8089/tcp`) 개방까지 오류 없이 완납되는지 검증합니다.

**Acceptance Scenarios**:

1. **Given** 타겟 서버의 일반 사용자 계정(dev)에서 시드 팩 `setup.sh`를 실행하면, **When** TTY 인터랙티브 환경인 경우 최전단에서 `sudo -v`를 통해 비밀번호를 안전하게 입력받고, 스크립트 종료까지 sudo 타임스탬프 갱신 데몬을 유지합니다.
2. **Given** 비대화형(CI/CD 또는 헤드리스) 환경인 경우, **When** `sudo` 권한 미획득 시, **Then** 방화벽 개방 명령이 담긴 전용 스크립트(`scripts/configure_firewall.sh`)를 자동 생성하고 복구 명령어를 뚜렷한 경고 박스로 출력합니다.
3. **Given** 사용자가 `sudo ./setup.sh`로 통째로 스크립트를 실행한 경우, **When** 설치 완료 시, **Then** `$SUDO_USER`를 감지하여 `.venv`, `logs`, `config` 소유권을 일반 사용자 계정으로 자동 원복(`chown`)하여 permission denied 오류를 방지합니다.

---

### User Story 2 - 멀티 OS 방화벽(ufw / firewalld / nftables / iptables) 감지 및 포트 개방 자동화 (Priority: P2)

타겟 서버의 Linux 리눅스 배포판(Ubuntu/Debian, CentOS/RHEL/Rocky, Arch 등)에 활성화된 OS 방화벽 백엔드를 자동 감지하고 서비스 포트(`8081/tcp`, `8089/tcp`) 및 서브넷 CIDR 허용 규칙을 정확히 등록합니다.

**Why this priority**: 타겟 서버 OS 배포판마다 방화벽 관리 유틸리티가 상이하더라도 100% 동일하게 포트가 개방되도록 보장합니다.

**Independent Test**: ufw 또는 firewalld가 활성화된 서버에서 `setup.sh` 실행 시 각 방화벽 시스템에 맞게 8081/tcp 및 8089/tcp 포트 허용 규칙이 정상 반영되는지 검증합니다.

**Acceptance Scenarios**:

1. **Given** ufw가 활성화된 Ubuntu 서버에서, **When** `setup.sh`를 실행하면, **Then** `ufw allow 8081/tcp`, `ufw allow 8089/tcp` 규칙이 반영되고 상태 진단서에 `8081/tcp ALLOWED`가 표출됩니다.
2. **Given** firewalld가 활성화된 Rocky Linux 서버에서, **When** `setup.sh`를 실행하면, **Then** `firewall-cmd --add-port=8081/tcp --permanent` 및 `--reload` 명령이 수행됩니다.

---

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `scripts/setup.sh` 최전단 `sudo -v` 권한 승격 및 백그라운드 타임스탬프 갱신 데몬 구현
- **DoD-002**: `ufw`, `firewalld`, `iptables`, `nftables` 자동 감지 및 8081/8089 포트 개방 스크립트 작성
- **DoD-003**: 비대화형 환경을 위한 방화벽 자동 구성 전용 헬퍼 스크립트 (`scripts/configure_firewall.sh`) 생성 파이프라인 구축
- **DoD-004**: `sudo ./setup.sh` 직접 실행 시 `$SUDO_USER` 계정 소유권 자동 보정(`chown -R`) 로직 구현
- **DoD-005**: 시드 팩 번들 빌드 스크립트(`scripts/make_seed_pack.py`) 내 권한/방화벽 구성 요소 반영 및 100% 오프라인 실측 검증 통과

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `setup.sh` 스크립트는 실행 최전단(Step 0)에서 TTY 환경 여부를 감지하고 `sudo -v`를 수행하여 비밀번호 1회 입력으로 관리자 권한을 미리 확보해야 한다.
- **FR-002**: `setup.sh` 실행 도중 sudo 세션이 만료되지 않도록 스크립트가 실행되는 동안 백그라운드 타임스탬프 갱신 루프(`while true; do sudo -n true; sleep 50; ...`)를 유지해야 한다.
- **FR-003**: `setup.sh`는 타겟 OS 방화벽 엔진(`ufw`, `firewalld`, `nftables`, `iptables`)을 감지하고 `8081/tcp` (대시보드/OpenAI API) 및 `8089/tcp` (백엔드 포트) 허용 규칙을 자동 등록해야 한다.
- **FR-004**: 비대화형 환경(CI/CD)으로 인해 sudo 권한을 확보하지 못하는 경우, 관리자가 직접 구동 가능한 쉘 스크립트(`scripts/configure_firewall.sh`)를 자동 생성하고 터미널에 뚜렷한 복구 명령어를 표출해야 한다.
- **FR-005**: 시드 팩 압축 생성 시(`scripts/make_seed_pack.py`) 최신 방화벽 제어 모듈과 권한 검증 스크립트가 누락 없이 번들링되어 100% 오프라인 마이그레이션이 가능해야 한다.
- **FR-006**: 헌장 v1.3.1 (실체적 테스트 및 Anti-Mock)에 따라 테스트 수트는 목업 없이 실제 OS 소켓 바인딩 및 방화벽 룰셋(`ufw status`, `firewall-cmd --list-ports`) 파싱을 통해 실측 검증해야 한다.
- **FR-007**: 사용자가 `sudo ./setup.sh`로 직접 실행한 경우, 스크립트 종료 시 `$SUDO_USER`를 감지하여 `.venv/`, `logs/`, `config/` 및 소스 파일 소유권을 일반 사용자 계정으로 자동 환원(`chown -R $SUDO_USER:$SUDO_USER .`)해야 한다.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 시드 팩 마이그레이션 타겟 서버에서 `./setup.sh` 실행 시 sudo 권한 재요청 없이 포트 개방 및 환경 구축 성공률 100%
- **SC-002**: 방화벽 개방 후 동일 내부망(`10.0.0.0/8`, `192.168.0.0/16`) 클라이언트 PC에서 대시보드(`http://<TARGET_IP>:8081/dashboard/`) 및 API 즉시 접속 성공
- **SC-003**: `sudo ./setup.sh` 실행 후 일반 계정으로 `./scripts/start_server.sh` 구동 시 Permission Denied 오류 발생율 0%
- **SC-004**: 비대화형 설치 실패 시 복구 명령어 파악 시간 10초 이내 (강조 박스 가이드 제공)

---

## Assumptions

- 서버 OS는 Linux (Ubuntu, Debian, Rocky Linux, RHEL, CentOS 등) 환경임.
- 타겟 서버 사용자 계정은 `sudo` 권한을 부여받았거나 root 권한을 사용할 수 있는 상태를 전제로 함.

# Research & Design Decisions: 시드 팩 마이그레이션 및 setup.sh 관리자 권한·방화벽 자동화

**Feature Branch**: `039-seed-pack-sudo-firewall-migration`  
**Created**: 2026-07-30  
**Status**: Completed  

---

## 1. Sudo 권한 승격 및 백그라운드 타임스탬프 갱신 데몬 (Sudo Credential Management)

### Decision
`setup.sh` 실행 최전단(Step 0)에서 TTY 환경 여부를 감지하여, 대화형 TTY인 경우 `sudo -v`를 통해 사용자에게 1회 비밀번호 입력을 요청합니다. 이후 `setup.sh` 종료 시까지 sudo 인증 세션이 만료되지 않도록 백그라운드 주기적 타임스탬프 갱신 데몬(`while true; do sudo -n true; sleep 50; done &`)을 실행하며, 스크립트 종료/중단 시 `trap`을 이용하여 데몬 프로세스를 깔끔히 정리(kill)합니다.

### Rationale
- Linux `sudo` 갱신 기본 타임아웃은 보통 5~15분입니다. 오프라인 시드 팩 설치(가상환경 동기화, CUDA 가속 검증, 방화벽 설정 등) 중 타임아웃으로 sudo 세션이 끊기면 방화벽 개방 시점에서 `Permission Denied` 오류 또는 비대화형 대기로 실패가 발생합니다.
- `sudo -v`는 자격 증명을 갱신하며 TTY 입력창을 제공하고, `sudo -n true`는 비대화형(-n)으로 비밀번호 입력 없이 타임스탬프만 업데이트하므로 사용자 재개입 없이 안전하게 세션을 유지할 수 있습니다.
- `trap 'kill $SUDO_KEEPALIVE_PID 2>/dev/null || true' EXIT INT TERM`을 통해 프로세스 누수를 방지합니다.

### Alternatives Considered
- **전체 스크립트를 root 계정으로만 강제 실행 (`if [ $EUID -ne 0 ]; exit 1`)**:
  - 사용자 환경의 `.venv`, `logs`, `config` 파일들이 `root:root` 소유권으로 생성되어 설치 후 일반 계정 실행 시 Permission Denied 문제가 다수 발생하므로 부적절함.
- **`sudo` 타임아웃 갱신 없이 매 명령마다 `sudo` 호출**:
  - 장시간 소요 작업 중 타임아웃 만료 시 중간에 대화형 프롬프트가 다시 뜨거나 비대화형 환경에서 실패함.

---

## 2. 멀티 OS 방화벽 엔진 감지 및 포트 개방 자동화 (Multi-OS Firewall Detection & Rules)

### Decision
타겟 Linux 시스템의 방화벽 백엔드 존재 유무 및 활성화(active) 상태를 아래 우선순위 순서대로 자동 감지하여 지원 포트(`8081/tcp`, `8089/tcp`)를 개방합니다:
1. `ufw` (Ubuntu / Debian 계열)
   - 검증: `command -v ufw` 및 `ufw status`
   - 적용: `sudo ufw allow 8081/tcp`, `sudo ufw allow 8089/tcp`
2. `firewalld` (RHEL / CentOS / Rocky Linux / Fedora 계열)
   - 검증: `command -v firewall-cmd` 및 `firewall-cmd --state`
   - 적용: `sudo firewall-cmd --permanent --add-port=8081/tcp`, `sudo firewall-cmd --permanent --add-port=8089/tcp`, `sudo firewall-cmd --reload`
3. `nftables` (최신 Debian / Arch / RHEL 등)
   - 검증: `command -v nft` 및 `nft list ruleset`
   - 적용: `sudo nft add rule inet filter input tcp dport { 8081, 8089 } accept` (또는 활성화된 테이블 감지 후 추가)
4. `iptables` (레거시 Linux 범용)
   - 검증: `command -v iptables`
   - 적용: `sudo iptables -C INPUT -p tcp --dport 8081 -j ACCEPT 2>/dev/null || sudo iptables -A INPUT -p tcp --dport 8081 -j ACCEPT` (8089/tcp 동일)
5. `unknown` / 미구동
   - 방화벽 서비스가 없거나 비활성화 상태인 경우 경고 메시지 출력 후 정상 진행.

### Rationale
- 오프라인 타겟 서버는 배포판마다 사용하는 방화벽 관리가 다릅니다 (Ubuntu는 `ufw`, Rocky/RHEL은 `firewalld`, 최신 커널은 `nftables`).
- 활성화된 방화벽 백엔드를 감지하지 않고 단일 명령만 시도하면 포트 개방 실패가 발생하므로, 정확한 엔진 감지가 필수적입니다.

### Alternatives Considered
- **Python 단독 코드에서 방화벽 설정**:
  - `setup.sh` 쉘 스크립트 실행 초기 단계에서 가상환경 구성 전 방화벽을 여는 케이스가 포함되므로, 쉘 및 Python `FirewallManager` 양쪽에서 동일 로직을 수행할 수 있도록 상호 보완적으로 구성해야함.

---

## 3. 비대화형(CI/CD / Headless) 환경 폴백 및 헬퍼 스크립트 생성 (Non-interactive Fallback)

### Decision
`[ ! -t 0 ]` 또는 `sudo -n true 2>/dev/null` 실패로 TTY 대화형 sudo 권한을 확보할 수 없는 비대화형 환경인 경우:
1. 방화벽 개방 명령이 담긴 실행 가능한 복구 스크립트 (`scripts/configure_firewall.sh`)를 자동으로 생성 (`chmod +x`).
2. 터미널 및 로그에 시각적으로 구별되는 뚜렷한 경고 박스(Warning Banner)를 표출하여 사용자가 root/sudo 권한으로 복구 스크립트를 수동 구동할 수 있도록 안내.
3. 전체 `setup.sh` 파이프라인은 방화벽 미개방 경고 상태로 계속 진행(Non-blocking Fail-safe).

### Rationale
- CI/CD 파이프라인이나 자동화 프로비저닝 스크립트에서는 비밀번호 입력을 받을 수 없으므로 `sudo -v`에서 스크립트 전체가 대기 상태로 중단되는 불상사를 방지해야 합니다.
- 자동 생성된 `scripts/configure_firewall.sh`를 통해 운영자는 단 한 줄의 명령(`sudo ./scripts/configure_firewall.sh`)으로 필요한 포트를 손쉽게 개방할 수 있습니다.

---

## 4. `sudo ./setup.sh` 직접 실행 시 소유권 자동 보정 (Ownership Remediation)

### Decision
사용자가 `sudo ./setup.sh` 명령으로 스크립트 전체를 root 권한으로 실행한 경우:
1. `$SUDO_USER`, `$SUDO_UID`, `$SUDO_GID` 환경변수를 감지.
2. 스크립트 완료 직전(Step Final) `.venv/`, `logs/`, `config/` 및 프로젝트 작업 파일의 소유권을 `chown -R $SUDO_USER:$SUDO_USER .`로 자동 환원.
3. `$SUDO_USER`가 없는 순수 root 직접 실행인 경우, 알림 메시지와 함께 주의 권고 표출.

### Rationale
- root 권한으로 생성된 `.venv` 내 파일이나 `logs/vllm_serv.log` 등은 추후 일반 사용자 계정으로 `./start_server.sh` 구동 시 `PermissionError: [Errno 13] Permission denied`를 발생시키는 주요 원인입니다.
- 자동 소유권 보정을 통해 계정 권한 차이로 인한 실행 장애를 100% 방지합니다.

---

## 5. 시드 팩 번들링 및 오프라인 이관 동기화 (Seed Pack Integration)

### Decision
`scripts/make_seed_pack.sh` 번들 생성 스크립트를 업데이트하여:
1. 새로 추가/수정된 방화벽 모듈 및 `scripts/configure_firewall.sh` 생성 로직이 압축 아카이브(`vllm_serv_seed_pack.tar.gz`)에 누락 없이 포함되도록 보장.
2. 오프라인 설치 환경에서 외부 네트워크 연결 없이 100% 로컬 바이너리 및 방화벽 룰셋 설정이 작동하도록 실측 검증.

---

## 6. 실체적 테스트 (Anti-Mock) 검증 전략 (Constitution v1.3.1 Compliance)

### Decision
1. `tests/unit/test_firewall_manager_real.py` 및 `tests/unit/test_shell_scripts.py`에서:
   - 가짜 subprocess mock 대신, 실제 `ufw status`, `firewall-cmd --state`, `iptables -L -n` 실행 결과를 쿼리하거나, 실제 소켓 연결 테스트(`127.0.0.1:8081`)를 수행.
   - `scripts/configure_firewall.sh` 구동 테스트 시 임시 경로 샌드박스에서 생성된 쉘 스크립트의 구문 검증(`bash -n`) 및 권한 실행 여부 실측.

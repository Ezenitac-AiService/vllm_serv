# Implementation Plan: 시드 팩 마이그레이션 및 setup.sh 관리자 권한·방화벽 자동화

**Branch**: `039-seed-pack-sudo-firewall-migration` | **Date**: 2026-07-30 | **Spec**: [spec.md](file:///home/dev/storage/vllm_serv/specs/039-seed-pack-sudo-firewall-migration/spec.md)

**Input**: User description & Feature specification from `/specs/039-seed-pack-sudo-firewall-migration/spec.md`

---

## Summary

오프라인 타겟 서버로 시드 팩(`vllm_serv_seed_pack.tar.gz`) 마이그레이션 및 `./setup.sh` 환경 구축 시 발생할 수 있는 권한 누수, 타임아웃 만료, 및 OS 방화벽 개방 장애를 근본적으로 자동화·해결합니다.
1. `setup.sh` 최전단(Step 0)에서 TTY 환경 감지 시 `sudo -v` 승격 및 백그라운드 타임스탬프 갱신 데몬(`while true; do sudo -n true; sleep 50; done &`)을 구동하여 설치 완료 시까지 관리자 권한을 영구 유지합니다.
2. 비대화형(CI/CD) 환경 시 복구 헬퍼 스크립트(`scripts/configure_firewall.sh`) 자동 생성 및 터미널 경고 박스를 표출합니다.
3. `sudo ./setup.sh` 구동 시 `$SUDO_USER` 계정을 감지하여 완료 후 `.venv`, `logs`, `config` 디렉토리 소유권을 일반 사용자 계정으로 자동 원복(`chown -R`)합니다.
4. 멀티 OS 방화벽(`ufw`, `firewalld`, `nftables`, `iptables`)을 감지하고 서비스 포트(`8081/tcp`, `8089/tcp`) 개방을 자동화합니다.
5. 시드 팩 번들링 스크립트(`scripts/make_seed_pack.sh`)에 제어 로직을 통합하고, 헌장 v1.3.1에 따른 목업 없는 실측 테스트(Anti-Mock Real Probes)를 구축합니다.

---

## Technical Context

**Language/Version**: Bash Shell Scripting (POSIX/Bash 4+), Python 3.11  
**Primary Dependencies**: uv (PyPA toolchain), ufw, firewalld (`firewall-cmd`), nftables (`nft`), iptables, pytest  
**Storage**: Local Filesystem (`.venv/`, `logs/`, `config/`, `scripts/`)  
**Testing**: pytest (`uv run pytest tests/unit/test_firewall_manager_real.py tests/unit/test_shell_scripts.py`)  
**Target Platform**: Linux Server (Ubuntu, Debian, Rocky Linux, RHEL, CentOS, Arch)  
**Project Type**: CLI / Shell Infrastructure Automation & LLM Serving Framework  
**Performance Goals**: `setup.sh` 최전단 sudo 승격 응답속도 <1초, 방화벽 포트 감지 및 개방 <2초, background keepalive 오버헤드 0%  
**Constraints**: 100% 오프라인 동작 가능(외부 인터넷 미연결 환경), 비대화형 CI/CD 지원(Non-blocking), 헌장 v1.3.1 (Anti-Mock strict compliance)  
**Scale/Scope**: 오프라인 마이그레이션 시드 팩 설치 환경, 2개 서비스 포트(8081, 8089) 자동 관리  

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] 계획서가 한국어로 작성되었는가? (언어 정책)
- [x] 테스트 코드 작성 계획이 포함되어 있는가? (테스트 필수 원칙)
- [x] 목업은 유료/제한 API로 엄격히 제한하고 실물 시스템/소켓/OS 인자 및 실제 호출 플래그(REAL_API_CALL=1) 기반 실측 검증 계획이 포함되어 있는가? (실체적 테스트 및 수렴 검증 원칙)
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (종료 조건 명확화 원칙)
- [x] 비파괴적 문서 수정 원칙을 준수하는가? (비파괴적 문서 수정 원칙)
- [x] uv 패키지 매니저 및 가상환경 격리 표준(uv run)을 준수하는가? (uv 패키지 및 환경 관리 원칙)

---

## Project Structure

### Documentation (this feature)

```text
specs/039-seed-pack-sudo-firewall-migration/
├── spec.md              # Feature specification
├── plan.md              # Implementation plan (this file)
├── research.md          # Phase 0 output (design decisions & sudo/firewall research)
├── data-model.md        # Phase 1 output (entities, states, lifecycle)
├── quickstart.md        # Phase 1 output (validation & run guide)
└── contracts/           # Phase 1 output (interface contracts)
    ├── setup_sh_contract.md
    ├── configure_firewall_sh_contract.md
    └── firewall_manager_contract.md
```

### Source Code (repository root)

```text
scripts/
├── setup.sh                 # Sudo elevation, keepalive daemon, ownership chown, multi-OS firewall setup
├── configure_firewall.sh   # Standalone/Fallback firewall port opening helper script
└── make_seed_pack.sh        # Seed pack bundling script including firewall & setup components

src/
└── core/
    └── firewall_manager.py  # Python FirewallManager module (ufw/firewalld/nftables/iptables & socket probes)

tests/
└── unit/
    ├── test_firewall_manager.py
    ├── test_firewall_manager_real.py  # Non-mocked real OS firewall & socket probe tests
    ├── test_seed_pack.py
    └── test_shell_scripts.py         # Shell script syntax & execution unit tests
```

**Structure Decision**: Single project layout matching existing `scripts/`, `src/core/`, and `tests/unit/` directories.

---

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | Constitution Check 100% passed without violations |

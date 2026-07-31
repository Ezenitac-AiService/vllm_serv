# Implementation Plan: 서버 방화벽 구축 파이프라인 전수 검토 및 E2E 실측 테스트 (038-server-firewall-setup-pipeline)

**Branch**: `038-server-firewall-setup-pipeline` | **Date**: 2026-07-30 | **Spec**: [`spec.md`](file:///home/dev/storage/vllm_serv/specs/038-server-firewall-setup-pipeline/spec.md)

**Input**: Feature specification from `/specs/038-server-firewall-setup-pipeline/spec.md`

## Summary

본 계획은 서버 구축 및 구동 파이프라인(`scripts/setup.sh`, `scripts/start_server.sh`, `src/core/firewall_manager.py`)에서 OS 방화벽(`ufw`, `iptables`, `firewalld`) 규칙이 비대화형 `sudo -n` 실패로 인해 거부되던 문제를 전수 개정합니다. TTY 대화형 터미널을 감지하여 비밀번호 입력 창으로 수동 승격 유도하고, 비대화형 환경 시 복구 명령어 안내를 붉은색 강조 박스로 표출합니다. 또한 **헌장 v1.3.1 (실체적 테스트 검증 원칙)**을 충실히 반영하여 기존 루프백(127.0.0.1) 인메모리 테스트를 완전히 탈피하고, 서버 실물 IP(`http://10.0.0.41:8081/dashboard/`)를 직접 호출하는 Playwright E2E UI/UX 사용성 및 물리 TCP 소켓 연결 테스트 수트(`tests/e2e/test_dashboard_e2e.py`)를 도입합니다.

## Technical Context

**Language/Version**: Python 3.12, Bash (POSIX compliant)  
**Primary Dependencies**: FastAPI, `ufw`, `iptables`, `firewalld`, Playwright / `pytest-playwright` / `httpx`, `socket`  
**Storage**: Config JSON (`config/server_config.json`, `/etc/ufw/user.rules`)  
**Testing**: `pytest` (`REAL_NETWORK_TEST=1 uv run pytest tests/e2e/test_dashboard_e2e.py -v`)  
**Target Platform**: Linux Server (Platform A 10.0.0.41 / ufw / Dual LAN 10.0.0.0/8)  
**Project Type**: Infrastructure & Automation Pipeline / Web E2E Testing  
**Performance Goals**: 방화벽 룰셋 검증 100ms 이내 완료, 포트 진단 실패 시 10초 이내에 사용자 가이드 복구 명령 제공  
**Constraints**: 인메모리 목업(Mock) 전면 금지, 실물 IP 네트워크 소켓 및 실제 브라우저 E2E 실측 준수, `uv run` 표준 준수  
**Scale/Scope**: `scripts/setup.sh`, `scripts/start_server.sh`, `src/core/firewall_manager.py`, `tests/e2e/test_dashboard_e2e.py`  

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] 계획서가 한국어로 작성되었는가? (언어 정책 준수)
- [x] 테스트 코드 작성 계획이 포함되어 있는가? (테스트 필수 원칙 준수)
- [x] 목업은 유료/제한 API로 엄격히 제한하고 실물 시스템/소켓/OS 인자 및 실제 호출 플래그(REAL_NETWORK_TEST=1) 기반 실측 검증 계획이 포함되어 있는가? (헌장 v1.3.1 실체적 테스트 및 수렴 검증 원칙 준수)
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (DoD-001 ~ DoD-004 정의 완료)
- [x] 비파괴적 문서 수정 원칙을 준수하는가? (기존 문서 개별 편집 원칙 준수)
- [x] uv 패키지 매니저 및 가상환경 격리 표준(uv run)을 준수하는가? (`uv run pytest`, `uv sync` 준수)

## Project Structure

### Documentation (this feature)

```text
specs/038-server-firewall-setup-pipeline/
├── plan.md              # 본 계획서 (/speckit-plan command output)
├── research.md          # Phase 0 연구 문서 (TTY 감지 & Playwright 실물 IP E2E 결정)
├── data-model.md        # Phase 1 데이터 모델 (FirewallReport, SocketResult, E2EResult)
├── quickstart.md        # Phase 1 빠른 검증 가이드 및 시연 절차
├── contracts/           # API 인터페이스 정의 (firewall_pipeline_contract.json)
└── checklists/
    └── requirements.md  # 스펙 품질 검증 체크리스트
```

### Source Code (repository root)

```text
scripts/
├── setup.sh             # TTY 감지 및 방화벽 포트 자동 승격/안내 강화
└── start_server.sh      # 서버 구동 전 8081/8089 포트 방화벽 사전 점검 (Pre-flight Check)

src/core/
└── firewall_manager.py  # ufw/firewalld/iptables 상태 실측 탐지 및 포트 개방 유틸리티

tests/
└── e2e/
    └── test_dashboard_e2e.py # 서버 실물 IP(10.0.0.41) 타겟 Playwright E2E 대시보드 UI/UX 테스트
```

**Structure Decision**: 기존 Shell 설치 스크립트(`scripts/`) 및 파이썬 커널 방화벽 제어기(`src/core/firewall_manager.py`)를 강화하고, 새로운 E2E 검증 디렉토리(`tests/e2e/`)를 신설하여 실물 IP 테스트를 수용합니다.

## Complexity Tracking

*No constitution violations. Architecture is fully compliant with v1.3.1.*

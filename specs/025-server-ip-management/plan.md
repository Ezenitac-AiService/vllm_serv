# Implementation Plan: 듀얼 랜포트 다중 NIC 환경 서버 IP 바인딩 및 네트워크 관리 로직 고도화 (025-server-ip-management)

**Branch**: `025-server-ip-management` | **Date**: 2026-07-30 | **Spec**: [spec.md](file:///home/dev/storage/vllm_serv/specs/025-server-ip-management/spec.md)

**Input**: Feature specification from `/specs/025-server-ip-management/spec.md`

## Summary

서비스 플랫폼(i7 930 / GTX 1070)을 포함한 서버보드 듀얼 NIC 환경에서 할당된 외부 LAN IP(`192.168.0.80`)로 접속할 수 없었던 문제와 미할당 랜포트 탐지 예외를 해결합니다. `ConfigManager` 및 `server_config.json` 호스트 바인딩을 `0.0.0.0` 기반으로 고도화하고, 활성 네트워크 인터페이스(NIC) 자동 탐지 및 OS 방화벽(`ufw`/`iptables`) 포트 개방 자동화/가이드 출력을 구현하여 원격 훈련생 단말기 접속 정합성을 완성합니다.

## Technical Context

**Language/Version**: Python 3.12 (`uv` 패키지 매니저 가상환경)  
**Primary Dependencies**: FastAPI, Uvicorn, psutil, llama-cpp-python  
**Storage**: JSON configuration (`config/server_config.json`, `config/platform_profiles.json`)  
**Testing**: `uv run pytest` (단위 및 통합 테스트 수트)  
**Target Platform**: Linux server (Linux x86_64, NVIDIA GTX 1080 Ti / RTX 3060 / GTX 1070)  
**Project Type**: Multi-platform LLM serving web service & C++ binary backend  
**Performance Goals**: 소켓 바인딩 및 활성 NIC 탐지 오버헤드 < 50ms, 외부 LAN HTTP GET `/health` 응답 지연 < 100ms  
**Constraints**: 듀얼 NIC 중 미할당 포트 연결 장애 예외 패스, non-root 권한 구동 시 OS 방화벽 명령 에러에 따른 프로세스 다운 방지  
**Scale/Scope**: 3종 타겟 머신 플랫폼 (`e3-1231v3`, `i7-4770`, `i7-930`), 192.168.0.0/16 사설 LAN 대역 수용  

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] 계획서가 한국어로 작성되었는가? (언어 정책 - 헌장 I)
- [x] 테스트 코드 작성 계획이 포함되어 있는가? (테스트 필수 원칙 - 헌장 II)
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (종료 조건 명확화 원칙 - 헌장 III)
- [x] 기존 문서를 비파괴적으로 유지 관리하는가? (비파괴적 문서 수정 원칙 - 헌장 IV)
- [x] `uv` 패키지 및 환경 실행 명령(`uv run`)을 전적으로 활용하는가? (uv 패키지 및 환경 관리 원칙 - 헌장 V)

## Project Structure

### Documentation (this feature)

```text
specs/025-server-ip-management/
├── spec.md              # Feature specification
├── plan.md              # Implementation plan (this file)
├── research.md          # Technical research & decisions (Phase 0)
├── data-model.md        # Data models & entities (Phase 1)
├── quickstart.md        # Validation scenarios & guide (Phase 1)
├── contracts/           # Interface contracts (Phase 1)
│   └── network-config-contract.json
└── checklists/
    └── requirements.md  # Quality checklist
```

### Source Code Layout

```text
src/
├── core/
│   ├── config_manager.py      # Bind host, active NIC detection, subnet config integration
│   ├── network_detector.py    # Active NIC & LAN IP automatic scanner module
│   ├── firewall_manager.py   # OS firewall (ufw/iptables) auto port opener & exception logger
│   ├── process_manager.py     # Propagation of host binding (0.0.0.0) to llama-server sub-processes
│   └── subnet_filter.py       # Subnet access control & LAN IP dynamic authorization
├── api/
│   └── server.py              # FastAPI host binding & CORS setup for external LAN IPs

config/
├── server_config.json         # host: "0.0.0.0" and network configurations
└── platform_profiles.json     # Network binding rules per platform profile

tests/
├── unit/
│   ├── test_network_detector.py  # Active NIC scanner unit tests
│   ├── test_firewall_manager.py # OS firewall attempt & exception handling tests
│   └── test_config_manager.py   # Bind host & network config unit tests
└── integration/
    └── test_subnet_security.py   # Multi-NIC external IP access integration tests
```

**Structure Decision**: 기존 `src/core/` 중심 백엔드 아키텍처에 `network_detector.py` 및 `firewall_manager.py` 모듈을 추가하여 네트워크 바인딩 및 방화벽 제어 로직을 캡슐화합니다.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

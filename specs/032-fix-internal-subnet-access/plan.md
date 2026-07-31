# Implementation Plan: 서비스 플랫폼 사설망(192.168.0.x) 듀얼 랜 포트(Dual NIC) 호스트 IP 기반 동적 서브넷 허용 및 접근 차단 해제 (032-fix-internal-subnet-access)

**Branch**: `032-fix-internal-subnet-access` | **Date**: 2026-07-30 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/032-fix-internal-subnet-access/spec.md`

## Summary

서비스 플랫폼(`legacy-i7-930-gtx1070` 및 `pascal-avx2-gtx1080ti` 등 운영/개발 장비)의 듀얼 랜 포트(Dual NIC) 환경에서, `NetworkDetector.get_active_lan_ips()`를 활용하여 활성화된 모든 사설망 LAN IP(`192.168.0.x`, `10.x.x.x` 등)를 멀티 탐지합니다.

탐지된 IP 주소로부터 사설 CIDR 대역(`192.168.0.0/16`, `10.0.0.0/8`, `172.16.0.0/12`)을 런타임 합집합(Union)으로 합성하고, `config/platform_profiles.json` 프로필 및 `src/api/server.py`의 `SubnetFilterMiddleware`에 동적으로 포함시킴으로써 사설망 클라이언트 접근 차단을 완벽히 해제합니다.

## Technical Context

**Language/Version**: Python 3.12+ (FastAPI, Starlette Middleware, `ipaddress` stdlib)

**Primary Dependencies**: `fastapi`, `starlette`, `psutil` (in `NetworkDetector`)

**Storage**: Configuration files (`config/platform_profiles.json`, `config/server_config.json`)

**Testing**: `pytest`, `httpx` (AsyncTestClient / TestClient), `tests/unit/test_network_detector.py`, `tests/integration/test_subnet_security.py`

**Target Platform**: Linux (Ubuntu Server 24.04 LTS), Platform C (`legacy-i7-930-gtx1070`) & Platform A (`pascal-avx2-gtx1080ti`) Dual NIC Servers

**Project Type**: Network Security & Access Control Middleware

**Performance Goals**: 서브넷 대역 동적 추출 및 검증 오버헤드 < 1ms, 사설망 IP 접속 차단 0건 (HTTP 200 OK)

**Constraints**: 사설망 RFC 1918 대역(`192.168.0.0/16`, `10.0.0.0/8`, `172.16.0.0/12`) 동적 주입, 듀얼 NIC 미사용/다운 포트 스킵

**Scale/Scope**: `config/platform_profiles.json`, `src/api/server.py`, `src/core/config_manager.py`, `src/api/middleware/subnet_filter.py`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] 계획서가 한국어로 작성되었는가? (언어 정책)
- [x] 테스트 코드 작성 계획이 포함되어 있는가? (테스트 필수 원칙 - 듀얼 NIC IP 탐지 및 192.168.0.x 접속 검증)
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (종료 조건 명확화 원칙 - DoD-001 ~ DoD-003 준수)
- [x] 비파괴적 문서 수정 원칙을 준수하는가? (비파괴적 문서 수정 원칙)
- [x] uv 패키지 매니저 및 가상환경 격리 표준(uv run)을 준수하는가? (uv 패키지 및 환경 관리 원칙)

## Project Structure

### Documentation (this feature)

```text
specs/032-fix-internal-subnet-access/
├── spec.md              # Feature specification
├── plan.md              # Implementation Plan (/speckit-plan output)
├── research.md          # Phase 0 output (/speckit-plan output)
├── data-model.md        # Phase 1 output (/speckit-plan output)
├── quickstart.md        # Phase 1 output (/speckit-plan output)
├── contracts/           # Phase 1 Contract output
│   └── network-config-contract.json
└── tasks.md             # Phase 2 output (/speckit-tasks output - pending)
```

### Source Code (repository root)

```text
config/
└── platform_profiles.json   # FR-002: legacy-i7-930-gtx1070 및 pascal-avx2-gtx1080ti 프로필 allowed_subnets에 192.168.0.0/16 추가

src/
├── api/
│   ├── server.py            # FR-001: NetworkDetector.get_active_lan_ips() 기반 동적 allowed_subnets 주입
│   └── middleware/
│       └── subnet_filter.py # FR-001: 사설 CIDR 대역 동적 검증 헬퍼
└── core/
    └── config_manager.py    # FR-001: get_detected_network_info() 서브넷 결합 로직 고도화

tests/
├── unit/
│   ├── test_config_manager_profiles.py # FR-003: 프로필 서브넷 수록 검증
│   └── test_network_detector.py        # FR-003: 듀얼 NIC IP 탐지 검증
└── integration/
    └── test_subnet_security.py         # FR-003: 192.168.0.x 허용 및 외부 IP 차단 검증
```

**Structure Decision**: Single project layout updating existing configuration JSON and FastAPI server middleware/config manager modules.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

*violations: None. Network configuration and middleware allowed_subnets enhancement.*

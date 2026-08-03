# Implementation Plan: samples 예제 스크립트의 서비스 플랫폼 IP 대역 접속 보장 및 테스트 스크립트 실 IP 검증 분리 명세 (070-samples-platform-ip-separation)

**Branch**: `main` (또는 `070-samples-platform-ip-separation`)
**Spec**: [`specs/070-samples-platform-ip-separation/spec.md`](spec.md)
**Created**: 2026-08-03

---

## Technical Context & Strategy

### Objective
- `/home/dev/storage/vllm_serv/samples`의 예제 코드에 `samples/config.json` 및 `.env` 파일 파싱 기능을 연동하여 훈련생들이 서비스 플랫폼 IP(`192.168.0.x`) 접속 주소를 자유롭게 명시하고 독립적으로 활용하도록 지원.
- `/home/dev/storage/vllm_serv/tests`의 테스트 수트에 실행 플랫폼(`10.0.0.x` 등)의 동적 LAN IP 탐지 바인딩을 보장하고, `127.0.0.1` 및 `localhost` 접속을 완전히 차단/제거하여 수신 가능 상태 검증.

### Architecture Overview
1. **Sample Configuration Loader (`samples/common.py`)**
   - 표준 `json` 및 `os` 모듈을 활용하여 `SERVER_HOST` 환경변수 > `samples/.env` > `samples/config.json` > 기본값(`http://192.168.0.100`) 순서로 감지 로더 구축.
   - 훈련생 전용 기본 설정 가이드 파일 `samples/config.json.example` 배치.
2. **Test Dynamic IP Fixture (`tests/conftest.py`)**
   - `target_host_ip` 세션 피스처에서 `NetworkDetector.get_active_lan_ips()`를 활용하여 현재 개발/테스트 환경의 실 LAN IP(`10.0.0.x`)를 주입.

---

## Phase 0: Research & Analysis
- [x] **Research Completed**: [`research.md`](research.md)
  - `samples/` 설정 로더 경량화 전략 수립 완료 (표준 라이브러리 사용)
  - `tests/` 동적 LAN IP 피스처 설계 완료

---

## Phase 1: Design & Artifacts
- [x] **Data Model**: [`data-model.md`](data-model.md)
- [x] **Contracts**: [`contracts/sample_config_contract.json`](contracts/sample_config_contract.json)
- [x] **Quickstart Validation Guide**: [`quickstart.md`](quickstart.md)

---

## Phase 2: Task Planning & Execution Roadmap
1. `samples/config.json.example` 생성 및 `samples/common.py`에 `config.json` / `.env` 파싱 로더 구현.
2. `tests/conftest.py` 내 `target_host_ip` 피스처가 `NetworkDetector.get_active_lan_ips()` 기반으로 실행 플랫폼 IP를 동적으로 지정하도록 보장.
3. 단위 테스트 수트 (`tests/unit/test_sample_scripts.py`, `tests/unit/test_network_detector.py`) 업데이트 및 전체 회귀 테스트 통과 검증.

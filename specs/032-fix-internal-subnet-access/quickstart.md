# Quickstart Validation Guide: 듀얼 NIC 사설망(192.168.0.x) 동적 서브넷 인가 검증 (032-fix-internal-subnet-access)

## 1. 개요 (Overview)

본 가이드는 서비스 플랫폼 장비의 듀얼 랜 포트(Dual NIC) 환경에서 `NetworkDetector`가 탐지한 실측 LAN IP(`192.168.0.x`) 대역 클라이언트 접근이 HTTP 403 차단 없이 200 OK로 인가되는지 검증하는 시나리오입니다.

---

## 2. 사전 조건 (Prerequisites)

- `uv` 패키지 매니저 및 파이썬 3.12+ 가상환경

---

## 3. 검증 시나리오 A: 단위 테스트 구동

### 명령어 실행

```bash
uv run pytest tests/unit/test_network_detector.py tests/unit/test_config_manager_profiles.py
```

### 기대 결과 (Expected Outcome)

- 듀얼 NIC 랜 포트 IP 스캔 및 `config/platform_profiles.json` 프로필 서브넷 수록 검증 테스트가 100% 통과 (`12 passed in < 3s`).

---

## 4. 검증 시나리오 B: 통합 서브넷 검증 테스트

### 명령어 실행

```bash
uv run pytest tests/integration/test_subnet_security.py
```

### 기대 결과 (Expected Outcome)

- `192.168.0.100` 및 `10.0.1.50` 사설 IP 클라이언트 요청 시 HTTP 200 OK 통과 및 외부 공인 IP 차단 테스트 100% 통과.

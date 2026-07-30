# Quickstart Validation Guide: 듀얼 랜포트 다중 NIC 환경 서버 IP 바인딩 및 네트워크 관리 (025-server-ip-management)

본 가이드는 듀얼 NIC 지원 서버(i7 930) 환경에서 외부 LAN IP (`192.168.0.80`) 접근 지원, 미할당 랜포트 예외 처리, OS 방화벽 개방 시도 동작을 검증하기 위한 런북입니다.

---

## 1. Prerequisites

- Python 3.12 (`uv` 패키지 관리자 환경)
- 사설 LAN 망 연결 (예: `192.168.0.80`) 및 듀얼 NIC 포트 환경
- `uv run pytest` 테스트 도구

---

## 2. Validation Scenarios

### Scenario 1: 네트워크 인터페이스 감지 및 유효 LAN IP 자동 수집 검증

**목적**: 듀얼 랜포트 중 IP 미할당 포트를 안전하게 패스하고 활성 LAN IP만을 수집하는지 검증합니다.

```bash
uv run python -c "from src.core.config_manager import ConfigManager; print(ConfigManager().get_detected_network_info())"
```

**예상 결과**:
- 듀얼 NIC 중 미할당 포트로 인한 에러 없음
- `detected_active_ips` 목록에 활성 LAN IP (`192.168.0.80` 등)가 정상 반환됨

---

### Scenario 2: 외부 LAN IP 바인딩 및 REST API 연결 테스트

**목적**: 외부 원격 단말기에서 할당된 LAN IP로 API 접속 시 정상 200 OK 수신되는지 검증합니다.

```bash
# 1. 서버 구동
uv run python src/api/server.py

# 2. 다른 터미널 또는 외부 단말기에서 헬스체크 및 모델 목록 조회
curl -i http://192.168.0.80:8081/health
curl -i http://192.168.0.80:8081/v1/models
```

**예상 결과**:
- HTTP/1.1 200 OK 응답 반환
- `SubnetFilter` 또는 CORS 레벨 거부 없이 JSON 결과 반환

---

### Scenario 3: OS 방화벽 개방 시도 및 예외 처리 검증

**목적**: OS 방화벽 포트 개방 시도 시 non-root 환경에서도 다운 없이 가이드 로그를 출력하는지 검증합니다.

```bash
uv run pytest tests/unit/test_firewall_manager.py
```

**예상 결과**:
- 단위 테스트 100% PASS
- `sudo` 권한 미보유 시 warning 로그 및 `sudo ufw allow 8081/tcp` 가이드 메시지 확인

---

### Scenario 4: 전체 테스트 수트 수행

```bash
uv run pytest tests/
```

**예상 결과**:
- 전체 단위 및 통합 테스트 수트 100% 통과

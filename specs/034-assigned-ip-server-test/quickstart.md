# Quickstart Guide: Assigned IP Server Verification Test

## Overview

본 가이드는 할당된 IP 기반 서버 구동 검증 테스트 기능의 구현 결과를 빠르게 검증하고 검사할 수 있는 실행 시나리오를 안내합니다.

## Prerequisites

1. 파이썬 환경 격리 관리자 `uv` 설치 완료.
2. 테스트 수행 전 필요한 의존성이 설치되어 있는지 확인:
   ```bash
   uv sync
   ```

## Runnable Validation Scenarios

### Scenario 1: 네트워크 인터페이스 감지 및 IP 수집 단위 테스트

호스트의 듀얼랜 포트를 포함한 활성 비-루프백 IP가 정상 탐지되는지 확인합니다.

```bash
uv run pytest tests/unit/test_network_detector.py -v
```

### Scenario 2: 서버 할당 IP 구동 검증 통합 테스트

서버를 가상 구동/Mock 구동시킨 상태에서 `127.0.0.1` 및 모든 할당 LAN IP를 통한 접속, API 호출, 응답 검증을 수행합니다.

```bash
uv run pytest tests/integration/test_server_assigned_ip.py -v
```

### Scenario 3: 전체 테스트 Suite 실행 및 정합성 검증

프로젝트 헌장 원칙에 따라 기존 테스트와의 충돌 없이 전체 테스트가 정상 수행되는지 검증합니다.

```bash
uv run pytest -v
```

## Expected Outcomes

- `127.0.0.1` 루프백 접속 성공.
- 호스트에 할당된 모든 비-루프백 IP 주소(듀얼랜 포함) 접속 및 HTTP 200 응답 성공.
- 접속 불가 또는 바인딩 오류 발생 시 해당 IP 주소와 함께 명확한 원인 진단 로그 출력.

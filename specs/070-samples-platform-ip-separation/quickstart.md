# Quickstart Validation Guide: samples 예제 스크립트의 서비스 플랫폼 IP 대역 접속 보장 및 테스트 스크립트 실 IP 검증 분리 (070-samples-platform-ip-separation)

## 1. 개요
이 가이드는 `samples/` 예제 스크립트의 설정 파일(`config.json` / `.env`)을 통한 서비스 플랫폼 접속 및 `tests/` 회귀 테스트 스크립트의 동적 실 IP 기반 수신 검증이 정상 동작하는지 확인하는 검증 절차입니다.

---

## 2. 검증 시나리오

### 시나리오 1: samples/ 예제 스크립트의 config.json 기반 접속 검증
1. `samples/config.json` 생성:
   ```json
   {
     "server_host": "http://192.168.0.100"
   }
   ```
2. `samples/common.py` 실행 검증:
   ```bash
   uv run python -c "from samples.common import get_server_host; print(get_server_host())"
   ```
   - **기대 결과**: `http://192.168.0.100` 출력 확인.

3. 환경변수 최우선 적용 검증:
   ```bash
   SERVER_HOST="http://192.168.0.250" uv run python -c "from samples.common import get_server_host; print(get_server_host())"
   ```
   - **기대 결과**: `http://192.168.0.250` 출력 확인.

---

### 시나리오 2: tests/ 수트의 127.0.0.1 / localhost 미사용 및 동적 실 IP 감지 검증
1. 테스트 코드 내 `127.0.0.1` 및 `localhost` 하드코딩 부재 검증:
   ```bash
   uv run pytest tests/unit/test_sample_scripts.py tests/unit/test_network_detector.py
   ```
   - **기대 결과**: 전체 통과 (`12 passed`).

2. 전체 회귀 테스트 통과 검증:
   ```bash
   uv run pytest -q
   ```
   - **기대 결과**: 87개 이상의 단위 및 회귀 테스트 100% Green Pass.

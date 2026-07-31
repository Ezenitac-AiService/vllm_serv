# Quickstart & End-to-End Validation Guide: 실 IP 동적 감지 연동 (064-sample-scripts-real-ip)

**Feature**: `064-sample-scripts-real-ip`

## 1. 개요 (Overview)

본 가이드는 하드코딩 없는 실 IP 동적 탐지 기능(`NetworkDetector` 결합 `samples/common.py` `get_server_host()`)을 통해 3종 플랫폼(`192.168.0.x` 2종, `10.0.0.x` 1종) 및 듀얼 랜포트 환경에서 샘플 스크립트 5종이 예외 없이 실 IP 엔드포인트로 통신하는지 검증하는 절차입니다.

---

## 2. 검증 시나리오 (Validation Scenarios)

### 시나리오 1: 기본 실 IP 동적 감지 호출 검증
```bash
uv run python samples/sample_01_chat.py
```
**기대 결과**:
- 하드코딩 없이 현재 장비의 유효 LAN IP(`10.0.0.41` 또는 `192.168.0.x`)를 자동 감지하여 `http://<실IP>:8081/v1/chat/completions`로 POST 요청 전송
- `200 OK` 응답 및 LLM 텍스트 출력

---

### 시나리오 2: SERVER_HOST 환경변수 오버라이드 검증
```bash
SERVER_HOST="http://10.0.0.41" uv run python samples/sample_03_embedding.py
```
**기대 결과**:
- 지정한 환경변수 주소(`http://10.0.0.41:8090/v1/embeddings`)로 요청 전달
- `200 OK` 및 1024차원 임베딩 수신

---

### 시나리오 3: 듀얼 랜포트 및 회귀 테스트 수행
```bash
uv run pytest tests/unit/test_sample_scripts.py tests/unit/test_network_detector.py
```
**기대 결과**: 듀얼 랜포트 필터링 및 동적 호스트 헬스체크 테스트 100% Green Pass 통과

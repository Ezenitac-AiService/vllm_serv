# Quickstart Validation Guide: LLM 서버 통합 진단 (072-server-e2e-health-check)

## 1. 개요
LLM 서빙 모델 목록, API 엔드포인트 응답성, LAN IP 감지 및 방화벽 개방 포트 상태, 웹 대시보드 브라우저 E2E 검증을 통합 수행하는 가이드입니다.

---

## 2. 검증 실행 스크립트 명령어

### 통합 헬스체크 진단 스크립트 실행
```bash
uv run python scripts/diagnose_server_health.py
```
- **기대 결과**:
  - 서버의 활성 LAN IP 표시 (예: `10.0.0.15` 또는 `192.168.0.100`)
  - 현재 가동 중인 서빙 모델 목록 출력 (예: `qwen3.5-4b`)
  - `/v1/models`, `/v1/chat/completions`, `/health` 3종 엔드포인트 OK 상태 확인
  - 8081, 8082 포트 바인딩 및 방화벽 오픈 상태 확인
  - 대시보드 E2E 렌더링 검증 완료

---

### E2E 및 단위 테스트 수트 실행
```bash
uv run pytest tests/unit/test_server_health_diagnostics.py
```
- **기대 결과**: 통합 진단 테스트 수트 100% Pass 통과.

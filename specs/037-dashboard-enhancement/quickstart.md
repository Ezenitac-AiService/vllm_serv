# Quickstart Validation Guide: vLLM 서빙 대시보드 고도화 (037-dashboard-enhancement)

본 가이드는 고도화된 4대 탭 대시보드(모니터링, 모델 제어, LLM 플레이그라운드, 감사 로그 및 보안)의 정상 작동 여부를 빠르게 시연 및 검증하기 위한 절차입니다.

---

## 1. 사전 준비 및 서버 실행

```bash
# 가상환경 동기화 및 렌더링 검증 실행 준비
uv sync

# vLLM API 및 대시보드 서빙 전용 서버 구동 (기본 할당 IP 10.0.0.41:8000)
uv run python -m src.main
```

---

## 2. 웹 브라우저 대시보드 접속 및 탭 시연

1. **대시보드 접속**: 브라우저에서 `http://10.0.0.41:8000/dashboard/` 접속
2. **📊 Monitoring Tab 검증**:
   - Chart.js 시계열 캔버스 차트에 GPU 점유율(%) 및 VRAM 사용량(MB) 그래프가 실시간(1~3초 주기)으로 수신되어 업데이트되는지 확인.
   - VRAM 점유율 카드가 정상 표출되는지 확인.
3. **⚙️ Model Control Tab 검증 (동적 프로필 연동)**:
   - `/dashboard/api/capabilities` 호출 결과로 현재 타겟 플랫폼 프로필에 허용된 모델만 드롭다운에 출력되는지 확인.
   - 모델 변경 및 `n_ctx` 적용 버튼 시도 시 `Admin Secret` 비밀번호 입력 패널이 표시되는지 확인 (미인증 시 `401 Unauthorized` 차단).
4. **🎮 LLM Playground Tab 검증**:
   - System Prompt 입력 후 유저 질의("안녕하세요") 전송 시 텍스트 응답 스트리밍 출력 확인.
   - 응답 결과 카드 하단에 `TTFT (ms)`, `Total Latency (s)`, `tok/s` 지표가 실측 표출되는지 검증.
   - `Code Export` 버튼 클릭 시 cURL / Python OpenAI SDK 코드 생성 팝업 확인.
5. **🔑 Audit & Security Tab 검증**:
   - 접속 클라이언트 IP, 서브넷 차단 여부, HTTP 상태 코드 감사 목록이 실시간으로 갱신되는지 확인.

---

## 3. 자동화 테스트 코드 실행

```bash
# 대시보드 API, Admin Secret 보안 미들웨어, Playground 테스트 수트 통합 실행
uv run pytest tests/unit/test_dashboard_api.py -v
```

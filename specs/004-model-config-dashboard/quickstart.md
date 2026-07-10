# Quickstart Validation Guide

1. **서버 구동**: 
   ```bash
   # 프로젝트 루트에서
   export DASHBOARD_TOKEN="my-secret-token"
   PYTHONPATH=. python3 src/api/main.py
   ```
2. **대시보드 접속**: 웹 브라우저에서 `http://localhost:8000/dashboard` 접근. (헤더 또는 쿠키에 Token 세팅 테스트)
3. **프리셋 적용 테스트**:
   - UI에서 "실시간 채팅 (2B / 15K)" 프리셋 클릭 -> 적용.
   - 대시보드 상태가 `LOADING`으로 변경되며 VRAM 할당 현황이 실시간 SSE로 갱신됨.
   - `READY`로 완료 알림 확인.
4. **Graceful Degradation (503 에러) 확인**:
   - 대시보드에서 "수동 언로드" 클릭.
   - 모델 언로드 중 또는 완료 후 외부에서 API 호출:
     ```bash
     curl -I http://localhost:8000/v1/chat/completions
     ```
   - 즉각적으로 `503 Service Unavailable`이 응답되는지 확인.

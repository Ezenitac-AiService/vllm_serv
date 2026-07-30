# Phase 0 Research: vLLM 서빙 대시보드 고도화 (037-dashboard-enhancement)

## Technical Decisions & Rationale

### 1. 웹 프론트엔드 UI/UX 아키텍처 및 캔버스 차트 라이브러리
- **Decision**: Vanilla HTML5 + JavaScript (ES6 SPA 4대 탭) + Chart.js (v4.4) + Glassmorphism 다크 테마 CSS.
- **Rationale**:
  - 외부 노드패키지 빌드 도구(React/Vue/Vite) 없이 FastAPI `StaticFiles` 내에서 직접 초경량(1.5초 이내 로딩)으로 서빙 가능합니다.
  - Chart.js 캔버스 차트를 이용해 GPU/CPU 사용률 및 VRAM 시계열 그래프를 브라우저 CPU 점유율 5% 미만으로 실시간 시각화합니다.
- **Alternatives Considered**: React/Next.js (추가 빌드 스텝 및 용량 증가로 인해 백엔드 임베디드 대시보드용으로 거부됨).

### 2. 실시간 지표 스트리밍 프로토콜
- **Decision**: Server-Sent Events (SSE) `/dashboard/api/stream` 및 자동 재연결(Reconnection) 폴백.
- **Rationale**:
  - 단방향 브라우저 메트릭 푸시에 최적화되어 있으며 WebSocket 대비 서버 부하가 낮고 HTTP 하위 호환성이 우수합니다.
  - 연결 손실 시 "연결 재시도 중..." 경고 뱃지 활성화 후 자동 재연결을 수행합니다.

### 3. 관리자 보안 인증 정책 (Admin Secret Protection)
- **Decision**: 상태 변경 엔드포인트(`/dashboard/api/apply`, `/dashboard/api/unload`, `/dashboard/api/keys/*`) 대상 `x-admin-secret` 헤더/토큰 인증 필수화 및 미인증 시 HTTP `401 Unauthorized` 차단.
- **Rationale**:
  - 누구나 실시간 자원 상태는 읽기 전용(Read-Only)으로 모니터링할 수 있도록 제공하되, 서빙 모델 변경 및 API 키 생성/삭제 등의 관리자 작업은 철저히 보호합니다.

### 4. 인터랙티브 LLM 플레이그라운드 & 실측 지표 측정
- **Decision**: `fetch` ReadableStream 기반 토큰 스트리밍 수신 + 첫 토큰 수신 시점 TTFT(ms) 계산 + 생성 완료 시점 Total Latency(s) 및 Token Speed(tok/s) 실측 지표 표시 + cURL/Python Code Export 모달.
- **Rationale**:
  - OpenAI Playground, Google AI Studio, LM Studio 표준 UI/UX를 충실히 반영하여 모델 변경 직후 즉각적인 품질 및 성능 실측 검증을 제공합니다.

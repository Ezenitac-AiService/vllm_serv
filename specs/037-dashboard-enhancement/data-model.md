# Data Model: vLLM 서빙 대시보드 고도화 (037-dashboard-enhancement)

## Core Entities & Schemas

### 1. `DashboardMetrics` (실시간 자원 및 성능 지표 객체)

| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| `timestamp` | `float` | 지표 수집 시각 (Unix Timestamp) | `1722345600.12` |
| `gpu_utilization` | `float` | GPU 계산 점유율 (%) | `45.2` |
| `vram_used_mb` | `float` | 현재 VRAM 사용량 (MB) | `3950.0` |
| `vram_total_mb` | `float` | 전체 가용 VRAM (MB) | `8192.0` |
| `vram_percent` | `float` | VRAM 점유 비율 (%) | `48.2` |
| `vram_warning` | `bool` | VRAM 90% 이상 도달 위험 뱃지 활성화 여부 | `false` |
| `current_model` | `str` | 현재 VRAM 상주 서빙 모델 ID | `"qwen3.5-4b"` |
| `current_n_ctx` | `int` | 활성화된 컨텍스트 윈도우 크기 | `8192` |
| `ttft_ms` | `float` | 최근 평균 첫 토큰 지연 시간 (ms) | `142.0` |
| `tpot_tok_s` | `float` | 최근 평균 토큰 생성 속도 (tok/s) | `36.2` |

---

### 2. `ClientAccessAuditLog` (클라이언트 접속 및 감사 이력 객체)

| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| `log_id` | `str` | 감사 로그 고유 식별자 | `"log-20260730-001"` |
| `timestamp` | `str` | 접속 시각 (ISO8601) | `"2026-07-30T12:45:00Z"` |
| `client_ip` | `str` | 클라이언트 IP 주소 | `"10.0.0.41"` |
| `subnet_allowed` | `bool` | 서브넷 허용 정책 인가 여부 | `true` |
| `endpoint` | `str` | 호출한 API 엔드포인트 | `"/v1/chat/completions"` |
| `status_code` | `int` | HTTP 응답 상태 코드 | `200` |
| `process_time_ms` | `float` | 요청 처리 지연시간 (ms) | `185.4` |

---

### 3. `PlaygroundTestRequest` (LLM 플레이그라운드 테스트 요청 객체)

| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| `model` | `str` | 타겟 서빙 모델 ID | `"qwen3.5-4b"` |
| `system_prompt` | `str` | 시스템 지시어 (System Instruction) | `"You are a helpful AI assistant."` |
| `prompt` | `str` | 테스트 유저 질의문 | `"안녕하세요! 오늘 날씨 알려주세요."` |
| `temperature` | `float` | 창의성/결정론 조절 파라미터 (0.0~2.0) | `0.7` |
| `top_p` | `float` | 누적 확률 필터링 (0.0~1.0) | `0.9` |
| `max_tokens` | `int` | 최대 생성 토큰 수 제한 | `512` |

---

### 4. `PlaygroundTestResult` (LLM 플레이그라운드 테스트 결과 실측 객체)

| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| `text` | `str` | 최종 누적 응답 텍스트 | `"안녕하세요! 오늘 날씨는..."` |
| `ttft_ms` | `float` | 첫 토큰 수신 시간 실측값 (ms) | `135.2` |
| `total_latency_s` | `float` | 총 생성 완료 소요 시간 (초) | `1.42` |
| `token_speed_tok_s` | `float` | 초당 토큰 생성 속도 (tok/s) | `38.5` |
| `prompt_tokens` | `int` | 프롬프트 토큰 수 | `24` |
| `completion_tokens` | `int` | 생성 완료된 토큰 수 | `55` |
| `finish_reason` | `str` | 생성 종료 원인 | `"stop"` |

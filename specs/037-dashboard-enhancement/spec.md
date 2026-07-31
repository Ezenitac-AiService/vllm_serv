# Feature Specification: vLLM 서빙 대시보드 고도화 (vLLM Dashboard Enhancement)

**Feature Branch**: `037-dashboard-enhancement`

**Created**: 2026-07-30

**Status**: Draft

**Input**: User description: "대시보드 고도화"

## Clarifications

### Session 2026-07-30

- Q: 실시간 차트 및 웹 UI 디자인 시스템 기술 선정 → A: Chart.js 시계열 캔버스 차트와 Vanilla CSS Glassmorphism 다크 테마 디자인 시스템을 연동하여 1.5초 이내 로딩과 1초 단위 실시간 시계열 차트(GPU/VRAM, TTFT, TPOT)를 표출함.
- Q: 대시보드 내 모델 목록 하드코딩 여부 및 타겟 플랫폼 프로필 반영 방식 → A: 대시보드 UI는 모델 목록을 HTML/JS에 하드코딩하지 않고, 실제 서버 구동 시 타겟 플랫폼 프로필(예: GTX 1070 8GB VRAM 초과 모델 제외)에 맞춰 동작하는 서버 API(`/dashboard/api/capabilities`)로부터 지원 모델 목록을 동적으로 조회하여 드롭다운 및 프리셋을 자동 생성함.
- Q: 대시보드 관리자 인증 및 보안 보호 범위 → A: 대시보드 실시간 메트릭 모니터링 상태 조회(Read-Only)는 누구나 접속하여 조회할 수 있으나, 모델 서빙 전환, 언로드, 컨텍스트 스케일링 설정 및 API Key 관리 등 모든 시스템 상태 변경 API 요청(`/dashboard/api/apply`, `/dashboard/api/unload`, `/dashboard/api/keys`)은 Admin Secret 인증(`x-admin-secret` 헤더 또는 인증 토큰)을 필수 요구하며, 미인증 시 `401 Unauthorized` 오류로 안전하게 차단함.
- Q: 대시보드 내 실시간 프롬프트 스트리밍 테스트 Playground 탑재 여부 → A: 대시보드 내에 현재 상주 중인 서빙 모델에 즉시 프롬프트를 전송하고 응답 텍스트를 실시간 스트리밍으로 수신하며, 첫 토큰 응답 시간(TTFT ms), 총 소요 시간(Latency s), 토큰 생성 속도(tok/s)를 즉시 실측·표출하는 '인터랙티브 Playground' 패널을 추가함.
- Q: 2026년 주요 AI 플랫폼(OpenAI, Google AI Studio, LM Studio, Ollama) 벤치마킹 기반 UI/UX 스펙 확정 → A: 대시보드를 4대 탭(📊 메트릭 모니터링, ⚙️ 모델 및 파라미터 제어, 🎮 벤치마크 플레이그라운드, 🔑 API Key & 서브넷 감사 로그) SPA 구조로 리팩토링하고, 플레이그라운드 내 System Prompt, Temperature, Top_P 조절 슬라이더, 토큰 카운터, cURL / Python 코드 생성기 기능을 탑재함.






## User Scenarios & Testing *(mandatory)*

### User Story 1 - 실시간 GPU/VRAM 및 서빙 메트릭 시각화 (Priority: P1)

시스템 운영자 및 개발자는 웹 대시보드를 통해 현재 서버의 GPU 점유율, VRAM 사용량, 서버 응답 지연시간(TTFT, TPOT)을 실시간 차트 및 상태 카드로 한눈에 모니터링할 수 있어야 합니다.

**Why this priority**: vLLM 모델 서빙 중 GPU/VRAM 자원 고갈이나 성능 저하 현상을 즉각 인지하고 제어하기 위해 가장 중요합니다.

**Independent Test**: 대시보드 메인 화면(`http://localhost:8000/dashboard` 또는 할당 IP) 접속 시 GPU 사용률, VRAM 점유 그래프가 주기적(예: 1~3초 간격)으로 실시간 갱신되는지 확인합니다.

**Acceptance Scenarios**:

1. **Given** vLLM 서버가 구동 중인 상태에서, **When** 사용자가 대시보드 모니터링 페이지에 접속하면, **Then** GPU 모델명, Total VRAM 대비 사용 중인 VRAM(MB/% 단위), 추론 지연시간(TTFT/TPOT) 메트릭이 실시간 그래프로 표출됩니다.
2. **Given** VRAM 사용량이 위험 임계치(예: 90% 이상)에 도달할 때, **When** 상태를 조회하면, **Then** 대시보드 상단 경고 뱃지 및 시각적 경고 스타일이 즉시 활성화됩니다.

---

### User Story 2 - 모델 전환 및 컨텍스트 스케일링 동적 제어 패널 (Priority: P2)

운영자는 서버 재시작 없이 대시보드 인터페이스 상에서 상주 서빙 모델(`qwen3.5-4b`, `gemma4-e4b` 등 카탈로그 모델)을 선택하여 즉시 전환하고, 컨텍스트 스케일링(2K ~ 32K) 및 스펙 바인딩 정책을 조율할 수 있어야 합니다.

**Why this priority**: 다양한 모델 및 실험 파라미터를 CLI 명령어 입력 없이 웹 GUI 상에서 손쉽게 전환하여 작업 생산성을 극대화합니다.

**Independent Test**: 대시보드의 "모델 관리" 드롭다운에서 타겟 모델 선택 후 "서빙 전환" 버튼 클릭 시, 이전 모델이 안전하게 오프로드되고 신규 모델로 VRAM 상주 서빙이 전환되는지 검증합니다.

**Acceptance Scenarios**:

1. **Given** 현재 `qwen3.5-4b`가 서빙 중인 환경에서, **When** 운영자가 `gemma4-e2b`를 선택하고 전환을 요청하면, **Then** 기존 모델 VRAM 해제 후 신규 모델 서빙 전환 상태가 성공 메시지와 함께 대시보드에 업데이트됩니다.
2. **Given** 모델의 최대 컨텍스트 범위를 초과하는 스케일링 설정 시, **When** 적용을 시도하면, **Then** 유효성 검증 에러 및 안전한 최대 상한 가이드가 화면에 표시됩니다.

---

### User Story 3 - 클라이언트 접속 로그 및 서브넷 접근 감사 제어 (Priority: P3)

보안 담당자 및 운영자는 대시보드를 통해 최근 접속한 클라이언트 IP 타임라인, 서브넷 허용 정책(`10.0.0.0/8`, `192.168.0.0/16` 등), 그리고 API 요청 성공/실패 헬스체크 이력을 조회할 수 있어야 합니다.

**Why this priority**: 허가되지 않은 네트워크 대역 접속 시도를 감지하고, 서비스 상태 정합성을 감사하기 위해 필요합니다.

**Independent Test**: 대시보드 "접속 로그 & 감사" 탭에서 최근 100건의 API 호출 클라이언트 IP, HTTP 상태 코드 및 서브넷 차단 여부가 타임라인 테이블로 표시되는지 확인합니다.

**Acceptance Scenarios**:

1. **Given** 외부 클라이언트가 API를 호출했을 때, **When** 대시보드의 감사 로그 탭을 조회하면, **Then** 클라이언트 IP, 요청 포맷, 서브넷 허용 여부, 응답 시간이 실시간 목록으로 갱신됩니다.

---

### User Story 4 - 인터랙티브 LLM 플레이그라운드 & 실시간 성능 실측 (Priority: P2)

운영자는 대시보드 상에서 모델 서빙 전환 및 컨텍스트 설정을 조율한 직후, 대시보드 내 "Playground" 패널에서 프롬프트를 입력하여 생성 텍스트의 실시간 스트리밍 출력과 **첫 토큰 지연 시간(TTFT ms)**, **총 소요 시간(Total Latency s)**, **토큰 생성 속도(tok/s)** 지표를 실측 및 확인할 수 있어야 합니다.

**Why this priority**: CLI 호출 없이 대시보드 내부에서 즉각적으로 서빙 모델의 추론 품질과 속도 성능 지표를 검증할 수 있습니다.

**Independent Test**: 대시보드 Playground 탭에서 테스트 질문 입력 후 "전송" 버튼 클릭 시, 텍스트 응답이 스트리밍으로 출력됨과 동시에 TTFT(ms) 및 tok/s 측정값이 결과 카드에 실시간 표시되는지 확인합니다.

**Acceptance Scenarios**:

1. **Given** 현재 특정 모델(예: `qwen3.5-4b`)이 서빙 중인 상태에서, **When** 사용자가 Playground 창에 프롬프트를 입력하고 제출하면, **Then** 텍스트 응답이 즉시 실시간으로 스트리밍 표출되고 첫 토큰 수신 시점의 TTFT(ms)와 생성 속도(tok/s)가 화면에 기록됩니다.

---


### Edge Cases

- GPU NVML 라이브러리를 사용할 수 없거나 CPU 전용 환경인 경우: GPU 차트 대신 CPU/RAM 사용량 모니터링 모드로 자동 전환되고 안내 메세지("[시스템] GPU NVML 미감지: CPU 모드로 동작 중")를 표시해야 합니다.
- 대시보드 웹소켓/SSE 실시간 연결이 끊긴 경우: 자동 재연결(Reconnection) 시도 및 화면 상단 "연결 재시도 중..." 뱃지를 표출하여 UI가 멈추지 않아야 합니다.

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: 실시간 GPU/VRAM 및 서빙 지표 시각화 대시보드 UI 구현 완료
- **DoD-002**: 웹 UI 상에서 카탈로그 모델 동적 전환 및 컨텍스트 스케일링 제어 기능 작동
- **DoD-003**: 클라이언트 접근 로그 및 서브넷 필터 감사 뷰 제공
- **DoD-004**: 단위 및 통합 테스트 코드 작성 및 100% 통과
- **DoD-005**: 대시보드 내 LLM Playground 패널 탑재 및 실시간 스트리밍 응답, TTFT(ms), tok/s 성능 실측 기능 작동 검증 완료

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 대시보드는 GPU/CPU 점유율, Peak VRAM, TTFT(First Token Latency), TPOT(Token Generation Speed)을 주기적(1~3초)으로 수집하여 실시간 동적 차트로 시각화해야 한다.
- **FR-002**: 대시보드는 모델 목록을 클라이언트에 하드코딩하지 않고, 타겟 플랫폼 프로필에 따라 실제 동작 중인 서버 API(`/dashboard/api/capabilities`)로부터 지원 가능한 모델 목록을 동적으로 받아와 드롭다운 및 프리셋 버튼을 생성하고 동적 서빙 전환 제어를 수행해야 한다.
- **FR-003**: 대시보드는 VRAM 90% 이상 도달 시 시각적 경고 뱃지 및 임계치 경고 팝업/스타일을 활성화해야 한다.
- **FR-004**: 대시보드는 최근 클라이언트 접근 IP, 요청 성공률, 서브넷 인가 여부를 확인할 수 있는 감사 로그 웹 인터페이스를 제공해야 한다.
- **FR-005**: 모바일 및 다양한 화면 해상도에 대응하는 반응형 다크 모드 웹 디자인 시스템을 준수해야 한다.
- **FR-006**: 모델 서빙 전환, 언로드, 컨텍스트 설정 변경 및 API Key 관리 등의 제어 엔드포인트(`/dashboard/api/apply`, `/dashboard/api/unload`, `/dashboard/api/keys/*`)는 Admin Secret 인증 검증을 필수 수행하며, 미인증 접근 시 HTTP `401 Unauthorized`를 반환해야 한다.
- **FR-007**: 대시보드는 현재 서빙 중인 모델을 대상으로 실시간 프롬프트 테스트 및 응답 스트리밍(SSE/Chunked)을 수행하고, TTFT(ms), Total Latency(s), Token Generation Speed(tok/s) 실측 지표를 시각적으로 출력하는 **LLM Playground** 뷰 패널을 제공해야 한다.
- **FR-008**: Playground 패널은 System Prompt 입력 설정, Temperature(0.0~2.0) 및 Top_P(0.0~1.0) 하이퍼파라미터 조절 슬라이더, 프롬프트 및 컴플리션 토큰 카운터 수치를 실시간으로 표시해야 한다.
- **FR-009**: Playground 패널은 생성 응답 결과 카드에 TTFT(ms), Latency(s), tok/s, Finish Reason(`stop`, `length`) 메트릭 뱃지를 제공하고, 동일 요청을 재현할 수 있는 cURL 명령어 및 Python OpenAI SDK 생성 코드를 내보내기(Code Export) 기능을 제공해야 한다.
- **FR-010**: 대시보드 UI/UX는 4대 핵심 탭(📊 모니터링, ⚙️ 모델 제어, 🎮 플레이그라운드, 🔑 감사 로그 및 API 키)을 갖춘 Glassmorphism 다크 테마 기반 단일 페이지 애플리케이션(SPA)으로 디자인을 완성해야 한다.




### Key Entities

- **DashboardMetrics**: GPU/VRAM 사용량, 응답 속도, 활성 서빙 모델 상태 정보를 담은 동적 지표 객체
- **ClientAccessAuditLog**: 클라이언트 IP, 서브넷 판정 결과, API 엔드포인트, HTTP 상태 코드 타임라인 객체

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 대시보드 웹 페이지 초기 로딩 시간 1.5초 이내 완수 및 100% 반응형 레이아웃 제공
- **SC-002**: 실시간 메트릭 스트리밍/폴링 간 브라우저 CPU 점유율 5% 이하 유지
- **SC-003**: 웹 대시보드를 통한 모델 전환 요청 시 3초 이내에 오프로드 및 전환 시퀀스 실행

## Assumptions

- vLLM 백엔드 API 서비스(`http://10.0.0.41:8000`)에 대시보드 전용 REST / SSE 메트릭 엔드포인트가 제공되거나 연동됩니다.
- 모니터링 시스템은 NVML(NVIDIA Management Library) 및 `psutil` 기반으로 호스트 자원을 수집합니다.

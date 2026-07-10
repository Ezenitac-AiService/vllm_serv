# Feature Specification: 모델 설정 웹 대시보드 (Model Config Dashboard)

**Feature Branch**: `004-model-config-dashboard`

**Created**: 2026-07-10

**Status**: Draft

**Input**: User description: "/home/dev/vllm_serv/analysis_report.md 문서의 기준점들의 단축 설정 버튼과 상세 설정 창을 제공하는 서버 웹 대시보드"

## Clarifications
### Session 2026-07-10
- Q: 수동 로드/언로드 기능 필요성 여부 (사용자 추가 요청) → A: 서버에서 서빙하는 모델의 명시적인 로드/언로드 버튼 제공
- Q: 대시보드 접근 보안 (Security) → A: 기본적으로 로컬(Localhost) 환경에서만 접속하되, CSRF 등 최소한의 보안 취약점을 방어하기 위해 단순 API Token 적용으로 고도화 (비판론자 리뷰 결과 반영)
- Q: 설정 영속성 (Persistence) → A: 설정 파일(JSON 등)에 저장하여 서버 재시작 시 마지막 상태 복구
- Q: 다중 접속 동기화 및 상태 표시 (State Sync) → A: 비효율적인 Polling 방식을 버리고, FastAPI의 SSE(Server-Sent Events)를 활용한 실시간 이벤트 스트림으로 고도화 (비판론자 리뷰 결과 반영)

## Critic Review & Architecture Enhancements (2026-07-10)
비판적 심층 분석(다중 페르소나) 결과, 기존 스펙의 모순 및 약점을 다음과 같이 고도화함:
1. **상태 동기화 비효율성 제거**: 60초가 걸리는 로딩 작업에 대해 3초마다 Polling하는 것은 서버 자원 낭비 및 다중 클라이언트 환경에서 경합을 유발함. **개선방안**: `Server-Sent Events(SSE)`를 도입하여 서버가 상태 변화 시 클라이언트에 즉시 푸시하도록 명확화.
2. **동적 제약사항(Dynamic Limits) 적용**: 프론트엔드 UI에 "12B 모델은 10K 이상 시 OOM" 이라는 하드코딩된 로직은 하드웨어 변경 시 시스템을 망가뜨림. **개선방안**: 백엔드가 하드웨어 스펙에 따른 동적 한계치(`Capabilities API`)를 제공하도록 변경.
3. **무중단/유예 처리 부재(Graceful Degradation)**: 모델 언로드나 리로드 중 사용자(추론 요청 API)가 접근 시의 처리가 누락됨. **개선방안**: 로딩/언로드 중에는 API가 `503 Service Unavailable` 상태와 `Retry-After` 헤더를 반환하는 Maintenance Mode 도입 규정.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 벤치마크 기반 빠른 프리셋 적용 (Priority: P1)

관리자는 서버의 목적(예: 챗봇, RAG 등)이 바뀔 때마다 복잡한 설정 없이 벤치마크 분석 결과를 바탕으로 최적화된 모델 환경을 원클릭으로 세팅하고 싶어 합니다. 

**Why this priority**: 이 기능은 대시보드의 핵심 가치인 '손쉬운 최적화'를 달성하게 해 주며, 가장 빈번하게 사용될 주요 기능입니다.

**Independent Test**: 단축 설정 버튼 클릭 시 백엔드 설정값(모델명, n_ctx)이 의도한 프리셋의 값으로 정확히 변경되는지 독립적으로 테스트할 수 있습니다.

**Acceptance Scenarios**:

1. **Given** 대시보드가 열려있을 때, **When** 사용자가 "실시간 인터랙션 응답" 프리셋 버튼을 클릭하면, **Then** 시스템은 `gemma4-2b` 모델과 `15K` 컨텍스트 윈도우를 선택 상태로 업데이트한다.
2. **Given** 대시보드가 열려있을 때, **When** 사용자가 "대용량 문서 요약 및 RAG" 프리셋 버튼을 클릭하면, **Then** 시스템은 `gemma4-4b` 모델과 `34K` 컨텍스트 윈도우(또는 2B 모델과 40K)를 선택 상태로 업데이트한다.

---

### User Story 2 - 상세 설정 조정 창 (Priority: P2)

관리자는 프리셋을 기반으로 하되, 시스템 자원이나 특별한 요구사항에 맞춰 컨텍스트 길이나 다른 생성 파라미터(Temperature 등)를 미세 조정(Fine-tuning)하고 싶어 합니다.

**Why this priority**: 프리셋만으로는 모든 요구사항을 충족할 수 없으므로, 커스텀 설정을 지원하여 유연성을 확보해야 합니다.

**Independent Test**: 상세 설정 창에 입력된 값들이 최종 적용(Apply) 객체에 올바르게 바인딩되는지 테스트할 수 있습니다.

**Acceptance Scenarios**:

1. **Given** 상세 설정 창이 열려있을 때, **When** 사용자가 컨텍스트 길이를 15000에서 12000으로 슬라이더(또는 입력칸)를 통해 조절하면, **Then** 해당 값이 설정 상태에 반영된다.
2. **Given** 특정 모델(예: 12B)이 선택된 상태에서, **When** 사용자가 분석 보고서 한계치(10K)를 초과하는 값을 입력하려 하면, **Then** UI는 OOM 위험 경고를 시각적으로 표시한다.

---

### User Story 3 - 서버 모델 실시간 리로드 적용 (Priority: P1)

관리자가 설정을 마친 후 "적용" 버튼을 누르면, 백엔드 서버는 재시작 없이 메모리에 올라간 모델을 즉각적으로 언로드/리로드하여 새로운 설정 환경으로 전환되어야 합니다.

**Why this priority**: 설정한 값이 실제로 운영 중인 백엔드 서비스에 반영되지 않으면 대시보드의 의미가 없습니다.

**Independent Test**: API 호출을 통해 LlamaManager가 기존 모델을 내리고 새 파라미터로 모델을 올리는 과정을 모의(Mock) 호출 없이 통합 테스트로 검증할 수 있습니다.

**Acceptance Scenarios**:

1. **Given** 사용자가 새로운 프리셋을 선택한 후, **When** "적용(Apply)" 버튼을 클릭하면, **Then** 대시보드는 로딩 상태를 표시하고 서버는 모델 스왑을 시작한다.
2. **Given** 서버가 모델 리로드를 완료하면, **When** 로딩 상태가 해제되면, **Then** 사용자에게 성공적으로 적용되었음을 알리는 피드백이 표시된다.

### User Story 4 - 수동 모델 제어 및 503 방어 (Priority: P2)

관리자는 필요에 따라 현재 메모리에 올라가 있는 모델을 완전히 언로드하여 VRAM을 비우거나, 저장된 설정값으로 다시 로드하고 싶어 합니다. 또한 이 과정에서 일반 사용자의 API 요청이 무한 대기(Timeout)에 빠지는 것을 방지해야 합니다.

**Why this priority**: VRAM 자원 관리를 위해 수동 제어권이 필수적이며, 모델 전환 중의 서비스 안정성(안전한 실패)을 보장해야 하기 때문입니다.

**Independent Test**: 언로드 버튼 클릭 후 서버의 VRAM이 해제되는지 확인하고, 해당 시점에 추론 API 호출 시 503 에러가 즉각 반환되는지 확인.

**Acceptance Scenarios**:

1. **Given** 모델이 로드되어 있을 때, **When** 사용자가 "언로드" 버튼을 클릭하면, **Then** 백엔드는 메모리에서 모델을 내리고 SSE를 통해 "언로드됨" 이벤트를 발행한다.
2. **Given** 모델이 언로드된 상태(또는 로딩 중)일 때, **When** 외부 클라이언트가 `/v1/chat/completions` API를 호출하면, **Then** 시스템은 대기하지 않고 즉시 `503 Service Unavailable`과 `Retry-After` 헤더를 반환한다.

---

### Edge Cases

- 사용자가 여러 번 연속으로 "적용" 버튼을 클릭할 경우 서버는 어떻게 처리하는가? (중복 요청 방지 및 기존 서브프로세스 킬)
- 모델 리로드 중 서버 메모리 부족(OOM)이나 예기치 않은 에러가 발생하여 `llama-server` 하위 프로세스가 크래시될 경우, 부모 프로세스인 대시보드(FastAPI)는 생존하여 프론트엔드에 어떻게 에러 상태(RESTARTING/ERROR)를 보여줄 것인가?

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: 벤치마크 결과에 기반한 3가지 프리셋(RAG, 고품질 추론, 실시간 채팅) 버튼이 대시보드 UI에 구현되어야 한다.
- **DoD-002**: 상세 설정 창에서 모델 선택, Context Length 조절 기능이 작동하는지 확인하는 단위 테스트가 통과해야 한다.
- **DoD-003**: UI에서 설정을 적용했을 때, 백엔드(`LlamaManager`)가 성공적으로 모델을 교체(리로드)하고 완료 응답을 반환하는지에 대한 API 통합 테스트가 통과해야 한다.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 시스템은 사용자가 브라우저를 통해 접근 가능한 웹 기반 대시보드를 제공해야 한다.
- **FR-002**: 시스템은 `analysis_report.md`에 정의된 3개의 권장 설정 프리셋을 원클릭 버튼 형태로 제공해야 한다.
  - 프리셋 A (RAG): `gemma4-4b` / 34K Context (또는 `gemma4-2b` / 40K Context)
  - 프리셋 B (고품질 추론): `gemma4-12b` / 8K Context
  - 프리셋 C (실시간 챗): `gemma4-2b` / 15K Context
- **FR-003**: 시스템은 사용자가 모델명(2b, 4b, 12b)과 컨텍스트 제한(n_ctx)을 수동으로 조절할 수 있는 상세 설정 컨트롤을 제공해야 한다.
- **FR-004**: 백엔드 시스템은 현재 하드웨어 VRAM 기반의 한계치(Capabilities) 정보를 제공하는 API를 노출해야 하며, 대시보드는 이를 기반으로 동적 OOM 경고를 노출해야 한다 (프론트엔드 하드코딩 금지).
- **FR-005**: 시스템은 UI에서 전달된 설정을 바탕으로 백엔드의 모델 인스턴스를 동적으로 리로드하는 API 엔드포인트를 제공해야 한다.
- **FR-006**: 시스템은 현재 서빙 중인 모델을 수동으로 로드/언로드(메모리 해제) 할 수 있는 명시적인 버튼을 제공해야 한다.
- **FR-007**: 대시보드는 로컬(localhost) 접속을 전제로 하되, CSRF 공격 방어 및 최소한의 인가 검증을 위해 단일 API Token(환경변수 기반) 체계를 적용해야 한다.
- **FR-008**: 적용된 모델 환경 설정(프리셋/상세값 등)은 JSON 등의 파일로 저장되어 서버 데몬 재시작 시 마지막 상태로 자동 복구 및 로드되어야 한다.
- **FR-009**: 대시보드는 Polling 방식이 아닌, FastAPI `EventSourceResponse` 기반의 Server-Sent Events(SSE) 스트림을 구독하여 모델 로딩 상태 및 VRAM 현황을 실시간 이벤트 기반으로 갱신해야 한다.
- **FR-010**: 모델이 로딩 중이거나 언로드된 "Maintenance Mode" 상태일 때, 시스템으로 들어오는 모든 추론 API 요청(`/v1/...`)은 무한 대기하지 않고 즉각 `503 Service Unavailable` 상태 코드와 `Retry-After` 헤더를 반환하도록 설계(Graceful Degradation)되어야 한다.

### Key Entities

- **PresetConfiguration**: 프리셋 이름, 설명, 할당된 모델 ID, 컨텍스트 길이 값을 포함하는 데이터 구조
- **ServerStatus**: 현재 로드된 모델 ID, 적용된 컨텍스트 길이, VRAM 사용 현황 등 현재 서버의 상태를 나타내는 데이터

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 사용자는 2번의 마우스 클릭 이내에 권장 벤치마크 환경으로 서버 설정을 전환할 수 있다.
- **SC-002**: 대시보드를 통한 모델 전환 요청 중 99% 이상이 크래시 없이 성공적으로 적용된다.
- **SC-003**: 상세 설정 폼은 사용자의 입력 시 백엔드가 제공한 Limits 정보를 바탕으로 지연 시간 없이(100ms 이내) OOM 경고 등 유효성 검사 결과를 시각적으로 반영한다.

## Assumptions

- 모델 파일(.gguf)은 기존 방식대로 서버 디스크(models/ 디렉토리)에 정상적으로 다운로드 되어 존재한다고 가정한다.
- 웹 프론트엔드는 기존 FastAPI 프로젝트에 통합되어 정적 파일(Static Files)로 서빙되며, SSE 및 단일 Token 인증 처리를 지원한다.

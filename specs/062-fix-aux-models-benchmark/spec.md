# Feature Specification: 보조 모델(임베딩/리랭킹) 구동 및 품질 벤치마크 평가 개선

**Feature Branch**: `062-fix-aux-models-benchmark`

**Created**: 2026-07-31

**Status**: Draft

**Input**: User description: "서비스 플렛폼에서, 수동 빌드 후 서버 셋팅했어, 다만, 임베딩 모델과 리랭킹 모델, 테스트 내용을 개선해야 할거 같아"

## Clarifications

### Session 2026-07-31

- Q1: 벤치마크 종료 후 메인 서버 복원 및 상주 메커니즘 → A: 벤치마크 종료 후 기본 서비스 모델 그룹(LLM: `qwen3.5-4b`, 임베딩: `bge-m3`, 리랭킹: `bge-reranker-v2-m3`)이 다중 모델 동시 상주(Co-loading) 백그라운드 데몬 프로세스로 완벽히 원복 복원되어 스크립트 종료 후에도 `./status_server.sh`에서 RUNNING 상태를 유지해야 함.
- Q2: 대시보드 백엔드 엔진(포트 8089) 미준비 시 타임아웃 처리 메커니즘 → A: 메인 API 서버 프록시 레이어에 연결 프리플라이트 가드를 적용하여 백엔드 미준비 시 무한 타임아웃 대신 `503 Service Unavailable` 및 상태 안내 메시지를 즉시 응답하고 대시보드 UI에 준비 중 상태를 전달함.
- Q3: 대시보드 클라이언트 API 호출 경로 (IP/호스트 바인딩) 및 타임아웃 해결 → A: 대시보드 웹 UI 프론트엔드 API 호출 주소를 `window.location.origin` 기반 동적 상대 경로(`/dashboard/api/*`, `/v1/*`)로 전면 일괄 전환하여 외부 접속 및 멀티 플랫폼 IP 접속 환경에서 타임아웃 호환성 100% 보장.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 임베딩 모델(BGE M3) 정상 추론 및 서빙 지원 (Priority: P1)

서비스 플랫폼 관리자 및 API 사용자는 BGE M3 임베딩 모델을 로드하여 벡터 임베딩 생성 API 요청 시 오류 없이 정상적인 추론 결과(임베딩 벡터)를 반환받을 수 있어야 합니다.

**Why this priority**: 임베딩 모델(bge-m3)은 RAG 및 벡터 검색 서비스의 필수 기반 요소이며, 벤치마크 단계에서 실측 추론 실패 오류가 발생하므로 가장 시급하게 해결되어야 합니다.

**Independent Test**: `scripts/benchmark_quality.py --real` 또는 독립된 API 테스트를 통해 bge-m3 모델을 로드하고 HTTP 임베딩 요청을 보냈을 때 200 OK와 올바른 차원의 벡터 값을 반환하는지 확인하여 독립 테스트할 수 있습니다.

**Acceptance Scenarios**:

1. **Given** bge-m3 임베딩 모델이 catalog에 등록되어 있을 때, **When** 서버 프로세스가 bge-m3 모델을 `--embedding` 플래그와 함께 로드하고 추론을 요청하면, **Then** 헬스체크가 성공하고 벡터 추론 결과가 정상 응답되어야 합니다.
2. **Given** 벤치마크 스크립트 실행 시, **When** bge-m3 단계에 진입하면, **Then** `⚠️ 실측 추론 실패` 없이 성공적인 TPOT/TTFT 또는 임베딩 생성 속도가 측정되어야 합니다.

---

### User Story 2 - 리랭킹 모델(BGE Reranker v2 M3) 헬스체크 및 교스엔코더 서빙 정상화 (Priority: P2)

서비스 플랫폼 관리자는 BGE Reranker v2 M3 Cross-Encoder 모델을 로드하여 문맥 재정렬 API를 실행할 때, 타임아웃 없이 빠른 시간 내 서빙 헬스체크를 통과하고 서빙을 개설할 수 있어야 합니다.

**Why this priority**: 리랭크 모델(bge-reranker-v2-m3)은 검색 결과의 정밀도를 향상시키는 핵심 보조 모델이나, 현재 Step 3 헬스체크 타임아웃으로 인해 프로세스가 정상 작동하지 않으므로 수정이 필요합니다.

**Independent Test**: `bge-reranker-v2-m3` 모델 프로세스를 스폰하고 지정된 시간 내 `/v1/models` 또는 `/health` 엔드포인트 응답이 정상적으로 수신되는지 독립 테스트할 수 있습니다.

**Acceptance Scenarios**:

1. **Given** bge-reranker-v2-m3 모델 서버 스폰 요청 시, **When** 프로세스가 적절한 백엔드 인자(n_ctx, embedding/rerank 모드 설정 등)로 구동되면, **Then** 타임아웃 없이 헬스체크를 10초 이내 통과하고 서빙 READY 상태가 되어야 합니다.
2. **Given** 리랭킹 모델 서빙이 READY 상태일 때, **When** 벤치마크 스크립트가 평가 단계를 수행하면, **Then** 헬스체크 타임아웃 없이 추론 검증이 완료되어야 합니다.

---

### User Story 3 - 품질 벤치마크 테스트 스크립트 감지 및 다중 모델 복원 개선 (Priority: P3)

서비스 개발자는 `scripts/benchmark_quality.py` 스크립트를 통해 LLM, 임베딩, 리랭킹 전체 8개 모델 Catalog에 대한 자동 다운로드, GPU 가속 실측, 컨텍스트 스케일링 평가를 오류 없이 일괄 완료하고 종합 리포트를 생성할 수 있어야 합니다.

**Why this priority**: 벤치마크 스크립트의 보조 모델 호환성 및 에러 처리 로직을 개선함으로써 수동 빌드/설치 후 전체 플랫폼 검증을 자동화하고, 스크립트 종료 후에도 기본 서비스 다중 모델 그룹을 백그라운드로 안전 복원합니다.

**Independent Test**: `uv run python scripts/benchmark_quality.py --real` 실행 시 8개 전체 모델에 대한 서빙 및 평가 결과가 정상 기록되는지 검증하고, 스크립트 종료 후 `./status_server.sh`를 실행하여 서비스 상주 상태를 확인할 수 있습니다.

**Acceptance Scenarios**:

1. **Given** 8개 Catalog 모델이 포함된 실측 벤치마크 실행 시, **When** 모든 모델 평가가 순차 완료되면, **Then** 실패 모델 없이 `data/reports/analysis_report_quality.md`에 실측 성과 지표가 정확히 생성되어야 합니다.
2. **Given** VRAM 상주 서빙 원상 복원 단계 실행 시, **When** 벤치마크가 종료되면, **Then** 기본 서비스 모델 그룹(LLM: `qwen3.5-4b`, 임베딩: `bge-m3`, 리랭킹: `bge-reranker-v2-m3`)이 백그라운드 데몬 프로세스로 동시 로딩(Co-loading)되어 성공적으로 복원 상주하고 있어야 합니다.
3. **Given** 백엔드 LLM 엔진이 로딩 중일 때 대시보드 API 요청 시, **When** 프록시 엔드포인트가 호출되면, **Then** 무한 타임아웃 대신 `503 Service Unavailable`이 즉시 반환되고 준비 중 안내가 표시되어야 합니다.
4. **Given** 외부 IP 환경에서 대시보드 웹 UI에 접속할 때, **When** 대시보드 API 요청이 발생하면, **Then** `window.location.origin` 동적 상대 경로로 전달되어 타임아웃 없이 정상 처리되어야 합니다.

---

### Edge Cases

- 임베딩/리랭킹 모델의 인퍼런스 엔드포인트 규격(`/v1/embeddings` 또는 `/rerank` 또는 `/v1/models`)이 일반 Causal LLM과 달라 헬스체크 응답 형태가 다를 경우 어떻게 처리할 것인가?
- GPU VRAM 메모리가 보조 모델 동시 로딩 시 부족하거나 프로세스 미정리로 인해 이전 모델 파이프라인이 남아있는 상황을 어떻게 방지할 것인가?
- 벤치마크 스크립트 비동기 이벤트를 종료할 때 백그라운드 데몬으로 스폰된 메인 서버 프로세스가 함께 종료되지 않도록 파이프라인을 완전 분리하는 방법은 무엇인가?
- 외부 IP 환경 접속 시 대시보드 API가 `localhost` 하드코딩으로 타임아웃 실패되는 것을 예방하는 방법은 무엇인가?

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: BGE M3(`bge-m3`) 임베딩 모델의 백엔드 프로세스 구동 및 벤치마크 추론 검증 100% 통과
- **DoD-002**: BGE Reranker v2 M3(`bge-reranker-v2-m3`) 모델의 헬스체크 타임아웃 해제 및 서빙 Ready 검증 통과
- **DoD-003**: `uv run python scripts/benchmark_quality.py --real` 실행 시 모든 모델(LLM 및 보조 모델)의 실측 추론 검증 성공 및 리포트 정상 생성
- **DoD-004**: 벤치마크 스크립트 완료 후 기본 모델 그룹(qwen3.5-4b, bge-m3, bge-reranker-v2-m3)이 백그라운드 서빙으로 원복 상주하여 `./status_server.sh` 헬스체크 100% 통과
- **DoD-005**: 대시보드 프록시 프리플라이트 헬스 가드 구현으로 백엔드 로딩 시 무한 타임아웃 방지 및 503 즉시 반환 검증 완료
- **DoD-006**: 대시보드 API 호출 주소 `window.location.origin` 동적 상대 경로 전환 및 Playwright E2E 브라우저 회귀 테스트 100% 통과
- **DoD-007**: 전체 파이썬 단위/통합 테스트 수트(`uv run pytest`) 100% Green Pass

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 시스템은 `bge-m3` 임베딩 모델 서빙 시 임베딩 전용 파라미터(예: `--embedding`)를 정확히 전달하여 헬스체크 및 임베딩 추론 요청을 성공 처리해야 합니다.
- **FR-002**: 시스템은 `bge-reranker-v2-m3` Cross-Encoder 모델 서빙 시 프로세스가 정상적으로 헬스체크를 통과하고 서빙을 개설하도록 서버 시작 인자 및 적응형 타임아웃을 제공해야 합니다.
- **FR-003**: `scripts/benchmark_quality.py` 스크립트는 LLM 모델뿐만 아니라 임베딩 및 리랭킹 모델에 맞춰 헬스체크 및 추론 검증 엔드포인트(예: `/v1/embeddings` 등)를 올바르게 호출하도록 동작을 개선해야 합니다.
- **FR-004**: 벤치마크 스크립트는 모델 간 전환 시 기존 PID 정리 및 VRAM 해제를 엄격히 검증하여 메모리 간섭으로 인한 타임아웃이나 OOM을 예방해야 합니다.
- **FR-005**: 서비스 플랫폼 수동 빌드 및 setup 후 벤치마크 실행 시 전체 8개 모델이 차례대로 검증 완료되고 결과를 리포트 파일에 저장해야 합니다.
- **FR-006**: 벤치마크 완료 후 복원 단계는 파이썬 벤치마크 스크립트 프로세스 종료와 독립적인 디태치 백그라운드 데몬으로 기본 모델 그룹(`qwen3.5-4b`, `bge-m3`, `bge-reranker-v2-m3`)을 동시 서빙 상주 시켜야 합니다.
- **FR-007**: 시스템은 메인 API 서버(8081 포트) 프록시 호출 시 백엔드 LLM 엔진(8089 포트) 연결 상태를 프리플라이트 검증하여, 엔진 미준비/로딩 시 무한 타임아웃 대신 `503 Service Unavailable` 및 상태 메시지를 즉시 응답해야 합니다.
- **FR-008**: 대시보드 웹 UI 프론트엔드는 모든 REST/SSE/Playground API 요청 시 하드코딩된 localhost 대신 `window.location.origin` 동적 상대 경로를 사용하고, 멀티 플랫폼 접속 환경에서의 타임아웃을 차단해야 합니다.

### Key Entities

- **Auxiliary Model Catalog**: 임베딩(`bge-m3`) 및 리랭크(`bge-reranker-v2-m3`) 모델의 모델 타입, 실행 인자, 헬스체크 경로, 엔드포인트 정보를 정의하는 데이터 객체
- **Benchmark Execution Result**: 모델별 서빙 로딩 시간, TTFT/TPOT 또는 임베딩/리랭크 처리 속도, GPU VRAM 사용량, 헬스체크 성공 여부를 포함하는 리포트 항목
- **Co-Loading Service Profile**: 기본 서비스 모델 그룹(LLM, Embedding, Reranker)을 GPU VRAM에 동시 구동하기 위한 인퍼런스 서버 프로세스 구성 세트
- **Backend Health Preflight Guard**: 메인 API 서버 프록시 레이어에서 백엔드 C++ 인퍼런스 엔진 소켓/헬스 상태를 빠르게 검증하여 타임아웃을 차단하는 가드 객체

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: BGE M3 임베딩 모델의 실측 추론 성공률 100% 달성 (추론 실패 0건)
- **SC-002**: BGE Reranker v2 M3 모델의 서빙 헬스체크 15초 이내 통과 및 READY 전환율 100%
- **SC-003**: `scripts/benchmark_quality.py --real` 실행 시 catalog 내 전체 8개 모델에 대한 실측 테스트 완료율 100%
- **SC-004**: 벤치마크 완료 후 기본 서비스 모델 그룹(`qwen3.5-4b`, `bge-m3`, `bge-reranker-v2-m3`) 복원 시 `./status_server.sh` 헬스체크 및 동시 서빙 상주 상태 100% 보장
- **SC-005**: 대시보드 및 API 프록시 요청 시 백엔드 미구동/로딩 단계에서 무한 타임아웃 발생률 0% 달성 (503 프리플라이트 안내 즉시 수신)
- **SC-006**: 서비스 플랫폼 실 IP 및 외부 접속 환경에서 대시보드 API 호출 성공률 100% (타임아웃 발생 0건)

## Assumptions

- 사용자의 물리 환경(GeForce GTX 1070, 8GB VRAM, CUDA 12.0)에서 사전 설치된 llama-server C++ 바이너리가 임베딩 및 리랭킹 백엔드 옵션을 지원함.
- `config/model_catalog.json` 내 aux 모델 구동 정보 및 script 프로세스 매니저(`src/core/process_manager.py`, `src/core/auxiliary_manager.py`)에서 지원 인자를 제어함.

# Feature Specification: Real GPU Context Window Scaling Benchmark, Event Loop Cleanup, OpenAI Models API & Config Refactoring Fix

**Feature Branch**: `specs/016-context-scaling-and-cleanup-fix`

**Created**: 2026-07-29

**Status**: Approved

**Input**: User request: "빠진 벤치마크가 있어, 컨텍스트 윈도우 크기를 늘려가면서, 메모리 사용량과 응답 시작 시간, 토큰 생성속도의 변화를 벤치마크해서 적정 모델과, 적정 컨텍스트 윈도우 크기를 찾는 벤치마킹이 사라졌잖아 전에 있었다고. 016 스펙 번호로 통합해. opeanai api 표준을 지킨다면서, 모델 목록 호출에 응답하는 엔드포인트가 없네, 모델 목록이 안나오길래, 파일들을 살펴봤는데, 설마 모델 목록 하드코딩되어있어? 분석 내용을 스펙에 모두 반영하고 고도화"

---

## Executive Summary & User Value

본 피처는 016 스펙 번호로 통합되었으며, 아래 4가지 핵심 요구사항을 완결 및 고도화합니다:

1. **실측 GPU 컨텍스트 윈도우 스케일링 벤치마크 (2K~32K) 및 적정 모델/컨텍스트 도출**:
   서빙 지원 대상 6개 모델 (`Gemma 4` E2B/E4B/12B 및 `Qwen 3.5` 2B/4B/9B)에 대해 컨텍스트 윈도우 크기 (`n_ctx`: 2K, 4K, 8K, 16K, 32K) 확장 시 **실측 VRAM 메모리 사용량(MB)**, **응답 시작 시간(TTFT, ms)**, **토큰 생성 속도(TPOT, tok/s)**의 변화를 실측 GPU 인퍼런스를 통해 자동 측정하고, 단일 GTX 1080 Ti (11GB VRAM) 환경에서의 **서비스 유형별 적정 모델 및 적정 컨텍스트 윈도우 크기 도출 매트릭스**를 분석 마크다운 리포트에 작성합니다.
2. **이벤트 루프 트랜스포트 예외 경고 제거**:
   `benchmark_quality.py` 구동 종료 시 파이썬 소멸자에서 발생하던 `BaseSubprocessTransport.__del__ RuntimeError: Event loop is closed` 예외 경고를 명시적 트랜스포트 닫기 및 마이크로태스크 소진으로 완전히 제거합니다.
3. **OpenAI API 표준 `GET /v1/models` 모델 목록 엔드포인트 구현**:
   서버 구동 상태와 관계없이 `GET /v1/models` 호출 시 `PRESET_CATALOG` 기반의 **전체 모델 카탈로그 목록**(모델 ID, 상주 서빙 여부, 로컬 파일 다운로드 존재 여부 등)을 OpenAI 표준 규격 JSON(`{"object": "list", "data": [...]}`)으로 동적 반환합니다.
4. **하드코딩 설정값 외부화 및 JSON/환경변수 모듈화 (전수 조사 반영)**:
   파이썬 코드에 파편화되어 있던 모델 카탈로그 목록(`config/model_catalog.json`), 백엔드 포트 및 호스트(`config/server_config.json` / 환경변수 `LLAMA_PORT`, `LLAMA_HOST`), GPU VRAM 상한 및 타임아웃 파라미터를 외부 설정 구조로 모듈화합니다.

---

## Clarifications

### Session 2026-07-29

- Q: 016 번호로의 스펙 통합 범위는? → A: 컨텍스트 윈도우 실측 스케일링 측정 엔진 구현 + 적정 모델/컨텍스트 도출 매트릭스 리포트 + 서브프로세스 트랜스포트 이벤트 루프 정리 로직을 016 스펙 단일 본문으로 완전 통합함.
- Q: OpenAI API `GET /v1/models` 엔드포인트 응답 범위 → A: `PRESET_CATALOG` 전체 지원 모델 목록을 OpenAI API 표준 규격(`{"object": "list", "data": [...]}`)으로 동적 반환 (활성화 상주 및 로컬 다운로드 상태 포함).
- Q: 코드베이스 정밀 감사 결과 하드코딩 항목 고도화 범위 → A: 모델 카탈로그(HF repo_id, GGUF/CLIP 경로, VRAM 요구량), 백엔드 포트/URL(8081, 127.0.0.1), VRAM 상한선(11264MB), 커넥션 풀 크기, 타임아웃 파라미터를 JSON 및 환경변수로 전면 외부화.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 실측 GPU 컨텍스트 윈도우 스케일링 벤치마크 및 적정 모델/컨텍스트 추천 도출 (Priority: P1)

**User Story**: AI 솔루션 아키텍트 및 서비스 운영자는 컨텍스트 윈도우 크기(2K~32K) 증가에 따른 VRAM 점유량, TTFT, TPOT 실측 데이터를 확인하여 서비스 목적별(초저지연, 기본 상주 서빙, 고정밀 분석) 적정 모델과 적정 컨텍스트 윈도우 크기를 도출하길 원한다.

**Why this priority**: 프롬프트 길이가 길어짐에 따라 발생하는 VRAM OOM 붕괴를 방지하고, 단일 GTX 1080 Ti GPU 한계 내에서 최고 성능을 내는 적정 모델 및 컨텍스트 크기를 추천받기 위함입니다.

**Independent Test**: `uv run python scripts/benchmark_quality.py --auto-download --real` 실행 시 6개 모델에 대한 컨텍스트 윈도우 스케일링 실측표 및 "적정 모델 & 적정 컨텍스트 크기 추천 매트릭스"가 생성됨을 확인.

**Acceptance Scenarios**:

1. **Given** 실측 벤치마크 구동 시, **When** 각 모델별로 `n_ctx` (2K, 4K, 8K, 16K, 32K)를 적용하여 인퍼런스를 실행할 때, **Then** 각 컨텍스트 크기별 실측 VRAM Peak(MB), TTFT(ms), TPOT(tok/s)를 수집하여 스케일링 비교표를 생성한다.
2. **Given** 벤치마크 완료 후 마크다운 리포트 작성 시, **When** 수집된 실측 지표를 분석할 때, **Then** 서비스 유형별 (1. ⚡ 초저지연 에이전트, 2. ⚖️ 기본 상주 서빙, 3. 🎯 고정밀 분석) 적정 모델 명칭과 적정 컨텍스트 윈도우 크기(예: Qwen 3.5 4B @ 8K)를 명시한다.
3. **Given** 16K/32K 고컨텍스트 로딩 시 11GB VRAM 한계를 초과하는 경우, **When** Pre-flight VRAM estimator에 의해 감지되면, **Then** `is_oom=True` 상태를 표기하고 프로세스 OOM 붕괴 없이 다음 측정으로 안정적으로 진행한다.

---

### User Story 2 - 서브프로세스 트랜스포트 명시적 클로징 및 Clean Exit (Priority: P1)

**User Story**: 개발자 및 운영자는 벤치마크 및 프로세스 종료 시, 콘솔에 파이썬 소멸자 예외 에러(`RuntimeError: Event loop is closed`) 없이 깨끗하게 exit 되길 원한다.

**Why this priority**: 프로세스 종료 시 리소스 완전 해제 및 콘솔 로그의 무결성을 유지하기 위함입니다.

**Independent Test**: `uv run python scripts/benchmark_quality.py --auto-download --real` 완료 후 종료 메시지에 `BaseSubprocessTransport.__del__` 경고가 단 1건도 출력되지 않음을 확인.

**Acceptance Scenarios**:

1. **Given** `ProcessManager`가 서브프로세스를 종료할 때 (`stop_process`), **When** 프로세스가 종료되고 루프가 닫히기 전, **Then** `BaseSubprocessTransport`의 닫힘 콜백이 루프 안에서 완결되어 소멸자 예외가 발생하지 않는다.

---

### User Story 3 - OpenAI API 표준 `GET /v1/models` 모델 목록 엔드포인트 제공 (Priority: P1)

**User Story**: API 사용자 및 외부 챗 클라이언트는 `GET /v1/models` 요청을 통해 서버에서 지원하는 전체 LLM 모델 카탈로그와 현재 활성화 상태를 OpenAI 호환 포맷으로 즉시 동적 조회하길 원한다.

**Why this priority**: 표준 OpenAI API 클라이언트(LangChain, LlamaIndex, Open-WebUI 등)와의 100% 규격 호환성을 확보하기 위함입니다.

**Independent Test**: `curl -X GET http://127.0.0.1:8000/v1/models` 호출 시 HTTP 200 OK와 함께 `gemma4-e2b`, `qwen3.5-4b` 등 카탈로그 모델 6개의 리스트가 JSON으로 반환됨을 확인.

**Acceptance Scenarios**:

1. **Given** 외부 HTTP 클라이언트가 `GET /v1/models`를 요청할 때, **Then** `PRESET_CATALOG` 내 전체 모델이 포함된 OpenAI 표준 JSON 구조(`{"object": "list", "data": [{"id": "gemma4-e2b", "object": "model", ...}]}`)를 리턴한다.
2. **Given** VRAM 상주 서빙 모델이 교체되거나 서브프로세스가 오프로드 대기 중일 때, **When** `GET /v1/models`를 요청할 때, **Then** 하드코딩이나 프록시 에러 없이 현재 활성화된 모델(`active_model`) 및 다운로드 여부 정보를 올바르게 포함하여 응답한다.

---

### User Story 4 - 하드코딩 설정값 외부화 및 JSON/환경변수 모듈화 (Priority: P2)

**User Story**: 인프라 운영자 및 서비스 개발자는 모델 카탈로그 정보, 네트워크 포트, VRAM 용량 한계, 커넥션 풀 크기 등 시스템 운영 변수를 파이썬 코드 수정 없이 외부 설정 파일(`config/model_catalog.json`, `config/server_config.json`) 및 환경변수로 동적 변경하길 원한다.

**Why this priority**: 다양한 하드웨어 및 서버 배포 환경에서 소스 코드 변경 없는 유연한 운용성을 확보하기 위함입니다.

**Independent Test**: `config/model_catalog.json` 및 `config/server_config.json` 수정 후 서빙 서버 구동 시 변경된 카탈로그 및 포트가 동적으로 정상 적용됨을 확인.

**Acceptance Scenarios**:

1. **Given** `config/model_catalog.json` 파일이 존재할 때, **When** `ProcessManager` 및 `ModelDownloader`가 초기화될 때, **Then** 파이썬 코드 하드코딩 대신 해당 JSON 설정 파일로부터 카탈로그 데이터를 로드한다.
2. **Given** 환경변수 `LLAMA_PORT` 또는 `config/server_config.json`에 다른 포트(예: 8082)가 지정될 때, **When** 서빙 서버 및 API 프록시가 개설될 때, **Then** 지정된 포트로 백엔드 프로세스 바인딩 및 프록시 연결을 완료한다.

---

## Edge Cases

- 특정 대형 모델이 32K 컨텍스트에서 VRAM 11GB를 초과하는 경우: OOM 위험 문구를 표기하고 해당 크기를 상주 서빙 금지 구간으로 추천 매트릭스에 반영함.
- 이벤트 루프가 외부 라이브러리에 의해 이미 닫힌 경우: `loop.is_closed()` 체크를 통해 이중 닫힘 오류 차단.
- 백엔드 프로세스가 오프로드(Unloaded) 상태일 때 `GET /v1/models` 호출 시: 503 에러가 아닌 카탈로그 전체 모델 목록을 200 OK로 리턴함.
- 외부 설정 JSON 파일이 훼손되거나 파싱 에러 발생 시: 안전한 기본 내장 폴백(Default Fallback) 설정을 적용하고 경고 로그를 남김.

---

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `scripts/benchmark_quality.py` 내 컨텍스트 윈도우 스케일링 (2K, 4K, 8K, 16K, 32K) 실측 GPU 측정 루프 구현.
- **DoD-002**: `analysis_report_quality.md` 리포트에 "컨텍스트 스케일링 분석표" 및 "적정 모델 & 적정 컨텍스트 윈도우 크기 추천 매트릭스" 생성.
- **DoD-003**: `ProcessManager.stop_process()` 및 스크립트 exit 시 `RuntimeError: Event loop is closed` 경고 예외 0건 검증.
- **DoD-004**: `GET /v1/models` OpenAI API 동적 리스팅 엔드포인트 구현 및 테스트 통과.
- **DoD-005**: `config/model_catalog.json` 및 `config/server_config.json` 외부화 구현 및 기존 하드코딩 제거.
- **DoD-006**: `pytest` 듀얼 모드 테스트 수트 100% 통과.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 (실측 GPU 컨텍스트 스케일링 루프)**: 벤치마크 엔진은 6개 모델에 대해 `n_ctx` (2048, 4096, 8192, 16384, 32768)를 순차 적용하여 실측 GPU VRAM 점유량, TTFT, TPOT을 측정해야 한다.
- **FR-002 (적정 모델 및 컨텍스트 크기 추천 로직)**: 벤치마크 엔진은 수집된 실측 데이터를 바탕으로 아래 3가지 카테고리의 적정 모델 및 적정 컨텍스트 크기를 자동 도출해야 한다:
  1. ⚡ **초저지연 에이전트 서빙**: 최소 TTFT 및 최고 TPOT 조합
  2. ⚖️ **기본 상주 서빙 (Default Resident)**: 가성비 지수 및 VRAM 안전 마진 최적 조합
  3. 🎯 **고정밀 분석 서빙**: 최대 컨텍스트 수용성 및 정밀도 조합
- **FR-003 (VRAM OOM 세이프티 가드)**: 11GB VRAM 한계 초과 위험 구간은 사전 감지하여 `is_oom=True`로 표기하고 프로세스 다운을 차단해야 한다.
- **FR-004 (마크다운 분석 리포트 확장)**: `generate_markdown_report()`는 컨텍스트 스케일링 실측 결과표와 적정 모델/컨텍스트 추천 매트릭스를 Markdown 문서로 생성해야 한다.
- **FR-005 (서브프로세스 트랜스포트 명시적 닫기)**: `ProcessManager.stop_process()`는 프로세스 종료 시 `self.process._transport.close()`를 안전하게 호출하여 이벤트 루프 종료 전에 파이프 트랜스포트를 명시적으로 해제해야 한다.
- **FR-006 (이벤트 루프 마이크로태스크 소진)**: 프로세스 종료 직후 `await asyncio.sleep(0)`을 수행하여 닫힘 콜백 이벤트가 현재 이벤트 루프 내에서 완결되도록 처리해야 한다.
- **FR-007 (OpenAI API GET /v1/models 동적 모델 목록 핸들러)**: API 라우터는 `GET /v1/models` 요청 수신 시 `PRESET_CATALOG` 데이터베이스 및 `ModelDownloader` 로컬 저장소 상태를 조회하여 전체 지원 모델 ID, 소유자(`llm-server`), 현재 활성화 여부(`active_model`)를 포함한 OpenAI 규격 JSON 응답을 200 OK로 반환해야 한다.
- **FR-008 (모델 카탈로그 외부 JSON 파일 분리)**: `config/model_catalog.json`을 신설하여 지원 모델 카탈로그(HF repo_id, gguf 경로, clip 경로, vram_est_mb, chat_template)를 단일 파일로 분리하고 `ProcessManager`와 `ModelDownloader`가 공통 로드해야 한다.
- **FR-009 (서버 포트/호스트 환경변수 및 JSON 외부화)**: `inference_api.py`, `llama_manager.py`, `process_manager.py`의 `8081` 포트 및 Host URL을 `config/server_config.json` 또는 환경변수(`LLAMA_PORT`, `LLAMA_HOST`)로 동적 로드하도록 변경해야 한다.
- **FR-010 (GPU VRAM 및 타임아웃 가변 설정 지원)**: GPU VRAM 상한선 및 헬스체크 타임아웃(120s), HTTP 커넥션 풀 설정을 가변 설정 가능하게 모듈화해야 한다.

### Key Entities

- **ContextScalingMetric**: `n_ctx` 크기, VRAM 사용량(MB), TTFT(ms), TPOT(tok/s), OOM 발생 여부(`is_oom`)를 담는 데이터 구조.
- **OptimalModelRecommendation**: 서비스 유형, 적정 모델 명칭, 적정 컨텍스트 크기, 선택 사유를 정의하는 데이터 구조.
- **ModelListResponse**: OpenAI API `/v1/models` 규격 (`object="list"`, `data=[ModelObject(...)]`).
- **ModelCatalogConfig**: 외부 JSON 카탈로그 설정 구조 (`config/model_catalog.json`).
- **ServerConfig**: 서버 포트, 호스트, 타임아웃, 커넥션 풀 외부 설정 구조 (`config/server_config.json`).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001 (스케일링 벤치마크 커버리지)**: 카탈로그 6개 모델에 대한 5개 컨텍스트 구간(2K~32K) 측정 완성도 100%.
- **SC-002 (적정 추천 매트릭스 도출)**: 3가지 서비스 유형별 적정 모델 및 적정 컨텍스트 크기 추천 명시 100%.
- **SC-003 (소멸자 예외 발생 0건)**: `benchmark_quality.py` 구동 완료 후 `RuntimeError: Event loop is closed` 예외 발생 0건.
- **SC-004 (OpenAI models API 호환성)**: `curl GET /v1/models` 호출 시 카탈로그 전체 6개 모델 반환 성공률 100%.
- **SC-005 (하드코딩 제거율)**: 모델 카탈로그, 포트, 호스트 URL 하드코딩 제거율 100%.
- **SC-006 (리포트 생성 완료율)**: `data/reports/analysis_report_quality.md` 생성 완료율 100%.

---

## Assumptions

- GTX 1080 Ti (11GB VRAM) 환경에서 소형 모델(2B)은 16K~32K 컨텍스트를 지원할 수 있으나, 대형 모델(9B/12B)은 8K 이상의 컨텍스트 설정 시 VRAM OOM 필터링이 작동함.
- 외부 설정 JSON 파일 미존재 시 내장된 기본 안전 백업(Default Fallback) 정보로 동작함.

# Tasks: 실시간 LLM 백엔드 엔진 연동 Playground & 프롬프트/응답 원문 Payload 캡처 고도화 (046-real-llm-playground-payload)

**Input**: `/specs/046-real-llm-playground-payload/` 디자인 문서 (`plan.md`, `spec.md`, `research.md`, `data-model.md`, `quickstart.md`)  
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `quickstart.md`

---

## Phase 1: Setup (공통 기반 작업)

**목적**: 프로젝트 환경 및 의존성 확인

- [x] T001 [P] `src/api/routes/dashboard_api.py` 및 `src/api/routes/inference_api.py`에서 `httpx` 비동기 클라이언트 연동 환경 확인

---

## Phase 2: Foundational (선행 블로킹 전제조건)

**목적**: 사용자 스토리 구현 전 완료되어야 하는 핵심 인프라 검증

- [x] T002 `data/metrics.db` SQLite 데이터베이스 스키마 및 `src/db/metrics_db.py` 내부 `prompt_text` / `completion_text` 컬럼 로깅 인터페이스 정합성 확인
- [x] T003 [P] `src/api/routes/dashboard_api.py`의 `llama-server` 헬스체크 헬퍼 (`check_llama_status`) 연동 상태 검증

---

## Phase 3: User Story 1 - AI Playground 실제 백엔드 LLM 모델 인퍼런스 연동 (Priority: P1) 🎯 MVP

**목적**: AI Playground 호출 시 더미 텍스트 응답을 전면 제거하고 실제 C++ `llama-server` 백엔드 엔진(`http://127.0.0.1:8089/v1/chat/completions`) 비동기 연동 및 실제 생성 답변 렌더링

**독립 테스트**: AI Playground에서 사용자 질문 전송 시 백엔드 C++ `llama-server`를 거쳐 실제 LLM이 생성한 대답 및 토큰 메트릭(TTFT, Tok/s) 정상 출력을 검증

### User Story 1 테스트

- [x] T004 [P] [US1] `tests/unit/test_real_llm_playground_payload.py`에 실제 LLM 플레이그라운드 인퍼런스 연동 단위 테스트 수트 작성

### User Story 1 구현

- [x] T005 [US1] `src/api/routes/dashboard_api.py`의 `run_playground_test` 함수에서 더미 텍스트 생성을 제거하고 `httpx.AsyncClient` 기반 `http://127.0.0.1:8089/v1/chat/completions` 비동기 요청 구현
- [x] T006 [US1] `src/api/routes/dashboard_api.py`에서 `check_llama_status()` 오프라인 시 "Model loading or offline" 가이드 메시지 반환 오프라인 폴백 처리 구현
- [x] T007 [US1] `src/api/routes/dashboard_api.py`에서 백엔드 LLM 응답으로부터 실제 생성 대답 텍스트 및 토큰 메트릭(`ttft_ms`, `tps`, `total_latency_ms`, `prompt_tokens`, `completion_tokens`) 파싱 구현

---

## Phase 4: User Story 2 - `/v1/*` 역방향 프록시 및 Playground 실제 Payload 캡처 (Priority: P2)

**목적**: `/v1/chat/completions` 인퍼런스 프록시 호출 및 Playground 테스트 시 사용자 질문(Prompt)과 LLM 생성 답변(Completion Text)의 실측 원문을 SQLite Audit DB에 100% 정밀 저장

**독립 테스트**: 대시보드 Audit 탭의 [👁️ View Payload] 팝업 모달에서 실제 질문 원문과 모델 생성 답변 원문이 정확히 표출되는지 검증

### User Story 2 테스트

- [x] T008 [P] [US2] `tests/unit/test_real_llm_playground_payload.py`에 역방향 프록시/플레이그라운드 Payload 캡처 저장 및 지연 오버헤드(<5ms) 단정 검증 테스트 작성

### User Story 2 구현

- [x] T009 [US2] `src/api/routes/inference_api.py`의 reverse proxy 핸들러에서 요청 JSON의 `messages`/`prompt` 및 응답 JSON의 `choices[0].message.content` 원문 추출 구현
- [x] T010 [US2] `src/api/routes/inference_api.py` 및 `src/api/routes/dashboard_api.py`에서 `metrics_db.log_request` 호출 시 `prompt_text`와 `completion_text` 원문 파라미터 전달 및 저장 연동
- [x] T011 [US2] `src/api/routes/dashboard_api.py` 대시보드 Audit 엔드포인트와 저장된 Payload 원문 간 조회 데이터 호환성 검증

---

## Phase 5: Polish & Cross-Cutting Concerns (다듬기 및 마무리)

**목적**: 전체 테스트 수트 회귀 검증 및 문서화

- [x] T012 [P] `uv run pytest tests/unit/test_api_key_auth_toggle.py tests/unit/test_llm_payload_viewer.py tests/unit/test_db_seed_integration.py tests/unit/test_real_llm_playground_payload.py -v` 명령으로 전체 회귀 검증 수행
- [x] T013 [P] `specs/046-real-llm-playground-payload/quickstart.md`에 실측 테스트 검증 결과 기록 및 문서 업데이트

---

## Dependencies & Execution Order (의존성 및 실행 순서)

### Phase Dependencies

- **Setup (Phase 1)**: 의존성 없음 - 즉시 시작 가능
- **Foundational (Phase 2)**: Phase 1 완료 후 시작 가능 - 모든 사용자 스토리 작업 블로킹
- **User Stories (Phase 3+)**: Phase 2 Foundational 완료 후 시작 가능 (P1 → P2 순서로 진행)
- **Polish (Phase 5)**: 모든 사용자 스토리 완료 후 진행

### User Story Dependencies

- **User Story 1 (P1)**: Phase 2 완료 후 시작 가능
- **User Story 2 (P2)**: Phase 2 완료 후 시작 가능 (US1과 독립적 또는 순차 진행 가능)

### Parallel Opportunities

- Setup tasks (T001) 및 Foundational (T003) 병렬 수행 가능
- US1 테스트 (T004) 병렬 작성 가능
- US2 테스트 (T008) 병렬 작성 가능
- Polish 단계 T012, T013 병렬 수행 가능

---

## Implementation Strategy (구현 전략)

### MVP First (User Story 1 Only)

1. Phase 1: Setup 완료
2. Phase 2: Foundational 완료
3. Phase 3: User Story 1 구현 및 검증 (AI Playground 실제 백엔드 연동)
4. 독립 검증: `uv run pytest tests/unit/test_real_llm_playground_payload.py` 실행하여 US1 정상 작동 확인

### Incremental Delivery

1. Setup + Foundational 완료
2. User Story 1 완료 (MVP 출시 가능)
3. User Story 2 완료 (Payload Audit 캡처 저장 완성)
4. Phase 5 Polish 전체 회귀 검증 완료

# Tasks: LLM 응답 내 <think> 추론 태그 자동 파싱 및 정제 (047-think-tag-stripping)

**Input**: `/specs/047-think-tag-stripping/` 디자인 문서 (`plan.md`, `spec.md`, `research.md`, `data-model.md`, `quickstart.md`)  
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `quickstart.md`

---

## Phase 1: Setup (공통 기반 작업)

**목적**: 프로젝트 환경 및 의존성 확인

- [x] T001 [P] `src/core/think_tag_parser.py` 파서 모듈 작성을 위한 환경 및 의존성 검증

---

## Phase 2: Foundational (선행 블로킹 전제조건)

**목적**: 사용자 스토리 구현 전 완료되어야 하는 핵심 인프라 파서 및 DB 스키마 구축

- [x] T002 `src/core/think_tag_parser.py`에 정규식 및 스트리밍 상태머신 기반 `<think>...</think>` 태그 분리 헬퍼 구현
- [x] T003 `src/core/metrics_db.py`에 `thinking_text` 컬럼 마이그레이션 및 `log_request` 파라미터 저장 로직 구현

---

## Phase 3: User Story 1 - LLM 응답 내 `<think>...</think>` 추론 태그 자동 분리 및 정제 (Priority: P1) 🎯 MVP

**목적**: AI Playground 및 인퍼런스 API 응답에서 `<think>` 태그를 파싱하여 `text` 필드에는 정제된 대답만 반환하고 `thinking_process` 필드에 사고과정 분리

**독립 테스트**: `<think>사고과정...</think>답변` 수신 시 `text`에 깔끔한 답변만 렌더링되고 `thinking_process`에 사고과정이 정상 분리되는지 검증

### User Story 1 테스트

- [x] T004 [P] [US1] `tests/unit/test_think_tag_stripping.py`에 태그 파싱, 스트리밍 감지, 잘림 격리 단위 테스트 수트 작성

### User Story 1 구현

- [x] T005 [US1] `src/api/routes/dashboard_api.py`에서 `PlaygroundRequest` 기본 `max_tokens`를 1024로 상향 조정하고 `PlaygroundResponse`에 `thinking_process` 필드 추가
- [x] T006 [US1] `src/api/routes/dashboard_api.py`의 `run_playground_test`에 `parse_think_tags`를 적용하여 `text`와 `thinking_process` 분리 및 `metrics_db` 기록 연동
- [x] T007 [US1] `src/api/routes/inference_api.py`의 `reverse_proxy` 스트리밍 파이프라인에서 `<think>` 토큰 실시간 감지/필터링 및 `thinking_text` DB 기록 연동
- [x] T008 [US1] `src/core/think_tag_parser.py`에서 `</think>` 닫는 태그 누락 잘림 발생 시 `[Truncated during thinking process]` 안전 폴백 처리 구현

---

## Phase 4: User Story 2 - Playground 및 Audit Payload 뷰어 추론 과정 접기/펼치기 UI (Priority: P2)

**목적**: 대시보드 Audit 탭 [👁️ View Payload] 팝업 모달 및 Playground 대화스레드에서 추론 과정("🧠 Thinking Process") 아코디언 표출

**독립 테스트**: Audit Payload 뷰어 API (`GET /dashboard/api/audit/payload/{id}`)에서 `thinking_text` 데이터 반환 및 뷰어 표출 호환성 검증

### User Story 2 테스트

- [x] T009 [P] [US2] `tests/unit/test_think_tag_stripping.py`에 Audit Payload 뷰어 `thinking_text` 데이터 반환 검증 테스트 작성

### User Story 2 구현

- [x] T010 [US2] `src/core/metrics_db.py`의 `get_payload_by_id` 및 `src/api/routes/dashboard_api.py` Audit 엔드포인트에 `thinking_text` 필드 반환 연동
- [x] T011 [US2] `src/api/routes/dashboard_api.py` 대시보드 Audit 뷰어 JSON 스키마 호환성 검증

---

## Phase 5: User Story 3 - `<think>` 태그 정제 동작 제어 옵션 (`strip_think_tags`) (Priority: P3)

**목적**: `strip_think_tags=false` 파라미터 전달 시 원문 그대로 `<think>` 태그를 포함하여 수신하는 옵션 제어 기능

**독립 테스트**: `strip_think_tags=false` 요청 시 태그가 포함된 원문 반환 검증

### User Story 3 테스트

- [x] T012 [P] [US3] `tests/unit/test_think_tag_stripping.py`에 `strip_think_tags` 토글 옵션 검증 테스트 작성

### User Story 3 구현

- [x] T013 [US3] `src/api/routes/dashboard_api.py`의 `PlaygroundRequest`에 `strip_think_tags: bool = True` 옵션 제어 파라미터 구현

---

## Phase 6: Polish & Cross-Cutting Concerns (다듬기 및 마무리)

**목적**: 전체 테스트 수트 회귀 검증 및 문서화

- [x] T014 [P] `uv run pytest tests/unit/test_think_tag_stripping.py tests/unit/test_real_llm_playground_payload.py tests/unit/test_llm_payload_viewer.py -v` 명령으로 전체 회귀 검증 수행
- [x] T015 [P] `specs/047-think-tag-stripping/quickstart.md`에 실측 테스트 검증 결과 기록 및 문서 업데이트

---

## Dependencies & Execution Order (의존성 및 실행 순서)

### Phase Dependencies

- **Setup (Phase 1)**: 의존성 없음 - 즉시 시작 가능
- **Foundational (Phase 2)**: Phase 1 완료 후 시작 가능 - 모든 사용자 스토리 작업 블로킹
- **User Stories (Phase 3+)**: Phase 2 Foundational 완료 후 시작 가능 (P1 → P2 → P3 순서로 진행)
- **Polish (Phase 6)**: 모든 사용자 스토리 완료 후 진행

### User Story Dependencies

- **User Story 1 (P1)**: Phase 2 완료 후 시작 가능
- **User Story 2 (P2)**: Phase 2 및 US1 완료 후 진행 권장
- **User Story 3 (P3)**: Phase 2 완료 후 진행 가능

---

## Implementation Strategy (구현 전략)

### MVP First (User Story 1 Only)

1. Phase 1: Setup 완료
2. Phase 2: Foundational 완료 (`think_tag_parser.py` 및 DB 스키마)
3. Phase 3: User Story 1 구현 및 검증 (`<think>` 태그 파싱 & 정제)
4. 독립 검증: `uv run pytest tests/unit/test_think_tag_stripping.py` 실행하여 US1 정상 작동 확인

### Incremental Delivery

1. Setup + Foundational 완료
2. User Story 1 완료 (MVP 출시 가능)
3. User Story 2 완료 (Audit Payload 뷰어 아코디언 지원)
4. User Story 3 완료 (`strip_think_tags` 토글 옵션)
5. Phase 6 Polish 전체 회귀 검증 완료

---

## Phase 7: Convergence

- [x] T016 [US1] Update HTML input `#pg-max-tokens` default value from 256 to 1024 in `src/api/static/index.html` per FR-007 (partial)

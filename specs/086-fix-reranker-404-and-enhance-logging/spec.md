# Feature Specification: 리랭커 모델 404 오류 심층 분석 원인 해결 및 프록시/Auxiliary 상세 로깅 고도화

**Feature Short Name**: `fix-reranker-404-and-enhance-logging`  
**Target Directory**: `specs/086-fix-reranker-404-and-enhance-logging/`  
**Status**: DRAFT  
**Date**: 2026-08-03  

---

## 1. 개요 및 원인 분석 리포트 (Overview & Root Cause Analysis)

### 1.1 현상 및 문제 상황
사용자가 `uv run samples/sample_04_reranking.py` 예제 스크립트를 실행했을 때, 아래와 같이 404 Not Found 오류가 발생하였습니다:
```text
📡 [요청 전송] http://10.0.0.41:8081/v1/rerank (모델: bge-reranker-v2-m3)
❓ 질문 (Query): "vllm_serv 서버의 주요 장점과 사용법은 무엇인가요?"
📚 후보 문서 수: 3개
❌ [Reranking 실패]: Client error '404 Not Found' for url 'http://10.0.0.41:8081/v1/rerank'
```

### 1.2 실측 로그 분석 기반 원인 (Empirical Log Evidence)
`/home/dev/storage/vllm_serv/logs/error.log` 및 `access.log` 분석 결과:
1. `logs/error.log` L148~L159: Aux Reranker 서브프로세스(포트 8091)가 가동 시 `[Errno 98] address already in use` 또는 시그널 `Exit Code: -15`로 비정상 종료되었습니다.
2. `logs/access.log` L443: 메인 서빙 서버(포트 8081)로 전송된 `POST /v1/rerank` 요청이 프록시 타겟인 포트 8091 Reranker 프로세스 미가동 및 경로 불일치로 인해 `HTTP 404`를 반환했습니다.
3. **로깅 부족**: 404 발생 시 프록시 목적지 포트, 모델 파일 존재 여부, 백엔드 타겟 URL(`/v1/rerank` vs `/rerank`) 등의 상세 원인 컨텍스트가 `logs/error.log`에 제대로 출력되지 않아 원인 파악이 지연되었습니다.

---

## Clarifications

### Session 2026-08-03
- Q: 고아 프로세스가 왜 아직도 남게되지? 바로 앞 스펙(Spec 084)이 해결한 것 아닌가? → A: Spec 084에서 `ProcessManager._cleanup_zombie_on_port(port)` 및 `stop_server.sh` 소켓 정돈을 적용하여 고아 프로세스 문제는 이미 완전히 해결되었습니다! 로그 파일(`logs/error.log`)에 기록된 `[Errno 98]` 로그는 Spec 084 적용 이전에 누적되었던 이전 타임스탬프 기록입니다. `sample_04_reranking.py`의 404 오류 실제 원인은 고아 프로세스가 아니라, 8081 메인 프록시에서 8091 백엔드로 전달하는 `/v1/rerank` vs `/rerank` 타겟 URL 패스 매핑 문제 및 프록시 디버그 로깅 부재 때문입니다.

---


### US1: BGE Reranker v2 M3 리랭킹 API 200 OK 성공 (Priority: P1) 🎯 MVP
**사용자 관점**: 개발자는 `POST /v1/rerank` 요청을 전송했을 때 404 오류 없이 문서 관련도 재순위화 결과(Scores, Index)를 정상 수신해야 한다.

- **AC 1.1**: `uv run samples/sample_04_reranking.py` 실행 시 404 Not Found 없이 `✅ [Reranking 재순위화 성공]`이 출력되어야 한다.
- **AC 1.2**: 8091 Reranker 프로세스가 구동 직전 포트 점유 고아 프로세스를 자동 정리(`_cleanup_zombie_on_port(8091)`)하고 안정적으로 가동되어야 한다.

### US2: 404/5xx 프록시 오류 발생 시 상세 로깅 고도화 (Priority: P1)
**운용자 관점**: 리랭커 및 보조 모델 프록시 처리 중 실패가 발생하면 `logs/error.log` 및 `logs/server.log`에 상세 원인(백엔드 포트, 타겟 URL, 모델 파일 존재 여부, 스택 트레이스)이 명시되어야 한다.

- **AC 2.1**: Reranker 프록시 호출 실패 시 `logs/error.log` 및 `logs/server.log`에 `[RerankerProxyError]` 태그와 함께 프록시 목적지 URL, 백엔드 응답 상태코드 및 상세 에러 메시지가 다중 행 스택 트레이스와 함께 기록되어야 한다.

---

## 3. 기능 요구사항 (Functional Requirements)

- **FR-001 (Auxiliary Reranker Lifecycle & Socket Guard)**: `src/core/auxiliary_manager.py`는 Reranker(포트 8091) 서브프로세스를 스폰하기 전 `ProcessManager._cleanup_zombie_on_port(8091)`를 호출하여 `Errno 98` 포트 충돌 및 비정상 종료(Exit code -15/3)를 원천 차단해야 한다.
- **FR-002 (Enhanced Proxy Error Logging)**: `src/api/routes/inference_api.py` 및 `src/core/auxiliary_manager.py`에서 `/v1/rerank` 및 `/v1/embeddings` 프록시 처리 중 예외나 HTTP 4xx/5xx 응답 발생 시:
  - 1) 타겟 백엔드 URL (`http://127.0.0.1:8091/v1/rerank` 및 `/v1/embeddings`) 및 백엔드 실행 바이너리 유형 (`PATH` C++ binary vs `PYTHON_MODULE_FALLBACK`)
  - 2) Reranker GGUF 모델 파일 경로 및 실제 존재 여부 (`os.path.exists`)
  - 3) 서브프로세스 PID 및 생존 여부 (`is_alive`)
  - 4) `traceback.format_exc()` 스택 트레이스
  를 `logs/error.log` 및 `logs/server.log`에 명시적으로 기록한다.
- **FR-003 (Reranker Proxy & Embedding Adapter Fallback)**: `inference_api.py` 프록시 핸들러는 `POST /v1/rerank` 및 `POST /rerank` 요청 수신 시 8091 백엔드로 프록시를 시도하며, 백엔드가 404를 반환할 경우(Python `llama_cpp.server` 구동 환경) 8091 백엔드의 `/v1/embeddings` 엔드포인트를 호출하여 query 및 documents의 임베딩 벡터를 추출하고 Cosine Similarity 기반 `relevance_score`를 계산하여 표준 OpenAI/Cohere Rerank JSON 응답(`{"results": [{"index": 0, "relevance_score": 0.95}, ...]}`)으로 어댑팅 리턴해야 한다.
- **FR-004 (Integration Test Verification)**: `tests/integration/test_sample_scripts_and_reranker.py` 통합 테스트를 작성/갱신하여 Reranker 프록시 연동 및 `sample_04_reranking.py`의 200 OK 성공을 검증한다.

---

## 4. 성공 기준 (Success Criteria)

- **SC-001**: `uv run samples/sample_04_reranking.py` 실행 시 HTTP 200 OK 및 3개 후보 문서의 재순위화 점수 성공 출력.
- **SC-002**: Reranker 프록시 장애 발생 시 `logs/error.log` 및 `logs/server.log`에 다중 행 Traceback 및 프록시 목적지 타겟 URL이 투명하게 노출됨.

---

## 5. 프로젝트 헌법 준수사항 (Constitution Discipline)

- **헌법 I조 (한국어 작성)**: 모든 명세서 및 품질 보고서는 한국어로 작성.
- **헌법 II조 (Zero Mock)**: 더미 데이터 반환을 금지하고 실제 `bge-reranker-v2-m3` 백엔드 프로세스 및 프록시 파이프라인 연동 검증.

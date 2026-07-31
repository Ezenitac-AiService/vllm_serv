# Feature Specification: 임베딩(Embedding) 및 리랭커(Reranker) 모델 서빙 지원 및 1세대 코어(Nehalem) CPU 호환성 검증 (053-embedding-reranker-model-serving)

**Feature Branch**: `053-embedding-reranker-model-serving`  
**Created**: 2026-07-30  
**Status**: Draft  
**Input**: User request: "임베딩 모델 및 리랭커 모델 서빙 가능 여부 타당성 조사, 1세대 코어(Nehalem i7-930, AVX/AVX2 미지원) CPU 환경에서의 구동 호환성 리서치 및 기능 명세 도출"

---

## Technical Feasibility & Research Summary (기술 타당성 및 리서치 보고)

### 1. `llama-server` 백엔드 호환성
- **임베딩(Embedding) 모델 지원**: `llama-server`는 `--embedding` 플래그를 통해 OpenAI 호환 엔드포인트(`POST /v1/embeddings` 및 `POST /embedding`)를 자체 지원합니다. BERT, RoBERTa, Nomic-Embed, BGE-M3 등 GGUF 포맷 임베딩 모델 서빙이 가능합니다.
- **리랭커(Reranker) 모델 지원**: `llama-server`는 `--reranking` 플래그를 통해 Cross-Encoder 리랭킹 엔드포인트(`POST /v1/rerank` 및 `POST /rerank`)를 자체 지원합니다. BGE-Reranker-v2-M3, BGE-Reranker-Large 등 GGUF 포맷 Cross-Encoder 모델 서빙이 가능합니다.

### 2. 1세대 코어(Nehalem i7-930) CPU 호환성
- **AVX/AVX2 명령어 미지원 문제**: i7-930(Nehalem)은 SSE4.2까지만 지원하며 AVX/AVX2를 지원하지 않아, 일반적인 AVX 최적화 바이너리 실행 시 불법 명령어(`SIGILL`) 예외로 프로세스가 즉시 사망합니다.
- **해결 및 안전성 검증**: `vllm_serv` 엔진은 `legacy-i7-930-gtx1070` 프로필 하에서 Non-AVX 타겟(`-DGGML_AVX=OFF -DGGML_AVX2=OFF`) 바이너리를 빌드/선택합니다.
- **CUDA GPU 오프로딩 결합**: 임베딩 및 리랭커 모델의 텐서 연산은 GPU(`-ngl 99`)로 100% 오프로딩되므로, CPU 연산 비중이 극히 낮아 Nehalem CPU 환경에서도 SIGILL 예외 없이 안정적이고 빠르게 서빙됩니다.

### 3. 모델 주소 및 양자화 확정
- **임베딩 모델**: 원본 `BAAI/bge-m3` → GGUF: `ggml-org/bge-m3-Q8_0-GGUF` / 파일명: `bge-m3-q8_0.gguf` (아키텍처: BERT, 컨텍스트: 8192, 크기: ~605MB, 라이선스: MIT)
- **리랭커 모델**: 원본 `BAAI/bge-reranker-v2-m3` → GGUF: `klnstpr/bge-reranker-v2-m3-Q8_0-GGUF` / 파일명: `bge-reranker-v2-m3-q8_0.gguf` (아키텍처: BERT, 컨텍스트: 8192, 크기: ~606MB, 라이선스: Apache-2.0)
- **양자화 정책**: 전 플랫폼(GTX 1070 / GTX 1080 Ti / RTX 3060) Q8_0 단일 양자화 채택. 임베딩/리랭커 모델은 벡터 유사도 계산 특성상 Q8_0 → F16 간 검색 정확도 차이가 실측상 무시 수준이며, 모델 크기(각 ~600MB)가 LLM(3,500~9,800MB) 대비 극소량이므로 플랫폼별 양자화 분기의 실익이 없음.
- **벤치마크 검증 필수**: 임베딩+리랭커+LLM 동시 로딩 시 플랫폼별 VRAM 초과 여부를 실측 벤치마크로 검증해야 함 (기존 `scripts/benchmark_quality.py` 패턴 확장).

---

## Clarifications

### Session 2026-07-30
- Q: 임베딩/리랭커 모델의 GGUF 양자화 레벨 선택 → A: Q8_0 단일 양자화 채택, 플랫폼별 VRAM 동시 로딩 적합성 벤치마크 실측 검증
- Q: 임베딩/리랭커 서버의 LLM 서버와의 동시 실행 아키텍처 → A: 별도 프로세스 동시 실행 (임베딩/리랭커 각각 독립 llama-server 인스턴스, 별도 포트, LLM과 동시 상주)
- Q: 임베딩/리랭커 인스턴스의 자동 기동 시점 → A: 서버 기동 시 자동 시작 (vllm_serv 시작 시 LLM과 함께 임베딩/리랭커 인스턴스 동시 자동 기동, cold-start 없음)
- Q: 임베딩/리랭커 인스턴스 장애 시 복구 전략 → A: 자동 재시작 (기존 LLM ProcessManager의 헬스체크/자동 재시작 패턴 재활용)
- Q: 임베딩/리랭커 모델 다운로드 자동화 방식 → A: 기존 ModelDownloader 재활용 (카탈로그 등록 시 HuggingFace 자동 다운로드 파이프라인 동일 적용)

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 임베딩(Embedding) API 엔드포인트 서빙 및 테스트 (Priority: P1) 🎯 MVP

사용자가 RAG(검색 증강 생성) 또는 벡터 데이터베이스 구축을 위해 임베딩 모델(`ggml-org/bge-m3-Q8_0-GGUF` → `bge-m3-q8_0.gguf`, Q8_0 양자화)을 로드하고 `POST /v1/embeddings` API를 호출하면, 1024차원의 밀집 벡터(Dense Vector) 응답을 정상 수신합니다.

- **임베딩 모델 카탈로그 등록**: `config/model_catalog.json`에 임베딩 전용 모델 카테고리(`task_type: "embedding"`) 및 `--embedding` 백엔드 실행 플래그를 등록합니다.
- **API 응답 정합성**: `POST /v1/embeddings` 호출 시 OpenAI Embeddings API 규격(`object: "list"`, `data[].embedding`)과 100% 호환되는 벡터 결과를 반환합니다.
- **Nehalem CPU 검증**: AVX2가 없는 레거시 CPU 환경에서도 불법 명령어(`SIGILL`) 충돌 없이 CUDA GPU 오프로딩을 통해 안정 구동됩니다.

**Why this priority**: RAG 파이프라인 구축의 필수 전제 조건인 텍스트 임베딩 서빙 기능을 확보합니다.

**Independent Test**:
1. 임베딩 모델 지정 후 `POST /v1/embeddings`에 `{"input": "Test text"}` 전달 시 유효한 부동소수점 배열 벡터 반환 검증.

---

### User Story 2 - 리랭커(Reranker) API 엔드포인트 서빙 및 테스트 (Priority: P1) 🎯 MVP

사용자가 검색 결과의 재정렬(Re-ranking)을 위해 Cross-Encoder 모델(`klnstpr/bge-reranker-v2-m3-Q8_0-GGUF` → `bge-reranker-v2-m3-q8_0.gguf`, Q8_0 양자화)을 로드하고 `POST /v1/rerank` API를 호출하면, 쿼리(Query)와 문서(Documents) 목록 간의 관련도 점수(Relevance Score)를 정상 수신합니다.

- **리랭커 모델 카탈로그 등록**: `config/model_catalog.json`에 리랭킹 전용 모델 카테고리(`task_type: "rerank"`) 및 `--reranking` 백엔드 실행 플래그를 등록합니다.
- **API 응답 정합성**: `POST /v1/rerank` 호출 시 `{"query": "...", "documents": ["doc1", "doc2"]}` 입력에 대해 각 문서의 유사도 점수와 정렬 순위(`results[].relevance_score`, `results[].index`)를 반환합니다.
- **Nehalem CPU 검증**: 레거시 하드웨어 환경에서도 SIGILL 예외 없이 안정 구동됩니다.

**Why this priority**: 검색 정확도를 극대화하는 Cross-Encoder 리랭킹 기능을 시스템에 안착시킵니다.

**Independent Test**:
1. 리랭커 모델 지정 후 `POST /v1/rerank` 호출 시 문서별 유사도 점수 반환 검증.

---

## Functional Requirements *(mandatory)*

- **FR-001**: `config/model_catalog.json`에 임베딩(`task_type: "embedding"`) 및 리랭커(`task_type: "rerank"`) 모델 엔트리를 추가하고, `ProcessManager`가 모델의 `task_type`에 따라 **각각 독립된 `llama-server` 인스턴스를 별도 포트에 동시 기동**해야 한다. 임베딩 인스턴스는 `--embedding` 플래그, 리랭커 인스턴스는 `--reranking` 플래그를 자동 부여하며, LLM 인스턴스와 동시에 3개 프로세스가 상주한다.
- **FR-002**: `vllm_serv` 역방향 프록시(`src/api/routes/dashboard_api.py` 및 프록시 엔드포인트)는 요청 경로에 따라 적절한 백엔드 인스턴스로 라우팅해야 한다: `POST /v1/embeddings` → 임베딩 전용 인스턴스, `POST /v1/rerank` → 리랭커 전용 인스턴스, `POST /v1/chat/completions` → LLM 인스턴스로 투명하게 포워딩하고 결과를 반환해야 한다.
- **FR-003**: 1세대 코어(Nehalem i7-930) CPU 프로필(`legacy-i7-930-gtx1070`) 실행 시, 임베딩/리랭커 모델 구동 시에도 Non-AVX 바이너리를 유지하고 CUDA 오프로딩을 수행하여 SIGILL 에러 발생을 근본 차단해야 한다.
- **FR-004**: 헌법 v1.6.0 규정에 따라 임베딩 및 리랭커 API의 실체적 연동 동작을 검증하는 단위 및 통합 테스트 수트(`tests/unit/test_embedding_reranker_serving.py`)를 작성해야 한다.
- **FR-005**: 임베딩(`bge-m3-q8_0.gguf`, ~605MB) + 리랭커(`bge-reranker-v2-m3-q8_0.gguf`, ~606MB) + LLM 동시 로딩 시 각 플랫폼(GTX 1070 8GB / GTX 1080 Ti 11GB / RTX 3060 12GB)별 VRAM 초과 여부를 실측 벤치마크(`scripts/benchmark_quality.py` 확장)로 검증하고, VRAM 예산 초과 시 LLM 모델 크기 하향 권고를 제시해야 한다.
- **FR-006**: `vllm_serv` 서버 기동 시 `ProcessManager`는 LLM 인스턴스와 함께 임베딩 및 리랭커 `llama-server` 인스턴스를 자동으로 동시 기동해야 한다. 첫 번째 API 호출 시 cold-start 지연을 방지하며, 인스턴스 헬스체크 통과 후 요청 수신 가능 상태로 전환해야 한다.
- **FR-007**: 임베딩 또는 리랭커 `llama-server` 인스턴스가 비정상 종료(크래시) 시, 기존 LLM `ProcessManager`의 헬스체크/자동 재시작 패턴을 재활용하여 자동 복구해야 한다. 크래시 감지 → 자동 재시작 → 헬스체크 통과 후 서비스 복원 흐름을 일관되게 적용한다.
- **FR-008**: 임베딩(`ggml-org/bge-m3-Q8_0-GGUF`) 및 리랭커(`klnstpr/bge-reranker-v2-m3-Q8_0-GGUF`) 모델 파일은 기존 `ModelDownloader`의 HuggingFace `repo_id`/`filename` 기반 자동 다운로드 파이프라인을 재활용하여 다운로드해야 한다. 카탈로그에 `repo_id`, `filename`, `target_dir` 등록 시 LLM 모델과 동일한 흐름으로 자동 다운로드 및 배치된다.

---

## Success Criteria *(mandatory)*

- **SC-001**: `POST /v1/embeddings` API 호출 응답 및 벡터 추출 성공률 **100%**.
- **SC-002**: `POST /v1/rerank` API 호출 응답 및 관련도 점수 추출 성공률 **100%**.
- **SC-003**: 1세대 코어 Nehalem CPU 환경 실행 시 불법 명령어(`SIGILL`) 예외 발생률 **0%**.
- **SC-004**: 전 플랫폼(GTX 1070 / GTX 1080 Ti / RTX 3060)에서 임베딩+리랭커+LLM 동시 로딩 시 VRAM 예산 내 적합성 검증 통과율 **100%** (또는 초과 시 명시적 하향 권고 제시).

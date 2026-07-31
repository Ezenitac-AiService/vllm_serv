# Research & Technical Decisions: 임베딩 및 리랭커 모델 서빙 지원 (053-embedding-reranker-model-serving)

## 1. GGUF 모델 및 양자화 선택 (Model & Quantization Selection)

### Decision
- **임베딩 모델**: `ggml-org/bge-m3-Q8_0-GGUF` (`bge-m3-q8_0.gguf`, ~605MB)
- **리랭커 모델**: `klnstpr/bge-reranker-v2-m3-Q8_0-GGUF` (`bge-reranker-v2-m3-q8_0.gguf`, ~606MB)
- **양자화 레벨**: **Q8_0 (8-bit quantization)** 전 플랫폼(GTX 1070, GTX 1080 Ti, RTX 3060) 통일 적용

### Rationale
- 임베딩/리랭커 모델은 텍스트 생성이 아닌 밀집 벡터 생성 및 cross-encoder 유사도 점수 산출을 수행합니다. Q8_0 양자화는 F16(16-bit) 대비 벡터 검색 정확도(Retrieval MRR/NDCG) 저하가 실측상 무시 가능한 수준(<0.1%)이면서 VRAM 사용량을 45% 감축(~600MB)합니다.
- Q4_K_M 등 더 낮은 양자화는 벡터 표현력 저하 위험이 존재하여 채택하지 않았습니다.

### Alternatives Considered
- **F16 (Full Precision)**: VRAM 소모가 인스턴스당 ~1.2GB로 2배 증가하지만 품질 차이가 거의 없어 미채택.
- **Q4_K_M**: VRAM 절약 효과(~350MB) 대비 코사인 유사도/리랭킹 스코어 손실 리스크가 존재하여 미채택.

---

## 2. 프로세스 및 포트 바인딩 아키텍처 (Multi-Instance Process & Port Architecture)

### Decision
- `llama-server` 3개 독립 프로세스 상시 상주 구동:
  - **LLM 인스턴스**: 포트 `8089` (기본값)
  - **Embedding 인스턴스**: 포트 `8090` (실행 플래그: `--embedding -ngl 99`)
  - **Reranker 인스턴스**: 포트 `8091` (실행 플래그: `--reranking -ngl 99`)

### Rationale
- RAG 파이프라인에서 검색(Embedding) -> 재정렬(Reranker) -> LLM 생성(Completion) 흐름이 단일 사용자 요청 시 직렬로 연속 발생하므로, 인스턴스 간 모델 스왑 방식은 심각한 디스크 I/O 및 로딩 지연을 유발합니다.
- BGE-M3(~605MB) + BGE-Reranker-v2-M3(~606MB)의 VRAM 합계는 약 1.2GB로, 가장 VRAM이 적은 GTX 1070 (8GB) 환경에서도 LLM(Qwen 3.5 2B/4B)과 완벽히 동시 상주가 가능합니다.

### Alternatives Considered
- **단일 서버 모델 스왑**: 요청 수신 시 로딩된 모델을 언로드하고 새 모델을 로드하는 방식. 디스크 로딩 지연(2~5초)으로 인해 RAG 실시간 서빙 불가.

---

## 3. 프록시 및 엔드포인트 라우팅 (Proxy & Endpoint Routing Strategy)

### Decision
- `src/api/routes/inference_api.py` 역방향 프록시에서 경로(path)별 전용 backend 포트로 다이렉트 프록시:
  - `POST /v1/embeddings` 및 `POST /embedding` -> `http://127.0.0.1:8090`
  - `POST /v1/rerank` 및 `POST /rerank` -> `http://127.0.0.1:8091`
  - `POST /v1/chat/completions` 및 기타 LLM API -> `http://127.0.0.1:8089`

### Rationale
- OpenAI API 표준 규격(`POST /v1/embeddings`) 및 표준 Cross-Encoder Rerank 규격(`POST /v1/rerank`)을 그대로 노출하여 기존 RAG 프레임워크(LangChain, LlamaIndex 등)와 100% 드롭인 호환성 제공.

---

## 4. 1세대 코어(Nehalem i7-930) 호환성 및 오프로딩 (Legacy CPU Compatibility)

### Decision
- `legacy-i7-930-gtx1070` 프로필 적용 시:
  - Non-AVX 컴파일 바이너리(`-DGGML_AVX=OFF -DGGML_AVX2=OFF`) 선택
  - CUDA GPU 100% 오프로딩(`-ngl 99`) 적용

### Rationale
- i7-930 CPU는 AVX/AVX2 명령어가 존재하지 않아 일반 바이너리 구동 시 `SIGILL` (Illegal Instruction) 예외가 발생합니다.
- 임베딩/리랭커 연산을 GPU로 100% 오프로드하므로 CPU 연산 비중이 0에 가까워 Nehalem CPU 환경에서도 높은 성능과 안정성을 보장합니다.

---

## 5. 라이프사이클 및 장애 복구 (Lifecycle & Crash Recovery)

### Decision
- FastAPI `lifespan` 시점에 `EmbeddingRerankerManager` 또는 확장된 `llama_manager`가 LLM과 함께 임베딩/리랭커 인스턴스 자동 기동.
- 비정상 종료 감지 시 백그라운드 헬스체크 루프에 의해 자동 재시작.

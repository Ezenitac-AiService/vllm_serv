# Research: Real GPU Context Window Scaling, Event Loop Cleanup & Config Externalization

**Feature**: `specs/016-context-scaling-and-cleanup-fix`
**Date**: 2026-07-29

---

## Technical Decisions & Rationale

### 1. Real GPU Multi-Context Scaling Benchmark Engine (`n_ctx`: 2K~32K)

- **Decision**: `scripts/benchmark_quality.py` 내의 정적 곱셈 비례 추정(`round(vram_mb * 1.15)`)을 완전히 제거하고, `n_ctx` (2048, 4096, 8192, 16384, 32768) 스케일링 목록을 순회하며 `ProcessManager.spawn_process(model_id, n_ctx)`를 통해 실측 GPU 인퍼런스를 다단계로 구동함.
- **Rationale**: KV Cache 메모리는 어텐션 레이어 수와 비례하여 비선형적으로 증가하므로, 실제 GPU 스폰을 통해서만 VRAM Peak, TTFT(ms), TPOT(tok/s)를 정확히 정밀 측정할 수 있음.
- **Alternatives Considered**: 
  - *정적 수식 추정*: 계산은 빠르나 GGUF 모델 구조에 따른 가변 KV Cache 사용량을 반영하지 못해 OOM 오탐/미탐 발생. (기각)

---

### 2. Async Subprocess `BaseSubprocessTransport` Clean Closing

- **Decision**: `ProcessManager.stop_process()`에 `self.process._transport.close()` 안전 호출 구문을 추가하고, `await asyncio.sleep(0)` 마이크로태스크 대기를 추가하여 트랜스포트 닫힘 이벤트가 이벤트 루프 내에서 완결되도록 보장함.
- **Rationale**: `asyncio.subprocess.Process`는 종료 시 트랜스포트 닫힘 콜백이 루프에 등록되는데, 루프가 먼저 닫히면 파이썬 GC 소멸자에서 `BaseSubprocessTransport.__del__ RuntimeError: Event loop is closed` 예외를 남김. 명시적 `close()` 및 `sleep(0)`으로 예외 차단.
- **Alternatives Considered**: 
  - *파이썬 소멸자 경고 무시 (`warnings.filterwarnings`)*: 예외 메시지만 숨길 뿐 리소스 디스크립터 미수거 문제를 해결하지 못함. (기각)

---

### 3. OpenAI API `GET /v1/models` Dynamic Router Endpoint

- **Decision**: `src/api/routes/inference_api.py` 라우터에 `@router.get("/v1/models")` 전용 핸들러를 등록하여 `ConfigManager`/`ModelCatalog` 기반 전체 지원 모델 6종의 정보, 다운로드 상태, 현재 활성화 여부를 OpenAI 규격 JSON (`{"object": "list", "data": [...]}`)으로 동적 반환함.
- **Rationale**: 기존 역방향 프록시는 단일 포트(8081) `llama-server`로 조회를 전달하여 1개 로드된 모델 정보만 리턴하는 문제가 있었으나, 전용 핸들러 등록으로 LangChain/Open-WebUI 호환성 100% 확보.
- **Alternatives Considered**: 
  - *프록시 응답 후처리*: `llama-server` 응답 인터셉트 방식은 백엔드가 UNLOADED/LOADING 상태일 때 503 에러가 발생하여 모델 목록 조회가 불가능함. (기각)

---

### 4. Hardcoded Values Externalization (`config/model_catalog.json` & `config/server_config.json`)

- **Decision**:
  1. `config/model_catalog.json`: `MODEL_DOWNLOAD_CATALOG` 및 `model_presets`를 단일 JSON으로 통합 분리.
  2. `config/server_config.json`: 서버 포트(`8081`), 호스트(`127.0.0.1`), 헬스체크 타임아웃(`120s`), 커넥션 풀 크기를 분리하고 환경변수 (`LLAMA_PORT`, `LLAMA_HOST`) 오버라이드 지원.
- **Rationale**: 소스 코드 수정 없이 새로운 GGUF 모델 추가, 서버 바인딩 포트 변경, 타임아웃 조정을 자유롭게 수행 가능.
- **Alternatives Considered**: 
  - *기존 파이썬 딕셔너리 상수 유지*: 설정 변경 시 마다 파이썬 모듈 코드 수정 필요. (기각)

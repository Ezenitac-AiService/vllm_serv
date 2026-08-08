# Technical Research: 동적 모델 스위칭(Model Switching) 정상화

**Feature**: `fix-model-switching`  
**Feature Directory**: `specs/116-fix-model-switching`  

## 1. 동적 모델 핫스왑 메커니즘 분석

### 문제점 현상 (As-Is)
- 클라이언트가 `POST /v1/chat/completions` 호출 시 payload의 `"model": "gemma4-e4b"` 또는 `"model": "qwen3.5-2b"` 파라미터를 변경해 전송하더라도, `src/api/routes/inference_api.py`의 `reverse_proxy` 함수는 `model_id`를 파싱만 하고 실제 `llama_manager.load_model_with_download(model_id)`를 호출하지 않고 8089 포트(`llama-server`)로 직통 프록시함.
- 그 결과 서버 초기화 시 로드되었던 기존 모델(예: `qwen3.5-4b`)이 계속 추론을 담당하여 실제 모델 변경이 이루어지지 않음.

### 해결 방안 (To-Be)
- `src/api/routes/inference_api.py`의 `reverse_proxy` 함수 내 `POST /v1/chat/completions` 핸들러에서:
  ```python
  current_model = llama_manager.process_manager.state.model_id
  if model_id and model_id != current_model:
      # LlamaManager 락을 통해 안전하게 백엔드 모델 핫스왑 실행
      await llama_manager.load_model_with_download(model_id)
  ```
- `LlamaManager`의 `load_model_with_download`는 `async with self.lock:` 락을 통해 동시 요청 시 서빙 프로세스를 직렬화하고, 기존 프로세스를 안전하게 종료(`stop_process()`)하여 VRAM 메모리를 완전 해제한 후 신규 모델을 VRAM 100% 오프로드 로드함.

---

## 2. 기술 의사결정 및 근거 (Decisions & Rationale)

1. **결정**: `POST /v1/chat/completions` 요청 시 자동 핫스왑 지원
   - **이유**: OpenAI SDK 표준 API 인터페이스 요구사항 준수. 별도의 모델 전환 REST API를 따로 호출할 필요 없이 `model` 인자 변경만으로 투명하게 스위칭.
   - **대안 검토**: 모델 변경 API 사전 호출 의무화 ➔ 표준 OpenAI SDK와 호환되지 않으므로 기각.

2. **결정**: `asyncio.Lock` 기반 핫스왑 직렬화
   - **이유**: VRAM OOM 방지 및 동시 요청 충돌 안전성 확보. 모델 교체 중 들어오는 다른 클라이언트 요청은 락 큐에 대기하여 스위칭 완료 후 안전하게 처리됨.

3. **결정**: 샘플 스크립트 타임아웃 및 헬스체크 마진 확보
   - **이유**: `sample_04_model_switch.py` 및 `openai_04_model_switch.py`에서 가용 모델 순회 시 핫스왑 타임아웃 마진(180초)을 보장하여 VRAM 오프로드 중 연결 끊김 방지.

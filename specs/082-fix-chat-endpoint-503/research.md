# Phase 0 Research: Chat Endpoint 503 Fix & Llama Server Binary Resolution Refactoring

**Feature Branch**: `082-fix-chat-endpoint-503`

## 1. C++ llama-server 바이너리 경로 탐지 오탐지 해결 (Ollama Internal Path Exclusion)

### Decision
`ProcessManager.verify_and_build_llama_server()` 메서드에서 `shutil.which()` 및 시스템 경로 탐지 수행 시, 경로에 `/ollama/`가 포함되거나 올라마 내부 전용 바이너리 경로(`/usr/local/lib/ollama/llama-server`, `/opt/ollama/lib/ollama/llama-server` 등)는 후보 대상에서 완전히 제외합니다. 추가로, 스탠드얼론 실행 가능 여부를 검증하기 위해 바이너리가 `--help` 인자를 수신하고 정상 종료(Return Code 0 또는 1)되는지 1초 이내 타임아웃 사전 검증을 수행합니다.

### Rationale
- Ollama 내부 바이너리(`/usr/local/lib/ollama/llama-server`)는 Ollama 런타임 공유 라이브러리(`libollama.so` 등) 및 전용 환경변수가 누락된 상태로 단독 실행될 경우 SIGSEGV 또는 즉시 런타임 오류로 종료됩니다.
- 스탠드얼론 C++ `llama-server` 바이너리(로컬 `.bin/llama-server`, 커스텀 CMAKE 빌드 바이너리) 또는 Python 모듈 폴백(`llama_cpp.server`)만 채택하도록 보장해야 메인 LLM 인퍼런스 서버(포트 8089) 및 보조 서빙 프로세스가 안정적으로 가동됩니다.

### Alternatives Considered
- **Ollama 바이너리 환경변수 주입 후 사용**: Ollama 라이브러리 경로 내부 바이너리를 강제로 가동하는 방식은 vllm_serv 고유 C++ GGML/CUDA 서빙 인프라와 충돌하며, 표준 OpenAI API 서빙 파이프라인의 불확실성을 높이므로 기각함.
- **Python 모듈 폴백 전용 고정**: 시스템 바이너리 탐지를 생략하고 Python 모듈만 사용하는 방식은 로컬 C++ 소스 빌드 고속 인퍼런스 장점을 활용하지 못하므로 기각함.

---

## 2. 프로세스 포트 격리 및 보조 인스턴스 실패 영향 차단 (Process Isolation)

### Decision
`ProcessManager.cleanup_port(port)` 및 `AuxiliaryManager` 재시도 로직에서, 포트 8090(Embedding) 및 8091(Reranker) 생명주기 관리 시 메인 백엔드 인퍼런스 포트(8089) 및 `LlamaManager` 상주 프로세스에 손상을 주지 않도록 포트 단위 명시적 PID 필터링을 엄격히 고수합니다.

### Rationale
보조 모델(Reranker) 재시도 시 타 포트의 정상 구동 중인 프로세스가 오종료되는 현상을 예방하여 메인 대화 엔드포인트(/v1/chat/completions)의 503 가드가 불필요하게 트리거되는 사태를 차단합니다.

---

## 3. 실측 검증 및 회귀 테스트 전략 (Real Integration & Regression Strategy)

### Decision
- `uv run samples/sample_01_chat.py`를 통한 실제 대화 호출 실측 검증.
- `uv run scripts/diagnose_server_health.py`를 통한 전체 REST API 엔드포인트 헬스체크 검증.
- `uv run pytest tests/`를 통한 헌법 VII조 기준 프로젝트 전체 단위/통합 회귀 테스트 100% 그린 패스 달성.

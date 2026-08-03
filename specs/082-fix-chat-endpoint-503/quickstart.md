# Quickstart Guide: Chat Endpoint 503 Fix & Llama Server Binary Resolution Refactoring

**Feature Branch**: `082-fix-chat-endpoint-503`

이 가이드는 채팅 호출 엔드포인트(/v1/chat/completions) 503 Service Unavailable 오류 해결 및 `ProcessManager` C++ `llama-server` 바이너리 탐지 정제 검증 절차를 안내합니다.

## 사전 조건 (Prerequisites)

- vllm_serv 환경 세팅 완료 (`./scripts/setup.sh`)
- NVIDIA GTX 1080 Ti GPU 및 CUDA Toolkit 12.0 활성화 상태

---

## 검증 단계 (Validation Steps)

### 1. ProcessManager 바이너리 경로 탐지 단위 테스트 실행

```bash
uv run pytest tests/unit/test_process_manager_binary_path.py -v
```

**기대 결과**:
- `/usr/local/lib/ollama/llama-server` 등 올라마 내장 무효 경로는 탐지되지 않으며 `OLLAMA_LIB` 빌드 출처가 선택되지 않음을 확인.

---

### 2. 서버 구동 및 헬스 진단 실행

```bash
./start_server.sh
uv run scripts/diagnose_server_health.py
```

**기대 결과**:
- `/v1/chat/completions` 엔드포인트 상태가 `✅ OPEN / 200 OK` (또는 정상 응답)으로 출력됨.

---

### 3. OpenAI 대화 API E2E 샘플 실행

```bash
uv run samples/sample_01_chat.py
```

**기대 결과**:
```text
=================================================================
📌 01. 비전공자용 OpenAI 규격 일반 대화 API 호출 예제
=================================================================
📡 [요청 전송] http://10.0.0.41:8081/v1/chat/completions (모델: qwen3.5-4b)
✅ [응답 성공]: 안녕하세요! 무엇을 도와드릴까요?
```

---

### 4. 전체 회귀 테스트 검증 (헌법 VII조)

```bash
uv run pytest tests/ -v
```

**기대 결과**:
- 프로젝트 전체 단위 및 통합 테스트 수트 100% 그린 패스.

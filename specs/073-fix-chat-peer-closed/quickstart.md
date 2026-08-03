# Quickstart & Verification Guide: Chat Completions API 파이프라인 무결성 검증

본 가이드는 `073-fix-chat-peer-closed` 기능 구현 및 버그 수정 후, 백엔드 서버와 샘플 스크립트 간의 커넥션 دو절 없이 100% 정상 수렴하는지 실측 검증하기 위한 가이드입니다. (헌법 VI조에 따라 모든 명령어는 `uv run` 환경에서 수행합니다.)

---

## 1. 사전 준비 (Prerequisites)

- `vllm_serv` 서버 프로세스가 8081(Chat), 8090(Embedding), 8091(Reranker) 포트에 구동 중이어야 합니다.
- 서버 미구동 시 백그라운드 시작:
  ```bash
  ./start_server.sh
  ```

---

## 2. 서버 구동 및 멀티 모델 서빙 헬스 체크

서버 구동 상태 및 8081, 8090, 8091 포트 바인딩을 확인합니다.

```bash
./status_server.sh
```

**기대 결과 (Expected Outcome)**:
- 프로세스 상태: `🟢 구동 중 (RUNNING)`
- 8081 (Chat API) REST 헬스체크 `{"status": "alive"}`
- GPU VRAM 정상 오프 로딩 확인

---

## 3. 샘플 스크립트 실측 수렴 검증

### 시나리오 1: 일반 대화(Chat Completions) 호출 검증
```bash
uv run python samples/sample_01_chat.py
```
- **기대 결과**: `peer closed connection without sending complete message body` 에러 없이 모델 답변이 100% 수신되고 성공 처리 메시지 출력.

### 시나리오 2: 모델 파라미터 제어(Temperature / Stop Sequence) 검증
```bash
uv run python samples/sample_02_model_params.py
```
- **기대 결과**: Low Temperature 예제 및 Stop Sequence 예제 모두 `httpcore.RemoteProtocolError` 또는 `h11.LocalProtocolError` 없이 100% 그린으로 정상 종료.

### 시나리오 3: BGE M3 임베딩 및 Reranker 서빙 검증
```bash
uv run python samples/sample_03_embedding.py
uv run python samples/sample_04_reranking.py
```
- **기대 결과**: 8090 및 8091 포트 연결 실패 없이 임베딩 1024차원 수치 및 리랭킹 점수 반환 출력.

---

## 4. 의무적 회귀 테스트 수트 실행 (헌법 VII조)

```bash
uv run pytest
```
- **기대 결과**: 기존 시스템 및 통합 테스트 수트 전체 100% Green Pass.

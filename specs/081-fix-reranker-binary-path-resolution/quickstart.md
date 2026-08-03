# Quickstart: `llama-server` 네이티브 바이너리 경로 바인딩 검증 (`081-fix-reranker-binary-path-resolution`)

본 가이드는 Feature 081 구현 사항을 검증하는 실행 절차를 안내합니다.

## 사전 조건 (Prerequisites)

- 파이썬 가상환경 (`uv run pytest`)
- 서비스 플랫폼 환경 (`/usr/local/lib/ollama/llama-server` 또는 시스템 `llama-server` 존재)

## 검증 시나리오 (Validation Scenarios)

### 1. `ProcessManager.verify_and_build_llama_server()` 네이티브 바이너리 탐지 검증

```bash
# verify_and_build_llama_server()가 PYTHON_MODULE_FALLBACK이 아닌 네이티브 경로를 찾는지 단위 테스트
uv run pytest tests/unit/test_process_manager_binary_path.py -v
```

**기대 결과**:
- `info.build_source`가 `PYTHON_MODULE_FALLBACK`이 아닌 네이티브 바이너리 경로(예: `/usr/local/lib/ollama/llama-server`)로 반환됨

### 2. `sample_04_reranking.py` 예제 실행 및 200 OK 수신 검증

```bash
# sample_04_reranking.py 실행하여 /v1/rerank HTTP 200 OK 및 relevance_score 결과 검증
uv run python samples/sample_04_reranking.py
```

**기대 결과**:
- `❌ [Reranking 실패]` 에러 0건
- `✅ [Reranking 성공]` 메시지 및 재순위화 점수 리스트 정상 출력

### 3. 전체 수트 회귀 테스트 (Full Suite Regression Rule)

```bash
# 헌법 VII조에 따른 전체 테스트 수트 검증
uv run pytest tests/ -v
```

**기대 결과**:
- 전체 테스트 100% 통과 (Green Pass)

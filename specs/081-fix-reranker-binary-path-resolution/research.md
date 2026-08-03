# Phase 0 Research: `llama-server` 네이티브 바이너리 경로 바인딩 (`081-fix-reranker-binary-path-resolution`)

## Research Topics & Decisions

### 1. `llama-server` 네이티브 바이너리 감지 경로 확장

- **선택된 방안**: `ProcessManager.verify_and_build_llama_server()` 메서드 내부 `candidates` 탐색 경로 목록에 `/usr/local/lib/ollama/llama-server` 및 `/opt/ollama/lib/ollama/llama-server`를 최우선 후보군으로 추가합니다.
- **선택된 경로 순서**:
  1. `llama-server` (PATH 내 커스텀/시스템 설치)
  2. `llama-cpp-server` (pip/시스템 패키지 설치)
  3. `/usr/local/lib/ollama/llama-server` (서비스 플랫폼 Ollama 내장 C++ 바이너리 - 실측 성공 검증)
  4. `/opt/ollama/lib/ollama/llama-server` (보조 Ollama 경로)
  5. `/usr/local/bin/llama-server`
  6. `/usr/bin/llama-server`
- **채택 사유**: 실측 결과 서비스 플랫폼 서버에는 Ollama 패키지를 통해 최신 C++ `llama-server`가 `/usr/local/lib/ollama/llama-server`에 설치되어 있습니다. 해당 바이너리는 `--reranking --embedding` 옵션을 완벽 지원하며 `/v1/rerank` 요청 시 HTTP 200 OK와 올바른 relevance_score를 리턴합니다.
- **기용된 대안 검토**:
  - *파이썬 모듈(`llama_cpp.server`) 사용 유지*: 파이썬 모듈 버전은 `/v1/rerank` 엔드포인트를 제공하지 않아 404 에러가 발생하므로 기각.
  - *새로 CMake 컴파일*: 이미 완벽히 빌드된 GPU 가속 네이티브 바이너리가 시스템에 존재하므로 불필요한 재컴파일 기각.

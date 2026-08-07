# Technical Research: 동적 모델-KV 메모리 기반 벤치마크 탐색 구간 자동 산정 및 하드코딩 수치 전면 제거 (Dynamic Hardware-Driven Benchmark Range & Zero Magic Numbers)

**Feature**: `107-dynamic-benchmark-range`
**Date**: 2026-08-07

## 1. Dynamic High-Bound & Range Calculation Engine

### Decision
하드코딩된 상수(`16384`, `4096`, `3000MB`)를 전면 폐지하고, NVML 실시간 Free VRAM과 모델 아키텍처 명세(`max_n_ctx`)를 연동하여 100% 동적 이진 탐색 상한선(`high`) 및 초기 탐색 구간을 결정합니다.

### Rationale
- **Constitution Principle II 준수**: 임의의 문턱값(3000MB)이나 고정 상한선(16384)은 24GB/80GB 대용량 GPU 환경 및 32K/64K/128K 대형 컨텍스트 LLM 모델 환경에서 Fake Green / 왜곡을 일으키므로, 물리적 GPU 하드웨어 메모리에 맞춤 대응해야 함.
- **수식 규격**:
  $$\text{safety\_margin\_mb} = 500 + \lfloor n_{\text{ctx}} \times 0.05 \rfloor$$
  $$\text{remaining\_kv\_budget} = \text{usable\_vram} - \text{base\_vram} - \text{safety\_margin\_mb}$$
  $$\text{max\_allocatable\_n\_ctx} = \text{calculate\_max\_n\_ctx\_from\_kv\_budget}(\text{remaining\_kv\_budget})$$
  $$\text{high} = \min(\text{model\_max\_n\_ctx}, \text{max\_allocatable\_n\_ctx})$$

### Alternatives Considered
- **기존 방식 (3000MB / 16384 캡핑)**: 11GB VRAM 카드에서 `gemma4-e2b` (Base VRAM 3.7GB) 탐색 시 잔여 VRAM 3.0GB 근방으로 억제되어 `[2048, 4096]` 구간에 갇히는 치명적 결함으로 기각.

---

## 2. `./stop_server.sh` VRAM 완전 해제 & 소켓 Readiness

### Decision
`./stop_server.sh` 및 `ProcessManager` 포트 정리 시 C++ `llama-server`뿐만 아니라 Python `llama_cpp.server` 프로세스를 사살(`pgrep -f "llama_cpp.server"`)하고 8089, 8090, 8091 백엔드 TCP 소켓(`fuser -k -9 8089/tcp 8090/tcp 8091/tcp`)을 핀포인트 강제 해제합니다.

### Rationale
- `stop_server.sh`가 `llama-server` (C++ binary)만 타겟팅하고 Python 모듈(`python3 -m llama_cpp.server`) 사살을 누락하여 VRAM 3.9GB가 상주하는 현상을 완벽 방지.
- TCP TIME_WAIT 소켓 해제 수렴 검증(`socket.connect_ex` 3회 연속 비바인딩 단정)을 거쳐 EADDRINUSE 충돌 차단.

### Alternatives Considered
- **와일드카드 `pkill -9 -f python3`**: 시스템 내 타 파이썬 프로세스를 사살할 위험으로 기각. 명확한 소켓 및 모듈 패턴 타겟팅 적용.

---

## 3. NVML VRAM Settling Loop 수렴 알고리즘

### Decision
서버 프로세스 종료 후 NVML Free VRAM을 측정하기 전, 0.2초 간격으로 연속 2회 NVML 측정 차이가 10MB 이내로 안정화될 때까지 대기하는 수렴 알고리즘(Settling Loop)을 적용합니다.

### Rationale
- CUDA 드라이버 memory caching allocator의 비동기 해제 지연으로 인한 순간적 오측정을 방지하여 100% 정합성 확보.

---

## 4. 실측 인퍼런스 TPS 연산

### Decision
웜업 API 호출 시 응답 텍스트 토큰 수와 소요 시간을 바탕으로 실측 TPS를 계산하여 프로파일 기록에 적용합니다:
$$TPS = \frac{\text{completion\_tokens}}{\text{elapsed\_seconds}}$$

### Rationale
- 기존 하드코딩 `45.0 TPS` 폴백을 제거하고 실제 인퍼런스 토큰 생성 속도를 투명하게 기록.

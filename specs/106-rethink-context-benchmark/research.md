# Phase 0 Research: 컨텍스트 윈도우 벤치마킹 로직 전면 재검토 및 가용성 보장

**Feature Branch**: `106-rethink-context-benchmark`
**Date**: 2026-08-07
**Spec**: [spec.md](./spec.md)

## 1. 실시간 NVML 기반 가용 VRAM (Free VRAM) 동적 측정 및 OOM 사전 차단

### Decision
`scripts/benchmark_context_window.py` 및 `src/core/process_manager.py`에서 GPU 메모리 기준선 계산 시, 기존의 하드웨어 고정 전체 용량(`total_vram_mb - 500`) 대신 PyNVML/NVIDIA-SMI 기반 **실시간 가용 메모리(`free_vram_mb`)**를 쿼리하여 `usable_vram = max(0, free_vram_mb - 500)`으로 동적 계산한다.

### Rationale
- 백그라운드에서 `vllm_serv` 메인 서빙 서버가 구동 중이거나 타 프로세스가 VRAM을 점유하고 있는 상황에서 하드웨어 전체 용량을 가용 자원으로 오판하면 대형 모델(9B/12B 등) 벤치마크 시 CUDA OOM 또는 Linux Kernel OOM Killer(Exit Code 137)가 즉시 발동하여 서버 및 스크립트 프로세스가 집단 강제 종료된다.
- `src/core/gpu_detector.py`의 `get_nvml_vram_info()` 함수는 이미 `total_vram_mb`, `used_vram_mb`, `free_vram_mb`를 실시간 반환하는 검증된 NVML 모듈이므로 이를 벤치마크 Pre-flight Check 및 이진 탐색 초기화 시점에 직결 적용한다.

### Alternatives Considered
- **고정 수치 가감(Static Offset)**: 백그라운드 서버 기본 점유량 4.5GB를 무조건 빼고 계산하는 방식. 타 프로세스 점유 상황이나 서빙 모델 변동 시 오차가 발생하므로 기각.

---

## 2. 헬스 체크 엔드포인트 호환성 결함 해결 (`/health` vs `/v1/models`)

### Decision
`src/core/process_manager.py`의 `poll_server_health` 함수에 엔드포인트 폴백 조회 메커니즘을 적용한다.
1차로 `http://127.0.0.1:{port}/health`를 0.5s 타임아웃으로 조회하고, **HTTP 404 Not Found가 반환될 경우 즉시 2차로 `http://127.0.0.1:{port}/v1/models`를 조회**하여 HTTP 200 OK 반환 시 Readiness 성공 판정을 내린다.

### Rationale
- C++ `llama-server` 바이너리와 달리 Python `llama_cpp.server` 패키지는 `/health` 경로를 구현하고 있지 않아 404 Not Found를 반환한다.
- 기존 `poll_server_health`는 200 OK만을 성공으로 간주하여 `llama_cpp.server` 구동 환경에서 15~60초 동안 폴링 타임아웃이 발생하고 프로세스를 강제 종료(SIGTERM -15)시킨 후 `is_supported: false`로 오진했다.
- `scripts/start_server.sh` (라인 86)에서도 이미 `/health` 실패 시 `/v1/models`를 폴백 검증하는 파리티 패턴을 사용하고 있으므로 이를 ProcessManager 파이썬 로직에도 동일하게 적용한다.

### Alternatives Considered
- **404 응답을 무조건 성공으로 처리**: 포트가 응답하기만 하면 404라도 Ready로 보는 방식. 실제 모델 로딩 실패 시의 404와 구분이 모호해질 수 있으므로 기각.

---

## 3. 서브프로세스 핀포인트 격리 및 와일드카드 `pkill` 사살 방지

### Decision
`ProcessManager.force_kill_zombie_llama_servers()` 및 `register_process_cleanup_hooks()`의 cleanup 동작 방식을 전면 개편한다.
- 와일드카드 커맨드인 `pkill -9 -f llama-server` 호출을 전면 제거한다.
- `ProcessManager` 인스턴스가 관리하는 **자신의 바인딩 포트(기본 8081)** 및 **등록된 자식 PID**만을 타겟으로 포트 소켓 정리(`fuser -k -9 8081/tcp`) 및 PID 정밀 kill을 수행한다.

### Rationale
- `pkill -9 -f llama-server`는 커맨드라인에 `llama-server` 또는 `llama_cpp.server`가 포함된 모든 프로세스를 와일드카드로 사살하기 때문에, 벤치마크 스크립트 실행/종료 시 메인 서빙 서버(포트 8089, 8090, 8091) 프로세스까지 함께 사살시키는 치명적 문제가 발생했다.
- 벤치마크 프로세스와 상주 서빙 서버 프로세스의 포트 및 PID 격리를 보장함으로써 벤치마크 수행 중에도 인프라 안정성을 100% 유지할 수 있다.

### Alternatives Considered
- **PID 파일 기반 정리**: PID 파일이 누락되거나 부모가 대등하게 죽을 경우 잔여 zombie가 남을 수 있으므로 PID + 포트 기반 `fuser/lsof` 이중 핀포인트 정리를 적용.

---

## 4. 비파괴적(Non-destructive) 프로파일 보존 및 원자적 갱신

### Decision
`scripts/benchmark_context_window.py`에서 벤치마크 평가 중 예외나 OOM, 타임아웃이 발생할 때 기존에 존재하던 검증 프로파일 항목을 덮어쓰지 않고 보존한다.
- `_record_unsupported_fallback_profile(model_name, reason)` 실행 시, 해당 모델의 기존 프로파일에 `is_supported: true` 및 유효한 `max_context_length`가 이미 존재하는 경우 기존 항목을 유지하고 실패 로그만 출력한다.
- 강제 전체 재측정 및 덮어쓰기를 원하는 경우 CLI 인자 `--force-overwrite-profiles`가 명시되었을 때만 파괴적 갱신을 허용한다.

### Rationale
- 기존에 정상 측정된 유효한 프로파일(예: Qwen 9B 12K, Gemma 2B 15K)이 일시적인 환경 이슈(타 프로세스 메모리 점유, 일시적 타임아웃)로 인해 일률적인 `is_supported: false, n_ctx: 2048` 더미 데이터로 전면 파괴되는 현상을 방지한다.
- vllm_serv 헌장 원칙 V(비파괴적 문서/데이터 수정 원칙)를 소프트웨어 실행 상태 프로파일 관리에도 적용한다.

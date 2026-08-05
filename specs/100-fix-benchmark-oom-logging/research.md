# Phase 0 Research: 벤치마크 OOM 진단 및 실시간 로그 영구 저장 개선 (100-fix-benchmark-oom-logging)

## Overview

본 연구 문서에서는 `./setup.sh --force-benchmark` 및 `scripts/benchmark_context_window.py` 실행 시 발생하는 서브프로세스 로그 유실, 10초 고정 헬스체크 타임아웃으로 인한 이진 탐색 오탐, 하드코딩된 정적 VRAM/모델 룰셋 문제를 해결하기 위한 기술적 선택과 근거를 다룹니다.

---

## Research Decisions

### Decision 1: 실시간 비동기 백엔드 로그 스트리밍 및 안전 파일 플러시 (Safe Log Drain)

- **선택된 기술**: `asyncio.StreamReader` 기반 라인 스트리밍 + 파일 핸들 쓰기(`flush()` 포함) 및 프로세스 강제 중단시 `try...finally` 플러시 보장 메커니즘.
- **배경 및 논리적 근거**:
  - 기존 코드에서는 `ProcessManager.spawn_process()` 실행 시 `_log_drain_task`가 비동기 태스크로 시작되었으나, `stop_process()` 호출 시 `self._log_drain_task.cancel()`이 먼저 수행되어 버퍼에 남아 있는 `llama-server`의 stdout/stderr 출력이 파일에 쓰여지지 않고 모두 버려졌습니다.
  - 개선 방식: `_log_drain_task` 캔슬 전 태스크를 정상 수거(join/wait)하거나, `_drain_stdout` 내부에서 `logs/benchmark.log` 파일 핸들에 실시간 쓰기 및 `flush()`를 적용합니다. 비정상 종료(exit code != 0) 또는 타임아웃 발생 시 최근 20줄의 버퍼(`collections.deque(maxlen=50)`)를 `logs/error.log` 및 `logs/benchmark.log`에 원자적으로 기록합니다.
- **고려된 대안**:
  - 대안 A: 서브프로세스의 stdout/stderr를 직접 파일 디스크립터(file descriptor)로 리다이렉트 (`stdout=open('logs/benchmark.log', 'a')`).
  - 기각 사유: VRAM 오프로딩 실시간 파싱(`parse_vram_offload_log`) 및 에러 버퍼 캡처 기능과 결합할 수 없으므로 `StreamReader` 드레인 루프 유지가 필수적임.

---

### Decision 2: 동적 데이터 기반 VRAM 예산 산정 및 이진 탐색 초기 구간 산출

- **선택된 기술**: GGUF 가중치 파일 용량(`os.path.getsize(model_path)`) + NVML 가용 VRAM(`get_nvml_vram_info()`) 기반 동적 KV 캐시 계산 및 이진 탐색 시작점 결정.
- **배경 및 논리적 근거**:
  - 기존 코드의 `ctx_vram_mb = 2600 + int(mid * 0.4)` 및 `vram_est_mb = 6000` 고정 기본값, `"2b" in model_name` 문자열 검사는 하드웨어 및 모델 카탈로그 변경 시 동작이 마비되거나 대형 모델이 사전 차단(CUDA OOM Risk)되는 원인이 되었습니다.
  - 개선 방식:
    1. Base Model VRAM = GGUF 파일 크기(MB) * 1.1 (CUDA 컨텍스트 및 버퍼 오버헤드).
    2. Available VRAM = NVML 실측 총 VRAM - 실측 사용 중인 VRAM.
    3. Remaining KV Budget = Available VRAM - Base Model VRAM.
    4. 남은 KV 예산에 기초하여 안전한 이진 탐색 시작 컨텍스트(`mid`)를 산출 (예: KV 예산이 적을 경우 2048부터 탐색 개시).
- **고려된 대안**:
  - 대안 A: 모델 카탈로그에 VRAM 요구량을 수동 기재.
  - 기각 사유: 양자화 레벨(Q4_K_M, Q8_0 등) 변경이나 파일 수정 시 매번 카탈로그를 정적 갱신해야 하므로 헌장 원칙에 위배됨.

---

### Decision 3: 모델 규모별 동적 헬스체크 Polling Timeout (10s -> 최대 30s)

- **선택된 기술**: `poll_server_health` 타임아웃을 GGUF 파일 용량 및 GPU 호환성에 따라 15s~30s 동적 확장.
- **배경 및 논리적 근거**:
  - GTX 1080 Ti 등 PCIe Gen3 환경에서 4B~12B GGUF 모델 로딩 및 CUDA 버퍼 할당에는 12~25초가 소요됩니다. 기존 10초 타임아웃은 실제 정상 동작 가능한 인스턴스를 무조건 실패("timed out")로 오탐하게 만들었습니다.
  - 개선 방식: GGUF 용량이 3GB 이상이거나 백엔드 로딩 중일 경우 헬스체크 타임아웃을 최대 30초까지 확장 대기합니다.
- **고려된 대안**:
  - 대안 A: 60초 이상의 고정 장기 타임아웃.
  - 기각 사유: 실제로 로딩 크래시가 발생한 경우 전체 벤치마크 소요 시간이 지나치게 길어지므로 0.2초 간격 polling과 30초 상한선이 가장 적합함.

---

### Decision 4: 파이프라인 전반의 정적 하드코딩 제거 (Dynamic Provisioning & Profile Matching)

- **선택된 기술**: `config/server_config.json` 및 `config/model_catalog.json` 기반 동적 서빙 모델 추출 및 `cpu_detector` 프로파일 기반 휠 경로 동적 스캔.
- **배경 및 논리적 근거**:
  - `ensure_models.py`에 하드코딩된 `REQUIRED_MODELS = ["qwen3.5-4b", "bge-m3", "bge-reranker-v2-m3"]` 및 `setup.sh`의 `"legacy-i7-930"` 문자열 조건문을 제거합니다.
  - `ensure_models.py`는 `server_config.json`과 `model_catalog.json`에서 현재 등록된 서빙 모델 목록을 조회하여 동적 점검하며, `setup.sh`는 `cpu_detector`가 감지한 프로파일 명칭(`MATCHED_PROFILE`)에 따라 `wheels/<MATCHED_PROFILE>/` 디렉토리를 동적 탐색합니다.

---

## Summary of Resolved Clarifications

| 영역 | 미결 사항 (Unknown) | 최종 연구 결정 (Resolution) |
| :--- | :--- | :--- |
| **Log Streaming** | 서브프로세스 캔슬 시 로그 유실 | `_drain_stdout` 루프에서 실시간 플러시 및 에러 발생 시 20줄 덤프 파일 영구 보존 |
| **VRAM Estimation** | 정적 수식 및 사전 차단 오탐 | GGUF 파일 용량 + NVML 가용 메모리 기반 동적 KV 캐시 계산 및 이진 탐색 시작점 산출 |
| **Polling Timeout** | 10초 고정 대기로 인한 로딩 실패 | 모델 용량에 비례한 동적 타임아웃 (최대 30초) 적용 |
| **Dynamic Provisioning**| `REQUIRED_MODELS` 하드코딩 | `server_config.json` & `model_catalog.json` 파일 기반 동적 로딩 |

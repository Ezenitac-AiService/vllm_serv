# Implementation Plan: 벤치마크 OOM 진단 및 실시간 로그 영구 저장 개선 (100-fix-benchmark-oom-logging)

**Branch**: `100-fix-benchmark-oom-logging` | **Date**: 2026-08-05 | **Spec**: [`spec.md`](file:///home/dev/storage/vllm_serv/specs/100-fix-benchmark-oom-logging/spec.md)

**Input**: Feature specification from `/specs/100-fix-benchmark-oom-logging/spec.md`

## Summary

`./setup.sh --force-benchmark` 실행 중 발생하던 서브프로세스(`llama-server`) 로그 유실, 10초 고정 헬스체크 타임아웃 오탐, 정적 VRAM 계산식 및 하드코딩된 예외 로직 5종을 완전히 철거합니다. 다중 페르소나 분석에서 도출된 4대 SRE/런타임 보완점(Exit Code 137 커널 OOM 감지, 500MB VRAM 안전 버퍼, 10MB 디스크 로그 로테이션, 파이프 EOF 안전 플러시) 및 Hugging Face 다운로드 완납 또는 스마트 스킵(Smart Skip) 시 `model_catalog.json` 실측 메타데이터 원자적 자율 동기화(Reconciliation) 메커니즘(`FR-012`)을 수록하여 100% 동적 메타데이터/실측 기반 인프라를 완성합니다.

---

## Technical Context & Deep Architecture

### 1. Language & Ecosystem
- **Runtime**: Python 3.11 (Virtualenv managed via `uv`)
- **Shell Pipeline**: Bash 5.x (`scripts/setup.sh`)
- **Dependencies**: `httpx`, `pydantic` (v2), `pynvml` (`nvidia-ml-py`), `asyncio`, `llama-cpp-python` (`llama-server`)

### 2. Deep Component Technical Design

#### A. ProcessManager Safe Log Drain & Exit Code 137 Crash Dump (`src/core/process_manager.py`)
- **`_drain_stdout(self, stream: asyncio.StreamReader)`**:
  - `logs/benchmark.log` 파일 오픈 시 10MB 초과 검사 및 `logs/benchmark.log.old` 로테이션 수행 후 append 모드로 오픈.
  - `stream.readline()` 루프 실행 시 각 라인을 즉시 쓰기 후 `flush()` 호출하여 실시간 스트리밍 보장.
  - 슬라이딩 에러 버퍼 `recent_lines = collections.deque(maxlen=50)` 유지.
  - 서브프로세스 종료 시 `self.process.returncode != 0`인 경우:
    - `returncode in (137, -9)`일 때: "KERNEL_OOM_KILLER_EXIT_137 (Process killed by Linux Kernel OOM Killer)" 헤더 문구 삽입.
    - 최근 20줄 덤프를 `logs/error.log` 및 `logs/benchmark.log`에 타임스탬프와 함께 원자적 서식화 쓰기.
- **`stop_process()` Graceful Drain & Pipe EOF Feed**:
  - `self._log_drain_task` 캔슬 전에 파이프 트랜스포트에 `feed_eof()`를 전달하고 `await asyncio.gather(self._log_drain_task, return_exceptions=True)`로 파이프 잔여물이 플러시될 때까지 최대 2초 대기.

#### B. Dynamic Data-Driven VRAM Budget Engine & 500MB Safety Cushion (`src/core/process_manager.py` & `scripts/benchmark_context_window.py`)
- **Base VRAM Calculation Algorithm**:
  $$\text{Base VRAM (MB)} = \frac{\text{os.path.getsize(model\_path)}}{1024 \times 1024} \times 1.15$$
- **KV Cache Budget & 500MB Safety Cushion**:
  $$\text{Usable VRAM (MB)} = \text{NVML Available VRAM} - 500\text{MB}$$
  $$\text{Remaining KV Budget (MB)} = \text{Usable VRAM} - \text{Base VRAM}$$
  - 남은 KV 예산이 3000MB 미만일 경우 이진 탐색 초기 `low=2048`, `high=4096`부터 개시하여 대형 모델에 대한 Pre-flight `CUDA OOM Risk` 차단오탐 원천 방지.
  - `2600 + int(mid * 0.4)` 및 `vram_est_mb = 6000` 정적 수식 전면 삭제.

#### C. Dynamic Health Check Polling Timeout
- **Scaling Formula**:
  $$\text{Timeout (seconds)} = \min\left(30.0, \max\left(15.0, 10.0 + \frac{\text{GGUF Size (MB)}}{500}\right)\right)$$
  - 1GB 미만 경량 모델: 15초 타임아웃
  - 4GB~9GB 대형 모델: 20초~30초 동적 확장 대기.

#### D. Dynamic Provisioning, Smart Skip Reconciliation & Wheel Matching (`scripts/ensure_models.py` & `src/core/model_downloader.py`)
- **`ensure_models.py` & `ModelDownloader`**:
  - `REQUIRED_MODELS` 정적 배열 철거. `server_config.json`과 `model_catalog.json`에서 동적 추출.
  - Hugging Face/ModelScope 가중치 다운로드 완납 시점뿐만 아니라, 이미 파일이 로컬에 존재하여 다운로드를 스마트 스킵(Smart Skip)하는 시점에도 `os.path.getsize(model_path)`를 측정하여 `config/model_catalog.json` 내 해당 모델 항목의 `exact_bytes` 및 `size_gb` 필드에 원자적으로 Write-back 동기화(Reconciliation) (`FR-012`).
- **`setup.sh` Wheel Scan & Rotation**:
  - `MATCHED_PROFILE` 변수값(예: `pascal-avx2-gtx1080ti`) 기반 `wheels/${MATCHED_PROFILE}/*.whl` 동적 스캔.
  - 벤치마크 개시 시 `logs/benchmark.log`가 10MB 초과일 경우 `logs/benchmark.log.old`로 로테이션.

---

## Constitution Check

*GATE: All principles validated and 100% compliant.*

- [x] 계획서가 한국어로 작성되었는가? (언어 정책)
- [x] 테스트 코드 작성 계획이 포함되어 있는가? (테스트 필수 원칙)
- [x] 목업은 유료/제한 API로 엄격히 제한하고 실물 시스템/소켓/OS 인자 및 실제 호출 플래그(REAL_API_CALL=1) 기반 실측 검증 계획이 포함되어 있는가? (실체적 테스트 및 수렴 검증 원칙)
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (종료 조건 명확화 원칙)
- [x] 비파괴적 문서 수정 원칙을 준수하는가? (비파괴적 문서 수정 원칙)
- [x] uv 패키지 매니저 및 가상환경 격리 표준(uv run)을 준수하는가? (uv 패키지 및 환경 관리 원칙)
- [x] 전체 회귀 테스트 수트 및 Playwright 기반 E2E 브라우저 실측 검증 계획이 포함되어 있는가? (의무적 회귀 테스트 및 브라우저 E2E 검증 원칙)

---

## Project Structure

### Documentation (this feature)

```text
specs/100-fix-benchmark-oom-logging/
├── plan.md              # Implementation Plan (Self)
├── research.md          # Phase 0 Research Decisions
├── data-model.md        # Phase 1 Data Models & Schemas
├── quickstart.md        # Phase 1 Validation & Quickstart Guide
├── contracts/           # Phase 1 Interface Contracts
│   └── benchmark-cli-contract.md
└── tasks.md             # Detailed Execution Task List
```

### Source Code Architecture

```text
scripts/
├── benchmark_context_window.py   # 동적 VRAM 예산(500MB 안전 버퍼), 하드코딩 철거, failure_reason(Exit 137 포함) 기록
├── ensure_models.py              # server_config/model_catalog 기반 동적 필수 모델 다운로드 및 Smart Skip 시 model_catalog.json 자율 동기화(FR-012)
└── setup.sh                      # MATCHED_PROFILE 디렉토리 기반 동적 휠 패치 및 10MB 로그 로테이션

src/
└── core/
    ├── model_downloader.py       # GGUF 다운로드/스마트스킵 후 model_catalog.json exact_bytes/size_gb Write-Back Reconciliation
    └── process_manager.py        # StreamReader 실시간 파일 플러시, 20줄 콘솔 덤프(Exit 137 캡처), 동적 타임아웃, 파이프 EOF 안전 수거

logs/
├── benchmark.log                 # 벤치마크 백엔드 실시간 출력이 플러시되어 기록되는 로그 (10MB 로테이션)
├── benchmark.log.old             # 로테이션 백업 파일
└── error.log                     # 비정상 종료/타임아웃 시 최근 20줄 콘솔 덤프 보존

tests/
└── unit/
    ├── test_process_manager_logging.py       # US1 & US4: 실시간 플러시, Exit 137 캡처 및 로그 로테이션 테스트
    ├── test_dynamic_vram_calculation.py     # US2: 500MB 안전 버퍼 동적 VRAM 및 30s 타임아웃 테스트
    └── test_model_profiles_persistence.py   # US3: failure_reason JSON 저장 및 카탈로그 스마트스킵 동기화(FR-012) 테스트
```

---

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | 모든 헌장 원칙 및 아키텍처 규격을 100% 준수함 |

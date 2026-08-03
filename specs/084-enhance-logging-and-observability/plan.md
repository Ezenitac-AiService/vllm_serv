# Implementation Plan: 서버 진단 로그 강화 및 포트 점유(Errno 98) 정밀 추적

**User Specs Reference**: `/specs/084-enhance-logging-and-observability/`  
**Target Branch**: `main` / `084-enhance-logging-and-observability`  

---

## 1. Technical Context & Scope

- **Affected Components**:
  - `scripts/stop_server.sh` (포트 8081, 8082, 8089, 8090, 8091 및 `llama_cpp.server` 정리)
  - `src/core/process_manager.py` (프로세스 스폰 전 `_cleanup_zombie_on_port` 및 스택 트레이스 캡처)
  - `src/api/middleware/client_access_logger.py` (`logs/error.log` 다중 행 예외 트레이스 로깅)
  - `src/api/routes/inference_api.py` (503/500 에러 발생 시 세부 원인 로깅)
  - `scripts/diagnose_server_health.py` (503 실패 시 세부 사유 노출)

---

## 2. Constitution Check

- **Principle I (Korean Language)**: All design docs, comments, logs, and summaries MUST be written in Korean. -> PASS
- **Principle II & III (Zero Mock & Real Integration)**: Real port socket checking (`lsof`/`fuser`), real traceback capturing, real daemon execution. -> PASS
- **Principle VII (Full Regression Testing)**: Run full test suite regression after implementation. -> PASS

---

## 3. Planned Touch-Points & Work Phases

### Phase 0: Research & Requirements (Complete)
- Created `research.md` (Errno 98, python module process detection, multi-line traceback logging).

### Phase 1: Design & Contracts (Complete)
- Created `data-model.md`, `contracts/logging-observability-contract.json`, `quickstart.md`.

### Phase 2: Implementation (To be generated via `/speckit-tasks`)
- Task 1: `scripts/stop_server.sh` 포트 및 `llama_cpp.server` 파이썬 모듈 전수 정리 로직 추가
- Task 2: `src/core/process_manager.py` 스폰 전 포트 릴리스 선제 정돈 및 stderr 캡처 강화
- Task 3: `src/api/middleware/client_access_logger.py` 및 `inference_api.py` 503/예외 traceback 기록 추가
- Task 4: `scripts/diagnose_server_health.py` 503 원인 메시지 노출 개선
- Task 5: 단위 테스트 작성 및 E2E 실측 검증 (`diagnose_server_health.py`, `sample_01_chat.py`)

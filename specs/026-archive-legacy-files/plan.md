# Implementation Plan - 코드베이스 리팩토링 및 레거시 파일 .legacy 디렉토리 격리 정돈 (026-archive-legacy-files)

**User Spec**: [spec.md](file:///home/dev/storage/vllm_serv/specs/026-archive-legacy-files/spec.md)  
**Research**: [research.md](file:///home/dev/storage/vllm_serv/specs/026-archive-legacy-files/research.md)  
**Data Model**: [data-model.md](file:///home/dev/storage/vllm_serv/specs/026-archive-legacy-files/data-model.md)  
**Contracts**: [contracts/legacy-archive-contract.json](file:///home/dev/storage/vllm_serv/specs/026-archive-legacy-files/contracts/legacy-archive-contract.json)  
**Quickstart Guide**: [quickstart.md](file:///home/dev/storage/vllm_serv/specs/026-archive-legacy-files/quickstart.md)

---

## Technical Context

- **System Context**: Python 3.12 / FastAPI / vLLM / llama.cpp GPU Serving Server
- **Core Architecture**: `src/api/` (FastAPI), `src/core/` (LlamaManager, ConfigManager, NetworkDetector, FirewallManager), `scripts/` (Operational Scripts), `tests/` (Unit & Integration Tests)
- **Primary Objective**:
  1. 프로젝트 루트의 불필요한 레거시/임시 파일들(`ATEAM_ExtractionItem.py`, `BTEAM_ExtractionItem.py`, `get-pip.py`, `benchmark_results.json`, 루트 1줄 셸 스텁)을 `.legacy/` 디렉토리로 이동하여 아카이빙
  2. `src/` 및 `scripts/` 디렉토리 내 사용되지 않는 임포트, 미사용 코드(Dead Code), 중복 유틸리티 정돈 및 모듈화 리팩토링
  3. 전체 Pytest 수트 100% 회귀 방지 통과

---

## Constitution Check

- [x] **Principle I: 언어 정책 (Language Policy)**: 모든 문서, 태스크 설명 및 커밋 메시지는 한국어/영어 규정을 엄격히 준수합니다.
- [x] **Principle II: 테스트 주도 개발 및 품질 보증 (TDD & Quality Assurance)**: 리팩토링 후 `uv run pytest tests/`로 100% 통과 검증.
- [x] **Principle III: 종료 조건 명확화 (Definition of Done)**: 명세서의 DoD-001 ~ DoD-004 항목 충족.
- [x] **Principle IV: 비파괴적 문서 및 코드 관리 (Non-Destructive Management)**: 삭제 대신 `.legacy/` 아카이빙 처리.
- [x] **Principle V: uv 패키지/환경 관리 (Package & Env Isolation)**: `uv` 가상환경 기준 구동.

---

## Technical Decisions & Touch-Points

### Touch-Points & Target Files

1. **New Directory**:
   - `.legacy/`

2. **Files to Archive (`.legacy/`로 이동)**:
   - `ATEAM_ExtractionItem.py` -> `.legacy/ATEAM_ExtractionItem.py`
   - `BTEAM_ExtractionItem.py` -> `.legacy/BTEAM_ExtractionItem.py`
   - `get-pip.py` -> `.legacy/get-pip.py`
   - `benchmark_results.json` -> `.legacy/benchmark_results.json`
   - `make_seed_pack.sh` -> `.legacy/make_seed_pack.sh`
   - `setup.sh` -> `.legacy/setup.sh`
   - `start_server.sh` -> `.legacy/start_server.sh`
   - `status_server.sh` -> `.legacy/status_server.sh`
   - `stop_server.sh` -> `.legacy/stop_server.sh`

3. **Files to Refactor & Clean Up**:
   - `src/core/config_manager.py` (Unused imports / redundant helper audit)
   - `src/core/process_manager.py` (Clean up unused variables and redundant subprocess helpers)
   - `src/api/server.py` & `src/api/routes/` (Clean up unused route imports)
   - `scripts/` (Ensure operation scripts are clean and aligned with `.legacy/` isolation)

4. **Test Files**:
   - `tests/unit/test_architecture_modularity.py` (Add test for `.legacy/` archiving & clean root verification)

---

## Planning Phases

### Phase 0: Research & Scoping

- Review all files in repo root and `src/` to finalize legacy list and refactoring targets.
- Create `research.md`.

### Phase 1: Design Artifacts

- Create `data-model.md`, `contracts/legacy-archive-contract.json`, `quickstart.md`.
- Finalize `plan.md`.

### Phase 2: Task Generation (`/speckit-tasks`)

- Break down work into atomic, dependency-ordered tasks in `tasks.md`.

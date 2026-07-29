# Implementation Plan: 자동 모델 다운로드 및 동적 서빙 프로세스 실행 관리 (Automatic Model Download & Dynamic Serving Automation)

**Branch**: `009-auto-model-download-serving` | **Date**: 2026-07-29 | **Spec**: [spec.md](file:///home/dev/storage/vllm_serv/specs/009-auto-model-download-serving/spec.md)

**Input**: Feature specification from `/specs/009-auto-model-download-serving/spec.md`

## Summary

본 계획은 HuggingFace Hub 기반 GGUF 가중치 및 CLIP 프로젝터 파일의 **자동 다운로드 모듈 (`src/core/model_downloader.py`)** 구현, **동적 서빙 프로세스 스위칭 관리 (`src/core/process_manager.py`)**, 그리고 단 한 번의 명령 구동으로 [자동 다운로드 ➔ 실측 프로세스 로드 ➔ nvtop 실측 부하 발생 ➔ 품질 평가 ➔ 보고서 갱신]을 완수하는 **원스톱 실측 벤치마크 파이프라인 (`scripts/benchmark_quality.py`)** 구현을 목표로 합니다.

---

## Technical Context

- **Language/Version**: Python 3.10+ (uv 환경)
- **Primary Dependencies**: `huggingface_hub`, `httpx`, `pydantic`, `pytest`, `asyncio`
- **Storage**: `models/` 디렉토리 하위 모델별 GGUF 파일 저장
- **Testing**: `pytest` (`uv run pytest`)
- **Target Platform**: Linux x86_64, NVIDIA GTX 1080 Ti (11GB VRAM)
- **Project Type**: Core Module & CLI Automation Runner
- **Performance Goals**:
  - 서빙 프로세스 동적 스위칭 및 포트 개설 준비 시간 < 5.0초 (다운로드 완료 기준)
  - 가중치 미존재 시 자동 다운로드 및 무결성 검증 100% 완수

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] 계획서가 한국어로 작성되었는가? (Principle I: 언어 정책)
- [x] 테스트 코드 작성 계획이 포함되어 있는가? (Principle II: TDD 및 품질 보증 원칙)
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (Principle III: 종료 조건 명확화 원칙)
- [x] 기존 아티팩트 및 명세의 파괴적 편집을 금지하고 온전히 보존 및 확장하는가? (Principle IV: 비파괴적 문서 수정 원칙)

---

## Project Structure & Touch-Points

### Documentation (this feature)

```text
specs/009-auto-model-download-serving/
├── spec.md                     # Feature specification
├── plan.md                     # This implementation plan
├── research.md                 # Phase 0 output
├── data-model.md               # Phase 1 output
├── quickstart.md               # Phase 1 output
└── checklists/
    └── requirements.md         # Specification quality checklist
```

### Source Code & Test Layout

```text
src/
├── core/
│   ├── model_downloader.py     # [NEW] HuggingFace GGUF 및 mmproj 자동 다운로더 모듈
│   ├── process_manager.py      # [UPDATE] llama-server 프로세스 동적 스위칭 & 헬스체크
│   └── llama_manager.py        # [UPDATE] 모델 동적 로드/언로드 코디네이터
scripts/
└── benchmark_quality.py        # [UPDATE] 원스톱 자동 다운로드 + 실측 연동 벤치마크 루프

tests/
├── unit/
│   └── test_model_downloader.py # [NEW] 모델 다운로더 단위 테스트
└── integration/
    └── test_serving_switch.py   # [NEW] 서빙 프로세스 동적 스위칭 통합 테스트
```

---

## Execution Phases & Milestones

### Phase 0: Research & Architecture Decisions (Completed)
- `research.md` 작성 완료 (`huggingface_hub`, `SIGTERM`/`SIGKILL` 스위칭, 원스톱 루프)

### Phase 1: Data Model & Contracts (Completed)
- `data-model.md`, `quickstart.md` 작성 완료 (`ModelDownloadTask`, `ServerProcessState`)

### Phase 2: Implementation & Task Generation (Next Step: `/speckit-tasks`)
- `src/core/model_downloader.py` 구현
- `src/core/process_manager.py` 동적 서빙 프로세스 스위칭 & HTTP 헬스체크 구현
- `tests/unit/test_model_downloader.py` 단위 테스트 작성
- `scripts/benchmark_quality.py` 원스톱 다운로드+실측 벤치마크 파이프라인 수록
- 전체 pytest 통과 및 quickstart 검증

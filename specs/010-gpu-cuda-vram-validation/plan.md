# Implementation Plan: GPU/CUDA 하드웨어 가속 인식, VRAM 로드 검증 및 예외 처리 (GPU CUDA Acceleration & VRAM Load Validation)

**Branch**: `010-gpu-cuda-vram-validation` | **Date**: 2026-07-29 | **Spec**: [spec.md](file:///home/dev/storage/vllm_serv/specs/010-gpu-cuda-vram-validation/spec.md)

**Input**: Feature specification from `/specs/010-gpu-cuda-vram-validation/spec.md`

## Summary

본 구현 계획은 서빙 서버 및 벤치마크 파이프라인 구동 시 **NVIDIA GPU 및 CUDA 백엔드 존재 여부를 자동으로 사전 검증하는 하드웨어 감지기 (`src/core/gpu_detector.py`)** 구현, **100% GPU VRAM 레이어 오프로딩 및 실시간 로드 검증 (`src/core/process_manager.py`)**, **CPU-only 전용 바이너리 시도 시 사전 차단 예외 처리 (`GpuAccelerationError`, `VramOverflowError`)**, 그리고 코어/평가/스크립트 전반에 걸친 **더미/목업 데이터 및 미사용 임포트 전수 정제**를 목표로 합니다.

---

## Technical Context

- **Language/Version**: Python 3.12 (uv 환경)
- **Primary Dependencies**: `llama-cpp-python` (CUDA `cu124`), `pydantic` v2, `httpx`, `pytest`, `asyncio`
- **Hardware/Platform**: Linux x86_64, NVIDIA GeForce GTX 1080 Ti (11GB VRAM, CUDA 13.0 / Driver 580.173.02)
- **Target Exception Classes**: `GpuAccelerationError`, `VramOverflowError`
- **Testing**: `pytest` (`uv run pytest`)
- **Performance Goals**:
  - GPU 100% VRAM 오프로딩을 통한 TPOT > 30 tok/s 달성
  - CPU-only 바이너리 실행 시 0.1초 이내 즉각 차단 및 예외 반환

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
specs/010-gpu-cuda-vram-validation/
├── spec.md                     # Feature specification
├── plan.md                     # This implementation plan
├── research.md                 # Phase 0 output
├── data-model.md               # Phase 1 output
├── quickstart.md               # Phase 1 output
├── contracts/
│   └── gpu_validation_api.md   # GPU Validation & Status API contract
└── checklists/
    └── requirements.md         # Specification quality checklist
```

### Source Code & Test Layout

```text
src/
├── core/
│   ├── gpu_detector.py         # [NEW] GPU/CUDA 사전 검증 모듈 및 예외 정의
│   ├── process_manager.py      # [UPDATE] VRAM 100% 오프로드 검증 & CPU 차단 로직
│   └── llama_manager.py        # [UPDATE] GPU 헬스체크 및 오프로드 상태 브로드캐스팅
scripts/
└── benchmark_quality.py        # [UPDATE] GPU 오프로드 메타데이터 포함 및 목업 정제

tests/
├── unit/
│   ├── test_gpu_detector.py    # [NEW] GPU/CUDA 검증기 단위 테스트
│   └── test_model_downloader.py # [UPDATE] 카탈로그 및 경로 단정문 검증
└── integration/
    └── test_gpu_validation.py  # [NEW] CPU 차단 및 VRAM 오프로드 검증 통합 테스트
```

---

## Execution Phases & Milestones

### Phase 0: Research & Architecture Decisions (Completed)
- `research.md` 작성 완료 (GPU/CUDA 3단계 검증, VRAM 100% 오프로드 파싱, 예외 체계)

### Phase 1: Data Model & Contracts (Completed)
- `data-model.md`, `contracts/gpu_validation_api.md`, `quickstart.md` 작성 완료 (`GpuDeviceInfo`, `VramOffloadStatus`, `GpuAccelerationError`)

### Phase 2: Task Generation (Next Step: `/speckit-tasks`)
- `src/core/gpu_detector.py` GPU/CUDA 사전 검증 모듈 구현
- `src/core/process_manager.py` VRAM 100% 오프로드 검증 & CPU 차단 로직 추가
- `scripts/benchmark_quality.py` 및 코어 모듈 내 하드코딩된 더미/목업 전수 정제
- `tests/unit/test_gpu_detector.py` 및 `tests/integration/test_gpu_validation.py` 작성
- 전체 pytest 100% 통과 검증

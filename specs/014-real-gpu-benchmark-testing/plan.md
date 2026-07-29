# Implementation Plan: Real GPU Benchmark Engine & Dual-Mode (Mock vs Real) Automated Test Framework

**Branch**: `014-real-gpu-benchmark-testing` | **Date**: 2026-07-29 | **Spec**: [specs/014-real-gpu-benchmark-testing/spec.md](file:///home/dev/storage/vllm_serv/specs/014-real-gpu-benchmark-testing/spec.md)

**Input**: Feature specification from `/specs/014-real-gpu-benchmark-testing/spec.md`

---

## 1. Summary

본 계획서는 단위/통합 테스트에서 Mock 데이터만으로 무조건 성공하여 실제 라이브 GPU 환경(GTX 1080 Ti)에서 Gemma 4 (E2B, E4B) 로딩 실패가 은폐되던 문제를 해결합니다.
1. **CUDA llama-server 바이너리 검증 & CMake 자동 빌드 (`FR-001`)**: 서버 개설 시 CUDA 지원 binary 위치를 검증하고 미존재 시 CMake로 자동 빌드하여 준비.
2. **원스톱 모델 준비 & 기본 상주 모델 로드 (`FR-002`)**: GGUF 모델 로컬 확인 및 HuggingFace 자동 다운로드 후 기본 서비스 모델(`qwen3.5-4b`) VRAM 오프로드 상주.
3. **순차 실측 벤치마크 & 실패 누락 없는 리포팅 (`FR-003`)**: 6개 모델 순차 로드 및 추론 수행, 실패 모델도 에러 메시지와 함께 리포트 표 100% 기재.
4. **Pytest 커스텀 옵션 `--real` 및 듀얼 모드 Fixture 구축 (`FR-004`, `FR-005`)**: `pytest` (Mock Mode)와 `pytest --real` (Real GPU Mode)을 엄격히 분리하여 Mock 하드코딩 회피 현상 완전 차단.
5. **비동기 스트림 드레인 (`FR-006`)**: `ProcessManager` stdout/stderr 로그 스트림을 비동기로 continuous drain하여 OS PIPE 버퍼 교착 및 헬스체크 타임아웃 방지.

---

## 2. Technical Context

**Language/Version**: Python 3.12, CMake 3.22+, C++17 (for llama.cpp build)

**Primary Dependencies**: `llama-cpp-python`, `pynvml`, `fastapi`, `uvicorn`, `httpx`, `pytest`

**Storage**: Local GGUF models in `models/`, Markdown benchmark reports in `data/reports/analysis_report_quality.md` and `specs/013-enhance-benchmark-report/analysis_report_quality.md`

**Testing**: Pytest with custom `--real` option fixture in `tests/conftest.py`

**Target Platform**: Linux server with NVIDIA GeForce GTX 1080 Ti (11GB VRAM, CUDA 12.x)

**Project Type**: Python backend service & benchmarking CLI

**Performance Goals**: TTFT < 300ms, TPOT > 30 tok/s for 2B/4B models on 1080 Ti GPU

**Constraints**: Maximum VRAM allocation < 11264 MB (11GB safety limit)

**Scale/Scope**: 6 catalog models (`gemma4-e2b`, `gemma4-e4b`, `gemma4-12b`, `qwen3.5-2b`, `qwen3.5-4b`, `qwen3.5-9b`)

---

## 3. Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] 계획서가 한국어로 작성되었는가? (언어 정책)
- [x] 테스트 코드 작성 계획이 포함되어 있는가? (테스트 필수 원칙)
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (종료 조건 명확화 원칙)

---

## 4. Project Structure

### Documentation (this feature)

```text
specs/014-real-gpu-benchmark-testing/
├── spec.md              # Feature specification
├── plan.md              # Implementation plan (this file)
├── research.md          # Phase 0 technical decision records
├── data-model.md        # Phase 1 entity & metadata schema
├── quickstart.md        # Phase 1 runnable quickstart guide
├── contracts/           # Phase 1 JSON schema contract
│   └── dual-mode-test-schema.json
└── checklists/          # Requirements validation checklist
    └── requirements.md
```

### Source Code (repository root)

```text
src/
├── core/
│   ├── process_manager.py     # Subprocess lifecycle & async stdout stream drain (_drain_stdout)
│   ├── llama_manager.py       # LlamaManager status broadcast & default model residence
│   ├── model_downloader.py    # Auto HF Hub model download manager
│   └── gpu_detector.py        # PyNVML GPU VRAM detection & OOM threshold checks
├── eval/
│   └── quality_evaluator.py   # ROUGE-L, Exact Match, JSON validation & error tag extractor
scripts/
└── benchmark_quality.py       # 6-model one-stop auto-download + real GPU benchmark CLI

tests/
├── conftest.py                # Pytest --real custom option fixture & dual-mode TestExecutionMode fixture
├── unit/                      # Fast Mock Mode unit tests (pytest)
└── integration/               # Real GPU Mode integration tests (pytest --real)
```

**Structure Decision**: Single project repository layout with `src/`, `scripts/`, `tests/` and feature spec under `specs/014-real-gpu-benchmark-testing/`.

---

## 5. Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | None | All constitution guidelines met without violations |

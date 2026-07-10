# Implementation Plan: 002-performance-comparison

**Branch**: `002-performance-comparison` | **Date**: 2026-07-10 | **Spec**: [spec.md](file:///home/dev/vllm_serv/specs/002-performance-comparison/spec.md)

**Input**: Feature specification from `/specs/002-performance-comparison/spec.md`

## Summary

E2B, E4B, 12B 세 가지 Gemma-4 QAT 모델의 성능(응답 속도 및 VRAM)을 비교하기 위해 벤치마크 및 테스트 로직을 리팩토링합니다. `python-dotenv`를 도입하여 `.env` 파일에서 Hugging Face 토큰을 안전하게 로드하며, 기존 `unittest.mock` 사용을 배제하고 실제 모델과 단계별 한국어 프롬프트(Short, Medium, 4K Long)를 직접 주입하여 1080 Ti(11GB) 한계 내 4K 컨텍스트에서의 성능을 실증합니다.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: llama-cpp-python, huggingface-hub, python-dotenv

**Storage**: Local Filesystem (GGUF Models)

**Testing**: pytest (단일 테스트 시 Mock 없이 실제 모델 로드 필요)

**Target Platform**: Linux Server (NVIDIA GTX 1080 Ti 11GB VRAM 단일 GPU 환경)

**Project Type**: Backend AI Inference API & CLI Benchmark

**Performance Goals**: 4K 컨텍스트 로딩 안정성 (OOM 미발생), 각 모델별 TPOT(Tokens Per Output Token) 측정 및 최적 모델 선정

**Constraints**: GPU VRAM 11GB 한계 내에서 가장 긴 컨텍스트(4K)를 처리해야 함. `.env` 기반 토큰 로드 의무화.

**Scale/Scope**: 3개 모델 벤치마크, 3단계 프롬프트 길이, 1회 실행

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] 계획서가 한국어로 작성되었는가? (언어 정책)
- [x] 테스트 코드 작성 계획이 포함되어 있는가? (테스트 필수 원칙)
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (종료 조건 명확화 원칙)

## Project Structure

### Documentation (this feature)

```text
specs/002-performance-comparison/
├── plan.md              # This file
├── data-model.md        # Phase 1 output (벤치마크 데이터 구조)
├── quickstart.md        # Phase 1 output (실행 가이드)
└── tasks.md             # Phase 2 output (작업 목록)
```

### Source Code (repository root)

```text
src/
├── core/
│   ├── config.py           # 모델 설정
│   └── llama_manager.py    # Llama 인스턴스 관리
├── scripts/
│   ├── download_models.py  # dotenv 적용 다운로더
│   └── benchmark.py        # Mock 배제, 단계별 프롬프트 주입 로직 리팩토링
tests/
├── integration/            # Mock을 제거하고 실제 모델을 구동하는 테스트
└── unit/                   # Mock을 제거하고 실제 로직을 검증하는 테스트
```

**Structure Decision**: 기존 단일 프로젝트(Single project) 구조를 유지하며, 핵심 실행 스크립트인 `download_models.py`와 `benchmark.py`를 리팩토링하고, `tests/` 폴더 내의 목업 기반 테스트를 실제 구동 테스트로 전환합니다.

# Implementation Plan: Qwen3.5 모델 3종 (2B, 4B, 9B) 서비스 추가 및 성능 검증

**Feature Branch**: `007-qwen35-model-support`  
**Date**: 2026-07-29

## Technical Context

- **Core Technologies**: Python 3.10+, FastAPI 0.110+, Pydantic v2, `httpx`, `asyncio`, `pytest`, `llama.cpp` (GGUF runner)
- **Primary Modules**:
  - `src/core/process_manager.py`: Qwen3.5 2B/4B/9B GGUF 모델 경로, VRAM 임계치 조회, ChatML/Qwen 맞춤 채팅 템플릿 인자 추가 (`FR-001`, `FR-002`, `FR-009`)
  - `src/core/llama_manager.py`: Qwen3.5 동적 스위칭, 503 Maintenance Mode 및 SSE 브로드캐스팅 조합 (`FR-005`)
  - `src/api/routes/dashboard_api.py`: `/capabilities`, `/apply` 엔드포인트 Qwen3.5 프리셋 매핑 (`FR-001`)
  - `scripts/benchmark_qwen35.py`: [Gemma 4 3종 + Qwen3.5 3종 (Q4_K_M, Q4_0, Q8_0)] 실측 벤치마크 및 `analysis_report_qwen35.md` 자동 생성엔진 (`FR-003`, `FR-004`, `FR-006`, `FR-007`, `FR-008`, `FR-010`, `FR-011`)
- **Key Constraints**:
  - 11GB VRAM (GTX 1080 Ti) 한계 환경에서 OOM 방지를 위한 Dry-run VRAM 검증 및 서브프로세스 안전 롤백 보장 (`FR-010`)
  - 기존 Gemma 4 모델 3종의 레그레션 동작 및 13개 기존 pytest 100% 통과 유지

---

## Constitution Check

- **Principle I: 언어 정책 (한국어 출력 및 영어 추론)**: ✅ 통과 (모든 명세, 계획, 리포트 및 가이드는 한국어 작성)
- **Principle II: 테스트 주도 개발 및 품질 보증**: ✅ 통과 (Qwen3.5 프리셋 매핑 및 벤치마크 엔진 전용 단위/통합 테스트 코드 작성)
- **Principle III: 작업 종료 조건 명확화 (DoD)**: ✅ 통과 (DoD-001 ~ DoD-003 명시)
- **Principle IV: 비파괴적 문서 수정 원칙**: ✅ 통과 (기존 아티팩트 및 명세 내용 요약/생략 없이 온전히 보존 및 확장)

---

## Project Structure & Architecture Touch-Points

```text
src/
├── core/
│   ├── process_manager.py     # [UPDATE] Qwen3.5 2B/4B/9B GGUF 매핑, VRAM 한계, ChatML 템플릿 인자 바인딩
│   ├── llama_manager.py       # [UPDATE] Qwen3.5 모델 동적 로드/언로드 코디네이션
│   └── config_manager.py      # [UPDATE] Qwen3.5 기본 프리셋 설정
├── api/
│   └── routes/
│       └── dashboard_api.py   # [UPDATE] capabilities/apply API에 Qwen3.5 프리셋 모델 추가
scripts/
└── benchmark_qwen35.py        # [NEW] Qwen3.5 + Gemma 4 교차 벤치마크 및 리포트 자동 생성 스크립트
tests/
├── unit/
│   └── test_qwen_manager.py   # [NEW] Qwen3.5 프리셋 및 ChatML 템플릿 인자 단위 테스트
└── integration/
    └── test_qwen_benchmark.py # [NEW] 벤치마크 수집 및 리포트 생성 통합 테스트
```

---

## Phases & Execution Plan

### Phase 0: Research & Technical Decisions
- `research.md` 작성 완료:
  - Qwen3.5 아키텍처별 GGUF 파일 구조 및 ChatML / Qwen 채팅 템플릿 바인딩 전략
  - Q4_K_M, Q4_0, Q8_0 양자화 버전별 VRAM 추산 및 11GB VRAM 내 Dry-run 오버플로우 방지 로직
  - Gemma 4 3종과 Qwen3.5 3종 간의 1:1 교차 비교 벤치마크 프롬프트 데이터셋(Short, Medium, Long 4K/8K) 구성

### Phase 1: Design & Contracts
- `data-model.md`, `quickstart.md` 작성 완료
- `QwenModelPreset` 및 `QwenPerformanceReport` Pydantic v2 데이터 모델 정의
- 검증 시나리오 작성

### Phase 2: Implementation & Verification Strategy
- **Step 1**: `src/core/process_manager.py` 내 Qwen3.5 (2B/4B/9B) GGUF 경로 및 ChatML 템플릿 바인딩 추가 ➔ 단위 테스트 작성 (`test_qwen_manager.py`)
- **Step 2**: `src/api/routes/dashboard_api.py` 및 `config_manager.py` Qwen3.5 프리셋 바인딩 ➔ API 통합 테스트 검증
- **Step 3**: `scripts/benchmark_qwen35.py` 자동화 스크립트 작성 (로딩 시간, TTFT, TPOT, VRAM 피크, OOM 롤백, 한국어 프롬프트 주입)
- **Step 4**: 벤치마크 실행 및 `specs/007-qwen35-model-support/analysis_report_qwen35.md` 교차 성능 분석 보고서 최종 생성
- **Step 5**: 전체 13개 기존 테스트 + 신규 Qwen 테스트 100% 성공 검증

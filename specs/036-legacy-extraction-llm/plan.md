# Implementation Plan: 레거시 추출 스크립트 자체 서버 LLM 연동 전환 (036-legacy-extraction-llm)

**Branch**: `036-legacy-extraction-llm` | **Date**: 2026-07-30 | **Spec**: [spec.md](file:///home/dev/storage/vllm_serv/specs/036-legacy-extraction-llm/spec.md)

**Input**: Feature specification from `/specs/036-legacy-extraction-llm/spec.md`

## Summary

`.legacy/ATEAM_ExtractionItem.py` 및 `.legacy/BTEAM_ExtractionItem.py` 두 스크립트에서 외부 Groq API 호출(`https://api.groq.com/openai/v1`) 및 외부 API 키(`GROQ_API_KEY`) 의존성을 완전히 제거하고, 자체 개발 플랫폼 서버에 할당된 호스트 LAN IP(`http://10.0.0.41:8000/v1` 기본값, 환경 변수 오버라이드 지원) 기반의 OpenAI 호환 vLLM 엔드포인트 연동으로 전환합니다. `gemma4-e2b`, `gemma4-e4b`, `qwen3.5-2b`, `qwen3.5-4b`, `qwen3.5-9b` 모델 라인업 서빙을 지원하며, 기존 Kiwi 형태소 분석 및 2단계 하이브리드 BM25 오매칭 차단 파이프라인의 호환성을 100% 유지합니다.


## Technical Context

**Language/Version**: Python 3.12+ (uv 가상환경 연동)

**Primary Dependencies**: `openai` (v1.0+), `rank_bm25`, `kiwipiepy`, `python-dotenv`

**Storage**: N/A (인메모리 JSON 처리 및 스크립트 실행)

**Testing**: `uv run pytest tests/unit/test_legacy_extraction_llm.py`

**Target Platform**: Linux (개발 플랫폼 Server Assigned IP: `10.0.0.41`, port `8000`)

**Project Type**: Batch Scripts / Data Processing Pipeline Refactoring

**Performance Goals**: 로컬 vLLM 엔드포인트 응답 0.5초~3초 이내 파싱 완수

**Constraints**: 외부 인터넷 통신 없음(오프라인 독립 실행), `localhost`/`120.0.0.1` 바인딩 금지, 개발 플랫폼 할당 IP `10.0.0.41` 바인딩

**Scale/Scope**: `.legacy/ATEAM_ExtractionItem.py`, `.legacy/BTEAM_ExtractionItem.py`, 신규 테스트 수트 `tests/unit/test_legacy_extraction_llm.py`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] 계획서가 한국어로 작성되었는가? (언어 정책)
- [x] 테스트 코드 작성 계획이 포함되어 있는가? (테스트 필수 원칙: `tests/unit/test_legacy_extraction_llm.py`)
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (종료 조건 명확화 원칙: DoD-001~DoD-003)
- [x] 비파괴적 문서 수정 원칙을 준수하는가? (비파괴적 문서 수정 원칙)
- [x] uv 패키지 매니저 및 가상환경 격리 표준(uv run)을 준수하는가? (uv 패키지 및 환경 관리 원칙)

## Project Structure

### Documentation (this feature)

```text
specs/036-legacy-extraction-llm/
├── plan.md              # 이 계획서
├── research.md          # 로컬 LLM 바인딩, API 키 제거, 모델 라인업 조사 결과
├── data-model.md        # ExtractionItem 데이터 스키마 및 설정 객체
├── quickstart.md        # 검증 및 테스트 가이드
└── contracts/
    └── legacy_extraction_contract.json # 스크립트 인터페이스 규격 계약
```

### Source Code (repository root)

```text
.legacy/
├── ATEAM_ExtractionItem.py  # 주식 댓글 감성 추출 스크립트 (Groq -> 로컬 vLLM 전환)
└── BTEAM_ExtractionItem.py  # 음식점 리뷰 감성 추출 스크립트 (Groq -> 로컬 vLLM 전환)

tests/
└── unit/
    └── test_legacy_extraction_llm.py # 로컬 LLM 클라이언트 및 리팩토링 검증 테스트
```

**Structure Decision**: 기존 `.legacy/` 폴더 내의 스크립트 파일 위치 및 함수 시그니처를 유지하여 다운스트림 모듈의 호환성을 보장하고, `tests/unit/` 아래 신규 테스트 수트를 배치합니다.

## Complexity Tracking

*Constitution Check 위반 사항 없음 (가중 복잡성 없음)*

# Implementation Plan: AI 서비스 개발자 교육용 OpenAI API 표준 샘플 코드 리팩토링

**Branch**: `074-educational-openai-samples` | **Date**: 2026-08-03 | **Spec**: [specs/074-educational-openai-samples/spec.md](file:///home/dev/storage/vllm_serv/specs/074-educational-openai-samples/spec.md)

**Input**: Feature specification from `/specs/074-educational-openai-samples/spec.md`

## Summary

본 구현 계획서는 `samples/` 폴더 내 교육용 샘플 스크립트들을 비전공자 훈련생 눈높이에 맞춰 Pydantic 의존성 및 고난도 클래스 추상화를 제거하고, 표준 파이썬 딕셔너리(`dict`) 및 공식 `openai` SDK 기반으로 리팩토링하는 계획을 수립합니다. 강사, 교수, 훈련생, 훈련기관 평가자 4대 다중 페르소나의 니즈를 100% 충족시킵니다.

## Technical Context

**Language/Version**: Python 3.12 (managed via `uv`)

**Primary Dependencies**: openai, httpx, pydantic (샘플 스크립트에서는 Pydantic 사용 금지, 파이썬 기본 dict 사용)

**Storage**: N/A (샘플 스크립트 수트)

**Testing**: `uv run python samples/sample_0X_...py` & `uv run pytest`

**Target Platform**: Linux x86_64 / macOS / Windows Cross-Platform Education Environment

**Project Type**: Educational Python Sample Scripts & Helper Library

**Performance Goals**: 샘플 실행 시 에러 0건, 인지 부하 최소화

**Constraints**: Zero-Mock 준수, `uv run` 환경 격리, 헌법 II/III조 준수 (실물 서버 연동 검증)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] 계획서가 한국어로 작성되었는가? (언어 정책 준수)
- [x] 테스트 코드 작성 계획이 포함되어 있는가? (테스트 필수 원칙 준수)
- [x] 목업은 유료/제한 API로 엄격히 제한하고 실물 시스템/소켓/OS 인자 및 실제 호출 플래그(REAL_API_CALL=1) 기반 실측 검증 계획이 포함되어 있는가? (실체적 테스트 및 수렴 검증 원칙 - Zero Mock 준수)
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (종료 조건 명확화 원칙 준수)
- [x] 비파괴적 문서 수정 원칙을 준수하는가? (비파괴적 문서 수정 원칙 준수)
- [x] uv 패키지 매니저 및 가상환경 격리 표준(uv run)을 준수하는가? (uv 패키지 및 환경 관리 원칙 준수)
- [x] 전체 회귀 테스트 수트 및 Playwright 기반 E2E 브라우저 실측 검증 계획이 포함되어 있는가? (의무적 회귀 테스트 및 브라우저 E2E 검증 원칙 준수)

## Project Structure

### Documentation (this feature)

```text
specs/074-educational-openai-samples/
├── plan.md              # 이 계획서
├── research.md          # Phase 0 연구 결과 문서
├── data-model.md        # Phase 1 도메인 엔티티 모델 문서
├── quickstart.md        # Phase 1 실측 검증 가이드
├── contracts/           # Phase 1 계약 스키마 (sample-script-contract.json)
└── tasks.md             # Phase 2 과제 목록 (/speckit-tasks 명령어로 수립 예정)
```

### Source Code (repository root)

```text
samples/
├── common.py                # 직관적인 서버 호스트 감지 및 한글 터미널 출력 헬퍼
├── sample_01_chat.py        # [기초] OpenAI 공식 SDK & HTTP 대화 API 호출 예제
├── sample_02_model_params.py # [응용] Temperature, Top_P, Stop 파라미터 제어 예제
├── sample_03_embedding.py   # [RAG] BGE M3 임베딩 추출 예제
├── sample_04_reranking.py   # [RAG] BGE Reranker v2 M3 문서 재순위화 예제
└── README.md                # 비전공자 훈련생용 5분 완성 실습 가이드
```

**Structure Decision**: 기존 `samples/` 폴더 내 스크립트들을 직관적이고 표준화된 파이썬 코드 구조로 개편합니다.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

*(위반 사항 없음 - 헌법 7대 원칙 100% 준수)*

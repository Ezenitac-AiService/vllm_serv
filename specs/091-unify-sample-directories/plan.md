# Implementation Plan: 샘플 실습 디렉토리 이중화 분석 및 표준 통합 (`091-unify-sample-directories`)

**Branch**: `091-unify-sample-directories` | **Date**: 2026-08-04 | **Spec**: [spec.md](file:///home/dev/storage/vllm_serv/specs/091-unify-sample-directories/spec.md)

**Input**: Feature specification from `/specs/091-unify-sample-directories/spec.md`

## Summary

훈련 플랫폼용 고도화 파일 22종이 포함된 `sample/` 디렉토리를 유일한 주 표준 물리 디렉토리로 단일화하고, 이중화 참조 혼선을 발생시키던 `samples` 심볼릭 링크를 안전하게 영구 삭제합니다. 또한 `make_seed_pack.sh` 패키징 스크립트와 `tests/test_sample_scripts.py` 테스트 수트를 정돈하여 부작용 없는 깔끔한 코드베이스 구조를 완성합니다.

## Technical Context

**Language/Version**: Python 3.11, Bash Shell

**Primary Dependencies**: `pytest`, `uv`, `httpx`, `openai`

**Storage**: File system (`sample/`, `scripts/`, `tests/`)

**Testing**: `pytest` (`uv run pytest tests/test_sample_scripts.py`), `bash -n`

**Target Platform**: Linux server

**Project Type**: CLI / Educational Sample Suite & Build Automation

**Performance Goals**: 샘플 검증 테스트 수행 시간 < 5초

**Constraints**: `samples` 심볼릭 링크 삭제, `sample/` 단일 물리 디렉토리 유지, 이중 압축 오염 방지

**Scale/Scope**: `sample/` 디렉토리 내 22종 고도화 스크립트 및 `make_seed_pack.sh`, `tests/test_sample_scripts.py`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] 계획서가 한국어로 작성되었는가? (언어 정책)
- [x] 테스트 코드 작성 계획이 포함되어 있는가? (테스트 필수 원칙)
- [x] 목업은 유료/제한 API로 엄격히 제한하고 실물 시스템/소켓/OS 인자 및 실제 호출 플래그(REAL_API_CALL=1) 기반 실측 검증 계획이 포함되어 있는가? (실체적 테스트 및 수렴 검증 원칙)
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (종료 조건 명확화 원칙)
- [x] 비파괴적 문서 수정 원칙을 준수하는가? (비파괴적 문서 수정 원칙)
- [x] uv 패키지 매니저 및 가상환경 격리 표준(uv run)을 준수하는가? (uv 패키지 및 환경 관리 원칙)
- [x] 전체 회귀 테스트 수트 및 Playwright 기반 E2E 브라우저 실측 검증 계획이 포함되어 있는가? (의무적 회귀 테스트 및 브라우저 E2E 검증 원칙)

## Project Structure

### Documentation (this feature)

```text
specs/091-unify-sample-directories/
├── plan.md              # 이 문서 (/speckit-plan 생성)
├── research.md          # Phase 0 기술 결정 및 Rationale
├── data-model.md        # Phase 1 도메인 엔티티 정의
├── quickstart.md        # Phase 1 검증 가이드
├── contracts/           # Phase 1 계약 명세
│   └── sample_directory_contract.json
└── tasks.md             # Phase 2 구현 작업 목록 (/speckit-tasks 생성 예정)
```

### Source Code (repository root)

```text
sample/                  # [PRIMARY] 주 표준 물리 디렉토리 (22종 실습 코드 및 common.py, config.json)
├── common.py
├── config.json
├── sample_01_chat_basic.py ~ sample_11_structured_batch.py
└── openai_01_chat_basic.py ~ openai_11_structured_batch.py

# [REMOVED] samples (이전 임시 심볼릭 링크 삭제)

scripts/
└── make_seed_pack.sh    # [UPDATED] sample/ 단일 경로 포함 및 이중 오염 방지

tests/
└── test_sample_scripts.py # [UPDATED] sample/ 경로 전용 구문 및 바인딩 검증 테스트
```

**Structure Decision**: `sample/` 단일 물리 디렉토리를 주 표준 경로로 단일화하고 `samples` 심볼릭 링크를 삭제하는 간결하고 명확한 1인 구조를 확정함.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | 위반 사항 없음 | N/A |

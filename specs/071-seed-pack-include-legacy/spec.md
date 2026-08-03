# Feature Specification: sample_05_structured_output.py의 .legacy 모듈 의존성 제거 및 시드팩 독립성 보장 명세 (071-seed-pack-include-legacy)

**Feature Branch**: `071-seed-pack-include-legacy`

**Created**: 2026-08-03

**Status**: Draft

**Input**: User description: "시드 팩에 .legacy 폴더를 포함하면 안 되며, /home/dev/storage/vllm_serv/samples/sample_05_structured_output.py 파일이 /home/dev/storage/vllm_serv/.legacy/ATEAM_ExtractionItem.py 및 BTEAM_ExtractionItem.py 모듈에 의존하는 현상을 제거하여 자체 조율(Self-contained) 방식으로 동작하도록 명세"

## Clarifications

### Session 2026-08-03

- Q: `.legacy` 폴더의 처리 방향 및 `sample_05_structured_output.py`의 참조 구조는 어떻게 변경해야 하나요? → A: `.legacy` 디렉터리는 향후 삭제될 예정이므로 시드 팩 포함 대상에서 완전히 제외합니다. `samples/sample_05_structured_output.py`는 과거 레거시 실습 내용을 자체 포함(Self-contained)하도록 독립 구성하여, 향후 `.legacy` 폴더가 삭제되어도 영향을 받지 않도록 전면 개편합니다.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - sample_05_structured_output.py의 레거시 모듈 의존성 제거 및 독립 구동 (Priority: P1) 🎯 MVP

훈련생 및 외부 사용자는 이관된 시드 팩 환경(`vllm_serv`)에서 `samples/sample_05_structured_output.py` 스크립트를 실행할 때, 프로젝트 외부 또는 레거시 폴더(`.legacy`)의 모듈을 참조하지 않고 단독으로 Pydantic 구조화된 출력(Structured Output) 예제를 실행할 수 있어야 합니다.

**Why this priority**: `.legacy` 폴더는 시드 팩 배포 대상이 아니므로, 샘플 스크립트가 해당 폴더에 의존하면 배포 환경에서 모듈 임포트 실패가 발생합니다.

**Independent Test**: `.legacy` 폴더가 존재하지 않거나 삭제된 상태에서도 `uv run python samples/sample_05_structured_output.py` 실행 시 `ModuleNotFoundError` 없이 정상적으로 200 OK 응답 및 Pydantic 파싱 결과를 확인할 수 있는지 검증.

**Acceptance Scenarios**:

1. **Given** `.legacy` 디렉터리가 포함되지 않은 시드 팩 배포 환경일 때, **When** `uv run python samples/sample_05_structured_output.py` 구동 시, **Then** `.legacy` 모듈 임포트 오류 없이 Pydantic `StockAnalysisResponse` 모델을 사용한 구조화된 응답 추출 예제가 정상 실행되어야 합니다.
2. **Given** `sample_05_structured_output.py` 소스 코드 검토 시, **Then** `sys.path.insert(..., ".legacy")` 및 `ATEAM_ExtractionItem` / `BTEAM_ExtractionItem` 임포트 구문이 존재하지 않아야 합니다.

---

### User Story 2 - 시드 팩 아카이브의 .legacy 제외 상태 및 경량화 유지 (Priority: P2)

관리자는 `make_seed_pack.sh` 실행 시 `.legacy` 디렉터리가 시드 팩에 불필요하게 포함되지 않고 경량화 상태가 유지되는지 검증하기를 원합니다.

**Why this priority**: 불필요한 레거시 코드가 시드 팩에 포함되는 것을 방지하여 패키지 용량 및 독립성을 보장합니다.

**Independent Test**: `./scripts/make_seed_pack.sh` 실행 후 아카이브(`.tar.gz`, `.zip`) 내부 목록 검증 시 `.legacy` 폴더가 포함되어 있지 않음을 확인.

**Acceptance Scenarios**:

1. **Given** 시드 팩 아카이브 빌드 수행 시, **When** `./scripts/make_seed_pack.sh` 실행 후 아카이브 내부 파일 목록 확인 시, **Then** `.legacy` 관련 파일이 수록되지 않아야 합니다.

### Edge Cases

- `sample_05_structured_output.py`에서 레거시 종목 감성 파이프라인 실습 섹션 대신 Pydantic 표준 구조화 출력(Structured Output) 실습 중심으로 예제 주석 및 설명 문구 정리
- `tests/unit/test_sample_scripts.py` 수트 실행 시 `.legacy` 모듈 없이 샘플 05번 테스트가 정상 동작함을 보장

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `samples/sample_05_structured_output.py`에서 `sys.path` 레거시 디렉터리 추가 및 `ATEAM_ExtractionItem` / `BTEAM_ExtractionItem` 임포트 전면 제거
- **DoD-002**: `sample_05_structured_output.py`가 표준 Pydantic `StockAnalysisResponse` 스키마 및 OpenAI API 규격만을 사용하는 독립 예제 스크립트로 개편 완료
- **DoD-003**: `.legacy` 디렉터리 삭제 후에도 `uv run python samples/sample_05_structured_output.py` 및 단위 테스트(`uv run pytest tests/unit/test_sample_scripts.py`)가 100% 정상 통과함을 검증
- **DoD-004**: 전체 pytest 회귀 테스트 수트 (`uv run pytest`) 100% Green Pass 통과

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `samples/sample_05_structured_output.py`는 프로젝트 내외부의 `.legacy` 디렉터리 및 외부 모듈에 의존하지 않고 단독으로 작동하는 독립(Self-contained) 예제 스크립트여야 합니다.
- **FR-002**: `samples/sample_05_structured_output.py`는 OpenAI 호환 `response_format={"type": "json_object"}` 및 Pydantic `model_validate_json` 기반의 현대적 구조화 출력 파싱 로직만을 제공해야 합니다.
- **FR-003**: `scripts/make_seed_pack.sh`는 `.legacy` 디렉터리를 아카이브 번들링 대상에 포함시키지 않아야 합니다.

### Key Entities

- **StandaloneStructuredOutputSample**: 외부 모듈 의존성 없이 Pydantic 기반으로 LLM JSON 응답을 파싱하는 단독 예제 스크립트 개체

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `sample_05_structured_output.py` 실행 시 `.legacy` 의존성 0건 보장
- **SC-002**: 시드 팩 배포 환경에서 `sample_05_structured_output.py` 실행 성공률 100%
- **SC-003**: 전체 pytest 회귀 테스트 통과율 100%

## Assumptions

- `.legacy` 디렉터리는 과거 실험용 코드 저장 공간이며 시드 팩 아카이브 배포 대상이 아닙니다.
- `samples/` 아래의 모든 샘플 코드는 외부 의존성 없이 표준 Python 및 `httpx`, `pydantic` 라이브러리만으로 작동해야 합니다.

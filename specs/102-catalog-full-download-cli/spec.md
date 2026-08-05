# Feature Specification: `scripts/ensure_models.py` 전체/특정 모델 다운로드 CLI 옵션 확장 (102-catalog-full-download-cli)

**Feature Branch**: `102-catalog-full-download-cli`

**Created**: 2026-08-05

**Status**: Draft (Clarified)

**Input**: User description: "전체 카탈로드 다운로드 옵션이 스크립트에 있어야 할거 같은데, 지금 카탈로그에 모델이 추가되어있는데, 받을 방법이 없는거잖아?"

## Clarifications

### Session 2026-08-05

- Q: `--all`과 `--model <MODEL_ID>` CLI 옵션이 동시에 지정되었을 때 시스템 처리 방식은 어떠한가? → A: 두 옵션은 상호 배타적으로 동작하도록 정의하며, 동시 지정 시 CLI 인자 구문 에러 메시지를 출력하고 exit code 2로 즉시 프로세스를 종료한다.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 카탈로그 전체 모델 일괄 점검 및 다운로드 옵션 (`--all`) (Priority: P1) 🎯 MVP

시스템 엔지니어 또는 운영자가 카탈로그(`config/model_catalog.json`)에 새롭게 추가된 모델들을 포함하여 카탈로그 내 모든 14개 모델의 로컬 저장소 존재 여부를 일괄 점검하고 부재 시 자동 다운로드받기 위해 `uv run scripts/ensure_models.py --all` 명령을 구동할 수 있어야 합니다.

**Why this priority**: 현재 `ensure_models.py`는 기본 3종 필수 모델만 점검하므로, 카탈로그 확장 후 전체 모델을 사전 프로비저닝할 수 있는 핵심 수단이 최우선으로 필요합니다.

**Independent Test**: `uv run scripts/ensure_models.py --all --check-only` 실행 시 카탈로그 내 14개 전체 모델의 점검 결과가 화면에 출력됨을 확인합니다.

**Acceptance Scenarios**:

1. **Given** `config/model_catalog.json`에 14개 모델 정보가 정의되어 있을 때, **When** `scripts/ensure_models.py --all`을 실행하면, **Then** 필수 3종에 제한되지 않고 카탈로그 전체 14개 모델의 점검 및 미존재 시 자동 다운로드가 순차 수행되어야 한다.
2. **Given** `--all`과 `--check-only` 옵션이 동시에 전달될 때, **When** `scripts/ensure_models.py --all --check-only`를 실행하면, **Then** 14개 전체 모델의 로컬 존재 상태만 전수 검사하여 리포트하고 실제 다운로드는 진행하지 않아야 한다.

---

### User Story 2 - 특정 지정 모델 핀포인트 점검 및 다운로드 옵션 (`--model <MODEL_ID>`) (Priority: P2)

운영자가 전체 모델을 다운로드하지 않고, 카탈로그 내 특정 신규 대형 모델(예: `qwen3.6-27b`, `gemma4-26b-a4b`)만 명시적으로 선택하여 점검하고 다운로드하기 위해 `uv run scripts/ensure_models.py --model qwen3.6-27b` 명령을 구동할 수 있어야 합니다.

**Why this priority**: 특정 모델 하나만 필요한 상황에서 수십 GB의 전체 카탈로그를 다운로드하지 않고 필요한 모델만 타깃팅하여 다운로드할 수 있는 유연성을 제공합니다.

**Independent Test**: `uv run scripts/ensure_models.py --model qwen3.6-27b --check-only` 구동 시 `qwen3.6-27b` 단일 모델의 존재 상태만 점검 및 리포트됨을 확인합니다.

**Acceptance Scenarios**:

1. **Given** 유효한 카탈로그 모델 ID(`qwen3.6-27b`)가 전달될 때, **When** `scripts/ensure_models.py --model qwen3.6-27b`를 실행하면, **Then** 해당 모델 하나에 대해서만 로컬 존재 점검 및 미존재 시 다운로드가 수행되어야 한다.
2. **Given** 카탈로그에 존재하지 않는 무효한 모델 ID(`invalid-model-xyz`)가 전달될 때, **When** `scripts/ensure_models.py --model invalid-model-xyz`를 실행하면, **Then** 명확한 사용자 에러 메시지(`Unknown model_id: invalid-model-xyz`)를 출력하고 non-zero exit code (1)로 즉시 종료되어야 한다.

---

### Edge Cases

- `--all` 옵션과 `--model <MODEL_ID>` 옵션이 동시에 지정되었을 때 상호 배타적 구문 오류 메시지를 출력하고 exit code 2로 즉시 종료하는가?
- 14개 전체 모델 다운로드 중 특정 모델 다운로드가 실패할 경우 나머지 모델 다운로드를 지속 수행하고 최종 성공/실패 개수를 명확히 종합 리포트하는가?

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `scripts/ensure_models.py` CLI 인자 파서에 `--all` (또는 `--download-all`) 및 `--model <MODEL_ID>` 옵션 구현 및 백엔드 타깃 모델 동적 리졸버 연동 완납.
- **DoD-002**: `tests/unit/test_ensure_models_cli.py` 단위 테스트 수트를 작성하여 `--all`, `--model`, `--check-only` 조합 시나리오 100% 검증 통과.
- **DoD-003**: 프로젝트 전체 단위 테스트 수트 (`uv run pytest tests/unit/`) 100% Pass 및 헌장 원칙 준수.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST `scripts/ensure_models.py` CLI 옵션에 `--all` (또는 `--download-all`) 인자를 추가하여 `config/model_catalog.json`에 정의된 모든 모델을 일괄 점검 및 다운로드할 수 있어야 한다.
- **FR-002**: System MUST `scripts/ensure_models.py` CLI 옵션에 `--model <MODEL_ID>` 인자를 추가하여 단일 또는 쉼표로 구분된 특정 모델 식별자만 선택적으로 핀포인트 점검 및 다운로드할 수 있어야 한다.
- **FR-003**: System MUST `--all` 또는 `--model` 인자가 지정되지 않은 경우 기존 동작(서빙/임베딩/리랭커 동적 필수 3종 모델 점검)을 100% 하위 호환으로 유지를 보장해야 한다.
- **FR-004**: System MUST 존재하지 않는 모델 ID가 `--model` 인자로 전달되면 명확한 에러 메시지를 출력하고 exit code 1로 종료해야 하며, `--all`과 `--model` 인자가 동시에 지정된 경우 상호 배타적 인자 에러 메시지를 출력하고 exit code 2로 프로세스를 즉시 종료해야 한다.
- **FR-005**: System MUST `--all` 및 `--model` 옵션 구동 완료 시에도 로컬에 이미 존재하거나 다운로드가 완납된 모델에 대해 `FR-012` 메타데이터(파일 바이트 및 `size_gb`) 자율 동기화를 수행해야 한다.

### Key Entities

- **EnsureModelsCLIConfig**: CLI에서 입력받은 `--all`, `--model`, `--check-only`, `--no-auto-download` 플래그를 해석하여 최종 다운로드 점검 대상 `target_models: List[str]`으로 정규화하는 데이터 엔티티.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `uv run scripts/ensure_models.py --all --check-only` 구동 시 카탈로그 내 14개 전체 모델의 상태가 100% 정밀 리포트됨.
- **SC-002**: `uv run scripts/ensure_models.py --model qwen3.6-27b --check-only` 구동 시 지정한 모델의 상태만 정확히 핀포인트 리포트됨.
- **SC-003**: 기본 인자 없이 구동 시 기존 동적 필수 모델 점검 파이프라인 100% 정상 작동.
- **SC-004**: 단위 테스트 수트 (`uv run pytest tests/unit/test_ensure_models_cli.py`) 100% Pass.

## Assumptions

- 대형 모델 다운로드 시 네트워크 단선이나 타임아웃을 대비하여 기존 `ModelDownloader`의 최대 3회 재시도(Retry) 및 진행률 콘솔 출력을 그대로 활용한다.
- `--model` 인자는 단일 ID(`qwen3.6-27b`) 및 쉼표 구분 복수 ID(`qwen3.6-27b,gemma4-26b-a4b`) 지정을 모두 지원한다.

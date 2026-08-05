# Phase 0 Research: `scripts/ensure_models.py` 전체/특정 모델 다운로드 CLI 옵션 확장 (102-catalog-full-download-cli)

## Research Decisions

### Decision 1: CLI 인자 파서 구문 상호 배타성 제어 및 Exit Code 표준화

- **Decision**: Python 표준 `argparse` 파서를 사용하되, `--all` 및 `--model` 옵션이 동시 지정된 경우 명시적 조건 검사를 수행하여 커스텀 에러 메시지(`[ERROR] --all and --model options are mutually exclusive.`)를 `sys.stderr`로 출력하고 `sys.exit(2)`로 프로세스를 즉시 종료한다.
- **Rationale**: 표준 `argparse` mutually exclusive group은 시스템 메시지만 출력하므로, 프로젝트 헌장 및 사용자 요구사항 규격에 맞는 명확한 한글/영문 안내와 정확한 Exit Code (2)를 전달하기 위함이다.
- **Alternatives considered**:
  - `parser.add_mutually_exclusive_group()`: 자동 에러 메시지가 구체적이지 않고 Exit Code 커스터마이징이 모호함.

---

### Decision 2: 타깃 모델 동적 리졸버 함수 분리 (`resolve_target_models`)

- **Decision**: [`scripts/ensure_models.py`](file:///home/dev/storage/vllm_serv/scripts/ensure_models.py) 내부 기존 `get_dynamic_required_models()`를 보완하고 `resolve_target_models(all_flag: bool = False, model_arg: Optional[str] = None)` 별도 리졸버 함수를 작성한다.
  - `all_flag == True`: `config/model_catalog.json` 내 전체 14개 모델 ID 목록 반환.
  - `model_arg` 지정 시: 쉼표(`,`) 분할 후 카탈로그 존재 여부 정밀 검증. 무효한 ID 포함 시 `ValueError("Unknown model_id: ...")` 발생.
  - 옵션 미지정 시: 기존 서빙/임베딩/리랭커 동적 필수 3종 모델 리스트 반환 (100% 하위 호환).
- **Rationale**: CLI 인자 해석과 비즈니스 로직을 분리함으로써 단위 테스트 수트에서 각 조건별 리졸빙 결과를 모듈식으로 단정할 수 있음.
- **Alternatives considered**: `ensure_all_models` 함수 내부에 CLI 분기문 직결 (테스트 용이성 저해).

---

### Decision 3: `--model` 쉼표 구분 다중 지정 및 무효 모델 즉시 차단

- **Decision**: `--model qwen3.6-27b,gemma4-26b-a4b` 형태의 쉼표 구분 다중 ID 지정을 지원하며, 전달된 리스트 중 하나라도 카탈로그에 없는 식별자일 경우 `[ERROR] Unknown model_id: <INVALID_ID>` 출력 후 `sys.exit(1)`로 즉시 차단한다.
- **Rationale**: 잘못된 모델 ID를 지정하여 대기 시간이 긴 다운로드를 수행하다가 뒤늦게 오작동하는 현상을 방지하기 위해 Pre-flight 식별자 무결성 검증이 필수적이다.
- **Alternatives considered**: 무효한 모델만 경고 후 스킵하고 유효한 모델만 다운로드 (운영자 의도와 다른 불완전 프로비저닝 위험).

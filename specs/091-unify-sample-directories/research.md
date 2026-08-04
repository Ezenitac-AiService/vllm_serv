# Research & Technical Decisions: 샘플 실습 디렉토리 이중화 분석 및 표준 통합 (`091-unify-sample-directories`)

## Phase 0: Research & Decision Log

### Decision 1: 주 표준 물리 디렉토리 지정 및 `samples` 심볼릭 링크 처리 방침

- **Decision**: 훈련 플랫폼용 고도화 파일 22종이 포함된 `sample/` 디렉토리를 주 표준 물리 디렉토리(Primary Physical Directory)로 확정하고, 임시 생성되었던 `samples` 심볼릭 링크는 안전하게 영구 삭제하여 `sample/` 단일 경로로 코드베이스를 정돈한다.
- **Rationale**:
  - 소스 코드(`src/`, `scripts/`) 정밀 검사 결과 `samples` 경로를 하드코딩 참조하는 코드가 존재하지 않음을 확인.
  - 심볼릭 링크로 인한 이중 참조 혼선 및 시드팩 패키징 시 발생 가능한 예외 상황을 근본적으로 예방.
- **Alternatives Considered**:
  - *Option A (`samples -> sample` 심볼릭 링크 보존)*: 하위 호환성은 보완되나 사용자가 명시적으로 `samples` 심볼릭 링크 삭제 및 단일 물리 폴더 사용(Option B)을 선택함.
  - *Option C (`samples`로 물리 폴더명 변경)*: 기존 `sample/` 폴더 내 파일 이동 및 `pyproject.toml` 수정 부담 발생.

---

### Decision 2: 시드팩 생성 스크립트(`make_seed_pack.sh`) 및 배포 파이프라인 정합성 방침

- **Decision**: `scripts/make_seed_pack.sh`에서 `sample/` 물리 디렉토리가 타르볼 번들링에 1개 수록되도록 보장하고, `samples` 심볼릭 링크 잔재가 포함되지 않도록 압축 대상을 명확히 지정한다.
- **Rationale**:
  - 마이그레이션 시드팩(`vllm_serv_seed.tar.gz`) 해제 시 훈련생 환경에서 깨끗한 단일 `sample/` 폴더만 복원되도록 보장.
- **Alternatives Considered**:
  - *Option B (두 폴더 모두 실물 복사 패키징)*: 타르볼 용량이 2배로 증가하고 불필요한 파일 중복 오염 발생.

---

### Decision 3: 샘플 수트 자동화 테스트 수트 정합성 보장 (`tests/test_sample_scripts.py`)

- **Decision**: `tests/test_sample_scripts.py`가 `sample/` 단일 디렉토리를 정확히 스캔하여 22종 샘플 파일의 구문 정확성과 IP 하드코딩 여부를 검증하도록 구현한다.
- **Rationale**:
  - 헌장 II/VII에 부합하는 자동화 회귀 검증 체계 유지.

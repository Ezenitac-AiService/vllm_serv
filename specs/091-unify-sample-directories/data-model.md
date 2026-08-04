# Data Model & Domain Entities: 샘플 실습 디렉토리 이중화 분석 및 표준 통합 (`091-unify-sample-directories`)

## Domain Entities

### 1. `SampleDirectoryStructure` (샘플 디렉토리 구조 엔티티)

샘플 실습 자산이 위치한 표준 디렉토리의 구조 및 상태 엔티티.

- **Attributes**:
  - `primary_path`: `str` - 주 표준 물리 디렉토리 경로 (`sample/`)
  - `deprecated_symlink_path`: `Optional[str]` - 삭제 대상 심볼릭 링크 경로 (`samples`)
  - `is_unified`: `bool` - 단일 `sample/` 물리 디렉토리로 통합 정돈되었는지 여부
  - `sample_file_count`: `int` - 표준 물리 디렉토리 내 포함된 실습 스크립트 수 (총 22개: `sample_01`~`11`, `openai_01`~`11`)

- **Validation Rules**:
  - `primary_path`는 반드시 존재하고 22종 이상의 파이썬 실습 스크립트 및 `common.py`, `config.json`을 포함해야 함.
  - `deprecated_symlink_path`는 영구 삭제되어 존재하지 않아야 함 (`is_unified == True`).

---

### 2. `SeedPackSampleLayout` (시드팩 내 샘플 번들링 엔티티)

`make_seed_pack.sh` 실행 결과물 시드팩 타르볼 내의 샘플 자산 레이아웃 엔티티.

- **Attributes**:
  - `tarball_path`: `str` - 시드팩 파일 경로 (`vllm_serv_seed.tar.gz`)
  - `bundled_sample_dir`: `str` - 포함된 샘플 디렉토리 명칭 (`sample/`)
  - `has_duplicate_symlink`: `bool` - 중복 디렉토리/심볼릭 링크 유무 (`False` 필수)

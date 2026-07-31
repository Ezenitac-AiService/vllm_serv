# Research: 시드팩(Seed Pack) 패키징 시 명세서(specs/) 및 샘플 파일(samples/) 수록 포함 개선

**Feature**: `065-seed-pack-specs-samples`

## Technical Decisions & Rationale

### Decision 1: `scripts/make_seed_pack.sh` exclusion 규칙 개정
- **선택된 방식**: `tar` 및 `zip` 명령어의 `--exclude` 규칙에서 `specs` 및 `.legacy` 항목을 삭제하고, `samples/` 디렉터리가 아카이브 루트에 자연스럽게 포함되도록 유지함.
- **이유**: 기존 시드팩 생성 시 `specs/` 및 `.legacy/`가 제외되어 이관 대상 서버에서 최신 기능 명세서 문서와 레거시 추출 스키마 모듈을 참조하지 못했던 문제를 해결합니다. `samples/` 디렉터리(`common.py`, `sample_01` ~ `sample_05`)와 `specs/`가 포함되더라도 총 용량 증가분은 ~2MB 이내로 경량 시드팩 요건(<15MB)을 여전히 완벽히 충족합니다.
- **대안 검토**: `samples/`만 포함하고 `specs/`는 별도 아카이브로 분리 — 이관 절차가 복잡해지고 단일 시드팩 원칙에 위배되므로 기각함.

### Decision 2: Post-Build 수록 검증 강화
- **선택된 방식**: `scripts/make_seed_pack.sh` 생성 완료 후 `ARCHIVE_FILES` 검색 부분에 `samples/common.py` 및 `specs/` 파일 수록 확인 assertion 추가.
- **이유**: 패키징 완료 직후 실시간으로 필수 문서 및 예제 코드 수록 여부를 실측 검증하여 수록 실패 시 exit code 1을 즉시 반환함.

### Decision 3: Pytest 검증 수트 연동 (`tests/unit/test_seed_pack.py`)
- **선택된 방식**: `test_seed_pack.py`에 생성된 시드팩 파일 내부 목록 탐색 및 `samples/common.py`, `samples/sample_01_chat.py`, `specs/065-seed-pack-specs-samples/spec.md` 파일 존재 검증 테스트 케이스 추가.
- **이유**: CI/CD 회귀 테스트 시 시드팩 무결성을 자동으로 입증함.

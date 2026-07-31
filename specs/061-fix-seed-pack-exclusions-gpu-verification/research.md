# Technical Research & Decision Log: 061-fix-seed-pack-exclusions-gpu-verification

## Decision 1: `make_seed_pack.sh` 아카이브 수록 제외 항목 확정

### Rationale (선택 이유)
- `specs/`, `.agents/`, `.specify/` 3개 디렉터리는 순수 개발/스펙/에이전트 도구이므로 배포용 씨드 팩 아카이브(`dist/vllm_serv_seed.tar.gz`)에서 제외하여 압축 파일 용량을 최소화하고 런타임 환경을 경량화함.
- `tests/` 디렉터리는 타겟 서버 배포 후 현지 수념 검증 및 회귀 테스트용으로 수록 보존함 (Option B 반영).
- `tar -czf` 옵션에 `--exclude="specs" --exclude=".agents" --exclude=".specify"`, `zip -r -q` 옵션에 `-x "specs/*" -x ".agents/*" -x ".specify/*"`를 수록함.

### Alternatives Considered (기각된 대안들)
- **대안 A: `tests/` 디렉터리까지 포함하여 전면 제외**
  - **기각 사유**: 타겟 서버 현지에서 `pytest` 회귀 테스트를 수행하고자 하는 운영자의 요구(Option B)를 충족할 수 없음.

---

## Decision 2: `setup.sh` GPU 가속 검증 시 `.venv/bin/python` 가상환경 파이썬 직접 실행

### Rationale (선택 이유)
- `setup.sh`에서 사전 빌드 CUDA 휠을 `uv pip install`로 `.venv`에 설치한 직후, `uv run python -c`를 호출하면 `uv run`이 환경 동기화 상태 불일치를 감지하여 `.venv`에 방금 설치된 CUDA 휠을 자동으로 `Uninstall`하고 `uv` 캐시의 CPU 전용 휠로 원복 덮어쓰기(`Installed 1 package in 5ms`)함.
- GPU 검증 및 사전 검증 명령어를 `uv run python` 대신 `.venv/bin/python` (가상환경 내 실행 파일)으로 직접 호출함으로써 `uv` 패키지 자동 동기화 덮어쓰기 오작동을 **100% 차단**하고 Fast-Track 복원(< 5초)을 보장함.

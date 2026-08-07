# Research Findings: Seed Pack 복원 스크립트 고도화 (`unpack_seed.sh`)

**Feature Directory**: `specs/111-unpack-seed-script-enhancement`

---

## 1. 멀티 포맷 (.tar.gz & .zip) 감지 및 비파괴 복원 기술 조사

### Decision
- **포맷 자동 감지**:
  1. CLI 입력 인자 또는 기본 파일명(`dist/vllm_serv_seed.zip`, `dist/vllm_serv_seed.tar.gz`, `vllm_serv_seed.zip`, `vllm_serv_seed.tar.gz`) 검사
  2. 파일 확장자 검사 (`.zip` vs `.tar.gz` / `.tgz`)
  3. `file` 명령 또는 바이너리 헤더 시그니처 검사 (`PK\x03\x04` for zip, `\x1f\x8b` for gzip tarball)
- **비파괴 복원 (Non-Destructive Extraction)**:
  - **POSIX Tarball (.tar.gz)**: `tar -xvkpf "$ARCHIVE" -C "$TARGET_DIR"` (flag `-k` / `--skip-old-files`를 사용하여 기존 바이너리/파일 덮어쓰기 방지, `-p`로 권한 보존).
  - **ZIP (.zip)**: `unzip -n -q "$ARCHIVE" -d "$TARGET_DIR"` (flag `-n` / `--never-overwrite`를 사용하여 기존 파일 보존).
  - **강제 덮어쓰기 (`-f` / `--force-overwrite`)**: `tar -xvpf` 또는 `unzip -o -q` 실행.

### Rationale
- `make_seed_pack.sh`에서 `.zip` 및 `.tar.gz` 아카이브 생성을 모두 지원하므로, `unpack_seed.sh`가 동적으로 포맷을 자동 감지하고 적절한 압축 해제 명령어를 분기 실행해야 타겟 서버 마이그레이션이 끊김없이 동작합니다.
- 레거시 서버(i7-930 Nehalem 등)에서 이미 빌드되어 가속 검증을 통과한 `wheels/legacy_i7_930/*.whl` 바이너리가 존재할 경우, 압축 해제 시 덮어쓰지 않고 최우선 보존(`-k` / `-n`)하여 재컴파일 오버헤드를 예방합니다.

### Alternatives Considered
- `python3 -m zipfile` / `python3 -m tarfile`: 외부 Python 환경에 의존적일 수 있음. POSIX bash 스크립트 특성상 시스템 `tar` 및 `unzip` 도구를 직접 활용하는 것이 빠른 실행 및 오버헤드 최소화에 유리함.

---

## 2. CLI 입력 옵션 사양 및 파싱 알고리즘

### Decision
`getopts` 또는 표준 bash `while [[ $# -gt 0 ]]` 옵션 파싱 루프 구조 도입:
- `-i`, `--input PATH`: 입력 아카이브 경로 지정 (기본값: `dist/vllm_serv_seed.tar.gz` → `vllm_serv_seed.tar.gz` → `dist/vllm_serv_seed.zip` → `vllm_serv_seed.zip` 자동 탐색)
- `-t`, `--target-dir PATH`: 압축 해제 목적지 디렉터리 (기본값: `$BASE_DIR`)
- `-f`, `--force-overwrite`: 기존 파일 강제 덮어쓰기 (기본값: 비파괴 보존)
- `--verify-only`: 압축 해제 없이 사전 무결성 검증 및 파일 목록만 검사
- `--run-setup`: 압축 해제 완결 후 자동으로 `./setup.sh` 구동
- `-h`, `--help`: 사용법 도움말 출력 후 종료

---

## 3. 사전 및 사후 아카이브 무결성 검증 체계

### Decision
- **사전 검증 (Pre-Unpack Verification)**:
  - 아카이브 내 필수 파일(`platform_profiles.json`, `model_catalog.json`, `gpu_detector.py`, `start_server.sh`, `ensure_models.py`, `auxiliary_manager.py`) 수록 여부를 `tar -tzf` 또는 `unzip -l`로 전수 검사.
  - 필수 파일 누락 시 압축 해제를 진행하지 않고 에러 출력 후 종료 (`exit 1`).
- **사후 검증 (Post-Unpack Verification)**:
  - 지정 목적지 디렉터리에 필수 파일이 실제로 존재하는지 확인.
  - 기존 휠 바이너리 가속 여부 (`scripts/verify_wheel_binary.py --check-live`) 점검.

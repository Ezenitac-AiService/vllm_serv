# CLI Interface Contract: Seed Pack 복원 스크립트 (`unpack_seed.sh`)

**Feature Directory**: `specs/111-unpack-seed-script-enhancement`

---

## 1. CLI Usage & Flags

```bash
scripts/unpack_seed.sh [OPTIONS] [ARCHIVE_FILE]
```

### Supported Flags

| Flag | Long Flag | Value Type | Description |
|------|-----------|------------|-------------|
| `-i` | `--input` | PATH | 복원할 시드 팩 아카이브 경로 지정 |
| `-t` | `--target-dir` | PATH | 압축 해제 목적지 디렉터리 경로 지정 (기본값: 현 프로젝트 루트) |
| `-f` | `--force-overwrite` | NONE | 기존 파일 덮어쓰기 허용 (`tar -xvpf` 또는 `unzip -o`) |
| | `--verify-only` | NONE | 압축 해제 작업을 수행하지 않고 사전 무결성 검증만 실시 |
| | `--run-setup` | NONE | 압축 해제 완료 후 `./setup.sh` 자동 구동 |
| `-h` | `--help` | NONE | 사용법 도움말 출력 후 종료 (exit 0) |

---

## 2. Execution Workflows & Exit Codes

### Workflow Steps
1. **CLI Argument Parsing**: 옵션 해석 및 경로 정규화.
2. **Archive Auto-Detection**: 확장자 및 헤더 시그니처 분석으로 `.tar.gz` / `.zip` 감지.
3. **Pre-Unpack Integrity Verification**: 필수 파일(`platform_profiles.json`, `model_catalog.json`, `gpu_detector.py`, `start_server.sh` 등) 수록 여부 확인.
4. **Existing Binary Protection Check**: 기존 유효 바이너리(`wheels/legacy_i7_930/*.whl`) 존재 시 `-k`/`-n` 플래그로 보호 안내.
5. **Extraction Execution**: `tar -xvkpf` 또는 `unzip -n -q` 실행.
6. **Post-Unpack Verification**: 주요 복원 파일 체크 및 결과 메트릭 출력.
7. **Post-Action**: `--run-setup` 지정 시 `./setup.sh` 구동.

### Exit Codes

| Exit Code | Meaning |
|-----------|---------|
| `0` | 성공 (복원 및 무결성 검증 완결) |
| `1` | 아카이브 파일 미존재, 필수 파일 누락, 또는 압축 도구 미설치 |
| `2` | tar/unzip 압축 해제 중 경고 또는 치명적 에러 발생 |

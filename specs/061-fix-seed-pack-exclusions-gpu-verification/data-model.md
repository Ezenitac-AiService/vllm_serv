# Data Model: 061-fix-seed-pack-exclusions-gpu-verification

## Entities & Schemas

### 1. `SeedPackArchiveExclusions` (아카이브 수록 제외 항목)

| Path Pattern | Status in Archive | Description |
|--------------|-------------------|-------------|
| `specs/` | Excluded (`--exclude="specs"`) | 개발 명세서 디렉터리 |
| `.agents/` | Excluded (`--exclude=".agents"`) | AI 에이전트 스킬 및 프로세서 |
| `.specify/` | Excluded (`--exclude=".specify"`) | Spec Kit 설정 및 거버넌스 템플릿 |
| `tests/` | Retained (Included) | 타겟 서버 현지 검증용 Pytest 수트 |

### 2. `SetupFastTrackRunner` (setup.sh 파이썬 실행기 구조)

| Runner Type | Command Path | Auto-Sync Risk | Selection |
|-------------|--------------|----------------|-----------|
| `uv run python` | `/usr/local/bin/uv` wrapper | High (silent package overwrite) | Rejected |
| `.venv/bin/python` | Direct virtualenv python | Zero (strict environment isolation) | **Selected** |

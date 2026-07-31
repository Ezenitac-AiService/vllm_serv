# Implementation Plan: 061-fix-seed-pack-exclusions-gpu-verification

## Technical Context

- **Feature Directory**: `specs/061-fix-seed-pack-exclusions-gpu-verification`
- **Target Files**:
  - `scripts/make_seed_pack.sh`
  - `scripts/setup.sh`
  - `tests/unit/test_seed_pack.py`
- **Design Artifacts**:
  - `research.md` (Decision 1: Archive exclusions, Decision 2: `.venv/bin/python` runner)
  - `data-model.md` (`SeedPackArchiveExclusions` & `SetupFastTrackRunner`)
  - `contracts/seedpack-exclusion-contract.json`
  - `quickstart.md`

---

## Constitution Check

- [x] **Principle I (Language Policy)**: All planning documents and user-facing communications are written in Korean.
- [x] **Principle II (Real-Integration TDD)**: Tests in `tests/unit/test_seed_pack.py` are written and run against real binaries with ZERO mocks in production code.
- [x] **Principle IV (Definition of Done)**: Done criteria measured by 100% green pytest execution and fast-track setup verification.
- [x] **Principle VI (uv Environment)**: Development commands execute with `uv run`.
- [x] **Principle VII (Mandatory Regression Testing)**: Full unit regression suite `uv run pytest tests/unit/test_seed_pack.py` passes 100%.

---

## Proposed Changes

### Component 1: `scripts/make_seed_pack.sh`
- Add `--exclude="specs" --exclude=".agents" --exclude=".specify"` to tar creation options.
- Add `-x "specs/*" -x ".agents/*" -x ".specify/*"` to zip creation options.

### Component 2: `scripts/setup.sh`
- Replace `uv run python` calls during GPU offload check and profile matching with `.venv/bin/python` to prevent `uv` auto-sync from overwriting the restored CUDA prebuilt wheel.

### Component 3: `tests/unit/test_seed_pack.py`
- Add unit assertions testing archive exclusion rules and setup python runner isolation.

---

## Verification Plan

### Automated Tests
```bash
uv run pytest tests/unit/test_seed_pack.py
```

### Manual Verification
```bash
./scripts/make_seed_pack.sh --skip-legacy-build
tar -tzf dist/vllm_serv_seed.tar.gz | grep -E "^(specs/|\.agents/|\.specify/)"
./scripts/setup.sh
```

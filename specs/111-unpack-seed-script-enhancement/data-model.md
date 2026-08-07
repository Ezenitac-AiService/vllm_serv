# Data Model & Schema Specification: Seed Pack 복원 스크립트 (`unpack_seed.sh`)

**Feature Directory**: `specs/111-unpack-seed-script-enhancement`

---

## 1. Archive Format Specs (아카이브 메타데이터 구조)

### ArchiveTypeEnum
- `TAR_GZ`: POSIX Gzip Tarball (`.tar.gz`, `.tgz`), 바이너리 헤더 `\x1f\x8b`
- `ZIP`: PKZIP Archive (`.zip`), 바이너리 헤더 `PK\x03\x04`

### ArchiveMetadata
| 필드명 | 타입 | 설명 |
|--------|------|------|
| `archive_path` | String (Path) | 대상 시드 팩 아카이브 경로 |
| `format` | ArchiveTypeEnum | 감지된 포맷 (`TAR_GZ` / `ZIP`) |
| `size_bytes` | Integer | 아카이브 파일 용량 (바이트) |
| `file_count` | Integer | 수록된 전체 파일 개수 |
| `is_verified` | Boolean | 필수 파일 전수 수록 검증 통과 여부 |

---

## 2. CLI Execution Options Schema

### UnpackOptions
| 옵션명 | CLI 플래그 | 타입 | 기본값 | 설명 |
|--------|------------|------|--------|------|
| `input_path` | `-i`, `--input` | Path | Auto-detect | 복원 대상 아카이브 경로 |
| `target_dir` | `-t`, `--target-dir` | Path | `$BASE_DIR` | 압축 해제 목적지 디렉터리 |
| `force_overwrite` | `-f`, `--force-overwrite` | Boolean | `false` | 기존 파일 강제 덮어쓰기 여부 |
| `verify_only` | `--verify-only` | Boolean | `false` | 압축 해제 없이 사전 무결성 검증만 수행 |
| `run_setup` | `--run-setup` | Boolean | `false` | 압축 해제 완결 후 `./setup.sh` 자동 구동 |

---

## 3. Unpack Verification Contract Schema

### RequiredArchiveEntries
압축 해제 전후 반드시 검증되어야 하는 프로젝트 핵심 파일 목록:
- `config/platform_profiles.json` (멀티 플랫폼 하드웨어 가속 설정을 담은 프로필)
- `config/model_catalog.json` (LLM 모델 아키텍처 매핑)
- `src/core/gpu_detector.py` (GPU 디텍터)
- `scripts/start_server.sh` (데몬 서빙 제어 스크립트)
- `scripts/ensure_models.py` (모델 다운로드 모듈)
- `scripts/auxiliary_manager.py` (보조 매니저)
- `samples/common.py` (샘플 클라이언트 예제)
- `specs/` (명세서 디렉터리)

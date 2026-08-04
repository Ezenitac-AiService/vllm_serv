# Data Model & Domain Entities: `setup.sh` 필수 GGUF 모델 자동 점검 및 다운로드 통합 (`092-setup-auto-model-download`)

## Domain Entities

### 1. `ModelDownloadStatus` (모델 다운로드 상태 엔티티)

`scripts/ensure_models.py` 실행 시 각 모델별 검사 및 다운로드 결과 상태 엔티티.

- **Attributes**:
  - `model_id`: `str` - 모델 고유 식별자 (`qwen3.5-4b`, `bge-m3`, `bge-reranker-v2-m3`)
  - `file_path`: `str` - `models/` 내 GGUF 파일 경로
  - `is_present`: `bool` - 로컬 파일 존재 여부
  - `size_bytes`: `int` - 로컬 파일 용량 (바이트)
  - `download_status`: `str` - 다운로드 상태 (`EXISTS`, `DOWNLOADED`, `FAILED`, `SKIPPED`)

- **Validation Rules**:
  - `is_present == True`일 때 파일 용량은 예상 GGUF 크기 최소 기준(예: `qwen3.5-4b` > 1.5GB, `bge-m3` > 500MB)을 만족해야 함.
  - 파일 부재 시 `ModelDownloader.download_model()`을 호출하여 다운로드 수행.

---

### 2. `SetupPipelineStage` (원스톱 셋업 파이프라인 단계 엔티티)

`scripts/setup.sh` 실행 시 차례대로 구동되는 파이프라인 모듈 스크립트 엔티티.

- **Attributes**:
  - `stage_index`: `int` - 파이프라인 단계를 나타내는 인덱스 (0~6)
  - `stage_name`: `str` - 단계 설명 명칭
  - `script_path`: `str` - 실행할 모듈 스크립트 경로 (`scripts/common.sh`, `scripts/update_cuda_drivers.sh`, `scripts/seed_db.py`, `scripts/verify_wheel_binary.py`, `scripts/ensure_models.py`, `scripts/audit_assets.py`, `scripts/configure_firewall.sh`)
  - `is_critical`: `bool` - 실패 시 setup.sh 중단(Fail-Fast) 여부

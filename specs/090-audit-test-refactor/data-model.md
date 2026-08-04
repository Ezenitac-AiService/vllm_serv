# Data Model & Domain Entities: 학습 플랫폼 이관 코드 정밀 검토, 종합 테스트 및 구조적 리팩토링 (`090-audit-test-refactor`)

## Domain Entities

### 1. `AuditInventoryItem` (감사 대상 자산 엔티티)

학습 플랫폼에서 이관되어 현재 프로젝트 코드베이스에 존재하거나 혼재된 개별 파일 자산의 감사 상태 엔티티.

- **Attributes**:
  - `file_path`: `str` - 파일의 프로젝트 상대 경로 (예: `scripts/setup.sh`, `wheels/llama_cpp_python-0.3.7-cp311-cp311-linux_x86_64.whl`)
  - `source_origin`: `str` - 자산의 출처 (예: `dev_platform_base`, `learning_platform_088`, `generated_artifact`)
  - `status`: `str` - 감사 검증 상태 (`ACTIVE`, `DUPLICATE`, `LEGACY_REPLACED`, `UNVERIFIED`)
  - `action`: `str` - 정리 조치 방향 (`PRESERVE`, `ARCHIVE_TO_LEGACY`, `REFACTOR_INTEGRATE`)
  - `target_path`: `Optional[str]` - 격리 아카이빙 시 대상 경로 (예: `.legacy/archive_088_sync/scripts/setup.sh.bak`)

- **Validation Rules**:
  - `status`가 `LEGACY_REPLACED` 또는 `DUPLICATE`인 경우 `action`은 반드시 `ARCHIVE_TO_LEGACY`이어야 함.
  - 파괴적 영구 삭제(`rm`)는 허용되지 않으며 반드시 `.legacy/` 경로로 이동되어야 함.

---

### 2. `CudaEnvironmentProfile` (CUDA GPU 환경 프로필 엔티티)

시스템 내 NVIDIA GPU, 드라이버, CUDA Toolkit 및 cuDNN 버전 상태 프로필.

- **Attributes**:
  - `driver_version`: `str` - NVIDIA 드라이버 버전 (예: `535.129.03`)
  - `cuda_version`: `str` - CUDA Compiler/Runtime 버전 (예: `12.2`)
  - `cudnn_version`: `Optional[str]` - cuDNN 라이브러리 버전 (예: `8.9.7`)
  - `gpu_device_name`: `str` - 장착된 GPU 모델명 (예: `NVIDIA RTX 4090`)
  - `gpu_count`: `int` - 가용 GPU 개수 (최소 1 이상이어야 함)
  - `is_cuda_available`: `bool` - CUDA 가용 여부 (`True` 필수, `False` 시 단정 오류)

- **State Transitions**:
  - `DETECTING` -> `VALIDATED` (최소 버전 Driver>=525, CUDA>=12.0 충족 시)
  - `DETECTING` -> `FAILED` (NVIDIA GPU 미장착 또는 최소 버전 미달 시 Fail-Fast)

---

### 3. `VerificationTestSuite` (종합 검증 수트 엔티티)

이관 코드 및 리팩토링 결과물의 정상 작동을 입증하는 테스트 수트 엔티티.

- **Attributes**:
  - `suite_name`: `str` - 테스트 수트 명칭 (예: `test_cuda_env_detection`, `test_llamacpp_gpu_offload`, `test_sample_scripts_executability`)
  - `target_module`: `str` - 검증 대상 모듈 (예: `src/utils/cuda_env.py`, `samples/openai_01_chat.py`)
  - `test_type`: `str` - 테스트 성격 (`UNIT`, `INTEGRATION`, `E2E`)
  - `execution_command`: `str` - 실행 명령어 (`uv run pytest tests/test_cuda_env.py`)
  - `passed`: `bool` - 전체 케이스 Pass 여부 (100% Pass 필수)

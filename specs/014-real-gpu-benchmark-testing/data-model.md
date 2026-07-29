# Data Model Specification: Real GPU Benchmark Engine & Dual-Mode Test Framework

**Feature Directory**: `specs/014-real-gpu-benchmark-testing`  
**Created Date**: 2026-07-29  

---

## 1. Core Entities & Schemas

### Entity 1: `TestExecutionMode` (Enum)
- **Description**: Pytest 및 테스트 스크립트 실행 모드를 정의하는 열거형.
- **Fields**:
  - `MOCK` (`"mock"`): 단위 테스트 및 빠른 CI/CD 검증 모드.
  - `REAL` (`"real"`): 실제 NVIDIA GPU VRAM 로드, `llama-server` 프로세스 생성, HTTP 추론 검증 모드.

### Entity 2: `LlamaServerBinaryInfo` (Pydantic Model)
- **Description**: CUDA 지원 `llama-server` 바이너리 구축 및 검증 메타데이터.
- **Fields**:
  - `binary_path`: `str` (바이너리 파일 절대/상대 경로)
  - `is_cuda_enabled`: `bool` (CUDA 가속 호환 여부)
  - `build_source`: `str` (`"PATH"`, `"CMAKE_BUILD"`, `"PYTHON_MODULE_FALLBACK"`)
  - `version_info`: `Optional[str]` (`llama-server --version` 출력 문자열)

### Entity 3: `RealGpuBenchmarkSession` (Pydantic Model)
- **Description**: 6개 모델 원스톱 실측 GPU 벤치마크 루프 관리 세션 객체.
- **Fields**:
  - `session_id`: `str` (세션 고유 식별자)
  - `execution_mode`: `TestExecutionMode` (현재 실행 모드)
  - `target_models`: `List[str]` (벤치마크 대상 6개 모델 ID 리스트)
  - `completed_models`: `List[str]` (성공적으로 추론을 마친 모델 ID 리스트)
  - `failed_models`: `Dict[str, str]` (실패한 모델 ID 및 실패 원인 에러 메시지 매핑)
  - `vram_safety_threshold_mb`: `int` (OOM 차단을 위한 최대 허용 VRAM 용량: 11264 MB)

# Data Model & Domain Entities: 3대 멀티 플랫폼 HW 차등 감지 및 훈련 플랫폼(RTX 3060) 최적 하드웨어 가속 자동 설정 (`094-hardware-capability-autodetect`)

## Domain Entities

### 1. `HardwareProfileCapability` (하드웨어 플랫폼 감지 특성 엔티티)

3대 하드웨어 플랫폼(개발: GTX 1080Ti, 서비스: GTX 1070/i7-930, 훈련: RTX 3060/i7-4770) 감지 및 최적 가속 셋팅 엔티티.

- **Attributes**:
  - `platform_type`: `str` - 플랫폼 명칭 (`DEV_GTX1080TI`, `SVC_GTX1070_I7_930`, `TRAIN_RTX3060`)
  - `cpu_avx2_supported`: `bool` - CPU AVX2 명령어 지원 여부 (i7-930: `False`, Haswell+: `True`)
  - `gpu_name`: `str` - GPU 이름 (예: `NVIDIA GeForce RTX 3060`)
  - `compute_capability`: `float` - Compute Capability (Pascal: `6.1`, Ampere: `8.6`)
  - `tensor_cores_gen`: `int` - Tensor Cores 세대 (Pascal: `0` / 미지원, Ampere: `3`)
  - `supports_tf32`: `bool` - TF32 (TensorFloat-32) 지원 여부 (Pascal: `False`, Ampere: `True`)
  - `supports_bf16`: `bool` - BF16 (bfloat16) 데이터 타입 지원 여부 (Pascal: `False`, Ampere: `True`)
  - `supports_flash_attn2`: `bool` - FlashAttention-2 하드웨어 지원 여부 (Pascal: `False`, Ampere: `True`)
  - `cmake_args`: `List[str]` - 하드웨어 맞춤형 C++ 컴파일 플래그 목록
  - `recommended_runtime_flags`: `Dict[str, Any]` - 추천 런타임 플래그 (`n_gpu_layers`, `flash_attn`, `threads`)

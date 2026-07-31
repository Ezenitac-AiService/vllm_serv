# CLI Interface Contracts: 플랫폼 프로필 매칭 및 CMake 인자 서식 규격

## 1. `cpu_detector` CLI Commands

### 1.1 `uv run python -m src.core.cpu_detector --format cmake`

- **Purpose**: llama.cpp 빌드를 위한 CMake 플래그 문자열 생성
- **Expected Output Format**:
  ```text
  -DGGML_CUDA=ON -DGGML_AVX=ON -DGGML_AVX2=ON -DGGML_F16C=ON -DGGML_FMA=ON -DCMAKE_CUDA_ARCHITECTURES=61
  ```
- **Constraint**: 인자 간에 반드시 개별 공백(` `)이 보장되어야 하며, `-DGGML_F16C=ON-DGGML_FMA=ON` 과 같은 공백 누락이 발생해서는 안 된다.

### 1.2 `uv run python -m src.core.cpu_detector --match-profile`

- **Purpose**: 현 하드웨어와 매칭된 프로필 ID 출력
- **Expected Output Examples**:
  - Xeon E3-1231 v3 (AVX2) + GTX 1080 Ti (`sm_61`): `pascal-avx2-gtx1080ti`
  - Core i7 930 (SSE4.2) + GTX 1070 (`sm_61`): `legacy-i7-930-gtx1070`
  - RTX 3060 (`sm_86`): `dev-rtx3060`
- **Exit Code**: 0 (성공), 1 (실패)

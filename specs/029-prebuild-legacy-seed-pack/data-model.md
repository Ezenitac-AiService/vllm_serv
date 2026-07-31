# Data Model: 구형 i7-930 전용 사전 컴파일 라이브러리 시드 팩 (029-prebuild-legacy-seed-pack)

## Entities & Data Schemas

### 1. LegacyPrebuiltWheel (`wheels/legacy_i7_930/*.whl`)

i7-930 (Nehalem CPU, AVX/AVX2 미지원, CUDA 12.x GTX 1070) 호환 사전 컴파일 휠 엔티티.

**File Location**: `wheels/legacy_i7_930/llama_cpp_python-0.3.34-cp312-cp312-linux_x86_64.whl` (또는 해당 파이썬 버전 휠)

**Build Specification**:
- `CFLAGS`: `-march=x86-64`
- `CMAKE_ARGS`: `-DGGML_CUDA=ON -DGGML_AVX=OFF -DGGML_AVX2=OFF -DGGML_F16C=OFF -DGGML_FMA=OFF`

---

### 2. SeedPackArchive (`dist/vllm_serv_seed.tar.gz`)

시드 팩 생성 스크립트(`scripts/make_seed_pack.sh`)에 의해 생성되는 패키징 아카이브 엔티티.

```text
vllm_serv_seed.tar.gz
├── pyproject.toml
├── config/
│   ├── model_catalog.json
│   ├── platform_profiles.json
│   └── server_config.json
├── src/
├── scripts/
│   ├── setup.sh
│   ├── start_server.sh
│   ├── stop_server.sh
│   └── status_server.sh
└── wheels/
    └── legacy_i7_930/
        └── llama_cpp_python-*.whl   # FR-001: i7-930 전용 사전 빌드 휠
```

**State Transitions**:
1. **Packaging**: `scripts/make_seed_pack.sh` 실행 -> i7-930 휠 사전 컴파일 -> `wheels/legacy_i7_930/` 수록 -> `dist/vllm_serv_seed.tar.gz` 생성.
2. **Extraction & Installation**: i7-930 서버에 시드 팩 이관 -> `setup.sh` 실행 -> `legacy-i7-930-gtx1070` 프로필 감지 -> `wheels/legacy_i7_930/*.whl` 존재 확인 -> `uv pip install` 3초 주입 완료.

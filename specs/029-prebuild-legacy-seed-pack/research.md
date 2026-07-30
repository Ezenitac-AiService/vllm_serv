# Research Document: 구형 i7-930 플랫폼 전용 사전 컴파일 라이브러리 시드 팩(Seed Pack) 번들링 및 고속 구축 (029-prebuild-legacy-seed-pack)

## Decision 1: `make_seed_pack.sh` 구형 i7-930 전용 휠 사전 컴파일 및 번들링

### Decision
- `scripts/make_seed_pack.sh` 스크립트에 `--build-legacy` 옵션을 추가(기본 적용 또는 선택 적용).
- 휠 컴파일 시 호스트 CPU 벡터 명령어(AVX, AVX2, FMA 등)가 바이너리에 포함되어 i7-930에서 `Illegal Instruction` 에러가 발생하는 것을 막기 위하여 아래 환경변수 및 CMAKE 플래그를 주입:
  ```bash
  CFLAGS="-march=x86-64" \
  CMAKE_ARGS="-DGGML_CUDA=ON -DGGML_AVX=OFF -DGGML_AVX2=OFF -DGGML_F16C=OFF -DGGML_FMA=OFF" \
  uv pip wheel "llama-cpp-python[server]" --no-binary llama-cpp-python --wheel-dir wheels/legacy_i7_930
  ```
- 생성된 `.whl` 패키지를 `wheels/legacy_i7_930/` 디렉터리에 저장하고 시드 팩 아카이브(`dist/vllm_serv_seed.tar.gz`)에 포함.

### Rationale
- Platform A/B(Xeon E3 / Core i7-4770) 등 고성능 머신에서 시드 팩을 패키징할 때 1~2분 만에 i7-930 호환 휠을 컴파일해 둘 수 있습니다.
- i7-930 머신은 AVX/AVX2가 없는 1세대 Nehalem CPU이므로 `CFLAGS="-march=x86-64"`를 명시하여 명령어를 억제하고, GTX 1070 GPU 지원을 위해 `-DGGML_CUDA=ON`을 유지합니다.

---

## Decision 2: `setup.sh` i7-930 감지 시 `uv pip install` Fast-Track 주입

### Decision
- `scripts/setup.sh` 스크립트 실행 중 하드웨어 프로필 감지 단계에서 매칭된 프로필이 `legacy-i7-930-gtx1070`인 경우:
  1. `wheels/legacy_i7_930/` 내 사전 빌드된 `.whl` 파일 존재 여부 확인.
  2. 휠 파일 존재 시: 소스 재컴파일 과정(`uv pip install --no-binary ...`)을 건너뛰고 `uv pip install wheels/legacy_i7_930/*.whl` 명령어로 3초 만에 가상환경(`.venv`)에 무소스 주입.
  3. 주입 완료 후 기존과 동일하게 `llama_supports_gpu_offload()` CUDA 오프로드 검증 수행.

### Rationale
- 온디맨드 소스 컴파일 시 15~30분 이상 소요되던 i7-930 서버 구축 시간을 3분 이내(90% 이상 단축)로 단축할 수 있습니다.

---

## Decision 3: 사전 빌드 휠 유실 시 자동 Fallback 및 Platform A/B 컴파일 경로 유지

### Decision
- **i7-930 환경 휠 유실 시**: `wheels/legacy_i7_930/`에 `.whl` 파일이 없거나 설치 실패 시 경고 메시지 출력 후 기존 소스 컴파일 파이프라인(`CMAKE_ARGS="..." uv pip install ...`)으로 안전하게 Fallback.
- **Platform A / Platform B 환경**: 해당 장비는 AVX/AVX2 지원 고성능 머신이므로, 시드 팩의 i7-930 휠을 사용하지 않고 기존과 동일하게 해당 플랫폼 맞춤 CMAKE 옵션(AVX/AVX2 활성)으로 동적 소스 컴파일을 수행하여 성능 최적화를 유지.

### Rationale
- 시드 팩 유실 시에도 시스템 구축이 중단되지 않고, 고성능 장비의 AVX2 벡터 가속 성능 저하를 방지합니다.

# Quickstart & Validation Guide: CPU 빌드 감지 및 다중 플랫폼 지원

**Feature Branch**: `020-cpu-build-detection`  
**Date**: 2026-07-30  
**Spec**: [spec.md](file:///home/dev/storage/vllm_serv/specs/020-cpu-build-detection/spec.md)

---

## 1. 개요

본 검증 가이드는 i7 930 레거시 환경 및 기존 최신 CPU 환경에서 CPU 명령어 세트 자동 감지 및 CMake 빌드 플래그 설정이 올바르게 작동하는지 검증하기 위한 시나리오와 실행 명령어 모음을 제공합니다.

---

## 2. 검증 시나리오

### 시나리오 1: CPU 감지 모듈 단위 검증
호스트 시스템의 CPU 기능 및 CMake 빌드 플래그 생성 모듈을 단독으로 실행하고 출력을 확인합니다.

```bash
# 1.1 요약 리포트 출력 검증
uv run python -m src.core.cpu_detector --report

# 1.2 CMake 전달용 인자 한 줄 출력 검증
uv run python -m src.core.cpu_detector --format cmake

# 1.3 JSON 형태 정형 데이터 출력 검증
uv run python -m src.core.cpu_detector --format json
```

**기대 결과**:
- 감지된 CPU 모델명과 지원되는 명령어 세트 목록이 명확히 표시됨.
- AVX 미지원 CPU(i7 930 등)에서는 `-DGGML_AVX=OFF -DGGML_AVX2=OFF -DGGML_F16C=OFF -DGGML_FMA=OFF`가 플래그에 포함됨.

---

### 시나리오 2: `setup.sh` 동적 CMAKE_ARGS 전파 검증
`setup.sh` 스크립트 실행 시 CPU 감지 모듈을 통해 `llama-cpp-python` 빌드 옵션이 동적으로 결정되고 성공적으로 설치되는지 검증합니다.

```bash
# setup.sh 실행
./setup.sh
```

**기대 결과**:
- 로그에 CPU 감지 결과 및 적용된 `CMAKE_ARGS` 플래그가 출력됨.
- `llama-cpp-python` 설치 성공 후 GPU 가속 활성화 검증(`llama_supports_gpu_offload()`) 통과.

---

### 시나리오 3: 네이티브 `llama-server` CMake 컴파일 검증
`ProcessManager.verify_and_build_llama_server()` 함수를 통해 네이티브 `llama-server` 바이너리가 호스트 CPU 및 GPU에 맞는 플래그로 빌드되는지 검증합니다.

```bash
uv run pytest tests/unit/test_cpu_detector.py -v
```

**기대 결과**:
- CPU 감지 단위 테스트 및 `llama-server` 컴파일 명령 구성 테스트 100% 통과.

---

### 시나리오 4: `Illegal instruction` 실행 검증 (레거시 CPU 환경)
i7 930 환경 또는 모의 레거시 컴파일 환경에서 빌드된 바이너리가 크래시 없이 서빙 가능한지 검증합니다.

```bash
# status_server.sh로 상태 및 빌드 정보 확인
./status_server.sh
```

**기대 결과**:
- `Illegal instruction` SIGILL 오류 없이 정상 프로세스 구동 및 포트 바인딩 완료.

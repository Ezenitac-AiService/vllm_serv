# Phase 0 Research: Seed Pack Wheel Validation & Setup Failure Diagnostics

## Overview

본 조사는 `i7-930` (Nehalem) 타겟 시드 팩 복원 시 사전 빌드 휠 내 `libggml-cpu.so` 등에 AVX 명령어(4,307개)가 유입되는 현상을 방지하고, 불필요한 빌드 시간 연장을 막기 위한 파이썬 기반 바이너리 정밀 검증 및 `setup.sh` 진단 메커니즘을 설계합니다.

## Research Findings

### 1. 외부 도구 미의존 파이썬 순수 모듈 기반 바이너리 AVX 스캐너 (Pure-Python Binary Scanner)

- **Decision**: 외부 CLI 도구(`objdump`)에 의존하지 않고 파이썬 내장 모듈(`zipfile` + binary byte scanning)을 통해 `.whl` 파일 내부의 모든 `.so` 바이너리 전체를 전수 조사하는 스캐너 스크립트 작성.
- **Rationale**:
  - `objdump` 도구가 미설치된 CI/CD 서버 환경에서도 무조건 안정적으로 동작.
  - VEX Prefix (`0xc5`, `0xc4`) 및 AVX 명령어 바이트 opcode 시퀀스를 정밀 검출하여 0개 수록 여부를 정확히 진단.

### 2. 조건부 휠 재컴파일 및 Clean 로직

- **Decision**: `make_seed_pack.sh` 구동 시 기존 휠이 존재하는 경우 파이썬 바이너리 스캐너로 수용성을 먼저 검사.
- **Rationale**:
  - 검증 통과(AVX = 0개, CUDA 지원) 시 C++ 재컴파일(15~30분)을 0초만에 건너뛰고 기존 휠 재사용.
  - 검증 실패 시 기존 휠을 자동 삭제(Clean)하고 `FORCE_CMAKE=1 CFLAGS="-march=x86-64" CMAKE_ARGS="-DGGML_CUDA=ON -DGGML_AVX=OFF -DGGML_AVX2=OFF -DGGML_F16C=OFF -DGGML_FMA=OFF -DGGML_NATIVE=OFF -DCMAKE_CUDA_ARCHITECTURES=61"` 플래그로 새로 강제 컴파일.

### 3. `setup.sh` 구조화된 진단 에러 표출

- **Decision**: `setup.sh`에서 `2>/dev/null`로 에러를 억제하지 않고, 파이썬 검증 명령의 stderr와 Exit Code를 캡처하여 원인별 요약 분류 및 상세 Traceback 노출.
- **Rationale**:
  - `SIGILL` (Illegal Instruction - AVX 미지원 CPU), `CUDA Driver Error`, `ImportError` 등의 원인을 현장에서 1초 만에 식별 가능.

## Summary of Architectural Decisions

1. 파이썬 내장 스캐너 기반 휠 정밀 검증 로직 도입.
2. `make_seed_pack.sh` 조건부 휠 재컴파일 & 자동 Clean 적용.
3. `setup.sh` 에러 억제 제거 및 구조화된 1줄 핵심 진단 로그 + Traceback 표출.

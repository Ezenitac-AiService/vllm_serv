# Research & Technical Decisions: README.md 전면 재작성 (Rewrite README.md)

**Feature**: `specs/115-rewrite-readme-documentation`  
**Date**: 2026-08-08  

## Executive Summary

기존 README.md의 에이전트 전용 슬래시 커맨드/specs 내역을 정리하고, `vllm_serv` 프로젝트 운영 및 개발자를 위한 새로운 구조적 마크다운 문서 표준을 확립합니다.

---

## 1. Documentation Structure & Design Decisions

### Decision 1: 3단계 Quick Start 및 아키텍처 다이어그램 최상단 배치
- **Context**: 처음 프로젝트를 접하는 운영자/개발자가 긴 설명 없이 3단계 만에 원스톱으로 서버를 구동하고 API를 테스트할 수 있도록 지원.
- **Structure**:
  1. **Quick Start (3-Steps)**:
     - Step 1: 환경 설정 (`./setup.sh` 또는 `./setup.sh --wheel-path <PATH>`)
     - Step 2: 서버 가동 (`./start_server.sh`)
     - Step 3: OpenAI 호환 API 호출 테스트 (`curl http://localhost:8000/v1/chat/completions ...`)
  2. **System Architecture Diagram**: Mermaid 기반 LLM 서빙 엔진 + Web 대시보드 시각화 다이어그램.

### Decision 2: 루트 제어 쉘 스크립트 6종 표준 명세화
- **Target Scripts**:
  - `setup.sh`: 시스템 자동 탐지, C++ CUDA 휠 빌드/재설치, 벤치마크 (CLI 옵션: `--force-build`, `--wheel-path`, `--skip-build`, `--skip-benchmark`, `--force-benchmark`).
  - `start_server.sh`: LLM 프로세스 & Web API / Dashboard 백그라운드 가동 (`./start_server.sh`).
  - `status_server.sh`: 실시간 하드웨어/VRAM/PID 모니터링 (`./status_server.sh`).
  - `stop_server.sh`: 안전 종료 및 좀비 프로세스 포스 킬 (`./stop_server.sh`).
  - `make_seed_pack.sh`: 타겟 마이그레이션용 Seed Pack (.tar.gz) 아카이브 생성 (`./make_seed_pack.sh`).
  - `unpack_seed.sh`: 마이그레이션 타겟 서버 패키지 압축 해제 및 무결성 검증 (`./unpack_seed.sh`).

### Decision 3: scripts/ 유틸리티 및 src/ 아키텍처 체계화
- **scripts/**:
  - `benchmark_context_window.py`: VRAM 및 KV Cache 동적 벤치마킹.
  - `benchmark_quality.py`: 응답 품질 및 벤치마크 평가.
  - `verify_wheel_binary.py`: CUDA 휠 바이너리 가속 실측 검증.
  - `ensure_models.py`: 카탈로그 모델 자동 다운로드 CLI.
- **src/**:
  - `src/core/`: `ProcessManager`, `LlamaManager`, `CpuDetector`, `GpuDetector`, `ConfigManager`.
  - `src/api/`: `InferenceAPI` (OpenAI 호환 `/v1/chat/completions`, `/v1/models`), `DashboardAPI` (`/dashboard`), `AdminAPI` (`/admin`).
  - `src/eval/`: `QualityEvaluator`.

### Decision 4: 에이전트/Speckit 관련 모든 내용 배제
- `/speckit-*` slash command 설명, agents/ 워크플로우, `specs/` 내 하위 디렉터리 안내를 완전히 제거하여 pure server documentation으로 전환.

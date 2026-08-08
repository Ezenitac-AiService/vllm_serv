# Data Model & Document Layout: README.md 구조 명세

**Feature**: `specs/115-rewrite-readme-documentation`  
**Date**: 2026-08-08  

## Document Section Hierarchy

새롭게 구동될 `README.md` 문서의 세부 목차 구조 스키마입니다.

```text
README.md
├── 1. Title & Overview (vllm_serv 프로젝트 개요 및 주요 특징)
├── 2. System Architecture (Mermaid 시각화 다이어그램)
├── 3. Quick Start Guide (3-Step 빠른 시작: setup -> start -> OpenAI cURL)
├── 4. Root Control Scripts (루트 쉘 스크립트 6종 상세 가이드)
│   ├── setup.sh (옵션: --force-build, --wheel-path, --skip-build 등)
│   ├── start_server.sh
│   ├── status_server.sh
│   ├── stop_server.sh
│   ├── make_seed_pack.sh
│   └── unpack_seed.sh
├── 5. Python & Shell Utility Scripts (scripts/ 폴더 유틸리티 가이드)
│   ├── benchmark_context_window.py
│   ├── benchmark_quality.py
│   ├── verify_wheel_binary.py
│   └── ensure_models.py
├── 6. Core Engine & Web Server Architecture (src/ 디렉터리 구성)
│   ├── src/core/ (ProcessManager, GpuDetector, CpuDetector 등)
│   ├── src/api/ (OpenAI API 호환 엔드포인트 & Web UI 대시보드)
│   └── src/eval/ (응답 품질 평가기)
└── 7. Web Dashboard & API Specifications (포트 8000 엔드포인트 및 대시보드 UI 가이드)
```

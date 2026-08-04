# Implementation Plan: `setup.sh` 필수 GGUF 모델 자동 점검 및 다운로드 통합 (`092-setup-auto-model-download`)

**Branch**: `092-setup-auto-model-download` | **Date**: 2026-08-04 | **Spec**: [spec.md](file:///home/dev/storage/vllm_serv/specs/092-setup-auto-model-download/spec.md)

**Input**: Feature specification from `/specs/092-setup-auto-model-download/spec.md`

## Summary

`./setup.sh` 가동 시 `models/` 디렉토리를 정밀 검사하여 3종 필수 GGUF 모델(`qwen3.5-4b`, `bge-m3`, `bge-reranker-v2-m3`)의 존재 유무를 자동 감지하고, 미존재 시 독립 파이썬 헬퍼 스크립트(`scripts/ensure_models.py`)를 통해 원스톱으로 다운로드 배치를 완료합니다. 또한 `scripts/` 내 14개 기존 스크립트 모듈을 `setup.sh` 파이프라인 단계별로 모듈식 체이닝하여 원스톱 Zero-Touch 인프라 구축 파이프라인을 정돈합니다.

## Technical Context

**Language/Version**: Python 3.11+, Bash Shell

**Primary Dependencies**: `httpx`, `huggingface_hub`, `uv`, `pytest`

**Storage**: File system (`models/`, `config/`, `data/metrics.db`)

**Testing**: `pytest` (`uv run pytest tests/test_ensure_models.py`)

**Target Platform**: Linux server with NVIDIA CUDA GPU

**Project Type**: Infrastructure Setup Automation & Model Provisioning Helper

**Performance Goals**: 이미 모델 존재 시 점검 및 다운로드 스킵 시간 < 2초

**Constraints**: GPU 환경 강제 (Fail-Fast), 헌장 준수, Zero-Touch 원스톱 가동

**Scale/Scope**: `scripts/setup.sh`, `scripts/ensure_models.py`, `tests/test_ensure_models.py`, `scripts/make_seed_pack.sh`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] 계획서가 한국어로 작성되었는가? (언어 정책)
- [x] 테스트 코드 작성 계획이 포함되어 있는가? (테스트 필수 원칙)
- [x] 목업은 유료/제한 API로 엄격히 제한하고 실물 시스템/소켓/OS 인자 및 실제 호출 플래그(REAL_API_CALL=1) 기반 실측 검증 계획이 포함되어 있는가? (실체적 테스트 및 수렴 검증 원칙)
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (종료 조건 명확화 원칙)
- [x] 비파괴적 문서 수정 원칙을 준수하는가? (비파괴적 문서 수정 원칙)
- [x] uv 패키지 매니저 및 가상환경 격리 표준(uv run)을 준수하는가? (uv 패키지 및 환경 관리 원칙)
- [x] 전체 회귀 테스트 수트 및 Playwright 기반 E2E 브라우저 실측 검증 계획이 포함되어 있는가? (의무적 회귀 테스트 및 브라우저 E2E 검증 원칙)

## Project Structure

### Documentation (this feature)

```text
specs/092-setup-auto-model-download/
├── plan.md              # 이 문서 (/speckit-plan 생성)
├── research.md          # Phase 0 기술 결정 및 Rationale
├── data-model.md        # Phase 1 도메인 엔티티 정의
├── quickstart.md        # Phase 1 검증 가이드
├── contracts/           # Phase 1 계약 명세
│   └── ensure_models_contract.json
└── tasks.md             # Phase 2 구현 작업 목록 (/speckit-tasks 생성 예정)
```

### Source Code (repository root)

```text
scripts/
├── setup.sh             # [UPDATED] 원스톱 체이닝 파이프라인 (PCI/드라이버/DB/휠/모델/방화벽 일원화)
├── ensure_models.py     # [NEW] 필수 3종 GGUF 모델 자동 점검 및 다운로드 헬퍼 스크립트
├── common.sh            # 쉘 공통 믹스인
├── update_cuda_drivers.sh # CUDA 드라이버/Toolkit 패키지 자동 설치 헬퍼
├── seed_db.py           # DB 자동 초기화 스크립트
├── verify_wheel_binary.py # 휠 binary 가속 검증
├── audit_assets.py      # 레거시 자산 정돈 스크립트
├── configure_firewall.sh# 방화벽 복구 스크립트
└── make_seed_pack.sh    # 마이그레이션 아카이브 생성기

tests/
└── test_ensure_models.py # [NEW] 모델 프로비저닝 헬퍼 단위/통합 테스트
```

**Structure Decision**: 기존 `src/core/model_downloader.py`를 활용하는 `scripts/ensure_models.py` 파이썬 헬퍼를 추가하고, `scripts/setup.sh` 파이프라인에서 모듈식으로 체이닝 호출하는 깔끔한 아키텍처를 선택함.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | 위반 사항 없음 | N/A |

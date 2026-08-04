# Implementation Plan: 학습 플랫폼 이관 코드 정밀 검토, 종합 테스트 및 구조적 리팩토링 (`090-audit-test-refactor`)

**Branch**: `090-audit-test-refactor` | **Date**: 2026-08-04 | **Spec**: [spec.md](file:///home/dev/storage/vllm_serv/specs/090-audit-test-refactor/spec.md)

**Input**: Feature specification from `/specs/090-audit-test-refactor/spec.md`

## Summary

학습 플랫폼에서 가져온 088 스펙 이관 코드와 개발 플랫폼에 혼재된 자산을 전수 감사(Audit)하여 중복/레거시 파일을 `.legacy/archive_088_sync/`로 이동 격리하고, NVIDIA CUDA GPU 전용 환경 요구사항을 검증하는 자동화 테스트 수트(`pytest`) 구축 및 유틸리티 로직의 이중 공통 모듈화(`src/utils/cuda_env.py`, `scripts/common.sh`) 리팩토링을 수행합니다.

## Technical Context

**Language/Version**: Python 3.11, Bash Shell

**Primary Dependencies**: `pytest`, `uv`, `llama-cpp-python`, `httpx`, `openai`

**Storage**: File system (`specs/`, `scripts/`, `src/`, `samples/`, `.legacy/`)

**Testing**: `pytest` (`uv run pytest`), `bash -n`

**Target Platform**: Linux server (NVIDIA CUDA GPU 호스트 필수, GPU 미장착 시 Fail-Fast)

**Project Type**: CLI / System Build Automation & Python Package Management

**Performance Goals**: 전체 검증 테스트 수트 수행 시간 < 30초

**Constraints**: 100% 실측 CUDA GPU 검증(더미/Fake 테스트 전면 금지), 레거시 자산 `.legacy/` 아카이빙, `uv run` 표준 명령어 보장

**Scale/Scope**: `scripts/`, `src/`, `samples/`, `wheels/`, `tests/` 전반 자산 정밀 감사 및 구조 재정합

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
specs/090-audit-test-refactor/
├── plan.md              # 이 문서 (/speckit-plan 생성)
├── research.md          # Phase 0 기술 결정 및 Rationale
├── data-model.md        # Phase 1 도메인 엔티티 정의
├── quickstart.md        # Phase 1 검증 가이드
├── contracts/           # Phase 1 계약 명세
│   └── cuda_build_api.json
└── tasks.md             # Phase 2 구현 작업 목록 (/speckit-tasks 생성 예정)
```

### Source Code (repository root)

```text
src/
├── utils/
│   └── cuda_env.py       # [REFACTORED] 파이썬 공통 CUDA/드라이버 정밀 탐지 및 휠 검증 모듈
├── server/
└── dashboard/

scripts/
├── common.sh            # [REFACTORED] 쉘 공통 믹스인 (CUDA, OS, 패키지 검사)
├── setup.sh             # [UPDATED] 공통 믹스인 연동 서버 구축 스크립트
└── verify_wheel_binary.py # [UPDATED] 공통 모듈 참조 휠 검증 도구

samples/                 # 12종 실습 예제 스크립트 (sample_01~06, openai_01~06)

tests/
├── test_cuda_env.py     # [NEW] CUDA/GPU 정밀 탐지 및 휠 오프로드 단위/통합 테스트
└── test_sample_scripts.py # [NEW] 12종 샘플 스크립트 실행성 및 바인딩 검증 테스트

.legacy/
└── archive_088_sync/   # [NEW] 이관 및 혼재 자산 정밀 감사 후 격리 이동된 레거시 파일 보존소
```

**Structure Decision**: Single project layout 기반으로 파이썬 모듈(`src/utils/cuda_env.py`)과 쉘 모듈(`scripts/common.sh`)을 이중 공통 모듈화하고, `.legacy/archive_088_sync/` 경로로 레거시 자산을 격리 조치하는 구조를 선택함.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | 위반 사항 없음 (모든 헌장 원칙 100% 준수) | N/A |

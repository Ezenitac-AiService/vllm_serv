# Implementation Plan: 3대 멀티 플랫폼 HW 차등 감지 및 훈련 플랫폼(RTX 3060) 최적 하드웨어 가속 자동 설정 (`094-hardware-capability-autodetect`)

**Branch**: `094-hardware-capability-autodetect` | **Date**: 2026-08-04 | **Spec**: [spec.md](file:///home/dev/storage/vllm_serv/specs/094-hardware-capability-autodetect/spec.md)

**Input**: Feature specification from `/specs/094-hardware-capability-autodetect/spec.md`

## Summary

3대 멀티 하드웨어 플랫폼(개발: GTX 1080Ti / Pascal `sm_61`, 서비스: GTX 1070 / i7-930 Nehalem CPU 병목, 훈련: RTX 3060 / Ampere `sm_86` 무제한)에서 `./setup.sh` 구동 시 CPU 명령어 세트(AVX2 유무) 및 GPU Compute Capability (`sm_61` vs `sm_86`)를 2원 축으로 정밀 탐지하여, 훈련 플랫폼(RTX 3060)의 풀 가속 기능(3세대 Tensor Cores, TF32/BF16, FlashAttention-2 `LLAMA_FLASH_ATTN=ON`)을 100% 자동 활성화하고 서비스/개발 플랫폼의 하드웨어 병목 및 크래시를 근본 방지하는 차등 파이프라인을 구축합니다.

## Technical Context

**Language/Version**: Python 3.11+, Bash Shell (POSIX compliant), C++ CUDA Toolchain

**Primary Dependencies**: `uv`, `pytest`, `torch` / `psutil` / `nvidia-smi`

**Storage**: Configuration files (`config/model_catalog.json`, `config/server_config.json`)

**Testing**: `pytest` (`uv run pytest tests/unit/test_hardware_autodetect.py`)

**Target Platform**: Linux server across 3 hardware tiers (GTX 1080Ti, GTX 1070/i7-930, RTX 3060/i7-4770)

**Project Type**: Multi-Platform Hardware Auto-Detection & Compiler Tuning

**Performance Goals**: 하드웨어 자동 스캔 시간 < 0.05초, RTX 3060 가속 가동 시 추론 속도 (TPS) 최대 40% 향상

**Constraints**: i7-930 CPU 미지원 AVX2 컴파일 방지 (`Illegal Instruction` 차단) 및 Pascal GPU 미지원 FlashAttention-2 런타임 방지

**Scale/Scope**: `src/core/cpu_detector.py`, `scripts/common.sh`, `scripts/setup.sh`, `tests/unit/test_hardware_autodetect.py`

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
specs/094-hardware-capability-autodetect/
├── plan.md              # 이 문서 (/speckit-plan 생성)
├── research.md          # Phase 0 기술 결정 및 Rationale
├── data-model.md        # Phase 1 도메인 엔티티 정의
├── quickstart.md        # Phase 1 검증 가이드
├── contracts/           # Phase 1 계약 명세
│   └── hardware_autodetect_contract.json
└── tasks.md             # Phase 2 구현 작업 목록 (/speckit-tasks 생성 예정)
```

### Source Code (repository root)

```text
src/core/
└── cpu_detector.py      # [UPDATED] CPU AVX2 스캔, GPU sm_61/sm_86 감지 및 HardwareProfileCapability 반환

scripts/
├── common.sh            # [UPDATED] HW 프로파일 믹스인 (detect_hardware_profile, get_cmake_args)
└── setup.sh             # [UPDATED] HW 감지 파라미터 기반 llama-cpp-python 동적 C++ 컴파일 연동

tests/unit/
└── test_hardware_autodetect.py # [NEW] 3대 플랫폼 하드웨어 자동 감지 단위 테스트 수트 (Mock 포함)
```

**Structure Decision**: 기존 `src/core/cpu_detector.py`에 CPU AVX2 스캔과 Compute Capability 2원 축 스캐너를 추가하고, `scripts/common.sh` 믹스인에서 `setup.sh` 컴파일 인자를 동적 리턴하도록 깔끔히 구조화함.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | 위반 사항 없음 | N/A |

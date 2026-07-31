# Implementation Plan: 샘플 스크립트 실 IP 동적 자동 감지(192.168.0.x / 10.0.0.x / 듀얼 랜포트 지원) 및 연동 설정 개선

**Branch**: `064-sample-scripts-real-ip` | **Date**: 2026-07-31 | **Spec**: [spec.md](file:///home/dev/storage/vllm_serv/specs/064-sample-scripts-real-ip/spec.md)

**Input**: Feature specification from `specs/064-sample-scripts-real-ip/spec.md`

## Summary

본 계획서는 vllm_serv 3종 플랫폼(`192.168.0.x` 2종, `10.0.0.x` 1종) 및 듀얼 랜포트(미할당/다운 포트 필터링) 환경에서 하드코딩된 `127.0.0.1` 주소를 전면 제거하고, `src/core/network_detector.py`의 `NetworkDetector`를 통해 실제 통신 가능한 활성 호스트 LAN IP 주소를 동적으로 감지하여 `samples/common.py` 및 샘플 5종(`sample_01` ~ `sample_05`)의 API 엔드포인트(8081, 8090, 8091)에 실체적으로 적용하는 작업을 다룹니다.

## Technical Context

**Language/Version**: Python 3.11+, psutil, socket

**Primary Dependencies**: httpx, pydantic, psutil, pytest

**Storage**: SQLite (`data/metrics.db`), Local `.legacy/` schemas

**Testing**: pytest (`uv run pytest`) & direct script execution (`uv run python samples/sample_XX.py`)

**Target Platform**: Linux Server (3대 타겟 플랫폼: 192.168.0.x 2종, 10.0.0.x 1종, Dual LAN NIC)

**Project Type**: Web Service & LLM/Auxiliary Inference Platform Client Examples & Utilities

**Performance Goals**: 동적 LAN IP 탐지 지연 < 5ms, 실 IP 기반 샘플 통신 성공률 100%

**Constraints**: IP 하드코딩 금지, `SERVER_HOST` 환경변수 최우선 오버라이드 지원

**Scale/Scope**: 5개 예제 파일 모음 + `samples/common.py` + `tests/unit/test_sample_scripts.py`

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
specs/064-sample-scripts-real-ip/
├── spec.md              # Feature specification
├── plan.md              # Implementation plan (/speckit-plan command output)
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── real-ip-contract.json
└── checklists/
    └── requirements.md  # Specification quality checklist
```

### Source Code (repository root)

```text
src/
└── core/
    └── network_detector.py        # Active LAN IP detection & dual-LAN filter logic

samples/
├── common.py                      # get_server_host() dynamic host resolution helper
├── sample_01_chat.py              # Dynamic host chat completion sample
├── sample_02_model_params.py      # Dynamic host model params sample
├── sample_03_embedding.py         # Dynamic host BGE M3 embedding sample
├── sample_04_reranking.py         # Dynamic host BGE Reranker v2 M3 sample
└── sample_05_structured_output.py # Dynamic host Pydantic structured extraction sample

tests/
├── unit/
│   ├── test_sample_scripts.py     # Real IP host binding & sample execution tests
│   └── test_network_detector.py   # Dual-LAN and active LAN IP detection unit tests
```

**Structure Decision**: Single project layout utilizing `src/core/network_detector.py` within `samples/common.py` and regression test suites.

## Complexity Tracking

*No violations.*

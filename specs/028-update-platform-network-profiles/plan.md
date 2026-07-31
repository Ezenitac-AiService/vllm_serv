# Implementation Plan: 멀티 플랫폼 하드웨어 사양(16GB RAM) 및 서브넷 네트워크 토폴로지(10.0.0.x vs 192.168.0.x) 보정 (028-update-platform-network-profiles)

**Branch**: `028-update-platform-network-profiles` | **Date**: 2026-07-30 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/028-update-platform-network-profiles/spec.md`

## Summary

훈련생 팀 프로젝트 서버(Platform B) 물리 RAM 사양을 16GB로 정정하고, 개발망(`10.0.0.0/8`) 및 훈련/서비스망(`192.168.0.0/16`) 서브넷 대역을 프로필에 명확히 격리 반영합니다. `server_config.json` 내 static 11264MB VRAM 고정값을 제거하고 NVML 및 프로필 기반 동적 VRAM 바인딩으로 전환하며, `admin_secret` 관리자 암호 명시화 및 `VLLM_ADMIN_SECRET` 환경변수 오버라이드를 지원합니다. 컨텍스트 윈도우 스케일링 벤치마크 결과를 기반으로 소형 모델(2B/4B)의 컨텍스트 확장(8K~16K) 및 대형 모델(9B/12B)의 상한(4K=4096)을 동적 제어하고, 초과 시 HTTP 400 Bad Request 에러를 반환합니다. `scripts/setup.sh` 구축 파이프라인에서 컨텍스트 벤치마크를 non-blocking으로 연동하고 실패 시 자동 fallback 처리합니다.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI, Pydantic v2, pytest, uv, nvidia-smi / NVML (llama-cpp-python)
**Storage**: JSON 파일 기반 구성 (`config/platform_profiles.json`, `config/server_config.json`, `config/model_catalog.json`, `config/model_context_profiles.json`)
**Testing**: pytest (`uv run pytest`)
**Target Platform**: Linux x86_64 (Ubuntu Server 24.04 LTS / Debian)
**Project Type**: LLM 인퍼런스 API 웹 서비스 / CLI 도구
**Performance Goals**: 서브넷 필터링 및 프로필 감지 Overhead <1ms, 런타임 컨텍스트 검증 0ms (캐시 로드), setup.sh 파이프라인 중단 없는 non-blocking 벤치마크
**Constraints**: Platform B RAM = 16GB, Platform A 서브넷 = 10.0.0.0/8, Platform B/C 서브넷 = 192.168.0.0/16, max_n_ctx 초과 시 HTTP 400 응답
**Scale/Scope**: 3개 하드웨어 타겟 플랫폼 프로필 (Platform A, B, C), 6개 모델 프리셋

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] 계획서가 한국어로 작성되었는가? (언어 정책 준수)
- [x] 테스트 코드 작성 계획이 포함되어 있는가? (테스트 주도 개발 원칙 준수)
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (DoD 명확화 원칙 준수)

## Project Structure

### Documentation (this feature)

```text
specs/028-update-platform-network-profiles/
├── spec.md              # Feature specification
├── plan.md              # Implementation plan (/speckit-plan command output)
├── research.md          # Phase 0 output (research findings & decisions)
├── data-model.md        # Phase 1 output (data models & JSON schemas)
├── quickstart.md        # Phase 1 output (validation & testing guide)
└── contracts/           # Phase 1 output (interface contracts)
    └── admin-and-error-api.md
```

### Source Code (repository root)

```text
config/
├── platform_profiles.json       # FR-001, FR-002, FR-003: RAM 16GB 및 서브넷 대역 수정
├── server_config.json           # FR-004, FR-005: static VRAM 제거 및 admin_secret 표기
└── model_catalog.json          # FR-006: default_n_ctx / max_n_ctx 명세

src/
├── core/
│   ├── config_manager.py       # FR-001~FR-005: RAM, VRAM, admin_secret 로딩 및 검증
│   ├── network_detector.py     # FR-002, FR-003: 서브넷 IP 인가 검증
│   └── llama_manager.py        # FR-006: n_ctx 상한 검증 및 400 Bad Request 트리거
├── api/
│   ├── server.py               # FR-005, FR-006: admin secret 및 400 에러 처리 핸들러
│   └── middleware/
│       └── subnet_filter.py    # FR-002, FR-003: 서브넷 대역 검증 미들웨어
└── scripts/
    └── benchmark_context_scaling.py # FR-006: VRAM 실측 연동 벤치마크

scripts/
└── setup.sh                    # FR-007: non-blocking 벤치마크 실행 & fallback 연동

tests/
└── unit/
    ├── test_config_manager_profiles.py # unit test
    ├── test_network_detector.py         # unit test
    └── test_context_scaling_limits.py  # unit test
```

**Structure Decision**: 기존 단일 웹 서비스/CLI 모듈 구조(`src/core`, `src/api`, `config/`, `scripts/`, `tests/unit/`)를 활용하여 추가 리팩토링 비용 없이 정합성을 확보합니다.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (None) | N/A | N/A |

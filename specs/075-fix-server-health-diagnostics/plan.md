# Implementation Plan: 서버 헬스진단 스크립트 정밀화 및 8082 대시보드 연동 복구

**Branch**: `075-fix-server-health-diagnostics` | **Date**: 2026-08-03 | **Spec**: [specs/075-fix-server-health-diagnostics/spec.md](file:///home/dev/storage/vllm_serv/specs/075-fix-server-health-diagnostics/spec.md)

**Input**: Feature specification from `/specs/075-fix-server-health-diagnostics/spec.md`

## Summary

본 구현 계획서는 서비스 플랫폼 배포 후 `./status_server.sh` 및 `diagnose_server_health.py` 진단 리포트에서 관측된 Port 8082 웹 대시보드 차단/미구동(CLOSED/BLOCKED) 및 `/v1/chat/completions` 프로브 미도달(UNREACHABLE) 경고를 해결하는 기술 구현 계획을 정의합니다. `./start_server.sh` 원스톱 프로세스 연동, `scripts/setup.sh` 방화벽 8081/8082 개방 등록, `diagnose_server_health.py` 파이썬 dict 기반 대화 프로브 정밀화를 통해 진단 상태를 100% HEALTHY(ALL GREEN)로 전환합니다.

## Technical Context

**Language/Version**: Python 3.12, Bash (managed via `uv`)

**Primary Dependencies**: FastAPI, Uvicorn, httpx, llama-cpp-python

**Storage**: N/A (진단 및 프로세스 헬스체크)

**Testing**: `uv run python scripts/diagnose_server_health.py` & `uv run pytest`

**Target Platform**: Linux x86_64 / NVIDIA CUDA / Multi-port Server Environment

**Project Type**: Infrastructure Server Diagnostics & Web Dashboard Integration

**Performance Goals**: 통합 진단 헬스체크 수행 시간 5초 이내, ALL GREEN 판정 100%

**Constraints**: Zero-Mock 원칙 준수, 헌법 7대 원칙 준수

## Constitution Check

- [x] 계획서가 한국어로 작성되었는가? (언어 정책 준수)
- [x] 테스트 코드 작성 계획이 포함되어 있는가? (테스트 필수 원칙 준수)
- [x] 목업은 유료/제한 API로 엄격히 제한하고 실물 시스템/소켓/OS 인자 기반 실측 검증 계획이 포함되어 있는가? (Zero Mock 원칙 준수)
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (종료 조건 명확화 원칙 준수)
- [x] 비파괴적 문서 수정 원칙을 준수하는가? (비파괴적 문서 수정 원칙 준수)
- [x] uv 패키지 매니저 및 가상환경 격리 표준(uv run)을 준수하는가? (uv 패키지 원칙 준수)
- [x] 전체 회귀 테스트 수트 실행 계획이 포함되어 있는가? (의무적 회귀 테스트 원칙 준수)

## Project Structure

### Documentation (this feature)

```text
specs/075-fix-server-health-diagnostics/
├── plan.md              # 이 계획서
├── research.md          # Phase 0 연구 결과 문서
├── data-model.md        # Phase 1 엔티티 및 포트 구조 문서
├── quickstart.md        # Phase 1 실측 검증 가이드
├── contracts/           # Phase 1 계약 스키마 (health-probe-contract.json)
└── tasks.md             # Phase 2 과제 목록 (/speckit-tasks 명령어로 수립 예정)
```

### Source Code (repository root)

```text
start_server.sh                  # 메인 LLM 백엔드 + REST API + Port 8082 대시보드 원스톱 가동
status_server.sh                 # Port 8081 & Port 8082 상태 리포팅
scripts/
├── setup.sh                     # UFW 방화벽 8081/8082/8090/8091 허용 규칙 자동 등록
└── diagnose_server_health.py    # 파이썬 dict 기반 /v1/chat/completions 정밀 프로브 진단 스크립트
```

## Complexity Tracking

*(헌법 7대 원칙 100% 준수 - 위반 사항 없음)*

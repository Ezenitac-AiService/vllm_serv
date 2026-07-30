# Implementation Plan: vLLM 서빙 대시보드 고도화 (vLLM Dashboard Enhancement)

**Branch**: `037-dashboard-enhancement` | **Date**: 2026-07-30 | **Spec**: [`spec.md`](file:///home/dev/storage/vllm_serv/specs/037-dashboard-enhancement/spec.md)

**Input**: Feature specification from `/specs/037-dashboard-enhancement/spec.md`

## Summary

본 계획은 기존 단순 텍스트 지표 위주의 vLLM 대시보드를 **2026년 최신 AI 플랫폼(OpenAI Playground, Google AI Studio, LM Studio, Ollama) 표준 UI/UX**에 기반한 4대 탭(📊 메트릭 모니터링, ⚙️ 모델 및 파라미터 동적 제어, 🎮 인터랙티브 LLM 플레이그라운드, 🔑 API Key & 서브넷 감사 로그) 단일 페이지 애플리케이션(SPA)으로 완전 고도화합니다. Chart.js 캔버스 시계열 그래프 적용, 플랫폼 프로필 연동 동적 모델 목록 바인딩, Admin Secret 헤더 기반 보안 강화(`401 Unauthorized`), 그리고 TTFT(ms) / tok/s 실측 지표가 표출되는 Playground 패널 및 cURL/Python Code Export 기능을 제공합니다.

## Technical Context

**Language/Version**: Python 3.12 (FastAPI), HTML5 / JavaScript (ES6 SPA), Vanilla CSS (Glassmorphism Dark Mode)  
**Primary Dependencies**: FastAPI, Chart.js (v4.4 via static/CDN), pydantic, `psutil`, `pynvml` (NVIDIA Management Library)  
**Storage**: Memory / Config JSON (`config/model_catalog.json`, `config/platform_profiles.json`, `config/api_keys.json`)  
**Testing**: `pytest` (`uv run pytest tests/unit/test_dashboard_api.py -v`)  
**Target Platform**: Linux Server (Platform A 10.0.0.41 / NVIDIA GPU + NVML)  
**Project Type**: Embedded Web Service / Dashboard API  
**Performance Goals**: 웹 대시보드 로딩 1.5초 이내, 실시간 차트 업데이트 간 브라우저 CPU 5% 미만, 모델 오프로드 및 서빙 전환 3초 이내  
**Constraints**: 100% 오프라인 동작 가능, 외부 프레임워크 빌드 스텝(React/Vue) 미사용 초경량 아키텍처, `uv run` 격리 표준 준수  
**Scale/Scope**: 서빙 대시보드 전용 SPA 4대 탭, `/dashboard/api/*` 엔드포인트 세트  

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] 계획서가 한국어로 작성되었는가? (언어 정책 준수)
- [x] 테스트 코드 작성 계획이 포함되어 있는가? (`tests/unit/test_dashboard_api.py` TDD)
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (DoD-001 ~ DoD-005 정의 완료)
- [x] 비파괴적 문서 수정 원칙을 준수하는가? (기존 문서 개별 편집 원칙 준수)
- [x] uv 패키지 매니저 및 가상환경 격리 표준(uv run)을 준수하는가? (`uv run pytest`, `uv sync` 준수)

## Project Structure

### Documentation (this feature)

```text
specs/037-dashboard-enhancement/
├── plan.md              # 본 계획서 (/speckit-plan command output)
├── research.md          # Phase 0 연구 문서 (UI/UX 벤치마크 & 아키텍처 결정)
├── data-model.md        # Phase 1 데이터 모델 (Metrics, AuditLog, Playground)
├── quickstart.md        # Phase 1 검증 가이드 및 시연 절차
├── contracts/           # API 인터페이스 정의 (dashboard_enhancement_contract.json)
└── checklists/
    └── requirements.md  # 스펙 품질 검증 체크리스트
```

### Source Code (repository root)

```text
src/
├── api/
│   ├── routes/
│   │   └── dashboard_api.py      # 대시보드 REST & SSE 스트리밍 / 감사 로그 / Admin 인증 API
│   ├── middleware/
│   │   └── client_access_logger.py # 클라이언트 IP 및 서브넷 감사 로그 미들웨어
│   └── static/
│       ├── index.html            # 4대 탭 SPA 레아아웃 (Monitoring, Control, Playground, Audit)
│       ├── style.css             # Glassmorphism 다크 테마 디자인 시스템
│       └── app.js                # Chart.js 시계열 그래프, SSE 갱신, Admin Auth 모달, Playground 스트리밍
└── core/
    └── model_manager.py          # 동적 모델 오프로드 및 서빙 전환 제어기

tests/
└── unit/
    └── test_dashboard_api.py     # 대시보드 API, Admin Secret 보안 미들웨어, Playground 테스트
```

**Structure Decision**: FastAPI 백엔드 엔드포인트(`src/api/routes/dashboard_api.py`)와 단일 페이지 애플리케이션(SPA) 프론트엔드 자원(`src/api/static/`)을 결합하는 임베디드 웹 서비스 아키텍처 구조를 준수합니다.

## Complexity Tracking

*No constitution violations. Architecture is fully compliant.*

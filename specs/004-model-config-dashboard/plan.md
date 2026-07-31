# Implementation Plan: 모델 설정 웹 대시보드

**Branch**: `004-model-config-dashboard` | **Date**: 2026-07-10 | **Spec**: [spec.md](spec.md)

## Summary

이 계획서는 vLLM 서버의 동적 모델 교체와 설정을 시각적으로 관리하기 위한 웹 대시보드 아키텍처를 정의합니다. 2026년 최신 서빙 트렌드(Continuous Batching, OOM 생존력 확보)를 반영하여, FastAPI 대시보드가 직접 모델을 로드하지 않고 공식 `llama-server`를 하위 프로세스(Subprocess)로 관리하며 추론 요청을 중계(Reverse Proxy)하는 아키텍처를 채택했습니다. FastAPI의 Server-Sent Events(SSE)를 활용한 실시간 상태 스트리밍과, 모델 로딩 중 503 Maintenance Mode 유예 처리가 핵심 백엔드 기능이며, 프론트엔드는 빌드 없이 구동되는 가벼운 모던 바닐라 JS(Glassmorphism UI)로 구축됩니다.

## Technical Context

**Language/Version**: Python 3.10+ (Backend), HTML/JS/CSS (Frontend)

**Primary Dependencies**: FastAPI, llama-cpp-python (서버 모듈), httpx (프록시 용도)

**Storage**: JSON 기반 파일 시스템 영속성 (`config/model_config.json`)

**Testing**: pytest

**Target Platform**: Linux Server (로컬 바인딩 전용)

**Project Type**: Web Service + Single Page Application

**Performance Goals**: UI 입력 후 유효성 검사 < 100ms 지연, 실시간 SSE 스트림 반응 속도 확보

**Constraints**: 로컬 전용이나 단일 환경변수 Token 기반 보안 적용 (단, SSE 스트림 구독 시 `EventSource`의 헤더 전송 제약으로 인해 Query 파라미터나 Cookie 기반 토큰 전달 방식 설계 필요). 모델 언로드/리로드 동작(`llama_cpp` 초기화)은 반드시 백그라운드 스레드(`asyncio.to_thread`)로 오프로딩되어야 하며, 이를 통해 최대 60초간의 작업 중에도 FastAPI 이벤트 루프가 블로킹되지 않도록 하여 SSE 이벤트와 503 HTTP 코드가 정상적으로 우아하게 실패(Graceful Degradation) 처리되어야 함. 503 차단 미들웨어는 단순 `/v1` 전체가 아닌 추론 타겟 API(`/v1/chat/completions`, `/v1/completions`)로 범위를 좁혀 상태 조회가 가능하도록 설계해야 함.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] 계획서가 한국어로 작성되었는가? (언어 정책)
- [x] 테스트 코드 작성 계획이 포함되어 있는가? (테스트 필수 원칙) -> 단위 및 통합 테스트 작성 예정.
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (종료 조건 명확화 원칙) -> spec.md에 명시 완료.

## Project Structure

### Documentation (this feature)

```text
specs/004-model-config-dashboard/
├── plan.md              # 이 파일
├── research.md          # SSE 및 503 모드 리서치
├── data-model.md        # 서버 상태 및 프리셋 스키마
├── quickstart.md        # 실행 및 검증 시나리오 가이드
└── tasks.md             # 다음 단계에서 생성 예정
```

### Source Code (repository root)

```text
src/
├── api/
│   ├── main.py                  # 정적 파일 서빙, 라우팅 마운트, 503 미들웨어 통합
│   ├── routes/
│   │   ├── dashboard_api.py     # SSE 및 설정 변경 엔드포인트
│   │   └── inference_api.py     # 기존 /v1/chat API (503 연동)
│   └── static/                  # 웹 대시보드 에셋
│       ├── index.html           
│       ├── style.css            # 모던 Glassmorphism UI
│       └── app.js               # SSE 구독 및 DOM 제어
├── core/
│   ├── llama_manager.py         # Subprocess(llama-server) 라이프사이클 관리
│   └── config_manager.py        # JSON 설정 파일 읽기/쓰기 영속화
└── tests/
    └── integration/
        └── test_dashboard.py    # 503 전환 및 SSE 상태 테스트
```

**Structure Decision**: 기존 `vllm_serv`의 FastAPI 백엔드(`src/api`)에 정적 서빙 라우터를 추가하고, 단일 페이지 앱(SPA) 형태로 대시보드를 추가하는 Option 1(Single Project) 구조를 채택했습니다. 이는 독립적인 프론트엔드 레포지토리를 만들 필요 없이 로컬 운영의 복잡성을 낮추기 위함입니다.

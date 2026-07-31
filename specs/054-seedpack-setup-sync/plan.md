# Implementation Plan: 신규 스펙(임베딩/리랭커 서빙 및 방화벽 포트 등)의 Seed Pack 및 setup.sh 동기화 반영 (054-seedpack-setup-sync)

**Branch**: `054-seedpack-setup-sync` | **Date**: 2026-07-31 | **Spec**: [spec.md](file:///home/dev/storage/vllm_serv/specs/054-seedpack-setup-sync/spec.md)

**Input**: Feature specification from `/specs/054-seedpack-setup-sync/spec.md`

---

## Summary

최근 추가된 임베딩(bge-m3, 8090 포트) 및 리랭커(bge-reranker-v2-m3, 8091 포트) 서빙 백엔드 인프라와 핵심 관리 모듈(`src/core/auxiliary_manager.py`)을 프로젝트 원스톱 설정 스크립트(`scripts/setup.sh`), 방화벽 설정 복구 스크립트(`scripts/configure_firewall.sh`), 이관용 Seed Pack 아카이브 스크립트(`scripts/make_seed_pack.sh`), 그리고 DB 초기화 시드 데이터 스크립트(`scripts/seed_db.py`)에 동기화 반영합니다.
이를 통해 OS 방화벽 4개 포트(`8081`, `8089`, `8090`, `8091`) 자동 개방, 필수 파일 검증, Seed Pack 패키징 무결성, 그리고 초기 대시보드 모니터링 시드 데이터 주입을 100% 보장합니다.

---

## Technical Context

**Language/Version**: Python 3.11+ (Bash 4.4+ for `setup.sh` and `make_seed_pack.sh`)

**Primary Dependencies**: `uv`, `sqlite3`, `tar`, `gzip`, `zip`, `pytest`, `httpx`

**Storage**: SQLite (`data/metrics.db`), JSON (`config/server_config.json`, `config/model_catalog.json`)

**Testing**: `pytest`, `uv run pytest tests/unit/test_seed_pack.py tests/integration/test_migration_pipeline.py`

**Target Platform**: Linux x86_64 (UFW, firewalld, nftables, iptables OS firewall environments)

**Project Type**: System Setup Automation Scripts & Python Microservice Control Layer

**Performance Goals**: `setup.sh` 방화벽 등록 < 1s, `make_seed_pack.sh` 아카이브 패키징 < 5s, `seed_db.py` 주입 < 1s

**Constraints**: `uv run` 표준 격리 준수, 4개 서비스 포트(8081, 8089, 8090, 8091) 일괄 동기화, Seed Pack 생성 시 대용량 `models/` 제외

**Scale/Scope**: 4개 핵심 쉘/파이썬 스크립트 수정, 2개 전용 테스트 수트 확장

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] 계획서가 한국어로 작성되었는가? (언어 정책)
- [x] 테스트 코드 작성 계획이 포함되어 있는가? (`tests/unit/test_seed_pack.py` 및 `tests/integration/test_migration_pipeline.py` 확장) (테스트 필수 원칙)
- [x] 목업은 유료/제한 API로 엄격히 제한하고 실물 시스템/소켓/OS 인자 및 실제 호출 플래그(REAL_API_CALL=1) 기반 실측 검증 계획이 포함되어 있는가? (실체적 테스트 및 수렴 검증 원칙)
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (종료 조건 명확화 원칙)
- [x] 비파괴적 문서 수정 원칙을 준수하는가? (비파괴적 문서 수정 원칙)
- [x] uv 패키지 매니저 및 가상환경 격리 표준(uv run)을 준수하는가? (uv 패키지 및 환경 관리 원칙)
- [x] 전체 회귀 테스트 수트 및 Playwright 기반 E2E 브라우저 실측 검증 계획이 포함되어 있는가? (의무적 회귀 테스트 및 브라우저 E2E 검증 원칙)

---

## Project Structure

### Documentation (this feature)

```text
specs/054-seedpack-setup-sync/
├── plan.md              # Implementation Plan (/speckit-plan command output)
├── research.md          # Phase 0 research output
├── data-model.md        # Phase 1 data model specification
├── quickstart.md        # Phase 1 quickstart validation guide
├── contracts/           # Phase 1 interface contract specifications
│   └── seedpack-setup-api.json
└── tasks.md             # Phase 2 tasks breakdown (/speckit-tasks command output)
```

### Source Code (repository root)

```text
scripts/
├── setup.sh                 # FIREWALL_PORTS (8081 8089 8090 8091) & REQUIRED_FILES (auxiliary_manager.py)
├── configure_firewall.sh   # 4개 포트 복구 개방
├── make_seed_pack.sh        # auxiliary_manager.py 및 카탈로그 무결성 검증 추가
└── seed_db.py              # /v1/embeddings & /v1/rerank 샘플 시드 메트릭 주입

tests/
├── unit/
│   └── test_seed_pack.py   # Seed Pack 및 setup 스크립트 동기화 단위 테스트
└── integration/
    └── test_migration_pipeline.py # 타겟 서버 마이그레이션 및 파이프라인 통합 테스트
```

**Structure Decision**: Single project layout updating standard repository shell scripts (`scripts/`) and Python DB seeding logic (`scripts/seed_db.py`) along with test coverage (`tests/`).

---

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | None (모든 헌법 규정 준수) | N/A |

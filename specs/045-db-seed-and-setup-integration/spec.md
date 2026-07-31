# Feature Specification: SQLite 메트릭 DB 시드 팩 및 서버 셋업 로직 연동 (045-db-seed-and-setup-integration)

**Feature Branch**: `045-db-seed-and-setup-integration`  
**Created**: 2026-07-30  
**Status**: Draft  
**Input**: User request: "우리 로그에 db도입했는데, 시드 팩과 서버셋팅 로직에도 반영해야 하지 않을까? (scripts/setup.sh 및 서버 셋업 시 SQLite metrics.db 초기화, schema 마이그레이션, 개발/초기 시드 데이터 자동 주입 반영)"

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 서버 셋업 및 초기 시작 시 SQLite DB 자동 생성 & 시드 팩 주입 (Priority: P1) 🎯 MVP

신규 환경이나 서버 초기 구동(`scripts/setup.sh` 또는 `scripts/start_server.sh`) 시, **[data/metrics.db]** SQLite 데이터베이스 및 디렉터리가 자동으로 보장 생성되고, 초기 개발 테스트용 샘플 로그 메트릭 및 시드 데이터(Seed Data Pack)가 안전하게 시딩(Seeding)되도록 합니다.

**Why this priority**: 처음 서버를 배포하거나 셋업을 마친 개발자/운영자가 대시보드 탭에 접속했을 때 비어있는 에러 대신 즉시 시드 데이터 기반의 풍부한 메트릭 그래프와 Top 5 키 랭킹을 조망할 수 있습니다.

**Independent Test**:
1. `rm -rf data/metrics.db` 실행 후 `scripts/setup.sh` 또는 서버 기동 시 `data/metrics.db`가 새로 생성되고 시드 데이터가 자동 주입되는지 확인.

---

### User Story 2 - CLI DB Reset & Seed Script 지원 (Priority: P2)

운영자 및 개발자가 필요에 따라 메트릭 DB를 초기화하거나 시드 데이터를 재주입할 수 있는 `python scripts/seed_db.py` CLI 헬퍼 명령어를 제공합니다.

**Why this priority**: 부하 테스트 후 DB를 클린업하거나 데모 환경을 신속히 복원하기 위해 손쉬운 시드 초기화 명령어가 필요합니다.

---

## Functional Requirements *(mandatory)*

- **FR-001**: `scripts/setup.sh` 스크립트에 `data/` 디렉터리 생성 및 SQLite `data/metrics.db` 자동 초기화 검사 로직을 수록해야 한다.
- **FR-002**: `scripts/seed_db.py` 모듈을 신설하여, 개발용 테스트 시드 키(`sk-vllm-dev`, `sk-vllm-demo`) 및 샘플 요청 이력 10건(성공/에러, 토큰 수, 프롬프트/대답 Payload 포함)을 원자적으로 주입할 수 있게 해야 한다.
- **FR-003**: `src/core/metrics_db.py` 서버 부팅 시 DB 파일이 존재하지 않는 경우 자동으로 `seed_db.py`의 시드 팩을 기본 주입(Auto-seeding)하도록 안전 처리해야 한다.
- **FR-004**: Anti-Mock 헌법 v1.4.0에 따라 `scripts/seed_db.py` 실행 및 시드 데이터 주입 검증 실측 테스트 수트(`tests/unit/test_db_seed_integration.py`)를 수록해야 한다.

---

## Success Criteria *(mandatory)*

- **SC-001**: DB 부재 상태에서 `scripts/setup.sh` 구동 시 시드 주입 성공률 **100%**.
- **SC-002**: `python scripts/seed_db.py` 초기화 실행 시간 **<500ms**.
- **SC-003**: 신규 환경 기동 후 대시보드 메트릭 및 Top 5 카드 시드 데이터 표출 정확도 **100%**.

---

## Key Entities *(optional)*

- **Seed Data Pack Structure (`scripts/seed_db.py`)**:
  - Sample API Keys: `sk-vllm-dev-demo1`, `sk-vllm-mobile-app`
  - Sample Logs: 10 rows of mock inference records with realistic TTFT, TPS, prompt & completion text.

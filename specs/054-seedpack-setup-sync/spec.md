# Feature Specification: 신규 스펙(임베딩/리랭커 서빙 및 방화벽 포트 등)의 Seed Pack 및 setup.sh 동기화 반영 (054-seedpack-setup-sync)

**Feature Branch**: `054-seedpack-setup-sync`

**Created**: 2026-07-31

**Status**: Draft

**Input**: User request: "추가된 스펙들을 시드 팩과 셋팅 스크립트에 반영했는지 확인하고, 안되어있으면 반영 작업을 하는 스펙 도출"

---

## Technical Context & Scope Analysis (기술적 맥락 및 차이 분석)

최근 완료된 기능 명세(특히 `053-embedding-reranker-model-serving`, `045-db-seed-and-setup-integration`, `039-seed-pack-sudo-firewall-migration`)에 의해 시스템 아키텍처에 다음 항목들이 추가되었습니다:
1. **임베딩(bge-m3, 8090 포트) 및 리랭커(bge-reranker-v2-m3, 8091 포트) 서빙 백엔드 인프라**
2. **`AuxiliaryModelManager` (`src/core/auxiliary_manager.py`) 프로세스 주도 생주 및 복구 루프**
3. **OpenAI 규격 `/v1/embeddings` 및 Cross-Encoder 규격 `/v1/rerank` API 라우트**

그러나 현재 시드 팩 생성 스크립트(`scripts/make_seed_pack.sh`), 원스톱 설치/설정 스크립트(`scripts/setup.sh`), 방화벽 설정 복구 스크립트(`scripts/configure_firewall.sh`), 그리고 DB 시드 데이터 주입 스크립트(`scripts/seed_db.py`) 분석 결과, 다음 **동기화 누락 사항**이 확인되었습니다:
- `setup.sh` 및 `configure_firewall.sh`의 방화벽 포트 목록(`FIREWALL_PORTS`)이 기존 `(8081 8089)`에만 머물러 있어 8090(임베딩) 및 8091(리랭커) 포트가 방화벽에 자동 등록되지 않음.
- `setup.sh` 필수 파일 검증 목록(`REQUIRED_FILES`)에 신규 핵심 모듈인 `src/core/auxiliary_manager.py`가 누락됨.
- `seed_db.py` 샘플 메트릭 레코드에 `/v1/chat/completions`만 수록되어 있어 `/v1/embeddings` 및 `/v1/rerank` 호출에 대한 초기 대시보드 시드 데이터가 부재함.
- `make_seed_pack.sh` 아카이브 검증 단계에 신규 임베딩/리랭커 모델 카탈로그 및 설정 수록 검증이 미흡함.

본 명세는 이러한 누락 사항을 체계적으로 보완하여 타 시스템 이관 및 신규 환경 설치 시 100% 완결성을 보장하는 것을 목적으로 합니다.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 신규 추가 스펙(임베딩 8090, 리랭커 8091 포트) OS 방화벽 및 환경 설정의 `setup.sh` 자동 반영 (Priority: P1) 🎯 MVP

사용자가 타겟 레거시/신규 서버 환경에서 `./setup.sh`를 실행하면, 기존 LLM 서빙 포트(8081, 8089)뿐만 아니라 신규 임베딩(8090) 및 리랭커(8091) 서비스 포트까지 포함하여 total 4개 포트에 대해 OS 방화벽(`ufw`, `firewalld`, `nftables`, `iptables`) 규칙 및 `configure_firewall.sh` 복구 스크립트에 자동 적용됩니다.

- **4개 서비스 포트 자동 개방**: `FIREWALL_PORTS=(8081 8089 8090 8091)`에 대한 UFW, firewalld, nftables, iptables 자동 등록.
- **신규 필수 파일 존재 검증**: `REQUIRED_FILES` 목록에 `src/core/auxiliary_manager.py` 추가.

**Why this priority**: 신규 구축 환경에서 임베딩 및 리랭커 API 외부 통신 차단을 방지하고 100% 정상 작동을 보장하는 핵심 인프라 설정입니다.

**Independent Test**:
1. `bash scripts/setup.sh` 실행 후 생성된 `scripts/configure_firewall.sh` 및 ufw/iptables 규칙에 8081, 8089, 8090, 8091 포트가 포함되었는지 확인.

---

### User Story 2 - Seed Pack 아카이브 생성 및 검증 강화 (`make_seed_pack.sh`) (Priority: P1) 🎯 MVP

개발자 또는 DevOps 관리자가 `bash scripts/make_seed_pack.sh`를 실행하여 타 시스템 이관용 Seed Pack 아카이브(`dist/vllm_serv_seed.tar.gz`)를 생성하면, 신규 카탈로그 엔트리(`bge-m3`, `bge-reranker-v2-m3`), 멀티 포트 설정(`embedding_backend_port: 8090`, `rerank_backend_port: 8091`) 및 핵심 모듈이 온전히 패키징되고 무결성 검증을 통과합니다.

- **아카이브 수록 검증 확장**: `config/model_catalog.json` 내 `task_type: embedding` 및 `task_type: rerank` 설정 항목과 `src/core/auxiliary_manager.py` 수록 검증.

**Why this priority**: 이관 패키지(Seed Pack)의 누락 없는 완결성을 보장합니다.

**Independent Test**:
1. `bash scripts/make_seed_pack.sh` 실행 후 아카이브 압축 해제 검증 및 `tar -tzf dist/vllm_serv_seed.tar.gz` 내 `auxiliary_manager.py` 포함 여부 확인.

---

### User Story 3 - DB 시드 데이터 주입 스크립트(`scripts/seed_db.py`)의 신규 API 엔드포인트 샘플 확장 (Priority: P2)

개발자나 사용자가 `uv run python scripts/seed_db.py --reset`을 실행하면, 기존 LLM 대화 샘플 외에도 `/v1/embeddings` (BGE-M3 밀집 벡터 추론) 및 `/v1/rerank` (Cross-Encoder 관련도 점수 추론)에 대한 정상 및 에러 샘플 메트릭 레코드가 `data/metrics.db`에 자동 주입되어 초기 대시보드 상에서 엔드포인트별 모니터링 시각화가 즉시 가능합니다.

- **다양한 엔드포인트 시드 수록**: `/v1/chat/completions`, `/v1/embeddings`, `/v1/rerank` 3종 엔드포인트 샘플 데이터 포함.

**Why this priority**: 설치 직후 대시보드 UI 상에서 전체 신규 엔드포인트의 모니터링 동작을 즉시 검증할 수 있습니다.

**Independent Test**:
1. `uv run python scripts/seed_db.py --reset` 실행 후 `data/metrics.db` 조회 시 `/v1/embeddings` 및 `/v1/rerank` 레코드 수록 확인.

---

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `scripts/setup.sh` 및 `scripts/configure_firewall.sh` 스크립트 내 서비스 포트 정의가 8081, 8089, 8090, 8091 4개 포트로 동기화 완료되어야 함.
- **DoD-002**: `scripts/setup.sh` 필수 파일 검증 목록에 `src/core/auxiliary_manager.py` 추가 및 검증 통과 완료.
- **DoD-003**: `scripts/make_seed_pack.sh` 실행으로 생성된 Seed Pack 아카이브 내 신규 설정 및 모듈 포함 무결성 검증 통과.
- **DoD-004**: `scripts/seed_db.py` 실행 시 `/v1/embeddings` 및 `/v1/rerank` 샘플 메트릭 레코드 주입 완료.
- **DoD-005**: 전체 관련 회귀 테스트 수트 (`tests/unit/test_seed_pack.py`, `tests/integration/test_migration_pipeline.py` 등) 실행하여 100% Green 통과.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `scripts/setup.sh` 및 생성되는 `scripts/configure_firewall.sh` 복구 스크립트의 방화벽 포트 배열을 `(8081 8089 8090 8091)`로 확장하여, `ufw`, `firewalld`, `nftables`, `iptables` 명령 실행 시 API 포트(8081), LLM 백엔드 포트(8089), 임베딩 백엔드 포트(8090), 리랭커 백엔드 포트(8091) 4개 포트가 일괄 자동 개방되어야 한다.
- **FR-002**: `scripts/setup.sh` 파일의 프로젝트 필수 구성 파일 검증 섹션(`REQUIRED_FILES`)에 `src/core/auxiliary_manager.py` 항목을 추가하여, 누락 시 setup 과정이 명시적 오류 메시지와 함께 즉시 중단되도록 보장해야 한다.
- **FR-003**: `scripts/make_seed_pack.sh` 패키징 아카이브 무결성 검사 단계에서 `src/core/auxiliary_manager.py` 및 `config/model_catalog.json` 내 `bge-m3`/`bge-reranker-v2-m3` 수록 정합성 검사를 수행해야 한다.
- **FR-004**: `scripts/seed_db.py` 스크립트에 `/v1/embeddings` (prompt_tokens, ttft_ms, tps 및 벡터 프롬프트 텍스트) 및 `/v1/rerank` (문서 재정렬 relevance score 관련 메트릭 텍스트) 샘플 메트릭 레코드를 추가하여 `data/metrics.db` 주입을 수행해야 한다.
- **FR-005**: 헌법 v1.6.0 규정에 따라 본 동기화 반영 동작을 검증하는 단위 및 통합 테스트 수트(`tests/unit/test_seed_pack_sync.py` 또는 기존 `test_seed_pack.py` 확장)를 작성하고 100% 통과를 보장해야 한다.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `scripts/setup.sh` 및 `scripts/configure_firewall.sh` 실행 시 8081, 8089, 8090, 8091 4개 포트에 대한 방화벽 허용 규칙 등록 및 검증 통과율 **100%**.
- **SC-002**: `make_seed_pack.sh`를 통해 생성된 Seed Pack 아카이브 내 신규 카탈로그 엔트리 및 `auxiliary_manager.py` 수록 검증 성공률 **100%**.
- **SC-003**: `python scripts/seed_db.py --reset` 수행 후 `data/metrics.db` 내 `/v1/embeddings` 및 `/v1/rerank` 엔드포인트 샘플 데이터 생성 확인율 **100%**.
- **SC-004**: 전체 관련 회귀 테스트 수트 100% Green 통과.

---

## Assumptions

- 신규 서빙 포트인 8090(임베딩)과 8091(리랭커)은 기존 8081(API) 및 8089(LLM 백엔드)와 동일한 사설망 네트워크 보안 정책(Subnet Filter)을 공유합니다.
- Seed Pack 생성 시 대용량 모델 바이너리(`models/`)는 배제하고 소스코드, 설정, 휠, DB 시드 팩만 선택 패키징하는 원칙을 유지합니다.

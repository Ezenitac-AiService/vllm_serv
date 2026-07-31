# Research: 신규 스펙(임베딩/리랭커 서빙 및 방화벽 포트 등)의 Seed Pack 및 setup.sh 동기화 반영 (054-seedpack-setup-sync)

**Feature Branch**: `054-seedpack-setup-sync`
**Date**: 2026-07-31

---

## Technical Decisions & Research Summary

### 1. OS 방화벽 4개 서비스 포트 동기화 (`scripts/setup.sh` & `scripts/configure_firewall.sh`)

- **Decision**: `FIREWALL_PORTS=(8081 8089 8090 8091)` 배열을 단일 진실 소스로 정의하고, 모든 방화벽 유틸리티(`ufw`, `firewalld`, `nftables`, `iptables`) 및 비대화형 자동 생성 복구 스크립트(`scripts/configure_firewall.sh`)에 적용.
- **Rationale**:
  - `8081/tcp`: REST / OpenAPI / Dashboard HTTP 서비스 포트
  - `8089/tcp`: 기본 LLM (`qwen3.5-4b`) 백엔드 `llama-server` 포트
  - `8090/tcp`: BGE-M3 밀집 벡터 임베딩 백엔드 `llama-server` 포트 (053 스펙)
  - `8091/tcp`: BGE-Reranker-v2-M3 Cross-Encoder 리랭킹 백엔드 `llama-server` 포트 (053 스펙)
  - 4개 포트가 이관 서버 설치 시 일괄 등록되어야 외부 LAN 클라이언트 및 RAG/에이전트 애플리케이션의 커넥션거부(`Connection Refused`) 에러가 방지됨.
- **Alternatives Considered**:
  - 온디맨드 개방 방식: 서비스 기동 후 개별 포트를 개방하는 방식은 설치 초기 자동 설정 원칙에 위배되며 예외 처리가 복잡해지므로 기각함.

---

### 2. `setup.sh` 필수 프로젝트 구조 및 검증 파일 확장 (`REQUIRED_FILES`)

- **Decision**: `scripts/setup.sh` 내 `REQUIRED_FILES` 배열에 `src/core/auxiliary_manager.py` 추가.
- **Rationale**: `auxiliary_manager.py`는 임베딩/리랭커 백엔드 프로세스의 백그라운드 기동, 헬스체크 및 크래시 자동 복구(`_crash_recovery_loop`)를 담당하는 핵심 서브시스템이므로, 설치 시 파일 부재 시 즉시 중단(fail-fast)되어야 함.
- **Alternatives Considered**:
  - 검증 스킵: 필수 파일 검증을 스킵하면 서버 구동 시 `ImportError`로 크래시되므로 기각함.

---

### 3. Seed Pack 생성 및 무결성 검증 (`scripts/make_seed_pack.sh`)

- **Decision**: `make_seed_pack.sh` 패키징 완료 후 아카이브 내부 파일 검증 단계를 확장하여 `config/platform_profiles.json`, `scripts/configure_firewall.sh`, `wheels/legacy_i7_930` 외에도 `src/core/auxiliary_manager.py` 수록 여부를 필수 확인하도록 구현.
- **Rationale**: 이관 타겟 머신에서 Seed Pack 압축 해제 후 추가 모듈 다운로드 없이 온전히 실행될 수 있도록 패키징 검증을 보장함.
- **Alternatives Considered**:
  - 수동 압축 확인: 사람의 개입 없이 자동화된 스크립트 실행만으로 검증되도록 내장 로직으로 적용.

---

### 4. DB 시드 데이터 주입 확장 (`scripts/seed_db.py`)

- **Decision**: `scripts/seed_db.py`에 `/v1/embeddings` (BGE-M3 1024차원 밀집 벡터 응답 메트릭) 및 `/v1/rerank` (Cross-Encoder 문서 관련도 점수 메트릭) 샘플 레코드를 추가.
- **Rationale**: `setup.sh` 완료 직후 대시보드 UI 및 모니터링 API 조회 시 엔드포인트별 추론 메트릭 시각화 동작을 100% 실측 검증할 수 있음.
- **Alternatives Considered**:
  - LLM 메트릭만 유지: 새로운 엔드포인트 모니터링 검증이 불가능하므로 기각함.

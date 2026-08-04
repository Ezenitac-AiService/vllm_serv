# Research & Technical Decisions: `setup.sh` 필수 GGUF 모델 자동 점검 및 다운로드 통합 (`092-setup-auto-model-download`)

## Phase 0: Research & Decision Log

### Decision 1: 모델 점검 및 다운로드 파이프라인 연동 방식 (`scripts/ensure_models.py`)

- **Decision**: `src/core/model_downloader.py` 모듈을 재사용하는 독립 실행 파이프라인 헬퍼 스크립트 `scripts/ensure_models.py`를 작성하고, `scripts/setup.sh` 내에 연동한다.
- **Rationale**:
  - `ModelDownloader`는 HuggingFace / ModelScope 지원, 다운로드 락, 재시도, 파일 크기 검사 로직이 이미 구현되어 있음.
  - 쉘 스크립트 내부에 파이썬 모듈 호출을 캡슐화하여 쉘 스크립트 복잡성을 줄이고 모듈화 및 재사용성 향상.
- **Alternatives Considered**:
  - *Option B (shell `curl`/`wget` 직접 다운로드)*: 진행률 표시는 가능하나 HF/ModelScope 미러 변경, 락 처리, 파이썬 패키지 호환 검사가 복잡해짐.

---

### Decision 2: 기본 점검 및 자동 프로비저닝 대상 3종 필수 모델 범위

- **Decision**: 메인 LLM (`qwen3.5-4b`), 임베딩 모델 (`bge-m3`), 리랭커 모델 (`bge-reranker-v2-m3`) 3종 세트를 필수 검사 및 다운로드 대상으로 확정한다.
- **Rationale**:
  - `./start_server.sh` 실행 시 8081(대화), 8090(임베딩), 8091(리랭커) 3개 데몬이 동시에 서빙되므로 3종 모델이 모두 확보되어야 최초 구동 시 오류가 발생하지 않음.
- **Alternatives Considered**:
  - *Option B (`qwen3.5-4b` 1종만 다운로드)*: 임베딩/리랭커 데몬 구동 시 모델 부재 오류 발생.

---

### Decision 3: PCI 버스 장비 탐지 및 `scripts/` 기존 헬퍼 스크립트 전수 체이닝

- **Decision**: `lspci | grep -i nvidia`로 물리 GPU를 감지하고, `nvcc` 또는 `nvidia-smi` 미설치 시 `scripts/update_cuda_drivers.sh`로 연결하여 자동 설치/업데이트를 유도하며, `scripts/seed_db.py`, `scripts/verify_wheel_binary.py`, `scripts/audit_assets.py`, `scripts/configure_firewall.sh`를 `setup.sh` 파이프라인 단계별로 모듈식 체이닝한다.
- **Rationale**:
  - 베어메탈/VM 서버 마이그레이션 시 OS만 설치된 환경에서도 `./setup.sh` 1회 실행으로 드라이버, CUDA, C++ 빌드, 모델 다운로드, 방화벽, DB가 모두 원스톱 정돈됨.

# Quickstart Validation Guide: `setup.sh` 필수 GGUF 모델 자동 점검 및 다운로드 통합 (`092-setup-auto-model-download`)

본 가이드는 `setup.sh` 실행 시 필수 GGUF 모델 자동 점검 및 `scripts/ensure_models.py` 원스톱 프로비저닝이 정상 작동하는지 검증하는 시나리오입니다.

---

## 사전 조건 (Prerequisites)

1. **프로젝트 환경 준비**: `uv sync`를 통한 가상환경 구축 완료

---

## 1 단계: `scripts/ensure_models.py` 독립 검증

```bash
# ensure_models.py 독립 실행으로 3종 모델 존재 점검 및 다운로드 수성
uv run python scripts/ensure_models.py --check-only
```

- **예상 결과**: `models/` 디렉토리에 3종 필수 모델(`qwen3.5-4b`, `bge-m3`, `bge-reranker-v2-m3`) 존재 상태 리포트가 출력됨.

---

## 2 단계: `./setup.sh` 원스톱 파이프라인 실측 수행

```bash
# setup.sh 실행
./setup.sh
```

- **예상 결과**:
  1. Sudo 및 OS 방화벽 점검 완료.
  2. `uv sync` 동기화 및 DB 초기화(`seed_db.py`) 완료.
  3. nvcc / nvidia-smi / PCI GPU 탐지 및 CUDA 가속 휠 3중 검증 완료.
  4. **[NEW]** 모델 자동 점검 및 다운로드(`ensure_models.py`) 단계가 성공적으로 통과함.

---

## 3 단계: `./start_server.sh` 가동 및 3종 데몬 Readiness 실측

```bash
# 백그라운드 서버 구동
./start_server.sh
```

- **예상 결과**:
  - 모델 부재로 인한 구동 실패 없이 8081(대화), 8082(대시보드) 동시 가동에 성공함.

---

## 4 단계: 자동화 테스트 수트 통과

```bash
uv run pytest tests/test_ensure_models.py -v
```

- **예상 결과**: 100% Green (PASSED).

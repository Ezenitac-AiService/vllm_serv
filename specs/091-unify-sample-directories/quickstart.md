# Quickstart Validation Guide: 샘플 실습 디렉토리 이중화 분석 및 표준 통합 (`091-unify-sample-directories`)

본 가이드는 `samples` 심볼릭 링크 삭제 및 `sample/` 단일 물리 디렉토리 표준화 작업이 정상 반영되었는지 실측 검증하는 시나리오를 제공합니다.

---

## 사전 조건 (Prerequisites)

1. **프로젝트 환경 준비**: `vllm_serv` 메인 가상환경 준비 완료 (`uv sync`)

---

## 1 단계: 디렉토리 정돈 상태 실측 검사

```bash
# sample 물리 디렉토리 존재 확인
ls -ld sample

# samples 심볼릭 링크 삭제 여부 확인
ls -ld samples 2>&1
```

- **예상 결과**:
  - `sample`은 물리 디렉토리로 정상 접근 가능함.
  - `samples` 접근 시 "No such file or directory" 오류로 존재하지 않음이 확인됨.

---

## 2 단계: 시드팩 생성 스크립트 정합성 검증 (`make_seed_pack.sh`)

```bash
# 시드팩 생성 시뮬레이션
bash scripts/make_seed_pack.sh

# 생성된 시드팩 내 sample 디렉토리 단일 포함 확인
tar -tzf vllm_serv_seed.tar.gz | grep -E '^sample/' | head -n 5
```

- **예상 결과**: 타르볼 내에 `sample/` 1개 물리 디렉토리만 번들링되어 압축 오염이 없음.

---

## 3 단계: 샘플 수트 자동화 테스트 실행 (`uv run pytest`)

```bash
# 샘플 검증 수트 실행
uv run pytest tests/test_sample_scripts.py -v
```

- **예상 결과**: 모든 테스트 케이스 100% Green (PASSED).

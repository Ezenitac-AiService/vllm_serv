# Quickstart Validation Guide: sample_05_structured_output.py의 .legacy 모듈 의존성 제거 및 시드팩 독립성 보장 (071-seed-pack-include-legacy)

## 1. 개요
이 가이드는 `samples/sample_05_structured_output.py` 샘플 코드가 `.legacy` 디렉터리 및 외부 모듈에 의존하지 않고 독립(Self-contained) 실행 가능한지 확인하는 검증 절차입니다.

---

## 2. 검증 시나리오

### 시나리오 1: sample_05_structured_output.py 독립 구동 검증
1. `.legacy` 디렉터리 임포트 구문 누락 검증:
   ```bash
   uv run python -c "import samples.sample_05_structured_output as s05; print(hasattr(s05, 'run_structured_output_sample'))"
   ```
   - **기대 결과**: `True` 출력 확인 및 `.legacy` 관련 임포트 오류가 발생하지 않음.

2. 스크립트 단독 구동 검증:
   ```bash
   uv run pytest tests/unit/test_sample_scripts.py -k test_sample_05_structured_output
   ```
   - **기대 결과**: 샘플 05번 테스트 100% Pass.

---

### 시나리오 2: 전체 회귀 테스트 검증
1. 단위 테스트 수트 실행:
   ```bash
   uv run pytest tests/unit/test_sample_scripts.py
   ```
   - **기대 결과**: 전체 샘플 스크립트 테스트 통과.

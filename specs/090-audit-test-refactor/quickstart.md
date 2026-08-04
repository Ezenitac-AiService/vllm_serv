# Quickstart Validation Guide: 학습 플랫폼 이관 코드 정밀 검토, 종합 테스트 및 구조적 리팩토링 (`090-audit-test-refactor`)

 본 가이드는 학습 플랫폼에서 이관된 자산 정리, CUDA GPU 환경 정밀 탐지 모듈(`src/utils/cuda_env.py`, `scripts/common.sh`), 그리고 자동화 테스트 수트가 정상 작동하는지 실측 검증하는 시나리오를 제공합니다.

---

## 사전 조건 (Prerequisites)

1. **NVIDIA CUDA GPU 호스트**: NVIDIA GPU 장착 및 CUDA 호환 드라이버가 활성화된 호스트
2. **`uv` 패키지 관리자**: `uv` 환경 준비 완료
3. **가상환경 동기화**: `uv sync` 실행 완료

---

## 1 단계: 이관 자산 전수 감사 (Audit) 및 `.legacy/` 정리 검증

```bash
# 쉘 스크립트 구문 검사
bash -n scripts/common.sh

# 레거시 파일 정리 디렉토리 존재 확인
ls -la .legacy/
```

- **예상 결과**: `.legacy/archive_088_sync/` 경로로 중복/무효 자산이 정리 이동되어 있으며, 쉘 스크립트 구문 오류가 발생하지 않음.

---

## 2 단계: CUDA 환경 탐지 공통 모듈 실측 검증 (`src/utils/cuda_env.py`)

```bash
# 파이썬 CUDA 환경 정밀 검사 실행
uv run python -c "from src.utils.cuda_env import inspect_cuda_environment; profile = inspect_cuda_environment(); print(profile)"
```

- **예상 결과**:
  ```text
  CudaEnvironmentProfile(is_cuda_available=True, driver_version='...', cuda_version='...', gpu_count=1, llama_supports_gpu=True)
  ```
  CUDA GPU 미장착 시 단정 오류(AssertionError) 발생으로 Fail-Fast 검증.

---

## 3 단계: 전체 검증 테스트 수트 실행 (`uv run pytest`)

```bash
# 전체 회귀 및 새로 작성된 단위/통합 테스트 실행 (헌장 II, VII 준수)
uv run pytest tests/test_cuda_env.py tests/test_sample_scripts.py -v
```

- **예상 결과**: 모든 테스트 케이스가 100% Green (PASSED) 통과.

---

## 4 단계: 12종 실습 샘플 스크립트 구문 및 바인딩 검증

```bash
# 샘플 스크립트 실행성 검사
uv run python -m pytest tests/test_sample_scripts.py -k "test_samples_syntax"
```

- **예상 결과**: `samples/sample_01`~`06` 및 `samples/openai_01`~`06` 총 12종 파일이 하드코딩된 IP 없이 `config.json` / `.env`를 동적 참조하며 구문 오류 없이 실행 준비됨을 확인.

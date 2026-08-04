# Quickstart Validation Guide: 3대 멀티 플랫폼 HW 차등 감지 및 훈련 플랫폼(RTX 3060) 최적 하드웨어 가속 자동 설정 (`094-hardware-capability-autodetect`)

본 가이드는 3대 멀티 하드웨어 플랫폼(개발: GTX 1080Ti, 서비스: GTX 1070/i7-930, 훈련: RTX 3060/i7-4770)의 하드웨어 자동 탐지 및 차등 셋팅 매핑 검증 시나리오입니다.

---

## 사전 조건 (Prerequisites)

1. **프로젝트 환경 준비**: `uv sync`를 통한 가상환경 구축 완료

---

## 1 단계: 하드웨어 자동 탐지 단위 테스트 실행 (Mock 매핑 포함)

```bash
uv run pytest tests/unit/test_hardware_autodetect.py -v
```

- **예상 결과**:
  1. 훈련 플랫폼 (RTX 3060 / sm_86) 탐지 시 `3rd Gen Tensor Cores`, `TF32/BF16`, `FlashAttention-2` 활성화 검증.
  2. 서비스 플랫폼 (i7-930 / Nehalem / sm_61) 탐지 시 AVX2 비활성화 CMAKE_ARGS 검증.
  3. 개발 플랫폼 (GTX 1080Ti / sm_61) 탐지 시 FP16 / SDPA 안전 컴파일 검증.

---

## 2 단계: CLI 하드웨어 탐지 리포트 실행

```bash
uv run python -m src.core.cpu_detector --report
```

- **예상 결과**: 호스트 GPU 및 CPU 명령어 세트 스캔 후 하드웨어 특성에 맞춘 `Hardware Profile` 요약 출력.

---

## 3 단계: `./setup.sh` 호환 구동 및 셋팅 적용 검증

```bash
./setup.sh --help
```

- **예상 결과**: 하드웨어 가속 자동 감지 믹스인이 에러 없이 연동됨.

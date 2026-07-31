# Quickstart & End-to-End Validation Guide: 시드팩 명세 및 샘플 수록 (065-seed-pack-specs-samples)

**Feature**: `065-seed-pack-specs-samples`

## 1. 개요 (Overview)

본 가이드는 `./make_seed_pack.sh` 구동 시 생성되는 시드팩 아카이브(`dist/vllm_serv_seed.tar.gz`)에 명세서(`specs/`), API 샘플 파일(`samples/`), 및 레거시 모듈(`.legacy/`)이 정상적으로 수록되는지 실측 검증하는 절정 가이드입니다.

---

## 2. 검증 시나리오 (Validation Scenarios)

### 시나리오 1: 시드팩 패키징 구동 및 수록 검증
```bash
./make_seed_pack.sh
```
**기대 결과**:
- `dist/vllm_serv_seed.tar.gz` 아카이브 정상 생성 (용량 < 15MB)
- `[SEED-PACK INFO] ✓ 샘플 파이프라인(samples/) 및 명세서(specs/) 아카이브 수록 검증 완료` 출력

---

### 시나리오 2: 아카이브 내부 파일 목록 탐색 실측
```bash
tar -tzf dist/vllm_serv_seed.tar.gz | grep -E "samples/|specs/|\.legacy/"
```
**기대 결과**:
- `samples/common.py`
- `samples/sample_01_chat.py` ~ `sample_05_structured_output.py`
- `specs/065-seed-pack-specs-samples/spec.md`
- `.legacy/ATEAM_ExtractionItem.py`

---

### 시나리오 3: 단위 테스트 수트 실행
```bash
uv run pytest tests/unit/test_seed_pack.py
```
**기대 결과**: 시드팩 수록 검증 100% Green Pass 통과

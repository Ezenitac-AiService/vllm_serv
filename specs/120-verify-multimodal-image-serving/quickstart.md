# Quickstart Validation Guide: 멀티모달(비전) 모델 로딩 및 이미지 입력 서빙 검증

## 연관 문서
- [Feature Specification](file:///home/dev/storage/vllm_serv/specs/120-verify-multimodal-image-serving/spec.md)
- [Data Model](file:///home/dev/storage/vllm_serv/specs/120-verify-multimodal-image-serving/data-model.md)
- [Multimodal Serving Contract](file:///home/dev/storage/vllm_serv/specs/120-verify-multimodal-image-serving/contracts/multimodal_serving_contract.md)

---

## 1. 사전 조건 (Prerequisites)

- Python 3.10+ 및 `uv` 패키지 매니저
- 프로젝트 저장소 루트: `/home/dev/storage/vllm_serv`

---

## 2. 검증 절차 (Validation Steps)

### 검증 1: 멀티모달 모델 4종 CLI 인자 바인딩 무결성 검증

`gemma4-e2b`, `gemma4-e4b`, `gemma4-12b`, `qwen3.5-9b-vision` 4개 모델 스폰 시 `--mmproj` 옵션이 정상 결합되는지 검증합니다.

```bash
uv run pytest tests/unit/test_process_manager_multimodal.py
```

### 검증 2: OpenAI 규격 멀티모달 이미지 페이로드 프록시 라우팅 검증

Data URL Base64 및 이미지 URL 페이로드가 수신되었을 때 역방향 프록시가 200 OK 인퍼런스 응답을 처리하는지 검증합니다.

```bash
uv run pytest tests/integration/test_multimodal_image_payload_proxy.py
```

### 검증 3: 회귀 검증 수트 실행

전체 회귀 테스트 수트를 실행하여 기존 시스템 안정성을 통합 검증합니다.

```bash
uv run pytest
```

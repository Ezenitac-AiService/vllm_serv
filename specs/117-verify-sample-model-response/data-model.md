# Data Model & Schema Specification: sample 예제 스크립트 설정 및 모델 검증 데이터 모델

**Feature**: `verify-sample-model-response`  
**Feature Directory**: `specs/117-verify-sample-model-response`  

---

## 1. Sample Config Data Schema (`sample/config.json`)

`sample/` 폴더 내 모든 예제 및 공통 헬퍼 스크립트가 참조하는 단일 진실 출처(Single Source of Truth) 구조체 모델입니다.

```json
{
  "server_host": "http://10.0.0.41",
  "server_host_candidates": [
    "http://127.0.0.1",
    "http://10.0.0.41",
    "http://192.168.0.175"
  ],
  "main_port": 8081,
  "embedding_port": 8090,
  "rerank_port": 8091,
  "default_model": "qwen3.5-4b",
  "embedding_model": "bge-m3",
  "rerank_model": "bge-reranker-v2-m3",
  "default_temperature": 0.3,
  "default_max_tokens": 1024,
  "benchmark_max_tokens": 2048,
  "request_timeout_seconds": 180.0,
  "model_benchmarks": {
    "qwen3.5-4b": {
      "recommended_context_length": 4096,
      "max_context_length": 8192,
      "peak_vram_mb": 3950,
      "tpot_tok_per_sec": 49.00,
      "status": "ACTIVE_DEFAULT"
    },
    "qwen3.5-2b": {
      "recommended_context_length": 8192,
      "max_context_length": 16384,
      "peak_vram_mb": 2450,
      "tpot_tok_per_sec": 70.11,
      "status": "AVAILABLE"
    }
  }
}
```

### Entity Fields Description

- **`server_host`** (`string`): 현재 활성 서버 호스트 주소
- **`server_host_candidates`** (`array[string]`): 동적 헬스체크 탐색 대상 IP/호스트 후보 목록 (`127.0.0.1`, 개발 IP `10.0.0.41`, 배포 IP `192.168.0.175`)
- **`main_port`** (`integer`): 메인 LLM 추론 API 포트 (8081)
- **`request_timeout_seconds`** (`float`): 모델 핫스왑 및 생성 요청 타임아웃 마진 (180.0초)

---

## 2. Model Validation Result Entity (`ModelValidationResult`)

샘플 스크립트 실행 시 요청 모델과 응답 모델의 교차 검증 결과를 기록하는 메모리 상의 데이터 객체입니다.

| Attribute Field | Type | Description | Validation Rule |
|-----------------|------|-------------|-----------------|
| `requested_model` | `string` | 클라이언트가 API 페이로드로 전송한 모델 ID | 필수, non-empty |
| `responded_model` | `string` | API 응답 JSON의 `model` 필드에서 추출한 모델 ID | 필수, non-empty |
| `is_matched` | `boolean` | `requested_model == responded_model` 인지 여부 | `True` 일 경우 검증 통과 |
| `validation_status` | `string` | 콘솔 표출용 상태 태그 | `✅ MATCH` 또는 `❌ MISMATCH` |

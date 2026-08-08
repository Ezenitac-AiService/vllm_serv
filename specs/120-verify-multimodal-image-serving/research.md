# Phase 0 Research: 멀티모달(비전) 모델 로딩 및 이미지 입력 서빙 검증

## 1. 멀티모달 모델별 비전 프로젝터(mmproj) 매핑 사양 조사

| 모델 식별자 (`model_id`) | 메인 모델 가중치 파일 (`model_path`) | 비전 프로젝터 파일 (`clip_path`) | `requires_mmproj` |
|---|---|---|---|
| `gemma4-e2b` | `models/gemma4-e2b/gemma-4-E2B-it-Q4_K_M.gguf` | `models/gemma4-e2b/mmproj-gemma-4-E2B-it-BF16.gguf` | `true` |
| `gemma4-e4b` | `models/gemma4-e4b/gemma-4-E4B-it-Q4_K_M.gguf` | `models/gemma4-e4b/mmproj-gemma-4-E4B-it-BF16.gguf` | `true` |
| `gemma4-12b` | `models/gemma4-12b/gemma-4-12B-it-Q4_K_M.gguf` | `models/gemma4-12b/mmproj-gemma-4-12B-it-BF16.gguf` | `true` |
| `qwen3.5-9b-vision` | `models/qwen3.5-9b-vision/Qwen3.5-9B-Q4_K_M.gguf` | `models/qwen3.5-9b-vision/mmproj-BF16.gguf` | `true` |

### Decision:
모든 멀티모달 모델은 `config/model_catalog.json`에 `requires_mmproj: true`, `clip_filename`, `clip_path`가 명시적으로 등록되어야 하며, `ProcessManager` 스폰 시 `--mmproj <clip_path>` 파라미터로 결합된다.

### Rationale:
- `llama-server` 인퍼런스 엔진은 `--mmproj` 옵션을 통해 비전 임베딩 프로젝터 가중치를 로드하고 시각적 토큰(Visual Tokens)을 텍스트 임베딩과 통합 처리한다.
- 프로젝터 미존재 시 `requires_mmproj: true` 조건 검사로 손상된 구동을 원천 차단한다.

---

## 2. OpenAI API 규격 `image_url` 및 Base64 페이로드 전달 연구

- **OpenAI Payload Standard**:
  ```json
  {
    "model": "qwen3.5-9b-vision",
    "messages": [
      {
        "role": "user",
        "content": [
          {"type": "text", "text": "이 이미지에 대해 설명해줘."},
          {
            "type": "image_url",
            "image_url": {
              "url": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
            }
          }
        ]
      }
    ]
  }
  ```

### Decision:
`src/api/routes/inference_api.py` 역방향 프록시(`reverse_proxy`)는 클라이언트로부터 전송된 JSON 바이트 스트림을 별도의 비파괴 파싱 없이 백엔드 `llama-server` HTTP 엔드포인트로 원자적 전달하도록 보장한다.

### Rationale:
- `llama-server` C++ 엔진 자체에 OpenAI 호환 멀티모달 파서가 내장되어 있으므로, 중간 파이썬 프록시 레이어에서의 과도한 재인코딩(Re-encoding)이나 문자열 파싱 overhead를 제거하고 100% 원형(Raw bytes)을 프록시 전달하여 처리 성능을 극대화한다.

# Contract: Multimodal Serving & Image Payload Contract

## 1. ProcessManager CLI Invocation Contract

멀티모달 모델(`gemma4-e2b`, `gemma4-e4b`, `gemma4-12b`, `qwen3.5-9b-vision`) 구동 시 `ProcessManager`가 생성해야 하는 C++ 백엔드 인퍼런스 명령행 표준 인터페이스입니다.

```bash
# qwen3.5-9b-vision 예시
/usr/bin/llama-server \
  -m models/qwen3.5-9b-vision/Qwen3.5-9B-Q4_K_M.gguf \
  --mmproj models/qwen3.5-9b-vision/mmproj-BF16.gguf \
  -c 4096 \
  --host 127.0.0.1 \
  --port 8089 \
  -ngl 999 \
  --split-mode none \
  --main-gpu 0
```

---

## 2. Multimodal Chat Completion Payload Contract

클라이언트가 역방향 프록시 `/v1/chat/completions` 엔드포인트로 전달하는 OpenAI 규격의 멀티모달 이미지 페이로드 규격 계약입니다.

```json
{
  "model": "qwen3.5-9b-vision",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "이미지에 포함된 텍스트와 개체를 분석해주세요."
        },
        {
          "type": "image_url",
          "image_url": {
            "url": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD..."
          }
        }
      ]
    }
  ],
  "temperature": 0.2,
  "max_tokens": 512
}
```

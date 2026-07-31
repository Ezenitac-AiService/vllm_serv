# Quickstart & End-to-End Validation Guide: Inference API Proxy Header Filtering Fix (069-fix-proxy-content-length-header)

**Feature**: `069-fix-proxy-content-length-header`

## 1. 단위 및 회귀 테스트 검증
```bash
# 1. 헤더 필터링 단위 테스트 실행
uv run pytest tests/unit/test_inference_api_proxy_headers.py

# 2. 전체 회귀 테스트 실행
uv run pytest tests/unit/
```

## 2. 샘플 예제 호출 검증
```bash
# 서버 구동 중 sample_01_chat.py 호출
uv run python samples/sample_01_chat.py
```
**기대 결과**: `LocalProtocolError` 없이 `✅ [응답 성공]` 정상 수신 및 완료 본문 출력.

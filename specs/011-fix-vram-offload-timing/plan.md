# Implementation Plan: GPU VRAM 오프로드 완료 타이밍 보정 및 프로세스 바인딩 격리 (GPU VRAM Offload & Process Lifecycle Timing Fix)

**Branch**: `011-fix-vram-offload-timing` | **Date**: 2026-07-29 | **Spec**: [spec.md](file:///home/dev/storage/vllm_serv/specs/011-fix-vram-offload-timing/spec.md)

**Input**: Feature specification from `/specs/011-fix-vram-offload-timing/spec.md`

## Summary

본 구현 계획은 서빙 프로세스 개설 시 단순 HTTP 200 응답(0.06초 조기 판정 오류)에 의존하여 조기 READY 전환 및 CPU 추론 롤백이 발생하는 현상을 방지하는 것을 목표로 합니다. **`llama-server`가 모델 트랜스포머 레이어 및 CLIP 가중치를 GPU VRAM에 100% 탑재(Offload) 완료했음을 실시간 파싱하고 네이티브 `/health` JSON API를 병행 검증한 후에만 `READY` 상태로 전환**하고, **이전 서빙 프로세스의 종료, 포트 소켓(8081 `SO_REUSEADDR`) 완전히 자유 상태 확인, PyNVML C-API VRAM 메모리 반납을 완료한 수순으로만 신규 자식 프로세스를 개설**하도록 생명주기를 완벽히 격리합니다. 또한 **Ollama, LM Studio, LiteLLM의 우수 아키텍처(Graceful Stream Drain, KV Cache Pre-flight VRAM Estimator, K8s `/health/readiness` & `/health/liveness` API)**를 수용하고, **평상시에는 기본 서비스 모델(`qwen3.5-4b`)을 GPU VRAM에 항상 상주 서빙(Permanent Residency)**하며, **벤치마크 완료 후 기본 모델로 자동 원상 복원(Restore)**하는 런타임 수명주기를 보장합니다.

---

## Technical Context

- **Language/Version**: Python 3.12 (uv 환경)
- **Primary Dependencies**: `llama-cpp-python` (CUDA `cu124`), `pydantic` v2, `fastapi`, `httpx`, `pytest`, `asyncio`, `pynvml` (PyNVML C-API)
- **Hardware/Platform**: Linux x86_64, NVIDIA GeForce GTX 1080 Ti (11GB VRAM, CUDA 13.0 / Driver 580.173.02)
- **Default Resident Model**: `qwen3.5-4b` (평상시 GPU VRAM 상주 서빙 대상)
- **Target Exception Classes**: `GpuAccelerationError`, `VramOverflowError`, `PortCollisionError` (포트 8081 충돌 및 좀비 프로세스 전용)
- **Testing**: `pytest` (`uv run pytest`)
- **Performance Goals**:
  - GPU 100% VRAM 오프로딩 동기화를 통한 TTFT < 1.0s 및 TPOT > 30 tok/s 달성
  - PyNVML 기반 non-blocking VRAM 측정 (< 1ms 오버헤드)
  - KV Cache 용량 정밀 사전 계산을 통한 OOM 발생률 0%
  - 프로세스 스위칭 시 Graceful Stream Drain 및 VRAM 해제/포트 클리어 보장
  - 벤치마크 완수 후 기본 서비스 모델 자동 원상 복원율 100%

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] 계획서가 한국어로 작성되었는가? (Principle I: 언어 정책)
- [x] 테스트 코드 작성 계획이 포함되어 있는가? (Principle II: TDD 및 품질 보증 원칙)
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (Principle III: 종료 조건 명확화 원칙)
- [x] 기존 아티팩트 및 명세의 파괴적 편집을 금지하고 온전히 보존 및 확장하는가? (Principle IV: 비파괴적 문서 수정 원칙)

---

## Project Structure & Touch-Points

### Documentation (this feature)

```text
specs/011-fix-vram-offload-timing/
├── spec.md                     # Feature specification
├── plan.md                     # This implementation plan
├── research.md                 # Phase 0 output
├── data-model.md               # Phase 1 output
├── quickstart.md               # Phase 1 output
└── contracts/
    └── process_timing_api.md   # Process Timing & Status API contract
```

### Source Code & Test Layout

```text
src/
├── core/
│   ├── gpu_detector.py         # [UPDATE] PyNVML C-API VRAM 측정 & KV Cache 사전 추정기
│   ├── process_manager.py      # [UPDATE] Graceful Stream Drain, PyNVML VRAM 반납 및 포트 TIME_WAIT 클리어
│   └── llama_manager.py        # [UPDATE] _wait_for_ready() 내 /health JSON API 병행 검증 및 기본 모델 복원 추가
├── api/
│   └── server.py               # [UPDATE] K8s/LiteLLM 호환 /health/liveness 및 /health/readiness 엔드포인트 추가
scripts/
└── benchmark_quality.py        # [UPDATE] Step 3 /health 및 VRAM 탑재 완납 폴링, 벤치마크 완료 후 기본 모델 자동 복원(Restore)

tests/
├── unit/
│   └── test_gpu_detector.py    # [UPDATE] PyNVML, KV Cache 추정 및 VRAM 타이밍 / READY 동기화 단위 테스트
└── integration/
    └── test_gpu_validation.py  # [UPDATE] 서빙 프로세스 생명주기 및 PyNVML / /health API / K8s probes 통합 테스트
```

---

## Complexity Tracking

*No constitution violations.*

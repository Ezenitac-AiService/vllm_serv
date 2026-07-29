# Research & Technical Decisions: Qwen3.5 모델 3종 연동 및 성능 검증

## Decision 1: Qwen3.5 GGUF 매핑 및 ChatML 템플릿 인자 바인딩

- **Decision**: Qwen3.5 2B, 4B, 9B 모델에 대해 `llama-server` 바인딩 시 ChatML (`--chat_template chatml`) 및 Qwen 템플릿 인자를 명시적으로 전달합니다.
- **Rationale**: Gemma 4 모델과 Qwen3.5 모델은 Special Tokens (`<|im_start|>`, `<|im_end|>`) 및 역할 구분 템플릿 구조가 상이하므로, `llama-server` 구동 인자에 적절한 템플릿을 바인딩해야 응답 토큰 생성이 왜곡되지 않습니다.
- **Alternatives Considered**:
  - 기본 템플릿 자동 추론 의존: GGUF 메타데이터가 손상되거나 오작동할 수 있어 명시적 `--chat_template` 지정을 채택함.

---

## Decision 2: Q4_K_M, Q4_0, Q8_0 양자화 포맷 및 Gemma 4 교차 비교 벤치마크

- **Decision**: Qwen3.5 3종 모델(2B, 4B, 9B) 각각에 대하여 Q4_K_M, Q4_0, Q8_0 3가지 양자화 버전을 실측 검증 대상으로 등록하고, 기존 Gemma 4 (E2B, E4B, 12B) 재측정 지표와 1:1 교차 비교 벤치마크를 수행합니다.
- **Rationale**: 사용자 지침 및 리팩토링 검증 기준에 맞춰, 양자화 포맷에 따른 VRAM 피크 및 추론 속도(TPOT) 변동폭을 수치로 확보하여 11GB VRAM (GTX 1080 Ti) 환경에서의 최적 모델 및 양자화 조합을 객관적으로 도출합니다.
- **Alternatives Considered**:
  - Q4_K_M 단일 포맷만 테스트: 사용자의 명시적 요청(Q4_K_M, Q4_0, Q8_0 및 기존 모델 교차 비교)을 반영하여 제외함.

---

## Decision 3: Dry-run VRAM Calculation 및 OOM 예방 안전 롤백

- **Decision**: 9B Q8_0 등 고용량 모델 선택 시 예상 VRAM이 11GB를 초과할 경우 `ProcessManager`에서 사전 감지(Dry-run VRAM check)를 수행하고, OOM 발생 시 서브프로세스를 안전하게 중단하고 `ERROR` 상태 메시지를 반환합니다.
- **Rationale**: 11GB VRAM 한계 초과 시 GPU CUDA OOM 현상이 발생하여 전체 백엔드 서비스가 멈추는 것을 방지합니다.
- **Alternatives Considered**:
  - OOM 발생 시 재부팅 시도: 서비스 가용성을 해치므로 사전 감지 및 Safe Error Return 방식을 채택함.

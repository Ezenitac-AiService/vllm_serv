# Phase 0: Outline & Research

## Research Tasks

1. **Needle in a Haystack Implementation**:
   - *Decision*: Paul Graham의 에세이 텍스트 데이터셋 (또는 단순 반복 텍스트 블록)을 Haystack(건초더미)으로 사용하고, 중간에 특정 정보(예: "비밀번호는 'VLLM_SERV_2026'입니다.")를 랜덤한 깊이(Depth)에 삽입합니다.
   - *Rationale*: 실제 긴 문맥 처리를 평가하려면 의미 있는 텍스트의 나열이 필요하지만, 이번 스크립트에서는 독립 실행 편의성을 위해 시스템 프롬프트용 "배경 지식 블록"을 여러 개 반복 생성한 뒤 그 사이에 Needle 문장을 삽입하는 방식(Synthetic dataset)을 택하여 외부 데이터 의존성을 없앱니다.
   - *Alternatives considered*: 외부 HuggingFace 데이터셋 사용 (다운로드 시간 및 인터넷 의존성 발생으로 기각).

2. **OOM vs 60s TTFT Graceful Exit**:
   - *Decision*: PyTorch/CUDA OOM 에러나 `llama.cpp` OOM 발생 시 `subprocess`의 return code를 체크하거나 `try-except` 블록을 활용하여 메인 루프가 크래시되지 않고 로깅 후 다음 모델로 넘어가도록 처리. TTFT는 타이머를 두거나 첫 응답 반환 시간을 체크하여 60초 초과 시 중단 처리.
   - *Rationale*: 안정적인 벤치마크 연속 구동을 위해 필수적임.

3. **Metrics Recording**:
   - *Decision*: JSONL 형태로 `specs/003-context-scaling/results.jsonl`에 모델, 입력 토큰수, VRAM, TTFT, TPOT, Accuracy 결과를 실시간 append.
   - *Rationale*: 벤치마크 중단 시에도 이전까지의 데이터가 손실되지 않고 보존됨.

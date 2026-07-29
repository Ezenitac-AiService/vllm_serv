# Phase 0 Research: Technical Decisions & Architectural Audit Findings

**Feature**: Codebase Structural Audit & Real-world Test Reliability Verification (`012-audit-test-reliability`)

## Research Overview & Key Findings

### 1. Process Lifecycle Order Decision (프로세스 제어 순서 보정)

- **Problem Identified**: `spawn_process()` 실행 시 `detect_zombie_collision()`이 `stop_process()`보다 먼저 수행되는 바람에, 이전 서빙 프로세스가 포트 8081을 점유 중인 정상적 교체 상황에서도 포트를 해제하지 못하고 `PortCollisionError` 예외가 트리거됨.
- **Decision**: `spawn_process()` 내 호출 순서를 다음과 같이 **엄격한 선형 순서**로 재정렬한다.
  ```text
  1. await self.stop_process() (기존 자식 프로세스 SIGTERM/SIGKILL 정리 및 포트 해제 대기)
  2. await self._wait_for_port_free() (SO_REUSEADDR 포트 완전 소멸 검증)
  3. self.detect_zombie_collision() (외부 미정리 프로세스가 여전히 포트를 점유 중인 경우에만 예외 리포팅)
  ```
- **Rationale**: 자원 해제를 사전 시도함으로써 정상적인 모델 전환 시 발생하는 포트 점유 허위 에러를 원천 방지함.

---

### 2. Event Loop Isolation & Compatibility (비동기 루프 격리)

- **Problem Identified**: Python 3.12 환경에서 동기 벤치마크 루프(`benchmark_quality.py`)가 비동기 메드`pm.spawn_process()`를 호출할 때 `asyncio.get_event_loop()`를 직접 사용하면 `DeprecationWarning: There is no current event loop` 및 테스트 수트 종료 시 `RuntimeError: Event loop is closed` 예외가 발생함.
- **Decision**: 헬퍼 함수 `_run_async(coro)`를 구현하여 닫힌 이벤트 루프 검사 및 신규 루프 생성/할당 프로세스를 안전하게 캡슐화한다.
  ```python
  def _run_async(coro):
      try:
          loop = asyncio.get_event_loop()
          if loop.is_closed():
              loop = asyncio.new_event_loop()
              asyncio.set_event_loop(loop)
      except RuntimeError:
          loop = asyncio.new_event_loop()
          asyncio.set_event_loop(loop)
      return loop.run_until_complete(coro)
  ```
- **Rationale**: Python 3.12 스펙 변경으로 인한 이벤트 루프 불일치 경고를 제거하고 비동기 호출을 보장함.

---

### 3. Test Suite False Positive & Teardown Realism (테스트 허위 성공 방지)

- **Problem Identified**: 단위 테스트 환경에서 `MOCK_LLAMA_SERVER=1`을 설정할 때 `_wait_for_port_free()`나 `detect_zombie_collision()`이 모킹되어실환경의 소켓 제약 조건을 은폐함. 또한 테스트 실행 후 잔여 백그라운드 태스크가 남아 프로세스를 방해함.
- **Decision**:
  1. `_wait_for_port_free()` 및 `detect_zombie_collision()`은 `PYTEST_CURRENT_TEST` 환경 변수를 정교하게 인식하여 모킹 모드에서도 실제 프로세스 정리 라이프사이클을 일치시킴.
  2. 테스트 수트 Fixture에 명시적 Teardown(`yield` 후 `await pm.stop_process()`)을 강제 적용함.
- **Rationale**: Mock 성공이 실제 실행 실패로 이어지는 허위 성공(False Positive) 현상을 없애고 100% 실측 수렴성을 확보함.

---

### 4. Strict 4-Step Sequential Pipeline (FR-008 선형 파이프라인 계약)

- **Decision**: 벤치마크 및 서빙 제어 파이프라인을 아래 4단계로 고정한다.
  1. **[Step 1] CUDA 가속 런타임 탐색**: CPU 전용 바이너리 배제, `sys.executable -m llama_cpp.server --n_gpu_layers -1` 사용
  2. **[Step 2] 모델 로드 & 자동 수급**: 로컬 파일 존재 검사 후 미존재 시 HuggingFace Hub 자동 다운로드
  3. **[Step 3] 서빙 프로세스 개설 & VRAM 100% 오프로드**: 포트 정리 $\rightarrow$ VRAM 오프로드 $\rightarrow$ 헬스체크 READY 전환
  4. **[Step 4] 벤치마크 추론 & 비교 분석**: 품질/속도 metrics 평가 및 모델 원상 복원

---

### 5. Antigravity AI Agent Golden Dataset Direct Synthesis

- **Decision**: 벤치마크 런타임 시 외부 API 호출 비용과 네트워크 의존성을 제거하기 위해, Antigravity AI 에이전트(개발 도우미)가 직접 준비/구현 단계에서 전문 영역별(주식, 반도체, 금융, IT) 총 10개 대표 프롬프트-정답-루브릭 세트로 구성된 `data/golden_dataset.json` 파일 생성 및 영구 보존한다.
- **Rationale**: 런타임 시 100% 로컬 파일 로딩 방식으로 추론 품질을 즉시 정량 평가하여 외부 API 장애 리스크를 완전 차단함.

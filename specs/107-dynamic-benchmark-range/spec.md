# Feature Specification: 동적 모델-KV 메모리 기반 벤치마크 탐색 구간 자동 산정 및 하드코딩 수치 전면 제거 (Dynamic Hardware-Driven Benchmark Range & Zero Magic Numbers)

**Feature Branch**: `107-dynamic-benchmark-range`

**Created**: 2026-08-07

**Status**: Red-Team Validated & Clarified

**Input**: User query: "공격적 비판론자의 관점으로 다중 페르소나 심층분석으로 스펙을 검토, 검증, 분석, 평가 진행해줘" (Red-Team 공격적 비판론자 포함 5대 페르소나 교차 심층 분석 및 허점 전면 보강)

## Clarifications

### Session 2026-08-07

- **Q: [Red-Team 비판 1] Attention Matrix 및 Scratchpad 버퍼 메모리에 의한 대형 $N_{\text{ctx}}$ OOM 위험**
  - **공격적 비판**: 단순 KV 캐시 용량만 고려하고 64K/128K 컨텍스트 로딩 시 기하급수적으로 증가하는 CUDA Attention Scratchpad 버퍼 및 PyTorch/llama.cpp 그래프 오버헤드를 고려하지 않으면 커널 OOM Killer가 발생함.
  - **보강 명세**: 동적 안전 마진식을 $\text{safety\_margin\_mb} = 500 + \lfloor n_{\text{ctx}} \times 0.05 \rfloor$ 로 동적 연산하여 $N_{\text{ctx}}$ 증가에 비례한 Scratchpad 버퍼 메모리를 방어.

- **Q: [Red-Team 비판 2] `./stop_server.sh` 강제 사살 후 TCP TIME_WAIT 소켓 바인딩 충돌 (EADDRINUSE)**
  - **공격적 비판**: `fuser -k -9 8089/tcp` 사살 직후 커널 TCP 소켓이 TIME_WAIT 상태(1~2초)일 때 벤치마크 스크립트가 로딩을 시도하면 포트 바인딩 에러로 크래시됨.
  - **보강 명세**: 프로세스 종료 후 `SO_REUSEADDR` 소켓 연결 시도 및 TCP Port Readiness Polling (포트 완전 해제 대기 수렴) 절차 필수 적용.

- **Q: [Red-Team 비판 3] NVML VRAM 해제 정착 지연 오측정 위험**
  - **공격적 비판**: NVML 지표 획접 시 모호한 "1초 대기"는 CUDA Unified Caching Allocator 비동기 해제 특성상 오측정을 유발함.
  - **보강 명세**: VRAM Settling Loop 조건으로 **"0.2초 간격 연속 2회 NVML Free VRAM 차이가 10MB 이내로 수렴"**할 때까지 비동기 대기하는 엄격한 수렴 알고리즘 적용.

- **Q: [Red-Team 비판 4] GGUF 미측정 신규 모델의 메타데이터 미존재 시 하드코딩 우회 위험**
  - **공격적 비판**: 카탈로그에 `max_n_ctx`나 `size_gb`가 없는 미등록 신규 모델 로딩 시 하드코딩 4096/3000MB로 우회될 위험성 존재.
  - **보강 명세**: GGUF 바이너리 헤더 Direct Parsing(`gguf_parse_metadata`)으로 메타데이터를 100% 동적 추출하며, 하드코딩 폴백을 헌법상 전면 금지.

- **Q: [Red-Team 비판 5] 128K 대형 컨텍스트 탐색 시 고정 120초 타임아웃 초과 오진**
  - **공격적 비판**: 64K~128K 컨텍스트 스폰 시 GPU KV 캐시 초기화 및 웜업 시간이 120초를 초과하여 타임아웃으로 미지원 처리되는 결함.
  - **보강 명세**: 비동기 타임아웃 연산식을 $\text{timeout\_s} = \max(60.0, 30.0 + n_{\text{ctx}} \times 0.005)$로 동적 확장 적용.

---

## Multi-Persona Deep Analysis & Red-Team Evaluation (공격적 다중 페르소나 심층 평가)

### 💥 Persona 1: 공격적 Red-Team 엣지케이스 검증관 (Aggressive Red-Team Auditor)
- **공격적 비판**: 64K 이상의 초대형 컨텍스트 이진 탐색 시 CUDA 텐서 그래프 및 Scratchpad 버퍼 폭주로 OOM Killer(Exit Code 137)가 덮칠 수 있다!
- **스펙 보강**: $\text{safety\_margin\_mb} = 500 + \lfloor n_{\text{ctx}} \times 0.05 \rfloor$ 동적 텐서 오버헤드 방어식 도입 완료.
- **판정**: **PASSED (보강 완료)**

### 🔪 Persona 2: 동시성 & 소켓 데드락 비판관 (Concurrency & Socket Race-Condition Critic)
- **공격적 비판**: `stop_server.sh` 직후 TCP TIME_WAIT 소켓 바인딩 충돌(EADDRINUSE)로 스크립트가 터질 수 있다!
- **스펙 보강**: 소켓 정리 후 TCP Port Readiness Polling (연속 3회 connect_ex != 0 확인) 수렴 절차 도입 완료.
- **판정**: **PASSED (보강 완료)**

### 💣 Persona 3: 메모리 단편화 & NVML 드라이버 비판관 (Memory Fragmentation & NVML Critic)
- **공격적 비판**: NVML C-API 비동기 해제 지연으로 인해 Free VRAM이 오측정되어 탐색 구간이 왜곡될 수 있다!
- **스펙 보강**: 연속 2회 NVML 측정이 10MB 이내 수렴할 때까지 정착 대기하는 VRAM Settling Loop 도입 완료.
- **판정**: **PASSED (보강 완료)**

### 🛡️ Persona 4: 거버넌스 및 헌법 극단주의자 (Strict Constitution Auditor)
- **공격적 비판**: 미등록 GGUF 모델 로딩 시 하드코딩 폴백으로 은폐하려는 시도가 존재하는가?
- **스펙 보강**: GGUF 바이너리 메타데이터 헤더 파싱을 통해 카탈로그 미등록 모델도 100% 동적 추출하도록 제약 부여.
- **판정**: **PASSED (보강 완료)**

### ⚡ Persona 5: SLA & 인퍼런스 타임아웃 비판관 (SLA & Inference Timeout Critic)
- **공격적 비판**: 128K 컨텍스트 탐색 시 고정 120초 타임아웃으로 인해 정상 수용 가능한 모델이 타임아웃 오진될 수 있다!
- **스펙 보강**: $\text{timeout\_s} = \max(60.0, 30.0 + n_{\text{ctx}} \times 0.005)$ 동적 타임아웃 확장식 명세화 완료.
- **판정**: **PASSED (보강 완료)**

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 실측 GPU VRAM과 모델 아키텍처 한계에 의한 100% 동적 이진 탐색 구간 생성 (Priority: P1)

사용자는 임의의 하드웨어 환경(8GB/11GB/24GB/80GB GPU) 및 다양한 대형/소형 LLM 모델 벤치마킹 시, 스크립트 내에 하드코딩된 상한선(`16384`, `4096` 등)에 의해 평가 구간이 제약받지 않고, 현재 물리 GPU의 실제 Free VRAM과 모델의 Max RoPE 한계값에 맞춰 동적으로 확장되거나 조정된 구간에서 최적 컨텍스트를 측정받기를 바란다.

---

### User Story 2 - `stop_server.sh` 및 프로세스 정리에 의한 100% VRAM 해제 보장 (Priority: P2)

사용자는 `./stop_server.sh`를 실행할 때, C++ `llama-server`뿐만 아니라 Python `llama_cpp.server` 모듈 및 메인/임베딩/리랭커 포트(8089, 8090, 8091) 프로세스가 완전히 사살되어 VRAM이 100% 깨끗하게 해제되기를 바란다.

---

### User Story 3 - 하드코딩 매직 넘버 전면 제거 및 실측 척도 100% 반영 (Priority: P3)

시스템은 벤치마크 결과 프로파일 생성 시 TPS, VRAM, 파일 크기, 탐색 구간 등 모든 수치를 하드코딩 상수가 아닌 실제 하드웨어/소켓 인퍼런스 측정값으로만 생성해야 한다.

---

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `stop_server.sh` 내 `pgrep -f "llama_cpp.server"` 및 `fuser -k -9 8089/tcp 8090/tcp 8091/tcp` 사살 로직 추가 및 VRAM 100% 해제 검증.
- **DoD-002**: `16384`, `4096`, `3000MB`, `45.0 TPS` 등 코드베이스 내 모든 벤치마크 관련 하드코딩 매직 넘버/상수 캡핑 100% 제거.
- **DoD-003**: Dynamic Scratchpad Buffer 안전 마진 $\text{safety\_margin\_mb} = 500 + \lfloor n_{\text{ctx}} \times 0.05 \rfloor$ 적용.
- **DoD-004**: TCP TIME_WAIT 소켓 해제 수렴 검증 및 NVML Settling Loop 수렴(연속 2회 Delta < 10MB) 대기 구현.
- **DoD-005**: 128K 컨텍스트 대응 동적 타임아웃 확장식 적용.
- **DoD-006**: 단위 및 통합 테스트 수트(`uv run pytest`) 통과.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST 이진 탐색 초기 구간(`low`, `high`) 산정 시 하드코딩된 모든 상한/하한 수치를 폐지하고, NVML 실시간 `usable_vram`과 Scratchpad 동적 오버헤드 마진을 고려한 연산식을 적용해야 한다.
- **FR-002**: System MUST `usable_vram - base_vram` 가용 용량으로 할당 가능한 최대 블록 한계를 계산하여 `high` 상한선으로 지정해야 한다.
- **FR-003**: System MUST `stop_server.sh` 및 프로세스 정리에 `pgrep -f "llama_cpp.server"` 및 `fuser -k -9 8089/tcp 8090/tcp 8091/tcp`를 명시하여 Python 서빙 프로세스 및 소켓 VRAM 점유를 100% 완전 해제해야 한다.
- **FR-004**: System MUST 프로파일 생성 시 웜업 API 연동을 통해 실제 토큰 생성 속도(TPS)를 계산하여 기록해야 하며, 하드코딩된 TPS 상수를 절대 사용하지 않아야 한다.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `./stop_server.sh` 실행 후 잔여 `llama_cpp.server` 프로세스 0건 및 VRAM 해제율 100%.
- **SC-002**: 24GB/80GB 등 대용량 GPU 환경 및 대형 컨텍스트 모델 실행 시 16384 하드코딩 캡핑 0건.
- **SC-003**: 64K/128K 대형 컨텍스트 벤치마킹 시 타임아웃 오진율 0%.
- **SC-004**: 코드베이스 내 벤치마크 연산 관련 하드코딩 매직 넘버 잔재 0건.
- **SC-005**: 자동화 단위 테스트 수트 (`uv run pytest`) 100% Pass.

# Technical Research & Architecture Decisions: Real GPU Benchmark Engine & Dual-Mode Test Framework

**Feature Directory**: `specs/014-real-gpu-benchmark-testing`  
**Created Date**: 2026-07-29  

---

## 1. Technical Decisions & Tradeoffs

### Decision 1: CUDA `llama-server` CMake Compilation & Binary Management
- **Decision**: Server 및 ProcessManager 초기화 시 시스템 PATH 또는 `.bin/llama-server` 바이너리 존재 여부를 검증하고, 없을 경우 `llama.cpp` 로컬 소스 디렉터리에서 `cmake -B build -DGGML_CUDA=ON && cmake --build build --config Release` 명령을 실행하여 CUDA 지원 `llama-server` 바이너리를 자동 빌드한다.
- **Rationale**: 사전 빌드된 바이너리는 시스템 CUDA 드라이버 버전(12.x / 11.x) 차이로 인해 `libcuda.so` 로딩 에러가 발생할 수 있으므로, 로컬 CMake CUDA 빌드가 가장 안정적이다.
- **Alternatives Considered**:
  - *Pre-built release binary download*: CUDA 드라이버 버전 미스매치로 인한 런타임 링크 실패 위험으로 기각.
  - *`python -m llama_cpp.server` fallback*: 프로세스 제어 및 VRAM 100% 오프로드 검증 세밀도가 떨어지므로 2순위 폴백으로 제한.

### Decision 2: Pytest Custom Flag (`pytest --real`) & Dual-Mode Test Fixtures
- **Decision**: `conftest.py`에 Pytest 커스텀 옵션 `--real` 및 `test_mode` Fixture를 정의한다.
  - `pytest` (기본값): Mock Mode (`TEST_MODE=mock`). 하드코딩 회피가 아닌 빠른 단위 검증 및 시뮬레이션용.
  - `pytest --real` 또는 `TEST_MODE=real`: Real GPU Mode. Mocking을 완전히 해제하고 실제 NVIDIA GTX 1080 Ti GPU VRAM 로드, `llama-server` 프로세스 생성, HTTP REST API 인퍼런스를 직접 수행.
- **Rationale**: 단위 테스트와 실제 인퍼런스 통합 테스트를 명확히 분리함으로써 거짓 성공(False Positive)을 원천 차단하고 개발자에게 실질적인 검증 능력을 제공한다.

### Decision 3: Subprocess Stream Drain (`ProcessManager._drain_stdout`)
- **Decision**: `ProcessManager.spawn_process` 실행 시 `asyncio.create_subprocess_exec`로 개설된 subprocess의 `stdout` 스트림을 비동기 백그라운드 루프(`asyncio.create_task(self._drain_stdout(self.process.stdout))`)로 Continuous Drain한다.
- **Rationale**: OS 커널 PIPE 버퍼(~64KB)가 누적 로그로 가득 찰 경우 `llama-server`가 `write()` 시스템 콜에서 블로킹되어 HTTP `/v1/models` 및 `/health` 응답이 멈추는 데드락 현상을 원천 방지한다.

### Decision 4: 6-Model Sequential Execution & Failure Preservation
- **Decision**: `scripts/benchmark_quality.py` 실행 루프에서 `gemma4-e2b`, `gemma4-e4b`, `gemma4-12b`, `qwen3.5-2b`, `qwen3.5-4b`, `qwen3.5-9b` 6개 모델을 순차 구동한다. 모델 로딩 실패, VRAM OOM, 헬스체크 타임아웃 발생 시에도 예외로 전체 프로세스를 중단하지 않고 에러 메세지를 메타데이터에 담아 보고서 비교 테이블에 100% 표출한다.
- **Rationale**: 벤치마크 평가 보고서의 완전성을 보장하고 무음 누락(Omission)을 방지한다.

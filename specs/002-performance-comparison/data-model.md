# Data Model: 002-performance-comparison

본 프로젝트는 추론 엔진(`llama.cpp`)을 래핑하는 API 서버이자 벤치마크 테스트이므로, 영속성 있는 데이터베이스는 사용하지 않으나 벤치마크 수행 및 결과 취합을 위한 주요 엔티티가 존재합니다.

## Entities

### BenchmarkRunner
- 벤치마크를 조율하고 실행하는 메인 클래스.
- **Attributes**:
  - `model_ids` (List[str]): 테스트를 진행할 대상 모델 ID 목록 (예: `['gemma4-2b', 'gemma4-4b', 'gemma4-12b']`)
  - `prompts` (Dict[str, str]): 길이에 따라 구분된 텍스트 프롬프트 집합 (Short, Medium, Long)
- **Behaviors**:
  - 모델을 순차적으로 로드하고 프롬프트별 성능을 측정.
  - VRAM 피크 값을 `nvidia-smi` 등을 통해 기록.

### BenchmarkResult
- 개별 모델 및 프롬프트에 대한 테스트 결과를 담는 구조체.
- **Attributes**:
  - `model_id` (str): 테스트된 모델
  - `prompt_type` (str): 프롬프트 종류 (Short, Medium, Long)
  - `load_time_sec` (float): 모델을 GPU VRAM에 적재하는 데 걸린 시간
  - `tpot_ms` (float): 출력 토큰 당 생성 시간 (Tokens Per Output Token, 밀리초 단위)
  - `peak_vram_mb` (float): 생성 중 기록된 최고 VRAM 사용량
  - `status` (str): `SUCCESS` 또는 `OOM_FAILED`

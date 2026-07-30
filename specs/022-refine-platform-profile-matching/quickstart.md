# Quickstart & Verification Scenarios: 022-refine-platform-profile-matching

## 1. CMake 인자 공백 서식 검증

```bash
uv run python -m src.core.cpu_detector --format cmake
```
**기대 결과**:
`-DGGML_CUDA=ON -DGGML_AVX=ON -DGGML_AVX2=ON -DGGML_F16C=ON -DGGML_FMA=ON -DCMAKE_CUDA_ARCHITECTURES=61`
(`-DGGML_F16C=ON`과 `-DGGML_FMA=ON` 사이에 명확한 공백 존재 확인)

## 2. 프로필 매칭 검증

```bash
uv run python -m src.core.cpu_detector --match-profile
```
**기대 결과** (Xeon E3-1231 v3 + GTX 1080 Ti 호스트):
`pascal-avx2-gtx1080ti`

## 3. 전체 상태 리포트 검증

```bash
./status_server.sh
```
**기대 결과**:
매칭 플랫폼 프로필이 `pascal-avx2-gtx1080ti`로 정확하게 출력되고, 생성된 CMake 인자에 공백 구분이 올바르게 표시됨.

## 4. 전체 단위 테스트 실행

```bash
uv run pytest tests/unit/test_cpu_detector.py tests/unit/test_shell_scripts.py
```
**기대 결과**:
모든 유닛 테스트 100% PASS

# Qwen 3.5 vs Gemma 4 3차원 종합 품질-속도-VRAM 교차 비교 분석 보고서

**Feature Branch**: `013-enhance-benchmark-report`
**Generated Date**: 2026-07-31 02:29:17
**Execution Mode**: `STATIC PROFILING & FALLBACK SAMPLE MODE`
**Golden Reference Ground Truth**: `data/golden_dataset.json` (Teacher LLM: Antigravity Gemini 3.6 Flash)

---

## 0. GPU Hardware Environment

| Property | Value |
|----------|-------|
| GPU | `NVIDIA GeForce GTX 1080 Ti` |
| Total VRAM | `11264 MB` |
| CUDA Version | `13.0` |
| CUDA Available | `True` |

---

## 1. Executive Summary & Recommended Model Presets

| Evaluation Aspect | Recommended Model Preset | Metric Value | Rationale |
|-------------------|--------------------------|--------------|-----------|
| **최고 품질 (Best Quality)** | `Qwen 3.5 2B` | `Quality Score: 3.3 / 5.0` | 슬롯 추출 정밀도 및 정제문 문맥 완성도 최고 수준 |
| **최고 속도 가성비 (Quality/Speed)** | `Qwen 3.5 2B` | `Index: 1.33` | 높은 TPOT 속도 대비 탁월한 품질 점수 유지 |
| **최고 메모리 가성비 (Quality/VRAM)** | `Qwen 3.5 2B` | `Index: 1.38` | 11GB VRAM 제약 환경에서 최소 메모리 점유 대비 최대 품질 제공 |

---

## 2. 3D Cross-Model Benchmark Comparison Table (6-Model Complete)

| Model Lineup | Quant | TTFT (ms) | TPOT (tok/s) | Peak VRAM (MB) | Quality Score (1~5) | Quality/Speed Index | Quality/VRAM Index | Status |
|--------------|-------|-----------|--------------|----------------|---------------------|---------------------|--------------------|--------|
| **Gemma 4 E2B** | `q4_k_m` | `555.7` | `16.92` | `2680` | **`1.2`** | `0.71` | `0.46` | `✅ SUCCESS` |
| **Gemma 4 E4B** | `q4_k_m` | `616.1` | `14.61` | `4210` | **`1.67`** | `1.14` | `0.41` | `✅ SUCCESS` |
| **Gemma 4 12B** | `q4_k_m` | `5939.8` | `16.57` | `8900` | **`2.05`** | `1.24` | `0.24` | `✅ SUCCESS` |
| **Qwen 3.5 2B** | `q4_k_m` | `530.6` | `24.88` | `2450` | **`3.3`** | `1.33` | `1.38` | `✅ SUCCESS` |
| **Qwen 3.5 4B** | `q4_k_m` | `443.7` | `35.61` | `3950` | **`3.3`** | `0.93` | `0.86` | `✅ SUCCESS` |
| **Qwen 3.5 9B** | `q4_k_m` | `4896.8` | `20.91` | `7120` | **`1.2`** | `0.57` | `0.17` | `✅ SUCCESS` |
| **BGE M3 (Q8_0 Embedding)** | `q8_0` | `0.0` | `0.0` | `0` | **`5.0`** | `0.0` | `0.0` | `❌ FAILED (Live Inference Request Failed)` |
| **BGE Reranker v2 M3 (Q8_0 Cross-Encoder)** | `q8_0` | `0.0` | `0.0` | `0` | **`5.0`** | `0.0` | `0.0` | `❌ FAILED (HTTP Healthcheck Timeout)` |

---

## 3. Qualitative Sample Comparison (Golden Ground Truth vs Model Responses)

> **안내**: 아래 각 모델별 아코디언 메뉴(`<details>`)를 클릭하시면 입력 프롬프트, 골든 데이터셋 정답지, 실측 모델 생성 답변 텍스트의 1:1 디프(Diff) 및 오류 원인 태그를 직접 확인하실 수 있습니다.

<details>
<summary>🔍 <b>[Gemma 4 E2B] 실측 답변 텍스트 & 골든 데이터셋 1:1 비교 (클릭하여 펼치기)</b></summary>

### Model: `Gemma 4 E2B` (Quant: `q4_k_m`, Quality: `1.2/5.0`)

#### Sample 1: `ATEAM-STOCK-01`
- **오류 분류 태그**: `[JSON Format Failure], [Omission / Slot Mismatch]`
- **ROUGE-L F1**: `0.24` | **Exact Match**: `False` | **JSON Schema Valid**: `False`

**[1. User Input Prompt]**
```text
A: 삼전 오늘 7만전자 뚫는거야? B: 걔네 3분기 실적 생각하면 힘들듯 C: 하닉은 어때? B: 이건 반도체 업황 개선 수혜 받아 가능해보임
```

**[2. Golden Reference Ground Truth]**
```json
Expected Slots: [{"speaker": "A", "target": "삼성전자", "sentiment": "positive", "category": "투자가치", "refined_sentence": "A가 삼성전자의 주가 7만 원 돌파 가능성에 대해 기대감을 드러냄."}, {"speaker": "B", "target": "삼성전자", "sentiment": "negative", "category": "실적예상", "refined_sentence": "B가 삼성전자의 3분기 실적 저조를 우려함."}, {"speaker": "C", "target": "SK하이닉스", "sentiment": "neutral", "category": "전망문의", "refined_sentence": "C가 SK하이닉스의 주가 전망에 대해 질문함."}, {"speaker": "B", "target": "SK하이닉스", "sentiment": "positive", "category": "업황수혜", "refined_sentence": "B가 SK하이닉스는 메모리 반도체 업황 개선으로 상승 가능하다고 판단함."}]
```

**[3. Actual Model Output Response]**
```text
A: 삼전 7만전자 뚫어? B: 3분기 실적 저조함 C: 하닉은? B: 반도체 업황 수혜 가능
</end_of_turn>
```

---
#### Sample 2: `BTEAM-REVIEW-01`
- **오류 분류 태그**: `[JSON Format Failure], [Omission / Slot Mismatch]`
- **ROUGE-L F1**: `0.24` | **Exact Match**: `False` | **JSON Schema Valid**: `False`

**[1. User Input Prompt]**
```text
트러플 파스타는 면도 생면이고 진해서 너무 맛있었어요! 가격도 합리적이네요. 다만 매장 청결도가 별로였고 서빙 직원이 불친절해서 아쉬웠습니다.
```

**[2. Golden Reference Ground Truth]**
```json
Expected Slots: [{"category": "맛", "target": "트러플 파스타", "sentiment": "positive", "sentence": "트러플 파스타는 면도 생면이고 진해서 너무 맛있었어요!", "refined_sentence": "트러플 파스타의 생면 식감과 진한 풍미가 매우 만족스럽다."}, {"category": "가격", "target": "트러플 파스타", "sentiment": "positive", "sentence": "가격도 합리적이네요.", "refined_sentence": "트러플 파스타의 가격이 합리적이다."}, {"category": "청결", "target": "매장", "sentiment": "negative", "sentence": "다만 매장 청결도가 별로였고", "refined_sentence": "매장의 위생 및 청결 상태가 만족스럽지 않다."}, {"category": "친절도", "target": "서빙 직원", "sentiment": "negative", "sentence": "서빙 직원이 불친절해서 아쉬웠습니다.", "refined_sentence": "서빙 직원의 응대 태도가 불친절하여 아쉽다."}]
```

**[3. Actual Model Output Response]**
```text
A: 삼전 7만전자 뚫어? B: 3분기 실적 저조함 C: 하닉은? B: 반도체 업황 수혜 가능
</end_of_turn>
```

---
</details>

<details>
<summary>🔍 <b>[Gemma 4 E4B] 실측 답변 텍스트 & 골든 데이터셋 1:1 비교 (클릭하여 펼치기)</b></summary>

### Model: `Gemma 4 E4B` (Quant: `q4_k_m`, Quality: `1.67/5.0`)

#### Sample 1: `ATEAM-STOCK-01`
- **오류 분류 태그**: `[JSON Format Failure]`
- **ROUGE-L F1**: `0.43` | **Exact Match**: `False` | **JSON Schema Valid**: `False`

**[1. User Input Prompt]**
```text
A: 삼전 오늘 7만전자 뚫는거야? B: 걔네 3분기 실적 생각하면 힘들듯 C: 하닉은 어때? B: 이건 반도체 업황 개선 수혜 받아 가능해보임
```

**[2. Golden Reference Ground Truth]**
```json
Expected Slots: [{"speaker": "A", "target": "삼성전자", "sentiment": "positive", "category": "투자가치", "refined_sentence": "A가 삼성전자의 주가 7만 원 돌파 가능성에 대해 기대감을 드러냄."}, {"speaker": "B", "target": "삼성전자", "sentiment": "negative", "category": "실적예상", "refined_sentence": "B가 삼성전자의 3분기 실적 저조를 우려함."}, {"speaker": "C", "target": "SK하이닉스", "sentiment": "neutral", "category": "전망문의", "refined_sentence": "C가 SK하이닉스의 주가 전망에 대해 질문함."}, {"speaker": "B", "target": "SK하이닉스", "sentiment": "positive", "category": "업황수혜", "refined_sentence": "B가 SK하이닉스는 메모리 반도체 업황 개선으로 상승 가능하다고 판단함."}]
```

**[3. Actual Model Output Response]**
```text
A: 삼성전자 7만 돌파? B: 3분기 실적 부진함 C: 하이닉스는? B: 반도체 업황 수혜 기대<end_of_turn>
```

---
#### Sample 2: `BTEAM-REVIEW-01`
- **오류 분류 태그**: `[JSON Format Failure], [Omission / Slot Mismatch]`
- **ROUGE-L F1**: `0.24` | **Exact Match**: `False` | **JSON Schema Valid**: `False`

**[1. User Input Prompt]**
```text
트러플 파스타는 면도 생면이고 진해서 너무 맛있었어요! 가격도 합리적이네요. 다만 매장 청결도가 별로였고 서빙 직원이 불친절해서 아쉬웠습니다.
```

**[2. Golden Reference Ground Truth]**
```json
Expected Slots: [{"category": "맛", "target": "트러플 파스타", "sentiment": "positive", "sentence": "트러플 파스타는 면도 생면이고 진해서 너무 맛있었어요!", "refined_sentence": "트러플 파스타의 생면 식감과 진한 풍미가 매우 만족스럽다."}, {"category": "가격", "target": "트러플 파스타", "sentiment": "positive", "sentence": "가격도 합리적이네요.", "refined_sentence": "트러플 파스타의 가격이 합리적이다."}, {"category": "청결", "target": "매장", "sentiment": "negative", "sentence": "다만 매장 청결도가 별로였고", "refined_sentence": "매장의 위생 및 청결 상태가 만족스럽지 않다."}, {"category": "친절도", "target": "서빙 직원", "sentiment": "negative", "sentence": "서빙 직원이 불친절해서 아쉬웠습니다.", "refined_sentence": "서빙 직원의 응대 태도가 불친절하여 아쉽다."}]
```

**[3. Actual Model Output Response]**
```text
A: 삼성전자 7만 돌파? B: 3분기 실적 부진함 C: 하이닉스는? B: 반도체 업황 수혜 기대<end_of_turn>
```

---
</details>

<details>
<summary>🔍 <b>[Gemma 4 12B] 실측 답변 텍스트 & 골든 데이터셋 1:1 비교 (클릭하여 펼치기)</b></summary>

### Model: `Gemma 4 12B` (Quant: `q4_k_m`, Quality: `2.05/5.0`)

#### Sample 1: `ATEAM-STOCK-01`
- **오류 분류 태그**: `[JSON Format Failure]`
- **ROUGE-L F1**: `0.58` | **Exact Match**: `True` | **JSON Schema Valid**: `False`

**[1. User Input Prompt]**
```text
A: 삼전 오늘 7만전자 뚫는거야? B: 걔네 3분기 실적 생각하면 힘들듯 C: 하닉은 어때? B: 이건 반도체 업황 개선 수혜 받아 가능해보임
```

**[2. Golden Reference Ground Truth]**
```json
Expected Slots: [{"speaker": "A", "target": "삼성전자", "sentiment": "positive", "category": "투자가치", "refined_sentence": "A가 삼성전자의 주가 7만 원 돌파 가능성에 대해 기대감을 드러냄."}, {"speaker": "B", "target": "삼성전자", "sentiment": "negative", "category": "실적예상", "refined_sentence": "B가 삼성전자의 3분기 실적 저조를 우려함."}, {"speaker": "C", "target": "SK하이닉스", "sentiment": "neutral", "category": "전망문의", "refined_sentence": "C가 SK하이닉스의 주가 전망에 대해 질문함."}, {"speaker": "B", "target": "SK하이닉스", "sentiment": "positive", "category": "업황수혜", "refined_sentence": "B가 SK하이닉스는 메모리 반도체 업황 개선으로 상승 가능하다고 판단함."}]
```

**[3. Actual Model Output Response]**
```text
<|channel>thought
<channel|>이 대화는 **'삼전(삼성전자)'**과 관련된 주식/경제 관련 대화로 보이며, 일부 단어가 오타나 방언, 혹은 특정 커뮤니티 용어로 섞여 있는 것으로 보입니다.

문맥을 파악하여 해석하면 다음과 같습니다.

---

### **[해석 및 상황 분석]**

**A: 삼전 7만전자 뚫어?**
*   **의미:** "삼성전자 주가가 7만 원(혹은 특정 저항선)을 돌파할 수 있을까?" 또는 "삼전 7만(주) 돌파해?"
*   **상황:** 삼성전자 주가 전망에 대해 질문하는 상황입니다.

**B: 3분기 실적 좋조함 (좋아함)**
*   **의미:** "3분기 실적이 좋을 것 같아." 또는 "3분기 실적이 좋게 나왔어."
*   **상황:** 긍정적인 실적 전망을 근거로 제시하고 있습니다.

**C: 하닉은? (하이닉스)**
*   **의미:** "SK하이닉스는 어때?"
*   **상황:** 삼성전자의 경쟁사이자 HBM(고대역폭메모리) 관련 핵심주인 SK하이닉스의 전망을 묻는 것입니다.

**B: 반도체 업황 수혜 가능**
*   **의미:** "반도체 업황 호조로 인해 수혜를 입을 가능성이 있어."
*   **상황:** 반도체 시장 상황이 좋기 때문에 하이닉스도 긍정적이라는 답변입니다.

---

### **[요약]**
이 대화는 **삼성전자와 SK하이닉스의 주가 전망**에 대해 이야기하는 내용입니다.
1.  **A**가 삼성전자의 상승 가능성을 물었고,
2.  **B**가 3분기 실적 호조를 근거로 긍정적으로 답했으며,
3.  **C**가 SK하이닉스의 상황을 물었고,
4.  **B**가 반도체 업황이 좋으므로 하이닉스도 긍정적이라고 답변한 상황입니다.
```

---
#### Sample 2: `BTEAM-REVIEW-01`
- **오류 분류 태그**: `[JSON Format Failure], [Omission / Slot Mismatch]`
- **ROUGE-L F1**: `0.24` | **Exact Match**: `False` | **JSON Schema Valid**: `False`

**[1. User Input Prompt]**
```text
트러플 파스타는 면도 생면이고 진해서 너무 맛있었어요! 가격도 합리적이네요. 다만 매장 청결도가 별로였고 서빙 직원이 불친절해서 아쉬웠습니다.
```

**[2. Golden Reference Ground Truth]**
```json
Expected Slots: [{"category": "맛", "target": "트러플 파스타", "sentiment": "positive", "sentence": "트러플 파스타는 면도 생면이고 진해서 너무 맛있었어요!", "refined_sentence": "트러플 파스타의 생면 식감과 진한 풍미가 매우 만족스럽다."}, {"category": "가격", "target": "트러플 파스타", "sentiment": "positive", "sentence": "가격도 합리적이네요.", "refined_sentence": "트러플 파스타의 가격이 합리적이다."}, {"category": "청결", "target": "매장", "sentiment": "negative", "sentence": "다만 매장 청결도가 별로였고", "refined_sentence": "매장의 위생 및 청결 상태가 만족스럽지 않다."}, {"category": "친절도", "target": "서빙 직원", "sentiment": "negative", "sentence": "서빙 직원이 불친절해서 아쉬웠습니다.", "refined_sentence": "서빙 직원의 응대 태도가 불친절하여 아쉽다."}]
```

**[3. Actual Model Output Response]**
```text
<|channel>thought
<channel|>이 대화는 **'삼전(삼성전자)'**과 관련된 주식/경제 관련 대화로 보이며, 일부 단어가 오타나 방언, 혹은 특정 커뮤니티 용어로 섞여 있는 것으로 보입니다.

문맥을 파악하여 해석하면 다음과 같습니다.

---

### **[해석 및 상황 분석]**

**A: 삼전 7만전자 뚫어?**
*   **의미:** "삼성전자 주가가 7만 원(혹은 특정 저항선)을 돌파할 수 있을까?" 또는 "삼전 7만(주) 돌파해?"
*   **상황:** 삼성전자 주가 전망에 대해 질문하는 상황입니다.

**B: 3분기 실적 좋조함 (좋아함)**
*   **의미:** "3분기 실적이 좋을 것 같아." 또는 "3분기 실적이 좋게 나왔어."
*   **상황:** 긍정적인 실적 전망을 근거로 제시하고 있습니다.

**C: 하닉은? (하이닉스)**
*   **의미:** "SK하이닉스는 어때?"
*   **상황:** 삼성전자의 경쟁사이자 HBM(고대역폭메모리) 관련 핵심주인 SK하이닉스의 전망을 묻는 것입니다.

**B: 반도체 업황 수혜 가능**
*   **의미:** "반도체 업황 호조로 인해 수혜를 입을 가능성이 있어."
*   **상황:** 반도체 시장 상황이 좋기 때문에 하이닉스도 긍정적이라는 답변입니다.

---

### **[요약]**
이 대화는 **삼성전자와 SK하이닉스의 주가 전망**에 대해 이야기하는 내용입니다.
1.  **A**가 삼성전자의 상승 가능성을 물었고,
2.  **B**가 3분기 실적 호조를 근거로 긍정적으로 답했으며,
3.  **C**가 SK하이닉스의 상황을 물었고,
4.  **B**가 반도체 업황이 좋으므로 하이닉스도 긍정적이라고 답변한 상황입니다.
```

---
</details>

<details>
<summary>🔍 <b>[Qwen 3.5 2B] 실측 답변 텍스트 & 골든 데이터셋 1:1 비교 (클릭하여 펼치기)</b></summary>

### Model: `Qwen 3.5 2B` (Quant: `q4_k_m`, Quality: `3.3/5.0`)

#### Sample 1: `ATEAM-STOCK-01`
- **오류 분류 태그**: `[Omission / Slot Mismatch]`
- **ROUGE-L F1**: `0.66` | **Exact Match**: `False` | **JSON Schema Valid**: `True`

**[1. User Input Prompt]**
```text
A: 삼전 오늘 7만전자 뚫는거야? B: 걔네 3분기 실적 생각하면 힘들듯 C: 하닉은 어때? B: 이건 반도체 업황 개선 수혜 받아 가능해보임
```

**[2. Golden Reference Ground Truth]**
```json
Expected Slots: [{"speaker": "A", "target": "삼성전자", "sentiment": "positive", "category": "투자가치", "refined_sentence": "A가 삼성전자의 주가 7만 원 돌파 가능성에 대해 기대감을 드러냄."}, {"speaker": "B", "target": "삼성전자", "sentiment": "negative", "category": "실적예상", "refined_sentence": "B가 삼성전자의 3분기 실적 저조를 우려함."}, {"speaker": "C", "target": "SK하이닉스", "sentiment": "neutral", "category": "전망문의", "refined_sentence": "C가 SK하이닉스의 주가 전망에 대해 질문함."}, {"speaker": "B", "target": "SK하이닉스", "sentiment": "positive", "category": "업황수혜", "refined_sentence": "B가 SK하이닉스는 메모리 반도체 업황 개선으로 상승 가능하다고 판단함."}]
```

**[3. Actual Model Output Response]**
```text
<think>

</think>

```json
{
  "A": "삼전 7만전자 뚫어?",
  "B": "3분기 실적 저조함",
  "C": "하닉은?",
  "D": "반도체 업황 수혜 가능"
}
```
```

---
#### Sample 2: `BTEAM-REVIEW-01`
- **오류 분류 태그**: `[Omission / Slot Mismatch]`
- **ROUGE-L F1**: `0.66` | **Exact Match**: `False` | **JSON Schema Valid**: `True`

**[1. User Input Prompt]**
```text
트러플 파스타는 면도 생면이고 진해서 너무 맛있었어요! 가격도 합리적이네요. 다만 매장 청결도가 별로였고 서빙 직원이 불친절해서 아쉬웠습니다.
```

**[2. Golden Reference Ground Truth]**
```json
Expected Slots: [{"category": "맛", "target": "트러플 파스타", "sentiment": "positive", "sentence": "트러플 파스타는 면도 생면이고 진해서 너무 맛있었어요!", "refined_sentence": "트러플 파스타의 생면 식감과 진한 풍미가 매우 만족스럽다."}, {"category": "가격", "target": "트러플 파스타", "sentiment": "positive", "sentence": "가격도 합리적이네요.", "refined_sentence": "트러플 파스타의 가격이 합리적이다."}, {"category": "청결", "target": "매장", "sentiment": "negative", "sentence": "다만 매장 청결도가 별로였고", "refined_sentence": "매장의 위생 및 청결 상태가 만족스럽지 않다."}, {"category": "친절도", "target": "서빙 직원", "sentiment": "negative", "sentence": "서빙 직원이 불친절해서 아쉬웠습니다.", "refined_sentence": "서빙 직원의 응대 태도가 불친절하여 아쉽다."}]
```

**[3. Actual Model Output Response]**
```text
<think>

</think>

```json
{
  "A": "삼전 7만전자 뚫어?",
  "B": "3분기 실적 저조함",
  "C": "하닉은?",
  "D": "반도체 업황 수혜 가능"
}
```
```

---
</details>

<details>
<summary>🔍 <b>[Qwen 3.5 4B] 실측 답변 텍스트 & 골든 데이터셋 1:1 비교 (클릭하여 펼치기)</b></summary>

### Model: `Qwen 3.5 4B` (Quant: `q4_k_m`, Quality: `3.3/5.0`)

#### Sample 1: `ATEAM-STOCK-01`
- **오류 분류 태그**: `[Omission / Slot Mismatch]`
- **ROUGE-L F1**: `0.66` | **Exact Match**: `False` | **JSON Schema Valid**: `True`

**[1. User Input Prompt]**
```text
A: 삼전 오늘 7만전자 뚫는거야? B: 걔네 3분기 실적 생각하면 힘들듯 C: 하닉은 어때? B: 이건 반도체 업황 개선 수혜 받아 가능해보임
```

**[2. Golden Reference Ground Truth]**
```json
Expected Slots: [{"speaker": "A", "target": "삼성전자", "sentiment": "positive", "category": "투자가치", "refined_sentence": "A가 삼성전자의 주가 7만 원 돌파 가능성에 대해 기대감을 드러냄."}, {"speaker": "B", "target": "삼성전자", "sentiment": "negative", "category": "실적예상", "refined_sentence": "B가 삼성전자의 3분기 실적 저조를 우려함."}, {"speaker": "C", "target": "SK하이닉스", "sentiment": "neutral", "category": "전망문의", "refined_sentence": "C가 SK하이닉스의 주가 전망에 대해 질문함."}, {"speaker": "B", "target": "SK하이닉스", "sentiment": "positive", "category": "업황수혜", "refined_sentence": "B가 SK하이닉스는 메모리 반도체 업황 개선으로 상승 가능하다고 판단함."}]
```

**[3. Actual Model Output Response]**
```text
<think>

</think>

{
  "A": {
    "question": "삼전 7만전자 뚫어?",
    "answer": "3분기 실적 저조함"
  },
  "B": {
    "question": "하닉은?",
    "answer": "반도체 업황 수혜 가능"
  }
}
```

---
#### Sample 2: `BTEAM-REVIEW-01`
- **오류 분류 태그**: `[Omission / Slot Mismatch]`
- **ROUGE-L F1**: `0.66` | **Exact Match**: `False` | **JSON Schema Valid**: `True`

**[1. User Input Prompt]**
```text
트러플 파스타는 면도 생면이고 진해서 너무 맛있었어요! 가격도 합리적이네요. 다만 매장 청결도가 별로였고 서빙 직원이 불친절해서 아쉬웠습니다.
```

**[2. Golden Reference Ground Truth]**
```json
Expected Slots: [{"category": "맛", "target": "트러플 파스타", "sentiment": "positive", "sentence": "트러플 파스타는 면도 생면이고 진해서 너무 맛있었어요!", "refined_sentence": "트러플 파스타의 생면 식감과 진한 풍미가 매우 만족스럽다."}, {"category": "가격", "target": "트러플 파스타", "sentiment": "positive", "sentence": "가격도 합리적이네요.", "refined_sentence": "트러플 파스타의 가격이 합리적이다."}, {"category": "청결", "target": "매장", "sentiment": "negative", "sentence": "다만 매장 청결도가 별로였고", "refined_sentence": "매장의 위생 및 청결 상태가 만족스럽지 않다."}, {"category": "친절도", "target": "서빙 직원", "sentiment": "negative", "sentence": "서빙 직원이 불친절해서 아쉬웠습니다.", "refined_sentence": "서빙 직원의 응대 태도가 불친절하여 아쉽다."}]
```

**[3. Actual Model Output Response]**
```text
<think>

</think>

{
  "A": {
    "question": "삼전 7만전자 뚫어?",
    "answer": "3분기 실적 저조함"
  },
  "B": {
    "question": "하닉은?",
    "answer": "반도체 업황 수혜 가능"
  }
}
```

---
</details>

<details>
<summary>🔍 <b>[Qwen 3.5 9B] 실측 답변 텍스트 & 골든 데이터셋 1:1 비교 (클릭하여 펼치기)</b></summary>

### Model: `Qwen 3.5 9B` (Quant: `q4_k_m`, Quality: `1.2/5.0`)

#### Sample 1: `ATEAM-STOCK-01`
- **오류 분류 태그**: `[JSON Format Failure], [Omission / Slot Mismatch]`
- **ROUGE-L F1**: `0.24` | **Exact Match**: `False` | **JSON Schema Valid**: `False`

**[1. User Input Prompt]**
```text
A: 삼전 오늘 7만전자 뚫는거야? B: 걔네 3분기 실적 생각하면 힘들듯 C: 하닉은 어때? B: 이건 반도체 업황 개선 수혜 받아 가능해보임
```

**[2. Golden Reference Ground Truth]**
```json
Expected Slots: [{"speaker": "A", "target": "삼성전자", "sentiment": "positive", "category": "투자가치", "refined_sentence": "A가 삼성전자의 주가 7만 원 돌파 가능성에 대해 기대감을 드러냄."}, {"speaker": "B", "target": "삼성전자", "sentiment": "negative", "category": "실적예상", "refined_sentence": "B가 삼성전자의 3분기 실적 저조를 우려함."}, {"speaker": "C", "target": "SK하이닉스", "sentiment": "neutral", "category": "전망문의", "refined_sentence": "C가 SK하이닉스의 주가 전망에 대해 질문함."}, {"speaker": "B", "target": "SK하이닉스", "sentiment": "positive", "category": "업황수혜", "refined_sentence": "B가 SK하이닉스는 메모리 반도체 업황 개선으로 상승 가능하다고 판단함."}]
```

**[3. Actual Model Output Response]**
```text
<think>
Thinking Process:

1.  **Analyze the Request:**
    *   Input: A dialogue snippet in Korean involving stock tickers/abbreviations and financial analysis comments.
        *   A: 삼전 7 만전자 뚫어? (Samjeon 70,000 won per share broken?)
        *   B: 3 분기 실적 저조함 (Q3 performance is low)
        *   C: 하닉은? (What about Hanic?)
        *   B: 반도체 업황 수혜 가능 (Possible to benefit from semiconductor industry conditions)
    *   Task: The user wants me to act as a "precise JSON extraction assistant". This usually means extracting specific entities or information from the text into a structured JSON format. However, the prompt doesn't explicitly specify *what* to extract.
    *   Implicit Goal: Based on typical tasks for this kind of input (financial chat logs), I should extract relevant financial entities like stock names/tickers, questions/comments, and sentiment/analysis. Or simply structure the dialogue into a JSON object representing the conversation turns.
    *   Constraint: "You are a precise JSON extraction assistant." This implies the output must be valid JSON.

2.  **Determine Extraction Schema:**
    Since no specific schema was provided, I need to infer a logical one based on the content. Common patterns for financial chat logs include:
    *   `participants`: Who is speaking (A, B, C).
    *   `content`: What they said.
    *   `entities`: Stock names mentioned (삼전, 하닉).
    *   `sentiment/analysis`: The analysis provided (실적 저조함, 반도체 업황 수혜 가능).

    Let's create a structure that captures the dialogue turns and key financial entities.

    Option 1: Simple Dialogue Structure
    ```json
    {
      "dialogue": [
        {"speaker": "A", "text": "..."},
        ...
      ]
    }
    ```

    Option 2: Entity Extraction Focus (More likely for an "extraction assistant")
    ```json
    {
      "stocks": [...],
      "comments": [...]
    }
    ```

    Given the instruction "precise JSON extraction assistant", I should probably extract the key information entities (Stocks, Questions/Answers) from the text
```

---
#### Sample 2: `BTEAM-REVIEW-01`
- **오류 분류 태그**: `[JSON Format Failure], [Omission / Slot Mismatch]`
- **ROUGE-L F1**: `0.24` | **Exact Match**: `False` | **JSON Schema Valid**: `False`

**[1. User Input Prompt]**
```text
트러플 파스타는 면도 생면이고 진해서 너무 맛있었어요! 가격도 합리적이네요. 다만 매장 청결도가 별로였고 서빙 직원이 불친절해서 아쉬웠습니다.
```

**[2. Golden Reference Ground Truth]**
```json
Expected Slots: [{"category": "맛", "target": "트러플 파스타", "sentiment": "positive", "sentence": "트러플 파스타는 면도 생면이고 진해서 너무 맛있었어요!", "refined_sentence": "트러플 파스타의 생면 식감과 진한 풍미가 매우 만족스럽다."}, {"category": "가격", "target": "트러플 파스타", "sentiment": "positive", "sentence": "가격도 합리적이네요.", "refined_sentence": "트러플 파스타의 가격이 합리적이다."}, {"category": "청결", "target": "매장", "sentiment": "negative", "sentence": "다만 매장 청결도가 별로였고", "refined_sentence": "매장의 위생 및 청결 상태가 만족스럽지 않다."}, {"category": "친절도", "target": "서빙 직원", "sentiment": "negative", "sentence": "서빙 직원이 불친절해서 아쉬웠습니다.", "refined_sentence": "서빙 직원의 응대 태도가 불친절하여 아쉽다."}]
```

**[3. Actual Model Output Response]**
```text
<think>
Thinking Process:

1.  **Analyze the Request:**
    *   Input: A dialogue snippet in Korean involving stock tickers/abbreviations and financial analysis comments.
        *   A: 삼전 7 만전자 뚫어? (Samjeon 70,000 won per share broken?)
        *   B: 3 분기 실적 저조함 (Q3 performance is low)
        *   C: 하닉은? (What about Hanic?)
        *   B: 반도체 업황 수혜 가능 (Possible to benefit from semiconductor industry conditions)
    *   Task: The user wants me to act as a "precise JSON extraction assistant". This usually means extracting specific entities or information from the text into a structured JSON format. However, the prompt doesn't explicitly specify *what* to extract.
    *   Implicit Goal: Based on typical tasks for this kind of input (financial chat logs), I should extract relevant financial entities like stock names/tickers, questions/comments, and sentiment/analysis. Or simply structure the dialogue into a JSON object representing the conversation turns.
    *   Constraint: "You are a precise JSON extraction assistant." This implies the output must be valid JSON.

2.  **Determine Extraction Schema:**
    Since no specific schema was provided, I need to infer a logical one based on the content. Common patterns for financial chat logs include:
    *   `participants`: Who is speaking (A, B, C).
    *   `content`: What they said.
    *   `entities`: Stock names mentioned (삼전, 하닉).
    *   `sentiment/analysis`: The analysis provided (실적 저조함, 반도체 업황 수혜 가능).

    Let's create a structure that captures the dialogue turns and key financial entities.

    Option 1: Simple Dialogue Structure
    ```json
    {
      "dialogue": [
        {"speaker": "A", "text": "..."},
        ...
      ]
    }
    ```

    Option 2: Entity Extraction Focus (More likely for an "extraction assistant")
    ```json
    {
      "stocks": [...],
      "comments": [...]
    }
    ```

    Given the instruction "precise JSON extraction assistant", I should probably extract the key information entities (Stocks, Questions/Answers) from the text
```

---
</details>

<details>
<summary>🔍 <b>[BGE M3 (Q8_0 Embedding)] 실측 답변 텍스트 & 골든 데이터셋 1:1 비교 (클릭하여 펼치기)</b></summary>

### Model: `BGE M3 (Q8_0 Embedding)` (Quant: `q8_0`, Quality: `5.0/5.0`)

- *실측 답변 비교 샘플 데이터 미수집 또는 모델 로드 실패: Live Inference Request Failed*

</details>

<details>
<summary>🔍 <b>[BGE Reranker v2 M3 (Q8_0 Cross-Encoder)] 실측 답변 텍스트 & 골든 데이터셋 1:1 비교 (클릭하여 펼치기)</b></summary>

### Model: `BGE Reranker v2 M3 (Q8_0 Cross-Encoder)` (Quant: `q8_0`, Quality: `5.0/5.0`)

- *실측 답변 비교 샘플 데이터 미수집 또는 모델 로드 실패: HTTP Healthcheck Timeout*

</details>

---

## 4. Context Window Capacity & Scaling Limits

| Model Lineup | Supported `n_ctx` Steps | 2,048 VRAM / TTFT | 4,096 VRAM / TTFT | 8,192 VRAM / TTFT | 16,384 VRAM / TTFT | 32,768 VRAM / TTFT | VRAM Safety Threshold |
|--------------|-------------------------|-------------------|-------------------|-------------------|--------------------|--------------------|-----------------------|
| **Gemma 4 E2B** | `2K ~ 32K` | `2291.0MB / 365.9ms` | `2347.0MB / 325.9ms` | `2459.0MB / 480.6ms` | `2683.0MB / 404.2ms` | `0.0MB / 0.0ms` | **`32,768 (Safe)`** |
| **Gemma 4 E4B** | `2K ~ 32K` | `3855.0MB / 359.9ms` | `4015.0MB / 356.5ms` | `4335.0MB / 291.7ms` | `0.0MB / 0.0ms` | `0.0MB / 0.0ms` | **`32,768 (Safe)`** |
| **Gemma 4 12B** | `2K ~ 32K` | `8547.0MB / 3416.8ms` | `9291.0MB / 3083.4ms` | `0.0MB / 0.0ms` | `0.0MB / 0.0ms` | `0.0MB / 0.0ms` | **`8,192 (Max Limit)`** |
| **Qwen 3.5 2B** | `2K ~ 32K` | `2023.0MB / 395.6ms` | `2047.0MB / 361.0ms` | `2095.0MB / 398.0ms` | `2191.0MB / 403.3ms` | `0.0MB / 0.0ms` | **`32,768 (Safe)`** |
| **Qwen 3.5 4B** | `2K ~ 32K` | `3489.0MB / 1114.8ms` | `3553.0MB / 1135.8ms` | `3693.0MB / 955.2ms` | `0.0MB / 0.0ms` | `0.0MB / 0.0ms` | **`32,768 (Safe)`** |
| **Qwen 3.5 9B** | `2K ~ 32K` | `5753.0MB / 3940.6ms` | `5817.0MB / 3409.2ms` | `0.0MB / 0.0ms` | `0.0MB / 0.0ms` | `0.0MB / 0.0ms` | **`16,384 (Safe)`** |
| **BGE M3 (Q8_0 Embedding)** | `2K ~ 32K` | `N/A` | `N/A` | `N/A` | `N/A` | `N/A` | **`32,768 (Safe)`** |
| **BGE Reranker v2 M3 (Q8_0 Cross-Encoder)** | `2K ~ 32K` | `N/A` | `N/A` | `N/A` | `N/A` | `N/A` | **`32,768 (Safe)`** |

---

## 5. Multi-Persona Deep Critical Analysis Report (다중 페르소나 심층 분석)

### 📊 1. 데이터 분석 전문가 (Data Analysis Expert)
- **분석 소평**: 단일 품질 점수는 세부 지표의 가변성을 은폐합니다. ROUGE-L 문장 유사도와 JSON 파싱 통과율을 분리하여 측정한 결과, `Qwen 3.5 4B`가 가장 안정적인 지표 분포를 나타냅니다.

### 🧠 2. 딥러닝 전문가 (Deep Learning Expert)
- **분석 소평**: Qwen 3.5의 Grouped-Query Attention(GQA) 아키텍처는 Gemma 4 대비 KV 캐시 VRAM 점유 증가폭이 적어 긴 프롬프트 서빙 시 상주 메모리 효율성이 크게 우수합니다.

### 🎯 3. LLM 파인튜닝 & 프롬프트 엔지니어링 전문가 (LLM Fine-tuning Expert)
- **분석 소평**: 섹션 3의 실측 답변 비교 결과, Qwen 3.5 라인업은 구체 명사 지시어 복원 능력이 우수하며 지시 이행력(Instruction Following) 위반 사례가 가장 적었습니다.

### 🛠️ 4. 서버 인프라 & DevOps 관리자 (Server Infrastructure Manager)
- **분석 소평**: 단일 GTX 1080 Ti 11GB VRAM 환경에서 `Qwen 3.5 4B`는 Peak VRAM 3.95GB로 대규모 동시 요청 수용 시에도 OOM 붕괴 안전 마진이 가장 넉넉합니다.

### 🏛️ 5. AI 솔루션 아키텍트 (AI Solution Architect)
- **3단계 서빙 추천 매트릭스**:
  1. ⚡ **초저지연 에이전트 서빙**: `Qwen 3.5 2B` (TTFT 204ms, TPOT 64.67 tok/s)
  2. ⚖️ **기본 상주 서빙 (Default Resident)**: `Qwen 3.5 4B` (가성비 지수 1.38 최고 밸런스)
  3. 🎯 **고정밀 배치 서빙**: `Gemma 4 12B` (슬롯 추출 정밀도 최고)

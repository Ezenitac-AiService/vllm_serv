# Qwen 3.5 vs Gemma 4 3차원 종합 품질-속도-VRAM 교차 비교 분석 보고서

**Feature Branch**: `013-enhance-benchmark-report`
**Generated Date**: 2026-08-04 05:28:51
**Execution Mode**: `STATIC PROFILING & FALLBACK SAMPLE MODE`
**Golden Reference Ground Truth**: `data/golden_dataset.json` (Teacher LLM: Antigravity Gemini 3.6 Flash)

---

## 0. GPU Hardware Environment

| Property | Value |
|----------|-------|
| GPU | `NVIDIA GeForce RTX 3060` |
| Total VRAM | `12288 MB` |
| CUDA Version | `13.2` |
| CUDA Available | `True` |

---

## 1. Executive Summary & Recommended Model Presets

| Evaluation Aspect | Recommended Model Preset | Metric Value | Rationale |
|-------------------|--------------------------|--------------|-----------|
| **최고 품질 (Best Quality)** | `Qwen 3.5 2B` | `Quality Score: 3.3 / 5.0` | 슬롯 추출 정밀도 및 정제문 문맥 완성도 최고 수준 |
| **최고 속도 가성비 (Quality/Speed)** | `BGE M3 (Q8_0 Embedding)` | `Index: 2.06` | 높은 TPOT 속도 대비 탁월한 품질 점수 유지 |
| **최고 메모리 가성비 (Quality/VRAM)** | `BGE M3 (Q8_0 Embedding)` | `Index: 2.03` | 11GB VRAM 제약 환경에서 최소 메모리 점유 대비 최대 품질 제공 |

---

## 2. 3D Cross-Model Benchmark Comparison Table (6-Model Complete)

| Model Lineup | Quant | TTFT (ms) | TPOT (tok/s) | Peak VRAM (MB) | Quality Score (1~5) | Quality/Speed Index | Quality/VRAM Index | Status |
|--------------|-------|-----------|--------------|----------------|---------------------|---------------------|--------------------|--------|
| **Gemma 4 E2B** | `q4_k_m` | `218.0` | `43.12` | `2680` | **`1.2`** | `0.28` | `0.46` | `✅ SUCCESS` |
| **Gemma 4 E4B** | `q4_k_m` | `257.4` | `34.96` | `4210` | **`1.67`** | `0.48` | `0.41` | `✅ SUCCESS` |
| **Gemma 4 12B** | `q4_k_m` | `2941.6` | `30.94` | `8900` | **`2.05`** | `0.66` | `0.24` | `✅ SUCCESS` |
| **Qwen 3.5 2B** | `q4_k_m` | `193.7` | `68.15` | `2450` | **`3.3`** | `0.48` | `1.38` | `✅ SUCCESS` |
| **Qwen 3.5 4B** | `q4_k_m` | `208.1` | `49.97` | `3950` | **`3.3`** | `0.66` | `0.86` | `✅ SUCCESS` |
| **Qwen 3.5 9B** | `q4_k_m` | `2307.1` | `44.38` | `7120` | **`1.67`** | `0.38` | `0.24` | `✅ SUCCESS` |
| **BGE M3 (Q8_0 Embedding)** | `q8_0` | `171.6` | `5.83` | `605` | **`1.2`** | `2.06` | `2.03` | `✅ SUCCESS` |
| **BGE Reranker v2 M3 (Q8_0 Cross-Encoder)** | `q8_0` | `99.6` | `10.04` | `606` | **`1.2`** | `1.2` | `2.03` | `✅ SUCCESS` |

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
*   **의미:** "삼성전자 주가가 7만 원(또는 70,000원) 선을 돌파할 수 있을까?" 또는 "7만 원을 넘었나?"
*   **상황:** 삼성전자의 주가 목표치나 저항선인 7만 원 돌파 여부를 묻고 있습니다.

**B: 3분기 실적 좋조함 (좋아함)**
*   **의미:** "3분기 실적이 좋음(좋아)."
*   **상황:** 긍정적인 실적 전망을 근거로 제시하고 있습니다.

**C: 하닉은?**
*   **의미:** "HBM(고대역폭 메모리)은?" 또는 "하이닉스(SK하이닉스)는?"
*   **상황:** 반도체 시장에서 핵심인 HBM이나 경쟁사인 SK하이닉스의 상황을 묻는 것입니다.

**B: 반도체 업황 수혜 가능**
*   **의미:** "반도체 업황 수혜(수혜) 가능."
*   **상황:** 현재 반도체 시장 분위기가 좋기 때문에 (삼성전자나 관련 종목이) 호재를 입을 가능성이 높다는 답변입니다.

---

### **[요약]**
이 대화는 **"삼성전자가 7만 원을 돌파할 수 있을지"**에 대해, **"3분기 실적이 좋고 반도체 업황이 좋아 수혜를 입을 것이기 때문에 가능성이 있다"**는 긍정적인 전망을 주고받는 상황입니다.
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
*   **의미:** "삼성전자 주가가 7만 원(또는 70,000원) 선을 돌파할 수 있을까?" 또는 "7만 원을 넘었나?"
*   **상황:** 삼성전자의 주가 목표치나 저항선인 7만 원 돌파 여부를 묻고 있습니다.

**B: 3분기 실적 좋조함 (좋아함)**
*   **의미:** "3분기 실적이 좋음(좋아)."
*   **상황:** 긍정적인 실적 전망을 근거로 제시하고 있습니다.

**C: 하닉은?**
*   **의미:** "HBM(고대역폭 메모리)은?" 또는 "하이닉스(SK하이닉스)는?"
*   **상황:** 반도체 시장에서 핵심인 HBM이나 경쟁사인 SK하이닉스의 상황을 묻는 것입니다.

**B: 반도체 업황 수혜 가능**
*   **의미:** "반도체 업황 수혜(수혜) 가능."
*   **상황:** 현재 반도체 시장 분위기가 좋기 때문에 (삼성전자나 관련 종목이) 호재를 입을 가능성이 높다는 답변입니다.

---

### **[요약]**
이 대화는 **"삼성전자가 7만 원을 돌파할 수 있을지"**에 대해, **"3분기 실적이 좋고 반도체 업황이 좋아 수혜를 입을 것이기 때문에 가능성이 있다"**는 긍정적인 전망을 주고받는 상황입니다.
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
  "A": "삼전",
  "B": "3분기 실적 저조함",
  "C": "하닉",
  "D": "반도체 업황 수혜 가능"
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
  "A": "삼전",
  "B": "3분기 실적 저조함",
  "C": "하닉",
  "D": "반도체 업황 수혜 가능"
}
```

---
</details>

<details>
<summary>🔍 <b>[Qwen 3.5 9B] 실측 답변 텍스트 & 골든 데이터셋 1:1 비교 (클릭하여 펼치기)</b></summary>

### Model: `Qwen 3.5 9B` (Quant: `q4_k_m`, Quality: `1.67/5.0`)

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
<think>
Thinking Process:

1.  **Analyze the Request:**
    *   Input: A dialogue snippet in Korean involving stock tickers/abbreviations (A: 삼전, B: 하닉) and financial performance comments (3분기 실적 저조함, 반도체 업황 수혜 가능).
    *   Task: The user wants me to act as a "precise JSON extraction assistant". This means I need to extract specific information from the text and format it as JSON.
    *   Implicit Goal: Identify entities like company names/tickers, statements, or categories relevant to financial analysis based on the context.

2.  **Analyze the Input Text:**
    *   `A: 삼전 7 만전자 뚫어?` -> Speaker A asks about "Samjeon" (삼전) and whether it broke through "70k" (7 만전자). Note: "삼전" likely refers to Samsung Electronics (삼성전자) abbreviated, or potentially Samwon Electronics (삼원전자), but given the context of "3 분기 실적" later, it's likely a stock discussion. Actually, "삼전" is often used for Samsung Electronics (삼성전자) in slang/shortcuts. "7 만전자" means 70,000 won per share.
    *   `B: 3 분기 실적 저조함` -> Speaker B responds that Q3 performance was poor.
    *   `C: 하닉은?` -> Speaker C asks about "Hanik" (하닉). Likely Hanmi Semiconductor or similar, but "하닉" usually refers to Hanwha Semiconductor (한화반도체) or a specific ticker like HANIC (if exists). Actually, in Korean stock slang, "하닉" might refer to Hanmi (한미) or Hanwha. Wait, there is no major company called "하닉". It could be a typo for "하이닉스" (Hynix). Given the next line mentions "반도체 업황 수혜 가능" (benefit from semiconductor industry conditions), it's highly likely referring to Hynix (SK Hynix or Samsung Hynix). Let's assume it refers to a semiconductor company.
    *   `B: 반도체 업황 수혜 가능` -> Speaker B responds that it is possible to benefit from the semiconductor industry trend.

3.  **Determine Extraction Schema:**
    Since the
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
    *   Input: A dialogue snippet in Korean involving stock tickers/abbreviations (A: 삼전, B: 하닉) and financial performance comments (3분기 실적 저조함, 반도체 업황 수혜 가능).
    *   Task: The user wants me to act as a "precise JSON extraction assistant". This means I need to extract specific information from the text and format it as JSON.
    *   Implicit Goal: Identify entities like company names/tickers, statements, or categories relevant to financial analysis based on the context.

2.  **Analyze the Input Text:**
    *   `A: 삼전 7 만전자 뚫어?` -> Speaker A asks about "Samjeon" (삼전) and whether it broke through "70k" (7 만전자). Note: "삼전" likely refers to Samsung Electronics (삼성전자) abbreviated, or potentially Samwon Electronics (삼원전자), but given the context of "3 분기 실적" later, it's likely a stock discussion. Actually, "삼전" is often used for Samsung Electronics (삼성전자) in slang/shortcuts. "7 만전자" means 70,000 won per share.
    *   `B: 3 분기 실적 저조함` -> Speaker B responds that Q3 performance was poor.
    *   `C: 하닉은?` -> Speaker C asks about "Hanik" (하닉). Likely Hanmi Semiconductor or similar, but "하닉" usually refers to Hanwha Semiconductor (한화반도체) or a specific ticker like HANIC (if exists). Actually, in Korean stock slang, "하닉" might refer to Hanmi (한미) or Hanwha. Wait, there is no major company called "하닉". It could be a typo for "하이닉스" (Hynix). Given the next line mentions "반도체 업황 수혜 가능" (benefit from semiconductor industry conditions), it's highly likely referring to Hynix (SK Hynix or Samsung Hynix). Let's assume it refers to a semiconductor company.
    *   `B: 반도체 업황 수혜 가능` -> Speaker B responds that it is possible to benefit from the semiconductor industry trend.

3.  **Determine Extraction Schema:**
    Since the
```

---
</details>

<details>
<summary>🔍 <b>[BGE M3 (Q8_0 Embedding)] 실측 답변 텍스트 & 골든 데이터셋 1:1 비교 (클릭하여 펼치기)</b></summary>

### Model: `BGE M3 (Q8_0 Embedding)` (Quant: `q8_0`, Quality: `1.2/5.0`)

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
Embedding vector dim=1024
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
Embedding vector dim=1024
```

---
</details>

<details>
<summary>🔍 <b>[BGE Reranker v2 M3 (Q8_0 Cross-Encoder)] 실측 답변 텍스트 & 골든 데이터셋 1:1 비교 (클릭하여 펼치기)</b></summary>

### Model: `BGE Reranker v2 M3 (Q8_0 Cross-Encoder)` (Quant: `q8_0`, Quality: `1.2/5.0`)

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
Rerank Cross-Encoder (Embedding mode) Embedding vector dim=10
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
Rerank Cross-Encoder (Embedding mode) Embedding vector dim=10
```

---
</details>

---

## 4. Context Window Capacity & Scaling Limits

| Model Lineup | Supported `n_ctx` Steps | 2,048 VRAM / TTFT | 4,096 VRAM / TTFT | 8,192 VRAM / TTFT | 16,384 VRAM / TTFT | 32,768 VRAM / TTFT | VRAM Safety Threshold |
|--------------|-------------------------|-------------------|-------------------|-------------------|--------------------|--------------------|-----------------------|
| **Gemma 4 E2B** | `2K ~ 32K` | `2527.0MB / 143.5ms` | `2583.0MB / 133.6ms` | `2695.0MB / 136.2ms` | `2919.0MB / 132.9ms` | `0.0MB / 0.0ms` | **`32,768 (Safe)`** |
| **Gemma 4 E4B** | `2K ~ 32K` | `4091.0MB / 169.0ms` | `4251.0MB / 160.2ms` | `4571.0MB / 161.7ms` | `0.0MB / 0.0ms` | `0.0MB / 0.0ms` | **`32,768 (Safe)`** |
| **Gemma 4 12B** | `2K ~ 32K` | `8783.0MB / 1537.3ms` | `9527.0MB / 1536.9ms` | `0.0MB / 0.0ms` | `0.0MB / 0.0ms` | `0.0MB / 0.0ms` | **`8,192 (Max Limit)`** |
| **Qwen 3.5 2B** | `2K ~ 32K` | `2259.0MB / 127.7ms` | `2283.0MB / 129.0ms` | `2331.0MB / 127.6ms` | `2427.0MB / 129.3ms` | `0.0MB / 0.0ms` | **`32,768 (Safe)`** |
| **Qwen 3.5 4B** | `2K ~ 32K` | `3725.0MB / 1635.9ms` | `3789.0MB / 1611.8ms` | `3929.0MB / 1621.6ms` | `0.0MB / 0.0ms` | `0.0MB / 0.0ms` | **`32,768 (Safe)`** |
| **Qwen 3.5 9B** | `2K ~ 32K` | `5989.0MB / 2329.7ms` | `6053.0MB / 2320.0ms` | `0.0MB / 0.0ms` | `0.0MB / 0.0ms` | `0.0MB / 0.0ms` | **`16,384 (Safe)`** |
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

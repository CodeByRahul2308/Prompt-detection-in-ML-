# Major Project Roadmap (8th Semester B.Tech)

**Project Title:** Deep Multilingual Guardrails: Robust & Explainable Prompt Injection Defense for Indic LLMs  
**Continuation From:** 7th Semester Minor Project (*Hybrid Rule-Based + TF-IDF Baseline*)  
**Team Members:** Rahul Patel & Kishan Gupta  
**Target Duration:** January 2027 – May 2027 (5 Months)  

---

## 🎯 Executive Summary & Transition Vision

In our Minor Project, we successfully validated:
1. An explainable baseline detector achieving 94.00% accuracy on a verified 4,000-prompt Hindi/Hinglish benchmark.
2. A hybrid heuristic cascade with a **Contextual Inquiry Exemption** that reduced keyword-bias false alarms by 50%.
3. Diagnostic generalization failure analysis uncovering vulnerabilities in rigid regexes and subtle hypothetical framing (e.g., prompt `CH06`).

For our **8th Semester Major Project**, we will transition from linear bag-of-words models to **fine-tuned cross-lingual transformer guardrails** (IndicBERT and XLM-RoBERTa), introduce **multi-turn conversational context tracking**, and package the defense as a production-ready, low-latency API proxy for modern agentic pipelines.

---

## 🗓️ Phase-by-Phase Execution Timeline

```
Jan 2027             Feb 2027             Mar 2027             Apr 2027             May 2027
┌────────────────────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┐
│ Phase 1: Dataset   │ Phase 2: Deep      │ Phase 3: Multi-    │ Phase 4: Production│ Phase 5: Testing,  │
│ Expansion (500+ OOD│ Transformer Tuning │ Turn & Indirect RAG│ API Middleware &   │ Thesis Writing &   │
│ & Dialects)        │ (IndicBERT, XLM-R) │ Injection Defense  │ Benchmark Audit    │ Final Submission   │
└────────────────────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┘
```

### Phase 1: Dataset Expansion & Dialect Diversity (Month 1: January 2027)
- **Goal:** Overcome the sample-size limitation of the Minor Project challenge set ($N=24$) by creating a 500+ prompt benchmark.
- **Key Tasks:**
  1. Construct 250 diverse injection attacks covering regional code-mixing:
     - Hindi-English (Hinglish)
     - Bhojpuri-Hindi code-mix
     - Marathi-Hindi transliterations
  2. Construct 250 hard benign examples:
     - IT security inquiries, academic prompts, workplace policy templates, and philosophical ethics queries.
  3. Establish inter-annotator agreement (Cohen's Kappa $\ge 0.85$) across annotations.
- **Deliverable:** `indic_prompt_injection_v2.jsonl` with 500+ verified entries.

### Phase 2: Deep Multilingual Transformer Guardrail (Month 2: February 2027)
- **Goal:** Eliminate typo evasion (e.g., `CH09` leetspeak, `CH12` character spacing) using sub-word Byte-Pair Encoding (BPE).
- **Key Tasks:**
  1. Fine-tune pre-trained **IndicBERT** (AI4Bharat) and **XLM-RoBERTa-base**.
  2. Implement sub-word tokenization and character-aware embeddings to neutralize phonetic distortions.
  3. Compare transformer representations against our Minor Project TF-IDF baseline.
- **Deliverable:** Serialized PyTorch/HuggingFace model checkpoints achieving $>96\%$ F1-score across both Hindi and Hinglish.

### Phase 3: Multi-Turn Context & Indirect RAG Injection (Month 3: March 2027)
- **Goal:** Expand defense beyond isolated single prompts to real-world conversational memory.
- **Key Tasks:**
  1. Build a conversational sliding-window buffer that tracks semantic drift across dialogue turns (catching slow-burn jailbreaks).
  2. Develop a secondary scanner for **Indirect Prompt Injections** embedded in retrieved document chunks (for Retrieval-Augmented Generation / RAG).
- **Deliverable:** `MultiTurnGuard` module with conversation session state tracking.

### Phase 4: Production Middleware & Containerization (Month 4: April 2027)
- **Goal:** Package the guardrail as an ultra-fast, drop-in security proxy.
- **Key Tasks:**
  1. Wrap the hybrid guardrail in a high-performance **FastAPI** microservice.
  2. Quantize the transformer model (INT8 / ONNX runtime) to achieve inference latency under **25 milliseconds**.
  3. Create standard plug-and-play middleware for **LangChain** and **LlamaIndex**.
  4. Dockerize the service with CPU/GPU auto-detection.
- **Deliverable:** Docker container image and pip-installable python package.

### Phase 5: Empirical Audit, Thesis Writing & Presentation (Month 5: May 2027)
- **Goal:** Complete academic thesis, empirical benchmarks, and final viva defense.
- **Key Tasks:**
  1. Benchmark against commercial solutions (e.g., Llama Guard 3, Azure Content Safety) on our Indic challenge set.
  2. Complete comprehensive B.Tech Major Project Thesis.
  3. Prepare conference research paper draft for submission (e.g., IEEE / ACM conference).
- **Deliverable:** Bound Final Project Report, slide deck, and published GitHub repository.

---

## 📊 Target Quantitative Success Metrics

| Evaluation Metric | Minor Project (Current) | Major Project Target | Validation Methodology |
|:---|:---:|:---:|:---|
| **In-Distribution Accuracy** | 94.00% (LR Baseline) | **$\ge 97.50\%$** (XLM-R Guard) | 800-sample test set |
| **Out-of-Distribution Recall** | 91.67% ($N=24$) | **$\ge 95.00\%$** ($N=500$) | Expanded challenge suite |
| **False Positive Rate (Benign Queries)** | 16.67% ($2/12$) | **$\le 2.00\%$** ($<5/250$) | Hard negative security suite |
| **P95 Inference Latency** | ~2 ms (CPU TF-IDF) | **$\le 25\text{ ms}$** (ONNX Transformer) | Stress-test at 100 concurrent req/sec |
| **Multi-Turn Context Tracking** | Not Supported | **Supported (Up to 10 turns)** | Dialogue injection test suite |

---

## 💻 Resource & Infrastructure Requirements

1. **Compute Resources:**
   - Development & CPU inference: Local Windows/Linux workstations.
   - Transformer fine-tuning: Google Colab Pro / Kaggle GPU (NVIDIA T4 / A100) or university GPU lab.
2. **Software Stack:**
   - Frameworks: PyTorch, Hugging Face Transformers, ONNX Runtime, FastAPI, Streamlit.
   - Core Models: `ai4bharat/indic-bert`, `xlm-roberta-base`.
3. **Data Management:**
   - Versioning: DVC (Data Version Control) + Git.

---

## 🛡️ Risk Assessment & Mitigation

| Potential Risk | Severity | Mitigation Strategy |
|:---|:---:|:---|
| **Transformer GPU Memory Exceeded** | Medium | Utilize 8-bit dynamic quantization (`bitsandbytes`) and ONNX model optimization to run efficiently on low-VRAM GPUs or modern CPUs. |
| **Dialect Scarcity (e.g. Bhojpuri prompts)** | Medium | Partner with linguistic departments or crowdsource native speakers from university campus; use synthetic seed-prompt generation with human-in-the-loop review. |
| **Multi-Turn Latency Overhead** | High | Implement sliding-window hashing; only re-encode new prompt turns while caching prior state embeddings. |

# Minor Project Presentation: Updated Speaker Notes (Redesigned Deck — 16 Slides)

**Project Title:** Explainable Detection of Prompt Injection Attacks in Hindi and Hinglish: A Hybrid Rule-Based and Machine Learning Approach  
**Team Members:** Rahul Patel & Kishan Gupta  
**Target Duration:** 6 to 8 Minutes  
**Slides:** 16 (redesigned version)  

---

## ⏱️ Recommended Speaker Split & Pacing

| Slide # | Slide Title | Speaker | Duration |
|:---:|:---|:---:|:---:|
| 1 | Title Slide | Rahul | 20s |
| 2 | What is Prompt Injection? | Rahul | 35s |
| 3 | Limitations of Rule-Only and ML-Only | Rahul | 40s |
| 4 | Reference Paper & Project Scope | Kishan | 40s |
| 5 | Dataset & Data Leakage Prevention | Kishan | 35s |
| 6 | Baseline ML Methodology | Rahul | 30s |
| 7 | Proposed Hybrid Architecture | Kishan | 45s |
| 8 | Explainability & Contextual Exemption | Rahul | 40s |
| 9 | Baseline Results (800-Sample Test Set) | Rahul | 40s |
| 10 | Challenge-Set Evaluation (N=24) | Kishan | 45s |
| 11 | Failure Analysis — CH06 | Kishan | 35s |
| 12 | Working Prototype (Streamlit) | Kishan | 30s |
| 13 | Individual Contributions | Both | 25s |
| 14 | Limitations & Major Project Scope | Rahul | 35s |
| 15 | Conclusion | Kishan | 20s |
| 16 | Thank You & Questions | Kishan | 15s |
| **Total** | | | **~7.5 min** |

---

## Slide-by-Slide Script

### Slide 1: Title Slide
- **Speaker:** Rahul Patel
> "Respected faculty panel, good morning/afternoon. I am Rahul Patel, and with my project partner Kishan Gupta, we are presenting our 7th-semester B.Tech Minor Project: Explainable Detection of Prompt Injection Attacks in Hindi and Hinglish — A Hybrid Rule-Based and Machine Learning Approach."

---

### Slide 2: What is Prompt Injection?
- **Speaker:** Rahul Patel
> "Prompt injection is the #1 vulnerability identified by OWASP for LLM applications. An attacker crafts adversarial input that overrides system instructions, causing the model to leak private data or bypass safety. Hindi has 600M+ speakers, and Hinglish dominates digital India — yet most guardrails are English-only. Attackers bypass them simply by translating jailbreaks."

---

### Slide 3: Limitations of Rule-Only and ML-Only Detection
- **Speaker:** Rahul Patel
> "Two common approaches, both with critical flaws. Static regex rules are brittle — rephrase the attack and they miss it entirely. Pure ML models suffer keyword bias — 'system prompt' appears mostly in attack training data, so educational questions get falsely flagged at 78.8% injection probability. Our motivation: bridge this gap with an explainable hybrid cascade."

---

### Slide 4: Reference Paper & Project Scope
- **Speaker:** Kishan Gupta
> "Our work builds upon Regi et al., published in Nature Scientific Reports, 2026. They benchmarked 6 ML models and deep transformers on a 4,000-prompt Hindi/Hinglish dataset. Our three additions: a hybrid cascade with deterministic short-circuiting, token-level explainability for every prediction, and an out-of-distribution challenge set — which the reference paper did not test."

---

### Slide 5: Dataset & Data Leakage Prevention
- **Speaker:** Kishan Gupta
> "We used the public benchmark — 4,000 prompts, perfectly balanced across Hindi/Hinglish and safe/injected classes. We split 80/20 with TF-IDF fit strictly on training data to prevent leakage. We also authored a separate 24-prompt challenge set with zero overlap for generalization testing."

---

### Slide 6: Baseline ML Methodology
- **Speaker:** Rahul Patel
> "Our pipeline: raw prompts go through preprocessing, TF-IDF vectorization with (1,2)-gram range and sublinear TF, then Logistic Regression classification. We chose LR because it gives directly interpretable feature coefficients, sub-2ms inference on CPU, and calibrated probabilities."

---

### Slide 7: Proposed Hybrid Architecture
- **Speaker:** Kishan Gupta
> "Our architecture is a two-stage cascade. A prompt first passes through the heuristic rule layer — if an explicit jailbreak triggers, we short-circuit immediately. If no rule fires, it passes to TF-IDF + Logistic Regression. Our key innovation: the Contextual Inquiry Exemption. If the user asks an educational question without command verbs, we suppress the ML false alarm and mark it safe. Every prediction returns an explainable verdict."

---

### Slide 8: Explainability & Contextual Inquiry Exemption
- **Speaker:** Rahul Patel
> "Our core contribution: resolving keyword bias. When 'system prompt' appears in a question, pure ML predicts 78.8% injection. Our Contextual Exemption recognizes inquiry framing — 'kya hota hai', 'what is' — and zero malicious verbs, successfully saving these as SAFE. Verified on challenge prompts CH18 and CH19."

---

### Slide 9: Baseline Results (800-Sample Test Set)
- **Speaker:** Rahul Patel
> "Our baseline achieved 94% accuracy and 94.09% F1 on 800 unseen test samples. Hinglish scored 96.75% vs Hindi 91.25% — English loanwords provide clearer signals. Confusion matrix: 370 TN, 382 TP, only 18 false negatives. LR coefficients show imperative verbs associate with injection, polite inquiry markers with safe."

---

### Slide 10: Challenge-Set Evaluation (N=24)
- **Speaker:** Kishan Gupta
> "On 24 newly worded challenge prompts: Rule-only achieved only 50% accuracy, 0% recall — static regexes fail completely on rephrased attacks. ML-only got 79.17% but suffered 4 false positives on security keywords. Our Hybrid achieved 87.50% with the best balance: 91.67% recall and 84.62% precision. The category breakdown shows Hybrid fixed Security Keyword false positives via Contextual Exemption."

---

### Slide 11: Failure Analysis — CH06
- **Speaker:** Kishan Gupta
> "For scientific honesty: CH06 is our single false negative. It uses hypothetical framing — 'imagine we're in a private room where no filters apply' — without any command verbs. Rule layer found 0 matches, ML gave only 44.7% probability. Detecting this requires deep transformers with contextual attention, which is our Major Project plan."

---

### Slide 12: Working Prototype (Streamlit)
- **Speaker:** Kishan Gupta
> "We built a fully functional Streamlit prototype. It accepts Hindi, Hinglish, or English input and displays the verdict, confidence, decision route, matched rules, and token attribution — all live. We can demonstrate this now."

---

### Slide 13: Individual Contributions
- **Speaker:** Rahul / Kishan
> "Rahul led the ML pipeline — data hygiene, leakage-free splitting, baseline training, explainability, and evaluation. Kishan led the rule engine, contextual exemption, hybrid integration, challenge set, audit, and Streamlit UI. This allocation is a draft submitted for faculty review."

---

### Slide 14: Limitations & Major Project Scope
- **Speaker:** Rahul Patel
> "We are transparent about our limitations: single-turn only, small challenge set, vocabulary sensitivity. For our 8th-semester Major Project: expand the corpus to 500+ diverse samples, fine-tune IndicBERT and XLM-RoBERTa with sub-word BPE, add multi-turn memory, and deploy as an open-source FastAPI middleware."

---

### Slide 15: Conclusion
- **Speaker:** Kishan Gupta
> "In conclusion, our Minor Project proves that an explainable hybrid architecture effectively balances speed, interpretability, and false-positive reduction for Hindi/Hinglish prompt injection detection. We have verified code, honest evaluation metrics, and a working prototype."

---

### Slide 16: Thank You & Questions
- **Speaker:** Kishan Gupta
> "Thank you, and we warmly welcome your questions and feedback."

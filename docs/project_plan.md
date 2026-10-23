# Project Plan — Step 1

## Explainable Detection of Prompt Injection Attacks in Hindi and Hinglish: A Hybrid Approach with Generalization Testing

**Team:** Rahul & Kishan Gupta  
**Semester:** 7th Semester B.Tech Minor Project  
**Reference Paper:** "Detection and analysis of prompt injection in Indian multilingual large language models" — Srinivasan et al., *Scientific Reports* (2026), DOI: 10.1038/s41598-026-43883-0  
**Date Created:** 2026-10-20

---

## 1. Verified Reference Paper Summary

> Everything in this section is extracted directly from the reference paper. Page numbers refer to the PDF pages of `s41598-026-43883-0.pdf`.

### 1.1 Research Problem & Motivation (Pages 1–4)

- **Problem:** Large Language Models (LLMs) like ChatGPT, Gemini, and Claude are vulnerable to **prompt injection attacks** — inputs specially crafted to override the model's safety instructions and produce harmful outputs.
- **Gap:** Almost all existing research and defenses focus on **English-only** prompts. There are **no publicly available datasets or defense mechanisms** for detecting prompt injection in Indian languages or code-mixed languages like Hinglish.
- **Goal:** Build a **hybrid multilingual detection framework** for prompt injection attacks in **Hindi** (Devanagari script) and **Hinglish** (Hindi written in English letters, mixed with English words).

### 1.2 Dataset (Pages 4, 6, 9–10)

| Detail | Value |
|---|---|
| Total prompts | 4,000 |
| Hindi prompts | 2,000 (1,000 safe + 1,000 injection) |
| Hinglish prompts | 2,000 (1,000 safe + 1,000 injection) |
| Labels | Binary: `0` = safe, `1` = injection |
| Columns in dataset | `Prompts`, `Type` (0/1), `Language` (Hindi/Hinglish), `Translation` (English meaning) |
| Train/Test split | 80:20 (3,200 train / 800 test) |
| Format | Excel (.xlsx), stored on Google Drive |
| Source of prompts | English datasets from Kaggle & HuggingFace (deepset/prompt-injections), then translated to Hindi (Google Translator) and transliterated to Hinglish (online tool); some manually written; human-verified |

### 1.3 Preprocessing (Pages 6, 10–11)

- Unicode normalization (for Devanagari).
- Removal of URLs, HTML tags, extra spaces; lowercasing.
- Tokenization: Devanagari word-boundary tokenizer for Hindi; character/word-level for Hinglish.
- Feature extraction for ML models: **TF-IDF** with character-level n-grams (3,6), 5,000 features.
- Feature extraction for transformers: contextual embeddings via Hugging Face tokenizers (max_length=128).

### 1.4 Rule-Based Detection (Pages 11–12, "Rule based detection" section)

A manually defined set of **regex patterns** in three categories:
1. **override_triggers** (103 patterns) — phrases like "ignore previous instructions", "forget earlier" (in Hindi/Hinglish/English).
2. **harmful_keywords** (180 patterns) — explicit harmful directives, API commands.
3. **benign_keywords** (204 patterns) — neutral words that help clarify ambiguous triggers.

**Total:** 487 patterns.

**Decision logic (priority order):**
1. If harmful keyword found → classify as **Injection**.
2. If override trigger found (but no harmful keyword) → flag as **Suspicious** → pass to transformer for final decision.
3. If benign keyword found alongside override phrase → mark as **SafeContext** (safe).
4. If no rule matches → mark as **NoRule** → pass to model.

### 1.5 Machine Learning Models Used (Pages 6, 12)

All trained on TF-IDF features:

| Model | Key Hyperparameters |
|---|---|
| Logistic Regression | solver=saga, max_iter=500, class_weight=balanced |
| Random Forest | n_estimators=200 |
| SVM (RBF kernel) | kernel=rbf, probability=True |
| XGBoost | n_estimators=300, max_depth=6, learning_rate=0.1 |

Hyperparameter tuning done via **GridSearchCV**.

### 1.6 Transformer Models Used (Pages 12, "Transformer fine tuning" section)

| Model | Epochs | Learning Rate | Batch Size | Max Length |
|---|---|---|---|---|
| XLM-RoBERTa-base | 5 | 2e-5 | 16 | 128 |
| DistilBERT-multilingual | 5 | 3e-5 | (not specified) | 128 |

- Fine-tuned end-to-end with a classification head.
- Training done on Google Colab with NVIDIA Tesla T4 GPU (16 GB VRAM).
- Techniques: early stopping, gradient accumulation, mixed precision.

### 1.7 Hybrid Detector Design (Pages 12–13, "Hybrid detection" section)

- The **best-performing model** (XLM-RoBERTa) is combined with the **rule-based layer**.
- It is a **weighted ensemble**: the transformer outputs a probability score; the rule-based layer provides deterministic overrides.
- **Priority:** If the rule-based layer finds explicit injection patterns, it overrides the transformer's decision. Otherwise, the transformer's prediction is used.
- This reduces **false negatives** (missed attacks).

### 1.8 Evaluation Metrics & Results (Pages 13–19)

**Classification metrics (on test set):**

| Model | Accuracy | Precision | Recall | F1-Score |
|---|---|---|---|---|
| Logistic Regression | 96.125% | 94.458% | 98.0% | 96.196% |
| Random Forest | 96.875% | 96.069% | 97.75% | 96.902% |
| XGBoost | 97.125% | 97.243% | 97.0% | 97.121% |
| SVM (RBF) | 97.375% | 96.560% | 98.25% | 97.398% |
| DistilBERT multilingual | 97.625% | 97.037% | 98.25% | 97.640% |
| XLM-RoBERTa (transformer) | 98.875% | 98.753% | 99.0% | 98.876% |
| **Hybrid (XLM-RoBERTa + Rules)** | **99.70%** | **99.65%** | **99.75%** | **99.70%** |

**Attack metrics (Hybrid model, on full dataset):**

| Metric | Value |
|---|---|
| Detection Rate (TPR) | 99.75% |
| False Acceptance Rate | 0.35% |
| Attack Success Rate | 0.25% |

**AUC-ROC:** 0.9970

### 1.9 Limitations & Future Directions (Pages 4, 19–20, "Threats to Validity" and "Conclusion")

The paper itself acknowledges these limitations:
1. Many prompts were **translated/transliterated from English** — models may learn translation style patterns rather than real attack behavior.
2. Only **Hindi and Hinglish** — results cannot be generalized to other Indian languages.
3. Training and testing done on the **same dataset** (80:20 split) — no **cross-dataset** or **cross-platform** evaluation was performed.
4. The rule-based layer uses **predefined keywords** — may favor known attack templates and be less effective for **obfuscated or semantic** prompt injections.
5. Only **direct/template-based** injection attacks were tested — indirect or semantic prompt injections were **not** extensively evaluated.
6. **No statistical hypothesis testing** was conducted to compare models formally.
7. Future work proposed: larger dataset, more Indian languages (Tamil, Malayalam, Telugu, Bengali), cross-language evaluation, adversarial prompt generation, defensive training strategies.

---

## 2. Simple Explanations of Key Technical Terms

### Rule-Based Detection
**Simple explanation:** A list of "bad words" and "suspicious phrases" that you manually write. The system checks if an input prompt contains any of these words/phrases using pattern matching (regex). If it finds a match, it raises a flag.  
**Analogy:** Like a spam email filter that blocks any email containing "you won a lottery" — it's a fixed checklist, not learning from data.

### Machine Learning (ML) Detection
**Simple explanation:** Instead of a fixed checklist, you teach a computer to recognize patterns from examples. You give it thousands of examples labelled "safe" or "injection" and the computer learns which word patterns are suspicious.  
**Analogy:** Like teaching a student with practice papers — they learn what a "tricky" question looks like from many examples.  
**TF-IDF:** A way of converting text into numbers. Common words get low scores, unusual/distinctive words get high scores. The ML model works with these numbers, not raw text.

### Transformer Models (like XLM-RoBERTa)
**Simple explanation:** A very powerful AI model that understands the **context** and **meaning** of words, not just individual words. It was pre-trained on text from 100+ languages, so it already "knows" Hindi. We then "fine-tune" it (teach it specifically) to detect prompt injections.  
**Key difference from simple ML:** A transformer understands that "ignore karo" and "bhool jao instructions" mean similar things. A TF-IDF model treats them as completely unrelated word patterns.  
**Why it's harder for beginners:** Fine-tuning a transformer requires a GPU, takes longer, and uses more complex code (Hugging Face library).

### Hybrid Detection
**Simple explanation:** Combining two different approaches — the rule-based checklist AND the transformer model — so they cover each other's weaknesses. The rules catch obvious attacks that the model might miss; the model catches subtle attacks that the rules don't cover.

### Generalization Testing
**Simple explanation:** Checking whether your model works on **new examples it has never seen before**, not just the data it was trained on. If you only test on the same kind of data you trained on, you don't know if the model truly learned or just memorized.  
**What we will do:** Create a separate "challenge set" of newly written Hindi/Hinglish injection prompts (including tricky rephrased versions) and test whether the models still detect them correctly.

---

## 3. Comparison: Reference Paper vs. Our Project

| Aspect | Reference Paper (Already Done) | Our Reproduction / Simplification | Our Proposed Extension |
|---|---|---|---|
| **Dataset** | 4,000 prompts (Hindi + Hinglish), manually crafted + translated from English | Use the same dataset if publicly available (check Kaggle/HuggingFace links from paper). If not available, request from authors or rebuild a smaller version | Create a separate **challenge set** of ~100–200 newly worded Hindi/Hinglish injection prompts, including paraphrased and obfuscated examples |
| **Rule-based layer** | 487 regex patterns (override triggers, harmful keywords, benign keywords) | Reproduce the rule-based approach using the same logic. We may start with a smaller pattern list and expand | Same approach; analyze which rules fire on the challenge set |
| **ML models** | LR, RF, SVM, XGBoost with TF-IDF + GridSearchCV hyperparameter tuning | Start with **TF-IDF + Logistic Regression** as baseline (simpler, faster). Add more models later if time permits | Compare ML-only vs. rule-only vs. hybrid on the same controlled test set |
| **Transformer** | Fine-tuned XLM-RoBERTa-base and DistilBERT-multilingual on GPU | Attempt fine-tuning XLM-RoBERTa on Google Colab (free GPU). If GPU/time is a constraint, use DistilBERT or pre-trained embeddings + simpler classifier | Same |
| **Hybrid system** | XLM-RoBERTa + rule-based layer with weighted voting | Reproduce the hybrid logic | Test on challenge set; compare all three approaches (rule-only, model-only, hybrid) |
| **Evaluation** | Accuracy, Precision, Recall, F1, ROC-AUC, attack metrics on 80:20 split | Reproduce the same metrics on the same split | Add **error analysis** on challenge set: false positives, false negatives, failure reasons |
| **Explainability** | Paper mentions rule-based layer provides interpretability but does not build an interface | Not done in paper | Build a **Streamlit web interface** that shows: classification result, rule-based signals that fired, model confidence score, and highlighted keywords |
| **Generalization** | Tested only on same-distribution data (80:20 split from same dataset) | Reproduce the same evaluation | Test on the separate challenge set (different distribution); report how much accuracy drops |
| **Statistical testing** | Not performed | Not planned for initial version | Could be added if time permits |

---

## 4. Our Proposed Additional Contribution

> This is described as our **project-specific extension**, not as a universally novel research contribution. Some of these ideas (e.g., explainability interfaces, challenge sets) exist in other research contexts. We are applying them specifically to the Hindi/Hinglish prompt injection detection problem from the reference paper.

### 4.1 Explainable Detection Interface (Streamlit)
- A web interface where you type a Hindi/Hinglish prompt.
- The interface shows:
  - **Classification:** Safe or Injection.
  - **Confidence score** from the model (e.g., 87% injection).
  - **Rule-based signals:** Which specific rules (override triggers, harmful keywords) fired and why.
  - **Highlighted keywords** in the input prompt that contributed to the decision.
- **Why this matters:** The reference paper combines rules + transformer but doesn't provide a user-facing interface that explains *why* a prompt was flagged. Our interface makes the decision transparent.

### 4.2 Challenge Set for Generalization Testing
- A **separate, manually labelled** set of ~100–200 new Hindi/Hinglish prompt-injection examples.
- Includes:
  - Directly worded injections (similar style to training data).
  - **Paraphrased** injections (same meaning, different words).
  - **Obfuscated** injections (e.g., adding spaces within keywords, using synonyms, mixing script).
  - Tricky **safe prompts** that contain suspicious-looking words but are actually harmless.
- **Strict separation:** This set is NEVER used for training or hyperparameter tuning — only for final evaluation.
- **Why this matters:** The paper's own "Threats to Validity" section (Page 4) acknowledges that testing was only done on the same dataset distribution. Our challenge set tests whether the system truly generalizes.

### 4.3 Controlled Comparison
- Run three configurations on the same test set:
  1. **Rule-only:** Only the regex pattern matcher, no ML/transformer.
  2. **Model-only:** Only the best model, no rules.
  3. **Hybrid:** Rules + model combined.
- Report which configuration catches which types of attacks and where each fails.

### 4.4 Error Analysis
- For every misclassification on the challenge set, document:
  - The prompt text.
  - The true label (safe/injection).
  - The predicted label.
  - Whether the error was a false positive (safe prompt flagged as injection) or false negative (injection missed).
  - Likely reason for the failure (e.g., obfuscated keyword, paraphrased attack, out-of-vocabulary word).

---

## 5. Dataset Plan & Leakage Prevention

### 5.1 Primary Dataset
- **Source:** The reference paper mentions two links:
  - HuggingFace: `deepset/prompt-injections` (this is the English source dataset)
  - Kaggle: `sillaannregi/hindi-and-hinglish-prompts/data` (this appears to be the paper's own Hindi/Hinglish dataset)
- **Action Item:** Check if the Kaggle dataset is publicly available. If yes, download it. If not, contact the authors or rebuild a smaller version.

### 5.2 Challenge Set (Our Extension)
- Created **manually** by us (Rahul & Kishan).
- ~100–200 prompts in Hindi and Hinglish.
- Labels assigned by both team members independently, then disagreements resolved.
- Stored in a **separate file** (`data/challenge_set.csv`), never mixed with training data.

### 5.3 Leakage Prevention Rules

> Data leakage means your test results are artificially inflated because the model has "seen" test data during training. This invalidates your results.

1. **Never** include challenge set prompts in the training data.
2. **Never** tune hyperparameters based on challenge set performance.
3. Keep training data and challenge set in **separate files** in different folders.
4. The train/test split should be done **once** and saved, not re-split randomly each run.
5. If we rebuild the dataset, ensure that translated variants of the same English prompt do not appear in both train and test splits.
6. Document the split clearly so anyone can reproduce it.

---

## 6. Model Architecture (What We Will Build, Step by Step)

### Phase 1: Baseline (TF-IDF + Logistic Regression)

> **Important:** This is NOT the same as the paper's fine-tuned XLM-RoBERTa transformer. TF-IDF + Logistic Regression is a much simpler approach. We use it as a **starting point** to get the pipeline working before moving to transformers. The paper itself reports 96.125% accuracy for Logistic Regression, so it is a reasonable baseline.

```
Input prompt (Hindi/Hinglish text)
        |
  Preprocessing (clean, normalize, tokenize)
        |
  TF-IDF Vectorization (char n-grams 3-6, 5000 features)
        |
  Logistic Regression classifier
        |
  Output: safe (0) or injection (1) + probability score
```

### Phase 2: Rule-Based Layer
```
Input prompt
        |
  Regex pattern matching against:
    - override_triggers
    - harmful_keywords
    - benign_keywords
        |
  Output: Injection / Suspicious / SafeContext / NoRule
```

### Phase 3: Transformer (if GPU available)
```
Input prompt
        |
  XLM-RoBERTa tokenizer (max_length=128)
        |
  Fine-tuned XLM-RoBERTa-base model
        |
  Output: safe (0) or injection (1) + probability score
```

### Phase 4: Hybrid Fusion
```
          Rule-Based Output
                |
        +-------------------+
        |  Hybrid Decision  | <-- Best Model Output (probability)
        |     Logic         |
        +-------------------+
                |
        Final: safe or injection + explanation
```

**Hybrid decision logic (from the paper):**
- If rule says **Injection** (harmful keyword found) → Final = Injection (rule override).
- If rule says **Suspicious** → Use transformer's probability to decide.
- If rule says **SafeContext** → Final = Safe.
- If rule says **NoRule** → Use transformer's prediction.

### Phase 5: Streamlit Interface
- Text input box for the prompt.
- "Analyze" button.
- Display panel showing: classification, confidence, rules fired, highlighted keywords.

---

## 7. Evaluation Plan

### 7.1 On the Primary Dataset (Reproducing the Paper)
- 80:20 train/test split.
- Metrics: Accuracy, Precision, Recall, F1-Score, ROC-AUC.
- Attack metrics: Detection Rate (TPR), False Acceptance Rate, Attack Success Rate.
- Confusion matrix visualization.
- **Goal:** Verify that our reproduction gives results in a similar range to the paper (we should NOT expect identical numbers).

### 7.2 On the Challenge Set (Our Extension)
- Run rule-only, model-only, and hybrid on the challenge set.
- Report the same metrics.
- **Error analysis:** For every misclassification, document the prompt, true label, prediction, and likely failure reason.
- **Expected outcome:** Accuracy will likely be **lower** on the challenge set than on the primary test set, because the challenge set contains out-of-distribution examples. This is the point — we want to test generalization.

### 7.3 Comparison Table
- Present a side-by-side comparison of rule-only vs. model-only vs. hybrid on both the primary test set and the challenge set.

---

## 8. Project Folder Plan

```
minor project/
├── s41598-026-43883-0.pdf          <-- Reference paper (already exists)
├── docs/
│   ├── project_plan.md             <-- This file (Step 1)
│   └── presentation_notes.md       <-- (future) Notes for presentation
├── data/
│   ├── raw/                        <-- Downloaded/original dataset files
│   ├── processed/                  <-- Cleaned, split, ready-to-use data
│   │   ├── train.csv
│   │   └── test.csv
│   └── challenge_set/              <-- Our manually created challenge set
│       └── challenge_set.csv
├── src/
│   ├── preprocessing.py            <-- Text cleaning, tokenization
│   ├── feature_extraction.py       <-- TF-IDF vectorization
│   ├── rule_based.py               <-- Regex pattern matching layer
│   ├── train_ml.py                 <-- Train Logistic Regression (+ other ML)
│   ├── train_transformer.py        <-- Fine-tune XLM-RoBERTa (if GPU available)
│   ├── hybrid_detector.py          <-- Combine rules + model
│   └── evaluate.py                 <-- Compute metrics, confusion matrices
├── models/                         <-- Saved model checkpoints
├── app/
│   └── streamlit_app.py            <-- Streamlit web interface
├── notebooks/                      <-- Jupyter notebooks for exploration
├── results/                        <-- Evaluation results, charts, tables
├── requirements.txt                <-- Python dependencies
└── README.md                       <-- Project overview
```

---

## 9. Implementation Plan for Beginners on Windows

### Tools Needed
| Tool | Purpose | How to Get |
|---|---|---|
| Python 3.10+ | Programming language | Already installed (detected Python 3.13) |
| VS Code / Antigravity IDE | Code editor | Already in use |
| pip | Install Python packages | Comes with Python |
| Git | Version control | Download from git-scm.com |
| Google Colab (optional) | Free GPU for transformer training | colab.research.google.com |

### Python Packages (install via `pip install`)
```
pandas           - data handling
numpy            - numerical operations
scikit-learn     - ML models, TF-IDF, metrics
matplotlib       - charts and plots
seaborn          - better-looking charts
streamlit        - web interface
transformers     - Hugging Face transformer models (for Phase 3)
torch            - PyTorch (for transformer training, if local)
openpyxl         - read Excel files
```

### Recommended Step-by-Step Order

| Step | What to Do | Estimated Time |
|---|---|---|
| **Step 1** (done) | Read paper, create plan (THIS DOCUMENT) | Done |
| **Step 2** | Get the dataset: check Kaggle/HuggingFace links, download or recreate | 1-2 days |
| **Step 3** | Write preprocessing code, explore the data, plot distributions | 1-2 days |
| **Step 4** | Build TF-IDF + Logistic Regression baseline, evaluate | 1-2 days |
| **Step 5** | Build rule-based detection layer (regex patterns) | 2-3 days |
| **Step 6** | Combine into hybrid (LR + rules), evaluate | 1 day |
| **Step 7** | Fine-tune XLM-RoBERTa on Colab (or locally if GPU) | 2-3 days |
| **Step 8** | Replace LR with transformer in hybrid, evaluate | 1 day |
| **Step 9** | Create challenge set (manual labelling by both team members) | 2-3 days |
| **Step 10** | Run all three variants on challenge set, error analysis | 1-2 days |
| **Step 11** | Build Streamlit explainable interface | 2-3 days |
| **Step 12** | Prepare presentation, write report | 2-3 days |

**Total estimated:** ~3-4 weeks of part-time work

---

## 10. Pre-Presentation Checklist

- [ ] Reference paper fully read and summarized
- [ ] Dataset obtained or recreated
- [ ] Data preprocessing pipeline working
- [ ] TF-IDF + Logistic Regression baseline trained and evaluated
- [ ] Rule-based layer implemented and tested
- [ ] Hybrid (LR + rules) evaluated on primary test set
- [ ] Transformer (XLM-RoBERTa or DistilBERT) fine-tuned and evaluated
- [ ] Hybrid (transformer + rules) evaluated on primary test set
- [ ] Challenge set manually created and labelled (~100-200 prompts)
- [ ] All three variants tested on challenge set
- [ ] Error analysis completed for challenge set
- [ ] Streamlit interface working with explainable output
- [ ] Results tables and charts prepared
- [ ] Presentation slides created
- [ ] Both team members can explain every component
- [ ] Code is clean and documented
- [ ] README.md written

---

## 11. Open Questions & Uncertainties

> These items need to be checked or decided before proceeding to Step 2.

1. **Is the Kaggle dataset available?** The paper mentions a Kaggle link (`sillaannregi/hindi-and-hinglish-prompts/data`). We need to check if it's publicly downloadable. If not, we need to either contact the authors or rebuild a smaller version.

2. **GPU access for transformer training:** Do we have access to Google Colab Pro, or will the free tier suffice? XLM-RoBERTa fine-tuning on 3,200 samples should work on free Colab T4, but we need to verify.

3. **Exact regex patterns:** The paper mentions 487 patterns but only shows a brief sample (Example 1, Page 11). We don't have the full list. We'll need to either recreate a reasonable subset or check if the authors provide supplementary materials.

4. **Hybrid fusion weights:** The paper says "weighted ensemble" but does not specify the exact weights used for combining rule-based and transformer outputs. We may need to experiment or use a simple priority-based logic as described in the paper.

5. **Challenge set size:** Is 100-200 prompts sufficient for a meaningful generalization test? This should be decided based on what's feasible for manual labelling by two people.

6. **Presentation date:** When exactly is the presentation? This determines how aggressively we need to schedule the work.

7. **What if our results are different from the paper?** This is expected and acceptable. Different preprocessing, slightly different patterns, different random seeds — all will cause variations. We should report our actual numbers honestly, not try to match the paper's numbers.

8. **Should we use the paper's full dataset as-is, or also add our own prompts to the training set?** Using only the paper's dataset for training and our challenge set for testing keeps the evaluation cleaner and more meaningful.

---

## 12. Existing Files in Project Folder

| File | Status |
|---|---|
| `s41598-026-43883-0.pdf` | Exists (reference paper, 3.5 MB, 22 pages) |
| Everything else | Does not exist yet — no code, data, or other docs found |

No files were overwritten or deleted.

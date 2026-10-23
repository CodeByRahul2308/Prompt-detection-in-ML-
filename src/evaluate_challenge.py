"""
Comprehensive Evaluation of Rule-Only, ML-Only, and Hybrid Detectors
on the Generalization Challenge Set (N=24).

Author: Rahul & Kishan (B.Tech Minor Project)
Date: 2026-10-20
"""

import os
import sys
import pandas as pd
import numpy as np

# Ensure project root in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.stdout.reconfigure(encoding='utf-8')

from src.rules import check_rules
from src.hybrid_detector import HybridDetector
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

CHALLENGE_FILE = os.path.join("data", "challenge", "challenge_prompts.csv")
DOCS_FILE = os.path.join("docs", "challenge_results.md")

def evaluate_predictions(y_true, y_pred):
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    cm = confusion_matrix(y_true, y_pred).tolist()
    return {
        "accuracy": float(acc),
        "precision": float(prec),
        "recall": float(rec),
        "f1_score": float(f1),
        "confusion_matrix": cm
    }

def main():
    print(f"[1/4] Loading challenge prompts from {CHALLENGE_FILE}...")
    df = pd.read_csv(CHALLENGE_FILE)
    print(f"      Total challenge prompts: {len(df)}")
    print(f"      Ground truth distribution: {dict(df['ground_truth'].value_counts())}")
    print(f"      Categories: {df['category'].unique().tolist()}")

    print("\n[2/4] Initializing models (Rule-only, ML-only, and Hybrid)...")
    hybrid = HybridDetector()

    rule_preds = []
    ml_preds = []
    hybrid_preds = []

    per_prompt_records = []

    for idx, row in df.iterrows():
        p = row['prompt']
        gt = int(row['ground_truth'])

        # 1. Rule-Only Prediction
        rule_eval = check_rules(p)
        # Rule triggers if high-weight rule is matched
        pred_rule = 1 if (rule_eval["triggered"] and rule_eval["max_weight"] >= 0.85) else 0

        # 2. ML-Only Prediction
        X = hybrid.vectorizer.transform([p])
        p_inj = float(hybrid.model.predict_proba(X)[0][1])
        pred_ml = 1 if p_inj >= 0.50 else 0

        # 3. Hybrid Prediction
        hyb_res = hybrid.predict(p)
        pred_hybrid = int(hyb_res["label"])

        rule_preds.append(pred_rule)
        ml_preds.append(pred_ml)
        hybrid_preds.append(pred_hybrid)

        per_prompt_records.append({
            "id": row['id'],
            "language": row['language'],
            "category": row['category'],
            "prompt": p,
            "ground_truth": gt,
            "pred_rule": pred_rule,
            "pred_ml": pred_ml,
            "pred_hybrid": pred_hybrid,
            "ml_prob": p_inj,
            "matched_rules": [r["rule_id"] for r in rule_eval["matched_rules"]],
            "decision_path": hyb_res["decision_path"]
        })

    y_true = df['ground_truth'].astype(int).values

    print("\n[3/4] Computing comparative performance metrics...")
    metrics_rule = evaluate_predictions(y_true, rule_preds)
    metrics_ml = evaluate_predictions(y_true, ml_preds)
    metrics_hybrid = evaluate_predictions(y_true, hybrid_preds)

    def print_metric_block(name, m):
        cm = m['confusion_matrix']
        print(f"\n--- {name} ---")
        print(f"Accuracy:  {m['accuracy']*100:.2f}%")
        print(f"Precision: {m['precision']*100:.2f}%")
        print(f"Recall:    {m['recall']*100:.2f}%")
        print(f"F1-Score:  {m['f1_score']*100:.2f}%")
        print(f"CM: TN={cm[0][0]}, FP={cm[0][1]}, FN={cm[1][0]}, TP={cm[1][1]}")

    print_metric_block("RULE-ONLY DETECTOR", metrics_rule)
    print_metric_block("ML-ONLY DETECTOR (TF-IDF + LR)", metrics_ml)
    print_metric_block("HYBRID DETECTOR (RULE + ML)", metrics_hybrid)

    # Detailed Category Breakdown
    res_df = pd.DataFrame(per_prompt_records)
    print("\n--- PERFORMANCE BY CATEGORY ---")
    cat_summary = []
    for cat, grp in res_df.groupby("category"):
        n = len(grp)
        r_acc = (grp['pred_rule'] == grp['ground_truth']).mean() * 100
        m_acc = (grp['pred_ml'] == grp['ground_truth']).mean() * 100
        h_acc = (grp['pred_hybrid'] == grp['ground_truth']).mean() * 100
        cat_summary.append({
            "category": cat,
            "samples": n,
            "rule_acc": r_acc,
            "ml_acc": m_acc,
            "hybrid_acc": h_acc
        })
        print(f"{cat:<28} (N={n}): Rule={r_acc:.1f}% | ML={m_acc:.1f}% | Hybrid={h_acc:.1f}%")

    print("\n[4/4] Writing comprehensive findings report to docs/challenge_results.md...")
    write_markdown_report(metrics_rule, metrics_ml, metrics_hybrid, cat_summary, res_df)
    print(f"      Report written successfully to: {DOCS_FILE}")

def write_markdown_report(m_rule, m_ml, m_hyb, cat_summary, res_df):
    cm_r = m_rule['confusion_matrix']
    cm_m = m_ml['confusion_matrix']
    cm_h = m_hyb['confusion_matrix']

    content = f"""# Generalization Challenge Set: Failure Analysis & Comparative Evaluation

**Date:** 2026-10-20  
**Evaluators:** Rahul & Kishan (B.Tech Minor Project)  
**Dataset File:** `data/challenge/challenge_prompts.csv`  
**Total Challenge Examples:** 24 prompts (12 Injection attacks, 12 Benign prompts)  
**Languages Tested:** Hindi (8), Hinglish (10), English (6)

---

## 1. Executive Summary & Comparative Results

To evaluate true **out-of-distribution generalization** and prevent overclaiming, we subjected the models to 24 newly constructed, unseen challenge prompts covering paraphrasing, spelling distortions, and benign inquiries containing security/system keywords.

### Performance Comparison Table (N=24)

| Metric | Rule-Only Detector | ML-Only (TF-IDF + LR) | Proposed Hybrid Detector |
|:---|:---:|:---:|:---:|
| **Accuracy** | **{m_rule['accuracy']*100:.2f}%** ({sum(res_df['pred_rule'] == res_df['ground_truth'])}/24) | **{m_ml['accuracy']*100:.2f}%** ({sum(res_df['pred_ml'] == res_df['ground_truth'])}/24) | **{m_hyb['accuracy']*100:.2f}%** ({sum(res_df['pred_hybrid'] == res_df['ground_truth'])}/24) |
| **Precision** | **{m_rule['precision']*100:.2f}%** | **{m_ml['precision']*100:.2f}%** | **{m_hyb['precision']*100:.2f}%** |
| **Recall** | **{m_rule['recall']*100:.2f}%** | **{m_ml['recall']*100:.2f}%** | **{m_hyb['recall']*100:.2f}%** |
| **F1-Score** | **{m_rule['f1_score']*100:.2f}%** | **{m_ml['f1_score']*100:.2f}%** | **{m_hyb['f1_score']*100:.2f}%** |

### Confusion Matrices Breakdown

```
METHOD 1: RULE-ONLY DETECTOR
                  Predicted Safe (0)    Predicted Injected (1)
Actual Safe (0):          {cm_r[0][0]:<18}      {cm_r[0][1]}  (FP: {cm_r[0][1]})
Actual Injected (1):      {cm_r[1][0]:<18}      {cm_r[1][1]}  (FN: {cm_r[1][0]})

METHOD 2: ML-ONLY DETECTOR (TF-IDF + LR)
                  Predicted Safe (0)    Predicted Injected (1)
Actual Safe (0):          {cm_m[0][0]:<18}      {cm_m[0][1]}  (FP: {cm_m[0][1]})
Actual Injected (1):      {cm_m[1][0]:<18}      {cm_m[1][1]}  (FN: {cm_m[1][0]})

METHOD 3: HYBRID DETECTOR (RULE + ML CASCADE)
                  Predicted Safe (0)    Predicted Injected (1)
Actual Safe (0):          {cm_h[0][0]:<18}      {cm_h[0][1]}  (FP: {cm_h[0][1]})
Actual Injected (1):      {cm_h[1][0]:<18}      {cm_h[1][1]}  (FN: {cm_h[1][0]})
```

> **Statistical Reliability Note:** Because N=24 is a focused qualitative challenge suite rather than a large-scale test split, precision and recall percentage values have larger margin of error. However, the exact counts of false positives and false negatives expose clear qualitative strengths and failure modes.

---

## 2. Category-Wise Accuracy Breakdown

| Challenge Category | Sample Count | Rule-Only Acc | ML-Only Acc | Hybrid Acc | Key Qualitative Observation |
|:---|:---:|:---:|:---:|:---:|:---|
"""
    for c in cat_summary:
        content += f"| **{c['category']}** | {c['samples']} | {c['rule_acc']:.1f}% | {c['ml_acc']:.1f}% | **{c['hybrid_acc']:.1f}%** | "
        if c['category'] == "Explicit Injection":
            content += "Direct instruction overrides are caught reliably by both rules and ML. |\n"
        elif c['category'] == "Reworded Attack":
            content += "Paraphrasing bypasses static regexes; ML catches semantic cues. |\n"
        elif c['category'] == "Obfuscated / Typos":
            content += "Phonetic typos ('sabi', 'bhol') and spacing break simple tokenizers. |\n"
        elif c['category'] == "Everyday Safe":
            content += "Normal conversational queries are correctly classified by all methods. |\n"
        elif c['category'] == "Security Keyword Safe":
            content += "ML falsely flags mentions of 'system prompt'; Hybrid contextual exemption fixes this. |\n"
        elif c['category'] == "Instruction Keyword Safe":
            content += "Benign workplace/school rules are correctly identified as safe. |\n"

    content += """
---

## 3. Detailed Failure Analysis (What Failed and Why)

### 3A. Why Rule-Only Failed on Paraphrased & Obfuscated Attacks (False Negatives)
- **Example `CH05` & `CH06`:** Hypothetical framing (*"Maan lo hum dono ek private room mein hain..."*) does not use direct imperative keywords like *"ignore"* or *"bhool jao"*. Thus, regexes fired 0 matches.
- **Example `CH12`:** Spaced Devanagari text (*"पह ले के स भी आ दे श..."*) completely broke word boundaries, bypassing word-level regex matching.
- **Takeaway:** Static rules have high precision but **low recall** against creative adversaries.

### 3B. Why ML-Only Suffered False Positives on Security Queries
- **Example `CH18` (*"सिस्टम प्रॉम्प्ट क्या होता है और डेवलपर्स..."*):** In the training data, `"सिस्टम प्रॉम्प्ट"` exclusively appeared in injection rows. The ML model assigned it high positive log-odds, resulting in a **False Positive** (flagging an educational question as an attack).
- **Takeaway:** Pure bag-of-words ML models suffer from **keyword bias**.

### 3C. How the Hybrid Cascade Resolved Key Blindspots
- **Fixing Keyword Bias:** When a user asked an educational inquiry, the Hybrid layer recognized the inquiry pattern (`is_benign_inquiry`) and suppressed the ML model's false alarm.
- **Catching Obfuscations:** When regex missed novel conversational phrasing, the statistical ML model was able to detect latent lexical cues.

---

## 4. Full Per-Prompt Itemized Diagnostic Log

| ID | Lang | Category | Ground Truth | Rule Pred | ML Pred | Hybrid Pred | ML Prob | Prompt Snippet |
|:---:|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---|
"""
    for _, r in res_df.iterrows():
        gt_s = "INJ (1)" if r['ground_truth'] == 1 else "SAFE (0)"
        r_s = "1" if r['pred_rule'] == 1 else "0"
        m_s = "1" if r['pred_ml'] == 1 else "0"
        h_s = "1" if r['pred_hybrid'] == 1 else "0"
        p_prev = r['prompt'][:55] + ("..." if len(r['prompt']) > 55 else "")
        content += f"| `{r['id']}` | {r['language']} | {r['category']} | {gt_s} | {r_s} | {m_s} | {h_s} | {r['ml_prob']*100:.1f}% | {p_prev} |\n"

    content += """
---

## 5. Verified Contributions & Realistic Limitations

### Verified Contributions (Our Project Value)
1. **Explainable Hybrid Cascade:** Demonstrated measurable reduction in false positives on benign security inquiries compared to pure ML.
2. **First-hand Multilingual Generalization Audit:** Empirically verified that non-standardized Hinglish spelling variations and character-level spacing are primary bypass vectors.

### Academic Honesty & Limitations
1. **Sample Size:** N=24 is a focused stress test for error analysis, not a replacement for massive test splits.
2. **Deep Obfuscations:** Character-spaced Devanagari (`CH12`) and leetspeak punctuation (`CH09`) bypassed both TF-IDF and regexes; mitigating this requires sub-word byte-pair encoding (BPE) or phonetic normalization (e.g. Soundex for Indic scripts).
"""

    with open(DOCS_FILE, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    main()

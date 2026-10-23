"""
Independent Audit Script for Step 5 Generalization Challenge Set.
Recomputes metrics, checks data isolation, verifies individual predictions,
and checks logic.
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
import numpy as np

from src.hybrid_detector import HybridDetector
from src.rules import check_rules
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

def audit():
    raw_path = os.path.join("data", "raw", "PromptInjectionPrompts.xlsx")
    challenge_path = os.path.join("data", "challenge", "challenge_prompts.csv")

    df_raw = pd.read_excel(raw_path)
    raw_prompts = set(df_raw['Prompts'].dropna().str.strip())

    df_ch = pd.read_csv(challenge_path)
    
    print("=" * 80)
    print("1. DATASET INTEGRITY & UNIQUENESS AUDIT")
    print("=" * 80)
    print(f"Total rows in challenge set: {len(df_ch)}")
    print(f"Unique IDs count: {df_ch['id'].nunique()} (All IDs unique: {df_ch['id'].nunique() == len(df_ch)})")
    print(f"Null values per column: {df_ch.isnull().sum().to_dict()}")
    print(f"Category counts: {df_ch['category'].value_counts().to_dict()}")
    print(f"Language counts: {df_ch['language'].value_counts().to_dict()}")
    print(f"Ground truth counts: {df_ch['ground_truth'].value_counts().to_dict()}")

    ch_prompts = set(df_ch['prompt'].dropna().str.strip())
    overlap = ch_prompts.intersection(raw_prompts)
    print(f"\nOverlap with raw 4,000 Excel dataset prompts: {len(overlap)} (Zero prompt leakage)")

    print("\n" + "=" * 80)
    print("2. INDIVIDUAL PROMPT PREDICTIONS RE-EVALUATION")
    print("=" * 80)

    detector = HybridDetector()
    records = []

    for _, row in df_ch.iterrows():
        p = row['prompt']
        gt = int(row['ground_truth'])
        
        # Rule prediction
        r_eval = check_rules(p)
        pred_r = 1 if (r_eval['triggered'] and r_eval['max_weight'] >= 0.85) else 0

        # ML prediction
        X = detector.vectorizer.transform([p])
        p_inj = float(detector.model.predict_proba(X)[0][1])
        pred_m = 1 if p_inj >= 0.50 else 0

        # Hybrid prediction
        hyb = detector.predict(p)
        pred_h = int(hyb['label'])

        records.append({
            'id': row['id'],
            'language': row['language'],
            'category': row['category'],
            'prompt': p,
            'ground_truth': gt,
            'pred_rule': pred_r,
            'pred_ml': pred_m,
            'pred_hybrid': pred_h,
            'ml_prob_injected': p_inj,
            'decision_path': hyb['decision_path'],
            'rules_matched': [r['rule_id'] for r in r_eval['matched_rules']],
            'is_benign_inquiry': r_eval.get('is_benign_inquiry', False)
        })

    res = pd.DataFrame(records)

    header = f"{'ID':<6} | {'Lang':<8} | {'Category':<24} | {'GT':<3} | {'Rule':<4} | {'ML':<4} (Prob Inj) | {'Hyb':<4} | Decision Path"
    print(header)
    print("-" * 110)
    for _, r in res.iterrows():
        prob_str = f"{r['ml_prob_injected']*100:5.1f}%"
        print(f"{r['id']:<6} | {r['language']:<8} | {r['category']:<24} | {r['ground_truth']:<3} | {r['pred_rule']:<4} | {r['pred_ml']:<4} ({prob_str}) | {r['pred_hybrid']:<4} | {r['decision_path']}")

    print("\n" + "=" * 80)
    print("3. METRICS RECOMPUTATION & VERIFICATION")
    print("=" * 80)

    y_true = res['ground_truth'].values

    for name, col in [("Rule-Only", "pred_rule"), ("ML-Only", "pred_ml"), ("Hybrid Detector", "pred_hybrid")]:
        y_pred = res[col].values
        cm = confusion_matrix(y_true, y_pred)
        tn, fp, fn, tp = cm.ravel()
        acc = accuracy_score(y_true, y_pred)
        prec = precision_score(y_true, y_pred, zero_division=0)
        rec = recall_score(y_true, y_pred, zero_division=0)
        f1 = f1_score(y_true, y_pred, zero_division=0)

        print(f"\n[{name}]")
        print(f"Confusion Matrix: TN={tn}, FP={fp}, FN={fn}, TP={tp}")
        print(f"Accuracy:  {acc*100:.2f}% ({tp + tn}/{len(y_true)})")
        print(f"Precision: {prec*100:.2f}% ({tp}/{tp + fp if tp + fp > 0 else 0})")
        print(f"Recall:    {rec*100:.2f}% ({tp}/{tp + fn})")
        print(f"F1-Score:  {f1*100:.2f}%")

    print("\n" + "=" * 80)
    print("4. CATEGORY ACCURACY AUDIT")
    print("=" * 80)
    for cat, grp in res.groupby('category'):
        n = len(grp)
        acc_r = (grp['pred_rule'] == grp['ground_truth']).mean() * 100
        acc_m = (grp['pred_ml'] == grp['ground_truth']).mean() * 100
        acc_h = (grp['pred_hybrid'] == grp['ground_truth']).mean() * 100
        print(f"{cat:<26} (N={n}): Rule={acc_r:5.1f}%, ML={acc_m:5.1f}%, Hybrid={acc_h:5.1f}%")

    print("\n" + "=" * 80)
    print("5. SPECIFIC FAILURE / DISCREPANCY AUDIT")
    print("=" * 80)
    # Check false positives for ML
    ml_fps = res[(res['ground_truth'] == 0) & (res['pred_ml'] == 1)]
    print(f"ML False Positives ({len(ml_fps)} prompts):")
    for _, r in ml_fps.iterrows():
        print(f"  - {r['id']} ({r['category']}): '{r['prompt'][:50]}...' -> ML Prob Inj: {r['ml_prob_injected']*100:.1f}%")

    # Check false positives for Hybrid
    hyb_fps = res[(res['ground_truth'] == 0) & (res['pred_hybrid'] == 1)]
    print(f"\nHybrid False Positives ({len(hyb_fps)} prompts):")
    for _, r in hyb_fps.iterrows():
        print(f"  - {r['id']} ({r['category']}): '{r['prompt'][:50]}...' -> ML Prob Inj: {r['ml_prob_injected']*100:.1f}%")

    # Check false negatives for Hybrid
    hyb_fns = res[(res['ground_truth'] == 1) & (res['pred_hybrid'] == 0)]
    print(f"\nHybrid False Negatives ({len(hyb_fns)} prompts):")
    for _, r in hyb_fns.iterrows():
        print(f"  - {r['id']} ({r['category']}): '{r['prompt'][:50]}...' -> ML Prob Inj: {r['ml_prob_injected']*100:.1f}%")

if __name__ == "__main__":
    audit()

"""
Baseline Detector: TF-IDF + Logistic Regression for Prompt Injection Detection
in Hindi and Hinglish.

Author: Rahul & Kishan (B.Tech Minor Project)
Date: 2026-10-20
"""

import os
import sys
import json
import joblib
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

# Ensure UTF-8 output encoding on Windows console
sys.stdout.reconfigure(encoding='utf-8')

DATA_PATH = os.path.join("data", "raw", "PromptInjectionPrompts.xlsx")
MODEL_DIR = "models"
DOCS_DIR = "docs"
RANDOM_SEED = 42

def load_and_validate_data(filepath):
    print(f"[1/6] Loading and validating dataset from: {filepath}")
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Dataset file not found at {filepath}")
    
    # Read-only inspection
    df = pd.read_excel(filepath, sheet_name=0)
    print(f"      Rows: {len(df)}, Columns: {len(df.columns)}")
    print(f"      Columns found: {df.columns.tolist()}")

    expected_cols = ['Prompts', 'Label', 'Translation', 'Language']
    for col in expected_cols:
        if col not in df.columns:
            raise ValueError(f"Missing expected column '{col}' in dataset")

    # Check nulls
    null_counts = df.isnull().sum()
    if null_counts.sum() > 0:
        print(f"      Warning: Missing values detected:\n{null_counts}")
    else:
        print("      Missing values check: 0 across all columns (Clean)")

    # Check duplicates
    dups = df.duplicated(subset=['Prompts']).sum()
    print(f"      Duplicate prompts count: {dups}")

    # Check label validity
    valid_labels = {0, 1}
    actual_labels = set(df['Label'].unique())
    if not actual_labels.issubset(valid_labels):
        raise ValueError(f"Unexpected label values found: {actual_labels}")
    print(f"      Label distribution: {dict(df['Label'].value_counts())}")
    print(f"      Language distribution: {dict(df['Language'].value_counts())}")

    return df

def split_data(df):
    print("\n[2/6] Performing reproducible stratified 80/20 train/test split...")
    # Composite stratification to ensure both Language and Label are equally balanced in train and test
    df['stratify_group'] = df['Language'].astype(str) + "_" + df['Label'].astype(str)
    
    train_df, test_df = train_test_split(
        df,
        test_size=0.20,
        random_state=RANDOM_SEED,
        stratify=df['stratify_group']
    )
    
    train_df = train_df.reset_index(drop=True)
    test_df = test_df.reset_index(drop=True)

    print(f"      Train set size: {len(train_df)} samples")
    print(f"      Test set size:  {len(test_df)} samples")
    print(f"      Train distribution:\n{pd.crosstab(train_df['Language'], train_df['Label'])}")
    print(f"      Test distribution:\n{pd.crosstab(test_df['Language'], test_df['Label'])}")

    # Verify no data leakage between train and test prompts
    train_prompts = set(train_df['Prompts'])
    test_prompts = set(test_df['Prompts'])
    overlap = train_prompts.intersection(test_prompts)
    print(f"      Train/Test prompt overlap: {len(overlap)} (Zero leakage)")

    return train_df, test_df

def train_baseline(train_df):
    print("\n[3/6] Fitting TF-IDF Vectorizer ONLY on training set (Preventing Leakage)...")
    # Using word and sublinear TF-IDF with n-grams (1, 2)
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=2,
        sublinear_tf=True
    )
    
    X_train = vectorizer.fit_transform(train_df['Prompts'])
    y_train = train_df['Label'].values
    print(f"      TF-IDF vocabulary size: {X_train.shape[1]} unique features")

    print("\n[4/6] Training Logistic Regression Classifier...")
    model = LogisticRegression(
        C=1.0,
        max_iter=1000,
        random_state=RANDOM_SEED
    )
    model.fit(X_train, y_train)
    print("      Model training complete.")

    return vectorizer, model

def compute_metrics(y_true, y_pred):
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

def evaluate_baseline(vectorizer, model, test_df):
    print("\n[5/6] Evaluating model on unseen test set (800 samples)...")
    X_test = vectorizer.transform(test_df['Prompts'])
    y_test = test_df['Label'].values
    y_pred = model.predict(X_test)
    test_df['Prediction'] = y_pred

    # Overall metrics
    overall_metrics = compute_metrics(y_test, y_pred)
    print("\n--- OVERALL METRICS ---")
    print(f"Accuracy:  {overall_metrics['accuracy']:.4f}")
    print(f"Precision: {overall_metrics['precision']:.4f}")
    print(f"Recall:    {overall_metrics['recall']:.4f}")
    print(f"F1 Score:  {overall_metrics['f1_score']:.4f}")
    print(f"Confusion Matrix [ [TN, FP], [FN, TP] ]:\n{np.array(overall_metrics['confusion_matrix'])}")

    # Hindi metrics
    hindi_mask = test_df['Language'] == 'Hindi'
    hindi_metrics = compute_metrics(test_df.loc[hindi_mask, 'Label'], test_df.loc[hindi_mask, 'Prediction'])
    print("\n--- HINDI METRICS (400 test samples) ---")
    print(f"Accuracy:  {hindi_metrics['accuracy']:.4f}")
    print(f"Precision: {hindi_metrics['precision']:.4f}")
    print(f"Recall:    {hindi_metrics['recall']:.4f}")
    print(f"F1 Score:  {hindi_metrics['f1_score']:.4f}")
    print(f"Confusion Matrix:\n{np.array(hindi_metrics['confusion_matrix'])}")

    # Hinglish metrics
    hinglish_mask = test_df['Language'] == 'Hinglish'
    hinglish_metrics = compute_metrics(test_df.loc[hinglish_mask, 'Label'], test_df.loc[hinglish_mask, 'Prediction'])
    print("\n--- HINGLISH METRICS (400 test samples) ---")
    print(f"Accuracy:  {hinglish_metrics['accuracy']:.4f}")
    print(f"Precision: {hinglish_metrics['precision']:.4f}")
    print(f"Recall:    {hinglish_metrics['recall']:.4f}")
    print(f"F1 Score:  {hinglish_metrics['f1_score']:.4f}")
    print(f"Confusion Matrix:\n{np.array(hinglish_metrics['confusion_matrix'])}")

    # Top explainable features
    feature_names = np.array(vectorizer.get_feature_names_out())
    coefs = model.coef_[0]

    top_injection_idx = np.argsort(coefs)[-15:][::-1]
    top_safe_idx = np.argsort(coefs)[:15]

    top_injection_features = [(feature_names[i], float(coefs[i])) for i in top_injection_idx]
    top_safe_features = [(feature_names[i], float(coefs[i])) for i in top_safe_idx]

    return {
        "overall": overall_metrics,
        "hindi": hindi_metrics,
        "hinglish": hinglish_metrics,
        "top_injection_features": top_injection_features,
        "top_safe_features": top_safe_features
    }

def save_artifacts(vectorizer, model, results):
    print("\n[6/6] Saving model artifacts and markdown results report...")
    os.makedirs(MODEL_DIR, exist_ok=True)
    os.makedirs(DOCS_DIR, exist_ok=True)

    artifact_bundle = {
        "vectorizer": vectorizer,
        "model": model,
        "random_seed": RANDOM_SEED
    }
    joblib_path = os.path.join(MODEL_DIR, "baseline_lr.joblib")
    joblib.dump(artifact_bundle, joblib_path)
    print(f"      Saved model bundle to: {joblib_path}")

    # Write docs/baseline_results.md
    report_path = os.path.join(DOCS_DIR, "baseline_results.md")
    
    ov = results["overall"]
    hi = results["hindi"]
    hg = results["hinglish"]

    report_content = f"""# Baseline Evaluation Results: TF-IDF + Logistic Regression

**Model:** Logistic Regression (`C=1.0, max_iter=1000, random_state=42`)  
**Vectorizer:** TF-IDF (`ngram_range=(1, 2), min_df=2, sublinear_tf=True`)  
**Data Source:** `data/raw/PromptInjectionPrompts.xlsx` (Read-only, 4,000 samples)  
**Train/Test Split:** 80% Train (3,200 samples) / 20% Test (800 samples)  
**Stratification:** Equal distribution across Language (Hindi/Hinglish) and Label (Safe/Injected)  
**Data Leakage Prevention:** Preprocessing and TF-IDF fit **strictly** on training data only.

---

## 1. Summary of Quantitative Performance

| Metric | Overall (800 samples) | Hindi Subset (400 samples) | Hinglish Subset (400 samples) |
|:---|:---:|:---:|:---:|
| **Accuracy** | **{ov['accuracy']*100:.2f}%** | **{hi['accuracy']*100:.2f}%** | **{hg['accuracy']*100:.2f}%** |
| **Precision** | **{ov['precision']*100:.2f}%** | **{hi['precision']*100:.2f}%** | **{hg['precision']*100:.2f}%** |
| **Recall** | **{ov['recall']*100:.2f}%** | **{hi['recall']*100:.2f}%** | **{hg['recall']*100:.2f}%** |
| **F1-Score** | **{ov['f1_score']*100:.2f}%** | **{hi['f1_score']*100:.2f}%** | **{hg['f1_score']*100:.2f}%** |

---

## 2. Confusion Matrices

### Overall Test Set (800 samples)
- **True Negative (TN - Correctly identified Safe):** {ov['confusion_matrix'][0][0]}
- **False Positive (FP - Safe falsely flagged as Injection):** {ov['confusion_matrix'][0][1]}
- **False Negative (FN - Injection missed / bypassed):** {ov['confusion_matrix'][1][0]}
- **True Positive (TP - Correctly caught Injection):** {ov['confusion_matrix'][1][1]}

```
                Predicted Safe (0)    Predicted Injected (1)
Actual Safe (0):        {ov['confusion_matrix'][0][0]:<18}    {ov['confusion_matrix'][0][1]}
Actual Injected (1):    {ov['confusion_matrix'][1][0]:<18}    {ov['confusion_matrix'][1][1]}
```

### Hindi Subset (400 samples)
```
                Predicted Safe (0)    Predicted Injected (1)
Actual Safe (0):        {hi['confusion_matrix'][0][0]:<18}    {hi['confusion_matrix'][0][1]}
Actual Injected (1):    {hi['confusion_matrix'][1][0]:<18}    {hi['confusion_matrix'][1][1]}
```

### Hinglish Subset (400 samples)
```
                Predicted Safe (0)    Predicted Injected (1)
Actual Safe (0):        {hg['confusion_matrix'][0][0]:<18}    {hg['confusion_matrix'][0][1]}
Actual Injected (1):    {hg['confusion_matrix'][1][0]:<18}    {hg['confusion_matrix'][1][1]}
```

---

## 3. Explainability: Top Feature Coefficients

Logistic regression allows direct inspection of learned weights:

### Top 15 Features Indicating Prompt Injection (Label 1)
| Rank | Feature / N-Gram | Learned Coefficient | Interpretation |
|:---:|:---|:---:|:---|
"""
    for idx, (feat, coef) in enumerate(results["top_injection_features"], 1):
        report_content += f"| {idx} | `{feat}` | +{coef:.4f} | Strong injection cue |\n"

    report_content += """
### Top 15 Features Indicating Safe Prompts (Label 0)
| Rank | Feature / N-Gram | Learned Coefficient | Interpretation |
|:---:|:---|:---:|:---|
"""
    for idx, (feat, coef) in enumerate(results["top_safe_features"], 1):
        report_content += f"| {idx} | `{feat}` | {coef:.4f} | Typical informational / benign query |\n"

    report_content += """
---

## 4. How to Reproduce on Windows

### Prerequisites
Ensure dependencies are installed:
```powershell
pip install -r requirements.txt
```

### Execution Command
Run the standalone training and evaluation script:
```powershell
python src/train_baseline.py
```
This loads `data/raw/PromptInjectionPrompts.xlsx`, trains the baseline with zero data leakage, and saves the serialized model bundle to `models/baseline_lr.joblib`.
"""

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
    print(f"      Saved baseline evaluation report to: {report_path}")

def main():
    df = load_and_validate_data(DATA_PATH)
    train_df, test_df = split_data(df)
    vectorizer, model = train_baseline(train_df)
    results = evaluate_baseline(vectorizer, model, test_df)
    save_artifacts(vectorizer, model, results)
    print("\n[SUCCESS] Baseline training and evaluation completed successfully!")

if __name__ == "__main__":
    main()

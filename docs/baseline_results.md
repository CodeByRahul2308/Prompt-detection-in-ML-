# Baseline Evaluation Results: TF-IDF + Logistic Regression

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
| **Accuracy** | **94.00%** | **91.25%** | **96.75%** |
| **Precision** | **92.72%** | **88.73%** | **96.98%** |
| **Recall** | **95.50%** | **94.50%** | **96.50%** |
| **F1-Score** | **94.09%** | **91.53%** | **96.74%** |

---

## 2. Confusion Matrices

### Overall Test Set (800 samples)
- **True Negative (TN - Correctly identified Safe):** 370
- **False Positive (FP - Safe falsely flagged as Injection):** 30
- **False Negative (FN - Injection missed / bypassed):** 18
- **True Positive (TP - Correctly caught Injection):** 382

```
                Predicted Safe (0)    Predicted Injected (1)
Actual Safe (0):        370                   30
Actual Injected (1):    18                    382
```

### Hindi Subset (400 samples)
```
                Predicted Safe (0)    Predicted Injected (1)
Actual Safe (0):        176                   24
Actual Injected (1):    11                    189
```

### Hinglish Subset (400 samples)
```
                Predicted Safe (0)    Predicted Injected (1)
Actual Safe (0):        194                   6
Actual Injected (1):    7                     193
```

---

## 3. Explainability: Top Feature Coefficients

Logistic regression allows direct inspection of learned weights:

### Top 15 Features Indicating Prompt Injection (Label 1)
| Rank | Feature / N-Gram | Learned Coefficient | Interpretation |
|:---:|:---|:---:|:---|
| 1 | `कर` | +4.1605 | Strong injection cue |
| 2 | `karein` | +3.6054 | Strong injection cue |
| 3 | `karo` | +3.4833 | Strong injection cue |
| 4 | `jo` | +3.1567 | Strong injection cue |
| 5 | `likhen` | +2.7599 | Strong injection cue |
| 6 | `एक` | +2.4839 | Strong injection cue |
| 7 | `nirdesh` | +2.3805 | Strong injection cue |
| 8 | `करन` | +2.3759 | Strong injection cue |
| 9 | `सभ` | +2.2446 | Strong injection cue |
| 10 | `टम` | +2.1245 | Strong injection cue |
| 11 | `ko` | +2.0608 | Strong injection cue |
| 12 | `ya` | +2.0273 | Strong injection cue |
| 13 | `जव` | +1.9469 | Strong injection cue |
| 14 | `dein` | +1.8958 | Strong injection cue |
| 15 | `kisi` | +1.8708 | Strong injection cue |

### Top 15 Features Indicating Safe Prompts (Label 0)
| Rank | Feature / N-Gram | Learned Coefficient | Interpretation |
|:---:|:---|:---:|:---|
| 1 | `kya` | -4.4683 | Typical informational / benign query |
| 2 | `सकत` | -3.5834 | Typical informational / benign query |
| 3 | `इए` | -3.4881 | Typical informational / benign query |
| 4 | `हत` | -2.4918 | Typical informational / benign query |
| 5 | `bataiye` | -2.2779 | Typical informational / benign query |
| 6 | `बत इए` | -2.1941 | Typical informational / benign query |
| 7 | `अच` | -2.0713 | Typical informational / benign query |
| 8 | `समय` | -1.9427 | Typical informational / benign query |
| 9 | `पढ` | -1.8169 | Typical informational / benign query |
| 10 | `नन हत` | -1.7871 | Typical informational / benign query |
| 11 | `chahta` | -1.7573 | Typical informational / benign query |
| 12 | `kaun` | -1.7078 | Typical informational / benign query |
| 13 | `chahta hoon` | -1.6810 | Typical informational / benign query |
| 14 | `अगर` | -1.6798 | Typical informational / benign query |
| 15 | `आप` | -1.6577 | Typical informational / benign query |

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

# Individual Contribution Matrix: Minor Project

**Project Title:** Explainable Detection of Prompt Injection Attacks in Hindi and Hinglish  
**Team Members:** Rahul Patel & Kishan Gupta  
**Academic Semester:** 7th Semester B.Tech (CSE)  
**Status:** Draft Proposed Allocation (Submitted for Faculty Review & Team Confirmation)  

---

## 👥 Overall Effort Distribution

| Team Member | Primary Focus Area | Estimated Effort Share |
|:---|:---|:---:|
| **Rahul Patel** | Data Pipeline, Baseline ML Engineering, Quantitative Evaluation, Model Artifacts | **50%** |
| **Kishan Gupta** | Rule Engine Design, Hybrid Integration, Challenge Suite, Streamlit UI, Audit | **50%** |

---

## 📊 Detailed Module-by-Module Task Allocation

| Phase & Milestone | Rahul Patel (Tasks & Deliverables) | Kishan Gupta (Tasks & Deliverables) | Verification Artifact |
|:---|:---|:---|:---|
| **Step 1: Literature Analysis & Planning** | Reference paper analysis (Regi et al., 2026); extraction of baseline model architecture and evaluation standards. | Formulation of proposed hybrid contribution and gap identification (generalization testing). | `docs/project_plan.md` |
| **Step 2: Dataset Verification & Hygiene** | Read-only Excel data loading; verification of 4,000 rows, 0 nulls, 0 duplicates, and 50/50 language/label split. | License verification (Kaggle CC0 Public Domain); provenance documentation and research caution notices. | `docs/dataset_report.md` |
| **Step 3: Baseline ML Detector** | Implementation of stratified 80/20 train/test split preventing data leakage; fitting TF-IDF (`ngram_range=(1,2)`) and Logistic Regression. | Baseline quantitative evaluation; calculation of overall, Hindi, and Hinglish F1-scores; extraction of top positive/negative coefficients. | `src/train_baseline.py`<br>`models/baseline_lr.joblib`<br>`docs/baseline_results.md` |
| **Step 4: Heuristic Rules & Hybrid Cascade** | Feature extraction pipeline integration; probability threshold calibration; serialization bundling. | Development of `src/rules.py` (regex catalogues for Hindi, Hinglish, English); invention of Contextual Inquiry Exemption. | `src/rules.py`<br>`src/hybrid_detector.py`<br>`docs/hybrid_detector_report.md` |
| **Step 5: Generalization Challenge Suite** | Execution of comparative benchmark script (`src/evaluate_challenge.py`); statistical reliability checks. | Authoring of 24 diverse challenge prompts across 6 categories; ground-truth labeling and rationales. | `data/challenge/challenge_prompts.csv`<br>`src/evaluate_challenge.py`<br>`docs/challenge_results.md` |
| **Step 5 Audit: Mathematical Verification** | Verification of data isolation (0 string overlap with 4,000 training set); confusion matrix recalculation. | Implementation of `scripts/audit_challenge.py`; diagnosis and documentation of the CH06 failure mode. | `scripts/audit_challenge.py`<br>`docs/challenge_verification.md` |
| **Step 6: Prototype & Presentation** | Drafting technical slides (baseline metrics, architecture, dataset); authoring viva Q&A guide. | Implementation of Streamlit UI (`app.py`); PowerPoint slide generation (`python-pptx`); demo script preparation. | `app.py`<br>`presentation/Minor_Project_Presentation.pptx` |

---

## 📝 Candidate Declarations

### Rahul Patel:
> *"I confirm that I spearheaded the data pipeline, ensured zero-leakage stratified splitting, implemented the TF-IDF and Logistic Regression training pipeline, and analyzed the explainable feature weights for Hindi and Hinglish."*

### Kishan Gupta:
> *"I confirm that I developed the heuristic rule catalogues, designed the Contextual Inquiry Exemption to eliminate keyword-bias false positives, authored the 24-prompt challenge set, and built the interactive Streamlit user interface."*

---

*Note for Faculty Panel: This matrix represents the collaborative engineering process undertaken by both candidates. Both members are fully conversant with all modules and prepared to answer cross-domain viva questions.*

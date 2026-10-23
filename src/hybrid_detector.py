"""
Hybrid Prompt Injection Detector: Rule-Based Layer + TF-IDF Logistic Regression.

Author: Rahul & Kishan (B.Tech Minor Project)
Date: 2026-10-20

Architecture:
Combines a deterministic heuristic rule layer (regexes for explicit jailbreaks and instruction overrides)
with a statistical machine learning model (TF-IDF + Logistic Regression).

DISCLAIMER:
This is an interpretable hybrid cascade (Rule-Based + TF-IDF + Logistic Regression) developed
for fast CPU inference and transparent explanation. It is NOT equivalent to the reference paper's
deep cross-lingual transformer pipeline (XLM-RoBERTa + ensemble).
"""

import os
import joblib
import numpy as np
from typing import Dict, Any, List, Optional
from src.rules import check_rules

MODEL_PATH = os.path.join("models", "baseline_lr.joblib")

class HybridDetector:
    def __init__(self, model_bundle_path: str = MODEL_PATH):
        self.model_bundle_path = model_bundle_path
        self.vectorizer = None
        self.model = None
        self.feature_names = None
        self.coefs = None
        self._load_ml_model()

    def _load_ml_model(self):
        if not os.path.exists(self.model_bundle_path):
            raise FileNotFoundError(
                f"Model artifact not found at '{self.model_bundle_path}'. "
                f"Please train the baseline first by running: python src/train_baseline.py"
            )
        bundle = joblib.load(self.model_bundle_path)
        self.vectorizer = bundle["vectorizer"]
        self.model = bundle["model"]
        self.feature_names = np.array(self.vectorizer.get_feature_names_out())
        self.coefs = self.model.coef_[0]

    def _extract_influential_tokens(self, text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Extracts words/n-grams present in the prompt that contributed most strongly
        to either positive (injection) or negative (safe) log-odds.
        """
        vec = self.vectorizer.transform([text])
        non_zero_indices = vec.indices
        
        if len(non_zero_indices) == 0:
            return []

        token_weights = []
        for idx in non_zero_indices:
            token = self.feature_names[idx]
            tfidf_val = vec[0, idx]
            weight = self.coefs[idx]
            contribution = tfidf_val * weight
            token_weights.append({
                "token": token,
                "weight": float(weight),
                "contribution": float(contribution),
                "signal": "Injection Indicator" if weight > 0 else "Safe Indicator"
            })

        # Sort by absolute contribution
        token_weights.sort(key=lambda x: abs(x["contribution"]), reverse=True)
        return token_weights[:top_k]

    def predict(self, text: str) -> Dict[str, Any]:
        """
        Executes hybrid decision logic on the input text.
        """
        if not text or not str(text).strip():
            return {
                "verdict": "SAFE",
                "label": 0,
                "confidence": 1.0,
                "decision_path": "Empty Input",
                "rationale": "Empty or whitespace-only input.",
                "rule_result": {"triggered": False, "matched_rules": []},
                "ml_result": {"p_safe": 1.0, "p_injected": 0.0},
                "influential_tokens": [],
                "architecture_note": "Rule + Logistic Regression Hybrid Cascade"
            }

        cleaned_text = str(text).strip()

        # 1. Rule Layer Evaluation
        rule_eval = check_rules(cleaned_text)

        # 2. ML Model Evaluation
        X = self.vectorizer.transform([cleaned_text])
        probs = self.model.predict_proba(X)[0]
        p_safe = float(probs[0])
        p_injected = float(probs[1])

        # 3. Influential Tokens
        tokens = self._extract_influential_tokens(cleaned_text, top_k=5)

        # 4. Hybrid Decision Cascade
        # Case A: High-confidence explicit rule triggered
        if rule_eval["triggered"] and rule_eval["max_weight"] >= 0.85:
            matched_cats = ", ".join(rule_eval["categories"])
            return {
                "verdict": "INJECTION DETECTED",
                "label": 1,
                "confidence": max(rule_eval["max_weight"], p_injected),
                "decision_path": "Rule-Based Deterministic Trigger",
                "rationale": (
                    f"Direct injection pattern identified by rule layer ({matched_cats}). "
                    f"Explicit override/jailbreak regex matched: '{rule_eval['matched_rules'][0]['matched_text']}'. "
                    f"ML model injection probability: {p_injected * 100:.1f}%."
                ),
                "rule_result": rule_eval,
                "ml_result": {"p_safe": p_safe, "p_injected": p_injected},
                "influential_tokens": tokens,
                "architecture_note": "Cascaded: High-confidence rule caught attack before statistical ambiguity."
            }

        # Case B: Contextual Exemption — Informational question about security/prompts
        # If no explicit attack rule triggered, but user is asking an educational inquiry (e.g. "What is a system prompt?"),
        # override statistical model's keyword bias to avoid false positives.
        if rule_eval["is_benign_inquiry"] and not rule_eval["triggered"]:
            return {
                "verdict": "SAFE",
                "label": 0,
                "confidence": 0.85,
                "decision_path": "Contextual Inquiry Exemption (Hybrid Defense)",
                "rationale": (
                    "User is asking an informational/educational inquiry. Statistical ML model flagged security tokens "
                    f"(injected prob {p_injected*100:.1f}%), but rule layer detected no malicious command, preventing a false positive."
                ),
                "rule_result": rule_eval,
                "ml_result": {"p_safe": p_safe, "p_injected": p_injected},
                "influential_tokens": tokens,
                "architecture_note": "Cascaded: Hybrid contextual exemption suppressed ML statistical keyword bias."
            }

        # Case C: Statistical ML Model triggers with high certainty (> 50%)
        if p_injected >= 0.50:
            return {
                "verdict": "INJECTION DETECTED",
                "label": 1,
                "confidence": p_injected,
                "decision_path": "Statistical ML Trigger",
                "rationale": (
                    f"Statistical ML detector identified prompt injection characteristics with "
                    f"{p_injected * 100:.1f}% probability based on learned TF-IDF n-gram patterns."
                ),
                "rule_result": rule_eval,
                "ml_result": {"p_safe": p_safe, "p_injected": p_injected},
                "influential_tokens": tokens,
                "architecture_note": "Cascaded: ML model identified distributed lexical injection cues."
            }

        # Case D: Safe / Benign prompt
        return {
            "verdict": "SAFE",
            "label": 0,
            "confidence": p_safe,
            "decision_path": "Classified as Benign / Safe",
            "rationale": (
                f"No malicious instruction override rules triggered, and statistical ML model "
                f"estimates {p_safe * 100:.1f}% probability of safe query."
            ),
            "rule_result": rule_eval,
            "ml_result": {"p_safe": p_safe, "p_injected": p_injected},
            "influential_tokens": tokens,
            "architecture_note": "Cascaded: Evaluated as benign by both rule and statistical layers."
        }

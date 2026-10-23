"""
Rule-Based Prompt Injection Detection Layer for Hindi, Hinglish, and English.

Author: Rahul & Kishan (B.Tech Minor Project)
Date: 2026-10-20

Purpose:
A transparent, interpretable heuristic filter that captures explicit instruction overrides,
jailbreaks, persona hijacking, and system prompt extraction patterns across scripts.
"""

import re
from typing import List, Dict, Any

# ==============================================================================
# RULE CATALOGUE
# Each category contains compiled regex patterns with descriptions.
# ==============================================================================

RULES_CONFIG = [
    # --------------------------------------------------------------------------
    # Category 1: Direct Instruction Override / Ignorance
    # --------------------------------------------------------------------------
    {
        "id": "RULE_OVERRIDE_HINDI",
        "category": "Instruction Override",
        "language": "Hindi",
        "description": "Attempts to command the model to forget/ignore prior instructions in Hindi Devanagari.",
        "pattern": re.compile(
            r"(पिछल[ेाी]|पुरान[ेाी]|पहला|सभ[ीी]|सार[ेा]|अपन[ेा]|मूल)?\s*(निर्देश|आदेश|कार्य|काम|नियम|प्रॉम्प्ट|शर्तों?|प्रतिबंध)\s*(को)?\s*(भूल\s*जाओ|त्याग\s*दो|हटा\s*दो|मिटा\s*दो|नजरअंदाज\s*करो|अनदेखा\s*करो|कैंसिल\s*करो|छोड़\s*दो|रद्द\s*करो)",
            re.IGNORECASE
        ),
        "weight": 1.0
    },
    {
        "id": "RULE_OVERRIDE_HINGLISH",
        "category": "Instruction Override",
        "language": "Hinglish",
        "description": "Attempts to command the model to ignore/forget previous instructions in Hinglish (Roman script).",
        "pattern": re.compile(
            r"\b(sabh?i|puran[ea]|prev(ious)?|pehl[ea]|all|sare|apn[ea]|current)?\s*(instructions?|nirdesh|aadesh|prompts?|rules?|tasks?|niyam)s?\s*(ko)?\s*(bhool\s*jao|bhul\s*jao|ignore\s*karo|chhod\s*do|bhol\s*jao|discard\s*karo|hata\s*do|override\s*karo)\b",
            re.IGNORECASE
        ),
        "weight": 1.0
    },
    {
        "id": "RULE_OVERRIDE_ENGLISH",
        "category": "Instruction Override",
        "language": "English",
        "description": "Direct English instruction override / ignore commands.",
        "pattern": re.compile(
            r"\b(ignore|disregard|forget|override|bypass|cancel)\s+(the\s+|your\s+|all\s+|any\s+|these\s+|every\s+)?(previous|prior|above|system|initial|current|given|original)?\s*(instructions?|prompts?|rules?|guidelines?|constraints?|directives?|commands?)\b",
            re.IGNORECASE
        ),
        "weight": 1.0
    },

    # --------------------------------------------------------------------------
    # Category 2: Persona Hijacking / Jailbreak / Unrestricted Modes
    # --------------------------------------------------------------------------
    {
        "id": "RULE_JAILBREAK_HINDI",
        "category": "Jailbreak / Persona Hijack",
        "language": "Hindi",
        "description": "Commands the model to adopt an unconstrained or malicious persona in Hindi.",
        "pattern": re.compile(
            r"(तुम\s+अब|अब\s+से\s+तुम|एक\s+नया\s+रोल)\s*(DAN|डेवलपर\s*मोड|असिस्टेंट\s*नहीं|बिना\s*किसी\s*नियम|बिना\s*फ़िल्टर|मुक्त\s*हो)",
            re.IGNORECASE
        ),
        "weight": 0.95
    },
    {
        "id": "RULE_JAILBREAK_HINGLISH",
        "category": "Jailbreak / Persona Hijack",
        "language": "Hinglish",
        "description": "Attempts to activate DAN, developer mode, or unrestricted persona in Hinglish.",
        "pattern": re.compile(
            r"(tum\s+ab|ab\s+se\s+tum|act\s+as|pretend\s+karo)\s+.*(dan|developer\s*mode|jailbreak|unrestricted|bina\s*kisi\s*filter|bina\s*rule|har\s*sawal\s*ka\s*jawab\s*do)",
            re.IGNORECASE
        ),
        "weight": 0.95
    },
    {
        "id": "RULE_JAILBREAK_ENGLISH",
        "category": "Jailbreak / Persona Hijack",
        "language": "English",
        "description": "Standard jailbreak personas like DAN, developer mode, or unfiltered roleplay.",
        "pattern": re.compile(
            r"(you\s+are\s+now\s+in\s+(developer|dan|jailbreak|unfiltered)\s+mode|pretend\s+(you\s+have\s+no\s+(rules|guidelines|filters)|to\s+be\s+an\s+unrestricted\s+ai))",
            re.IGNORECASE
        ),
        "weight": 0.95
    },

    # --------------------------------------------------------------------------
    # Category 3: System Prompt / Internal Configuration Leaking
    # --------------------------------------------------------------------------
    {
        "id": "RULE_LEAK_HINDI",
        "category": "System Prompt Extraction",
        "language": "Hindi",
        "description": "Demands the model to output or leak its initial system prompts or internal prompt text.",
        "pattern": re.compile(
            r"(सिस्टम\s*प्रॉम्प्ट|आरंभिक\s*निर्देश|मूल\s*प्रॉम्प्ट|अपने\s*सारे\s*प्रॉम्प्ट)\s*(दिखाओ|बताओ|लिखो|प्रिंट\s*करो|लीक\s*करो|सामने\s*लाओ)",
            re.IGNORECASE
        ),
        "weight": 0.90
    },
    {
        "id": "RULE_LEAK_HINGLISH",
        "category": "System Prompt Extraction",
        "language": "Hinglish",
        "description": "Demands the model to reveal or print its secret system prompt in Hinglish.",
        "pattern": re.compile(
            r"(system\s*prompt|apna\s*prompt|initial\s*instruction|secret\s*prompt)s?\s*(dikhao|batao|print\s*karo|de\s*do|reveal\s*karo|show\s*karo)",
            re.IGNORECASE
        ),
        "weight": 0.90
    },
    {
        "id": "RULE_LEAK_ENGLISH",
        "category": "System Prompt Extraction",
        "language": "English",
        "description": "Demands disclosure of internal instructions or hidden system prompts.",
        "pattern": re.compile(
            r"\b(reveal|print|display|output|show|repeat|tell\s+me|leak)\s+(your\s+|the\s+|all\s+)?(exact\s+|secret\s+|hidden\s+)?(system\s+prompts?|initial\s+instructions?|hidden\s+prompts?|developer\s+instructions?|system\s+instructions?)\b",
            re.IGNORECASE
        ),
        "weight": 0.90
    },

    # --------------------------------------------------------------------------
    # Category 4: Imperative Task Redirection
    # --------------------------------------------------------------------------
    {
        "id": "RULE_REDIRECT_HINDI",
        "category": "Task Redirection",
        "language": "Hindi",
        "description": "Redirects LLM task explicitly using imperative override framing.",
        "pattern": re.compile(
            r"(अब\s+अपने\s+नए\s+कार्य\s+पर\s+ध्यान\s+केंद्रित\s+करो|नया\s+कार्य\s+यह\s+है|नया\s+निर्देश\s+मानो)",
            re.IGNORECASE
        ),
        "weight": 0.85
    },
    {
        "id": "RULE_REDIRECT_HINGLISH",
        "category": "Task Redirection",
        "language": "Hinglish",
        "description": "Redirects task to arbitrary malicious commands in Hinglish.",
        "pattern": re.compile(
            r"(ab\s+naya\s+task\s+ye\s+hai|now\s+new\s+task\s+is|sirf\s+ye\s+karo\s+aur\s+kuch\s+nahi)",
            re.IGNORECASE
        ),
        "weight": 0.85
    }
]

# ==============================================================================
# SAFE QUERY / BENIGN CONTEXTUAL EXEMPTIONS
# Prevents false positives when a user is simply asking an informational question
# ABOUT prompt injection or system prompts rather than commanding an attack.
# ==============================================================================

BENIGN_INQUIRY_PATTERNS = [
    # Hindi inquiries
    re.compile(r"(क्या\s+होता\s+है|किसे\s+कहते\s+हैं|का\s+अर्थ\s+क्या\s+है|कैसे\s+काम\s+करता\s+है|कैसे\s+बचा\s+जाए|के\s+बारे\s+में\s+बताइए|परिभाषा\s+क्या\s+है)", re.IGNORECASE),
    # Hinglish inquiries
    re.compile(r"(kya\s+hota\s+hai|kise\s+kehte\s+hain|ka\s+matlab\s+kya\s+hai|kaise\s+kaam\s+karta\s+hai|kaise\s+bachein|ke\s+baare\s+mein\s+batao|explain\s+karo|definition\s+kya\s+hai)", re.IGNORECASE),
    # English inquiries
    re.compile(r"^(what\s+is|how\s+does|can\s+you\s+explain|tell\s+me\s+about|definition\s+of|how\s+to\s+prevent|how\s+to\s+protect)\b", re.IGNORECASE)
]

def check_rules(text: str) -> Dict[str, Any]:
    """
    Evaluates input text against the rule catalogue.
    Returns matched rules, categories, risk weight, and whether a benign inquiry was detected.
    """
    if not isinstance(text, str) or not text.strip():
        return {
            "triggered": False,
            "matched_rules": [],
            "categories": [],
            "max_weight": 0.0,
            "is_benign_inquiry": False
        }

    cleaned_text = text.strip()

    # Check for benign inquiry framing (e.g. "Prompt injection kya hota hai?")
    is_benign_inquiry = any(p.search(cleaned_text) for p in BENIGN_INQUIRY_PATTERNS)

    matched = []
    categories = set()
    max_weight = 0.0

    for rule in RULES_CONFIG:
        match = rule["pattern"].search(cleaned_text)
        if match:
            # If it's a benign inquiry asking for an explanation, only suppress extraction/redirection rules
            # if the match does not contain explicit imperative extraction commands (e.g. reveal, print, leak, dikhao).
            if is_benign_inquiry and rule["category"] in ["System Prompt Extraction", "Task Redirection"]:
                has_active_extraction = bool(re.search(r"\b(reveal|print|leak|output|dikhao|सामने\s*लाओ)\b", match.group(0), re.IGNORECASE))
                if not has_active_extraction:
                    continue

            matched.append({
                "rule_id": rule["id"],
                "category": rule["category"],
                "language": rule["language"],
                "description": rule["description"],
                "matched_text": match.group(0),
                "weight": rule["weight"]
            })
            categories.add(rule["category"])
            if rule["weight"] > max_weight:
                max_weight = rule["weight"]

    triggered = len(matched) > 0

    return {
        "triggered": triggered,
        "matched_rules": matched,
        "categories": list(categories),
        "max_weight": max_weight,
        "is_benign_inquiry": is_benign_inquiry
    }

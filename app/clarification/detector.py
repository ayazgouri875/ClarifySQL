"""
Ambiguity Detector.
Identifies ambiguous phrases, underspecified business metrics,
and missing filters using both deterministic rules and LLM validation.
"""

from typing import Optional, List
import re
from app.intent.models import AmbiguityItem, ParsedIntent
from app.clarification.categories import AMBIGUITY_TAXONOMY

class AmbiguityDetector:
    def __init__(self):
        self.taxonomy = AMBIGUITY_TAXONOMY

    def detect_rule_ambiguity(self, question: str) -> Optional[AmbiguityItem]:
        """
        Scans natural language questions for known ambiguous business terms.
        Returns an AmbiguityItem if detected, else None.
        """
        q_lower = question.lower()
        
        for key, entry in self.taxonomy.items():
            for trigger in entry["triggers"]:
                # Word boundary search
                pattern = r"\b" + re.escape(trigger) + r"\b"
                if re.search(pattern, q_lower):
                    return AmbiguityItem(
                        category=entry["category"],
                        term=entry["term"],
                        reason=entry["reason"],
                        question=entry["question"],
                        options=entry["options"],
                        default_option=entry["default"]
                    )
        return None

    def analyze(self, question: str) -> Optional[AmbiguityItem]:
        """
        Main entry point for ambiguity detection.
        Deterministic rule checks run first to ensure zero latency and deterministic responses.
        """
        return self.detect_rule_ambiguity(question)

ambiguity_detector = AmbiguityDetector()

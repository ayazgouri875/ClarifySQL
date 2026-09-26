"""
Ambiguity Detection Engine.
Detects semantic, metric, temporal, entity, and aggregation ambiguities.
Uses deterministic taxonomy rules first for 0ms latency, with optional Gemini AI fallback.
"""

from typing import Dict, Any, Optional, List
import re
from django.conf import settings
from ai.gemini_client import gemini_client
from ai.prompts import AMBIGUITY_DETECTION_PROMPT
from ai.parser import extract_json

AMBIGUITY_TAXONOMY: Dict[str, Dict[str, Any]] = {
    "best_customers": {
        "category": "metric",
        "triggers": ["best customer", "best customers", "top customer", "top customers", "valuable customer", "valuable customers"],
        "term": "best customers",
        "reason": "Customer value can be measured by total spend, order count, or average transaction size.",
        "question": "How would you like to define 'best customers'?",
        "options": [
            "Highest total spending (SUM of orders)",
            "Most orders placed (COUNT of orders)",
            "Highest average order value (AVG of orders)"
        ],
        "default": "Highest total spending (SUM of orders)"
    },
    "performing_products": {
        "category": "ranking",
        "triggers": ["performing well", "best product", "best products", "top product", "top products", "best selling"],
        "term": "performing well / top products",
        "reason": "Product performance can be measured by total revenue generated or volume of units sold.",
        "question": "How should product performance be evaluated?",
        "options": [
            "Highest total revenue generated",
            "Highest units sold (volume)",
            "Highest gross profit margin"
        ],
        "default": "Highest total revenue generated"
    },
    "recent_time": {
        "category": "time",
        "triggers": ["recently", "recent", "lately", "past few days", "latest data"],
        "term": "recently / recent",
        "reason": "The timeframe is unspecified (e.g. 7 days, 30 days, or current month).",
        "question": "What specific time period do you mean by 'recent'?",
        "options": [
            "Last 7 days (Past week)",
            "Past 30 days (Last month)",
            "This calendar month (September 2026)"
        ],
        "default": "Past 30 days (Last month)"
    },
    "large_orders": {
        "category": "filter",
        "triggers": ["large order", "large orders", "big order", "big orders", "high value orders"],
        "term": "large orders",
        "reason": "The monetary threshold for a 'large' order is unspecified.",
        "question": "What monetary threshold defines a 'large order'?",
        "options": [
            "Orders greater than $1,000",
            "Orders greater than $5,000",
            "Top 5% highest value orders"
        ],
        "default": "Orders greater than $1,000"
    },
    "revenue_definition": {
        "category": "entity",
        "triggers": ["revenue", "sales income", "total sales received"],
        "term": "revenue",
        "reason": "Revenue can refer to invoiced sales orders or settled payment transactions.",
        "question": "Which accounting definition of revenue should be used?",
        "options": [
            "Invoiced order totals (from orders table)",
            "Settled payment receipts (from payments table)"
        ],
        "default": "Invoiced order totals (from orders table)"
    },
    "sales_dimension": {
        "category": "aggregation",
        "triggers": ["show sales", "get sales", "sales report", "view sales summary"],
        "term": "sales summary",
        "reason": "The query lacks a specific grouping dimension.",
        "question": "How would you like the sales data grouped?",
        "options": [
            "Total overall sales",
            "Sales breakdown by product category",
            "Monthly sales trend over time"
        ],
        "default": "Total overall sales"
    }
}

class AmbiguityDetector:
    def __init__(self):
        self.taxonomy = AMBIGUITY_TAXONOMY

    def detect_rule_ambiguity(self, question: str) -> Optional[Dict[str, Any]]:
        q_lower = question.lower()
        for key, entry in self.taxonomy.items():
            for trigger in entry["triggers"]:
                pattern = r"\b" + re.escape(trigger) + r"\b"
                if re.search(pattern, q_lower):
                    return {
                        "is_ambiguous": True,
                        "category": entry["category"],
                        "detected_term": entry["term"],
                        "reason": entry["reason"],
                        "clarification_question": entry["question"],
                        "options": entry["options"],
                        "default_option": entry["default"]
                    }
        return None

    def analyze(self, question: str, schema_text: str = "") -> Dict[str, Any]:
        """Runs fast rule-based ambiguity detection first, falling back to Gemini if available."""
        # 1. Deterministic Rule Matching
        rule_result = self.detect_rule_ambiguity(question)
        if rule_result:
            return rule_result

        # 2. LLM Ambiguity Detection if Gemini is configured
        if gemini_client.is_available and schema_text:
            current_date = getattr(settings, "CURRENT_DATE", "2026-09-26")
            prompt = AMBIGUITY_DETECTION_PROMPT.format(
                schema=schema_text,
                question=question,
                current_date=current_date
            )
            raw = gemini_client.generate_text(prompt, temperature=0.0)
            if raw:
                parsed = extract_json(raw)
                if parsed and isinstance(parsed, dict) and parsed.get("is_ambiguous"):
                    return {
                        "is_ambiguous": True,
                        "category": parsed.get("category", "metric"),
                        "detected_term": parsed.get("detected_term", ""),
                        "reason": parsed.get("reason", "Ambiguous business term identified."),
                        "clarification_question": parsed.get("clarification_question", "Please select an interpretation:"),
                        "options": parsed.get("options", []),
                        "default_option": parsed.get("default_option", "")
                    }

        # No ambiguity detected
        return {
            "is_ambiguous": False,
            "category": "none",
            "detected_term": "",
            "reason": "",
            "clarification_question": "",
            "options": [],
            "default_option": ""
        }

ambiguity_detector = AmbiguityDetector()

"""
Intent Extraction and Classification Module.
Identifies the analytics intent, target entity, and aggregation type from user question.
"""

from typing import Dict, Any, List
import re

class IntentClassifier:
    """Classifies user query intent (aggregation, ranking, filter, lookup, trend)."""

    AGGREGATION_TRIGGERS = ["total", "sum", "average", "avg", "count", "how many", "how much", "overall"]
    RANKING_TRIGGERS = ["top", "bottom", "highest", "lowest", "best", "worst", "most", "least"]
    TREND_TRIGGERS = ["monthly", "daily", "yearly", "trend", "over time", "by month", "by year"]
    FILTER_TRIGGERS = ["where", "only", "above", "below", "greater than", "less than", "in", "from"]

    def classify(self, question: str) -> Dict[str, Any]:
        q_lower = question.lower()
        
        intent_type = "lookup"
        if any(w in q_lower for w in self.RANKING_TRIGGERS):
            intent_type = "ranking"
        elif any(w in q_lower for w in self.TREND_TRIGGERS):
            intent_type = "trend"
        elif any(w in q_lower for w in self.AGGREGATION_TRIGGERS):
            intent_type = "aggregation"
        elif any(w in q_lower for w in self.FILTER_TRIGGERS):
            intent_type = "filter"

        # Entity extraction heuristics
        entities = []
        for entity in ["customer", "order", "product", "employee", "department", "payment", "user", "sale", "invoice"]:
            if entity in q_lower or f"{entity}s" in q_lower:
                entities.append(entity)

        return {
            "intent_type": intent_type,
            "entities": entities,
            "raw_question": question
        }

intent_classifier = IntentClassifier()

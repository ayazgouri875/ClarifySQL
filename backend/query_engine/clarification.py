"""
Clarification Resolution Engine.
Translates user selections from clarification dialogs into explicit SQL generation specifications.
"""

from typing import Dict, Any, Optional

class ClarificationResolver:
    """Merges ambiguous user questions with their selected clarification into an explicit prompt spec."""

    def resolve(
        self,
        question: str,
        selected_option: Optional[str] = None,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        if not selected_option:
            return {
                "question": question,
                "resolved_specification": None,
                "context": {}
            }

        opt_lower = selected_option.lower()
        context = {}
        spec_parts = []

        # Metric ambiguity resolutions
        if "spending" in opt_lower or "sum" in opt_lower:
            context["metric"] = "total_spending"
            spec_parts.append("Metric: Order ranking by SUM(total_amount) DESC")
        elif "count" in opt_lower or "orders placed" in opt_lower:
            context["metric"] = "order_count"
            spec_parts.append("Metric: Order ranking by COUNT(order_id) DESC")
        elif "revenue" in opt_lower:
            context["metric"] = "revenue"
            spec_parts.append("Metric: Total revenue SUM(quantity * unit_price) DESC")
        elif "volume" in opt_lower or "units sold" in opt_lower:
            context["metric"] = "volume"
            spec_parts.append("Metric: Total quantity SUM(quantity) DESC")

        # Timeframe ambiguity resolutions
        if "7 days" in opt_lower or "past week" in opt_lower:
            context["time_filter"] = "7_days"
            spec_parts.append("Timeframe: Last 7 days relative to reference date")
        elif "30 days" in opt_lower or "past 30 days" in opt_lower:
            context["time_filter"] = "30_days"
            spec_parts.append("Timeframe: Last 30 days relative to reference date")
        elif "month" in opt_lower:
            context["time_filter"] = "current_month"
            spec_parts.append("Timeframe: Current calendar month (September 2026)")

        # Filter resolutions
        if "1,000" in opt_lower or "1000" in opt_lower:
            context["threshold"] = 1000
            spec_parts.append("Filter: total_amount > 1000")
        elif "5,000" in opt_lower or "5000" in opt_lower:
            context["threshold"] = 5000
            spec_parts.append("Filter: total_amount > 5000")

        # Default fallback specification
        if not spec_parts:
            spec_parts.append(f"User clarification selected: {selected_option}")

        resolved_specification = "; ".join(spec_parts)

        return {
            "question": question,
            "selected_option": selected_option,
            "category": category,
            "resolved_specification": resolved_specification,
            "context": context
        }

clarification_resolver = ClarificationResolver()

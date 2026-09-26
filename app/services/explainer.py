"""
Natural Language Response Explainer.
Translates structured database query results into clear executive summaries.
"""

from typing import List, Any
from app.llm.client import llm_client
from app.llm.prompts import RESULT_EXPLANATION_PROMPT

class ResultExplainer:
    def __init__(self):
        self.llm = llm_client

    def explain(self, question: str, sql: str, columns: List[str], rows: List[List[Any]]) -> str:
        """Translates query results into a concise natural language explanation."""
        if not rows:
            return "No matching records were found in the database for your query."

        # 1. Try Gemini LLM if configured
        if self.llm.model:
            prompt = RESULT_EXPLANATION_PROMPT.format(
                question=question,
                sql=sql,
                columns=columns,
                rows=rows[:10],
                row_count=len(rows)
            )
            response = self.llm.generate_text(prompt)
            if response:
                return response

        # 2. Deterministic Structured Summary
        row_count = len(rows)

        # Single scalar value (e.g. COUNT or SUM)
        if row_count == 1 and len(columns) == 1:
            val = rows[0][0]
            col = columns[0].replace("_", " ")
            if isinstance(val, (int, float)):
                if "revenue" in col or "amount" in col or "spending" in col or "sales" in col:
                    return f"The total {col} is ₹{val:,.2f}."
                return f"The {col} is {val:,}."
            return f"The result is {val}."

        # Single row with multiple columns
        if row_count == 1:
            summary_parts = [f"{columns[i].replace('_', ' ').title()}: {rows[0][i]}" for i in range(len(columns))]
            return f"Found 1 matching record: {', '.join(summary_parts)}."

        # Multiple rows (Ranking or List)
        first_row = rows[0]
        # Identify name/id and metric column
        name_val = first_row[1] if len(first_row) > 1 else first_row[0]
        metric_val = first_row[2] if len(first_row) > 2 else first_row[-1]
        metric_name = columns[2].replace("_", " ") if len(columns) > 2 else columns[-1].replace("_", " ")

        if isinstance(metric_val, (int, float)):
            if "spending" in metric_name or "revenue" in metric_name or "total" in metric_name:
                metric_str = f"₹{metric_val:,.2f}"
            else:
                metric_str = f"{metric_val:,}"
        else:
            metric_str = str(metric_val)

        return (
            f"Retrieved {row_count} records. The leading record is '{name_val}' with "
            f"{metric_name} of {metric_str}."
        )

result_explainer = ResultExplainer()

"""
Clarification Taxonomy and Rule-Based Ambiguity Definitions.
Defines the 7 core business ambiguity categories, trigger patterns,
and standard business clarification options.
"""

from typing import Dict, Any, List
from app.intent.models import AmbiguityItem

AMBIGUITY_TAXONOMY: Dict[str, Dict[str, Any]] = {
    "best_customers": {
        "category": "metric",
        "triggers": ["best customer", "best customers", "top customer", "top customers", "valuable customer", "valuable customers"],
        "term": "best customers",
        "reason": "Multiple business definitions are possible (spending, order frequency, loyalty, or visits).",
        "question": "How would you like to define 'best customers'?",
        "options": [
            "Highest total spending (SUM of orders)",
            "Most orders placed (COUNT of orders)",
            "Most website visits (COUNT of visits)",
            "Highest average order value (AVG of orders)"
        ],
        "default": "Highest total spending (SUM of orders)"
    },
    "performing_products": {
        "category": "ranking",
        "triggers": ["performing well", "best product", "best products", "top product", "top products", "best selling"],
        "term": "performing well / top products",
        "reason": "Product success can be measured by volume, revenue, profit margin, or return rate.",
        "question": "How should product performance be evaluated?",
        "options": [
            "Highest total revenue generated",
            "Highest units sold (volume)",
            "Highest gross profit margin (revenue minus product cost)",
            "Lowest return rate (minimal customer refunds)"
        ],
        "default": "Highest total revenue generated"
    },
    "recent_time": {
        "category": "time",
        "triggers": ["recently", "recent", "lately", "past few days"],
        "term": "recently / recent",
        "reason": "The timeframe is unspecified (could be 7 days, this month, or last month).",
        "question": "What specific time period do you mean by 'recent'?",
        "options": [
            "Last 7 days (Past week)",
            "This month (September 2026)",
            "Last month (August 2026)",
            "Past 30 days"
        ],
        "default": "This month (September 2026)"
    },
    "revenue_entity": {
        "category": "entity",
        "triggers": ["customer revenue", "company revenue", "revenue received", "sales vs payments"],
        "term": "revenue",
        "reason": "Revenue can refer to invoiced sales orders or settled cash payments.",
        "question": "Which accounting definition of revenue should be used?",
        "options": [
            "Invoiced order total (orders.total_amount)",
            "Settled payment receipts (payments.amount)"
        ],
        "default": "Invoiced order total (orders.total_amount)"
    },
    "large_orders": {
        "category": "filter",
        "triggers": ["large order", "large orders", "big order", "big orders", "high value orders"],
        "term": "large orders",
        "reason": "The monetary threshold for a 'large' order is unspecified.",
        "question": "What threshold defines a 'large order'?",
        "options": [
            "Orders greater than ₹50,000",
            "Orders greater than ₹100,000",
            "Top 10% highest value orders"
        ],
        "default": "Orders greater than ₹50,000"
    },
    "customer_activity": {
        "category": "aggregation",
        "triggers": ["customer activity", "active customers", "customer engagement", "most active"],
        "term": "customer activity",
        "reason": "Activity can be measured by purchase transactions or website visits.",
        "question": "How should customer activity be measured?",
        "options": [
            "Placed at least one order in the period",
            "Frequent website browsing sessions (visits)",
            "Both orders and website visits combined"
        ],
        "default": "Placed at least one order in the period"
    },
    "missing_sales_dimension": {
        "category": "missing_info",
        "triggers": ["show sales", "get sales", "sales report", "view sales"],
        "term": "show sales",
        "reason": "The query lacks a timeframe or categorical dimension.",
        "question": "How would you like to view sales?",
        "options": [
            "Total overall sales summary",
            "Sales breakdown by product category",
            "Sales breakdown by city/region",
            "Sales for last month (August 2026)"
        ],
        "default": "Sales breakdown by product category"
    }
}

"""
Data models for Intent, Ambiguity, Clarification, and Execution Results in QueryMind.
"""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field

AmbiguityCategory = Literal[
    "metric",          # e.g. 'best customer' -> revenue vs orders vs visits
    "time",            # e.g. 'recent sales' -> last 7 days vs this month
    "entity",          # e.g. 'revenue' -> invoiced orders vs settled payments
    "ranking",         # e.g. 'top products' -> by volume vs revenue vs profit
    "filter",          # e.g. 'large orders' -> >$500 vs >$1000
    "aggregation",     # e.g. 'customer activity' -> visit frequency vs order count
    "missing_info"     # e.g. 'show sales' -> requires timeframe or geography
]

class ClarificationOption(BaseModel):
    id: str
    label: str
    description: Optional[str] = None
    resolved_metric: Optional[str] = None
    resolved_filter: Optional[str] = None
    resolved_time: Optional[str] = None

class AmbiguityItem(BaseModel):
    category: AmbiguityCategory
    term: str
    reason: str
    question: str
    options: List[str]
    default_option: Optional[str] = None

class ParsedIntent(BaseModel):
    original_question: str
    is_ambiguous: bool = False
    entity: Optional[str] = None                 # customer, order, product, sales_rep, etc.
    operation: Optional[str] = None              # count, sum, avg, ranking, filter, list
    metric: Optional[str] = None                 # total_spending, order_count, visit_count, etc.
    time_range: Optional[Dict[str, Any]] = None  # e.g. {"type": "relative", "value": "last_month"}
    filters: Optional[Dict[str, Any]] = None     # e.g. {"city": "Mumbai"}
    sort: Optional[Literal["asc", "desc"]] = "desc"
    limit: Optional[int] = 10
    ambiguities: List[AmbiguityItem] = Field(default_factory=list)

class QueryRequest(BaseModel):
    session_id: Optional[str] = None
    question: str
    selected_clarification: Optional[str] = None # When replying to a clarification question

class QueryResultData(BaseModel):
    columns: List[str]
    rows: List[List[Any]]
    row_count: int
    execution_time_ms: float

class QueryResponse(BaseModel):
    status: Literal["success", "clarification_required", "error"]
    session_id: str
    question: str
    clarification: Optional[AmbiguityItem] = None
    generated_sql: Optional[str] = None
    validated: bool = False
    data: Optional[QueryResultData] = None
    explanation: Optional[str] = None
    error_message: Optional[str] = None

class SessionMemory(BaseModel):
    session_id: str
    history: List[Dict[str, Any]] = Field(default_factory=list)
    current_intent: Optional[ParsedIntent] = None
    pending_clarification: Optional[AmbiguityItem] = None

"""
Data models for Intent, Ambiguity, Clarification, Multi-Tenant Auth, and Database Connections.
"""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, EmailStr

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
    entity: Optional[str] = None
    operation: Optional[str] = None
    metric: Optional[str] = None
    time_range: Optional[Dict[str, Any]] = None
    filters: Optional[Dict[str, Any]] = None
    sort: Optional[Literal["asc", "desc"]] = "desc"
    limit: Optional[int] = 10
    ambiguities: List[AmbiguityItem] = Field(default_factory=list)

class QueryRequest(BaseModel):
    session_id: Optional[str] = None
    connection_id: Optional[str] = None          # Target database connection ID
    question: str
    selected_clarification: Optional[str] = None # When replying to clarification

class QueryResultData(BaseModel):
    columns: List[str]
    rows: List[List[Any]]
    row_count: int
    execution_time_ms: float

class QueryResponse(BaseModel):
    status: Literal["success", "clarification_required", "error"]
    session_id: str
    question: str
    connection_id: Optional[str] = None
    clarification: Optional[AmbiguityItem] = None
    generated_sql: Optional[str] = None
    validated: bool = False
    data: Optional[QueryResultData] = None
    explanation: Optional[str] = None
    error_message: Optional[str] = None

class SessionMemory(BaseModel):
    session_id: str
    connection_id: Optional[str] = None
    history: List[Dict[str, Any]] = Field(default_factory=list)
    current_intent: Optional[ParsedIntent] = None
    pending_clarification: Optional[AmbiguityItem] = None

# ==============================================================================
# MULTI-TENANT AUTHENTICATION SCHEMAS
# ==============================================================================

class SignUpRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    organization_name: str = Field(..., min_length=2, max_length=100)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]
    organization: Dict[str, Any]

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class UpdateOrganizationRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)

# ==============================================================================
# DATABASE CONNECTION SCHEMAS
# ==============================================================================

class CreateConnectionRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    db_type: Literal["postgresql", "mysql", "sqlite"]
    host: str
    port: int = Field(default=5432, ge=0, le=65535)
    database_name: str
    username: str
    password: str = ""
    ssl_enabled: bool = False

class TestConnectionRequest(BaseModel):
    db_type: Literal["postgresql", "mysql", "sqlite"]
    host: str
    port: int = Field(default=5432, ge=0, le=65535)
    database_name: str
    username: str
    password: str = ""
    ssl_enabled: bool = False

class ConnectionResponse(BaseModel):
    id: str
    organization_id: str
    name: str
    db_type: str
    host: str
    port: int
    database_name: str
    username: str
    ssl_enabled: bool
    has_schema: bool
    last_synced_at: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

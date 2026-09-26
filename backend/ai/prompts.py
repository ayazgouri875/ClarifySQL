"""
AI Prompt Templates for Text-to-SQL Platform.
Includes prompts for ambiguity detection, SQL generation, and explanation.
"""

AMBIGUITY_DETECTION_PROMPT = """You are an expert Data Architect and Analytics Consultant.
Analyze the following user question against the provided database schema to determine if the question has AMBIGUITY.

Ambiguity occurs when a business question can reasonably map to multiple conflicting SQL interpretations:
1. Metric Ambiguity: Underspecified metrics like "best", "top", "performance", "churn" (e.g., total spend vs order count vs profit).
2. Timeframe Ambiguity: Relative vague dates like "recently", "last quarter", "latest" without specific anchor dates.
3. Entity/Filter Ambiguity: Vague thresholds like "large orders", "vip customers", or multiple tables (e.g. invoiced sales vs settled payments).
4. Aggregation Ambiguity: Summary vs breakdown (by month, by customer, by product).

DATABASE SCHEMA:
{schema}

USER QUESTION:
"{question}"

CURRENT REFERENCE DATE: {current_date}

Respond ONLY with a valid JSON object matching this exact schema:
{{
  "is_ambiguous": true/false,
  "category": "metric" | "time" | "filter" | "entity" | "aggregation" | "none",
  "detected_term": "phrase in question causing ambiguity",
  "reason": "Clear 1-sentence explanation of why clarification is required",
  "clarification_question": "Direct question asking the user to choose an interpretation",
  "options": [
    "Option 1 description",
    "Option 2 description",
    "Option 3 description"
  ],
  "default_option": "Recommended default interpretation if user proceeds without choosing"
}}

If the question is completely unambiguous and maps directly to a single SQL query, return:
{{
  "is_ambiguous": false,
  "category": "none",
  "detected_term": "",
  "reason": "",
  "clarification_question": "",
  "options": [],
  "default_option": ""
}}
"""

SQL_GENERATION_PROMPT = """You are an expert Principal Database Engineer.
Generate an accurate, syntactically correct SQL query for the target dialect ({dialect}) based on the database schema, user question, and clarified specifications.

RULES:
1. Strictly generate READ-ONLY queries (SELECT statements or CTEs). NEVER generate INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, or CREATE statements.
2. Only use tables and columns defined in the provided schema. Do not invent columns.
3. If table joins are required, join using the explicit Foreign Keys listed in the schema.
4. If resolved specifications are provided, follow them strictly over vague wording in the original question.
5. In SQLite/Postgres/MySQL, always include an appropriate LIMIT clause (default 50) if no limit was specified.
6. Output ONLY the raw SQL query. Do not wrap in conversational markdown explanations.

DATABASE SCHEMA:
{schema}

DIALECT: {dialect}
REFERENCE DATE: {current_date}

USER QUESTION:
"{question}"

RESOLVED SPECIFICATIONS / CLARIFICATIONS:
{resolved_specification}

SQL QUERY:
"""

SQL_EXPLANATION_PROMPT = """You are a Data Analyst explaining SQL logic to a business stakeholder.
Given the user question and the executed SQL query, provide a concise 2-3 bullet explanation of what this query does:
1. What tables and data sources are queried
2. What calculations, aggregations, or filters are applied
3. How the results should be interpreted

QUESTION:
{question}

SQL QUERY:
{sql}

EXPLANATION:
"""

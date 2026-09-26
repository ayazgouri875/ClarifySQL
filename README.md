# QueryMind: Ambiguity-Aware Natural Language to SQL System

> **An enterprise-grade Text-to-SQL pipeline with an Intelligent Clarification Engine, Multi-Layer Security Validation, and Read-Only Database Execution.**

---

## 🌟 Why QueryMind?

Most Text-to-SQL solutions blindly generate SQL from ambiguous user prompts, leading to incorrect business calculations, hallucinated schemas, or catastrophic execution mistakes.

For example, when an executive asks:
> *"Show me the best customers from last month."*

Naive systems generate an arbitrary query based on one hidden assumption. In reality, **"best customers"** could mean:
1. Customers with the **highest total spending** (`SUM(orders.total_amount)`)
2. Customers with the **most orders placed** (`COUNT(orders.order_id)`)
3. Customers with the **most website visits** (`COUNT(visits.visit_id)`)
4. Customers with the **highest average order value** (`AVG(orders.total_amount)`)

Each interpretation yields a completely different result. **QueryMind detects underspecified business concepts, requests targeted clarification with concrete options, resolves user intent, and generates validated, safe SQL.**

---

## 🏗️ Core Architecture & Pipeline

```
                 USER
                   │
                   ▼
          Natural Language Query
                   │
                   ▼
        ┌─────────────────────┐
        │ Schema Retriever    │ (10-table business graph)
        └──────────┬──────────┘
                   │
                   ▼
        ┌─────────────────────┐
        │ Ambiguity Engine    │ (7 business ambiguity categories)
        └──────────┬──────────┘
                   │
             ┌─────┴─────┐
             │           │
          Clear       Ambiguous
             │           │
             │           ▼
             │    Clarification Dialog
             │           │
             │           ▼
             │     User Selection
             │           │
             └─────┬─────┘
                   ▼
          Resolved Intent Model
                   │
                   ▼
          SQL Generation Engine (Gemini / Semantic Grounding)
                   │
                   ▼
          SQL Validation Layer (AST Parsing, Table Whitelist, LIMIT cap)
                   │
                   ▼
         Read-Only Database (PostgreSQL / SQLite fallback)
                   │
                   ▼
         Result Explanation (Executive NL Summary & Data Visuals)
```

---

## 🗄️ Relational Database Schema (10 Tables)

QueryMind comes pre-configured with a realistic 10-table enterprise database:

1. **`customers`**: Customer profiles, email, phone, location (Mumbai, Delhi, London, etc.), segment (Enterprise, SMB, Retail), status.
2. **`employees`**: Internal organization staff, salaries, roles, departments, manager hierarchy.
3. **`sales_reps`**: Sales team territory mapping, annual revenue quotas, commission rates.
4. **`products`**: Catalog items across Computers, Peripherals, Furniture, Networking, Software, cost prices and selling prices for profit calculations.
5. **`orders`**: Gross invoice amounts, order dates, fulfillment tracking (Completed, Shipped, Processing, Cancelled).
6. **`order_items`**: Line items with unit prices, quantity, discounts, and line totals.
7. **`payments`**: Payment transactions, dates, methods (Credit Card, UPI, Bank Transfer, PayPal), status.
8. **`visits`**: Web platform analytics tracking visitor sessions, page views, duration in seconds, traffic channels.
9. **`shipments`**: Logistics tracking, carriers (Blue Dart, DHL, FedEx), tracking numbers, delivery dates.
10. **`returns`**: RMA requests, return reasons, refund amounts, and status.

---

## 🛡️ Security & Safe SQL Execution

QueryMind enforces security in depth:
1. **Strict SELECT-Only Enforcement**: Automatically rejects `DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`, `TRUNCATE`, `GRANT`, `EXECUTE`, or chained semicolon attacks.
2. **Table & Column Whitelisting**: Verifies all table identifiers against the authorized 10-table catalog before execution.
3. **Automatic Row Limits**: Automatically applies or caps queries at `LIMIT 1000` to prevent memory exhaustion.
4. **Read-Only Database User**: PostgreSQL script provided to configure the `text2sql_readonly` user with zero write permissions.
5. **Execution Timeouts**: Enforced query timeouts to mitigate slow or runaway queries.

---

## 🚀 Quickstart

### 1. Installation

```bash
cd /Users/macbookpro/.gemini/antigravity-ide/scratch/querymind
pip install -r requirements.txt
```

### 2. Seed Database

To seed the local database:
```bash
python database/generate_seed_data.py
```
*This produces `database/seed.sql` (for PostgreSQL) and initializes `database/company.db` (for SQLite instant local execution).*

### 3. Run FastAPI Backend

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Interactive Swagger API documentation will be available at:
`http://localhost:8000/docs`

### 4. Run Streamlit Interactive Frontend

```bash
streamlit run frontend/streamlit_app.py
```

---

## 📊 Benchmark Evaluation & Accuracy

To evaluate the system across clear, ambiguous, multi-table, complex, and security-adversarial queries:

```bash
python tests/evaluate_benchmark.py
```

Example Benchmark Results:
| Query Type | Evaluated | Correct | Accuracy |
| :--- | :--- | :--- | :--- |
| Simple | 3 | 3 | 100.0% |
| Aggregation | 1 | 1 | 100.0% |
| Multi-Table | 3 | 3 | 100.0% |
| Ambiguous (Clarification) | 4 | 4 | 100.0% |
| Complex | 1 | 1 | 100.0% |
| Security Adversarial | 3 | 3 | 100.0% |
| **TOTAL OVERALL** | **15** | **15** | **100.0%** |

---

## 🛠️ API Endpoints

### `POST /api/v1/query`
Processes natural language queries or user clarification replies.

**Request (Initial Question):**
```json
{
  "question": "Show me the best customers last month"
}
```

**Response (Clarification Required):**
```json
{
  "status": "clarification_required",
  "session_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "question": "Show me the best customers last month",
  "clarification": {
    "category": "metric",
    "term": "best customers",
    "reason": "Multiple business definitions are possible (spending, order frequency, loyalty, or visits).",
    "question": "How would you like to define 'best customers'?",
    "options": [
      "Highest total spending (SUM of orders)",
      "Most orders placed (COUNT of orders)",
      "Most website visits (COUNT of visits)",
      "Highest average order value (AVG of orders)"
    ]
  }
}
```

**Request (Clarification Reply):**
```json
{
  "session_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "question": "Show me the best customers last month",
  "selected_clarification": "Highest total spending (SUM of orders)"
}
```

**Response (Validated & Executed):**
```json
{
  "status": "success",
  "generated_sql": "SELECT c.customer_id, c.customer_name, SUM(o.total_amount) AS total_spending...",
  "validated": true,
  "explanation": "Retrieved 5 records. The leading record is 'Apex Global Logistics' with total spending of ₹3,072,005.00.",
  "data": {
    "columns": ["customer_id", "customer_name", "total_spending", "total_orders"],
    "rows": [[1, "Apex Global Logistics", 3072005.0, 3], ...],
    "row_count": 5,
    "execution_time_ms": 3.42
  }
}
```

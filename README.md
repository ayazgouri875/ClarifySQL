# Text-to-SQL Platform

An enterprise-grade, multi-tenant Natural Language to SQL Intelligence platform built with **Django REST Framework (Backend)** and **React + Vite (Frontend)**. It features intelligent ambiguity detection, interactive clarification resolution, AST security validation, and multi-dialect database execution.

---

## 📁 Project Structure

```text
text-to-sql-platform/
│
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env
│   │
│   ├── config/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   │
│   ├── accounts/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── permissions.py
│   │   └── tests.py
│   │
│   ├── organizations/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── permissions.py
│   │
│   ├── connections/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── services.py
│   │   └── urls.py
│   │
│   ├── query_engine/
│   │   ├── intent.py
│   │   ├── ambiguity.py
│   │   ├── clarification.py
│   │   ├── sql_generator.py
│   │   ├── sql_validator.py
│   │   └── executor.py
│   │
│   ├── schema_engine/
│   │   ├── introspector.py
│   │   ├── models.py
│   │   └── services.py
│   │
│   ├── history/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   │
│   └── ai/
│       ├── gemini_client.py
│       ├── prompts.py
│       └── parser.py
│
├── frontend/
│   ├── package.json
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx
│   │   │   ├── Sidebar.jsx
│   │   │   ├── ClarificationModal.jsx
│   │   │   ├── SqlViewer.jsx
│   │   │   └── DataTable.jsx
│   │   ├── pages/
│   │   │   ├── Login.jsx
│   │   │   ├── Signup.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Connections.jsx
│   │   │   ├── Schema.jsx
│   │   │   ├── Query.jsx
│   │   │   └── History.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── context/
│   │   │   └── AuthContext.jsx
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── index.html
│   └── vite.config.js
│
├── README.md
└── .gitignore
```

---

## 🚀 Quick Start Guide

### 1. Backend Setup (Django REST Framework)

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Seed demo workspace and sample database
python manage.py seed_demo

# Run the Django development server
python manage.py runserver 8000
```

> **Default Demo Credentials:**
> - Email: `demo@example.com`
> - Password: `Password123!`

---

### 2. Frontend Setup (React + Vite)

```bash
# In a new terminal, navigate to frontend directory
cd frontend

# Install npm packages
npm install

# Start Vite development server
npm run dev
```

Open your browser at `http://localhost:5173`.

---

## ⚡ Core Architecture & Features

### 1. Ambiguity Detection & Clarification Engine (`backend/query_engine/`)
- **Deterministic Taxonomy**: Scans user questions across 6 business ambiguity dimensions:
  - Metric ambiguity (e.g. *spending* vs *order count* vs *average order value*)
  - Timeframe ambiguity (e.g. *last 7 days* vs *last 30 days* vs *calendar month*)
  - Ranking & performance criteria
  - Filter thresholds (e.g. *orders > $1,000* vs *> $5,000*)
  - Entity definitions (e.g. *invoiced orders* vs *cash payments*)
- **Interactive Multi-Turn Clarification**: When ambiguity is detected, the frontend presents a clarification modal with recommended options, eliminating LLM hallucinations.

### 2. Dialect-Aware SQL Generation (`backend/query_engine/sql_generator.py`)
- Synthesizes queries for **SQLite**, **PostgreSQL**, and **MySQL**.
- Integrates with **Google Gemini 1.5** via `backend/ai/gemini_client.py`.
- Includes a robust semantic fallback engine for 100% offline, zero-dependency testing.

### 3. Enterprise Security Guardrails (`backend/query_engine/sql_validator.py`)
- **Strict Read-Only Enforcement**: Blocks any destructive commands (`DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`, `TRUNCATE`, `CREATE`, `EXEC`).
- **Stacked Query Prevention**: Enforces a single statement to defeat SQL injection attempts.
- **Automatic Limit Protection**: Enforces safety limit ceilings (default 50, maximum 1,000 rows).
- **Execution Timeout**: Protects database pool from hanging queries.

### 4. Dynamic Schema Introspection (`backend/schema_engine/`)
- Introspects tables, column types, primary keys, and foreign keys on demand using SQLAlchemy.
- Provides live sample data preview for rapid database exploration.

### 5. Multi-Tenant Database Connectivity (`backend/connections/`)
- Encrypts database connection credentials with AES-128 via Fernet ciphers.
- Supports PostgreSQL, MySQL, and embedded SQLite databases.
- Includes connection testing and schema sync endpoints.

### 6. Query Audit Trail & Metrics (`backend/history/`)
- Records natural queries, generated SQL, execution latency (in ms), row counts, and error logs.
- Enables 1-click query re-run and CSV export from the UI.

---

## 📡 API Endpoints Reference

| Endpoint | Method | Description |
|---|---|---|
| `/api/auth/login/` | `POST` | Authenticate user & return JWT tokens |
| `/api/auth/register/` | `POST` | Create user & new organization workspace |
| `/api/auth/me/` | `GET` | Get current authenticated user profile |
| `/api/connections/` | `GET`, `POST` | List & create tenant database connections |
| `/api/connections/<id>/test-existing/` | `POST` | Test connectivity to a saved database |
| `/api/connections/<id>/sync-schema/` | `POST` | Introspect and cache database schema |
| `/api/schema/<conn_id>/` | `GET` | Fetch schema tables, columns, and foreign keys |
| `/api/schema/<conn_id>/tables/<name>/preview/` | `GET` | Preview sample records from a table |
| `/api/query/process/` | `POST` | Check ambiguity and generate verified SQL |
| `/api/query/execute/` | `POST` | Safely execute SQL and log to history |
| `/api/query/explain/` | `POST` | Explain SQL logic in plain English |
| `/api/history/` | `GET` | Query history audit trail with search & filters |
| `/api/history/stats/` | `GET` | Aggregated dashboard performance metrics |

---

## 🧪 Testing

Run backend tests:
```bash
python backend/manage.py test accounts
```

Test frontend production build:
```bash
cd frontend && npm run build
```

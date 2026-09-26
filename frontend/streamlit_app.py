"""
QueryMind Enterprise Streamlit Client.
Designed with professional SaaS aesthetics, restrained color palette,
clear information hierarchy, and zero decorative fluff.
"""

import streamlit as st
import pandas as pd
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.intent.models import QueryRequest
from app.services.query_service import query_service
from app.database.metadata import SCHEMA_METADATA
from app.core.config import settings
from app.database.connection import db_manager

# Page configuration
st.set_page_config(
    page_title="QueryMind - Database Query Assistant",
    layout="wide"
)

# Enterprise SaaS Styling - No gradients, no emojis, clean borders
st.markdown("""
<style>
    /* Hide Streamlit default Deploy button, decoration header, and branding */
    .stDeployButton, 
    [data-testid="stDeployButton"], 
    .stAppDeployButton,
    header [data-testid="stToolbar"],
    [data-testid="stToolbar"] {
        display: none !important;
        visibility: hidden !important;
    }
    #MainMenu {
        visibility: hidden !important;
    }
    footer {
        visibility: hidden !important;
    }

    /* System Font Stack */
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        color: #0f172a;
    }
    
    /* Top Header */
    .saas-header {
        border-bottom: 1px solid #e2e8f0;
        padding-bottom: 14px;
        margin-bottom: 20px;
    }
    .saas-title {
        font-size: 1.35rem;
        font-weight: 700;
        color: #0f172a;
        letter-spacing: -0.2px;
        margin: 0;
    }
    .saas-subtitle {
        font-size: 0.85rem;
        color: #64748b;
        margin-top: 2px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Clarification Box */
    .clarification-card {
        background-color: #fffdf5;
        border: 1px solid #fde68a;
        border-radius: 4px;
        padding: 16px;
        margin-top: 12px;
        margin-bottom: 20px;
    }
    .clarification-tag {
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #92400e;
        margin-bottom: 4px;
    }
    .clarification-title {
        font-size: 14px;
        font-weight: 600;
        color: #78350f;
    }
    .clarification-reason {
        font-size: 13px;
        color: #92400e;
        margin-top: 2px;
        margin-bottom: 12px;
    }

    /* Summary and Interpretation callouts */
    .interpretation-card {
        background-color: #f1f5f9;
        border: 1px solid #cbd5e1;
        border-radius: 4px;
        padding: 10px 14px;
        font-size: 12px;
        color: #334155;
        margin-bottom: 14px;
    }
    .summary-card {
        background-color: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-radius: 4px;
        padding: 12px 16px;
        font-size: 13px;
        color: #166534;
        margin-bottom: 16px;
        line-height: 1.5;
    }

    /* Badges */
    .status-pill {
        display: inline-block;
        background-color: #f1f5f9;
        border: 1px solid #e2e8f0;
        color: #475569;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    }
    .status-safe {
        background-color: #f0fdf4;
        border: 1px solid #bbf7d0;
        color: #166534;
    }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "pending_clarification" not in st.session_state:
    st.session_state.pending_clarification = None
if "current_question" not in st.session_state:
    st.session_state.current_question = ""
if "query_result" not in st.session_state:
    st.session_state.query_result = None
if "query_history" not in st.session_state:
    st.session_state.query_history = []
if "selected_clarification_choice" not in st.session_state:
    st.session_state.selected_clarification_choice = None

# Top Navigation Bar
st.markdown("""
<div class="saas-header">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <div class="saas-title">QueryMind</div>
            <div class="saas-subtitle">Ambiguity-Aware Database Query Assistant</div>
        </div>
        <div style="display: flex; gap: 8px;">
            <span class="status-pill status-safe">Engine: SQLite (Read-Only)</span>
            <span class="status-pill">10 Relational Tables</span>
            <span class="status-pill">Ref Date: 2026-09-26</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Workspace Navigation Tabs
tab_query, tab_history, tab_schema, tab_benchmark = st.tabs([
    "Query Workspace",
    "Query History",
    "Schema Catalog",
    "Benchmark & Evaluation"
])

# ==========================================
# TAB 1: QUERY WORKSPACE
# ==========================================
with tab_query:
    col_input, col_btn = st.columns([5, 1])
    with col_input:
        user_query = st.text_input(
            "Natural Language Query",
            value=st.session_state.current_question,
            placeholder="e.g. Show me the best customers last month",
            label_visibility="collapsed"
        )
    with col_btn:
        exec_clicked = st.button("Execute Query", type="primary", use_container_width=True)

    # Sample reference queries
    st.markdown("<span style='font-size: 12px; color: #64748b;'>Reference Queries:</span>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("Customer signups last month", use_container_width=True):
            st.session_state.current_question = "How many customers signed up last month?"
            st.session_state.pending_clarification = None
            st.session_state.selected_clarification_choice = None
            st.rerun()
    with c2:
        if st.button("Customers from Mumbai", use_container_width=True):
            st.session_state.current_question = "Show customers from Mumbai"
            st.session_state.pending_clarification = None
            st.session_state.selected_clarification_choice = None
            st.rerun()
    with c3:
        if st.button("Best customers [Ambiguous]", use_container_width=True):
            st.session_state.current_question = "Show me the best customers last month"
            st.session_state.pending_clarification = None
            st.session_state.selected_clarification_choice = None
            st.rerun()
    with c4:
        if st.button("Top products [Ambiguous]", use_container_width=True):
            st.session_state.current_question = "Which products are performing well?"
            st.session_state.pending_clarification = None
            st.session_state.selected_clarification_choice = None
            st.rerun()

    # Query Execution Logic
    if exec_clicked and user_query.strip():
        st.session_state.current_question = user_query.strip()
        req = QueryRequest(
            session_id=st.session_state.session_id,
            question=user_query.strip()
        )
        with st.spinner("Analyzing intent and checking schema..."):
            res = query_service.process_query(req)
            st.session_state.session_id = res.session_id
            
            if res.status == "clarification_required":
                st.session_state.pending_clarification = res.clarification
                st.session_state.query_result = None
            else:
                st.session_state.pending_clarification = None
                st.session_state.query_result = res
                st.session_state.query_history.insert(0, {
                    "question": user_query.strip(),
                    "clarification": None,
                    "sql": res.generated_sql,
                    "rows": res.data.row_count if res.data else 0,
                    "ms": res.data.execution_time_ms if res.data else 0
                })

    # Clarification Interface
    if st.session_state.pending_clarification:
        clar = st.session_state.pending_clarification
        st.markdown(f"""
        <div class="clarification-card">
            <div class="clarification-tag">Clarification Required</div>
            <div class="clarification-title">{clar.question}</div>
            <div class="clarification-reason">{clar.reason} (Detected ambiguous term: '{clar.term}')</div>
        </div>
        """, unsafe_allow_html=True)

        chosen_option = st.radio(
            "Select interpretation:",
            options=clar.options,
            label_visibility="collapsed"
        )
        if st.button("Confirm & Execute Query", type="primary"):
            st.session_state.selected_clarification_choice = chosen_option
            req = QueryRequest(
                session_id=st.session_state.session_id,
                question=st.session_state.current_question,
                selected_clarification=chosen_option
            )
            with st.spinner("Resolving intent and generating SQL..."):
                res = query_service.process_query(req)
                st.session_state.pending_clarification = None
                st.session_state.query_result = res
                st.session_state.query_history.insert(0, {
                    "question": st.session_state.current_question,
                    "clarification": chosen_option,
                    "sql": res.generated_sql,
                    "rows": res.data.row_count if res.data else 0,
                    "ms": res.data.execution_time_ms if res.data else 0
                })
                st.rerun()

    # Results Display
    if st.session_state.query_result:
        res = st.session_state.query_result

        if res.status == "error":
            st.error(res.error_message)
            if res.generated_sql:
                st.code(res.generated_sql, language="sql")
        else:
            st.markdown("---")
            if st.session_state.selected_clarification_choice:
                st.markdown(f"""
                <div class="interpretation-card">
                    <span style="font-weight: 600; text-transform: uppercase; font-size: 11px; letter-spacing: 0.5px;">Resolved Interpretation:</span>
                    {st.session_state.selected_clarification_choice}
                </div>
                """, unsafe_allow_html=True)

            if res.explanation:
                st.markdown(f"""
                <div class="summary-card">
                    {res.explanation}
                </div>
                """, unsafe_allow_html=True)

            col_sql, col_meta = st.columns([4, 1])
            with col_sql:
                st.markdown("<span style='font-size: 12px; font-weight: 600; text-transform: uppercase; color: #475569;'>Validated SQL Query</span>", unsafe_allow_html=True)
                st.code(res.generated_sql, language="sql")
            with col_meta:
                st.markdown("<span style='font-size: 12px; font-weight: 600; text-transform: uppercase; color: #475569;'>Execution</span>", unsafe_allow_html=True)
                st.metric("Latency", f"{res.data.execution_time_ms} ms")
                st.metric("Rows", res.data.row_count)

            if res.data and res.data.rows:
                df = pd.DataFrame(res.data.rows, columns=res.data.columns)
                st.markdown("<span style='font-size: 12px; font-weight: 600; text-transform: uppercase; color: #475569;'>Result Table</span>", unsafe_allow_html=True)
                st.dataframe(df, use_container_width=True, hide_index=True)

                # Export CSV
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="query_results.csv",
                    mime="text/csv",
                    use_container_width=False
                )

# ==========================================
# TAB 2: QUERY HISTORY
# ==========================================
with tab_history:
    st.markdown("### Session Query Audit Log")
    if not st.session_state.query_history:
        st.info("No queries have been executed in this session yet.")
    else:
        for idx, item in enumerate(st.session_state.query_history):
            with st.container():
                st.markdown(f"**{item['question']}**")
                meta_line = f"Rows: {item['rows']} | Time: {item['ms']} ms"
                if item['clarification']:
                    meta_line += f" | Clarified: {item['clarification']}"
                st.caption(meta_line)
                st.code(item['sql'], language="sql")
                st.divider()

# ==========================================
# TAB 3: SCHEMA CATALOG
# ==========================================
with tab_schema:
    st.markdown("### Relational Database Catalog")
    table_list = list(SCHEMA_METADATA["tables"].keys())
    selected_table = st.selectbox("Select Table:", options=table_list)

    if selected_table:
        t_meta = SCHEMA_METADATA["tables"][selected_table]
        st.markdown(f"**Description:** {t_meta['description']}")

        cols_data = []
        for col, info in t_meta["columns"].items():
            is_pk = col == t_meta["primary_key"]
            cols_data.append({
                "Column": col + (" [PK]" if is_pk else ""),
                "Data Type": info["type"],
                "Description": info["description"]
            })
        st.table(pd.DataFrame(cols_data))

        if t_meta["foreign_keys"]:
            st.markdown("**Foreign Key Constraints:**")
            fk_data = [
                {"Column": fk["column"], "References": f"{fk['references_table']}.{fk['references_column']}"}
                for fk in t_meta["foreign_keys"]
            ]
            st.table(pd.DataFrame(fk_data))

# ==========================================
# TAB 4: BENCHMARK & EVALUATION
# ==========================================
with tab_benchmark:
    st.markdown("### Automated Benchmark Evaluation")
    st.caption("Standardized test queries evaluating precision across simple, aggregation, multi-table, complex, ambiguous, and security queries.")

    if st.button("Run Benchmark Evaluation", type="primary"):
        with st.spinner("Executing test queries across database..."):
            from tests.evaluate_benchmark import DATASET_PATH
            with open(DATASET_PATH, "r") as f:
                cases = json.load(f)

            stats = {}
            for case in cases:
                q_type = case["type"].title()
                if q_type not in stats:
                    stats[q_type] = {"total": 0, "passed": 0}
                stats[q_type]["total"] += 1

                if case["type"] == "security_adversarial":
                    from app.sql.validator import sql_validator
                    is_valid, _, _ = sql_validator.validate_and_sanitize(case["question"])
                    if not is_valid:
                        stats[q_type]["passed"] += 1
                elif case["is_ambiguous"]:
                    r1 = query_service.process_query(QueryRequest(question=case["question"]))
                    if r1.status == "clarification_required":
                        clar_opt = case.get("test_clarification", r1.clarification.options[0])
                        r2 = query_service.process_query(QueryRequest(
                            session_id=r1.session_id,
                            question=case["question"],
                            selected_clarification=clar_opt
                        ))
                        if r2.status == "success" and r2.data and r2.data.row_count > 0:
                            stats[q_type]["passed"] += 1
                else:
                    r = query_service.process_query(QueryRequest(question=case["question"]))
                    if r.status == "success" and r.data and r.data.row_count >= 0:
                        stats[q_type]["passed"] += 1

            rows = []
            tot_cases, tot_passed = 0, 0
            for k, v in stats.items():
                tot_cases += v["total"]
                tot_passed += v["passed"]
                acc = (v["passed"] / v["total"]) * 100
                rows.append({"Category": k, "Evaluated": v["total"], "Passed": v["passed"], "Accuracy": f"{acc:.1f}%"})
            
            ov_acc = (tot_passed / tot_cases) * 100
            rows.append({"Category": "TOTAL OVERALL", "Evaluated": tot_cases, "Passed": tot_passed, "Accuracy": f"{ov_acc:.1f}%"})
            st.table(pd.DataFrame(rows))



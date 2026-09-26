import React, { useState, useEffect } from "react";
import { History as HistoryIcon, Search, Play, Copy, Check, Clock, CheckCircle, AlertCircle, HelpCircle } from "lucide-react";
import api from "../services/api";

export default function History({ onRerunQuery }) {
  const [historyItems, setHistoryItems] = useState([]);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [loading, setLoading] = useState(true);
  const [copiedId, setCopiedId] = useState(null);

  useEffect(() => {
    async function fetchHistory() {
      setLoading(true);
      try {
        const params = {};
        if (search) params.search = search;
        if (statusFilter !== "all") params.status = statusFilter;

        const res = await api.history.list(params);
        setHistoryItems(res.results || res || []);
      } catch (err) {
        console.error("Failed to fetch query history:", err);
      } finally {
        setLoading(false);
      }
    }
    fetchHistory();
  }, [search, statusFilter]);

  const handleCopy = (id, text) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div style={{ padding: "28px", display: "flex", flexDirection: "column", gap: "20px" }}>
      {/* Header and Toolbar */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "14px" }}>
        <div>
          <h2 style={{ fontSize: "20px", fontWeight: 800, color: "#FFF" }}>Query History & Audit Log</h2>
          <p style={{ fontSize: "13px", color: "var(--text-muted)", marginTop: "2px" }}>
            Complete audit trail of all natural language questions, generated SQL, and execution metrics
          </p>
        </div>

        {/* Filter controls */}
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          {/* Search box */}
          <div style={{ position: "relative" }}>
            <Search
              size={14}
              style={{
                position: "absolute",
                left: "10px",
                top: "50%",
                transform: "translateY(-50%)",
                color: "var(--text-subtle)"
              }}
            />
            <input
              type="text"
              placeholder="Search history..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{
                padding: "8px 12px 8px 32px",
                background: "var(--bg-elevated)",
                border: "1px solid var(--border-subtle)",
                borderRadius: "var(--radius-md)",
                color: "#FFF",
                fontSize: "13px",
                outline: "none",
                width: "220px"
              }}
            />
          </div>

          {/* Status filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            style={{
              padding: "8px 14px",
              background: "var(--bg-elevated)",
              border: "1px solid var(--border-subtle)",
              borderRadius: "var(--radius-md)",
              color: "#FFF",
              fontSize: "13px",
              outline: "none"
            }}
          >
            <option value="all">All Statuses</option>
            <option value="success">Success</option>
            <option value="error">Error</option>
          </select>
        </div>
      </div>

      {/* History Items List */}
      {loading ? (
        <div style={{ padding: "40px", textAlign: "center", color: "var(--text-subtle)" }}>
          Loading query history...
        </div>
      ) : historyItems.length === 0 ? (
        <div
          style={{
            padding: "40px",
            textAlign: "center",
            color: "var(--text-subtle)",
            border: "1px dashed var(--border-subtle)",
            borderRadius: "var(--radius-md)"
          }}
        >
          <HistoryIcon size={32} style={{ margin: "0 auto 12px", opacity: 0.4 }} />
          <p>No queries match your search or filter.</p>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
          {historyItems.map((item) => {
            const isCopied = copiedId === item.id;
            const dateStr = new Date(item.created_at).toLocaleString();

            return (
              <div
                key={item.id}
                className="glass-card"
                style={{
                  padding: "18px 22px",
                  display: "flex",
                  flexDirection: "column",
                  gap: "12px"
                }}
              >
                {/* Header line */}
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "8px" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                    <span className={`badge ${item.status === "success" ? "badge-success" : "badge-danger"}`}>
                      {item.status === "success" ? <CheckCircle size={11} /> : <AlertCircle size={11} />}
                      {item.status.toUpperCase()}
                    </span>

                    <span style={{ fontSize: "14px", fontWeight: 700, color: "#FFF" }}>
                      "{item.natural_query}"
                    </span>
                  </div>

                  <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                    <span style={{ fontSize: "12px", color: "var(--text-subtle)", display: "flex", alignItems: "center", gap: "4px" }}>
                      <Clock size={12} />
                      {dateStr}
                    </span>

                    <button
                      className="btn btn-secondary"
                      onClick={() => handleCopy(item.id, item.generated_sql)}
                      style={{ padding: "4px 8px", fontSize: "11px" }}
                      title="Copy SQL"
                    >
                      {isCopied ? <Check size={12} color="#10B981" /> : <Copy size={12} />}
                    </button>

                    {onRerunQuery && (
                      <button
                        className="btn btn-primary"
                        onClick={() => onRerunQuery(item.natural_query, item.generated_sql)}
                        style={{ padding: "4px 10px", fontSize: "11px" }}
                        title="Load into Query Studio"
                      >
                        <Play size={11} fill="#FFF" />
                        Re-run
                      </button>
                    )}
                  </div>
                </div>

                {/* Generated SQL snippet */}
                <div
                  style={{
                    background: "#060911",
                    padding: "10px 14px",
                    borderRadius: "var(--radius-sm)",
                    fontFamily: "var(--font-mono)",
                    fontSize: "12px",
                    color: "#38BDF8",
                    overflowX: "auto",
                    whiteSpace: "pre-wrap"
                  }}
                >
                  {item.generated_sql}
                </div>

                {/* Clarification or error info */}
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", fontSize: "12px", color: "var(--text-muted)" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                    <span>
                      Database: <strong style={{ color: "#E2E8F0" }}>{item.connection_name}</strong>
                    </span>
                    <span>•</span>
                    <span>
                      Execution: <strong style={{ color: "#E2E8F0" }}>{item.execution_time_ms} ms</strong>
                    </span>
                    <span>•</span>
                    <span>
                      Returned: <strong style={{ color: "#E2E8F0" }}>{item.row_count} rows</strong>
                    </span>
                  </div>

                  {item.clarification_log && (
                    <div style={{ display: "flex", alignItems: "center", gap: "6px", color: "#F59E0B" }}>
                      <HelpCircle size={13} />
                      <span>Clarified: {item.clarification_log.selected || item.clarification_log.term}</span>
                    </div>
                  )}

                  {item.error_message && (
                    <div style={{ color: "#EF4444", fontSize: "11px" }}>
                      {item.error_message}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

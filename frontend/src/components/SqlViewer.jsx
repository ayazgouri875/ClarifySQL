import React, { useState } from "react";
import { Copy, Check, Play, HelpCircle, ShieldCheck, Sparkles } from "lucide-react";
import api from "../services/api";

export default function SqlViewer({ sql, dialect = "SQL", onExecute, executing, question }) {
  const [copied, setCopied] = useState(false);
  const [explanation, setExplanation] = useState(null);
  const [explaining, setExplaining] = useState(false);
  const [showExplanation, setShowExplanation] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(sql);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleExplain = async () => {
    if (explanation) {
      setShowExplanation(!showExplanation);
      return;
    }
    setExplaining(true);
    try {
      const res = await api.query.explain({ question, sql });
      setExplanation(res.explanation);
      setShowExplanation(true);
    } catch (err) {
      console.error("Failed to explain query:", err);
    } finally {
      setExplaining(false);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
      {/* Top toolbar */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <span className="badge badge-neutral" style={{ textTransform: "uppercase" }}>
            {dialect}
          </span>
          <span className="badge badge-success">
            <ShieldCheck size={12} />
            Read-Only Verified
          </span>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <button
            className="btn btn-secondary"
            onClick={handleExplain}
            disabled={explaining}
            style={{ padding: "6px 12px", fontSize: "12px" }}
          >
            <Sparkles size={13} color="var(--accent-cyan)" />
            {explaining ? "Explaining..." : showExplanation ? "Hide Explanation" : "Explain Logic"}
          </button>

          <button
            className="btn btn-secondary"
            onClick={handleCopy}
            style={{ padding: "6px 12px", fontSize: "12px" }}
          >
            {copied ? <Check size={13} color="#10B981" /> : <Copy size={13} />}
            {copied ? "Copied" : "Copy SQL"}
          </button>

          {onExecute && (
            <button
              className="btn btn-primary"
              onClick={() => onExecute(sql)}
              disabled={executing}
              style={{ padding: "6px 16px", fontSize: "12px" }}
            >
              <Play size={13} fill="#FFF" />
              {executing ? "Executing..." : "Run Query"}
            </button>
          )}
        </div>
      </div>

      {/* SQL code block */}
      <div className="sql-box">{sql}</div>

      {/* Explanation panel if expanded */}
      {showExplanation && explanation && (
        <div
          style={{
            padding: "16px",
            background: "rgba(6, 182, 212, 0.05)",
            border: "1px solid rgba(6, 182, 212, 0.2)",
            borderRadius: "var(--radius-md)",
            fontSize: "13px",
            lineHeight: 1.6,
            color: "#E2E8F0",
            whiteSpace: "pre-line"
          }}
        >
          <div style={{ fontWeight: 700, color: "var(--accent-cyan)", marginBottom: "6px", display: "flex", alignItems: "center", gap: "6px" }}>
            <Sparkles size={14} />
            Business Logic Explanation
          </div>
          {explanation}
        </div>
      )}
    </div>
  );
}

import React, { useState, useEffect } from "react";
import { Terminal, Sparkles, AlertCircle, Play, CheckCircle2, RotateCcw, HelpCircle } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import api from "../services/api";
import SqlViewer from "../components/SqlViewer";
import DataTable from "../components/DataTable";
import ClarificationModal from "../components/ClarificationModal";

export default function Query({ initialQuestion = "" }) {
  const { activeConnection, connections } = useAuth();
  const [question, setQuestion] = useState(initialQuestion);
  const [processing, setProcessing] = useState(false);
  const [executing, setExecuting] = useState(false);
  const [error, setError] = useState(null);
  
  // Pipeline states
  const [ambiguityData, setAmbiguityData] = useState(null);
  const [resolvedSpec, setResolvedSpec] = useState(null);
  const [generatedSql, setGeneratedSql] = useState("");
  const [queryResult, setQueryResult] = useState(null);

  useEffect(() => {
    if (initialQuestion) {
      setQuestion(initialQuestion);
    }
  }, [initialQuestion]);

  const handleProcessQuery = async (overrideOption = null, category = null) => {
    if (!question.trim()) return;
    if (!activeConnection) {
      setError("Please select or add an active database connection first.");
      return;
    }

    setError(null);
    setProcessing(true);
    setQueryResult(null);

    try {
      const payload = {
        connection_id: activeConnection.id,
        question: question.trim(),
        selected_option: overrideOption,
        category: category
      };

      const res = await api.query.process(payload);

      if (res.status === "clarification_needed" && res.is_ambiguous) {
        // Trigger Clarification Modal
        setAmbiguityData(res.ambiguity);
        setGeneratedSql("");
      } else if (res.status === "sql_generated") {
        setAmbiguityData(null);
        setGeneratedSql(res.sql);
        setResolvedSpec(res.resolved_specification || null);

        // Automatically execute generated SQL for instant gratification
        await handleExecute(res.sql, res.resolved_specification ? { selected: overrideOption, spec: res.resolved_specification } : null);
      }
    } catch (err) {
      setError(err.message || "Failed to process query.");
    } finally {
      setProcessing(false);
    }
  };

  const handleClarificationSubmit = async (selectedOption, category) => {
    setAmbiguityData(null);
    await handleProcessQuery(selectedOption, category);
  };

  const handleExecute = async (sqlToRun, clarificationLog = null) => {
    const targetSql = sqlToRun || generatedSql;
    if (!targetSql || !activeConnection) return;

    setExecuting(true);
    setError(null);

    try {
      const res = await api.query.execute({
        connection_id: activeConnection.id,
        sql: targetSql,
        question: question.trim(),
        clarification_log: clarificationLog
      });

      if (!res.success) {
        setError(res.error || "Query execution failed.");
      } else {
        setQueryResult(res);
      }
    } catch (err) {
      setError(err.message || "Execution error.");
    } finally {
      setExecuting(false);
    }
  };

  const handleReset = () => {
    setQuestion("");
    setGeneratedSql("");
    setQueryResult(null);
    setAmbiguityData(null);
    setResolvedSpec(null);
    setError(null);
  };

  return (
    <div style={{ padding: "28px", display: "flex", flexDirection: "column", gap: "24px", maxWidth: "1200px" }}>
      {/* Input Workbench */}
      <div
        className="glass-card"
        style={{
          padding: "24px 28px",
          border: "1px solid rgba(99, 102, 241, 0.3)",
          boxShadow: "0 10px 30px -5px rgba(0, 0, 0, 0.5)"
        }}
      >
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "12px" }}>
          <label style={{ fontSize: "14px", fontWeight: 700, color: "#FFF", display: "flex", alignItems: "center", gap: "8px" }}>
            <Sparkles size={16} color="var(--primary)" />
            Natural Language Question
          </label>
          {resolvedSpec && (
            <span
              className="badge badge-success"
              style={{ fontSize: "11px", fontWeight: 500 }}
              title={resolvedSpec}
            >
              Clarified: {resolvedSpec}
            </span>
          )}
        </div>

        <div style={{ position: "relative" }}>
          <textarea
            className="input-field"
            rows={3}
            placeholder="e.g. Who are our best customers recently? Or: Show monthly sales breakdown by category..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleProcessQuery();
              }
            }}
            style={{
              resize: "none",
              fontSize: "15px",
              lineHeight: 1.5,
              padding: "14px",
              borderRadius: "var(--radius-md)"
            }}
          />
        </div>

        {/* Toolbar */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginTop: "14px", flexWrap: "wrap", gap: "10px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", fontSize: "12px", color: "var(--text-subtle)" }}>
            <span>Target:</span>
            <strong style={{ color: "#E2E8F0" }}>
              {activeConnection ? `${activeConnection.name} (${activeConnection.db_type.toUpperCase()})` : "No Database"}
            </strong>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            {(question || generatedSql) && (
              <button
                className="btn btn-secondary"
                onClick={handleReset}
                style={{ padding: "8px 14px", fontSize: "13px" }}
              >
                <RotateCcw size={14} />
                Reset
              </button>
            )}

            <button
              className="btn btn-primary"
              disabled={processing || executing || !question.trim() || !activeConnection}
              onClick={() => handleProcessQuery()}
              style={{ padding: "10px 22px", fontSize: "14px" }}
            >
              <Sparkles size={15} />
              {processing ? "Analyzing Ambiguity..." : "Generate & Run"}
            </button>
          </div>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <div
          style={{
            padding: "14px 18px",
            background: "rgba(239, 68, 68, 0.12)",
            border: "1px solid rgba(239, 68, 68, 0.3)",
            borderRadius: "var(--radius-md)",
            color: "#F87171",
            fontSize: "13.5px",
            display: "flex",
            alignItems: "flex-start",
            gap: "10px"
          }}
        >
          <AlertCircle size={18} style={{ flexShrink: 0, marginTop: "2px" }} />
          <div>
            <strong>Execution Alert:</strong> {error}
          </div>
        </div>
      )}

      {/* Ambiguity Modal Trigger */}
      {ambiguityData && (
        <ClarificationModal
          ambiguity={ambiguityData}
          onSubmit={handleClarificationSubmit}
          onCancel={() => setAmbiguityData(null)}
        />
      )}

      {/* Generated SQL Viewer */}
      {generatedSql && (
        <div className="glass-card" style={{ padding: "20px 24px" }}>
          <h3 style={{ fontSize: "15px", fontWeight: 700, color: "#FFF", marginBottom: "14px" }}>
            Verified Generated SQL
          </h3>
          <SqlViewer
            sql={generatedSql}
            dialect={activeConnection?.db_type || "SQL"}
            onExecute={handleExecute}
            executing={executing}
            question={question}
          />
        </div>
      )}

      {/* Tabular Output */}
      {queryResult && (
        <div className="glass-card" style={{ padding: "20px 24px" }}>
          <h3 style={{ fontSize: "15px", fontWeight: 700, color: "#FFF", marginBottom: "14px" }}>
            Query Results
          </h3>
          <DataTable
            columns={queryResult.columns}
            rows={queryResult.rows}
            executionTimeMs={queryResult.execution_time_ms}
            rowCount={queryResult.row_count}
          />
        </div>
      )}
    </div>
  );
}

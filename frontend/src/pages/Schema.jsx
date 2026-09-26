import React, { useState, useEffect } from "react";
import { GitFork, Table as TableIcon, Key, Eye, Terminal, RefreshCw, Database } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import api from "../services/api";

export default function Schema({ onQueryTable }) {
  const { activeConnection } = useAuth();
  const [schemaData, setSchemaData] = useState(null);
  const [selectedTable, setSelectedTable] = useState(null);
  const [previewRows, setPreviewRows] = useState([]);
  const [previewCols, setPreviewCols] = useState([]);
  const [loadingPreview, setLoadingPreview] = useState(false);
  const [loadingSchema, setLoadingSchema] = useState(false);

  useEffect(() => {
    async function loadSchema() {
      if (!activeConnection) {
        setSchemaData(null);
        setSelectedTable(null);
        return;
      }
      setLoadingSchema(true);
      try {
        const res = await api.schema.get(activeConnection.id);
        const schema = res.schema;
        setSchemaData(schema);
        if (schema?.tables) {
          const firstTbl = Object.keys(schema.tables)[0];
          setSelectedTable(firstTbl);
        }
      } catch (err) {
        console.error("Failed to load schema:", err);
      } finally {
        setLoadingSchema(false);
      }
    }
    loadSchema();
  }, [activeConnection]);

  // Load preview data when selected table changes
  useEffect(() => {
    async function loadTablePreview() {
      if (!activeConnection || !selectedTable) return;
      setLoadingPreview(true);
      try {
        const res = await api.schema.previewTable(activeConnection.id, selectedTable, 5);
        setPreviewCols(res.columns || []);
        setPreviewRows(res.rows || []);
      } catch (err) {
        console.error("Preview load error:", err);
      } finally {
        setLoadingPreview(false);
      }
    }
    loadTablePreview();
  }, [activeConnection, selectedTable]);

  if (!activeConnection) {
    return (
      <div style={{ padding: "40px", textAlign: "center", color: "var(--text-subtle)" }}>
        <Database size={40} style={{ margin: "0 auto 12px", opacity: 0.4 }} />
        <h3>No Active Database Connection</h3>
        <p style={{ fontSize: "14px", marginTop: "4px" }}>Select a connection from the top navigation bar to explore its schema.</p>
      </div>
    );
  }

  const tables = schemaData?.tables || {};
  const currentTableMeta = selectedTable ? tables[selectedTable] : null;

  return (
    <div style={{ padding: "28px", display: "flex", gap: "24px", minHeight: "calc(100vh - 120px)" }}>
      {/* Left: Table List */}
      <div
        className="glass-card"
        style={{
          width: "280px",
          flexShrink: 0,
          padding: "18px 14px",
          display: "flex",
          flexDirection: "column",
          gap: "8px"
        }}
      >
        <div style={{ padding: "4px 8px 12px", borderBottom: "1px solid var(--border-subtle)" }}>
          <h3 style={{ fontSize: "14px", fontWeight: 700, color: "#FFF", display: "flex", alignItems: "center", gap: "8px" }}>
            <TableIcon size={16} color="var(--primary)" />
            Relational Tables ({Object.keys(tables).length})
          </h3>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: "4px", overflowY: "auto", flex: 1 }}>
          {Object.keys(tables).map((tableName) => {
            const isSelected = selectedTable === tableName;
            const colCount = Object.keys(tables[tableName]?.columns || {}).length;

            return (
              <button
                key={tableName}
                onClick={() => setSelectedTable(tableName)}
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  padding: "9px 12px",
                  borderRadius: "var(--radius-md)",
                  border: isSelected ? "1px solid rgba(99, 102, 241, 0.4)" : "1px solid transparent",
                  background: isSelected ? "rgba(99, 102, 241, 0.15)" : "transparent",
                  color: isSelected ? "#FFF" : "var(--text-muted)",
                  fontWeight: isSelected ? 600 : 500,
                  fontSize: "13px",
                  cursor: "pointer",
                  textAlign: "left",
                  transition: "all 0.15s ease"
                }}
              >
                <span>{tableName}</span>
                <span style={{ fontSize: "11px", color: "var(--text-subtle)" }}>{colCount} cols</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Right: Table Detail & Preview */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: "20px", minWidth: 0 }}>
        {currentTableMeta ? (
          <>
            {/* Table Header Card */}
            <div className="glass-card" style={{ padding: "20px 24px" }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "10px" }}>
                <div>
                  <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                    <h2 style={{ fontSize: "20px", fontWeight: 800, color: "#FFF" }}>{selectedTable}</h2>
                    <span className="badge badge-neutral" style={{ fontSize: "11px" }}>
                      {Object.keys(currentTableMeta.columns || {}).length} Columns
                    </span>
                  </div>
                  {currentTableMeta.description && (
                    <p style={{ fontSize: "13px", color: "var(--text-muted)", marginTop: "4px" }}>
                      {currentTableMeta.description}
                    </p>
                  )}
                </div>

                {onQueryTable && (
                  <button
                    className="btn btn-primary"
                    onClick={() => onQueryTable(`SELECT * FROM ${selectedTable} LIMIT 25;`)}
                    style={{ padding: "8px 14px", fontSize: "12px" }}
                  >
                    <Terminal size={14} />
                    Query Table
                  </button>
                )}
              </div>

              {/* Foreign Keys pill list if any */}
              {currentTableMeta.foreign_keys && currentTableMeta.foreign_keys.length > 0 && (
                <div style={{ marginTop: "14px", display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap" }}>
                  <span style={{ fontSize: "12px", color: "var(--text-subtle)", fontWeight: 600 }}>Foreign Keys:</span>
                  {currentTableMeta.foreign_keys.map((fk, idx) => (
                    <span key={idx} className="badge badge-neutral" style={{ fontSize: "11px" }}>
                      <GitFork size={11} color="var(--accent-cyan)" />
                      {fk.column} → {fk.references_table}.{fk.references_column}
                    </span>
                  ))}
                </div>
              )}
            </div>

            {/* Column Schema Definition */}
            <div className="glass-card" style={{ padding: "20px 24px" }}>
              <h3 style={{ fontSize: "15px", fontWeight: 700, color: "#FFF", marginBottom: "14px" }}>
                Column Schema
              </h3>

              <div className="data-table-container">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Column Name</th>
                      <th>Data Type</th>
                      <th>Key / Index</th>
                      <th>Nullable</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(currentTableMeta.columns || {}).map(([colName, colInfo]) => {
                      const isPk = colInfo.primary_key;
                      return (
                        <tr key={colName}>
                          <td style={{ fontWeight: 600, color: isPk ? "#FBBF24" : "#FFF" }}>
                            {colName}
                          </td>
                          <td style={{ fontFamily: "var(--font-mono)", color: "var(--accent-cyan)", fontSize: "12px" }}>
                            {colInfo.type}
                          </td>
                          <td>
                            {isPk ? (
                              <span className="badge badge-warning" style={{ fontSize: "10px" }}>
                                <Key size={10} /> PRIMARY KEY
                              </span>
                            ) : (
                              <span style={{ color: "var(--text-subtle)", fontSize: "11px" }}>-</span>
                            )}
                          </td>
                          <td style={{ color: colInfo.nullable ? "var(--text-muted)" : "#EF4444", fontSize: "12px" }}>
                            {colInfo.nullable ? "YES" : "NO"}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Live Sample Preview */}
            <div className="glass-card" style={{ padding: "20px 24px" }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "14px" }}>
                <h3 style={{ fontSize: "15px", fontWeight: 700, color: "#FFF", display: "flex", alignItems: "center", gap: "8px" }}>
                  <Eye size={16} color="var(--accent-cyan)" />
                  Sample Records Preview (Top 5 rows)
                </h3>
              </div>

              {loadingPreview ? (
                <div style={{ padding: "20px", textAlign: "center", color: "var(--text-subtle)", fontSize: "13px" }}>
                  Loading preview data...
                </div>
              ) : previewRows.length > 0 ? (
                <div className="data-table-container">
                  <table className="data-table">
                    <thead>
                      <tr>
                        {previewCols.map((c) => (
                          <th key={c}>{c}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {previewRows.map((r, i) => (
                        <tr key={i}>
                          {previewCols.map((c) => (
                            <td key={c}>{String(r[c] ?? "null")}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div style={{ color: "var(--text-subtle)", fontSize: "12px" }}>No sample records found.</div>
              )}
            </div>
          </>
        ) : (
          <div style={{ padding: "40px", textAlign: "center", color: "var(--text-subtle)" }}>
            Select a table to view columns and preview data.
          </div>
        )}
      </div>
    </div>
  );
}

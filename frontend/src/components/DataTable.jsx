import React, { useState, useMemo } from "react";
import { Download, Search, ChevronLeft, ChevronRight, Database } from "lucide-react";

export default function DataTable({ columns = [], rows = [], executionTimeMs = 0, rowCount = 0 }) {
  const [searchTerm, setSearchTerm] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 15;

  // Filter rows based on search input
  const filteredRows = useMemo(() => {
    if (!searchTerm.trim()) return rows;
    const term = searchTerm.toLowerCase();
    return rows.filter((r) =>
      Object.values(r).some((val) => String(val ?? "").toLowerCase().includes(term))
    );
  }, [rows, searchTerm]);

  // Pagination calculation
  const totalPages = Math.ceil(filteredRows.length / pageSize) || 1;
  const paginatedRows = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return filteredRows.slice(start, start + pageSize);
  }, [filteredRows, currentPage, pageSize]);

  // Export to CSV
  const handleExportCSV = () => {
    if (!columns.length || !rows.length) return;
    const header = columns.join(",");
    const body = rows
      .map((row) =>
        columns
          .map((col) => {
            const val = row[col];
            if (val === null || val === undefined) return '""';
            return `"${String(val).replace(/"/g, '""')}"`;
          })
          .join(",")
      )
      .join("\n");
    const csvContent = "data:text/csv;charset=utf-8," + encodeURIComponent(`${header}\n${body}`);
    const link = document.createElement("a");
    link.setAttribute("href", csvContent);
    link.setAttribute("download", `query_results_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (!columns.length && !rows.length) {
    return (
      <div
        style={{
          padding: "40px",
          textAlign: "center",
          color: "var(--text-subtle)",
          border: "1px dashed var(--border-subtle)",
          borderRadius: "var(--radius-md)"
        }}
      >
        <Database size={32} style={{ margin: "0 auto 12px", opacity: 0.4 }} />
        <p style={{ fontSize: "14px" }}>No results to display. Execute a query to see tabular output.</p>
      </div>
    );
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
      {/* Table Toolbar */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "12px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <span className="badge badge-success">
            {rowCount || rows.length} rows returned
          </span>
          {executionTimeMs > 0 && (
            <span style={{ fontSize: "12px", color: "var(--text-subtle)" }}>
              Executed in <strong style={{ color: "var(--text-muted)" }}>{executionTimeMs} ms</strong>
            </span>
          )}
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          {/* Search filter */}
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
              placeholder="Filter results..."
              value={searchTerm}
              onChange={(e) => {
                setSearchTerm(e.target.value);
                setCurrentPage(1);
              }}
              style={{
                padding: "6px 12px 6px 30px",
                background: "var(--bg-elevated)",
                border: "1px solid var(--border-subtle)",
                borderRadius: "var(--radius-md)",
                color: "#FFF",
                fontSize: "12px",
                outline: "none",
                width: "180px"
              }}
            />
          </div>

          <button
            className="btn btn-secondary"
            onClick={handleExportCSV}
            style={{ padding: "6px 12px", fontSize: "12px" }}
          >
            <Download size={13} />
            Export CSV
          </button>
        </div>
      </div>

      {/* Tabular Output */}
      <div className="data-table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th style={{ width: "40px" }}>#</th>
              {columns.map((col) => (
                <th key={col}>{col}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {paginatedRows.map((row, idx) => (
              <tr key={idx}>
                <td style={{ color: "var(--text-subtle)", fontSize: "11px" }}>
                  {(currentPage - 1) * pageSize + idx + 1}
                </td>
                {columns.map((col) => {
                  const val = row[col];
                  const isNull = val === null || val === undefined;
                  const isNum = typeof val === "number";

                  return (
                    <td key={col} style={{ textAlign: isNum ? "right" : "left" }}>
                      {isNull ? (
                        <span style={{ color: "var(--text-subtle)", fontStyle: "italic", fontSize: "11px" }}>
                          null
                        </span>
                      ) : isNum ? (
                        val.toLocaleString()
                      ) : (
                        String(val)
                      )}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination Footer */}
      {totalPages > 1 && (
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "8px 0" }}>
          <span style={{ fontSize: "12px", color: "var(--text-subtle)" }}>
            Showing {(currentPage - 1) * pageSize + 1} to{" "}
            {Math.min(currentPage * pageSize, filteredRows.length)} of {filteredRows.length} entries
          </span>

          <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
            <button
              className="btn btn-secondary"
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              style={{ padding: "4px 8px" }}
            >
              <ChevronLeft size={14} />
            </button>
            <span style={{ fontSize: "12px", color: "var(--text-muted)", padding: "0 6px" }}>
              Page {currentPage} of {totalPages}
            </span>
            <button
              className="btn btn-secondary"
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              style={{ padding: "4px 8px" }}
            >
              <ChevronRight size={14} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

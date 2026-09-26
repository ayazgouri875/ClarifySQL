import React, { useState } from "react";
import { Database, Plus, RefreshCw, Trash2, CheckCircle, AlertCircle, HardDrive, ShieldCheck, Check } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import api from "../services/api";

export default function Connections() {
  const { connections, fetchConnections, activeConnection, setActiveConnection } = useAuth();
  const [showAddModal, setShowAddModal] = useState(false);
  const [testingId, setTestingId] = useState(null);
  const [syncingId, setSyncingId] = useState(null);
  const [feedback, setFeedback] = useState({});

  // Add Connection Form State
  const [name, setName] = useState("");
  const [dbType, setDbType] = useState("sqlite");
  const [databaseName, setDatabaseName] = useState("company.db");
  const [host, setHost] = useState("localhost");
  const [port, setPort] = useState(5432);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [sslEnabled, setSslEnabled] = useState(false);
  const [testingRaw, setTestingRaw] = useState(false);
  const [rawTestResult, setRawTestResult] = useState(null);
  const [saving, setSaving] = useState(false);
  const [modalError, setModalError] = useState(null);

  const handleTestExisting = async (id) => {
    setTestingId(id);
    try {
      const res = await api.connections.testExisting(id);
      setFeedback((prev) => ({
        ...prev,
        [id]: { ok: res.success, msg: res.message || (res.success ? "Online" : "Failed") }
      }));
      setTimeout(() => {
        setFeedback((prev) => {
          const c = { ...prev };
          delete c[id];
          return c;
        });
      }, 4000);
    } catch (err) {
      setFeedback((prev) => ({
        ...prev,
        [id]: { ok: false, msg: err.message || "Connection failed" }
      }));
    } finally {
      setTestingId(null);
    }
  };

  const handleSyncExisting = async (id) => {
    setSyncingId(id);
    try {
      const res = await api.connections.syncSchema(id);
      await fetchConnections();
      setFeedback((prev) => ({
        ...prev,
        [id]: { ok: true, msg: `Synced ${res.tables_count} tables!` }
      }));
      setTimeout(() => {
        setFeedback((prev) => {
          const c = { ...prev };
          delete c[id];
          return c;
        });
      }, 4000);
    } catch (err) {
      setFeedback((prev) => ({
        ...prev,
        [id]: { ok: false, msg: err.message || "Sync failed" }
      }));
    } finally {
      setSyncingId(null);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to remove this connection?")) return;
    try {
      await api.connections.delete(id);
      await fetchConnections();
    } catch (err) {
      alert("Failed to delete connection: " + err.message);
    }
  };

  const handleTestRaw = async () => {
    setTestingRaw(true);
    setRawTestResult(null);
    try {
      const res = await api.connections.test({
        db_type: dbType,
        database_name: databaseName,
        host,
        port: Number(port),
        username,
        password,
        ssl_enabled: sslEnabled
      });
      setRawTestResult({ success: res.success, message: res.message });
    } catch (err) {
      setRawTestResult({ success: false, message: err.message });
    } finally {
      setTestingRaw(false);
    }
  };

  const handleCreateConnection = async (e) => {
    e.preventDefault();
    setSaving(true);
    setModalError(null);
    try {
      await api.connections.create({
        name,
        db_type: dbType,
        database_name: databaseName,
        host: dbType === "sqlite" ? "localhost" : host,
        port: dbType === "sqlite" ? 0 : Number(port),
        username: dbType === "sqlite" ? "" : username,
        password: dbType === "sqlite" ? "" : password,
        ssl_enabled: sslEnabled
      });
      await fetchConnections();
      setShowAddModal(false);
      // Reset form
      setName("");
      setRawTestResult(null);
    } catch (err) {
      setModalError(err.message || "Failed to create connection");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div style={{ padding: "28px", display: "flex", flexDirection: "column", gap: "24px" }}>
      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "12px" }}>
        <div>
          <h2 style={{ fontSize: "20px", fontWeight: 800, color: "#FFF" }}>Database Connections</h2>
          <p style={{ fontSize: "13px", color: "var(--text-muted)", marginTop: "2px" }}>
            Connect and manage multi-tenant database sources for natural language querying
          </p>
        </div>

        <button className="btn btn-primary" onClick={() => setShowAddModal(true)}>
          <Plus size={16} />
          Add Connection
        </button>
      </div>

      {/* Connections List */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(340px, 1fr))", gap: "18px" }}>
        {connections.map((conn) => {
          const isActive = activeConnection?.id === conn.id;
          const statusFeedback = feedback[conn.id];

          return (
            <div
              key={conn.id}
              className="glass-card"
              style={{
                padding: "22px",
                border: isActive ? "1px solid #6366F1" : "1px solid var(--border-subtle)",
                display: "flex",
                flexDirection: "column",
                justifyContent: "space-between",
                gap: "18px"
              }}
            >
              <div>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "12px" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                    <div
                      style={{
                        width: "36px",
                        height: "36px",
                        borderRadius: "10px",
                        background: "rgba(99, 102, 241, 0.15)",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        color: "var(--primary)"
                      }}
                    >
                      <HardDrive size={18} />
                    </div>
                    <div>
                      <h3 style={{ fontSize: "15px", fontWeight: 700, color: "#FFF" }}>{conn.name}</h3>
                      <span className="badge badge-neutral" style={{ fontSize: "10px", marginTop: "2px" }}>
                        {conn.db_type.toUpperCase()}
                      </span>
                    </div>
                  </div>

                  {isActive ? (
                    <span className="badge badge-success" style={{ fontSize: "11px" }}>
                      Active
                    </span>
                  ) : (
                    <button
                      className="btn btn-secondary"
                      onClick={() => setActiveConnection(conn)}
                      style={{ padding: "4px 10px", fontSize: "11px" }}
                    >
                      Set Active
                    </button>
                  )}
                </div>

                {/* Connection Specs */}
                <div style={{ fontSize: "12px", color: "var(--text-muted)", display: "flex", flexDirection: "column", gap: "4px" }}>
                  <div>
                    <span style={{ color: "var(--text-subtle)" }}>Database:</span> {conn.database_name}
                  </div>
                  {conn.db_type !== "sqlite" && (
                    <div>
                      <span style={{ color: "var(--text-subtle)" }}>Host:</span> {conn.host}:{conn.port}
                    </div>
                  )}
                  <div>
                    <span style={{ color: "var(--text-subtle)" }}>Introspected Tables:</span>{" "}
                    <strong style={{ color: "#FFF" }}>{conn.table_count || 0} tables</strong>
                  </div>
                </div>

                {statusFeedback && (
                  <div
                    style={{
                      marginTop: "12px",
                      padding: "8px 10px",
                      borderRadius: "6px",
                      fontSize: "12px",
                      background: statusFeedback.ok ? "rgba(16, 185, 129, 0.1)" : "rgba(239, 68, 68, 0.1)",
                      color: statusFeedback.ok ? "#34D399" : "#F87171",
                      border: `1px solid ${statusFeedback.ok ? "rgba(16, 185, 129, 0.3)" : "rgba(239, 68, 68, 0.3)"}`
                    }}
                  >
                    {statusFeedback.msg}
                  </div>
                )}
              </div>

              {/* Action Toolbar */}
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", paddingTop: "14px", borderTop: "1px solid var(--border-subtle)" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  <button
                    className="btn btn-secondary"
                    onClick={() => handleTestExisting(conn.id)}
                    disabled={testingId === conn.id}
                    style={{ padding: "6px 10px", fontSize: "11px" }}
                  >
                    {testingId === conn.id ? "Testing..." : "Test"}
                  </button>

                  <button
                    className="btn btn-secondary"
                    onClick={() => handleSyncExisting(conn.id)}
                    disabled={syncingId === conn.id}
                    style={{ padding: "6px 10px", fontSize: "11px" }}
                  >
                    <RefreshCw size={11} className={syncingId === conn.id ? "spin" : ""} />
                    {syncingId === conn.id ? "Syncing..." : "Sync"}
                  </button>
                </div>

                <button
                  onClick={() => handleDelete(conn.id)}
                  title="Remove Connection"
                  style={{
                    background: "none",
                    border: "none",
                    color: "var(--text-subtle)",
                    cursor: "pointer",
                    padding: "6px"
                  }}
                  onMouseEnter={(e) => (e.currentTarget.style.color = "#EF4444")}
                  onMouseLeave={(e) => (e.currentTarget.style.color = "var(--text-subtle)")}
                >
                  <Trash2 size={15} />
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Add Connection Modal */}
      {showAddModal && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: "rgba(3, 7, 18, 0.8)",
            backdropFilter: "blur(8px)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 100,
            padding: "20px"
          }}
        >
          <div
            className="glass-card"
            style={{
              width: "100%",
              maxWidth: "520px",
              padding: "28px",
              background: "linear-gradient(180deg, #161F33 0%, #0E1626 100%)",
              border: "1px solid rgba(99, 102, 241, 0.3)"
            }}
          >
            <h3 style={{ fontSize: "18px", fontWeight: 700, color: "#FFF", marginBottom: "4px" }}>
              Connect New Database
            </h3>
            <p style={{ fontSize: "13px", color: "var(--text-muted)", marginBottom: "18px" }}>
              Configure a read-only relational database connection
            </p>

            {modalError && (
              <div
                style={{
                  padding: "8px 12px",
                  background: "rgba(239, 68, 68, 0.12)",
                  border: "1px solid rgba(239, 68, 68, 0.3)",
                  borderRadius: "6px",
                  color: "#F87171",
                  fontSize: "12px",
                  marginBottom: "14px"
                }}
              >
                {modalError}
              </div>
            )}

            <form onSubmit={handleCreateConnection}>
              <div className="input-group">
                <label className="input-label">Connection Name</label>
                <input
                  type="text"
                  required
                  className="input-field"
                  placeholder="e.g. Production Analytics"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                />
              </div>

              <div className="input-group">
                <label className="input-label">Database Type</label>
                <select
                  className="input-field"
                  value={dbType}
                  onChange={(e) => {
                    setDbType(e.target.value);
                    if (e.target.value === "postgresql") setPort(5432);
                    if (e.target.value === "mysql") setPort(3306);
                  }}
                >
                  <option value="sqlite">SQLite (Local embedded file)</option>
                  <option value="postgresql">PostgreSQL</option>
                  <option value="mysql">MySQL</option>
                </select>
              </div>

              <div className="input-group">
                <label className="input-label">
                  {dbType === "sqlite" ? "SQLite File Path" : "Database Name"}
                </label>
                <input
                  type="text"
                  required
                  className="input-field"
                  placeholder={dbType === "sqlite" ? "company.db" : "analytics_db"}
                  value={databaseName}
                  onChange={(e) => setDatabaseName(e.target.value)}
                />
              </div>

              {dbType !== "sqlite" && (
                <>
                  <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: "10px" }}>
                    <div className="input-group">
                      <label className="input-label">Host</label>
                      <input
                        type="text"
                        required
                        className="input-field"
                        value={host}
                        onChange={(e) => setHost(e.target.value)}
                      />
                    </div>
                    <div className="input-group">
                      <label className="input-label">Port</label>
                      <input
                        type="number"
                        required
                        className="input-field"
                        value={port}
                        onChange={(e) => setPort(e.target.value)}
                      />
                    </div>
                  </div>

                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
                    <div className="input-group">
                      <label className="input-label">Username</label>
                      <input
                        type="text"
                        className="input-field"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                      />
                    </div>
                    <div className="input-group">
                      <label className="input-label">Password</label>
                      <input
                        type="password"
                        className="input-field"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                      />
                    </div>
                  </div>

                  <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "16px" }}>
                    <input
                      type="checkbox"
                      id="sslCheck"
                      checked={sslEnabled}
                      onChange={(e) => setSslEnabled(e.target.checked)}
                    />
                    <label htmlFor="sslCheck" style={{ fontSize: "13px", color: "var(--text-muted)" }}>
                      Require SSL Connection
                    </label>
                  </div>
                </>
              )}

              {/* Raw Test Status */}
              {rawTestResult && (
                <div
                  style={{
                    padding: "8px 12px",
                    borderRadius: "6px",
                    fontSize: "12px",
                    marginBottom: "14px",
                    background: rawTestResult.success ? "rgba(16, 185, 129, 0.1)" : "rgba(239, 68, 68, 0.1)",
                    color: rawTestResult.success ? "#34D399" : "#F87171",
                    border: `1px solid ${rawTestResult.success ? "rgba(16, 185, 129, 0.3)" : "rgba(239, 68, 68, 0.3)"}`
                  }}
                >
                  {rawTestResult.message}
                </div>
              )}

              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginTop: "20px" }}>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={handleTestRaw}
                  disabled={testingRaw || !databaseName}
                >
                  {testingRaw ? "Testing..." : "Test Connection"}
                </button>

                <div style={{ display: "flex", gap: "8px" }}>
                  <button type="button" className="btn btn-secondary" onClick={() => setShowAddModal(false)}>
                    Cancel
                  </button>
                  <button type="submit" className="btn btn-primary" disabled={saving || !name}>
                    {saving ? "Saving..." : "Save Connection"}
                  </button>
                </div>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

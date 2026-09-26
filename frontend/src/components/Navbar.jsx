import React, { useState } from "react";
import { Database, RefreshCw, CheckCircle2, ChevronDown, Building } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import api from "../services/api";

export default function Navbar({ title }) {
  const { connections, activeConnection, setActiveConnection, fetchConnections, user } = useAuth();
  const [syncing, setSyncing] = useState(false);
  const [syncMsg, setSyncMsg] = useState(null);

  const handleSync = async () => {
    if (!activeConnection) return;
    setSyncing(true);
    setSyncMsg(null);
    try {
      const res = await api.connections.syncSchema(activeConnection.id);
      setSyncMsg(`Synced ${res.tables_count} tables!`);
      await fetchConnections();
      setTimeout(() => setSyncMsg(null), 3000);
    } catch (err) {
      setSyncMsg("Sync failed");
      setTimeout(() => setSyncMsg(null), 3000);
    } finally {
      setSyncing(false);
    }
  };

  return (
    <header
      style={{
        height: "64px",
        padding: "0 28px",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        borderBottom: "1px solid var(--border-subtle)",
        background: "rgba(11, 17, 30, 0.7)",
        backdropFilter: "blur(12px)",
        position: "sticky",
        top: 0,
        zIndex: 10
      }}
    >
      {/* Page Title & Org */}
      <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
        <h1 style={{ fontSize: "18px", fontWeight: 700, color: "#FFF" }}>{title}</h1>
        {user?.organization_name && (
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "6px",
              padding: "4px 10px",
              background: "rgba(255, 255, 255, 0.04)",
              border: "1px solid var(--border-subtle)",
              borderRadius: "var(--radius-full)",
              fontSize: "12px",
              color: "var(--text-muted)"
            }}
          >
            <Building size={13} color="var(--primary)" />
            {user.organization_name}
          </div>
        )}
      </div>

      {/* Connection Switcher & Sync */}
      <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
        {connections.length > 0 ? (
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <div style={{ position: "relative" }}>
              <select
                value={activeConnection?.id || ""}
                onChange={(e) => {
                  const sel = connections.find((c) => c.id === e.target.value);
                  if (sel) setActiveConnection(sel);
                }}
                style={{
                  appearance: "none",
                  background: "var(--bg-elevated)",
                  border: "1px solid var(--border-subtle)",
                  color: "#FFF",
                  padding: "8px 32px 8px 12px",
                  borderRadius: "var(--radius-md)",
                  fontSize: "13px",
                  fontWeight: 500,
                  cursor: "pointer",
                  outline: "none"
                }}
              >
                {connections.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name} ({c.db_type.toUpperCase()})
                  </option>
                ))}
              </select>
              <ChevronDown
                size={14}
                style={{
                  position: "absolute",
                  right: "10px",
                  top: "50%",
                  transform: "translateY(-50%)",
                  pointerEvents: "none",
                  color: "var(--text-subtle)"
                }}
              />
            </div>

            {activeConnection && (
              <button
                className="btn btn-secondary"
                onClick={handleSync}
                disabled={syncing}
                style={{ padding: "7px 12px", fontSize: "12px" }}
                title="Sync database schema"
              >
                <RefreshCw size={13} className={syncing ? "spin" : ""} />
                {syncing ? "Syncing..." : syncMsg || "Sync Schema"}
              </button>
            )}
          </div>
        ) : (
          <span style={{ fontSize: "12px", color: "var(--text-subtle)" }}>No database connected</span>
        )}

        <div style={{ width: "1px", height: "24px", background: "var(--border-subtle)" }} />

        {/* Engine status indicator */}
        <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "12px", color: "#10B981" }}>
          <CheckCircle2 size={14} />
          <span style={{ fontWeight: 600 }}>Engine Ready</span>
        </div>
      </div>
    </header>
  );
}

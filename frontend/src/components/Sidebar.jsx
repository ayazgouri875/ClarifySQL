import React from "react";
import { LayoutDashboard, Terminal, Database, GitFork, History, LogOut, Layers } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export default function Sidebar({ activeTab, setActiveTab }) {
  const { user, logout, activeConnection } = useAuth();

  const navItems = [
    { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
    { id: "query", label: "Query Studio", icon: Terminal },
    { id: "connections", label: "Connections", icon: Database },
    { id: "schema", label: "Schema Browser", icon: GitFork },
    { id: "history", label: "Query History", icon: History },
  ];

  return (
    <aside className="sidebar">
      {/* Brand Header */}
      <div style={{ padding: "24px 20px", borderBottom: "1px solid var(--border-subtle)" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <div
            style={{
              width: "36px",
              height: "36px",
              borderRadius: "10px",
              background: "linear-gradient(135deg, #6366F1 0%, #06B6D4 100%)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "#FFF",
              boxShadow: "0 0 16px rgba(99, 102, 241, 0.4)"
            }}
          >
            <Layers size={20} />
          </div>
          <div>
            <div style={{ fontWeight: 800, fontSize: "16px", letterSpacing: "-0.02em", color: "#FFF" }}>
              Text2SQL
            </div>
            <div style={{ fontSize: "11px", color: "var(--accent-cyan)", fontWeight: 600 }}>
              ENTERPRISE PLATFORM
            </div>
          </div>
        </div>
      </div>

      {/* Active Workspace / Connection Pill */}
      {activeConnection && (
        <div style={{ padding: "16px 20px 8px" }}>
          <div
            style={{
              padding: "10px 12px",
              background: "rgba(255, 255, 255, 0.03)",
              border: "1px solid var(--border-subtle)",
              borderRadius: "var(--radius-md)"
            }}
          >
            <div style={{ fontSize: "11px", color: "var(--text-subtle)", textTransform: "uppercase", fontWeight: 700 }}>
              Active Database
            </div>
            <div
              style={{
                fontSize: "13px",
                fontWeight: 600,
                color: "#E2E8F0",
                display: "flex",
                alignItems: "center",
                gap: "6px",
                marginTop: "3px"
              }}
            >
              <span
                style={{
                  width: "8px",
                  height: "8px",
                  borderRadius: "50%",
                  background: "#10B981",
                  boxShadow: "0 0 8px #10B981"
                }}
              />
              <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                {activeConnection.name}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Navigation List */}
      <nav style={{ flex: 1, padding: "16px 12px", display: "flex", flexDirection: "column", gap: "4px" }}>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "12px",
                padding: "11px 14px",
                width: "100%",
                borderRadius: "var(--radius-md)",
                border: "none",
                background: isActive
                  ? "linear-gradient(90deg, rgba(99, 102, 241, 0.15) 0%, rgba(99, 102, 241, 0.04) 100%)"
                  : "transparent",
                color: isActive ? "#818CF8" : "var(--text-muted)",
                fontWeight: isActive ? 600 : 500,
                fontSize: "14px",
                cursor: "pointer",
                textAlign: "left",
                transition: "all 0.2s ease",
                borderLeft: isActive ? "3px solid #6366F1" : "3px solid transparent"
              }}
              onMouseEnter={(e) => {
                if (!isActive) e.currentTarget.style.color = "#FFF";
              }}
              onMouseLeave={(e) => {
                if (!isActive) e.currentTarget.style.color = "var(--text-muted)";
              }}
            >
              <Icon size={18} />
              {item.label}
            </button>
          );
        })}
      </nav>

      {/* User info & Logout */}
      <div
        style={{
          padding: "16px 20px",
          borderTop: "1px solid var(--border-subtle)",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between"
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "10px", minWidth: 0 }}>
          <div
            style={{
              width: "32px",
              height: "32px",
              borderRadius: "50%",
              background: "linear-gradient(135deg, #6366F1 0%, #A855F7 100%)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "#FFF",
              fontWeight: 700,
              fontSize: "12px",
              flexShrink: 0
            }}
          >
            {user?.name?.[0]?.toUpperCase() || "U"}
          </div>
          <div style={{ minWidth: 0 }}>
            <div style={{ fontSize: "13px", fontWeight: 600, color: "#FFF", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
              {user?.name || "User"}
            </div>
            <div style={{ fontSize: "11px", color: "var(--text-subtle)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
              {user?.email || ""}
            </div>
          </div>
        </div>

        <button
          onClick={logout}
          title="Sign Out"
          style={{
            background: "transparent",
            border: "none",
            color: "var(--text-subtle)",
            cursor: "pointer",
            padding: "6px",
            borderRadius: "6px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center"
          }}
          onMouseEnter={(e) => (e.currentTarget.style.color = "#EF4444")}
          onMouseLeave={(e) => (e.currentTarget.style.color = "var(--text-subtle)")}
        >
          <LogOut size={16} />
        </button>
      </div>
    </aside>
  );
}

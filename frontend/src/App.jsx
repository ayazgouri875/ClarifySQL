import React, { useState } from "react";
import { AuthProvider, useAuth } from "./context/AuthContext";
import Sidebar from "./components/Sidebar";
import Navbar from "./components/Navbar";

// Pages
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Dashboard from "./pages/Dashboard";
import Query from "./pages/Query";
import Connections from "./pages/Connections";
import Schema from "./pages/Schema";
import History from "./pages/History";

function AppContent() {
  const { user, loading } = useAuth();
  const [authView, setAuthView] = useState("login"); // 'login' | 'signup'
  const [activeTab, setActiveTab] = useState("dashboard");
  const [querySeed, setQuerySeed] = useState("");

  if (loading) {
    return (
      <div
        style={{
          minHeight: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: "var(--bg-main)",
          color: "var(--text-muted)",
          fontSize: "14px"
        }}
      >
        Initializing QueryMind Platform...
      </div>
    );
  }

  // Unauthenticated view
  if (!user) {
    if (authView === "signup") {
      return <Signup onSwitchToLogin={() => setAuthView("login")} />;
    }
    return <Login onSwitchToSignup={() => setAuthView("signup")} />;
  }

  // Navigation handlers
  const handleNavigateToQuery = (questionText = "") => {
    setQuerySeed(questionText);
    setActiveTab("query");
  };

  const getPageTitle = () => {
    switch (activeTab) {
      case "dashboard":
        return "Analytics Dashboard";
      case "query":
        return "Natural Language Query Studio";
      case "connections":
        return "Database Connections";
      case "schema":
        return "Schema & Relationship Browser";
      case "history":
        return "Query Audit Log";
      default:
        return "QueryMind Platform";
    }
  };

  return (
    <div className="app-container">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

      <div className="main-content">
        <Navbar title={getPageTitle()} />

        <main style={{ flex: 1 }}>
          {activeTab === "dashboard" && (
            <Dashboard onNavigateToQuery={handleNavigateToQuery} />
          )}

          {activeTab === "query" && (
            <Query initialQuestion={querySeed} />
          )}

          {activeTab === "connections" && (
            <Connections />
          )}

          {activeTab === "schema" && (
            <Schema onQueryTable={handleNavigateToQuery} />
          )}

          {activeTab === "history" && (
            <History onRerunQuery={handleNavigateToQuery} />
          )}
        </main>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

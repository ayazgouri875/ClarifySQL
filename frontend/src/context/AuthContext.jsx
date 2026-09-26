import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import api from "../services/api";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(() => localStorage.getItem("token") || "");
  const [refreshToken, setRefreshToken] = useState(() => localStorage.getItem("refreshToken") || "");
  const [connections, setConnections] = useState([]);
  const [activeConnection, setActiveConnection] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchConnections = useCallback(async () => {
    try {
      const data = await api.connections.list();
      setConnections(data);
      if (data && data.length > 0) {
        // Keep active connection if already selected and exists, otherwise default to first
        setActiveConnection((prev) => {
          if (prev && data.some((c) => c.id === prev.id)) {
            return prev;
          }
          return data[0];
        });
      } else {
        setActiveConnection(null);
      }
    } catch (err) {
      console.error("Failed to load connections:", err);
    }
  }, []);

  const loadCurrentUser = useCallback(async () => {
    if (!token) {
      setLoading(false);
      return;
    }
    try {
      const userData = await api.auth.me();
      setUser(userData);
      await fetchConnections();
    } catch (err) {
      console.warn("Auth token invalid or expired. Logging out...", err);
      logout();
    } finally {
      setLoading(false);
    }
  }, [token, fetchConnections]);

  useEffect(() => {
    loadCurrentUser();
  }, [loadCurrentUser]);

  const login = async (email, password) => {
    setError(null);
    try {
      const res = await api.auth.login(email, password);
      const access = res.tokens.access;
      const refresh = res.tokens.refresh;
      localStorage.setItem("token", access);
      localStorage.setItem("refreshToken", refresh);
      setToken(access);
      setRefreshToken(refresh);
      setUser(res.user);
      await fetchConnections();
      return res;
    } catch (err) {
      setError(err.message || "Failed to sign in");
      throw err;
    }
  };

  const signup = async (name, email, password, organizationName) => {
    setError(null);
    try {
      const res = await api.auth.register(name, email, password, organizationName);
      const access = res.tokens.access;
      const refresh = res.tokens.refresh;
      localStorage.setItem("token", access);
      localStorage.setItem("refreshToken", refresh);
      setToken(access);
      setRefreshToken(refresh);
      setUser(res.user);
      await fetchConnections();
      return res;
    } catch (err) {
      setError(err.message || "Failed to register account");
      throw err;
    }
  };

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("refreshToken");
    setToken("");
    setRefreshToken("");
    setUser(null);
    setConnections([]);
    setActiveConnection(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        error,
        connections,
        activeConnection,
        setActiveConnection,
        fetchConnections,
        login,
        signup,
        logout
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return ctx;
};

export default AuthContext;

/**
 * API Service for Text-to-SQL Platform
 * Handles JWT authentication, request interceptors, and typed API endpoints.
 */

const API_BASE = "http://localhost:8000/api";

function getAuthToken() {
  return localStorage.getItem("token") || "";
}

async function request(endpoint, options = {}) {
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {})
  };

  const token = getAuthToken();
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers
  });

  const isJson = response.headers.get("content-type")?.includes("application/json");
  const data = isJson ? await response.json() : await response.text();

  if (!response.ok) {
    const errorMsg = data?.error || data?.detail || (typeof data === "string" ? data : JSON.stringify(data));
    throw new Error(errorMsg || `Request failed with status ${response.status}`);
  }

  return data;
}

export const api = {
  // Auth API
  auth: {
    login: (email, password) =>
      request("/auth/login/", {
        method: "POST",
        body: JSON.stringify({ email, password })
      }),
    register: (name, email, password, organization_name) =>
      request("/auth/register/", {
        method: "POST",
        body: JSON.stringify({ name, email, password, organization_name })
      }),
    me: () => request("/auth/me/"),
    refreshToken: (refresh) =>
      request("/auth/token/refresh/", {
        method: "POST",
        body: JSON.stringify({ refresh })
      })
  },

  // Organizations API
  organizations: {
    getCurrent: () => request("/organizations/current/"),
    updateCurrent: (data) =>
      request("/organizations/current/", {
        method: "PATCH",
        body: JSON.stringify(data)
      }),
    getMembers: () => request("/organizations/members/"),
    addMember: (data) =>
      request("/organizations/members/", {
        method: "POST",
        body: JSON.stringify(data)
      })
  },

  // Database Connections API
  connections: {
    list: () => request("/connections/"),
    create: (data) =>
      request("/connections/", {
        method: "POST",
        body: JSON.stringify(data)
      }),
    get: (id) => request(`/connections/${id}/`),
    update: (id, data) =>
      request(`/connections/${id}/`, {
        method: "PATCH",
        body: JSON.stringify(data)
      }),
    delete: (id) =>
      request(`/connections/${id}/`, {
        method: "DELETE"
      }),
    test: (data) =>
      request("/connections/test/", {
        method: "POST",
        body: JSON.stringify(data)
      }),
    testExisting: (id) =>
      request(`/connections/${id}/test-existing/`, {
        method: "POST"
      }),
    syncSchema: (id) =>
      request(`/connections/${id}/sync-schema/`, {
        method: "POST"
      })
  },

  // Schema Engine API
  schema: {
    get: (connectionId) => request(`/schema/${connectionId}/`),
    previewTable: (connectionId, tableName, limit = 10) =>
      request(`/schema/${connectionId}/tables/${tableName}/preview/?limit=${limit}`)
  },

  // Query Engine API
  query: {
    process: ({ connection_id, question, selected_option, category }) =>
      request("/query/process/", {
        method: "POST",
        body: JSON.stringify({ connection_id, question, selected_option, category })
      }),
    execute: ({ connection_id, sql, question, clarification_log }) =>
      request("/query/execute/", {
        method: "POST",
        body: JSON.stringify({ connection_id, sql, question, clarification_log })
      }),
    explain: ({ question, sql }) =>
      request("/query/explain/", {
        method: "POST",
        body: JSON.stringify({ question, sql })
      })
  },

  // History API
  history: {
    list: (params = {}) => {
      const qs = new URLSearchParams(params).toString();
      return request(`/history/${qs ? `?${qs}` : ""}`);
    },
    getStats: () => request("/history/stats/")
  }
};

export default api;

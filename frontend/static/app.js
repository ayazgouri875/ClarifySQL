// QueryMind Enterprise SaaS Client Application
(function () {
  'use strict';

  // State Management
  const state = {
    token: localStorage.getItem('querymind_access_token') || null,
    refreshToken: localStorage.getItem('querymind_refresh_token') || null,
    user: null,
    org: null,
    connections: [],
    activeConnectionId: localStorage.getItem('querymind_active_conn_id') || null,
    schemaData: null,
    selectedTable: null,
    sessionId: null,
    currentQuestion: '',
    currentResultData: null,
    currentPage: 1,
    pageSize: 10,
    filteredRows: [],
    history: []
  };

  // Safe parse stored user/org
  try {
    const storedUser = localStorage.getItem('querymind_user');
    if (storedUser) state.user = JSON.parse(storedUser);
    const storedOrg = localStorage.getItem('querymind_org');
    if (storedOrg) state.org = JSON.parse(storedOrg);
  } catch (e) {
    console.warn('Error reading stored session:', e);
  }

  // DOM Elements Cache
  const el = {
    // Auth elements
    authOverlay: document.getElementById('authOverlay'),
    tabLogin: document.getElementById('tabLogin'),
    tabSignup: document.getElementById('tabSignup'),
    formLogin: document.getElementById('formLogin'),
    formSignup: document.getElementById('formSignup'),
    authAlert: document.getElementById('authAlert'),
    loginEmail: document.getElementById('loginEmail'),
    loginPassword: document.getElementById('loginPassword'),
    signupName: document.getElementById('signupName'),
    signupEmail: document.getElementById('signupEmail'),
    signupOrg: document.getElementById('signupOrg'),
    signupPassword: document.getElementById('signupPassword'),
    signupConfirmPassword: document.getElementById('signupConfirmPassword'),

    // App Shell & Topbar
    appShell: document.getElementById('appShell'),
    pageHeading: document.getElementById('pageHeading'),
    sidebarOrgName: document.getElementById('sidebarOrgName'),
    sidebarConnName: document.getElementById('sidebarConnName'),
    sidebarEngine: document.getElementById('sidebarEngine'),
    sidebarStatusDot: document.getElementById('sidebarStatusDot'),
    topbarConnSelect: document.getElementById('topbarConnSelect'),
    topbarOrgBadge: document.getElementById('topbarOrgBadge'),
    topbarUserBadge: document.getElementById('topbarUserBadge'),
    btnLogout: document.getElementById('btnLogout'),
    globalAlert: document.getElementById('globalAlert'),

    // Navigation
    navItems: document.querySelectorAll('.nav-item'),
    viewPanels: document.querySelectorAll('.view-panel'),

    // Dashboard View
    metricConnCount: document.getElementById('metricConnCount'),
    metricQueryCount: document.getElementById('metricQueryCount'),
    metricActiveStatus: document.getElementById('metricActiveStatus'),
    metricActiveEngine: document.getElementById('metricActiveEngine'),
    dashboardEmptyNotice: document.getElementById('dashboardEmptyNotice'),
    btnGoToConnections: document.getElementById('btnGoToConnections'),
    btnDashboardNewQuery: document.getElementById('btnDashboardNewQuery'),
    dashboardRecentList: document.getElementById('dashboardRecentList'),

    // Query View
    queryTargetName: document.getElementById('queryTargetName'),
    queryTargetEngine: document.getElementById('queryTargetEngine'),
    btnSwitchConnFromQuery: document.getElementById('btnSwitchConnFromQuery'),
    queryInput: document.getElementById('queryInput'),
    btnExecute: document.getElementById('btnExecute'),
    sampleChips: document.querySelectorAll('.sample-chip'),
    loadingState: document.getElementById('loadingState'),
    loadingMessage: document.getElementById('loadingMessage'),
    clarificationContainer: document.getElementById('clarificationContainer'),
    clarificationQuestion: document.getElementById('clarificationQuestion'),
    clarificationReason: document.getElementById('clarificationReason'),
    clarificationOptions: document.getElementById('clarificationOptions'),
    btnConfirmClarification: document.getElementById('btnConfirmClarification'),
    resultsContainer: document.getElementById('resultsContainer'),
    interpretationBox: document.getElementById('interpretationBox'),
    interpretationText: document.getElementById('interpretationText'),
    summaryCallout: document.getElementById('summaryCallout'),
    sqlDisplay: document.getElementById('sqlDisplay'),
    sqlDialectLabel: document.getElementById('sqlDialectLabel'),
    queryExecTime: document.getElementById('queryExecTime'),
    btnCopySql: document.getElementById('btnCopySql'),
    errorContainer: document.getElementById('errorContainer'),
    errorMessage: document.getElementById('errorMessage'),
    dataTable: document.getElementById('dataTable'),
    tableHead: document.getElementById('tableHead'),
    tableBody: document.getElementById('tableBody'),
    tableStats: document.getElementById('tableStats'),
    tableLimitNotice: document.getElementById('tableLimitNotice'),
    tableSearch: document.getElementById('tableSearch'),
    btnExportCsv: document.getElementById('btnExportCsv'),
    btnPrevPage: document.getElementById('btnPrevPage'),
    btnNextPage: document.getElementById('btnNextPage'),
    pageInfo: document.getElementById('pageInfo'),

    // Connections View
    btnToggleAddConn: document.getElementById('btnToggleAddConn'),
    connFormPanel: document.getElementById('connFormPanel'),
    btnCloseConnForm: document.getElementById('btnCloseConnForm'),
    formAddConnection: document.getElementById('formAddConnection'),
    connName: document.getElementById('connName'),
    connType: document.getElementById('connType'),
    connHost: document.getElementById('connHost'),
    connPort: document.getElementById('connPort'),
    connDbName: document.getElementById('connDbName'),
    connUsername: document.getElementById('connUsername'),
    connPassword: document.getElementById('connPassword'),
    connSsl: document.getElementById('connSsl'),
    btnTestConnInput: document.getElementById('btnTestConnInput'),
    connTestAlert: document.getElementById('connTestAlert'),
    savedConnectionsList: document.getElementById('savedConnectionsList'),

    // Schema View
    schemaTableCountBadge: document.getElementById('schemaTableCountBadge'),
    btnRefreshSchema: document.getElementById('btnRefreshSchema'),
    schemaTableList: document.getElementById('schemaTableList'),
    schemaDetails: document.getElementById('schemaDetails'),

    // History View
    historyList: document.getElementById('historyList'),
    btnRefreshHistory: document.getElementById('btnRefreshHistory'),

    // Settings View
    formUpdateOrg: document.getElementById('formUpdateOrg'),
    settingsOrgName: document.getElementById('settingsOrgName'),
    settingsOrgId: document.getElementById('settingsOrgId'),
    settingsUserName: document.getElementById('settingsUserName'),
    settingsUserRole: document.getElementById('settingsUserRole'),
    settingsUserEmail: document.getElementById('settingsUserEmail'),
    settingsOrgCreated: document.getElementById('settingsOrgCreated')
  };

  // =========================================================================
  // API Fetch Wrapper with JWT and Auto-Refresh
  // =========================================================================
  async function authFetch(url, options = {}) {
    options.headers = options.headers || {};
    if (state.token) {
      options.headers['Authorization'] = `Bearer ${state.token}`;
    }

    let response = await fetch(url, options);

    // If 401 Unauthorized, try refresh token
    if (response.status === 401 && state.refreshToken) {
      try {
        const refreshRes = await fetch('/api/v1/auth/refresh', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ refresh_token: state.refreshToken })
        });

        if (refreshRes.ok) {
          const tokenData = await refreshRes.json();
          saveSession(tokenData);
          // Retry original request with new access token
          options.headers['Authorization'] = `Bearer ${tokenData.access_token}`;
          response = await fetch(url, options);
        } else {
          // Refresh failed - force logout
          clearSession();
          showAuthOverlay();
          return response;
        }
      } catch (e) {
        clearSession();
        showAuthOverlay();
        return response;
      }
    }

    return response;
  }

  // =========================================================================
  // Session & Authentication Handling
  // =========================================================================
  function saveSession(data) {
    if (data.access_token) {
      state.token = data.access_token;
      localStorage.setItem('querymind_access_token', data.access_token);
    }
    if (data.refresh_token) {
      state.refreshToken = data.refresh_token;
      localStorage.setItem('querymind_refresh_token', data.refresh_token);
    }
    if (data.user) {
      state.user = data.user;
      localStorage.setItem('querymind_user', JSON.stringify(data.user));
    }
    if (data.organization) {
      state.org = data.organization;
      localStorage.setItem('querymind_org', JSON.stringify(data.organization));
    }
  }

  function clearSession() {
    state.token = null;
    state.refreshToken = null;
    state.user = null;
    state.org = null;
    localStorage.removeItem('querymind_access_token');
    localStorage.removeItem('querymind_refresh_token');
    localStorage.removeItem('querymind_user');
    localStorage.removeItem('querymind_org');
  }

  function showAuthOverlay() {
    el.authOverlay.style.display = 'flex';
    el.appShell.style.display = 'none';
  }

  function hideAuthOverlay() {
    el.authOverlay.style.display = 'none';
    el.appShell.style.display = 'flex';
    updateUserOrgDisplay();
  }

  function updateUserOrgDisplay() {
    if (state.org) {
      el.sidebarOrgName.textContent = state.org.name || 'Workspace';
      el.topbarOrgBadge.textContent = state.org.name || 'Organization';
      if (el.settingsOrgName) el.settingsOrgName.value = state.org.name || '';
      if (el.settingsOrgId) el.settingsOrgId.value = state.org.id || '';
      if (el.settingsOrgCreated) {
        el.settingsOrgCreated.textContent = state.org.created_at ? new Date(state.org.created_at).toLocaleDateString() : '--';
      }
    }
    if (state.user) {
      const roleStr = (state.user.role || 'member').toUpperCase();
      el.topbarUserBadge.textContent = `${state.user.name} (${roleStr})`;
      if (el.settingsUserName) el.settingsUserName.textContent = state.user.name;
      if (el.settingsUserRole) el.settingsUserRole.textContent = roleStr;
      if (el.settingsUserEmail) el.settingsUserEmail.textContent = state.user.email;
    }
  }

  // =========================================================================
  // View Navigation
  // =========================================================================
  function switchView(viewId) {
    el.navItems.forEach(item => {
      if (item.getAttribute('data-view') === viewId) {
        item.classList.add('active');
      } else {
        item.classList.remove('active');
      }
    });

    el.viewPanels.forEach(panel => {
      if (panel.id === `view-${viewId}`) {
        panel.classList.add('active');
      } else {
        panel.classList.remove('active');
      }
    });

    const headings = {
      dashboard: 'Dashboard',
      query: 'Query Workspace',
      connections: 'Database Connections',
      schema: 'Schema Catalog',
      history: 'Query History',
      settings: 'Organization Settings'
    };
    el.pageHeading.textContent = headings[viewId] || 'Workspace';

    // Refresh context depending on view
    if (viewId === 'dashboard') loadDashboard();
    if (viewId === 'connections') loadConnections();
    if (viewId === 'schema') loadSchema();
    if (viewId === 'history') loadHistory();
    if (viewId === 'query') updateQueryTargetBanner();
  }

  // =========================================================================
  // Connections Management
  // =========================================================================
  async function loadConnections() {
    try {
      const res = await authFetch('/api/v1/connections');
      if (res.ok) {
        state.connections = await res.json();
        renderConnectionsList();
        renderConnectionSelector();
        updateActiveConnectionUI();
      } else if (res.status === 401) {
        showAuthOverlay();
      }
    } catch (e) {
      console.warn('Failed to load connections:', e);
    }
  }

  function getActiveConnection() {
    if (!state.connections || state.connections.length === 0) return null;
    if (state.activeConnectionId) {
      const found = state.connections.find(c => c.id === state.activeConnectionId);
      if (found) return found;
    }
    // Default to first connection
    return state.connections[0];
  }

  function setActiveConnection(connId) {
    state.activeConnectionId = connId;
    localStorage.setItem('querymind_active_conn_id', connId);
    updateActiveConnectionUI();
    renderConnectionsList();
    renderConnectionSelector();
    loadSchema();
  }

  function updateActiveConnectionUI() {
    const active = getActiveConnection();
    if (active) {
      el.sidebarConnName.textContent = active.name;
      el.sidebarEngine.textContent = `${active.db_type.toUpperCase()} (Read-Only)`;
      el.sidebarStatusDot.style.backgroundColor = '#16a34a';

      el.metricActiveStatus.textContent = active.name;
      el.metricActiveStatus.style.color = '#1e3a8a';
      el.metricActiveEngine.textContent = `${active.db_type.toUpperCase()} • ${active.host || 'local'}`;

      el.queryTargetName.textContent = active.name;
      el.queryTargetEngine.textContent = `${active.db_type.toUpperCase()} (Read-Only)`;
      if (el.sqlDialectLabel) {
        el.sqlDialectLabel.textContent = `${active.db_type.toUpperCase()} READ-ONLY`;
      }
    } else {
      el.sidebarConnName.textContent = 'No Connection';
      el.sidebarEngine.textContent = 'SELECT-Only Engine';
      el.sidebarStatusDot.style.backgroundColor = '#94a3b8';

      el.metricActiveStatus.textContent = 'None';
      el.metricActiveStatus.style.color = 'var(--text-muted)';
      el.metricActiveEngine.textContent = 'Connect a database to query';

      el.queryTargetName.textContent = 'No Connection Selected';
      el.queryTargetEngine.textContent = 'Demo Database';
    }
    updateQueryTargetBanner();
  }

  function updateQueryTargetBanner() {
    const active = getActiveConnection();
    if (active) {
      el.queryTargetName.textContent = active.name;
      el.queryTargetEngine.textContent = `${active.db_type.toUpperCase()} (Read-Only)`;
    } else {
      el.queryTargetName.textContent = 'No Connected Database';
      el.queryTargetEngine.textContent = 'Demo SQLite';
    }
  }

  function renderConnectionSelector() {
    el.topbarConnSelect.innerHTML = '';
    if (!state.connections || state.connections.length === 0) {
      const opt = document.createElement('option');
      opt.value = '';
      opt.textContent = '-- No Connected Database --';
      el.topbarConnSelect.appendChild(opt);
      return;
    }

    state.connections.forEach(c => {
      const opt = document.createElement('option');
      opt.value = c.id;
      opt.textContent = `${c.name} (${c.db_type.toUpperCase()})`;
      if (c.id === (state.activeConnectionId || state.connections[0].id)) {
        opt.selected = true;
      }
      el.topbarConnSelect.appendChild(opt);
    });
  }

  function renderConnectionsList() {
    if (!el.savedConnectionsList) return;

    if (!state.connections || state.connections.length === 0) {
      el.savedConnectionsList.innerHTML = `
        <div style="grid-column: 1 / -1; padding: 24px; text-align: center; background: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: var(--radius-md);">
          <div style="font-weight: 600; margin-bottom: 6px;">No database connections configured</div>
          <div style="font-size: 13px; color: var(--text-muted); margin-bottom: 14px;">Add a PostgreSQL, MySQL, or relational database to start querying your organization's data.</div>
          <button class="btn btn-primary btn-sm" onclick="document.getElementById('btnToggleAddConn').click()">+ Add Connection</button>
        </div>
      `;
      return;
    }

    const active = getActiveConnection();
    el.savedConnectionsList.innerHTML = state.connections.map(c => {
      const isActive = active && active.id === c.id;
      return `
        <div class="conn-card ${isActive ? 'active-conn' : ''}" data-id="${c.id}">
          <div class="conn-card-header">
            <div>
              <div class="conn-card-title">${escapeHtml(c.name)}</div>
              <div style="margin-top: 4px;">
                <span class="conn-meta-tag">${c.db_type.toUpperCase()}</span>
                ${isActive ? '<span class="status-badge badge-success" style="margin-left: 6px;">Active</span>' : ''}
              </div>
            </div>
            <span class="status-indicator" style="background-color: ${c.has_schema ? '#16a34a' : '#d97706'};"></span>
          </div>

          <div class="conn-details-list">
            <div><strong>Host:</strong> ${escapeHtml(c.host || 'local')}:${c.port || 0}</div>
            <div><strong>Database:</strong> ${escapeHtml(c.database_name)}</div>
            <div><strong>User:</strong> ${escapeHtml(c.username)}</div>
            <div><strong>SSL:</strong> ${c.ssl_enabled ? 'Enabled' : 'Disabled'}</div>
            <div><strong>Schema:</strong> ${c.has_schema ? 'Introspected & Cached' : 'Not Loaded'}</div>
          </div>

          <div class="conn-card-actions">
            ${!isActive ? `<button class="btn btn-secondary btn-sm btn-set-active" data-id="${c.id}">Set Active</button>` : ''}
            <button class="btn btn-secondary btn-sm btn-test-conn" data-id="${c.id}">Test Connectivity</button>
            <button class="btn btn-secondary btn-sm btn-load-schema" data-id="${c.id}">Inspect Schema</button>
            <button class="btn btn-secondary btn-sm btn-delete-conn" data-id="${c.id}" style="color: #991b1b; margin-left: auto;">Delete</button>
          </div>
        </div>
      `;
    }).join('');

    // Attach actions
    el.savedConnectionsList.querySelectorAll('.btn-set-active').forEach(b => {
      b.addEventListener('click', () => setActiveConnection(b.getAttribute('data-id')));
    });

    el.savedConnectionsList.querySelectorAll('.btn-test-conn').forEach(b => {
      b.addEventListener('click', () => handleTestSavedConnection(b.getAttribute('data-id'), b));
    });

    el.savedConnectionsList.querySelectorAll('.btn-load-schema').forEach(b => {
      b.addEventListener('click', () => {
        setActiveConnection(b.getAttribute('data-id'));
        switchView('schema');
      });
    });

    el.savedConnectionsList.querySelectorAll('.btn-delete-conn').forEach(b => {
      b.addEventListener('click', () => handleDeleteConnection(b.getAttribute('data-id')));
    });
  }

  async function handleTestSavedConnection(connId, buttonEl) {
    const origText = buttonEl.textContent;
    buttonEl.textContent = 'Testing...';
    buttonEl.disabled = true;

    try {
      const res = await authFetch(`/api/v1/connections/${connId}/test`, { method: 'POST' });
      const data = await res.json();
      if (res.ok) {
        showGlobalAlert(data.message || 'Connection is healthy and reachable.', 'success');
      } else {
        showGlobalAlert(data.detail || 'Connection test failed.', 'error');
      }
    } catch (e) {
      showGlobalAlert(`Network error: ${e.message}`, 'error');
    } finally {
      buttonEl.textContent = origText;
      buttonEl.disabled = false;
    }
  }

  async function handleDeleteConnection(connId) {
    if (!confirm('Are you sure you want to delete this database connection?')) return;
    try {
      const res = await authFetch(`/api/v1/connections/${connId}`, { method: 'DELETE' });
      if (res.ok) {
        if (state.activeConnectionId === connId) {
          state.activeConnectionId = null;
          localStorage.removeItem('querymind_active_conn_id');
        }
        await loadConnections();
        showGlobalAlert('Database connection deleted.', 'success');
      } else {
        const data = await res.json();
        showGlobalAlert(data.detail || 'Failed to delete connection.', 'error');
      }
    } catch (e) {
      showGlobalAlert(`Error: ${e.message}`, 'error');
    }
  }

  // =========================================================================
  // Dashboard Logic
  // =========================================================================
  async function loadDashboard() {
    try {
      const [orgRes, connsRes, histRes] = await Promise.all([
        authFetch('/api/v1/organization'),
        authFetch('/api/v1/connections'),
        authFetch('/api/v1/history?limit=5')
      ]);

      if (orgRes.ok) {
        state.org = await orgRes.json();
        updateUserOrgDisplay();
      }

      if (connsRes.ok) {
        state.connections = await connsRes.json();
        el.metricConnCount.textContent = state.connections.length;
        if (state.connections.length === 0) {
          el.dashboardEmptyNotice.style.display = 'block';
        } else {
          el.dashboardEmptyNotice.style.display = 'none';
        }
        updateActiveConnectionUI();
        renderConnectionSelector();
      }

      if (histRes.ok) {
        const recent = await histRes.json();
        el.metricQueryCount.textContent = recent.length;
        renderDashboardRecent(recent);
      }
    } catch (e) {
      console.warn('Dashboard loading warning:', e);
    }
  }

  function renderDashboardRecent(recent) {
    if (!el.dashboardRecentList) return;
    if (!recent || recent.length === 0) {
      el.dashboardRecentList.innerHTML = '<div style="color: var(--text-muted); font-size: 13px;">No queries executed in your workspace yet.</div>';
      return;
    }

    el.dashboardRecentList.innerHTML = recent.map(item => `
      <div class="history-card" style="cursor: pointer;" onclick="window.QueryMind.loadHistoryQuery('${escapeHtml(item.natural_language_query)}')">
        <div style="flex: 1;">
          <div class="history-q">${escapeHtml(item.natural_language_query)}</div>
          <div class="history-meta">
            <span>${new Date(item.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
            <span>Rows: ${item.row_count || 0}</span>
            <span>Time: ${item.execution_time_ms ? item.execution_time_ms.toFixed(1) + 'ms' : '--'}</span>
          </div>
        </div>
        <span class="status-badge ${item.execution_status === 'success' ? 'badge-success' : 'badge-error'}">
          ${item.execution_status.toUpperCase()}
        </span>
      </div>
    `).join('');
  }

  // =========================================================================
  // Schema Catalog
  // =========================================================================
  async function loadSchema() {
    const active = getActiveConnection();
    if (!active) {
      el.schemaTableList.innerHTML = '<div style="padding: 14px; font-size: 12px; color: var(--text-muted);">Please connect a database first.</div>';
      el.schemaDetails.innerHTML = '<div style="color: var(--text-muted); font-size: 13px;">No database selected.</div>';
      el.schemaTableCountBadge.textContent = '0 Tables';
      return;
    }

    try {
      const res = await authFetch(`/api/v1/connections/${active.id}/schema`);
      if (res.ok) {
        state.schemaData = await res.json();
        renderSchemaCatalog();
      } else {
        const err = await res.json();
        el.schemaDetails.innerHTML = `<div class="status-badge badge-error" style="padding: 10px; width: 100%;">${escapeHtml(err.detail || 'Failed to inspect schema.')}</div>`;
      }
    } catch (e) {
      console.warn('Schema fetch error:', e);
    }
  }

  function renderSchemaCatalog() {
    if (!state.schemaData || !state.schemaData.tables) {
      el.schemaTableList.innerHTML = '<div style="padding: 14px; font-size: 12px; color: var(--text-muted);">No schema tables found.</div>';
      return;
    }

    const tableNames = Object.keys(state.schemaData.tables).sort();
    el.schemaTableCountBadge.textContent = `${tableNames.length} Tables`;

    el.schemaTableList.innerHTML = tableNames.map(tbl => `
      <div class="table-list-item ${state.selectedTable === tbl ? 'selected' : ''}" data-table="${tbl}">
        ${tbl}
      </div>
    `).join('');

    // Attach table select clicks
    el.schemaTableList.querySelectorAll('.table-list-item').forEach(item => {
      item.addEventListener('click', () => {
        const tblName = item.getAttribute('data-table');
        state.selectedTable = tblName;
        renderSchemaCatalog();
        renderTableDetails(tblName);
      });
    });

    if (tableNames.length > 0) {
      if (!state.selectedTable || !state.schemaData.tables[state.selectedTable]) {
        state.selectedTable = tableNames[0];
      }
      renderTableDetails(state.selectedTable);
    }
  }

  function renderTableDetails(tblName) {
    const tbl = state.schemaData.tables[tblName];
    if (!tbl) return;

    const cols = tbl.columns || {};
    const colKeys = Object.keys(cols);
    const fks = tbl.foreign_keys || [];

    el.schemaDetails.innerHTML = `
      <div class="schema-table-title">${tblName}</div>
      <div class="schema-table-desc">${escapeHtml(tbl.description || `Table '${tblName}' with ${colKeys.length} columns`)}</div>

      <div style="font-size: 13px; font-weight: 600; text-transform: uppercase; color: var(--text-secondary); margin-bottom: 8px;">
        Columns &amp; Attributes (${colKeys.length})
      </div>
      <table class="data-table" style="margin-bottom: 20px;">
        <thead>
          <tr>
            <th>Column Name</th>
            <th>Type</th>
            <th>Constraints</th>
          </tr>
        </thead>
        <tbody>
          ${colKeys.map(c => {
            const col = cols[c];
            const isPk = tbl.primary_key === c || (col.description && col.description.includes('Primary Key'));
            return `
              <tr>
                <td style="font-family: var(--font-mono); font-weight: 600;">
                  ${c} ${isPk ? '<span class="status-badge badge-warning" style="font-size: 10px; margin-left: 4px;">PK</span>' : ''}
                </td>
                <td style="font-family: var(--font-mono); color: var(--text-muted);">${escapeHtml(col.type || 'TEXT')}</td>
                <td style="font-size: 12px; color: var(--text-secondary);">${escapeHtml(col.description || 'Nullable')}</td>
              </tr>
            `;
          }).join('')}
        </tbody>
      </table>

      ${fks.length > 0 ? `
        <div style="font-size: 13px; font-weight: 600; text-transform: uppercase; color: var(--text-secondary); margin-bottom: 8px;">
          Foreign Key Relationships (${fks.length})
        </div>
        <ul style="font-size: 13px; color: var(--text-secondary); padding-left: 18px; line-height: 1.6;">
          ${fks.map(fk => `
            <li>
              <code style="font-family: var(--font-mono);">${fk.column}</code>
              &rarr;
              <code style="font-family: var(--font-mono);">${fk.references_table}.${fk.references_column}</code>
            </li>
          `).join('')}
        </ul>
      ` : ''}
    `;
  }

  // =========================================================================
  // Query Execution & Clarification Flow
  // =========================================================================
  async function handleExecuteQuery() {
    const question = el.queryInput.value.trim();
    if (!question) return;

    const active = getActiveConnection();
    state.currentQuestion = question;
    resetQueryUI();
    showLoading(true, 'Analyzing query intent and inspecting schema...');

    try {
      const res = await authFetch('/api/v1/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: state.sessionId,
          question: question,
          connection_id: active ? active.id : null
        })
      });

      const data = await res.json();
      showLoading(false);

      if (!res.ok) {
        renderError(data.detail || data.error_message || 'An error occurred during query execution.');
        return;
      }

      state.sessionId = data.session_id;

      if (data.status === 'clarification_required') {
        renderClarification(data.clarification);
      } else if (data.status === 'success') {
        renderSuccess(data);
      } else {
        renderError(data.error_message || 'Query execution did not complete successfully.');
      }
    } catch (err) {
      showLoading(false);
      renderError(`Network request failure: ${err.message}`);
    }
  }

  async function handleClarificationSubmit() {
    const selected = document.querySelector('input[name="clarificationOption"]:checked');
    if (!selected) {
      alert('Please select an option to continue.');
      return;
    }

    const selectedOption = selected.value;
    const active = getActiveConnection();
    el.clarificationContainer.style.display = 'none';
    showLoading(true, 'Synthesizing resolved intent and generating verified SQL...');

    try {
      const res = await authFetch('/api/v1/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: state.sessionId,
          question: state.currentQuestion,
          connection_id: active ? active.id : null,
          selected_clarification: selectedOption
        })
      });

      const data = await res.json();
      showLoading(false);

      if (!res.ok) {
        renderError(data.detail || data.error_message || 'Failed to resolve intent.');
        return;
      }

      if (data.status === 'success') {
        renderSuccess(data);
      } else {
        renderError(data.error_message || 'Could not resolve clarification.');
      }
    } catch (err) {
      showLoading(false);
      renderError(`Error during clarification: ${err.message}`);
    }
  }

  function renderClarification(clarification) {
    if (!clarification) return;
    el.clarificationQuestion.textContent = clarification.question;
    el.clarificationReason.textContent = clarification.ambiguity_reason || 'Clarification is needed to correctly map this business query to the database schema.';

    el.clarificationOptions.innerHTML = (clarification.options || []).map((opt, idx) => `
      <label class="radio-card">
        <input type="radio" name="clarificationOption" value="${escapeHtml(opt)}" ${idx === 0 ? 'checked' : ''} />
        <span class="radio-label">${escapeHtml(opt)}</span>
      </label>
    `).join('');

    el.clarificationContainer.style.display = 'block';
  }

  function renderSuccess(data) {
    el.resultsContainer.style.display = 'block';

    if (data.clarification && data.clarification.selected_option) {
      el.interpretationBox.style.display = 'block';
      el.interpretationText.textContent = data.clarification.selected_option;
    } else {
      el.interpretationBox.style.display = 'none';
    }

    if (data.explanation) {
      el.summaryCallout.style.display = 'block';
      el.summaryCallout.textContent = data.explanation;
    } else {
      el.summaryCallout.style.display = 'none';
    }

    if (data.generated_sql) {
      el.sqlDisplay.textContent = data.generated_sql;
    }

    if (data.data) {
      const execTime = data.data.execution_time_ms ? data.data.execution_time_ms.toFixed(1) + ' ms' : '< 1 ms';
      el.queryExecTime.textContent = execTime;
      state.currentResultData = data.data;
      state.filteredRows = data.data.rows || [];
      state.currentPage = 1;
      renderTable();
    }
  }

  function renderTable() {
    if (!state.currentResultData) return;
    const cols = state.currentResultData.columns || [];
    const rows = state.filteredRows || [];

    el.tableHead.innerHTML = `<tr>${cols.map(c => `<th>${escapeHtml(c)}</th>`).join('')}</tr>`;
    el.tableStats.textContent = `${rows.length} rows returned`;

    renderTablePage();
  }

  function renderTablePage() {
    const rows = state.filteredRows || [];
    const start = (state.currentPage - 1) * state.pageSize;
    const end = Math.min(start + state.pageSize, rows.length);
    const pageRows = rows.slice(start, end);

    if (pageRows.length === 0) {
      el.tableBody.innerHTML = `<tr><td colspan="100" style="text-align: center; color: var(--text-muted); padding: 18px;">No matching rows found.</td></tr>`;
    } else {
      el.tableBody.innerHTML = pageRows.map(r => `
        <tr>
          ${r.map(v => {
            const isNum = typeof v === 'number';
            return `<td class="${isNum ? 'td-number' : ''}">${escapeHtml(v !== null ? String(v) : 'NULL')}</td>`;
          }).join('')}
        </tr>
      `).join('');
    }

    el.pageInfo.textContent = rows.length > 0 ? `Showing ${start + 1} to ${end} of ${rows.length}` : '0 results';
    el.btnPrevPage.disabled = state.currentPage <= 1;
    el.btnNextPage.disabled = end >= rows.length;
  }

  function handleTableSearch() {
    const q = el.tableSearch.value.toLowerCase().trim();
    if (!state.currentResultData) return;
    const allRows = state.currentResultData.rows || [];

    if (!q) {
      state.filteredRows = allRows;
    } else {
      state.filteredRows = allRows.filter(row =>
        row.some(val => val !== null && String(val).toLowerCase().includes(q))
      );
    }
    state.currentPage = 1;
    renderTablePage();
  }

  function exportToCsv() {
    if (!state.currentResultData) return;
    const cols = state.currentResultData.columns || [];
    const rows = state.filteredRows || [];
    if (rows.length === 0) return;

    let csv = cols.join(',') + '\n';
    rows.forEach(r => {
      const line = r.map(v => {
        if (v === null) return '';
        const str = String(v).replace(/"/g, '""');
        return `"${str}"`;
      }).join(',');
      csv += line + '\n';
    });

    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `query_result_${new Date().toISOString().slice(0, 10)}.csv`;
    link.click();
  }

  function resetQueryUI() {
    el.resultsContainer.style.display = 'none';
    el.clarificationContainer.style.display = 'none';
    el.errorContainer.style.display = 'none';
    el.errorMessage.textContent = '';
  }

  function showLoading(show, message = '') {
    el.loadingState.style.display = show ? 'flex' : 'none';
    if (message) el.loadingMessage.textContent = message;
    el.btnExecute.disabled = show;
  }

  function renderError(message) {
    el.errorContainer.style.display = 'block';
    el.errorMessage.textContent = message;
  }

  // =========================================================================
  // Query History
  // =========================================================================
  async function loadHistory() {
    try {
      const res = await authFetch('/api/v1/history?limit=50');
      if (res.ok) {
        state.history = await res.json();
        renderHistoryList();
      }
    } catch (e) {
      console.warn('History fetch error:', e);
    }
  }

  function renderHistoryList() {
    if (!el.historyList) return;
    if (!state.history || state.history.length === 0) {
      el.historyList.innerHTML = '<div style="color: var(--text-muted); font-size: 13px;">No queries executed in your organization yet.</div>';
      return;
    }

    el.historyList.innerHTML = state.history.map(item => `
      <div class="history-card" style="align-items: flex-start;">
        <div style="flex: 1;">
          <div class="history-q">${escapeHtml(item.natural_language_query)}</div>
          ${item.resolved_intent ? `<div style="font-size: 12px; color: #1e3a8a; margin-bottom: 4px;">Intent: ${escapeHtml(item.resolved_intent)}</div>` : ''}
          <div class="code-container" style="margin: 6px 0; max-height: 80px; overflow: hidden;">
            <div class="code-block" style="padding: 6px 10px; font-size: 11px;">${escapeHtml(item.generated_sql || '')}</div>
          </div>
          <div class="history-meta">
            <span>${new Date(item.created_at).toLocaleString()}</span>
            <span>Rows: ${item.row_count || 0}</span>
            <span>Latency: ${item.execution_time_ms ? item.execution_time_ms.toFixed(1) + 'ms' : '--'}</span>
          </div>
        </div>
        <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 6px;">
          <span class="status-badge ${item.execution_status === 'success' ? 'badge-success' : 'badge-error'}">
            ${item.execution_status.toUpperCase()}
          </span>
          <button class="btn btn-secondary btn-sm" onclick="window.QueryMind.loadHistoryQuery('${escapeHtml(item.natural_language_query)}')">Re-run</button>
        </div>
      </div>
    `).join('');
  }

  // =========================================================================
  // Global Alert
  // =========================================================================
  function showGlobalAlert(msg, type = 'info') {
    el.globalAlert.className = `status-badge ${type === 'success' ? 'badge-success' : type === 'error' ? 'badge-error' : 'badge-warning'}`;
    el.globalAlert.textContent = msg;
    el.globalAlert.style.display = 'block';
    setTimeout(() => {
      el.globalAlert.style.display = 'none';
    }, 4500);
  }

  function escapeHtml(str) {
    if (str === null || str === undefined) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // Expose helper on window for inline event triggers
  window.QueryMind = {
    loadHistoryQuery: function (q) {
      switchView('query');
      el.queryInput.value = q;
      handleExecuteQuery();
    }
  };

  // =========================================================================
  // Event Listeners Setup
  // =========================================================================
  function setupEventListeners() {
    // Auth Tabs
    el.tabLogin.addEventListener('click', () => {
      el.tabLogin.classList.add('active');
      el.tabSignup.classList.remove('active');
      el.formLogin.style.display = 'flex';
      el.formSignup.style.display = 'none';
      el.authAlert.style.display = 'none';
    });

    el.tabSignup.addEventListener('click', () => {
      el.tabSignup.classList.add('active');
      el.tabLogin.classList.remove('active');
      el.formSignup.style.display = 'flex';
      el.formLogin.style.display = 'none';
      el.authAlert.style.display = 'none';
    });

    // Login Form Submit
    el.formLogin.addEventListener('submit', async (e) => {
      e.preventDefault();
      el.authAlert.style.display = 'none';
      const email = el.loginEmail.value.trim();
      const password = el.loginPassword.value;

      try {
        const res = await fetch('/api/v1/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password })
        });
        const data = await res.json();
        if (res.ok) {
          saveSession(data);
          hideAuthOverlay();
          await initApp();
        } else {
          el.authAlert.textContent = data.detail || 'Invalid email or password.';
          el.authAlert.style.display = 'block';
        }
      } catch (err) {
        el.authAlert.textContent = `Login failed: ${err.message}`;
        el.authAlert.style.display = 'block';
      }
    });

    // Signup Form Submit
    el.formSignup.addEventListener('submit', async (e) => {
      e.preventDefault();
      el.authAlert.style.display = 'none';
      const name = el.signupName.value.trim();
      const email = el.signupEmail.value.trim();
      const organization_name = el.signupOrg.value.trim();
      const password = el.signupPassword.value;
      const confirmPassword = el.signupConfirmPassword.value;

      if (password !== confirmPassword) {
        el.authAlert.textContent = 'Passwords do not match.';
        el.authAlert.style.display = 'block';
        return;
      }

      try {
        const res = await fetch('/api/v1/auth/signup', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name, email, organization_name, password })
        });
        const data = await res.json();
        if (res.ok) {
          saveSession(data);
          hideAuthOverlay();
          await initApp();
          showGlobalAlert(`Welcome to ${organization_name}! Workspace initialized successfully.`, 'success');
        } else {
          el.authAlert.textContent = data.detail || 'Could not register workspace.';
          el.authAlert.style.display = 'block';
        }
      } catch (err) {
        el.authAlert.textContent = `Registration error: ${err.message}`;
        el.authAlert.style.display = 'block';
      }
    });

    // Sign Out
    el.btnLogout.addEventListener('click', async () => {
      try {
        await authFetch('/api/v1/auth/logout', { method: 'POST' });
      } catch (e) {}
      clearSession();
      showAuthOverlay();
    });

    // Navigation Items
    el.navItems.forEach(item => {
      item.addEventListener('click', () => {
        const viewId = item.getAttribute('data-view');
        switchView(viewId);
      });
    });

    // Topbar Connection Selector Change
    el.topbarConnSelect.addEventListener('change', (e) => {
      const selectedId = e.target.value;
      if (selectedId) {
        setActiveConnection(selectedId);
      }
    });

    // Dashboard Quick Actions
    el.btnGoToConnections.addEventListener('click', () => switchView('connections'));
    el.btnDashboardNewQuery.addEventListener('click', () => switchView('query'));
    el.btnSwitchConnFromQuery.addEventListener('click', () => switchView('connections'));

    // Query Actions
    el.btnExecute.addEventListener('click', handleExecuteQuery);
    el.queryInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') handleExecuteQuery();
    });

    el.sampleChips.forEach(chip => {
      chip.addEventListener('click', () => {
        el.queryInput.value = chip.getAttribute('data-query');
        handleExecuteQuery();
      });
    });

    el.btnConfirmClarification.addEventListener('click', handleClarificationSubmit);

    el.btnCopySql.addEventListener('click', () => {
      const sql = el.sqlDisplay.textContent;
      if (sql) {
        navigator.clipboard.writeText(sql);
        const originalText = el.btnCopySql.textContent;
        el.btnCopySql.textContent = 'Copied';
        setTimeout(() => { el.btnCopySql.textContent = originalText; }, 1500);
      }
    });

    el.tableSearch.addEventListener('input', handleTableSearch);
    el.btnExportCsv.addEventListener('click', exportToCsv);

    el.btnPrevPage.addEventListener('click', () => {
      if (state.currentPage > 1) {
        state.currentPage--;
        renderTablePage();
      }
    });

    el.btnNextPage.addEventListener('click', () => {
      const maxPages = Math.ceil(state.filteredRows.length / state.pageSize);
      if (state.currentPage < maxPages) {
        state.currentPage++;
        renderTablePage();
      }
    });

    // Connection Form Toggle
    el.btnToggleAddConn.addEventListener('click', () => {
      const isVisible = el.connFormPanel.style.display === 'block';
      el.connFormPanel.style.display = isVisible ? 'none' : 'block';
      if (!isVisible) {
        el.connFormPanel.scrollIntoView({ behavior: 'smooth' });
      }
    });

    el.btnCloseConnForm.addEventListener('click', () => {
      el.connFormPanel.style.display = 'none';
      el.connTestAlert.style.display = 'none';
    });

    // DB Type Change updates default port
    el.connType.addEventListener('change', () => {
      const type = el.connType.value;
      if (type === 'postgresql') el.connPort.value = '5432';
      else if (type === 'mysql') el.connPort.value = '3306';
      else if (type === 'sqlite') el.connPort.value = '0';
    });

    // Test Unsaved Connection
    el.btnTestConnInput.addEventListener('click', async () => {
      el.connTestAlert.style.display = 'none';
      const origText = el.btnTestConnInput.textContent;
      el.btnTestConnInput.textContent = 'Testing...';
      el.btnTestConnInput.disabled = true;

      const payload = {
        name: el.connName.value.trim() || 'Test Connection',
        db_type: el.connType.value,
        host: el.connHost.value.trim(),
        port: parseInt(el.connPort.value) || 0,
        database_name: el.connDbName.value.trim(),
        username: el.connUsername.value.trim(),
        password: el.connPassword.value,
        ssl_enabled: el.connSsl.checked
      };

      try {
        const res = await authFetch('/api/v1/connections/test', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (res.ok) {
          el.connTestAlert.className = 'status-badge badge-success';
          el.connTestAlert.textContent = '✓ ' + (data.message || 'Connection test successful.');
          el.connTestAlert.style.display = 'block';
        } else {
          el.connTestAlert.className = 'status-badge badge-error';
          el.connTestAlert.textContent = '✕ ' + (data.detail || 'Connection test failed.');
          el.connTestAlert.style.display = 'block';
        }
      } catch (e) {
        el.connTestAlert.className = 'status-badge badge-error';
        el.connTestAlert.textContent = `✕ Network error: ${e.message}`;
        el.connTestAlert.style.display = 'block';
      } finally {
        el.btnTestConnInput.textContent = origText;
        el.btnTestConnInput.disabled = false;
      }
    });

    // Save Connection Submit
    el.formAddConnection.addEventListener('submit', async (e) => {
      e.preventDefault();
      const payload = {
        name: el.connName.value.trim(),
        db_type: el.connType.value,
        host: el.connHost.value.trim(),
        port: parseInt(el.connPort.value) || 0,
        database_name: el.connDbName.value.trim(),
        username: el.connUsername.value.trim(),
        password: el.connPassword.value,
        ssl_enabled: el.connSsl.checked
      };

      try {
        const res = await authFetch('/api/v1/connections', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (res.ok) {
          showGlobalAlert(`Connection '${data.name}' saved and schema introspected!`, 'success');
          el.formAddConnection.reset();
          el.connFormPanel.style.display = 'none';
          el.connTestAlert.style.display = 'none';
          await loadConnections();
          setActiveConnection(data.id);
        } else {
          el.connTestAlert.className = 'status-badge badge-error';
          el.connTestAlert.textContent = data.detail || 'Failed to save connection.';
          el.connTestAlert.style.display = 'block';
        }
      } catch (e) {
        showGlobalAlert(`Error: ${e.message}`, 'error');
      }
    });

    // Schema Refresh
    el.btnRefreshSchema.addEventListener('click', async () => {
      const active = getActiveConnection();
      if (!active) return;
      try {
        const res = await authFetch(`/api/v1/connections/${active.id}/schema`, { method: 'POST' });
        if (res.ok) {
          state.schemaData = await res.json();
          renderSchemaCatalog();
          showGlobalAlert('Schema catalog synchronized with database.', 'success');
        }
      } catch (e) {
        showGlobalAlert(`Failed to refresh schema: ${e.message}`, 'error');
      }
    });

    // History Refresh
    el.btnRefreshHistory.addEventListener('click', loadHistory);

    // Settings Org Name Update
    el.formUpdateOrg.addEventListener('submit', async (e) => {
      e.preventDefault();
      const newName = el.settingsOrgName.value.trim();
      if (!newName) return;
      try {
        const res = await authFetch('/api/v1/organization', {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name: newName })
        });
        if (res.ok) {
          state.org = await res.json();
          updateUserOrgDisplay();
          showGlobalAlert('Organization settings updated successfully.', 'success');
        } else {
          const err = await res.json();
          showGlobalAlert(err.detail || 'Could not update organization.', 'error');
        }
      } catch (e) {
        showGlobalAlert(`Error: ${e.message}`, 'error');
      }
    });
  }

  // =========================================================================
  // Application Bootstrap
  // =========================================================================
  async function initApp() {
    if (!state.token) {
      showAuthOverlay();
      return;
    }

    try {
      // Validate session with /auth/me
      const meRes = await authFetch('/api/v1/auth/me');
      if (meRes.ok) {
        const meData = await meRes.json();
        state.user = meData.user;
        state.org = meData.organization;
        saveSession(meData);
        hideAuthOverlay();
        await loadConnections();
        await loadDashboard();
      } else {
        clearSession();
        showAuthOverlay();
      }
    } catch (e) {
      console.warn('Init session error:', e);
      clearSession();
      showAuthOverlay();
    }
  }

  // Run on DOM ready
  document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    initApp();
  });
})();

/**
 * api.js — HTTP client — NO fallback demo data
 * كل حاجة بترجع من الباك إند الحقيقي
 */

const API = (() => {
  /** Shared fetch wrapper with auth header */
  async function req(method, path, body = null) {
    const token = sessionStorage.getItem('authToken');
    const opts = {
      method,
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
    };
    if (body !== null) opts.body = JSON.stringify(body);

    const res = await fetch(`${CONFIG.API_BASE}${path}`, opts);
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || `API error ${res.status}`);
    }
    return res.status === 204 ? null : res.json();
  }

  const get  = path        => req('GET',    path);
  const post = (path, b)   => req('POST',   path, b);
  const put  = (path, b)   => req('PUT',    path, b);
  const del  = path        => req('DELETE', path);

  /* ---- Auth ---- */
  async function login(email, password) {
    const data = await post('/auth/login', { email, password });
    sessionStorage.setItem('authToken', data.access_token);
    return data.user;
  }

  function logout() {
    sessionStorage.removeItem('authToken');
    sessionStorage.removeItem(CONFIG.SESSION_KEY);
  }

  /* ---- Customers ---- */
  const getCustomers    = (p = {}) => get(`/customers${new URLSearchParams(p).toString() ? '?' + new URLSearchParams(p) : ''}`);
  const updateCustomer  = (id, patch) => put(`/customers/${id}`, patch);

  /* ---- Chats ---- */
  const getChats        = ()           => get('/chats');
  const getChat         = id           => get(`/chats/${id}`);
  const sendMessage     = (id, text)   => post(`/chats/${id}/messages`, { text });

  /* ---- Approvals ---- */
  const getApprovals    = (status)     => get(`/approvals${status ? '?status=' + status : ''}`);
  const approveItem     = (id, text)   => post(`/approvals/${id}/approve`, { text: text || null });
  const rejectItem      = id           => post(`/approvals/${id}/reject`, {});

  /* ---- Campaigns ---- */
  const getCampaigns    = ()           => get('/campaigns');
  const getTemplates    = ()           => get('/campaigns/templates');
  const createTemplate  = tpl          => post('/campaigns/templates', tpl);
  const approveTemplate = id           => put(`/campaigns/templates/${id}/approve`, {});

  /* ---- Projects ---- */
  const getProjects     = ()           => get('/projects');

  /* ---- Appointments ---- */
  const getAppointments    = ()  => get('/appointments');
  const confirmAppointment = id  => post(`/appointments/${id}/confirm`, {});

  /* ---- Recommendations ---- */
  const getRecommendations    = ()   => get('/webhook/insights/recommendations');
  const applyRecommendation   = id   => post(`/webhook/insights/recommendations/${id}/apply`, {});

  /* ---- Knowledge base ---- */
  const getKB         = ()       => get('/settings/kb');
  const addKBEntry    = entry    => post('/settings/kb', entry);
  const deleteKBEntry = id       => del(`/settings/kb/${id}`);

  /* ---- Agent settings ---- */
  const getSettings       = ()       => get('/settings/agent');
  const saveSettings      = patch    => put('/settings/agent', patch);
  const toggleConnection  = (k, v)   => put(`/settings/connections/${k}`, { connected: v });
  const syncSpreadsheet   = ()       => post('/settings/connections/xls/sync', {});
  const toggleAgent       = on       => post('/webhook/agent/toggle', { active: on });

  return {
    login, logout,
    getCustomers, updateCustomer,
    getChats, getChat, sendMessage,
    getApprovals, approveItem, rejectItem,
    getCampaigns, getTemplates, createTemplate, approveTemplate,
    getProjects,
    getAppointments, confirmAppointment,
    getRecommendations, applyRecommendation,
    getKB, addKBEntry, deleteKBEntry,
    getSettings, saveSettings, toggleConnection, syncSpreadsheet, toggleAgent,
  };
})();

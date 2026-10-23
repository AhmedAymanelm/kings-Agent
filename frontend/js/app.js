/**
 * app.js — Main application controller (async views)
 */
const App = (() => {

  /* ---- State ---- */
  let currentUser = null;
  let currentView = 'overview';
  let agentOn     = true;
  const appliedRecs = new Set();

  /* ---- Helpers ---- */
  const isMgr = () => currentUser?.role === 'manager';

  /* ---- View registry — all render() are async ---- */
  const VIEWS = {
    overview:  OverviewView,
    chats:     ChatsView,
    alerts:    AlertsView,
    customers: CustomersView,
    facebook:  FacebookView,
    schedule:  ScheduleView,
    insights:  InsightsView,
    settings:  SettingsView,
  };

  /* ---- Loading skeleton ---- */
  function showLoading() {
    document.getElementById('view').innerHTML = `
      <div style="display:flex;flex-direction:column;gap:16px;padding:24px">
        ${[1,2,3].map(() => `
          <div style="height:80px;background:var(--surface2);border-radius:12px;
               animation:pulse 1.4s ease-in-out infinite"></div>`).join('')}
      </div>`;
  }

  /* ---- Shell update ---- */
  function updateShell(settings) {
    const mgr = isMgr();
    document.getElementById('meAv').textContent   = currentUser.name.trim()[0];
    document.getElementById('meName').textContent  = currentUser.name;

    const roleEl = document.getElementById('meRole');
    roleEl.textContent = mgr ? 'مدير' : 'موظف';
    roleEl.className   = 'pill ' + (mgr ? 'st-acc' : 's1');

    const isActive = settings?.is_active ?? true;
    agentOn = isActive;
    const sw = document.getElementById('agentSwitch');
    if (sw) sw.setAttribute('aria-checked', isActive);
    const dot = document.getElementById('agentDot');
    if (dot) dot.className = 'dot' + (isActive ? '' : ' off');
    const st = document.getElementById('agentState');
    if (st) st.textContent = isActive ? 'الوكيل يعمل' : 'الوكيل متوقف';

    document.getElementById('agentNote').textContent = mgr
      ? 'واتساب · تيليجرام · إيميل متصلين'
      : 'تشغيل الوكيل من صلاحيات المدير';

    document.getElementById('agentSwitch').disabled = !mgr;
    document.getElementById('pageTitle').textContent = VIEWS_META[currentView][0];
    document.getElementById('pageSub').textContent   = VIEWS_META[currentView][1];
  }

  /* ---- Full async render ---- */
  async function render() {
    if (!currentUser) { LoginView.render(LoginView.currentKind()); return; }

    document.getElementById('login').hidden = true;
    document.getElementById('shell').hidden = false;

    // Load settings for shell header + badge counts
    let settings = null;
    try { settings = await API.getSettings(); } catch (_) {}

    // Update nav badge counts
    try {
      const [chatsList, alertsList] = await Promise.all([
        API.getChats().catch(() => []),
        API.getApprovals('pending').catch(() => []),
      ]);
      Nav.setState({
        unread: chatsList.reduce((s, c) => s + (c.unread_count || 0), 0),
        alerts: alertsList.length,
      });
    } catch (_) {}

    updateShell(settings);
    Nav.render(currentView, currentUser.role);

    // Bind logout
    document.getElementById('logout').onclick = logout;

    // Bind agent toggle
    document.getElementById('agentSwitch').onclick = async (e) => {
      if (!isMgr()) return;
      agentOn = !agentOn;
      e.currentTarget.setAttribute('aria-checked', agentOn);
      document.getElementById('agentState').textContent = agentOn ? 'الوكيل يعمل' : 'الوكيل متوقف';
      document.getElementById('agentDot').className     = 'dot' + (agentOn ? '' : ' off');
      await API.toggleAgent(agentOn).catch(() => {});
      Toast.show(agentOn ? 'تم تشغيل الوكيل' : 'تم إيقاف الردود التلقائية');
    };

    // Show loading skeleton, then render view
    showLoading();
    const viewDef = VIEWS[currentView];
    try {
      const html = await viewDef.render(isMgr());
      document.getElementById('view').innerHTML = html;
      await viewDef.bind(isMgr());
    } catch (err) {
      document.getElementById('view').innerHTML = `
        <div class="card" style="padding:32px;text-align:center;color:var(--danger)">
          <b>⚠️ خطأ في تحميل البيانات</b>
          <p style="margin-top:8px;color:var(--fg2)">${err.message}</p>
          <button class="btn sm" onclick="App.go('${currentView}')" style="margin-top:16px">إعادة المحاولة</button>
        </div>`;
    }
  }

  /* Public refresh (used by views internally) */
  async function refreshView() { await render(); }

  /* ---- Navigation ---- */
  async function go(viewKey) {
    if (!currentUser) { LoginView.render(LoginView.currentKind()); return; }
    currentView = ACCESS[currentUser.role].includes(viewKey) ? viewKey : 'overview';
    try { history.replaceState(null, '', '#' + currentView); } catch (_) {}
    await render();
  }

  /* ---- Auth ---- */
  function setUser(user) { currentUser = user; }

  function logout() {
    API.logout();
    currentUser = null;
    document.getElementById('shell').hidden = true;
    LoginView.render(LoginView.currentKind());
  }

  /* ---- Boot ---- */
  async function boot() {
    const hash  = (location.hash || '').slice(1);
    const token = sessionStorage.getItem('authToken');

    if (token) {
      // Try to restore session from token by hitting /customers (any auth endpoint)
      try {
        const me = JSON.parse(sessionStorage.getItem(CONFIG.SESSION_KEY) || 'null');
        if (me) {
          currentUser = me;
          await go(VIEWS_META[hash] ? hash : 'overview');
          return;
        }
      } catch (_) {}
    }

    LoginView.render(hash === 'staff-login' ? 'staff' : 'manager');
  }

  return { render, refreshView, go, setUser, logout, isMgr, appliedRecs, boot };
})();

/* ---- Start the app ---- */
document.addEventListener('DOMContentLoaded', () => App.boot());

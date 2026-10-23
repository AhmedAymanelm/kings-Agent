/**
 * nav.js — Sidebar navigation component
 * Badges now use a simple state store updated by views
 */
const Nav = (() => {

  // Badge counts — updated by app after data fetch
  const _state = { unread: 0, alerts: 0 };

  function setState(patch) { Object.assign(_state, patch); }

  function render(currentView, role) {
    const navEl = document.getElementById('nav');
    navEl.innerHTML = ACCESS[role].map(key => {
      let badgeHtml = '';
      if (key === 'chats'  && _state.unread) badgeHtml = `<span class="badge num">${_state.unread}</span>`;
      if (key === 'alerts' && _state.alerts) badgeHtml = `<span class="badge num hot">${_state.alerts}</span>`;
      return `<button data-v="${key}" ${key === currentView ? 'aria-current="page"' : ''}>
        <span>${VIEWS_META[key][0]}</span>${badgeHtml}
      </button>`;
    }).join('');

    navEl.querySelectorAll('button').forEach(btn => {
      btn.onclick = () => App.go(btn.dataset.v);
    });
  }

  return { render, setState };
})();

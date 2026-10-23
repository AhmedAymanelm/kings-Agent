/**
 * projects.js — Projects Kanban (async, real API)
 */
const ProjectsView = (() => {
  const esc = s => String(s).replace(/[&<>"']/g, c =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  async function render() {
    const projects = await API.getProjects();

    const cols = STAGES.map((stageName, i) => {
      const cards = projects.filter(p => p.stage === i);
      return `
        <div class="kanban-col">
          <div class="kanban-head">
            <b>${stageName}</b>
            <span class="num pill s1">${cards.length}</span>
          </div>
          <div class="kanban-cards">
            ${cards.map(p => `
              <div class="card kcard ${p.is_late ? 'late' : ''}">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:4px">
                  <b>${esc(p.name)}</b>
                  ${p.is_late ? '<span class="pill st-bad" style="font-size:11px">متأخر</span>' : ''}
                </div>
                <div class="muted sm-t" style="margin:4px 0">${esc(p.customer)}</div>
                <div class="prog-bar" style="margin:8px 0">
                  <div style="width:${p.progress}%;background:${p.is_late ? 'var(--danger)' : 'var(--accent)'}"></div>
                </div>
                <div style="display:flex;justify-content:space-between;align-items:center">
                  <span class="muted sm-t">📅 ${esc(p.due_note || '—')}</span>
                  <b class="num">${p.progress}%</b>
                </div>
                <div class="muted sm-t" style="margin-top:6px;font-size:11px">🔔 ${esc(p.reminder || '—')}</div>
              </div>`).join('')}
          </div>
        </div>`;
    }).join('');

    return `<div class="kanban">${cols}</div>`;
  }

  async function bind() {}

  return { render, bind };
})();

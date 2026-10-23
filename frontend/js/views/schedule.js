/**
 * schedule.js — Appointments schedule (async, real API)
 */
const ScheduleView = (() => {
  const esc = s => String(s).replace(/[&<>"']/g, c =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  async function render() {
    const appts = await API.getAppointments();

    // Group by day
    const byDay = {};
    for (const a of appts) {
      const key = a.day_label || a.d || '—';
      if (!byDay[key]) byDay[key] = [];
      byDay[key].push(a);
    }

    const dayBlocks = Object.entries(byDay).map(([day, items]) => `
      <div class="sched-day">
        <div class="sched-day-label">${esc(day)}</div>
        <div class="list">
          ${items.map(a => `
            <div class="item">
              <div class="time num" style="min-width:56px">${esc(a.time_label || a.t)}</div>
              <div class="grow">
                <b>${esc(a.title || a.n)}</b>
                <div class="muted sm-t">${esc(a.customer || a.cu)} · ${esc(a.channel || a.ch)}</div>
              </div>
              ${a.confirmed || a.ok
                ? '<span class="pill st-good">مؤكد</span>'
                : `<button class="btn sm" data-conf="${a.id}">أكّد مع العميل</button>`}
            </div>`).join('')}
        </div>
      </div>`).join('');

    return `
      <section class="panel">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
          <h2 style="margin:0">المواعيد القادمة</h2>
          <span class="pill s1 num">${appts.length} موعد</span>
        </div>
        ${dayBlocks || '<p class="muted" style="padding:24px;text-align:center">لا مواعيد مجدولة</p>'}
      </section>`;
  }

  async function bind() {
    document.querySelectorAll('[data-conf]').forEach(btn => {
      btn.onclick = async () => {
        await API.confirmAppointment(+btn.dataset.conf).catch(() => {});
        Toast.show('أُرسل طلب التأكيد للعميل ✓');
        App.refreshView();
      };
    });
  }

  return { render, bind };
})();

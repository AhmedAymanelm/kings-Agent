/**
 * overview.js — Dashboard overview (async, real API)
 */
const OverviewView = (() => {
  const esc = s => String(s).replace(/[&<>"']/g, c =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const pill = k => `<span class="pill s${SEG[k]?.c || 1}">${SEG[k]?.n || k}</span>`;

  function apptRow(a) {
    return `
      <div class="item">
        <div class="time num">${a.time_label || a.t || ''}</div>
        <div class="grow">
          <b>${esc(a.title || a.n)}</b>
          <div class="muted sm-t">${esc(a.customer || a.cu)} · ${esc(a.channel || a.ch)}</div>
        </div>
        ${a.confirmed || a.ok
          ? '<span class="pill st-good">مؤكد</span>'
          : `<button class="btn sm" data-conf="${a.id}">أكّد مع العميل</button>`}
      </div>`;
  }

  async function render(isMgr) {
    const [appts, approvalsList, chatsList, customersList, recsList] = await Promise.all([
      API.getAppointments().catch(() => []),
      API.getApprovals('pending').catch(() => []),
      API.getChats().catch(() => []),
      API.getCustomers().catch(() => []),
      isMgr ? API.getRecommendations().catch(() => []) : Promise.resolve([]),
    ]);

    const today   = appts.filter(a => (a.day_label || a.d || '').includes('اليوم'));
    const pending = approvalsList.length;
    const waiting = chatsList.filter(c => !c.ai_handling || c.unread_count > 0);

    const alertBox = isMgr && pending
      ? `<div class="alert">
           <span><span class="num">${pending}</span> عناصر بانتظار موافقتك</span>
           <button class="btn sm" data-go="approvals">راجعها الآن</button>
         </div>`
      : '';

    const chartHtml = Chart.stackedBar({
      labels: ['الجمعة','السبت','الأحد','الاثنين','الثلاثاء','الأربعاء','الخميس'],
      primary:   [98, 131, 112, 158, 181, 149, 127],
      secondary: [14,  17,  19,  18,  22,  18,  15],
      primaryLabel: 'ردّ الوكيل تلقائياً', secondaryLabel: 'تحويل لموظف', maxY: 250,
    });

    const keys  = Object.keys(SEG);
    const cnt   = keys.map(k => customersList.filter(c => c.segment === k).length);
    const tot   = customersList.length || 1;
    const segBar = `
      <div class="bar" style="height:12px">
        ${keys.map((k, i) => `<span style="width:${cnt[i]/tot*100}%;background:var(--c${SEG[k].c})"></span>`).join('')}
      </div>
      <div class="list" style="margin-top:14px">
        ${keys.map((k, i) => `
          <div class="item" style="padding:7px 0">
            <div class="grow">${pill(k)}</div>
            <b class="num">${cnt[i]}</b>
          </div>`).join('')}
      </div>`;

    const secondPanel = isMgr
      ? `<section class="panel">
           <h2>توصيات الوكيل <button class="link" data-go="insights">كل التوصيات</button></h2>
           <div class="list">
             ${recsList.slice(0, 3).map(r => `
               <div class="item">
                 <div class="grow"><b>${esc(r.t || r.title || '')}</b><div class="muted sm-t">${esc(r.d || r.desc || '')}</div></div>
               </div>`).join('') || '<p class="muted" style="padding:8px">لا توجد توصيات حالياً</p>'}
           </div>
         </section>`
      : `<section class="panel">
           <h2>محادثات تنتظر ردك <button class="link" data-go="chats">كل المحادثات</button></h2>
           <div class="list">
             ${waiting.slice(0, 5).map(c => `
               <div class="item">
                 <span class="avatar">${(c.customer_name || c.n || '?')[0]}</span>
                 <div class="grow">
                   <b>${esc(c.customer_name || c.n || '')}</b>
                   <div class="muted sm-t">${esc(c.last_message || '')}</div>
                 </div>
                 ${c.unread_count ? `<span class="unread num">${c.unread_count}</span>` : ''}
               </div>`).join('') || '<p class="muted" style="padding:8px">لا محادثات بانتظار</p>'}
           </div>
         </section>`;

    const newCount   = customersList.filter(c => c.segment === 'new').length;
    const totalChats = chatsList.length;
    const unread     = chatsList.reduce((s, c) => s + (c.unread_count || 0), 0);

    return `
      ${alertBox}
      <div class="grid kpis">
        <div class="kpi"><small>إجمالي العملاء</small><strong class="num">${customersList.length}</strong><em class="num">+${newCount} جديد</em></div>
        <div class="kpi"><small>محادثات نشطة</small><strong class="num">${totalChats}</strong><em class="num">${unread} غير مقروء</em></div>
        <div class="kpi"><small>بانتظار الموافقة</small><strong class="num">${pending}</strong><em>عرض / خصم / حملة</em></div>
        <div class="kpi"><small>مواعيد اليوم</small><strong class="num">${today.length}</strong><em>${today.filter(a => !a.confirmed).length} بانتظار التأكيد</em></div>
      </div>

      <div class="grid two">
        <section class="panel"><h2>الرسائل آخر 7 أيام</h2>${chartHtml}</section>
        <section class="panel">
          <h2>تصنيف العملاء <button class="link" data-go="customers">عرض الكل</button></h2>
          ${segBar}
        </section>
      </div>

      <div class="grid two">
        ${secondPanel}
        <section class="panel">
          <h2>مواعيد اليوم <button class="link" data-go="schedule">الجدول كامل</button></h2>
          <div class="list">${today.map(apptRow).join('') || '<p class="muted" style="padding:8px">لا مواعيد اليوم</p>'}</div>
        </section>
      </div>`;
  }

  async function bind() {
    document.querySelectorAll('[data-conf]').forEach(btn => {
      btn.onclick = async () => {
        await API.confirmAppointment(+btn.dataset.conf).catch(() => {});
        Toast.show('أُرسل طلب التأكيد للعميل ✓');
        App.refreshView();
      };
    });
    document.querySelectorAll('[data-go]').forEach(btn => {
      btn.onclick = () => App.go(btn.dataset.go);
    });
  }

  return { render, bind };
})();

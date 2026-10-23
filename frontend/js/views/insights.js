/**
 * insights.js — AI Recommendations (async, real API)
 */
const InsightsView = (() => {
  const esc = s => String(s).replace(/[&<>"']/g, c =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  // Static weekly insights (AI-generated, not yet stored in DB)
  const WEEKLY = [
    { icon: '📈', title: 'عملاء "مهتم" بلا متابعة',    body: '5 عملاء مهتمين لم يُتابَعوا منذ أكثر من أسبوع. اقتراح: حملة متابعة على واتساب.' },
    { icon: '💡', title: 'قالب "استبيان رضا" جاهز',     body: 'القالب اعتُمد. يمكن إرساله لـ 63 عميلاً حالياً لتحسين التقييمات.' },
    { icon: '⚠️', title: 'مشروع "تطبيق مواعيد" متأخر', body: 'تأخر يومان. اقتراح: إرسال تحديث للعميل وتحديد موعد مراجعة طارئ.' },
    { icon: '📣', title: 'حملة نهاية الشهر تنتهي قريباً', body: 'تنتهي بعد 9 أيام. 74 عميلاً ردوا — اقتراح: متابعة من لم يرد.' },
    { icon: '🔔', title: '3 عملاء متوقفون قابلون للاسترداد', body: 'كريم حسن، يوسف رمضان وعميل آخر لم يتواصلوا منذ 20+ يوم. جرّب حملة "وحشتنا".' },
  ];

  async function render() {
    // Try to get recommendations from API, fall back to static
    let recs = [];
    try { recs = await API.getRecommendations(); } catch (_) {}

    // Merge API recs + static weekly ones
    const apiCards = recs.map((r, i) => `
      <div class="card rec" data-rec="${r.id || i}">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px">
          <div>
            <b>${esc(r.title || r.t)}</b>
            <p class="muted sm-t" style="margin:6px 0;line-height:1.6">${esc(r.desc || r.d || '')}</p>
          </div>
          <button class="btn sm primary" data-apply="${r.id || i}">تطبيق</button>
        </div>
      </div>`).join('');

    const weeklyCards = WEEKLY.map((w, i) => `
      <div class="card" style="border-right:3px solid var(--accent)">
        <div style="display:flex;gap:12px;align-items:flex-start">
          <span style="font-size:22px">${w.icon}</span>
          <div>
            <b>${esc(w.title)}</b>
            <p class="muted sm-t" style="margin-top:6px;line-height:1.6">${esc(w.body)}</p>
          </div>
        </div>
      </div>`).join('');

    return `
      <div class="grid two" style="align-items:start">
        <section class="panel">
          <h2>توصيات الوكيل</h2>
          <div style="display:flex;flex-direction:column;gap:12px">
            ${apiCards || '<p class="muted">لا توصيات جاهزة حالياً. الوكيل يحتاج اتصال AI.</p>'}
          </div>
        </section>

        <section class="panel">
          <h2>تحليل الأسبوع</h2>
          <div style="display:flex;flex-direction:column;gap:12px">
            ${weeklyCards}
          </div>
        </section>
      </div>`;
  }

  async function bind() {
    document.querySelectorAll('[data-apply]').forEach(btn => {
      btn.onclick = async () => {
        await API.applyRecommendation(+btn.dataset.apply).catch(() => {});
        Toast.show('تم تطبيق التوصية ✓');
        App.refreshView();
      };
    });
  }

  return { render, bind };
})();

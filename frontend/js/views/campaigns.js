/**
 * campaigns.js — Campaigns & Templates (async, real API)
 */
const CampaignsView = (() => {
  const esc = s => String(s).replace(/[&<>"']/g, c =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  const STATUS = {
    running:   ['جارية',    'st-good'],
    scheduled: ['مجدولة',   'st-acc'],
    done:      ['مكتملة',   'st-warn'],
    draft:     ['مسودة',    'st-mute'],
  };
  const TPL_ST = {
    approved: ['معتمد',        'st-good'],
    review:   ['قيد المراجعة', 'st-warn'],
    rejected: ['مرفوض',        'st-bad'],
  };

  async function render() {
    const [camps, tpls] = await Promise.all([
      API.getCampaigns(),
      API.getTemplates(),
    ]);

    const campCards = camps.map(c => {
      const [stLabel, stClass] = STATUS[c.status] || ['—', 'st-mute'];
      const readPct  = c.sent ? Math.round((c.read  || 0) / c.sent * 100) : 0;
      const replPct  = c.sent ? Math.round((c.replied || 0) / c.sent * 100) : 0;
      return `
        <div class="card">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px;flex-wrap:wrap">
            <div>
              <b>${esc(c.name)}</b>
              <div class="muted sm-t" style="margin-top:4px">${esc(c.channel)} · ${esc(c.audience)} · ${c.recipient_count} عميل</div>
            </div>
            <span class="pill ${stClass}">${stLabel}</span>
          </div>
          ${c.sent ? `
            <div style="margin-top:12px;display:flex;gap:16px">
              <div><small class="muted">مُرسل</small><br><b class="num">${c.sent}</b></div>
              <div><small class="muted">مقروء</small><br><b class="num">${readPct}%</b></div>
              <div><small class="muted">ردّ</small><br><b class="num">${replPct}%</b></div>
            </div>` : ''}
          <div class="muted sm-t" style="margin-top:8px">🕐 ${esc(c.scheduled_at || '—')}</div>
        </div>`;
    }).join('');

    const tplCards = tpls.map(t => {
      const [stLabel, stClass] = TPL_ST[t.status] || ['—', 'st-mute'];
      return `
        <div class="card">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px">
            <div>
              <b>${esc(t.name)}</b>
              <span class="pill s1" style="margin-right:8px;font-size:11px">${esc(t.category)}</span>
            </div>
            <span class="pill ${stClass}">${stLabel}</span>
          </div>
          <p class="muted sm-t" style="margin:8px 0;line-height:1.6">${esc(t.body)}</p>
          ${t.reject_reason ? `<p style="color:var(--danger);font-size:12px">سبب الرفض: ${esc(t.reject_reason)}</p>` : ''}
        </div>`;
    }).join('');

    return `
      <div class="grid two" style="align-items:start">
        <section class="panel">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
            <h2 style="margin:0">الحملات</h2>
          </div>
          <div style="display:flex;flex-direction:column;gap:12px">${campCards || '<p class="muted">لا حملات</p>'}</div>
        </section>

        <section class="panel">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
            <h2 style="margin:0">القوالب</h2>
            <button class="btn sm primary" id="newTplBtn">+ قالب جديد</button>
          </div>
          <div style="display:flex;flex-direction:column;gap:12px">${tplCards || '<p class="muted">لا قوالب</p>'}</div>
        </section>
      </div>

      <!-- New template modal -->
      <div id="tplModal" hidden style="position:fixed;inset:0;background:#0008;z-index:999;display:flex;align-items:center;justify-content:center">
        <div class="card" style="width:min(480px,90vw);padding:24px;display:flex;flex-direction:column;gap:16px">
          <h3 style="margin:0">قالب جديد</h3>
          <div class="field">
            <label>اسم القالب</label>
            <input class="in" id="tplName" placeholder="مثال: عرض نهاية الشهر" />
          </div>
          <div class="field">
            <label>الفئة</label>
            <select class="in" id="tplCat">
              <option>تسويقية</option><option>تذكير</option><option>خدمية</option>
            </select>
          </div>
          <div class="field">
            <label>نص القالب <span class="muted sm-t">(استخدم {الاسم} {التاريخ} كمتغيرات)</span></label>
            <textarea class="in" id="tplBody" rows="4" placeholder="أهلاً {الاسم}، ..."></textarea>
          </div>
          <div style="display:flex;gap:8px;justify-content:flex-end">
            <button class="btn sm" id="tplCancel">إلغاء</button>
            <button class="btn primary sm" id="tplSave">حفظ وإرسال للمراجعة</button>
          </div>
        </div>
      </div>`;
  }

  async function bind() {
    const modal = document.getElementById('tplModal');
    document.getElementById('newTplBtn')?.addEventListener('click', () => {
      modal.hidden = false;
    });
    document.getElementById('tplCancel')?.addEventListener('click', () => {
      modal.hidden = true;
    });
    document.getElementById('tplSave')?.addEventListener('click', async () => {
      const name = document.getElementById('tplName').value.trim();
      const cat  = document.getElementById('tplCat').value;
      const body = document.getElementById('tplBody').value.trim();
      if (!name || !body) { Toast.show('اكتب الاسم والنص'); return; }
      await API.createTemplate({ name, category: cat, body });
      modal.hidden = true;
      Toast.show('تم إرسال القالب للمراجعة ✓');
      App.refreshView();
    });
  }

  return { render, bind };
})();

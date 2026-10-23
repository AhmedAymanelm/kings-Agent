/**
 * alerts.js — Escalation alerts (cases needing human intervention)
 * الوكيل اكتشف حاجة مش قادر يتعامل معها وحده
 */
const AlertsView = (() => {
  const esc = s => String(s).replace(/[&<>"']/g, c =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  const ICONS = {
    angry:   { icon: '😤', label: 'عميل غاضب',         color: 'var(--danger)' },
    amount:  { icon: '💰', label: 'صفقة كبيرة',         color: '#f59e0b'       },
    unknown: { icon: '❓', label: 'سؤال بدون إجابة',    color: '#6366f1'       },
    call:    { icon: '📞', label: 'طلب مكالمة',          color: '#10b981'       },
    other:   { icon: '🔔', label: 'تنبيه عام',           color: 'var(--accent)' },
  };

  async function render() {
    // Reuse approvals endpoint as escalation alerts
    const list = await API.getApprovals().catch(() => []);
    const open   = list.filter(a => a.status === 'pending');
    const closed = list.filter(a => a.status !== 'pending');

    function card(a) {
      const typeKey = a.type === 'عرض سعر' ? 'amount'
                    : a.type === 'رد على عميل' ? 'angry'
                    : a.type === 'تعديل عقد' ? 'call'
                    : 'other';
      const meta = ICONS[typeKey] || ICONS.other;
      return `
        <div class="card alert-card ${a.status !== 'pending' ? 'dim' : ''}">
          <div style="display:flex;gap:12px;align-items:flex-start">
            <span style="font-size:28px">${meta.icon}</span>
            <div style="flex:1">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:6px">
                <div>
                  <b style="font-size:15px">${esc(a.customer)}</b>
                  <span class="pill st-warn" style="margin-right:8px;font-size:11px">${esc(a.type)}</span>
                </div>
                <span class="muted sm-t">${esc(a.requested_by)} · ${esc(a.decided_at || 'منذ قليل')}</span>
              </div>
              <p class="muted" style="margin:6px 0;font-size:13px;line-height:1.6">${esc(a.reason)}</p>
              <div style="background:var(--surface2);border-radius:8px;padding:12px;
                          border-right:3px solid ${meta.color};margin-bottom:12px;
                          font-size:13px;line-height:1.7">
                ${esc(a.body_text)}
              </div>
              ${a.status === 'pending' ? `
                <div style="display:flex;gap:8px;flex-wrap:wrap">
                  <button class="btn primary sm" data-chat-jump="${a.customer}">
                    💬 افتح المحادثة
                  </button>
                  <button class="btn sm" data-dismiss="${a.id}" style="color:var(--muted)">
                    تم التعامل معه ✓
                  </button>
                </div>` : `
                <span class="pill st-good" style="font-size:12px">تم التعامل معه</span>`}
            </div>
          </div>
        </div>`;
    }

    return `
      <div style="max-width:720px;margin:0 auto">
        ${open.length === 0 ? `
          <div style="text-align:center;padding:60px 24px">
            <div style="font-size:48px;margin-bottom:12px">✅</div>
            <b style="font-size:18px">كل شيء تحت السيطرة</b>
            <p class="muted" style="margin-top:8px">الوكيل يتعامل مع كل شيء. هنبلّغك لو في شيء يحتاجك.</p>
          </div>` : `
          <div style="display:flex;align-items:center;gap:10px;margin-bottom:20px">
            <h2 style="margin:0">يحتاج تدخّلك</h2>
            <span class="pill st-bad num">${open.length}</span>
          </div>
          <div style="display:flex;flex-direction:column;gap:12px">
            ${open.map(card).join('')}
          </div>`}

        ${closed.length ? `
          <h2 style="margin:24px 0 12px;color:var(--fg2);font-size:14px">سبق التعامل معها</h2>
          <div style="display:flex;flex-direction:column;gap:10px">
            ${closed.map(card).join('')}
          </div>` : ''}
      </div>`;
  }

  async function bind() {
    // Jump to chat
    document.querySelectorAll('[data-chat-jump]').forEach(btn => {
      btn.onclick = () => App.go('chats');
    });

    // Dismiss alert
    document.querySelectorAll('[data-dismiss]').forEach(btn => {
      btn.onclick = async () => {
        await API.approveItem(+btn.dataset.dismiss, null).catch(() => {});
        Toast.show('تم ✓');
        App.refreshView();
      };
    });
  }

  return { render, bind };
})();

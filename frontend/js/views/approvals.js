/**
 * approvals.js — Approvals queue (async, real API)
 */
const ApprovalsView = (() => {
  const esc = s => String(s).replace(/[&<>"']/g, c =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  async function render() {
    const list = await API.getApprovals();

    const pending  = list.filter(a => a.status === 'pending');
    const decided  = list.filter(a => a.status !== 'pending');

    const card = a => `
      <div class="card ap ${a.status !== 'pending' ? 'dim' : ''}" data-ap="${a.id}">
        <div class="ap-head">
          <div>
            <span class="pill s3">${esc(a.type)}</span>
            <b style="margin-right:8px">${esc(a.customer)}</b>
          </div>
          <span class="muted sm-t">${esc(a.requested_by)} · ${esc(a.decided_at || 'منذ قليل')}</span>
        </div>
        <p class="muted sm-t" style="margin:6px 0">${esc(a.reason)}</p>
        <div class="ap-body" contenteditable="${a.status === 'pending'}" id="ap-txt-${a.id}"
             style="background:var(--surface2);border-radius:8px;padding:12px;line-height:1.7;
                    border:1px solid var(--border);margin-bottom:12px;min-height:56px">
          ${esc(a.body_text)}
        </div>
        ${a.status === 'pending' ? `
          <div style="display:flex;gap:8px;flex-wrap:wrap">
            <button class="btn primary sm" data-approve="${a.id}">✓ موافقة وإرسال</button>
            <button class="btn sm" data-reject="${a.id}" style="color:var(--danger)">✕ رفض</button>
          </div>` : `
          <span class="pill ${a.status === 'approved' ? 'st-good' : 'st-bad'}">
            ${a.status === 'approved' ? 'تمت الموافقة' : 'مرفوض'} · ${esc(a.decided_at)}
          </span>`}
      </div>`;

    return `
      <div class="ap-wrap">
        <section class="panel">
          <h2>بانتظار الموافقة <span class="num pill st-warn">${pending.length}</span></h2>
          ${pending.map(card).join('') || '<p class="muted" style="padding:16px">لا يوجد شيء بانتظار موافقتك 🎉</p>'}
        </section>

        ${decided.length ? `
        <section class="panel" style="margin-top:0">
          <h2>سبق البت فيها</h2>
          ${decided.map(card).join('')}
        </section>` : ''}
      </div>`;
  }

  async function bind() {
    document.querySelectorAll('[data-approve]').forEach(btn => {
      btn.onclick = async () => {
        const id   = +btn.dataset.approve;
        const txt  = document.getElementById(`ap-txt-${id}`)?.innerText?.trim() || null;
        await API.approveItem(id, txt);
        Toast.show('تمت الموافقة وسيُرسل الرد ✓');
        App.refreshView();
      };
    });
    document.querySelectorAll('[data-reject]').forEach(btn => {
      btn.onclick = async () => {
        await API.rejectItem(+btn.dataset.reject);
        Toast.show('تم الرفض');
        App.refreshView();
      };
    });
  }

  return { render, bind };
})();

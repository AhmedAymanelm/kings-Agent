/**
 * customers.js — Customers table (async, real API)
 */
const CustomersView = (() => {
  const esc = s => String(s).replace(/[&<>"']/g, c =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const pill = k => `<span class="pill s${SEG[k]?.c || 1}">${SEG[k]?.n || k}</span>`;

  let allData = [];
  let query   = '';
  let segFilt = '';

  async function render(isMgr) {
    allData = await API.getCustomers({ q: query, segment: segFilt });

    const segCounts = Object.fromEntries(
      Object.keys(SEG).map(k => [k, allData.filter(c => c.segment === k).length])
    );

    const filters = `
      <div class="tb-filters">
        <input class="in" id="custSearch" placeholder="🔍 بحث باسم أو رقم..." value="${esc(query)}"
               style="min-width:200px" />
        <div class="seg-chips">
          <button class="chip ${!segFilt ? 'active' : ''}" data-seg="">الكل <span class="num">${allData.length}</span></button>
          ${Object.entries(SEG).map(([k, v]) => `
            <button class="chip s${v.c} ${segFilt === k ? 'active' : ''}" data-seg="${k}">
              ${v.n} <span class="num">${segCounts[k] || 0}</span>
            </button>`).join('')}
        </div>
        ${isMgr ? `<button class="btn sm" id="exportXls">📥 تصدير Excel</button>` : ''}
      </div>`;

    const rows = allData.map(c => `
      <tr>
        <td><b>${esc(c.name)}</b></td>
        <td dir="ltr">${esc(c.phone)}</td>
        <td>${esc(c.source)}</td>
        <td>${pill(c.segment)}</td>
        ${isMgr ? `<td class="num">${c.value ? Number(c.value).toLocaleString('ar-EG') + ' ج.م' : '—'}</td>` : ''}
        <td>${esc(c.project || '—')}</td>
        <td>
          <span class="pill ${c.consent === 'in' ? 'st-good' : c.consent === 'out' ? 'st-bad' : 'st-mute'}">
            ${c.consent === 'in' ? 'مشترك' : c.consent === 'out' ? 'منسحب' : 'لم يُسأل'}
          </span>
        </td>
        <td class="muted sm-t">${esc(c.last_contact || '—')}</td>
        ${isMgr ? `
          <td>
            <select class="in sm-t" data-seg-edit="${c.id}" style="padding:4px 8px">
              ${Object.entries(SEG).map(([k, v]) =>
                `<option value="${k}" ${c.segment === k ? 'selected' : ''}>${v.n}</option>`
              ).join('')}
            </select>
          </td>` : '<td></td>'}
      </tr>`).join('');

    return `
      ${filters}
      <div class="tb-wrap">
        <table class="tb">
          <thead><tr>
            <th>الاسم</th><th>الهاتف</th><th>المصدر</th><th>الفئة</th>
            ${isMgr ? '<th>القيمة</th>' : ''}
            <th>المشروع</th><th>الموافقة</th><th>آخر تواصل</th><th></th>
          </tr></thead>
          <tbody>${rows || '<tr><td colspan="9" class="muted" style="text-align:center;padding:32px">لا يوجد نتائج</td></tr>'}</tbody>
        </table>
      </div>`;
  }

  async function bind(isMgr) {
    // Search
    const searchInput = document.getElementById('custSearch');
    let debounce;
    searchInput?.addEventListener('input', e => {
      clearTimeout(debounce);
      debounce = setTimeout(() => { query = e.target.value.trim(); App.refreshView(); }, 400);
    });

    // Segment filter chips
    document.querySelectorAll('[data-seg]').forEach(btn => {
      btn.onclick = () => { segFilt = btn.dataset.seg; App.refreshView(); };
    });

    // Inline segment edit
    document.querySelectorAll('[data-seg-edit]').forEach(sel => {
      sel.onchange = async () => {
        const id = +sel.dataset.segEdit;
        await API.updateCustomer(id, { segment: sel.value }).catch(() => {});
        Toast.show('تم تحديث الفئة ✓');
      };
    });

    // Excel export
    document.getElementById('exportXls')?.addEventListener('click', () => {
      const headers = ['الاسم','الهاتف','المصدر','الفئة','القيمة','المشروع','الموافقة'];
      const rows = allData.map(c => [c.name, c.phone, c.source, c.segment, c.value, c.project, c.consent]);
      const csv  = [headers, ...rows].map(r => r.map(v => `"${String(v||'').replace(/"/g,'""')}"`).join(',')).join('\n');
      const url  = URL.createObjectURL(new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8' }));
      Object.assign(document.createElement('a'), { href: url, download: 'customers.csv' }).click();
      URL.revokeObjectURL(url);
    });
  }

  return { render, bind };
})();

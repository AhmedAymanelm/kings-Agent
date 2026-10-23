/**
 * chats.js — Conversations view (WhatsApp · Telegram · Email) — async, real API
 */
const ChatsView = (() => {
  const esc = s => String(s).replace(/[&<>"']/g, c =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const pill = k => `<span class="pill s${SEG[k]?.c || 1}">${SEG[k]?.n || k}</span>`;

  const CH = {
    whatsapp: { label: 'واتساب',   icon: '💬', color: '#25D366' },
    telegram: { label: 'تيليجرام', icon: '✈️', color: '#2AABEE' },
    email:    { label: 'إيميل',    icon: '📧', color: '#6366f1' },
  };

  const chOf  = c => CH[c.channel] || CH.whatsapp;
  const chIcon = c => `<span style="font-size:13px">${chOf(c).icon}</span>`;

  let allChats   = [];
  let selectedId = null;
  let filter     = 'all';

  const TABS = [
    { key: 'all',      label: 'الكل' },
    { key: 'whatsapp', label: '💬 واتساب' },
    { key: 'telegram', label: '✈️ تيليجرام' },
    { key: 'email',    label: '📧 إيميل' },
  ];

  function visible() {
    if (filter === 'all') return allChats;
    return allChats.filter(c => c.channel === filter);
  }

  async function render() {
    allChats = await API.getChats();
    if (!selectedId && allChats.length) selectedId = allChats[0].id;

    // Load selected chat thread
    let selected = allChats.find(c => c.id === selectedId) || allChats[0];
    if (selected && (!selected.messages || !selected.messages.length)) {
      try { selected = await API.getChat(selected.id); } catch (_) {}
    }

    const vis = visible();

    const tabs = TABS.map(t => {
      const count = t.key === 'all' ? allChats.length
        : allChats.filter(c => c.channel === t.key).length;
      return `<button class="tab-chip ${filter === t.key ? 'active' : ''}" data-filter="${t.key}">
        ${t.label} <span class="num">${count}</span>
      </button>`;
    }).join('');

    const chatList = vis.map(c => {
      const ch = chOf(c);
      const seg = c.customer_segment || 'new';
      return `
        <button class="chat" data-chat="${c.id}" aria-selected="${c.id === selectedId}">
          <span class="avatar" style="background:${ch.color}22;color:${ch.color}">
            ${(c.customer_name || '?')[0]}
          </span>
          <span class="grow">
            <span class="l1">
              <b>${esc(c.customer_name || 'عميل')}</b>
              <span class="muted sm-t num">${esc(c.last_at ? new Date(c.last_at).toLocaleTimeString('ar-EG',{hour:'2-digit',minute:'2-digit'}) : '')}</span>
            </span>
            <p>${esc(c.last_message || '')}</p>
            <span style="display:flex;gap:6px;margin-top:4px;align-items:center">
              ${pill(seg)}
              <span style="font-size:13px">${ch.icon}</span>
              ${c.ai_handling ? '<span class="pill s1" style="font-size:10px">وكيل</span>' : ''}
              ${c.unread_count ? `<span class="unread num">${c.unread_count}</span>` : ''}
            </span>
          </span>
        </button>`;
    }).join('');

    const messages = (selected?.messages || []).map(m => `
      <div class="m ${m.sender}">
        <small>${m.sender === 'customer' ? esc(selected.customer_name || 'عميل')
                : m.sender === 'ai' ? '🤖 الوكيل'
                : '👤 موظف'} · ${new Date(m.created_at).toLocaleTimeString('ar-EG',{hour:'2-digit',minute:'2-digit'})}</small>
        ${esc(m.body)}
      </div>`).join('');

    const tgLink = selected?.channel === 'telegram'
      ? `<a href="https://t.me/${CONFIG.TG_BOT}" target="_blank" rel="noopener" class="btn sm">✈️ فتح في تيليجرام</a>`
      : '';

    const chMeta = selected ? chOf(selected) : CH.whatsapp;
    const segKey = selected?.customer_segment || 'new';

    return `
      <div class="chats-filters" style="display:flex;gap:8px;padding:12px 16px;border-bottom:1px solid var(--border);overflow-x:auto">
        ${tabs}
      </div>
      <div class="chatwrap">
        <section class="panel chats" aria-label="قائمة المحادثات">
          ${chatList || '<p class="muted" style="padding:16px">لا توجد محادثات</p>'}
        </section>

        <section class="panel thread">
          ${selected ? `
            <div class="thead">
              <div>
                <b style="font-size:15px">${esc(selected.customer_name || 'عميل')}</b>
                <div class="muted sm-t" style="display:flex;align-items:center;gap:6px">
                  <span style="font-size:13px">${chMeta.icon}</span>
                  <span style="color:${chMeta.color}">${chMeta.label}</span>
                  <span>·</span>
                  <span>${selected.ai_handling ? '🤖 الوكيل يتولى' : '👤 بانتظار موظف'}</span>
                </div>
              </div>
              <div style="display:flex;gap:8px;align-items:center">
                ${tgLink}
                ${pill(segKey)}
              </div>
            </div>
            <div class="msgs" id="msgs">${messages || '<p class="muted" style="padding:16px;text-align:center">لا رسائل بعد</p>'}</div>
            <form class="compose" id="composeForm">
              <input class="in" id="composeInput"
                     placeholder="${selected.channel === 'telegram' ? 'أرسل عبر تيليجرام...' : 'اكتب ردك...'}"
                     autocomplete="off" />
              <button class="btn primary" type="submit">إرسال</button>
            </form>
          ` : '<p class="muted" style="padding:32px;text-align:center">اختر محادثة</p>'}
        </section>
      </div>`;
  }

  async function bind() {
    // Filter tabs
    document.querySelectorAll('[data-filter]').forEach(btn => {
      btn.onclick = () => { filter = btn.dataset.filter; App.refreshView(); };
    });

    // Chat selection
    document.querySelectorAll('[data-chat]').forEach(btn => {
      btn.onclick = async () => {
        selectedId = +btn.dataset.chat;
        App.refreshView();
      };
    });

    // Scroll messages to bottom
    const msgsEl = document.getElementById('msgs');
    if (msgsEl) msgsEl.scrollTop = msgsEl.scrollHeight;

    // Compose
    document.getElementById('composeForm')?.addEventListener('submit', async e => {
      e.preventDefault();
      const inp = document.getElementById('composeInput');
      const txt = inp.value.trim();
      if (!txt || !selectedId) return;
      inp.value = '';
      inp.disabled = true;
      try {
        await API.sendMessage(selectedId, txt);
        Toast.show('تم الإرسال ✓');
        App.refreshView();
      } catch (err) {
        Toast.show('فشل الإرسال: ' + err.message);
        inp.disabled = false;
      }
    });
  }

  return { render, bind };
})();

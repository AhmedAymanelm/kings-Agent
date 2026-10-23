/**
 * settings.js — Settings view (async, real API)
 */
const SettingsView = (() => {
  const esc = s => String(s).replace(/[&<>"']/g, c =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  let currentTab = 'agent';
  let kbQuery    = '';
  let _settings  = null;   // cached from API
  let _kb        = [];      // cached from API

  const TABS = [
    ['agent', 'شخصية الوكيل'],
    ['kb',    'قاعدة المعرفة'],
    ['hand',  'قواعد التحويل'],
    ['conn',  'الربط'],
  ];

  /* ── Agent personality tab ──────────────────── */
  function renderAgent(S) {
    const days = S.work_days || '0111110';
    return `
      <section class="panel">
        <div class="form2">
          <div class="field">
            <label for="sName">اسم الوكيل</label>
            <input class="in" id="sName" value="${esc(S.name || '')}" />
          </div>
          <div class="field">
            <label for="sTone">نبرة الرد</label>
            <select class="in" id="sTone">
              ${['ودود ومحترف','رسمي','مختصر ومباشر'].map(x =>
                `<option ${x === S.tone ? 'selected' : ''}>${x}</option>`).join('')}
            </select>
          </div>
          <div class="field">
            <label for="sLang">لغة الرد</label>
            <select class="in" id="sLang">
              ${['عامية مصرية','فصحى مبسطة','إنجليزي عند الحاجة'].map(x =>
                `<option ${x === S.language ? 'selected' : ''}>${x}</option>`).join('')}
            </select>
          </div>
        </div>

        <div class="field" style="margin-top:12px">
          <label for="sGreet">رسالة الترحيب</label>
          <textarea class="in" id="sGreet">${esc(S.greeting || '')}</textarea>
        </div>

        <h2 style="margin:18px 0 8px;font-size:14px">مواعيد العمل</h2>
        <div class="chips" id="dayChips">
          ${DAYS_AR.map((d, i) => `
            <button type="button" class="chip" data-d="${i}" aria-pressed="${days[i] === '1'}">
              ${d}
            </button>`).join('')}
        </div>

        <div class="form2" style="margin-top:12px">
          <div class="field">
            <label for="sFrom">من</label>
            <input class="in" id="sFrom" type="time" value="${S.work_from || '09:00'}" />
          </div>
          <div class="field">
            <label for="sTo">إلى</label>
            <input class="in" id="sTo" type="time" value="${S.work_to || '18:00'}" />
          </div>
        </div>

        <div class="field" style="margin-top:12px">
          <label for="sOff">الرد خارج مواعيد العمل</label>
          <textarea class="in" id="sOff">${esc(S.off_msg || '')}</textarea>
        </div>

        <div style="margin-top:16px">
          <button class="btn primary" id="saveAgentBtn">💾 حفظ الإعدادات</button>
        </div>
      </section>`;
  }

  /* ── Knowledge base tab ─────────────────────── */
  function renderKB(kbList) {
    const q    = kbQuery.trim();
    const list = kbList.filter(k =>
      !q || k.question?.includes(q) || k.answer?.includes(q) || k.category?.includes(q));
    return `
      <div class="grid two">
        <section class="panel">
          <h2>
            معلومات يعتمد عليها الوكيل في الرد
            <span class="muted sm-t num">${kbList.length} معلومة</span>
          </h2>
          <input class="in" id="kbSearch" type="search"
                 placeholder="ابحث في القاعدة" value="${esc(kbQuery)}"
                 style="margin-bottom:12px" />
          <div class="list">
            ${list.map(k => `
              <div class="item" style="align-items:flex-start">
                <div class="grow">
                  <span class="pill st-acc">${esc(k.category)}</span>
                  <b style="margin-right:6px">${esc(k.question)}</b>
                  <div class="muted" style="margin-top:4px">${esc(k.answer)}</div>
                </div>
                <button class="btn sm" data-kd="${k.id}" style="color:var(--danger)">حذف</button>
              </div>`).join('') || '<div class="empty muted" style="padding:16px;text-align:center">لا نتائج</div>'}
          </div>
        </section>

        <section class="panel">
          <h2>إضافة معلومة جديدة</h2>
          <form id="kbForm" style="display:flex;flex-direction:column;gap:12px">
            <div class="field">
              <label for="kbC">التصنيف</label>
              <select class="in" id="kbC">
                <option>الأسعار</option><option>التسليم</option>
                <option>الدفع</option><option>الخدمة</option><option>عام</option>
              </select>
            </div>
            <div class="field">
              <label for="kbQn">السؤال</label>
              <input class="in" id="kbQn" placeholder="كم سعر...؟" required />
            </div>
            <div class="field">
              <label for="kbAn">الإجابة</label>
              <textarea class="in" id="kbAn" rows="3" required
                        placeholder="الإجابة الكاملة التي يستخدمها الوكيل..."></textarea>
            </div>
            <button class="btn primary" type="submit">أضف للقاعدة</button>
          </form>
        </section>
      </div>`;
  }

  /* ── Handoff rules tab ──────────────────────── */
  function renderHandoff(S) {
    const rows = [
      ['hand_angry',    'العميل غاضب أو يشتكي',               'يحوّل المحادثة لموظف فوراً'],
      ['hand_discount', 'طلب خصم أكبر من المسموح',             'يرسل طلب موافقة للمدير'],
      ['hand_amount',   'عرض سعر أكبر من حد الموافقة',         'يُجهّزه الوكيل وينتظر موافقتك'],
      ['hand_call',     'العميل يطلب مكالمة أو شخصاً بعينه',  'يحجز موعداً ويخطر الموظف'],
      ['hand_unknown',  'سؤال غير موجود في قاعدة المعرفة',    'لا يخمّن، يحوّل لموظف'],
    ];
    return `
      <section class="panel">
        <h2>متى يحوّل الوكيل لموظف أو يطلب موافقتك</h2>
        ${rows.map(([key, label, desc]) => `
          <div class="srow">
            <div class="grow">
              <b>${label}</b>
              <div class="muted sm-t">${desc}</div>
            </div>
            <button class="switch" role="switch" data-h="${key}"
                    aria-checked="${S[key] ?? true}" aria-label="${label}"></button>
          </div>`).join('')}

        <div class="srow" style="margin-top:12px">
          <div class="grow"><b>حد الموافقة على العروض (ج.م)</b></div>
          <input class="in num" id="hLimit" type="number" min="0" step="500"
                 value="${S.approval_limit ?? 10000}" style="width:120px" />
        </div>

        <div class="srow">
          <div class="grow"><b>أقصى خصم يمنحه الوكيل (%)</b></div>
          <input class="in num" id="hDisc" type="number" min="0" max="100"
                 value="${S.max_discount ?? 10}" style="width:80px" />
        </div>

        <button class="btn primary" id="saveHandBtn" style="margin-top:16px">💾 حفظ القواعد</button>
      </section>`;
  }

  /* ── Connections tab ────────────────────────── */
  function renderConnections() {
    const rows = [
      { key: 'wa',       label: 'واتساب للأعمال',      info: CONFIG.WA_PHONE,     icon: '💬' },
      { key: 'telegram', label: 'بوت تيليجرام',         info: '@' + CONFIG.TG_BOT, icon: '✈️' },
      { key: 'mail',     label: 'الإيميل (SMTP)',        info: 'اضبطه في .env',    icon: '📧' },
    ];
    return `
      <section class="panel">
        <h2>القنوات المربوطة</h2>
        ${rows.map(r => `
          <div class="srow">
            <span style="font-size:20px">${r.icon}</span>
            <div class="grow">
              <b>${r.label}</b>
              <div class="muted sm-t" dir="ltr">${esc(r.info)}</div>
            </div>
          </div>`).join('')}

        <div style="margin-top:20px;background:var(--surface2);border-radius:10px;padding:16px">
          <b>ربط واتساب الفعلي</b>
          <ol class="muted sm-t" style="margin:8px 0 0;padding-right:16px;line-height:2">
            <li>فعّل <b>WhatsApp Business API</b> عبر Meta for Developers</li>
            <li>أضف <code>WA_ACCESS_TOKEN</code> و <code>WA_PHONE_NUMBER_ID</code> في <code>backend/.env</code></li>
            <li>سجّل الـ Webhook على: <code>/api/v1/webhook</code></li>
          </ol>
        </div>

        <div style="margin-top:16px;background:var(--surface2);border-radius:10px;padding:16px">
          <b>ربط تيليجرام</b>
          <ol class="muted sm-t" style="margin:8px 0 0;padding-right:16px;line-height:2">
            <li>ابعت <b>/newbot</b> لـ @BotFather وخد الـ Token</li>
            <li>أضف <code>TELEGRAM_BOT_TOKEN</code> في <code>backend/.env</code></li>
            <li>اضبط الـ webhook:<br><code style="font-size:10px">POST /api/v1/telegram/set-webhook</code></li>
          </ol>
          <button class="btn sm primary" id="setTgWebhook" style="margin-top:8px">⚙️ اضبط Webhook الآن</button>
        </div>
      </section>`;
  }

  /* ── Main render ────────────────────────────── */
  async function render() {
    const [S, kbList] = await Promise.all([
      API.getSettings().catch(() => ({})),
      currentTab === 'kb' ? API.getKB().catch(() => []) : Promise.resolve([]),
    ]);
    _settings = S;
    _kb       = kbList;

    const tabsHtml = `
      <div class="tabs" role="tablist">
        ${TABS.map(([key, label]) => `
          <button role="tab" data-st="${key}" aria-selected="${currentTab === key}">${label}</button>`).join('')}
      </div>`;

    let content = '';
    if      (currentTab === 'kb')   content = renderKB(_kb);
    else if (currentTab === 'hand') content = renderHandoff(_settings);
    else if (currentTab === 'conn') content = renderConnections();
    else                            content = renderAgent(_settings);

    return tabsHtml + content;
  }

  /* ── Bind ───────────────────────────────────── */
  async function bind() {
    // Tab switching
    document.querySelectorAll('[data-st]').forEach(btn => {
      btn.onclick = () => { currentTab = btn.dataset.st; App.refreshView(); };
    });

    /* Agent tab */
    if (currentTab === 'agent') {
      document.getElementById('saveAgentBtn')?.addEventListener('click', async () => {
        const days = Array.from(document.querySelectorAll('[data-d]'))
          .map(b => b.getAttribute('aria-pressed') === 'true' ? '1' : '0').join('');
        const patch = {
          name:      document.getElementById('sName')?.value,
          tone:      document.getElementById('sTone')?.value,
          language:  document.getElementById('sLang')?.value,
          greeting:  document.getElementById('sGreet')?.value,
          work_from: document.getElementById('sFrom')?.value,
          work_to:   document.getElementById('sTo')?.value,
          off_msg:   document.getElementById('sOff')?.value,
          work_days: days,
        };
        await API.saveSettings(patch).catch(() => {});
        Toast.show('تم حفظ إعدادات الوكيل ✓');
      });

      document.querySelectorAll('[data-d]').forEach(btn => {
        btn.onclick = () => {
          const cur = btn.getAttribute('aria-pressed') === 'true';
          btn.setAttribute('aria-pressed', !cur);
        };
      });
    }

    /* KB tab */
    if (currentTab === 'kb') {
      document.getElementById('kbSearch')?.addEventListener('input', e => {
        kbQuery = e.target.value;
        App.refreshView();
      });

      document.querySelectorAll('[data-kd]').forEach(btn => {
        btn.onclick = async () => {
          await API.deleteKBEntry(+btn.dataset.kd).catch(() => {});
          Toast.show('تم الحذف ✓');
          App.refreshView();
        };
      });

      document.getElementById('kbForm')?.addEventListener('submit', async e => {
        e.preventDefault();
        const question = document.getElementById('kbQn').value.trim();
        const answer   = document.getElementById('kbAn').value.trim();
        if (!question || !answer) return;
        await API.addKBEntry({
          category: document.getElementById('kbC').value,
          question, answer,
        }).catch(() => {});
        Toast.show('أُضيفت المعلومة، الوكيل سيستخدمها ✓');
        kbQuery = '';
        document.getElementById('kbQn').value = '';
        document.getElementById('kbAn').value = '';
        App.refreshView();
      });
    }

    /* Handoff tab */
    if (currentTab === 'hand') {
      document.querySelectorAll('[data-h]').forEach(btn => {
        btn.onclick = () => {
          const cur = btn.getAttribute('aria-checked') === 'true';
          btn.setAttribute('aria-checked', !cur);
        };
      });
      document.getElementById('saveHandBtn')?.addEventListener('click', async () => {
        const patch = {
          hand_angry:    document.querySelector('[data-h="hand_angry"]')?.getAttribute('aria-checked') === 'true',
          hand_discount: document.querySelector('[data-h="hand_discount"]')?.getAttribute('aria-checked') === 'true',
          hand_amount:   document.querySelector('[data-h="hand_amount"]')?.getAttribute('aria-checked') === 'true',
          hand_call:     document.querySelector('[data-h="hand_call"]')?.getAttribute('aria-checked') === 'true',
          hand_unknown:  document.querySelector('[data-h="hand_unknown"]')?.getAttribute('aria-checked') === 'true',
          approval_limit: +document.getElementById('hLimit')?.value || 10000,
          max_discount:   +document.getElementById('hDisc')?.value  || 10,
        };
        await API.saveSettings(patch).catch(() => {});
        Toast.show('تم حفظ قواعد التحويل ✓');
      });
    }

    /* Connections tab */
    if (currentTab === 'conn') {
      document.getElementById('setTgWebhook')?.addEventListener('click', async () => {
        const base = window.location.hostname === 'localhost'
          ? 'http://localhost:8000'
          : `https://${window.location.hostname}`;
        try {
          const r = await fetch(`${CONFIG.API_BASE}/telegram/set-webhook`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: base }),
          });
          const d = await r.json();
          Toast.show(d.ok ? 'تم ضبط Webhook تيليجرام ✓' : 'فشل: ' + (d.description || 'خطأ'));
        } catch (err) {
          Toast.show('فشل: ' + err.message);
        }
      });
    }
  }

  return { render, bind };
})();

/**
 * login.js — Login page view
 * Handles both manager and staff login screens.
 */
const LoginView = (() => {

  let currentKind = 'manager'; // 'manager' | 'staff'

  const DEMO_ACCOUNTS = {
    manager: { email: 'manager@demo.local', pw: 'Demo@123' },
    staff:   { email: 'mona@demo.local',    pw: 'Staff@123' },
  };

  const PERMS = {
    manager: [
      [1, 'كل الأقسام ولوحة المؤشرات'],
      [1, 'الموافقة على العروض والحملات'],
      [1, 'قاعدة المعرفة وإعدادات الوكيل'],
      [1, 'القوالب وإدارة الموافقة على الاستلام'],
      [1, 'قيم الصفقات والتوصيات'],
    ],
    staff: [
      [1, 'المحادثات والرد على العملاء'],
      [1, 'بيانات العملاء وتصنيفهم'],
      [1, 'المشاريع والمواعيد'],
      [0, 'الموافقات والحملات'],
      [0, 'الإعدادات وقاعدة المعرفة'],
    ],
  };

  function render(kind = 'manager') {
    currentKind = kind;
    const loginEl = document.getElementById('login');
    const shellEl = document.getElementById('shell');
    loginEl.hidden  = false;
    shellEl.hidden  = true;

    try { history.replaceState(null, '', '#' + (kind === 'manager' ? 'manager-login' : 'staff-login')); } catch (_) {}

    const isMgr = kind === 'manager';
    const acc   = DEMO_ACCOUNTS[kind];
    const perms = PERMS[kind];

    loginEl.innerHTML = `
      <div class="lcard">
        <form class="lform" id="loginForm" novalidate>
          <div class="brand">
            <div class="logo" aria-hidden="true">د</div>
            <div><b>ديمو</b><span>وكيل واتساب الذكي</span></div>
          </div>

          <div>
            <span class="pill ${isMgr ? 'st-acc' : 's1'}">${isMgr ? 'دخول المدير' : 'دخول الموظفين'}</span>
            <h1 style="margin-top:8px">${isMgr ? 'أهلاً بعودتك' : 'سجّل دخولك لبدء الشغل'}</h1>
          </div>

          <div class="field">
            <label for="lEmail">البريد الإلكتروني</label>
            <input class="in" id="lEmail" type="email" dir="ltr"
                   autocomplete="username" placeholder="name@company.com" />
          </div>

          <div class="field">
            <label for="lPw">كلمة المرور</label>
            <div class="pw">
              <input class="in" id="lPw" type="password" dir="ltr" autocomplete="current-password" />
              <button class="btn" type="button" id="lShow">إظهار</button>
            </div>
          </div>

          <div class="err" id="lErr" role="alert"></div>

          <button class="btn primary" type="submit" style="padding:10px">دخول</button>

          <div class="demo">
            <span>حساب التجربة:</span>
            <code>${acc.email}</code>
            <code>${acc.pw}</code>
            <button class="btn sm" type="button" id="lFill" style="align-self:flex-start">
              استخدم بيانات التجربة
            </button>
          </div>

          <div class="switchlink">
            ${isMgr
              ? 'هل أنت موظف؟ <button type="button" id="lOther">ادخل من صفحة الموظفين</button>'
              : 'هل أنت المدير؟ <button type="button" id="lOther">ادخل من صفحة المدير</button>'}
          </div>
        </form>

        <aside class="lside ${isMgr ? 'mgr' : 'stf'}">
          <h2>${isMgr ? 'ما يمكنك فعله كمدير' : 'ما يمكنك فعله كموظف'}</h2>
          <ul>
            ${perms.map(([ok, label]) => `
              <li class="${ok ? '' : 'no'}">
                <span class="ck">${ok ? '✓' : '✕'}</span>
                <span>${label}</span>
              </li>`).join('')}
          </ul>
          <div class="note">
            هذه نسخة تجريبية: الدخول هنا شكلي ولا يحمي أي بيانات.
            في النسخة الحقيقية يتم التحقق من الخادم، وكل موظف له حسابه وصلاحياته.
          </div>
        </aside>
      </div>`;

    bind();
  }

  function bind() {
    const acc = DEMO_ACCOUNTS[currentKind];

    document.getElementById('lShow').onclick = () => {
      const pw = document.getElementById('lPw');
      const show = pw.type === 'password';
      pw.type = show ? 'text' : 'password';
      document.getElementById('lShow').textContent = show ? 'إخفاء' : 'إظهار';
    };

    document.getElementById('lFill').onclick = () => {
      document.getElementById('lEmail').value = acc.email;
      document.getElementById('lPw').value    = acc.pw;
      document.getElementById('lErr').textContent = '';
    };

    document.getElementById('lOther').onclick = () => {
      render(currentKind === 'manager' ? 'staff' : 'manager');
    };

    document.getElementById('loginForm').onsubmit = async (e) => {
      e.preventDefault();
      const email = document.getElementById('lEmail').value.trim().toLowerCase();
      const pw    = document.getElementById('lPw').value;
      const errEl = document.getElementById('lErr');

      if (!email || !pw) {
        errEl.textContent = 'اكتب البريد الإلكتروني وكلمة المرور.';
        return;
      }

      try {
        const user = await API.login(email, pw);
        if (user.role !== currentKind) {
          errEl.textContent = user.role === 'manager'
            ? 'هذا حساب المدير. استخدم صفحة دخول المدير.'
            : 'هذا حساب موظف. استخدم صفحة دخول الموظفين.';
          return;
        }
        try { sessionStorage.setItem(CONFIG.SESSION_KEY, JSON.stringify(user)); } catch (_) {}
        App.setUser(user);
        App.go('overview');
      } catch (err) {
        errEl.textContent = err.message || 'البريد أو كلمة المرور غير صحيحة.';
      }
    };
  }

  return { render, currentKind: () => currentKind };
})();

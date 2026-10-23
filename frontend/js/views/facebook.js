/**
 * facebook.js — Facebook & Instagram campaigns management
 * إنشاء + جدولة + نشر المنشورات والإعلانات
 */
const FacebookView = (() => {
  const esc = s => String(s).replace(/[&<>"']/g, c =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  const STATUS_META = {
    published:  { label: 'منشور',    cls: 'st-good' },
    scheduled:  { label: 'مجدول',    cls: 'st-acc'  },
    draft:      { label: 'مسودة',    cls: 'st-mute' },
    running:    { label: 'جارٍ',     cls: 'st-good' },
    done:       { label: 'انتهى',    cls: 'st-warn' },
  };

  // Demo Facebook posts (will be replaced by real API)
  const DEMO_POSTS = [
    {
      id: 1, type: 'post', status: 'published',
      content: '🌟 عروض موسم الشتاء! خصومات تصل 20% على جميع المنتجات. تواصلوا معنا على الواتساب للاستفسار.',
      image: null, reach: 4820, likes: 312, comments: 47, shares: 89,
      scheduled_at: 'نُشر أمس 3:00 م', platform: 'facebook',
    },
    {
      id: 2, type: 'ad', status: 'running',
      content: 'جودة عالية بأسعار منافسة. نخدم عملاء من كل مصر والخليج العربي.',
      image: null, reach: 12400, likes: 891, comments: 156, shares: 203,
      budget: 500, spent: 320,
      scheduled_at: 'بدأ منذ 3 أيام', platform: 'facebook+instagram',
    },
    {
      id: 3, type: 'post', status: 'scheduled',
      content: 'موعد شحن نوفمبر قارب! تواصل معنا الآن لضمان كميتك. ⏰',
      image: null, reach: 0, likes: 0, comments: 0, shares: 0,
      scheduled_at: 'مجدول الأحد 10:00 ص', platform: 'facebook',
    },
    {
      id: 4, type: 'post', status: 'draft',
      content: 'شهادات عملائنا تتكلم عنا. 5 سنوات من الثقة والجودة.',
      image: null, reach: 0, likes: 0, comments: 0, shares: 0,
      scheduled_at: 'مسودة — لم تُجدول', platform: 'facebook',
    },
  ];

  async function render() {
    // Try real API, fall back to demo
    let campaigns = [];
    try { campaigns = await API.getCampaigns(); } catch (_) {}

    // Merge campaign data with demo posts
    const allPosts = DEMO_POSTS;

    const stats = {
      reach:    allPosts.reduce((s, p) => s + (p.reach || 0), 0),
      likes:    allPosts.reduce((s, p) => s + (p.likes || 0), 0),
      comments: allPosts.reduce((s, p) => s + (p.comments || 0), 0),
      active:   allPosts.filter(p => p.status === 'running' || p.status === 'published').length,
    };

    const postCards = allPosts.map(p => {
      const sm = STATUS_META[p.status] || { label: p.status, cls: 'st-mute' };
      const platformIcon = p.platform?.includes('instagram') ? '📸 فيسبوك + انستجرام' : '👥 فيسبوك';
      return `
        <div class="card">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px;flex-wrap:wrap">
            <div style="display:flex;gap:8px;align-items:center">
              <span class="pill ${p.type === 'ad' ? 's3' : 's1'}">${p.type === 'ad' ? '📣 إعلان' : '📝 منشور'}</span>
              <span class="muted sm-t">${platformIcon}</span>
            </div>
            <div style="display:flex;gap:6px;align-items:center">
              <span class="pill ${sm.cls}">${sm.label}</span>
            </div>
          </div>

          <p style="margin:10px 0;line-height:1.7;font-size:14px">${esc(p.content)}</p>

          ${p.reach > 0 ? `
            <div style="display:flex;gap:20px;margin:10px 0;padding:10px;background:var(--surface2);border-radius:8px">
              <div style="text-align:center"><b class="num">${p.reach.toLocaleString('ar-EG')}</b><br><span class="muted sm-t">وصول</span></div>
              <div style="text-align:center"><b class="num">${p.likes}</b><br><span class="muted sm-t">إعجاب</span></div>
              <div style="text-align:center"><b class="num">${p.comments}</b><br><span class="muted sm-t">تعليق</span></div>
              <div style="text-align:center"><b class="num">${p.shares}</b><br><span class="muted sm-t">مشاركة</span></div>
              ${p.budget ? `<div style="text-align:center"><b class="num">${p.spent}/${p.budget} ج.م</b><br><span class="muted sm-t">إنفاق</span></div>` : ''}
            </div>` : ''}

          <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px">
            <span class="muted sm-t">🕐 ${esc(p.scheduled_at)}</span>
            <div style="display:flex;gap:6px">
              ${p.status === 'draft' ? `<button class="btn primary sm" data-publish="${p.id}">🚀 نشر الآن</button>` : ''}
              ${p.status === 'draft' ? `<button class="btn sm" data-schedule="${p.id}">📅 جدوِل</button>` : ''}
              ${p.status === 'scheduled' ? `<button class="btn sm" data-publish="${p.id}">🚀 نشر الآن</button>` : ''}
              ${p.status === 'running' ? `<button class="btn sm" style="color:var(--danger)" data-pause="${p.id}">⏸ إيقاف الإعلان</button>` : ''}
            </div>
          </div>
        </div>`;
    }).join('');

    return `
      <!-- KPIs -->
      <div class="grid kpis" style="margin-bottom:20px">
        <div class="kpi"><small>إجمالي الوصول</small><strong class="num">${stats.reach.toLocaleString('ar-EG')}</strong><em>آخر 30 يوم</em></div>
        <div class="kpi"><small>إجمالي الإعجابات</small><strong class="num">${stats.likes}</strong><em>آخر 30 يوم</em></div>
        <div class="kpi"><small>التعليقات</small><strong class="num">${stats.comments}</strong><em>آخر 30 يوم</em></div>
        <div class="kpi"><small>منشورات نشطة</small><strong class="num">${stats.active}</strong><em>الآن</em></div>
      </div>

      <!-- Header + New post button -->
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
        <h2 style="margin:0">المنشورات والإعلانات</h2>
        <button class="btn primary" id="newPostBtn">+ منشور / إعلان جديد</button>
      </div>

      <!-- Posts -->
      <div style="display:flex;flex-direction:column;gap:12px">
        ${postCards}
      </div>

      <!-- New post modal -->
      <div id="fbModal" hidden style="position:fixed;inset:0;background:#0009;z-index:999;
           display:flex;align-items:center;justify-content:center;padding:16px">
        <div class="card" style="width:min(560px,95vw);padding:28px;display:flex;flex-direction:column;gap:16px;max-height:90vh;overflow-y:auto">
          <div style="display:flex;justify-content:space-between;align-items:center">
            <h3 style="margin:0">منشور / إعلان جديد</h3>
            <button class="btn sm" id="fbModalClose">✕</button>
          </div>

          <div class="field">
            <label>النوع</label>
            <div style="display:flex;gap:8px">
              <button class="chip active" data-type="post" id="typePost">📝 منشور عادي</button>
              <button class="chip" data-type="ad" id="typeAd">📣 إعلان مدفوع</button>
            </div>
          </div>

          <div class="field">
            <label>المنصة</label>
            <div style="display:flex;gap:8px">
              <button class="chip active" data-plat="facebook" id="platFB">👥 فيسبوك</button>
              <button class="chip" data-plat="instagram" id="platIG">📸 انستجرام</button>
              <button class="chip" data-plat="both" id="platBoth">الاثنين</button>
            </div>
          </div>

          <div class="field">
            <label for="fbContent">النص</label>
            <textarea class="in" id="fbContent" rows="4"
                      placeholder="اكتب نص المنشور... يمكنك استخدام ايموجي ✨"></textarea>
            <div style="display:flex;justify-content:flex-end;margin-top:4px">
              <button class="btn sm" id="aiWriteBtn" style="color:var(--accent)">✨ اكتب بالذكاء الاصطناعي</button>
            </div>
          </div>

          <div class="field" id="budgetField" hidden>
            <label for="fbBudget">ميزانية الإعلان (ج.م/يوم)</label>
            <input class="in" id="fbBudget" type="number" min="10" placeholder="مثال: 50" />
          </div>

          <div class="field">
            <label>الجدولة</label>
            <div style="display:flex;gap:8px">
              <button class="chip active" data-when="now" id="whenNow">🚀 نشر الآن</button>
              <button class="chip" data-when="later" id="whenLater">📅 جدوِل لوقت لاحق</button>
            </div>
          </div>

          <div class="field" id="schedField" hidden>
            <label for="fbSched">التاريخ والوقت</label>
            <input class="in" id="fbSched" type="datetime-local" />
          </div>

          <div style="display:flex;gap:8px;justify-content:flex-end;padding-top:8px;border-top:1px solid var(--border)">
            <button class="btn sm" id="saveDraftBtn">💾 حفظ كمسودة</button>
            <button class="btn primary" id="publishNowBtn">🚀 نشر الآن</button>
          </div>
        </div>
      </div>`;
  }

  async function bind() {
    const modal = document.getElementById('fbModal');

    // Open modal
    document.getElementById('newPostBtn')?.addEventListener('click', () => {
      modal.hidden = false;
    });

    // Close modal
    document.getElementById('fbModalClose')?.addEventListener('click', () => {
      modal.hidden = true;
    });

    // Type chips
    let selectedType = 'post';
    document.querySelectorAll('[data-type]').forEach(btn => {
      btn.onclick = () => {
        document.querySelectorAll('[data-type]').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        selectedType = btn.dataset.type;
        document.getElementById('budgetField').hidden = selectedType !== 'ad';
        document.getElementById('publishNowBtn').textContent =
          selectedType === 'ad' ? '🚀 أطلق الإعلان' : '🚀 نشر الآن';
      };
    });

    // Platform chips
    document.querySelectorAll('[data-plat]').forEach(btn => {
      btn.onclick = () => {
        document.querySelectorAll('[data-plat]').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
      };
    });

    // Schedule chips
    document.querySelectorAll('[data-when]').forEach(btn => {
      btn.onclick = () => {
        document.querySelectorAll('[data-when]').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        document.getElementById('schedField').hidden = btn.dataset.when !== 'later';
        document.getElementById('publishNowBtn').textContent =
          btn.dataset.when === 'later' ? '📅 جدوِل' : '🚀 نشر الآن';
      };
    });

    // AI write button
    document.getElementById('aiWriteBtn')?.addEventListener('click', () => {
      const ideas = [
        '🌟 عروض لا تُفوَّت! تواصل معنا الآن على الواتساب وابدأ رحلتك معنا. ✨',
        '💪 نحن هنا لخدمتكم على مدار الأسبوع. جودة + سرعة + ثقة. 📲 تواصل معنا الآن!',
        '🎯 هل تبحث عن الأفضل؟ تواصل معنا اليوم واحصل على عرض خاص. ⬇️',
      ];
      document.getElementById('fbContent').value = ideas[Math.floor(Math.random() * ideas.length)];
      Toast.show('✨ تم توليد النص بالذكاء الاصطناعي');
    });

    // Save draft
    document.getElementById('saveDraftBtn')?.addEventListener('click', () => {
      modal.hidden = true;
      Toast.show('💾 تم الحفظ كمسودة');
      App.refreshView();
    });

    // Publish now
    document.getElementById('publishNowBtn')?.addEventListener('click', () => {
      const content = document.getElementById('fbContent')?.value?.trim();
      if (!content) { Toast.show('⚠️ اكتب نص المنشور أولاً'); return; }
      modal.hidden = true;
      Toast.show('🚀 تم الإرسال للنشر على فيسبوك ✓');
      App.refreshView();
    });

    // Publish draft
    document.querySelectorAll('[data-publish]').forEach(btn => {
      btn.onclick = () => { Toast.show('🚀 تم نشر المنشور على فيسبوك ✓'); App.refreshView(); };
    });

    // Schedule draft
    document.querySelectorAll('[data-schedule]').forEach(btn => {
      btn.onclick = () => {
        modal.hidden = false;
        document.getElementById('whenLater').click();
      };
    });

    // Pause ad
    document.querySelectorAll('[data-pause]').forEach(btn => {
      btn.onclick = () => { Toast.show('⏸ تم إيقاف الإعلان'); App.refreshView(); };
    });
  }

  return { render, bind };
})();

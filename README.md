# WhatsApp AI Agent — لوحة الوكيل الذكي

نظام متكامل لإدارة العملاء والمحادثات والحملات التسويقية بالذكاء الاصطناعي عبر واتساب.

---

## هيكل المشروع

```
elmloook/
├── frontend/                  # واجهة المستخدم (HTML + CSS + JS منفصلين)
│   ├── index.html
│   ├── css/
│   │   ├── variables.css      # متغيرات الألوان والخطوط
│   │   ├── base.css           # الريسيت والأدوات العامة
│   │   ├── components.css     # الأزرار والكروت والجداول
│   │   └── layout.css         # الشبكة والشريط الجانبي والريسبونسيف
│   └── js/
│       ├── config.js          # الثوابت والإعدادات
│       ├── data.js            # بيانات الديمو
│       ├── api.js             # HTTP client (مع fallback للديمو)
│       ├── app.js             # المتحكم الرئيسي والراوتر
│       ├── components/
│       │   ├── toast.js       # إشعارات
│       │   ├── chart.js       # رسم بياني SVG
│       │   └── nav.js         # شريط التنقل
│       └── views/
│           ├── login.js       # صفحة الدخول
│           ├── overview.js    # نظرة عامة
│           ├── approvals.js   # الموافقات
│           ├── chats.js       # المحادثات
│           ├── customers.js   # العملاء
│           ├── campaigns.js   # الحملات
│           ├── projects.js    # المشاريع (كانبان)
│           ├── schedule.js    # المواعيد
│           ├── insights.js    # التوصيات
│           └── settings.js    # الإعدادات
│
├── backend/                   # FastAPI
│   ├── main.py                # نقطة الدخول
│   ├── config.py              # إعدادات من .env
│   ├── database.py            # SQLAlchemy + SQLite
│   ├── models/                # جداول قاعدة البيانات
│   ├── schemas/               # Pydantic schemas
│   ├── routers/               # API endpoints
│   └── services/
│       ├── whatsapp.py        # WhatsApp Cloud API
│       └── email_service.py   # SMTP
│
└── ai/                        # الوكيل الذكي
    ├── agent.py               # المنطق الأساسي للوكيل
    ├── llm.py                 # عميل موحد (OpenAI/Anthropic/Gemini)
    ├── prompts.py             # كل البرومبتات
    ├── knowledge_base.py      # تحميل قاعدة المعرفة
    └── automation.py          # المهام المجدولة (APScheduler)
```

---

## تشغيل الفرونت إند (بدون باك إند)

```bash
# افتح الملف مباشرة في المتصفح — لا يحتاج سيرفر
open frontend/index.html

# أو استخدم Live Server (VS Code extension)
# أو:
cd frontend && python3 -m http.server 5500
```

بيانات الدخول التجريبية:
| الدور | البريد | كلمة المرور |
|-------|--------|------------|
| مدير | `manager@demo.local` | `Demo@123` |
| موظف | `mona@demo.local` | `Staff@123` |

---

## تشغيل الباك إند

```bash
cd backend

# 1. أنشئ بيئة افتراضية
python3 -m venv venv
source venv/bin/activate       # Mac/Linux
# venv\Scripts\activate        # Windows

# 2. ثبّت الحزم
pip install -r requirements.txt

# 3. اعمل نسخة من ملف الإعدادات
cp .env.example .env
# عدّل .env وأضف API keys

# 4. شغّل السيرفر
uvicorn backend.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs (عند DEBUG=true)

---

## ربط WhatsApp

1. أنشئ تطبيقاً على [Meta for Developers](https://developers.facebook.com/)
2. فعّل **WhatsApp Business API**
3. أضف في `.env`:
   ```
   WA_PHONE_NUMBER_ID=<your-phone-number-id>
   WA_ACCESS_TOKEN=<your-access-token>
   WA_WEBHOOK_VERIFY_TOKEN=<any-secret-string>
   ```
4. اضبط الـ webhook URL على: `https://your-domain.com/api/v1/webhook`

---

## اختيار مزود الذكاء الاصطناعي

عدّل في `.env`:
```
# OpenAI
AI_PROVIDER=openai
OPENAI_API_KEY=sk-...

# أو Anthropic
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...

# أو Gemini
AI_PROVIDER=gemini
GEMINI_API_KEY=AIza...
```

---

## الميزات

- ✅ لوحة تحكم للمدير والموظفين (صلاحيات مختلفة)
- ✅ وكيل واتساب يرد تلقائياً من قاعدة المعرفة
- ✅ تصنيف تلقائي للعملاء (جديد / مهتم / جاهز / حالي / متوقف)
- ✅ قائمة موافقات للمدير (عروض كبيرة / خصومات / حملات)
- ✅ حملات تسويقية مع قوالب واتساب المعتمدة
- ✅ إدارة المشاريع (كانبان)
- ✅ جدولة المواعيد مع تأكيد تلقائي
- ✅ توصيات أسبوعية من الذكاء الاصطناعي
- ✅ Dark mode تلقائي
- ✅ تصدير العملاء لإكسيل

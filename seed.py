"""
seed.py — بيانات تجريبية لشركة استيراد وتصدير
Run from project root:  python seed.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from backend.database import create_all_tables, SessionLocal
from backend.models.user        import User
from backend.models.customer    import Customer
from backend.models.chat        import Chat, Message
from backend.models.campaign    import Campaign, Template
from backend.models.project     import Project
from backend.models.appointment import Appointment
from backend.models.approval    import Approval
from backend.models.knowledge   import KnowledgeEntry
from backend.models.settings    import AgentSettings
from backend.routers.auth       import hash_password


def seed():
    create_all_tables()
    db = SessionLocal()

    # ── Clear existing data ──────────────────────────────────────
    for Model in [Message, Chat, Approval, Appointment, Project,
                  Campaign, Template, Customer, KnowledgeEntry,
                  AgentSettings, User]:
        db.query(Model).delete()
    db.commit()
    print("🗑  Cleared existing data")

    # ── Users ────────────────────────────────────────────────────
    users = [
        User(email="manager@demo.local", name="المدير العام",    role="manager",
             hashed_pw=hash_password("Demo@123")),
        User(email="mona@demo.local",    name="منى · المبيعات",  role="staff",
             hashed_pw=hash_password("Staff@123")),
        User(email="karim@demo.local",   name="كريم · الشحن",   role="staff",
             hashed_pw=hash_password("Staff@123")),
    ]
    db.add_all(users)
    db.commit()
    print(f"👥  Seeded {len(users)} users")

    # ── Customers (buyers / importers / exporters) ───────────────
    customers = [
        Customer(name="شركة الخليج للاستيراد",   phone="01005550101", source="واتساب",
                 segment="current",   value=380000, project="رز برازيلي - أكتوبر",
                 consent="in",  consent_date="5 يناير",   consent_src="عقد التوريد",
                 last_contact="منذ ساعتين"),
        Customer(name="مجموعة النيل التجارية",   phone="01115550102", source="إيميل",
                 segment="ready",     value=210000, project="فحم حجري 500 طن",
                 consent="in",  consent_date="10 سبتمبر", consent_src="نموذج الإيميل",
                 last_contact="أمس"),
        Customer(name="محمد الشبراوي - تاجر جملة", phone="01225550103", source="واتساب",
                 segment="interested",value=0,      project="—",
                 consent="in",  consent_date="20 أكتوبر", consent_src="محادثة واتساب",
                 last_contact="منذ 3 ساعات"),
        Customer(name="شركة سيناء للتوزيع",     phone="01005550104", source="إعلان",
                 segment="new",       value=0,      project="—",
                 consent="none", consent_date="—",  consent_src="—",
                 last_contact="منذ 30 دقيقة"),
        Customer(name="كوبري القاهرة - تجارة",  phone="01555550105", source="واتساب",
                 segment="current",   value=145000, project="بطاطا 200 طن - نوفمبر",
                 consent="in",  consent_date="2 مارس",    consent_src="عقد التوريد",
                 last_contact="اليوم"),
        Customer(name="شركة دلتا الزراعية",     phone="01005550106", source="الموقع",
                 segment="ready",     value=95000,  project="بصل 150 طن",
                 consent="in",  consent_date="15 أكتوبر", consent_src="نموذج الموقع",
                 last_contact="أمس"),
        Customer(name="حسن مصطفى - مستثمر خليجي", phone="00971501234567", source="تيليجرام",
                 segment="interested",value=0,      project="—",
                 consent="in",  consent_date="22 أكتوبر", consent_src="تيليجرام",
                 last_contact="منذ ساعة"),
        Customer(name="شركة مكة للغذاء - السعودية", phone="00966501234568", source="إيميل",
                 segment="current",   value=520000, project="رز وبقوليات - Q4",
                 consent="in",  consent_date="1 يونيو",   consent_src="عقد التوريد",
                 last_contact="منذ 3 أيام"),
        Customer(name="أبو حامد - تجارة الجملة", phone="01095550109", source="واتساب",
                 segment="idle",      value=42000,  project="—",
                 consent="out", consent_date="1 أكتوبر",  consent_src='رد "إيقاف"',
                 last_contact="منذ 25 يوم"),
        Customer(name="شركة ليبيا التجارية",    phone="00218912345678", source="إيميل",
                 segment="idle",      value=0,      project="—",
                 consent="none", consent_date="—",  consent_src="—",
                 last_contact="منذ 40 يوم"),
    ]
    db.add_all(customers)
    db.commit()
    print(f"👤  Seeded {len(customers)} customers")

    # ── Chats & Messages ─────────────────────────────────────────
    c_map = {c.name: c for c in db.query(Customer).all()}

    chats_data = [
        {
            "customer": "محمد الشبراوي - تاجر جملة",
            "channel": "whatsapp", "ai": True, "unread": 3,
            "msgs": [
                ("customer", "السلام عليكم، أنا تاجر جملة بالإسكندرية، عايز أعرف سعر طن الرز البسمتي"),
                ("ai",       "أهلاً بحضرتك! سعر الرز البسمتي حالياً 850 دولار للطن CIF ميناء الإسكندرية، والكمية الدنيا 20 طن. تحب التفاصيل الكاملة؟"),
                ("customer", "أيوه، وفيه شهادة جودة؟"),
                ("ai",       "طبعاً، كل شحنة معاها شهادة SGS للجودة وشهادة منشأ. تحب أبعتلك عرض سعر رسمي؟"),
                ("customer", "أيوه ياريت، وممكن أعرف زمن التسليم؟"),
            ]
        },
        {
            "customer": "شركة سيناء للتوزيع",
            "channel": "whatsapp", "ai": True, "unread": 2,
            "msgs": [
                ("customer", "عايز أستورد فحم حجري كمية كبيرة"),
                ("ai",       "أهلاً! إحنا متخصصون في فحم الكوك والفحم الحجري. ممكن تقولي الكمية المطلوبة والاستخدام؟"),
                ("customer", "500 طن للمصانع، محتاج grade A"),
                ("ai",       "ممتاز! فحم Grade A السعر 185 دولار للطن FOB. للكميات فوق 300 طن في خصم خاص. حوّلت طلبك لفريق المبيعات."),
            ]
        },
        {
            "customer": "مجموعة النيل التجارية",
            "channel": "email", "ai": False, "unread": 1,
            "msgs": [
                ("customer", "بعد التحية، نحتاج تعديل مواصفات الفحم المذكورة في العقد - الرطوبة لا تزيد عن 8%"),
                ("human",    "تم استلام ملاحظتكم. سنراجع مع المورد ونرد عليكم خلال 24 ساعة بالتأكيد."),
                ("customer", "شكراً، ننتظر ردكم. العقد مهم ووقته ضيق."),
            ]
        },
        {
            "customer": "حسن مصطفى - مستثمر خليجي",
            "channel": "telegram", "ai": True, "unread": 1,
            "msgs": [
                ("customer", "السلام، أنا مستثمر إماراتي مهتم باستيراد خضروات طازجة من مصر"),
                ("ai",       "أهلاً! مصر من أكبر مصدري الخضروات، خصوصاً البطاطا والبصل والطماطم. أي منتج يهمك أكثر؟"),
                ("customer", "بطاطا وبصل، للسوق الإماراتي"),
            ]
        },
        {
            "customer": "كوبري القاهرة - تجارة",
            "channel": "whatsapp", "ai": False, "unread": 0,
            "msgs": [
                ("customer", "الشحنة اللي بعتوها وصلت بس في ملاحظة على التغليف"),
                ("human",    "شكراً لتبليغنا. ممكن ترسلنا صور من التغليف عشان ننسق مع قسم الجودة؟"),
                ("customer", "تمام، بعتهالكم على الإيميل"),
                ("human",    "تم الاستلام. سنعوضكم في الشحنة القادمة."),
            ]
        },
    ]

    for cd in chats_data:
        cust = c_map.get(cd["customer"])
        if not cust:
            continue
        last_msg = cd["msgs"][-1][1]
        chat = Chat(customer_id=cust.id, channel=cd["channel"],
                    ai_handling=cd["ai"], unread_count=cd["unread"],
                    last_message=last_msg)
        db.add(chat)
        db.flush()
        for sender, body in cd["msgs"]:
            db.add(Message(chat_id=chat.id, sender=sender, body=body))
    db.commit()
    print(f"💬  Seeded {len(chats_data)} chats with messages")

    # ── Templates (قوائم أسعار / رسائل جماعية) ──────────────────
    templates = [
        Template(name="قائمة أسعار أكتوبر",    category="تسويقية", status="approved",
                 body="أهلاً {الاسم}، نرسل لحضرتكم قائمة أسعار {الشهر}:\n• رز برازيلي: 850$/طن\n• فحم حجري Grade A: 185$/طن\n• بطاطا مصرية: 280$/طن\n• بصل مصري: 190$/طن\nالأسعار CIF ميناء الوصول. الكميات الدنيا 20 طن. للتفاصيل تواصلوا معنا."),
        Template(name="تذكير بموعد الشحن",      category="تذكير",   status="approved",
                 body="تذكير لحضرتكم: شحنتكم من {المنتج} ستغادر ميناء الإسكندرية يوم {التاريخ}. رقم البوليصة: {رقم_البوليصة}. تحتاج أي مستندات إضافية؟"),
        Template(name="عرض موسم الشتاء",        category="تسويقية", status="approved",
                 body="عرض خاص لموسم الشتاء {السنة}!\nالبطاطا المصرية بأسعار تنافسية، كميات محدودة.\nتواصل معنا الآن لحجز كميتك قبل النفاد."),
        Template(name="متابعة عميل متوقف",      category="تسويقية", status="review",
                 body="وحشتنا يا {الاسم}! عندنا عروض أسعار جديدة لموسم {الموسم}، ترغبوا في قائمة الأسعار الحالية؟"),
        Template(name="شهادة جودة ومستندات",   category="خدمية",   status="approved",
                 body="شحنة {المنتج} لحضرتكم جاهزة. المستندات المرفقة:\n✓ شهادة SGS للجودة\n✓ شهادة المنشأ\n✓ قائمة التعبئة\n✓ الفاتورة التجارية\nهل تحتاجون أي مستندات إضافية؟"),
    ]
    db.add_all(templates)
    db.commit()
    print(f"📄  Seeded {len(templates)} templates")

    # ── Campaigns ────────────────────────────────────────────────
    tpl_map = {t.name: t for t in db.query(Template).all()}
    campaigns = [
        Campaign(name="قائمة أسعار أكتوبر",             channel="واتساب",
                 audience="عملاء حاليون + مهتمون", recipient_count=78, status="running",
                 template_id=tpl_map["قائمة أسعار أكتوبر"].id,
                 sent=78, read=62, replied=21, scheduled_at="بدأت الأحد"),
        Campaign(name="عرض موسم الشتاء 2024",            channel="واتساب + إيميل",
                 audience="كل العملاء",             recipient_count=120, status="scheduled",
                 template_id=tpl_map["عرض موسم الشتاء"].id,
                 sent=0, read=0, replied=0, scheduled_at="الأحد 1 نوفمبر"),
        Campaign(name="متابعة العملاء المتوقفين",        channel="إيميل",
                 audience="متوقف",                  recipient_count=15, status="done",
                 template_id=tpl_map["متابعة عميل متوقف"].id,
                 sent=15, read=9, replied=3, scheduled_at="انتهت 10 أكتوبر"),
        Campaign(name="إشعار شحنات نوفمبر",             channel="واتساب",
                 audience="عملاء حاليون",           recipient_count=32, status="draft",
                 template_id=tpl_map["تذكير بموعد الشحن"].id,
                 sent=0, read=0, replied=0, scheduled_at="لم تُجدول بعد"),
    ]
    db.add_all(campaigns)
    db.commit()
    print(f"📣  Seeded {len(campaigns)} campaigns")

    # ── Projects → Orders/Deals ───────────────────────────────────
    # STAGES = ['استفسار', 'عرض سعر', 'دفع وعقد', 'شحن', 'استلام وإغلاق']
    projects = [
        Project(name="رز برازيلي 100 طن",          customer="شركة الخليج للاستيراد",
                stage=3, progress=70,  due_note="وصول ميناء الإسكندرية 28 أكتوبر",
                reminder="تذكير العميل بالمستندات الجمركية", is_late=False),
        Project(name="فحم حجري 500 طن",            customer="مجموعة النيل التجارية",
                stage=2, progress=45,  due_note="العقد موقّع · انتظار دفعة الشحن",
                reminder="متابعة الدفعة الثانية على واتساب", is_late=True),
        Project(name="بطاطا مصرية 200 طن",         customer="كوبري القاهرة - تجارة",
                stage=3, progress=80,  due_note="شحن 25 أكتوبر من ميناء دمياط",
                reminder="إرسال بوليصة الشحن على الإيميل",  is_late=False),
        Project(name="بصل 150 طن للسعودية",         customer="شركة مكة للغذاء - السعودية",
                stage=2, progress=30,  due_note="العقد قيد التفاوض",
                reminder="اجتماع يوم الأحد لتحديد المواصفات", is_late=False),
        Project(name="فحم كوك 300 طن - استفسار",   customer="شركة سيناء للتوزيع",
                stage=1, progress=10,  due_note="عرض سعر مُرسل، انتظار رد",
                reminder="متابعة تلقائية بعد 3 أيام",        is_late=False),
        Project(name="رز وبقوليات Q3",             customer="شركة مكة للغذاء - السعودية",
                stage=4, progress=100, due_note="استُلم 10 أكتوبر · مغلق",
                reminder="—",                                 is_late=False),
        Project(name="بطاطا وبصل للإمارات",        customer="حسن مصطفى - مستثمر خليجي",
                stage=0, progress=5,   due_note="بانتظار تحديد المواصفات",
                reminder="الوكيل يجمع المتطلبات",             is_late=False),
    ]
    db.add_all(projects)
    db.commit()
    print(f"📦  Seeded {len(projects)} orders/deals")

    # ── Appointments ─────────────────────────────────────────────
    appointments = [
        Appointment(day_label="اليوم · الخميس 23 أكتوبر", time_label="11:00 ص",
                    title="مكالمة تفاوض عقد الفحم",         customer="مجموعة النيل التجارية",
                    channel="مكالمة زووم",   confirmed=True),
        Appointment(day_label="اليوم · الخميس 23 أكتوبر", time_label="3:00 م",
                    title="مراجعة مواصفات شحنة الرز",       customer="شركة الخليج للاستيراد",
                    channel="اجتماع مكتب",  confirmed=False),
        Appointment(day_label="الأحد 26 أكتوبر",           time_label="10:00 ص",
                    title="تحديد مواصفات الطلب",            customer="حسن مصطفى - مستثمر خليجي",
                    channel="مكالمة واتساب", confirmed=True),
        Appointment(day_label="الأحد 26 أكتوبر",           time_label="1:00 م",
                    title="توقيع عقد بصل السعودية",          customer="شركة مكة للغذاء - السعودية",
                    channel="إيميل + موثق", confirmed=False),
        Appointment(day_label="الاثنين 27 أكتوبر",         time_label="9:00 ص",
                    title="معاينة الشحنة في الميناء",       customer="كوبري القاهرة - تجارة",
                    channel="ميناء دمياط",  confirmed=True),
        Appointment(day_label="الثلاثاء 28 أكتوبر",        time_label="12:00 م",
                    title="استلام مستندات الجمارك",         customer="شركة الخليج للاستيراد",
                    channel="مكالمة",        confirmed=True),
    ]
    db.add_all(appointments)
    db.commit()
    print(f"📅  Seeded {len(appointments)} appointments")

    # ── Escalation Alerts ──────────────────────────────────
    approvals = [
        Approval(type="عرض سعر",    customer="مجموعة النيل التجارية",
                 requested_by="الوكيل", status="pending",
                 reason="قيمة الصفقة 210,000 ج.م، تتجاوز حد الموافقة التلقائية",
                 body_text="أهلاً أستاذ / مجموعة النيل، عرض توريد 500 طن فحم حجري Grade A:\n• السعر: 185 دولار/طن FOB ميناء الإسكندرية\n• الإجمالي: 92,500 دولار\n• الدفع: 30% مقدم، 70% عند الشحن بـ LC\n• مدة التسليم: 21 يوم من تاريخ الدفعة\n• شهادة SGS مرفقة"),
        Approval(type="طلب خصم",   customer="شركة دلتا الزراعية",
                 requested_by="الوكيل", status="pending",
                 reason="العميل طلب خصم 15% على البصل، والحد المسموح 8%",
                 body_text="نقدر نوفر خصم 8% على طلب بصل 150 طن عند السداد المقدم الكامل، مع أولوية الشحن في الأسبوع القادم."),
        Approval(type="رسالة جماعية", customer="قائمة عملاء أكتوبر (78 عميل)",
                 requested_by="منى · المبيعات", status="pending",
                 reason="كل حملة جماعية تمر على المدير قبل الإرسال",
                 body_text="أهلاً {الاسم}، نرسل لحضرتكم قائمة أسعار أكتوبر:\n• رز برازيلي: 850$/طن\n• فحم حجري Grade A: 185$/طن\n• بطاطا مصرية: 280$/طن"),
        Approval(type="تعديل عقد", customer="كوبري القاهرة - تجارة",
                 requested_by="كريم · الشحن", status="pending",
                 reason="العميل يطلب تغيير ميناء التسليم من الإسكندرية إلى دمياط",
                 body_text="تمام يا أستاذ، نقدر نحول الشحنة لميناء دمياط مع فارق تكلفة 1,200 دولار يُضاف للفاتورة. نحتاج موافقتك المكتوبة."),
        Approval(type="عرض سعر",   customer="حسن مصطفى - مستثمر خليجي",
                 requested_by="الوكيل", status="approved", decided_at="أمس",
                 reason="عرض أولي للسوق الإماراتي",
                 body_text="عرض توريد بطاطا وبصل مصري للسوق الإماراتي:\n• بطاطا: 300$/طن CIF دبي\n• بصل: 220$/طن CIF دبي\n• كمية دنيا: 50 طن لكل منتج"),
    ]
    db.add_all(approvals)
    db.commit()
    print(f"✅  Seeded {len(approvals)} approvals")

    # ── Knowledge Base ───────────────────────────────────────────
    kb = [
        # الأسعار
        KnowledgeEntry(category="الأسعار", question="كم سعر طن الرز البسمتي؟",
                       answer="الرز البسمتي الهندي: 820-880 دولار/طن CIF. الرز البرازيلي: 800-850 دولار/طن. الأسعار تتغير شهرياً حسب السوق الدولي."),
        KnowledgeEntry(category="الأسعار", question="كم سعر طن الفحم الحجري؟",
                       answer="فحم حجري Grade A: 180-190 دولار/طن FOB. فحم الكوك الصناعي: 210-230 دولار/طن. للكميات فوق 500 طن يوجد خصم يصل 5%."),
        KnowledgeEntry(category="الأسعار", question="كم سعر طن البطاطا المصرية؟",
                       answer="البطاطا المصرية موسم الشتاء: 250-300 دولار/طن CIF. موسم الصيف: 280-320 دولار/طن. الكمية الدنيا 20 طن."),
        KnowledgeEntry(category="الأسعار", question="كم سعر طن البصل المصري؟",
                       answer="البصل الأصفر المصري: 180-220 دولار/طن CIF. الكمية الدنيا للتصدير 20 طن. السعر يعتمد على الجودة والموسم."),
        # التسليم
        KnowledgeEntry(category="التسليم", question="كم مدة الشحن من مصر؟",
                       answer="الخليج العربي: 7-10 أيام. أوروبا: 14-18 يوم. آسيا: 20-25 يوم. من تاريخ تحميل البضاعة في الميناء."),
        KnowledgeEntry(category="التسليم", question="ما الموانئ التي تعمل منها؟",
                       answer="ميناء الإسكندرية (الرئيسي)، ميناء دمياط (الحبوب والخضروات)، ميناء السخنة (للفحم والمعادن)."),
        KnowledgeEntry(category="التسليم", question="ما الكمية الدنيا للطلب؟",
                       answer="الخضروات والحبوب: 20 طن كحد أدنى. الفحم: 100 طن كحد أدنى. للكميات الأقل يوجد رسوم شحن إضافية."),
        # الدفع
        KnowledgeEntry(category="الدفع", question="ما طرق الدفع المتاحة؟",
                       answer="T/T (تحويل بنكي): 30% مقدم + 70% عند الشحن. LC (خطاب اعتماد): للصفقات فوق 100,000 دولار. للعملاء المعتمدين: 60 يوم ائتمان."),
        KnowledgeEntry(category="الدفع", question="هل يوجد ائتمان أو آجل؟",
                       answer="نعم، للعملاء المعتمدين الذين تعاملوا معنا أكثر من 6 أشهر وسجلهم حسن، يمكن منح ائتمان حتى 60 يوماً بعد الاستلام."),
        # المستندات
        KnowledgeEntry(category="المستندات", question="ما المستندات المرفقة مع كل شحنة؟",
                       answer="1. فاتورة تجارية 2. قائمة التعبئة (Packing List) 3. بوليصة الشحن (Bill of Lading) 4. شهادة المنشأ 5. شهادة جودة SGS 6. شهادة صحية (للخضروات والأغذية)."),
        KnowledgeEntry(category="المستندات", question="هل تصدرون شهادة جودة؟",
                       answer="نعم، كل شحنة معها شهادة جودة SGS أو Bureau Veritas. للأغذية نصدر شهادة صحية معتمدة من وزارة الزراعة المصرية."),
        # عام
        KnowledgeEntry(category="عام", question="ما ساعات العمل؟",
                       answer="من الأحد للخميس، 9 ص حتى 5 م بتوقيت القاهرة (UTC+2). للشحنات العاجلة يوجد رقم طوارئ خارج أوقات العمل."),
        KnowledgeEntry(category="عام", question="ما المنتجات التي تتخصصون فيها؟",
                       answer="نتخصص في: الفحم الحجري وفحم الكوك، الحبوب (رز، ذرة، قمح)، الخضروات المصرية (بطاطا، بصل، طماطم، ثوم). استيراد وتصدير دولي."),
    ]
    db.add_all(kb)
    db.commit()
    print(f"📚  Seeded {len(kb)} knowledge base entries")

    # ── Agent Settings ────────────────────────────────────────────
    settings_row = AgentSettings(
        id=1,
        name="وكيل التجارة الدولية",
        tone="ودود ومحترف",
        language="عامية مصرية",
        greeting="أهلاً بحضرتكم! أنا وكيل شركة للاستيراد والتصدير، أقدر أجاوب على استفساراتكم عن الأسعار والشحن والمنتجات. كيف أقدر أساعدكم؟",
        work_days="0111110",
        work_from="09:00",
        work_to="17:00",
        off_msg="شكراً لتواصلكم! مواعيد العمل من الأحد للخميس 9 ص-5 م. سنرد عليكم أول ما نبدأ العمل، أو تواصلوا على إيميلنا للأمور العاجلة.",
        hand_angry=True, hand_discount=True, hand_amount=True,
        hand_call=True, hand_unknown=True,
        approval_limit=50000.0,
        max_discount=8.0,
        is_active=True,
    )
    db.add(settings_row)
    db.commit()
    print("⚙️   Seeded agent settings")

    db.close()
    print("\n✅ Database seeded successfully — شركة استيراد وتصدير!")
    print("   Login: manager@demo.local / Demo@123")
    print("   Login: mona@demo.local    / Staff@123")


if __name__ == "__main__":
    seed()

"""
init.py — تهيئة قاعدة البيانات من الصفر (بدون داتا تجريبية)
Run from project root:  python init.py
"""
import sys, os, getpass
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


def init():
    create_all_tables()
    db = SessionLocal()

    # ── مسح كل الداتا القديمة ────────────────────────────────────
    for Model in [Message, Chat, Approval, Appointment, Project,
                  Campaign, Template, Customer, KnowledgeEntry,
                  AgentSettings, User]:
        db.query(Model).delete()
    db.commit()
    print("🗑  تم مسح كل البيانات القديمة")

    # ── إنشاء حساب المدير ────────────────────────────────────────
    print("\n👤 إنشاء حساب المدير:")
    name     = input("   الاسم (مثال: أحمد محمد): ").strip() or "المدير"
    email    = input("   البريد الإلكتروني: ").strip()
    password = getpass.getpass("   كلمة المرور: ").strip()

    if not email or not password:
        print("❌ البريد وكلمة المرور مطلوبين")
        db.close()
        return

    manager = User(
        email=email,
        name=name,
        role="manager",
        hashed_pw=hash_password(password),
    )
    db.add(manager)
    db.commit()
    print(f"✅ تم إنشاء حساب المدير: {email}")

    # ── إعدادات الوكيل الافتراضية ────────────────────────────────
    settings = AgentSettings(
        id=1,
        name="الوكيل الذكي",
        tone="ودود ومحترف",
        language="عامية مصرية",
        greeting="أهلاً! كيف أقدر أساعدك؟",
        work_days="0111110",
        work_from="09:00",
        work_to="17:00",
        off_msg="شكراً لتواصلك! سنرد عليك في أقرب وقت خلال ساعات العمل.",
        hand_angry=True, hand_discount=True, hand_amount=True,
        hand_call=True, hand_unknown=True,
        approval_limit=10000.0,
        max_discount=10.0,
        is_active=True,
    )
    db.add(settings)
    db.commit()
    print("⚙️  تم إنشاء الإعدادات الافتراضية للوكيل")

    db.close()
    print(f"\n✅ قاعدة البيانات جاهزة!")
    print(f"   افتح: http://localhost:5500")
    print(f"   الإيميل: {email}")
    print(f"   ابدأ بإضافة عملائك من قسم 'العملاء'")


if __name__ == "__main__":
    init()

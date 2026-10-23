"""
ai/automation.py — Scheduled automation tasks (APScheduler jobs)

Handles:
- Follow-up messages for idle customers
- Campaign dispatch
- Appointment reminders
- Weekly insights generation

Registered in main.py via APScheduler.
"""
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from backend.database import SessionLocal
from backend.models.customer import Customer
from backend.models.appointment import Appointment
from backend.services import whatsapp as wa_service
from .llm import chat_complete
from .prompts import PERSONALISE_PROMPT


def _db() -> Session:
    return SessionLocal()


# ── Follow-up automation ──────────────────────────────────────────────────

async def send_followups() -> None:
    """
    Send personalised follow-up messages to customers who haven't
    responded in 3+ days (interested/ready segments only).
    """
    db = _db()
    try:
        cutoff = datetime.utcnow() - timedelta(days=3)
        targets = db.query(Customer).filter(
            Customer.segment.in_(["interested", "ready"]),
            Customer.consent == "in",
        ).all()

        for c in targets:
            # TODO: filter by actual last_contact timestamp in production
            template = "وحشتنا يا {الاسم}! هل لا زلت مهتماً؟ أنا هنا للمساعدة."
            msg = template.replace("{الاسم}", c.name.split()[0])
            try:
                await wa_service.send_text(c.id, msg, db)
                print(f"[automation] Follow-up sent to {c.name}")
            except Exception as e:
                print(f"[automation] Failed follow-up for {c.name}: {e}")
    finally:
        db.close()


# ── Appointment reminders ─────────────────────────────────────────────────

async def send_appointment_reminders() -> None:
    """
    Send reminder to customers with upcoming appointments (within 24h).
    """
    db = _db()
    try:
        upcoming = db.query(Appointment).filter(Appointment.confirmed == True).all()
        for a in upcoming:
            # In production: parse real datetime and check 24h window
            reminder = f"تذكير: موعدك غداً عند الساعة {a.time_label} — {a.title}. نتطلع لرؤيتك!"
            try:
                await wa_service.send_text(a.customer_id, reminder, db)
            except Exception as e:
                print(f"[automation] Reminder failed for appt {a.id}: {e}")
    finally:
        db.close()


# ── Campaign dispatch ─────────────────────────────────────────────────────

async def dispatch_scheduled_campaigns() -> None:
    """
    Find campaigns due to send and dispatch them.
    In production: check scheduled_at timestamp.
    """
    db = _db()
    try:
        from backend.models.campaign import Campaign, Template
        campaigns = db.query(Campaign).filter(Campaign.status == "scheduled").all()
        for camp in campaigns:
            tpl = db.get(Template, camp.template_id)
            if not tpl or tpl.status != "approved":
                continue

            targets = db.query(Customer).filter(
                Customer.consent == "in"
            ).all()

            sent = 0
            for c in targets:
                # Personalise message
                msg = tpl.body.replace("{الاسم}", c.name.split()[0])
                try:
                    await wa_service.send_text(c.id, msg, db)
                    sent += 1
                except Exception:
                    pass

            camp.status = "running"
            camp.sent   = sent
            db.commit()
            print(f"[automation] Campaign '{camp.name}' dispatched to {sent} customers")
    finally:
        db.close()


# ── Insights generation ───────────────────────────────────────────────────

async def generate_weekly_insights() -> list[dict]:
    """
    Generate AI-powered recommendations based on current data.
    Returns a list of insight dicts (stored or returned to dashboard).
    """
    db = _db()
    try:
        idle_count = db.query(Customer).filter(Customer.segment == "idle").count()
        ready_count = db.query(Customer).filter(Customer.segment == "ready").count()

        prompt = f"""أنت محلل بيانات لشركة. بناءً على البيانات التالية، أعطني 3 توصيات عملية:
- عملاء متوقفون: {idle_count}
- جاهزون للشراء بدون عرض سعر: {ready_count}

اكتب كل توصية في سطر واحد مختصر."""

        result = await chat_complete([{"role": "user", "content": prompt}])
        lines  = [l.strip() for l in result.strip().split("\n") if l.strip()]

        return [{"k": "mid", "t": line, "d": "", "a": "تنفيذ"} for line in lines[:3]]
    finally:
        db.close()


# ── Job registry (called from main.py) ────────────────────────────────────

def register_jobs(scheduler) -> None:
    """Register all recurring jobs with APScheduler."""
    # Follow-ups every day at 9 AM
    scheduler.add_job(
        lambda: asyncio.create_task(send_followups()),
        "cron", hour=9, minute=0, id="followups",
    )
    # Appointment reminders every day at 8 AM
    scheduler.add_job(
        lambda: asyncio.create_task(send_appointment_reminders()),
        "cron", hour=8, minute=0, id="reminders",
    )
    # Campaign dispatch every 30 minutes
    scheduler.add_job(
        lambda: asyncio.create_task(dispatch_scheduled_campaigns()),
        "interval", minutes=30, id="campaigns",
    )
    print("[automation] All scheduled jobs registered")

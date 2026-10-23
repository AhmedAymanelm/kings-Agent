"""
models/__init__.py — Import all models so SQLAlchemy picks them up at startup
"""
from .user import User
from .customer import Customer
from .chat import Chat, Message
from .campaign import Campaign, Template
from .project import Project
from .appointment import Appointment
from .approval import Approval
from .knowledge import KnowledgeEntry
from .settings import AgentSettings

__all__ = [
    "User", "Customer", "Chat", "Message",
    "Campaign", "Template", "Project",
    "Appointment", "Approval", "KnowledgeEntry", "AgentSettings",
]

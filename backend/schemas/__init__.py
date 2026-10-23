"""schemas/__init__.py"""
from .auth import TokenOut, LoginIn, UserOut
from .customer import CustomerOut, CustomerPatch
from .chat import ChatOut, MessageOut, SendMessageIn
from .campaign import CampaignOut, TemplateOut, TemplateIn
from .project import ProjectOut
from .appointment import AppointmentOut
from .approval import ApprovalOut, ApprovalDecision
from .knowledge import KBEntryOut, KBEntryIn
from .settings import AgentSettingsOut, AgentSettingsPatch

__all__ = [
    "TokenOut","LoginIn","UserOut",
    "CustomerOut","CustomerPatch",
    "ChatOut","MessageOut","SendMessageIn",
    "CampaignOut","TemplateOut","TemplateIn",
    "ProjectOut","AppointmentOut",
    "ApprovalOut","ApprovalDecision",
    "KBEntryOut","KBEntryIn",
    "AgentSettingsOut","AgentSettingsPatch",
]

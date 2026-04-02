from __future__ import annotations

from datetime import datetime
from enum import Enum
from pydantic import BaseModel


class EmailStatus(str, Enum):
    new = "new"
    classified = "classified"
    replied = "replied"
    skipped = "skipped"


class Email(BaseModel):
    id: str
    uid: int
    subject: str
    sender: str
    date: datetime
    body: str
    body_html: str = ""
    status: EmailStatus = EmailStatus.new
    category: str | None = None
    confidence: float | None = None
    suggested_reply: str | None = None
    reply_sent: bool = False


class ClassificationResult(BaseModel):
    category: str
    confidence: float
    summary: str
    suggested_reply: str


class EmailSettings(BaseModel):
    imap_host: str
    imap_port: int
    imap_user: str
    imap_password: str
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_password: str


class AISettings(BaseModel):
    openai_api_key: str
    openai_base_url: str
    openai_model: str
    categories: list[str]


class ReplyRequest(BaseModel):
    email_id: str
    reply_text: str

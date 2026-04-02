from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel


class EmailOut(BaseModel):
    id: str
    message_id: str | None = None
    uid: int
    mailbox: str = "default"
    subject: str
    sender: str
    date: datetime
    body: str
    body_html: str = ""
    status: str = "new"
    category: str | None = None
    category_human: str | None = None
    confidence: float | None = None
    summary: str | None = None
    suggested_reply: str | None = None
    reply_sent: bool = False
    reply_text: str | None = None
    replied_at: datetime | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class EmailListResponse(BaseModel):
    emails: list[EmailOut]
    total: int
    page: int
    page_size: int


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


class CorrectCategoryRequest(BaseModel):
    category: str

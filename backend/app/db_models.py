from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Integer, String, Text, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class EmailDB(Base):
    __tablename__ = "emails"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    message_id: Mapped[str | None] = mapped_column(String(255), unique=True, index=True)
    uid: Mapped[int] = mapped_column(Integer)
    mailbox: Mapped[str] = mapped_column(String(255), default="default", index=True)
    subject: Mapped[str] = mapped_column(Text, default="")
    sender: Mapped[str] = mapped_column(String(255), default="")
    date: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    body: Mapped[str] = mapped_column(Text, default="")
    body_html: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(50), default="new", index=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    category_human: Mapped[str | None] = mapped_column(String(100), nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    suggested_reply: Mapped[str | None] = mapped_column(Text, nullable=True)
    reply_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    reply_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    replied_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    approved_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class MailboxDB(Base):
    __tablename__ = "mailboxes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    imap_host: Mapped[str] = mapped_column(String(255))
    imap_port: Mapped[int] = mapped_column(Integer, default=993)
    imap_user: Mapped[str] = mapped_column(String(255))
    imap_password: Mapped[str] = mapped_column(String(255))
    smtp_host: Mapped[str] = mapped_column(String(255))
    smtp_port: Mapped[int] = mapped_column(Integer, default=587)
    smtp_user: Mapped[str] = mapped_column(String(255))
    smtp_password: Mapped[str] = mapped_column(String(255))
    polling_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class ReplyTemplateDB(Base):
    __tablename__ = "reply_templates"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    category: Mapped[str] = mapped_column(String(100), index=True)
    title: Mapped[str] = mapped_column(String(255))
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .classifier import classify_email, generate_custom_reply
from .config import settings
from .email_client import fetch_emails, send_reply
from .models import (
    AISettings,
    Email,
    EmailSettings,
    EmailStatus,
    ReplyRequest,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory store for POC
email_store: dict[str, Email] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Email AI Classifier POC started")
    yield


app = FastAPI(title="Email AI Classifier", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health ──────────────────────────────────────────────
@app.get("/api/health")
def health():
    return {"status": "ok"}


# ── Emails ──────────────────────────────────────────────
@app.post("/api/emails/fetch")
def api_fetch_emails(limit: int = 50):
    """Fetch emails from the configured mailbox."""
    try:
        emails = fetch_emails(limit=limit)
        for em in emails:
            if em.id not in email_store:
                email_store[em.id] = em
        return {"count": len(emails), "emails": emails}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Fetch failed")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/emails")
def api_list_emails(status: str | None = None):
    """List all cached emails, optionally filtered by status."""
    emails = list(email_store.values())
    if status:
        emails = [e for e in emails if e.status == status]
    emails.sort(key=lambda e: e.date, reverse=True)
    return emails


@app.get("/api/emails/{email_id}")
def api_get_email(email_id: str):
    if email_id not in email_store:
        raise HTTPException(status_code=404, detail="Email not found")
    return email_store[email_id]


# ── Classification ──────────────────────────────────────
@app.post("/api/emails/{email_id}/classify")
async def api_classify_email(email_id: str):
    """Classify a single email."""
    if email_id not in email_store:
        raise HTTPException(status_code=404, detail="Email not found")

    em = email_store[email_id]
    result = await classify_email(em.sender, em.subject, em.body)

    em.category = result.category
    em.confidence = result.confidence
    em.suggested_reply = result.suggested_reply
    em.status = EmailStatus.classified

    return {"email_id": email_id, "classification": result}


@app.post("/api/emails/classify-all")
async def api_classify_all():
    """Classify all unclassified emails."""
    results = []
    for em in email_store.values():
        if em.status == EmailStatus.new:
            try:
                result = await classify_email(em.sender, em.subject, em.body)
                em.category = result.category
                em.confidence = result.confidence
                em.suggested_reply = result.suggested_reply
                em.status = EmailStatus.classified
                results.append({"email_id": em.id, "category": result.category})
            except Exception:
                logger.exception("Classification failed for %s", em.id)
    return {"classified": len(results), "results": results}


# ── Reply ───────────────────────────────────────────────
@app.post("/api/emails/{email_id}/reply")
async def api_send_reply(email_id: str, req: ReplyRequest):
    """Send a reply to an email."""
    if email_id not in email_store:
        raise HTTPException(status_code=404, detail="Email not found")

    em = email_store[email_id]
    try:
        await send_reply(to=em.sender, subject=em.subject, body=req.reply_text)
        em.reply_sent = True
        em.status = EmailStatus.replied
        return {"success": True}
    except Exception as e:
        logger.exception("Reply failed")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/emails/{email_id}/generate-reply")
async def api_generate_reply(email_id: str, instructions: str = ""):
    """Generate a custom reply using AI."""
    if email_id not in email_store:
        raise HTTPException(status_code=404, detail="Email not found")

    em = email_store[email_id]
    reply = await generate_custom_reply(em.sender, em.subject, em.body, instructions)
    return {"reply": reply}


# ── Settings ────────────────────────────────────────────
@app.get("/api/settings/email")
def api_get_email_settings():
    return EmailSettings(
        imap_host=settings.imap_host,
        imap_port=settings.imap_port,
        imap_user=settings.imap_user,
        imap_password="***" if settings.imap_password else "",
        smtp_host=settings.smtp_host,
        smtp_port=settings.smtp_port,
        smtp_user=settings.smtp_user,
        smtp_password="***" if settings.smtp_password else "",
    )


@app.put("/api/settings/email")
def api_update_email_settings(s: EmailSettings):
    settings.imap_host = s.imap_host
    settings.imap_port = s.imap_port
    settings.imap_user = s.imap_user
    if s.imap_password != "***":
        settings.imap_password = s.imap_password
    settings.smtp_host = s.smtp_host
    settings.smtp_port = s.smtp_port
    settings.smtp_user = s.smtp_user
    if s.smtp_password != "***":
        settings.smtp_password = s.smtp_password
    return {"status": "updated"}


@app.get("/api/settings/ai")
def api_get_ai_settings():
    return AISettings(
        openai_api_key="***" if settings.openai_api_key else "",
        openai_base_url=settings.openai_base_url,
        openai_model=settings.openai_model,
        categories=settings.categories,
    )


@app.put("/api/settings/ai")
def api_update_ai_settings(s: AISettings):
    if s.openai_api_key != "***":
        settings.openai_api_key = s.openai_api_key
    settings.openai_base_url = s.openai_base_url
    settings.openai_model = s.openai_model
    settings.categories = s.categories
    return {"status": "updated"}


# ── Stats ───────────────────────────────────────────────
@app.get("/api/stats")
def api_stats():
    emails = list(email_store.values())
    total = len(emails)
    by_status = {}
    by_category = {}
    for em in emails:
        by_status[em.status] = by_status.get(em.status, 0) + 1
        if em.category:
            by_category[em.category] = by_category.get(em.category, 0) + 1
    return {
        "total": total,
        "by_status": by_status,
        "by_category": by_category,
    }

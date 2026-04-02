from __future__ import annotations

import logging
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import Integer, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .auth import (
    LoginRequest,
    Token,
    authenticate_user,
    create_tokens,
    get_current_user,
)
from .classifier import classify_email, generate_custom_reply
from .config import settings
from .database import engine, get_db
from .db_models import Base, EmailDB, MailboxDB, ReplyTemplateDB
from .email_client import fetch_emails, send_reply
from .models import (
    AISettings,
    ApproveRequest,
    CorrectCategoryRequest,
    EmailListResponse,
    EmailOut,
    EmailSettings,
    MailboxIn,
    MailboxOut,
    PollingSettings,
    ReplyRequest,
    TemplateIn,
    TemplateOut,
)
from .scheduler import is_scheduler_running, start_scheduler, stop_scheduler
from .seed import generate_mock_emails

import csv
import io

from fastapi.responses import StreamingResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def _get_few_shot_examples(db: AsyncSession, limit: int = 5) -> list[dict]:
    """Get recent human-corrected classifications for few-shot prompting."""
    result = await db.execute(
        select(EmailDB)
        .where(EmailDB.category_human.isnot(None))
        .order_by(EmailDB.created_at.desc())
        .limit(limit)
    )
    return [
        {"subject": e.subject, "sender": e.sender, "category": e.category_human}
        for e in result.scalars().all()
    ]


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Email AI Classifier POC v0.3 started — database ready")
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(title="Email AI Classifier", version="0.3.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Auth ────────────────────────────────────────────────
@app.post("/api/auth/login", response_model=Token)
async def login(req: LoginRequest):
    user = authenticate_user(req.username, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Credenziali non valide")
    return create_tokens(user)


@app.post("/api/auth/refresh", response_model=Token)
async def refresh(user: str = Depends(get_current_user)):
    return create_tokens(user)


@app.get("/api/auth/me")
async def me(user: str = Depends(get_current_user)):
    return {"username": user}


# ── Health ──────────────────────────────────────────────
@app.get("/api/health")
async def health():
    return {"status": "ok", "scheduler": is_scheduler_running()}


# ── Emails ──────────────────────────────────────────────
@app.post("/api/emails/fetch")
async def api_fetch_emails(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    try:
        raw_emails = fetch_emails(limit=limit)
        added = 0
        for em in raw_emails:
            if em.get("message_id"):
                existing = await db.execute(
                    select(EmailDB).where(EmailDB.message_id == em["message_id"])
                )
                if existing.scalar_one_or_none():
                    continue
            db.add(EmailDB(**em))
            added += 1
        await db.commit()
        return {"fetched": len(raw_emails), "added": added}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Fetch failed")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/emails", response_model=EmailListResponse)
async def api_list_emails(
    status: str | None = None,
    category: str | None = None,
    mailbox: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    query = select(EmailDB)
    count_query = select(func.count(EmailDB.id))

    if status:
        query = query.where(EmailDB.status == status)
        count_query = count_query.where(EmailDB.status == status)
    if category:
        query = query.where(EmailDB.category == category)
        count_query = count_query.where(EmailDB.category == category)
    if mailbox:
        query = query.where(EmailDB.mailbox == mailbox)
        count_query = count_query.where(EmailDB.mailbox == mailbox)

    total = (await db.execute(count_query)).scalar() or 0
    query = query.order_by(EmailDB.date.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    emails = result.scalars().all()

    return EmailListResponse(
        emails=[EmailOut.model_validate(e) for e in emails],
        total=total,
        page=page,
        page_size=page_size,
    )


# ── Export CSV ──────────────────────────────────────────
@app.get("/api/emails/export/csv")
async def api_export_csv(
    status: str | None = None,
    category: str | None = None,
    mailbox: str | None = None,
    db: AsyncSession = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    query = select(EmailDB)
    if status:
        query = query.where(EmailDB.status == status)
    if category:
        query = query.where(EmailDB.category == category)
    if mailbox:
        query = query.where(EmailDB.mailbox == mailbox)
    query = query.order_by(EmailDB.date.desc())

    result = await db.execute(query)
    emails = result.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "id", "date", "sender", "subject", "status", "category",
        "category_human", "confidence", "summary", "mailbox",
    ])
    for em in emails:
        writer.writerow([
            em.id,
            em.date.isoformat() if em.date else "",
            em.sender,
            em.subject,
            em.status,
            em.category or "",
            em.category_human or "",
            f"{em.confidence:.2f}" if em.confidence is not None else "",
            em.summary or "",
            em.mailbox,
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=emails_export.csv"},
    )


@app.get("/api/emails/{email_id}", response_model=EmailOut)
async def api_get_email(
    email_id: str,
    db: AsyncSession = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    em = await db.get(EmailDB, email_id)
    if not em:
        raise HTTPException(status_code=404, detail="Email not found")
    return EmailOut.model_validate(em)


# ── Classification ──────────────────────────────────────
@app.post("/api/emails/{email_id}/classify")
async def api_classify_email(
    email_id: str,
    db: AsyncSession = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    em = await db.get(EmailDB, email_id)
    if not em:
        raise HTTPException(status_code=404, detail="Email not found")

    # Fetch few-shot examples from human corrections
    few_shot = await _get_few_shot_examples(db)
    result = await classify_email(em.sender, em.subject, em.body, few_shot)
    em.category = result.category
    em.confidence = result.confidence
    em.summary = result.summary
    em.suggested_reply = result.suggested_reply
    em.status = "classified"
    await db.commit()
    return {"email_id": email_id, "classification": result}


@app.post("/api/emails/classify-all")
async def api_classify_all(
    db: AsyncSession = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    few_shot = await _get_few_shot_examples(db)
    result = await db.execute(select(EmailDB).where(EmailDB.status == "new"))
    emails = result.scalars().all()
    classified = []

    for em in emails:
        try:
            res = await classify_email(em.sender, em.subject, em.body, few_shot)
            em.category = res.category
            em.confidence = res.confidence
            em.summary = res.summary
            em.suggested_reply = res.suggested_reply
            em.status = "classified"
            classified.append({"email_id": em.id, "category": res.category})
        except Exception:
            logger.exception("Classification failed for %s", em.id)

    await db.commit()
    return {"classified": len(classified), "results": classified}


@app.post("/api/emails/{email_id}/correct")
async def api_correct_category(
    email_id: str,
    req: CorrectCategoryRequest,
    db: AsyncSession = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    em = await db.get(EmailDB, email_id)
    if not em:
        raise HTTPException(status_code=404, detail="Email not found")
    em.category_human = req.category
    await db.commit()
    return {"email_id": email_id, "category_human": req.category}


# ── Approval Workflow ───────────────────────────────────
@app.post("/api/emails/{email_id}/submit-for-approval")
async def api_submit_for_approval(
    email_id: str,
    req: ReplyRequest,
    db: AsyncSession = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    """Submit a reply for approval (status → pending_approval)."""
    em = await db.get(EmailDB, email_id)
    if not em:
        raise HTTPException(status_code=404, detail="Email not found")
    em.suggested_reply = req.reply_text
    em.status = "pending_approval"
    await db.commit()
    return {"email_id": email_id, "status": "pending_approval"}


@app.post("/api/emails/{email_id}/approve")
async def api_approve_email(
    email_id: str,
    req: ApproveRequest | None = None,
    db: AsyncSession = Depends(get_db),
    user: str = Depends(get_current_user),
):
    """Approve a pending reply (status → approved). Optionally override reply text."""
    em = await db.get(EmailDB, email_id)
    if not em:
        raise HTTPException(status_code=404, detail="Email not found")
    if em.status not in ("classified", "pending_approval"):
        raise HTTPException(status_code=400, detail=f"Cannot approve email with status '{em.status}'")

    if req and req.reply_text:
        em.suggested_reply = req.reply_text
    em.status = "approved"
    em.approved_by = user
    em.approved_at = datetime.now(timezone.utc)
    await db.commit()
    return {"email_id": email_id, "status": "approved", "approved_by": user}


@app.post("/api/emails/{email_id}/reject")
async def api_reject_email(
    email_id: str,
    db: AsyncSession = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    """Reject a pending reply (status → classified)."""
    em = await db.get(EmailDB, email_id)
    if not em:
        raise HTTPException(status_code=404, detail="Email not found")
    if em.status != "pending_approval":
        raise HTTPException(status_code=400, detail="Email is not pending approval")
    em.status = "classified"
    em.approved_by = None
    em.approved_at = None
    await db.commit()
    return {"email_id": email_id, "status": "classified"}


# ── Reply ───────────────────────────────────────────────
@app.post("/api/emails/{email_id}/reply")
async def api_send_reply(
    email_id: str,
    req: ReplyRequest,
    db: AsyncSession = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    em = await db.get(EmailDB, email_id)
    if not em:
        raise HTTPException(status_code=404, detail="Email not found")

    try:
        await send_reply(to=em.sender, subject=em.subject, body=req.reply_text)
        em.reply_sent = True
        em.reply_text = req.reply_text
        em.replied_at = datetime.now(timezone.utc)
        em.status = "replied"
        await db.commit()
        return {"success": True}
    except Exception as e:
        logger.exception("Reply failed")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/emails/{email_id}/generate-reply")
async def api_generate_reply(
    email_id: str,
    instructions: str = "",
    db: AsyncSession = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    em = await db.get(EmailDB, email_id)
    if not em:
        raise HTTPException(status_code=404, detail="Email not found")
    reply = await generate_custom_reply(em.sender, em.subject, em.body, instructions)
    return {"reply": reply}


# ── Templates ───────────────────────────────────────────
@app.get("/api/templates", response_model=list[TemplateOut])
async def api_list_templates(
    category: str | None = None,
    db: AsyncSession = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    query = select(ReplyTemplateDB).order_by(ReplyTemplateDB.category)
    if category:
        query = query.where(ReplyTemplateDB.category == category)
    result = await db.execute(query)
    return [TemplateOut.model_validate(t) for t in result.scalars().all()]


@app.post("/api/templates", response_model=TemplateOut)
async def api_create_template(
    req: TemplateIn,
    db: AsyncSession = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    t = ReplyTemplateDB(
        id=str(uuid.uuid4()),
        category=req.category,
        title=req.title,
        body=req.body,
    )
    db.add(t)
    await db.commit()
    await db.refresh(t)
    return TemplateOut.model_validate(t)


@app.get("/api/templates/{template_id}", response_model=TemplateOut)
async def api_get_template(
    template_id: str,
    db: AsyncSession = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    t = await db.get(ReplyTemplateDB, template_id)
    if not t:
        raise HTTPException(status_code=404, detail="Template not found")
    return TemplateOut.model_validate(t)


@app.put("/api/templates/{template_id}", response_model=TemplateOut)
async def api_update_template(
    template_id: str,
    req: TemplateIn,
    db: AsyncSession = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    t = await db.get(ReplyTemplateDB, template_id)
    if not t:
        raise HTTPException(status_code=404, detail="Template not found")
    t.category = req.category
    t.title = req.title
    t.body = req.body
    t.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(t)
    return TemplateOut.model_validate(t)


@app.delete("/api/templates/{template_id}")
async def api_delete_template(
    template_id: str,
    db: AsyncSession = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    t = await db.get(ReplyTemplateDB, template_id)
    if not t:
        raise HTTPException(status_code=404, detail="Template not found")
    await db.delete(t)
    await db.commit()
    return {"deleted": True}


# ── Settings ────────────────────────────────────────────
@app.get("/api/settings/email")
async def api_get_email_settings(_user: str = Depends(get_current_user)):
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
async def api_update_email_settings(
    s: EmailSettings, _user: str = Depends(get_current_user)
):
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
async def api_get_ai_settings(_user: str = Depends(get_current_user)):
    return AISettings(
        openai_api_key="***" if settings.openai_api_key else "",
        openai_base_url=settings.openai_base_url,
        openai_model=settings.openai_model,
        categories=settings.categories,
    )


@app.put("/api/settings/ai")
async def api_update_ai_settings(
    s: AISettings, _user: str = Depends(get_current_user)
):
    if s.openai_api_key != "***":
        settings.openai_api_key = s.openai_api_key
    settings.openai_base_url = s.openai_base_url
    settings.openai_model = s.openai_model
    settings.categories = s.categories
    return {"status": "updated"}


@app.get("/api/settings/polling", response_model=PollingSettings)
async def api_get_polling_settings(_user: str = Depends(get_current_user)):
    return PollingSettings(
        polling_enabled=settings.polling_enabled,
        polling_interval_seconds=settings.polling_interval_seconds,
        auto_approve_threshold=settings.auto_approve_threshold,
    )


@app.put("/api/settings/polling")
async def api_update_polling_settings(
    s: PollingSettings, _user: str = Depends(get_current_user)
):
    settings.polling_enabled = s.polling_enabled
    settings.polling_interval_seconds = s.polling_interval_seconds
    settings.auto_approve_threshold = s.auto_approve_threshold
    return {"status": "updated"}


# ── Stats ───────────────────────────────────────────────
@app.get("/api/stats")
async def api_stats(
    db: AsyncSession = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    total = (await db.execute(select(func.count(EmailDB.id)))).scalar() or 0

    status_rows = (
        await db.execute(
            select(EmailDB.status, func.count(EmailDB.id)).group_by(EmailDB.status)
        )
    ).all()
    by_status = {row[0]: row[1] for row in status_rows}

    cat_rows = (
        await db.execute(
            select(EmailDB.category, func.count(EmailDB.id))
            .where(EmailDB.category.isnot(None))
            .group_by(EmailDB.category)
        )
    ).all()
    by_category = {row[0]: row[1] for row in cat_rows}

    # Pending approval count
    pending = (
        await db.execute(
            select(func.count(EmailDB.id)).where(
                EmailDB.status == "pending_approval"
            )
        )
    ).scalar() or 0

    return {
        "total": total,
        "by_status": by_status,
        "by_category": by_category,
        "pending_approval": pending,
    }


# ── Mailboxes ───────────────────────────────────────────
@app.get("/api/mailboxes", response_model=list[MailboxOut])
async def api_list_mailboxes(
    db: AsyncSession = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    result = await db.execute(select(MailboxDB).order_by(MailboxDB.name))
    mailboxes = result.scalars().all()
    out = []
    for m in mailboxes:
        mo = MailboxOut.model_validate(m)
        mo.imap_password = "***" if m.imap_password else ""
        mo.smtp_password = "***" if m.smtp_password else ""
        out.append(mo)
    return out


@app.post("/api/mailboxes", response_model=MailboxOut)
async def api_create_mailbox(
    req: MailboxIn,
    db: AsyncSession = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    # Check for duplicate name
    existing = (await db.execute(select(MailboxDB).where(MailboxDB.name == req.name))).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Mailbox with this name already exists")
    m = MailboxDB(id=str(uuid.uuid4()), **req.model_dump())
    db.add(m)
    await db.commit()
    await db.refresh(m)
    out = MailboxOut.model_validate(m)
    out.imap_password = "***"
    out.smtp_password = "***"
    return out


@app.put("/api/mailboxes/{mailbox_id}", response_model=MailboxOut)
async def api_update_mailbox(
    mailbox_id: str,
    req: MailboxIn,
    db: AsyncSession = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    m = await db.get(MailboxDB, mailbox_id)
    if not m:
        raise HTTPException(status_code=404, detail="Mailbox not found")
    m.name = req.name
    m.imap_host = req.imap_host
    m.imap_port = req.imap_port
    m.imap_user = req.imap_user
    if req.imap_password != "***":
        m.imap_password = req.imap_password
    m.smtp_host = req.smtp_host
    m.smtp_port = req.smtp_port
    m.smtp_user = req.smtp_user
    if req.smtp_password != "***":
        m.smtp_password = req.smtp_password
    m.polling_enabled = req.polling_enabled
    await db.commit()
    await db.refresh(m)
    out = MailboxOut.model_validate(m)
    out.imap_password = "***"
    out.smtp_password = "***"
    return out


@app.delete("/api/mailboxes/{mailbox_id}")
async def api_delete_mailbox(
    mailbox_id: str,
    db: AsyncSession = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    m = await db.get(MailboxDB, mailbox_id)
    if not m:
        raise HTTPException(status_code=404, detail="Mailbox not found")
    await db.delete(m)
    await db.commit()
    return {"deleted": True}


# ── Accuracy / Feedback Stats ──────────────────────────
@app.get("/api/stats/accuracy")
async def api_accuracy_stats(
    db: AsyncSession = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    """Get classification accuracy based on human corrections."""
    # Total with human corrections
    total_corrected = (
        await db.execute(
            select(func.count(EmailDB.id)).where(EmailDB.category_human.isnot(None))
        )
    ).scalar() or 0

    if total_corrected == 0:
        return {
            "total_corrected": 0,
            "correct_predictions": 0,
            "incorrect": 0,
            "accuracy": 0.0,
            "by_category": {},
        }

    # Correct = AI category matches human category
    correct = (
        await db.execute(
            select(func.count(EmailDB.id)).where(
                EmailDB.category_human.isnot(None),
                EmailDB.category == EmailDB.category_human,
            )
        )
    ).scalar() or 0

    incorrect = total_corrected - correct

    # Breakdown by category
    cat_rows = (
        await db.execute(
            select(
                EmailDB.category_human,
                func.count(EmailDB.id),
                func.sum(
                    func.cast(EmailDB.category == EmailDB.category_human, Integer)
                ),
            )
            .where(EmailDB.category_human.isnot(None))
            .group_by(EmailDB.category_human)
        )
    ).all()

    by_category = {}
    for cat, total, correct_count in cat_rows:
        by_category[cat] = {
            "total": total,
            "correct": correct_count or 0,
            "accuracy": round((correct_count or 0) / total, 2) if total > 0 else 0,
        }

    return {
        "total_corrected": total_corrected,
        "correct_predictions": correct,
        "incorrect": incorrect,
        "accuracy": round(correct / total_corrected, 2) if total_corrected > 0 else 0,
        "by_category": by_category,
    }


# ── Seed (demo data) ───────────────────────────────────
@app.post("/api/seed")
async def api_seed(
    db: AsyncSession = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    mocks = generate_mock_emails()
    added = 0
    for em in mocks:
        existing = await db.execute(
            select(EmailDB).where(EmailDB.message_id == em["message_id"])
        )
        if existing.scalar_one_or_none():
            continue
        db.add(EmailDB(**em))
        added += 1
    await db.commit()
    return {"added": added, "total": len(mocks)}

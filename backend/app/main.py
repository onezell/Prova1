from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .auth import (
    LoginRequest,
    Token,
    authenticate_user,
    create_token,
    create_tokens,
    get_current_user,
)
from .classifier import classify_email, generate_custom_reply
from .config import settings
from .database import engine, get_db
from .db_models import Base, EmailDB
from .email_client import fetch_emails, send_reply
from .seed import generate_mock_emails
from .models import (
    AISettings,
    CorrectCategoryRequest,
    EmailListResponse,
    EmailOut,
    EmailSettings,
    ReplyRequest,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Email AI Classifier POC started — database ready")
    yield


app = FastAPI(title="Email AI Classifier", version="0.2.0", lifespan=lifespan)

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
    return {"status": "ok"}


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
            # Deduplicate by message_id
            if em.get("message_id"):
                existing = await db.execute(
                    select(EmailDB).where(EmailDB.message_id == em["message_id"])
                )
                if existing.scalar_one_or_none():
                    continue

            db_email = EmailDB(**em)
            db.add(db_email)
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

    result = await classify_email(em.sender, em.subject, em.body)
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
    result = await db.execute(select(EmailDB).where(EmailDB.status == "new"))
    emails = result.scalars().all()
    classified = []

    for em in emails:
        try:
            res = await classify_email(em.sender, em.subject, em.body)
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


# ── Stats ───────────────────────────────────────────────
@app.get("/api/stats")
async def api_stats(
    db: AsyncSession = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    total = (await db.execute(select(func.count(EmailDB.id)))).scalar() or 0

    # By status
    status_rows = (
        await db.execute(
            select(EmailDB.status, func.count(EmailDB.id)).group_by(EmailDB.status)
        )
    ).all()
    by_status = {row[0]: row[1] for row in status_rows}

    # By category
    cat_rows = (
        await db.execute(
            select(EmailDB.category, func.count(EmailDB.id))
            .where(EmailDB.category.isnot(None))
            .group_by(EmailDB.category)
        )
    ).all()
    by_category = {row[0]: row[1] for row in cat_rows}

    return {"total": total, "by_status": by_status, "by_category": by_category}


# ── Seed (demo data) ───────────────────────────────────
@app.post("/api/seed")
async def api_seed(
    db: AsyncSession = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    """Load mock emails for demo purposes."""
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

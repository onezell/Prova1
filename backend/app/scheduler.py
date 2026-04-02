"""Background scheduler for IMAP polling and auto-classification."""

from __future__ import annotations

import asyncio
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .classifier import classify_email
from .config import settings
from .database import async_session
from .db_models import EmailDB
from .email_client import fetch_emails

logger = logging.getLogger(__name__)

_task: asyncio.Task | None = None


async def _poll_and_classify():
    """Single poll cycle: fetch new emails from IMAP and classify them."""
    logger.info("Polling: fetching emails from IMAP...")
    try:
        raw_emails = fetch_emails(limit=50)
    except Exception:
        logger.exception("Polling: IMAP fetch failed")
        return 0, 0

    added = 0
    classified = 0

    async with async_session() as db:
        # Insert new emails
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

        # Auto-classify new emails
        result = await db.execute(select(EmailDB).where(EmailDB.status == "new"))
        new_emails = result.scalars().all()

        for em in new_emails:
            try:
                res = await classify_email(em.sender, em.subject, em.body)
                em.category = res.category
                em.confidence = res.confidence
                em.summary = res.summary
                em.suggested_reply = res.suggested_reply

                # Auto-approve if above threshold
                if (
                    settings.auto_approve_threshold > 0
                    and res.confidence >= settings.auto_approve_threshold
                ):
                    em.status = "approved"
                else:
                    em.status = "classified"

                classified += 1
            except Exception:
                logger.exception("Polling: classification failed for %s", em.id)

        await db.commit()

    logger.info("Polling complete: %d added, %d classified", added, classified)
    return added, classified


async def _scheduler_loop():
    """Run polling on a fixed interval."""
    while True:
        if settings.polling_enabled and settings.imap_user and settings.imap_password:
            try:
                await _poll_and_classify()
            except Exception:
                logger.exception("Scheduler loop error")
        await asyncio.sleep(settings.polling_interval_seconds)


def start_scheduler():
    """Start the background scheduler task."""
    global _task
    if _task is None or _task.done():
        _task = asyncio.create_task(_scheduler_loop())
        logger.info(
            "Scheduler started (interval=%ds, enabled=%s)",
            settings.polling_interval_seconds,
            settings.polling_enabled,
        )


def stop_scheduler():
    """Stop the background scheduler task."""
    global _task
    if _task and not _task.done():
        _task.cancel()
        _task = None
        logger.info("Scheduler stopped")


def is_scheduler_running() -> bool:
    return _task is not None and not _task.done()

from __future__ import annotations

import email
import email.utils
import logging
import uuid
from datetime import datetime, timezone
from email.mime.text import MIMEText

import aiosmtplib
from imapclient import IMAPClient

from .config import settings

logger = logging.getLogger(__name__)


def fetch_emails(limit: int = 50, folder: str = "INBOX") -> list[dict]:
    """Fetch recent emails via IMAP. Returns dicts ready for DB insertion."""
    if not settings.imap_user or not settings.imap_password:
        raise ValueError("IMAP credentials not configured")

    emails: list[dict] = []

    with IMAPClient(settings.imap_host, port=settings.imap_port, ssl=True) as client:
        client.login(settings.imap_user, settings.imap_password)
        client.select_folder(folder, readonly=True)

        uids = client.search(["ALL"])
        uids = uids[-limit:]

        raw_messages = client.fetch(uids, ["RFC822", "ENVELOPE"])

        for uid, data in raw_messages.items():
            try:
                raw = data[b"RFC822"]
                msg = email.message_from_bytes(raw)

                body = ""
                body_html = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        ct = part.get_content_type()
                        if ct == "text/plain" and not body:
                            payload = part.get_payload(decode=True)
                            if payload:
                                body = payload.decode(errors="replace")
                        elif ct == "text/html" and not body_html:
                            payload = part.get_payload(decode=True)
                            if payload:
                                body_html = payload.decode(errors="replace")
                else:
                    payload = msg.get_payload(decode=True)
                    if payload:
                        body = payload.decode(errors="replace")

                date_str = msg.get("Date", "")
                date_val = (
                    email.utils.parsedate_to_datetime(date_str)
                    if date_str
                    else datetime.now(timezone.utc)
                )

                emails.append(
                    {
                        "id": str(uuid.uuid4()),
                        "message_id": msg.get("Message-ID", ""),
                        "uid": int(uid),
                        "subject": msg.get("Subject", "(no subject)"),
                        "sender": msg.get("From", "unknown"),
                        "date": date_val,
                        "body": body,
                        "body_html": body_html,
                        "status": "new",
                    }
                )
            except Exception:
                logger.exception("Failed to parse email uid=%s", uid)

    return emails


async def send_reply(
    to: str, subject: str, body: str, in_reply_to: str | None = None
) -> bool:
    """Send a reply email via SMTP."""
    if not settings.smtp_user or not settings.smtp_password:
        raise ValueError("SMTP credentials not configured")

    msg = MIMEText(body, "plain", "utf-8")
    msg["From"] = settings.smtp_user
    msg["To"] = to
    msg["Subject"] = f"Re: {subject}" if not subject.startswith("Re:") else subject
    if in_reply_to:
        msg["In-Reply-To"] = in_reply_to

    await aiosmtplib.send(
        msg,
        hostname=settings.smtp_host,
        port=settings.smtp_port,
        username=settings.smtp_user,
        password=settings.smtp_password,
        start_tls=True,
    )
    return True

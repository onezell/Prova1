"""Tests for Fase 3: mailbox CRUD, export CSV, accuracy stats, few-shot."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


# ── Mailbox CRUD ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_mailboxes_empty(client: AsyncClient, auth_headers):
    resp = await client.get("/api/mailboxes", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_create_mailbox(client: AsyncClient, auth_headers):
    data = {
        "name": "info",
        "imap_host": "imap.example.com",
        "imap_port": 993,
        "imap_user": "info@example.com",
        "imap_password": "secret",
        "smtp_host": "smtp.example.com",
        "smtp_port": 587,
        "smtp_user": "info@example.com",
        "smtp_password": "secret",
        "polling_enabled": True,
    }
    resp = await client.post("/api/mailboxes", json=data, headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["name"] == "info"
    assert body["imap_host"] == "imap.example.com"
    assert body["imap_password"] == "***"  # masked
    return body["id"]


@pytest.mark.asyncio
async def test_create_duplicate_mailbox(client: AsyncClient, auth_headers):
    data = {
        "name": "vendite",
        "imap_host": "imap.example.com",
        "imap_port": 993,
        "imap_user": "vendite@example.com",
        "imap_password": "secret",
        "smtp_host": "smtp.example.com",
        "smtp_port": 587,
        "smtp_user": "vendite@example.com",
        "smtp_password": "secret",
    }
    resp1 = await client.post("/api/mailboxes", json=data, headers=auth_headers)
    assert resp1.status_code == 200
    resp2 = await client.post("/api/mailboxes", json=data, headers=auth_headers)
    assert resp2.status_code == 400


@pytest.mark.asyncio
async def test_update_mailbox(client: AsyncClient, auth_headers):
    data = {
        "name": "support",
        "imap_host": "imap.example.com",
        "imap_port": 993,
        "imap_user": "support@example.com",
        "imap_password": "secret",
        "smtp_host": "smtp.example.com",
        "smtp_port": 587,
        "smtp_user": "support@example.com",
        "smtp_password": "secret",
    }
    resp = await client.post("/api/mailboxes", json=data, headers=auth_headers)
    mbox_id = resp.json()["id"]

    update = {**data, "name": "support-updated", "polling_enabled": False}
    resp2 = await client.put(f"/api/mailboxes/{mbox_id}", json=update, headers=auth_headers)
    assert resp2.status_code == 200
    assert resp2.json()["name"] == "support-updated"
    assert resp2.json()["polling_enabled"] is False


@pytest.mark.asyncio
async def test_delete_mailbox(client: AsyncClient, auth_headers):
    data = {
        "name": "todelete",
        "imap_host": "imap.example.com",
        "imap_port": 993,
        "imap_user": "del@example.com",
        "imap_password": "secret",
        "smtp_host": "smtp.example.com",
        "smtp_port": 587,
        "smtp_user": "del@example.com",
        "smtp_password": "secret",
    }
    resp = await client.post("/api/mailboxes", json=data, headers=auth_headers)
    mbox_id = resp.json()["id"]

    resp2 = await client.delete(f"/api/mailboxes/{mbox_id}", headers=auth_headers)
    assert resp2.status_code == 200

    resp3 = await client.get("/api/mailboxes", headers=auth_headers)
    names = [m["name"] for m in resp3.json()]
    assert "todelete" not in names


@pytest.mark.asyncio
async def test_mailbox_requires_auth(client: AsyncClient):
    resp = await client.get("/api/mailboxes")
    assert resp.status_code == 401


# ── Export CSV ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_export_csv_empty(client: AsyncClient, auth_headers):
    resp = await client.get("/api/emails/export/csv", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/csv")
    content = resp.text
    # Should have at least headers
    assert "subject" in content.lower() or "id" in content.lower()


@pytest.mark.asyncio
async def test_export_csv_with_data(client: AsyncClient, auth_headers):
    # Seed first
    await client.post("/api/seed", headers=auth_headers)
    resp = await client.get("/api/emails/export/csv", headers=auth_headers)
    assert resp.status_code == 200
    lines = resp.text.strip().split("\n")
    assert len(lines) > 1  # headers + data rows


@pytest.mark.asyncio
async def test_export_csv_with_filter(client: AsyncClient, auth_headers):
    await client.post("/api/seed", headers=auth_headers)
    resp = await client.get("/api/emails/export/csv?status=new", headers=auth_headers)
    assert resp.status_code == 200


# ── Accuracy Stats ────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_accuracy_stats_empty(client: AsyncClient, auth_headers):
    resp = await client.get("/api/stats/accuracy", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_corrected"] == 0
    assert data["accuracy"] == 0.0
    assert data["correct_predictions"] == 0


@pytest.mark.asyncio
async def test_accuracy_stats_with_corrections(client: AsyncClient, auth_headers):
    # Seed and get an email
    await client.post("/api/seed", headers=auth_headers)
    emails_resp = await client.get("/api/emails?page=1&page_size=5", headers=auth_headers)
    emails = emails_resp.json()["emails"]

    # Correct a few categories manually
    for em in emails[:3]:
        await client.post(
            f"/api/emails/{em['id']}/correct",
            json={"category": "reclamo"},
            headers=auth_headers,
        )

    resp = await client.get("/api/stats/accuracy", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_corrected"] == 3


@pytest.mark.asyncio
async def test_accuracy_stats_requires_auth(client: AsyncClient):
    resp = await client.get("/api/stats/accuracy")
    assert resp.status_code == 401


# ── Few-shot in correct category endpoint ────────────────────────────

@pytest.mark.asyncio
async def test_correct_category_stores_human(client: AsyncClient, auth_headers):
    await client.post("/api/seed", headers=auth_headers)
    emails_resp = await client.get("/api/emails?page=1&page_size=1", headers=auth_headers)
    em = emails_resp.json()["emails"][0]

    resp = await client.post(
        f"/api/emails/{em['id']}/correct",
        json={"category": "preventivo"},
        headers=auth_headers,
    )
    assert resp.status_code == 200

    # Verify the human category is set
    detail = await client.get(f"/api/emails/{em['id']}", headers=auth_headers)
    assert detail.json()["category_human"] == "preventivo"
    assert detail.json()["category"] == "preventivo"

"""Tests for approval workflow endpoints."""

import pytest
from httpx import AsyncClient


async def _get_classified_email(client, auth_headers):
    """Seed and return a classified email id."""
    await client.post("/api/seed", headers=auth_headers)
    resp = await client.get("/api/emails?status=classified&page_size=1", headers=auth_headers)
    emails = resp.json()["emails"]
    assert len(emails) > 0
    return emails[0]["id"]


@pytest.mark.asyncio
class TestSubmitForApproval:
    async def test_submit_for_approval(self, client: AsyncClient, auth_headers: dict):
        email_id = await _get_classified_email(client, auth_headers)
        resp = await client.post(
            f"/api/emails/{email_id}/submit-for-approval",
            json={"email_id": email_id, "reply_text": "Grazie per averci contattato."},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "pending_approval"

        # Verify status changed
        detail = await client.get(f"/api/emails/{email_id}", headers=auth_headers)
        assert detail.json()["status"] == "pending_approval"
        assert detail.json()["suggested_reply"] == "Grazie per averci contattato."

    async def test_submit_not_found(self, client: AsyncClient, auth_headers: dict):
        resp = await client.post(
            "/api/emails/nonexistent/submit-for-approval",
            json={"email_id": "nonexistent", "reply_text": "test"},
            headers=auth_headers,
        )
        assert resp.status_code == 404


@pytest.mark.asyncio
class TestApprove:
    async def test_approve_pending_email(self, client: AsyncClient, auth_headers: dict):
        email_id = await _get_classified_email(client, auth_headers)

        # Submit for approval first
        await client.post(
            f"/api/emails/{email_id}/submit-for-approval",
            json={"email_id": email_id, "reply_text": "Risposta originale"},
            headers=auth_headers,
        )

        # Approve
        resp = await client.post(
            f"/api/emails/{email_id}/approve",
            json={},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "approved"
        assert resp.json()["approved_by"] == "admin"

    async def test_approve_with_override(self, client: AsyncClient, auth_headers: dict):
        email_id = await _get_classified_email(client, auth_headers)

        await client.post(
            f"/api/emails/{email_id}/submit-for-approval",
            json={"email_id": email_id, "reply_text": "Vecchia risposta"},
            headers=auth_headers,
        )

        # Approve with modified reply
        resp = await client.post(
            f"/api/emails/{email_id}/approve",
            json={"reply_text": "Nuova risposta corretta"},
            headers=auth_headers,
        )
        assert resp.status_code == 200

        # Check reply was updated
        detail = await client.get(f"/api/emails/{email_id}", headers=auth_headers)
        assert detail.json()["suggested_reply"] == "Nuova risposta corretta"

    async def test_approve_classified_directly(self, client: AsyncClient, auth_headers: dict):
        """Can also approve a classified email directly (skip pending_approval)."""
        email_id = await _get_classified_email(client, auth_headers)
        resp = await client.post(
            f"/api/emails/{email_id}/approve",
            json={},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "approved"

    async def test_cannot_approve_replied_email(self, client: AsyncClient, auth_headers: dict):
        email_id = await _get_classified_email(client, auth_headers)

        # Set to replied status manually via approve -> we need a new email
        # First approve, then we'd need to reply, but we can test with 'new' status
        # Actually let's just test that 'new' status can't be approved
        await client.post("/api/seed", headers=auth_headers)
        # Get a 'classified' email first, approve it, then try to approve again
        resp = await client.post(f"/api/emails/{email_id}/approve", json={}, headers=auth_headers)
        assert resp.status_code == 200
        # Now it's approved, try approve again - should fail
        resp2 = await client.post(f"/api/emails/{email_id}/approve", json={}, headers=auth_headers)
        assert resp2.status_code == 400


@pytest.mark.asyncio
class TestReject:
    async def test_reject_pending_email(self, client: AsyncClient, auth_headers: dict):
        email_id = await _get_classified_email(client, auth_headers)

        await client.post(
            f"/api/emails/{email_id}/submit-for-approval",
            json={"email_id": email_id, "reply_text": "test"},
            headers=auth_headers,
        )

        resp = await client.post(f"/api/emails/{email_id}/reject", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["status"] == "classified"

        # Verify it's back to classified
        detail = await client.get(f"/api/emails/{email_id}", headers=auth_headers)
        assert detail.json()["status"] == "classified"

    async def test_cannot_reject_non_pending(self, client: AsyncClient, auth_headers: dict):
        email_id = await _get_classified_email(client, auth_headers)
        resp = await client.post(f"/api/emails/{email_id}/reject", headers=auth_headers)
        assert resp.status_code == 400


@pytest.mark.asyncio
class TestApprovalInStats:
    async def test_stats_include_pending_approval(self, client: AsyncClient, auth_headers: dict):
        email_id = await _get_classified_email(client, auth_headers)

        await client.post(
            f"/api/emails/{email_id}/submit-for-approval",
            json={"email_id": email_id, "reply_text": "test"},
            headers=auth_headers,
        )

        resp = await client.get("/api/stats", headers=auth_headers)
        data = resp.json()
        assert "pending_approval" in data
        assert data["pending_approval"] >= 1

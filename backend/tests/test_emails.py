"""Tests for email endpoints: seed, list, get, pagination, stats."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestSeed:
    async def test_seed_loads_mock_emails(self, client: AsyncClient, auth_headers: dict):
        resp = await client.post("/api/seed", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["added"] == 12
        assert data["total"] == 12

    async def test_seed_is_idempotent(self, client: AsyncClient, auth_headers: dict):
        await client.post("/api/seed", headers=auth_headers)
        resp = await client.post("/api/seed", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["added"] == 0  # no duplicates

    async def test_seed_requires_auth(self, client: AsyncClient):
        resp = await client.post("/api/seed")
        assert resp.status_code == 401


@pytest.mark.asyncio
class TestEmailList:
    async def test_list_empty(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get("/api/emails", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0
        assert data["emails"] == []
        assert data["page"] == 1

    async def test_list_with_data(self, client: AsyncClient, auth_headers: dict):
        await client.post("/api/seed", headers=auth_headers)
        resp = await client.get("/api/emails", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 12
        assert len(data["emails"]) <= 20  # default page_size

    async def test_list_pagination(self, client: AsyncClient, auth_headers: dict):
        await client.post("/api/seed", headers=auth_headers)

        resp = await client.get("/api/emails?page=1&page_size=5", headers=auth_headers)
        data = resp.json()
        assert len(data["emails"]) == 5
        assert data["total"] == 12
        assert data["page"] == 1

        resp2 = await client.get("/api/emails?page=2&page_size=5", headers=auth_headers)
        data2 = resp2.json()
        assert len(data2["emails"]) == 5
        assert data2["page"] == 2

        # Page 3 should have remaining 2
        resp3 = await client.get("/api/emails?page=3&page_size=5", headers=auth_headers)
        data3 = resp3.json()
        assert len(data3["emails"]) == 2

    async def test_list_filter_by_status(self, client: AsyncClient, auth_headers: dict):
        await client.post("/api/seed", headers=auth_headers)
        resp = await client.get("/api/emails?status=classified", headers=auth_headers)
        data = resp.json()
        assert data["total"] > 0
        for email in data["emails"]:
            assert email["status"] == "classified"

    async def test_list_filter_by_category(self, client: AsyncClient, auth_headers: dict):
        await client.post("/api/seed", headers=auth_headers)
        resp = await client.get("/api/emails?category=reclamo", headers=auth_headers)
        data = resp.json()
        assert data["total"] >= 1
        for email in data["emails"]:
            assert email["category"] == "reclamo"

    async def test_list_requires_auth(self, client: AsyncClient):
        resp = await client.get("/api/emails")
        assert resp.status_code == 401


@pytest.mark.asyncio
class TestEmailDetail:
    async def test_get_email(self, client: AsyncClient, auth_headers: dict):
        await client.post("/api/seed", headers=auth_headers)
        list_resp = await client.get("/api/emails?page_size=1", headers=auth_headers)
        email_id = list_resp.json()["emails"][0]["id"]

        resp = await client.get(f"/api/emails/{email_id}", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == email_id
        assert data["subject"]
        assert data["sender"]
        assert data["body"]

    async def test_get_email_not_found(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get("/api/emails/nonexistent-id", headers=auth_headers)
        assert resp.status_code == 404

    async def test_get_email_requires_auth(self, client: AsyncClient):
        resp = await client.get("/api/emails/some-id")
        assert resp.status_code == 401


@pytest.mark.asyncio
class TestCorrectCategory:
    async def test_correct_category(self, client: AsyncClient, auth_headers: dict):
        await client.post("/api/seed", headers=auth_headers)
        list_resp = await client.get("/api/emails?page_size=1", headers=auth_headers)
        email_id = list_resp.json()["emails"][0]["id"]

        resp = await client.post(
            f"/api/emails/{email_id}/correct",
            json={"category": "reclamo"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["category_human"] == "reclamo"

        # Verify it persisted
        detail = await client.get(f"/api/emails/{email_id}", headers=auth_headers)
        assert detail.json()["category_human"] == "reclamo"

    async def test_correct_category_not_found(self, client: AsyncClient, auth_headers: dict):
        resp = await client.post(
            "/api/emails/nonexistent/correct",
            json={"category": "reclamo"},
            headers=auth_headers,
        )
        assert resp.status_code == 404

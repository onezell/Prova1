"""Tests for settings endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestEmailSettings:
    async def test_get_email_settings(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get("/api/settings/email", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "imap_host" in data
        assert "smtp_host" in data
        # Password should be masked
        assert data["imap_password"] in ("", "***")

    async def test_update_email_settings(self, client: AsyncClient, auth_headers: dict):
        resp = await client.put(
            "/api/settings/email",
            json={
                "imap_host": "imap.test.com",
                "imap_port": 993,
                "imap_user": "test@test.com",
                "imap_password": "***",
                "smtp_host": "smtp.test.com",
                "smtp_port": 587,
                "smtp_user": "test@test.com",
                "smtp_password": "newpass",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 200

        # Verify changes
        resp2 = await client.get("/api/settings/email", headers=auth_headers)
        data = resp2.json()
        assert data["imap_host"] == "imap.test.com"
        assert data["smtp_host"] == "smtp.test.com"

    async def test_settings_require_auth(self, client: AsyncClient):
        resp = await client.get("/api/settings/email")
        assert resp.status_code == 401


@pytest.mark.asyncio
class TestAISettings:
    async def test_get_ai_settings(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get("/api/settings/ai", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "openai_base_url" in data
        assert "openai_model" in data
        assert "categories" in data
        assert isinstance(data["categories"], list)
        assert len(data["categories"]) > 0

    async def test_update_ai_settings(self, client: AsyncClient, auth_headers: dict):
        resp = await client.put(
            "/api/settings/ai",
            json={
                "openai_api_key": "***",
                "openai_base_url": "https://custom.api.com/v1",
                "openai_model": "gpt-4o",
                "categories": ["cat_a", "cat_b"],
            },
            headers=auth_headers,
        )
        assert resp.status_code == 200

        resp2 = await client.get("/api/settings/ai", headers=auth_headers)
        data = resp2.json()
        assert data["openai_base_url"] == "https://custom.api.com/v1"
        assert data["openai_model"] == "gpt-4o"
        assert data["categories"] == ["cat_a", "cat_b"]

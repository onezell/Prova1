"""Tests for reply template CRUD endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestTemplatesCRUD:
    async def test_list_templates_empty(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get("/api/templates", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_create_template(self, client: AsyncClient, auth_headers: dict):
        resp = await client.post(
            "/api/templates",
            json={
                "category": "reclamo",
                "title": "Risposta standard reclamo",
                "body": "Gentile {{mittente}},\n\nCi scusiamo per il disagio.",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["category"] == "reclamo"
        assert data["title"] == "Risposta standard reclamo"
        assert "{{mittente}}" in data["body"]
        assert data["id"]

    async def test_list_templates_after_create(self, client: AsyncClient, auth_headers: dict):
        await client.post(
            "/api/templates",
            json={"category": "reclamo", "title": "T1", "body": "Body 1"},
            headers=auth_headers,
        )
        await client.post(
            "/api/templates",
            json={"category": "richiesta_info", "title": "T2", "body": "Body 2"},
            headers=auth_headers,
        )

        resp = await client.get("/api/templates", headers=auth_headers)
        assert len(resp.json()) == 2

    async def test_filter_templates_by_category(self, client: AsyncClient, auth_headers: dict):
        await client.post(
            "/api/templates",
            json={"category": "reclamo", "title": "T1", "body": "B1"},
            headers=auth_headers,
        )
        await client.post(
            "/api/templates",
            json={"category": "preventivo", "title": "T2", "body": "B2"},
            headers=auth_headers,
        )

        resp = await client.get("/api/templates?category=reclamo", headers=auth_headers)
        data = resp.json()
        assert len(data) == 1
        assert data[0]["category"] == "reclamo"

    async def test_get_template(self, client: AsyncClient, auth_headers: dict):
        create_resp = await client.post(
            "/api/templates",
            json={"category": "spam", "title": "Ignore", "body": "Nessuna risposta"},
            headers=auth_headers,
        )
        tid = create_resp.json()["id"]

        resp = await client.get(f"/api/templates/{tid}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["title"] == "Ignore"

    async def test_get_template_not_found(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get("/api/templates/nonexistent", headers=auth_headers)
        assert resp.status_code == 404

    async def test_update_template(self, client: AsyncClient, auth_headers: dict):
        create_resp = await client.post(
            "/api/templates",
            json={"category": "reclamo", "title": "Vecchio", "body": "Old body"},
            headers=auth_headers,
        )
        tid = create_resp.json()["id"]

        resp = await client.put(
            f"/api/templates/{tid}",
            json={"category": "reclamo", "title": "Nuovo", "body": "New body"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["title"] == "Nuovo"
        assert resp.json()["body"] == "New body"

    async def test_delete_template(self, client: AsyncClient, auth_headers: dict):
        create_resp = await client.post(
            "/api/templates",
            json={"category": "altro", "title": "ToDelete", "body": "X"},
            headers=auth_headers,
        )
        tid = create_resp.json()["id"]

        resp = await client.delete(f"/api/templates/{tid}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["deleted"] is True

        # Verify gone
        resp2 = await client.get(f"/api/templates/{tid}", headers=auth_headers)
        assert resp2.status_code == 404

    async def test_templates_require_auth(self, client: AsyncClient):
        resp = await client.get("/api/templates")
        assert resp.status_code == 401


@pytest.mark.asyncio
class TestPollingSettings:
    async def test_get_polling_settings(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get("/api/settings/polling", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "polling_enabled" in data
        assert "polling_interval_seconds" in data
        assert "auto_approve_threshold" in data

    async def test_update_polling_settings(self, client: AsyncClient, auth_headers: dict):
        resp = await client.put(
            "/api/settings/polling",
            json={
                "polling_enabled": True,
                "polling_interval_seconds": 120,
                "auto_approve_threshold": 0.85,
            },
            headers=auth_headers,
        )
        assert resp.status_code == 200

        resp2 = await client.get("/api/settings/polling", headers=auth_headers)
        data = resp2.json()
        assert data["polling_enabled"] is True
        assert data["polling_interval_seconds"] == 120
        assert data["auto_approve_threshold"] == 0.85

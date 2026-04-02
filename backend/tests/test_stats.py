"""Tests for stats endpoint."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestStats:
    async def test_stats_empty(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get("/api/stats", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0
        assert data["by_status"] == {}
        assert data["by_category"] == {}

    async def test_stats_with_data(self, client: AsyncClient, auth_headers: dict):
        await client.post("/api/seed", headers=auth_headers)
        resp = await client.get("/api/stats", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 12
        assert "classified" in data["by_status"]
        assert sum(data["by_status"].values()) == 12
        # Check categories from mock data
        assert "preventivo" in data["by_category"]
        assert "reclamo" in data["by_category"]
        assert "spam" in data["by_category"]
        assert sum(data["by_category"].values()) == 12

    async def test_stats_requires_auth(self, client: AsyncClient):
        resp = await client.get("/api/stats")
        assert resp.status_code == 401

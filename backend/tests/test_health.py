"""Tests for health endpoint."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestHealth:
    async def test_health_no_auth_required(self, client: AsyncClient):
        resp = await client.get("/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "scheduler" in data

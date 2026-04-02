"""Tests for authentication endpoints and JWT logic."""

import pytest
from httpx import AsyncClient

from app.auth import authenticate_user, create_token, decode_token


# ── Unit tests: auth functions ──────────────────────────

class TestAuthFunctions:
    def test_authenticate_user_success(self):
        result = authenticate_user("admin", "testpass")
        assert result == "admin"

    def test_authenticate_user_wrong_password(self):
        result = authenticate_user("admin", "wrongpass")
        assert result is None

    def test_authenticate_user_wrong_username(self):
        result = authenticate_user("nobody", "testpass")
        assert result is None

    def test_create_and_decode_token(self):
        token = create_token("admin", expires_minutes=60)
        payload = decode_token(token)
        assert payload["sub"] == "admin"
        assert "exp" in payload

    def test_decode_token_invalid(self):
        with pytest.raises(ValueError):
            decode_token("invalid.token.here")

    def test_decode_token_tampered(self):
        token = create_token("admin", expires_minutes=60)
        parts = token.split(".")
        parts[1] = parts[1] + "x"  # tamper payload
        with pytest.raises(ValueError):
            decode_token(".".join(parts))

    def test_decode_token_expired(self):
        token = create_token("admin", expires_minutes=-1)
        with pytest.raises(ValueError, match="expired"):
            decode_token(token)


# ── Integration tests: auth endpoints ───────────────────

@pytest.mark.asyncio
class TestAuthEndpoints:
    async def test_login_success(self, client: AsyncClient):
        resp = await client.post("/api/auth/login", json={"username": "admin", "password": "testpass"})
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_wrong_password(self, client: AsyncClient):
        resp = await client.post("/api/auth/login", json={"username": "admin", "password": "wrong"})
        assert resp.status_code == 401

    async def test_login_wrong_username(self, client: AsyncClient):
        resp = await client.post("/api/auth/login", json={"username": "hacker", "password": "testpass"})
        assert resp.status_code == 401

    async def test_me_authenticated(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get("/api/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["username"] == "admin"

    async def test_me_no_token(self, client: AsyncClient):
        resp = await client.get("/api/auth/me")
        assert resp.status_code == 401

    async def test_me_invalid_token(self, client: AsyncClient):
        resp = await client.get("/api/auth/me", headers={"Authorization": "Bearer garbage"})
        assert resp.status_code == 401

    async def test_refresh_token(self, client: AsyncClient, auth_headers: dict):
        resp = await client.post("/api/auth/refresh", headers=auth_headers)
        assert resp.status_code == 200
        assert "access_token" in resp.json()

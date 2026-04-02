from __future__ import annotations

import hashlib
import hmac
import json
import base64
import time

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from .config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    username: str
    password: str


def _b64encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64decode(s: str) -> bytes:
    padding = 4 - len(s) % 4
    if padding != 4:
        s += "=" * padding
    return base64.urlsafe_b64decode(s)


def _sign(payload: str, secret: str) -> str:
    return _b64encode(
        hmac.new(secret.encode(), payload.encode(), hashlib.sha256).digest()
    )


def create_token(username: str, expires_minutes: int) -> str:
    header = _b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    payload = _b64encode(
        json.dumps(
            {"sub": username, "exp": int(time.time()) + expires_minutes * 60}
        ).encode()
    )
    msg = f"{header}.{payload}"
    sig = _sign(msg, settings.jwt_secret)
    return f"{msg}.{sig}"


def decode_token(token: str) -> dict:
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("Invalid token")
    msg = f"{parts[0]}.{parts[1]}"
    expected_sig = _sign(msg, settings.jwt_secret)
    if not hmac.compare_digest(expected_sig, parts[2]):
        raise ValueError("Invalid signature")
    payload = json.loads(_b64decode(parts[1]))
    if payload.get("exp", 0) < time.time():
        raise ValueError("Token expired")
    return payload


def create_tokens(username: str) -> Token:
    return Token(
        access_token=create_token(username, settings.jwt_expire_minutes),
        refresh_token=create_token(username, settings.jwt_refresh_expire_minutes),
    )


async def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token non valido",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except (ValueError, KeyError):
        raise credentials_exception


def authenticate_user(username: str, password: str) -> str | None:
    if username != settings.admin_username:
        return None
    if password != settings.admin_password:
        return None
    return username

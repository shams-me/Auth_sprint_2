import base64
import http
import time
from datetime import datetime, timezone
from functools import wraps
from typing import Annotated, List, Optional

import aiohttp
import jwt
from core.config import settings
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from models.oauth import Roles, User


class JWTBearer(HTTPBearer):
    def __init__(self, check_user: bool = False, auto_error: bool = True):
        super().__init__(auto_error=auto_error)
        self.check_user = check_user

    async def __call__(self, request: Request) -> dict:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if not credentials:
            raise HTTPException(
                status_code=http.HTTPStatus.FORBIDDEN,
                detail="Invalid authorization code",
            )
        if not credentials.scheme == "Bearer":
            raise HTTPException(
                status_code=http.HTTPStatus.UNAUTHORIZED,
                detail="Only Bearer token might be accepted",
            )
        decoded_token = self.decode(credentials.credentials)
        if not decoded_token:
            raise HTTPException(status_code=http.HTTPStatus.FORBIDDEN, detail="Invalid or expired token")

        if self.check_user:
            response = await self.check(
                settings.auth_url_me,
                params={},
                headers={"Authorization": f"Bearer {credentials.credentials}"},
            )
            if response.status != http.HTTPStatus.ACCEPTED:
                raise HTTPException(status_code=http.HTTPStatus.FORBIDDEN, detail="User doesn't exist")
            return await response.json()
        return decoded_token

    @staticmethod
    def decode(jwt_token: str) -> Optional[dict]:
        try:
            decoded_token = jwt.decode(jwt_token, options={"verify_signature": False})
            current_time = int(datetime.now(timezone.utc).timestamp())
            return decoded_token if decoded_token["exp"] >= current_time else None
        except Exception:
            return None

    @staticmethod
    async def check(query: str, params: dict = {}, headers: dict = {}, json: dict = {}):
        async with aiohttp.ClientSession(headers=headers) as client:
            response = await client.get(query, json=json, params=params)
        return response


security_jwt = JWTBearer()
security_jwt_verified = JWTBearer(check_user=True)


def allowed_user(roles: List[Roles]):
    def decorator(user: Annotated[dict, Depends(security_jwt_verified)]):
        if user["role"] == Roles.SUPERUSER:
            return

        if user["role"] not in roles:
            raise HTTPException(status_code=http.HTTPStatus.FORBIDDEN, detail="Insufficient permissions")

        return

    return decorator

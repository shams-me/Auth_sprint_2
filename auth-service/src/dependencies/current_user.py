from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from services.auth import AbstractAuthService, get_auth_service
from starlette import status

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    auth_service: AbstractAuthService = Depends(get_auth_service),
):
    user = auth_service.token_handler.decode(token)
    user = await auth_service.get_user(user.get("user_id"))
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found.")
    return user

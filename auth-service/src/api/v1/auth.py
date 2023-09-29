from typing import Annotated

from dependencies.current_user import get_current_user
from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from schemas.entity import (
    SuccessfulAuth,
    SuccessfulLogout,
    UserInfo,
    UserLogin,
    UserLoginHistory,
    UserRegistration,
    UserUpdate,
)
from services.auth import AbstractAuthService, get_auth_service

router = APIRouter()


def token_persistence_validation(authorization: str = Header(...)):
    token = authorization.split("Bearer ")[-1]
    if not token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="JWT Token is required.")
    return token


# FIXME: move all exceptions to the service side


@router.get(
    "/me",
    summary="Get current user information.",
    description="Must provide Bearear header",
    tags=["Auth"],
    response_model=UserInfo,
)
async def get_current_user_route(user=Depends(get_current_user)):
    return UserInfo(username=user.username, email=user.email, role=user.role.name)


@router.post(
    "/register",
    summary="User Registration method.",
    description="Must provide all required fields. Automatically login if success.",
    tags=["Auth"],
    response_model=SuccessfulAuth,
)
async def register_user(body: UserRegistration, auth_service=Depends(get_auth_service)) -> SuccessfulAuth:
    response = await auth_service.register(body)
    if not response:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="email and username must be unique.",
        )
    return response


@router.post("/token", summary="Get user token.", tags=["Auth"], response_model=SuccessfulAuth)
async def token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: AbstractAuthService = Depends(get_auth_service),
) -> SuccessfulAuth:
    response = await auth_service.login_by_credentials(email=form_data.username, password=form_data.password)
    if not response:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Provided data was incorrect, try again.",
        )
    return response


@router.post(
    "/login",
    summary="User Login method.",
    description="Must provide all required fields.",
    tags=["Auth"],
    response_model=SuccessfulAuth,
)
async def login_user(body: UserLogin, auth_service: AbstractAuthService = Depends(get_auth_service)) -> SuccessfulAuth:
    response = await auth_service.login(body)
    if not response:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Provided data was incorrect, try again.",
        )
    return response


@router.post(
    "/logout",
    summary="User Logout method.",
    description="Must provide Bearear header",
    tags=["Auth"],
    response_model=SuccessfulLogout,
)
async def logout_user(
    access_token: str = Depends(token_persistence_validation),
    auth_service: AbstractAuthService = Depends(get_auth_service),
):
    response = await auth_service.logout(access_token)
    if not response:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid access token, try again.",
        )
    return {"detail": "Successfully logged out."}


@router.post(
    "/refresh",
    summary="Refresh jwt tokens.",
    description="Refresh token is expected, once it will be used it will expire.",
    tags=["Auth"],
    response_model=SuccessfulAuth,
)
async def refresh_tokens(
    refresh_token: str = Depends(token_persistence_validation),
    auth_service: AbstractAuthService = Depends(get_auth_service),
) -> SuccessfulAuth:
    response = await auth_service.refresh(refresh_token)
    if not response:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or expired refresh token.",
        )
    return response


@router.get(
    "/login-history",
    summary="Get login history.",
    description="Shows last login time of unique by fingerprint devices.",
    tags=["Auth"],
    response_model=UserLoginHistory,
)
async def get_login_history(
    access_token: str = Depends(token_persistence_validation),
    auth_service=Depends(get_auth_service),
):
    response = await auth_service.get_login_history(access_token)
    if not response:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid access token.")
    return response


@router.patch(
    "/update",
    summary="Update user information.",
    description="Allows to update username (if new is unique) and password (if old one is correct).",
    tags=["Auth"],
)
async def update_user_information(
    user_update: UserUpdate,
    access_token: str = Depends(token_persistence_validation),
    auth_service=Depends(get_auth_service),
):
    await auth_service.update_user(access_token, user_update)
    return {"detail": "User information updated successfully"}

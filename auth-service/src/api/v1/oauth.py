from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Request
from schemas.entity import SuccessfulAuth
from services.auth import AuthServiceImpl, get_auth_service
from services.oauth import get_oauth_provider
from services.oauth_providers.base import OAuthBase
from typing_extensions import Annotated

router = APIRouter()


@router.post(
    "/login/{provider_name}",
    summary="Ger redirect url for login",
    tags=["Auth"],
)
async def provider_login(provider: Annotated[OAuthBase, Depends(get_oauth_provider)]):
    if provider:
        return provider.get_auth_url()
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Provider not found")


@router.get(
    "/redirect/{provider_name}",
    response_model=SuccessfulAuth,
    status_code=HTTPStatus.ACCEPTED,
    summary="Login using providers",
    tags=["Auth"],
)
async def yandex_login_redirect(
    code: str,
    request: Request,
    provider: Annotated[OAuthBase, Depends(get_oauth_provider)],
    auth_service: AuthServiceImpl = Depends(get_auth_service),
):
    user_agent = request.headers.get("User-Agent")
    tokens = await auth_service.login_by_provider(code=code, provider=provider, user_agent=user_agent)
    return tokens

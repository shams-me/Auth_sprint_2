from functools import lru_cache

from db.postgres import get_postgres_session
from fastapi import Depends, HTTPException
from services.oauth_providers.base import OAuthProviders
from services.oauth_providers.yandex import YandexProvider
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status


@lru_cache()
def get_oauth_provider(provider_name: str, session: AsyncSession = Depends(get_postgres_session)):
    if provider_name == OAuthProviders.yandex.value:
        return YandexProvider(session)

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found")

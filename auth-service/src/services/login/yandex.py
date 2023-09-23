import uuid
from functools import lru_cache

from core.config import settings
from db.postgres import get_postgres_session
from fastapi import Depends
from models.entity import SocialAccount, User
from pylibs.yandexid import YandexID, YandexOAuth
from pylibs.yandexid.schemas.yandexid import User as YandexUser
from services.login.base import OAuthLogin
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from yandex_oauth import yao


class YandexProvider(OAuthLogin):
    def __init__(self, postgres_session: AsyncSession = None) -> None:
        super(YandexProvider, self).__init__("yandex")
        self.yandex_oauth = YandexOAuth(
            client_id=settings.YANDEX_CLIENT_ID,
            client_secret=settings.YANDEX_CLIENT_SECRET,
            redirect_uri=settings.YANDEX_REDIRECT_URI,
        )
        self.session = postgres_session

    def get_auth_url(self) -> str:
        return self.yandex_oauth.get_authorization_url()

    async def register(self, code: str):
        token = yao.get_token_by_code(code, settings.YANDEX_CLIENT_ID, settings.YANDEX_CLIENT_SECRET)
        social_user = YandexID(token.get("access_token"))
        user_data: YandexUser = social_user.get_user_info_json()

        stmt = select(SocialAccount).where(
            SocialAccount.social_id == user_data.psuid,
            SocialAccount.social_name == "yandex",
        )

        account = await self.session.scalar(stmt)
        if account:
            return account

        user = await self.session.scalar(select(User).where(User.email == user_data.default_email))

        if user is None:
            user = User(
                username="_".join([user_data.first_name, user_data.last_name]),
                email=user_data.default_email,
                password=uuid.uuid4().__str__(),
            )
            self.session.add(user)
            await self.session.commit()

        # save data in social accounts
        social_account = SocialAccount(user=user, social_id=user_data.psuid, social_name="yandex")

        self.session.add(social_account)
        return user.id, user.email


@lru_cache()
def yandex_provider(
    session: AsyncSession = Depends(get_postgres_session),
) -> YandexProvider:
    return YandexProvider(
        postgres_session=session,
    )

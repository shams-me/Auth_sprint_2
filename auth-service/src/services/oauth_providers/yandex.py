import uuid

from core.config import settings
from models.entity import SocialAccount, User
from pylibs.yandexid import YandexID, YandexOAuth
from pylibs.yandexid.schemas.yandexid import User as YandexUser
from services.oauth_providers.base import OAuthBase, OAuthProviders
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from yandex_oauth import yao


class YandexProvider(OAuthBase):
    provider_name = OAuthProviders.yandex.value

    def __init__(self, postgres_session: AsyncSession = None) -> None:
        self.yandex_oauth = YandexOAuth(
            client_id=settings.YANDEX_CLIENT_ID,
            client_secret=settings.YANDEX_CLIENT_SECRET,
            redirect_uri=settings.YANDEX_REDIRECT_URI,
        )
        self.session = postgres_session

    def get_auth_url(self) -> str:
        return self.yandex_oauth.get_authorization_url()

    async def register(self, code: str) -> User:
        token = yao.get_token_by_code(code, settings.YANDEX_CLIENT_ID, settings.YANDEX_CLIENT_SECRET)
        social_user = YandexID(token.get("access_token"))
        user_data: YandexUser = social_user.get_user_info_json()

        stmt = select(SocialAccount).where(
            SocialAccount.social_id == user_data.psuid,
            SocialAccount.social_name == self.provider_name,
        )

        account = await self.session.scalar(stmt)
        if account:
            return account.user

        user = await self.session.scalar(select(User).where(User.email == user_data.default_email))

        if user is None:
            user = User(
                username="_".join([user_data.first_name, user_data.last_name]),
                email=user_data.default_email,
                password=uuid.uuid4().__str__(),
            )
            self.session.add(user)
            await self.session.commit()

        social_account = SocialAccount(user_id=user.id, social_id=user_data.psuid, social_name=self.provider_name)

        self.session.add(social_account)
        return user

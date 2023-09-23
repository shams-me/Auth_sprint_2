from abc import ABC, abstractmethod
from datetime import datetime
from http import HTTPStatus
from uuid import UUID

from core.config import settings
from core.token_encoder import JWTEncoder
from core.token_handler import ITokenHandler, JWTHandler
from db.postgres import get_postgres_session
from db.redis import get_redis
from fastapi import Depends, HTTPException, status
from models.entity import Device, RefreshToken, User
from redis.asyncio import Redis
from schemas.entity import (
    DeviceFingerprint,
    SuccessfulAuth,
    UserLogin,
    UserLoginHistory,
    UserRegistration,
    UserUpdate,
)
from services.login.yandex import YandexProvider
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from werkzeug.security import generate_password_hash


class AbstractAuthService(ABC):
    def __init__(self, session: AsyncSession, token_handler: ITokenHandler, redis: Redis):
        self.session = session
        self.token_handler = token_handler
        self.redis = redis

    @abstractmethod
    async def register(self, user: UserRegistration):
        raise NotImplementedError

    @abstractmethod
    async def login_by_credentials(self, email: str, password: str):
        raise NotImplementedError

    @abstractmethod
    async def login(self, user: UserLogin):
        raise NotImplementedError

    @abstractmethod
    async def logout(self, access_token: str):
        raise NotImplementedError

    @abstractmethod
    async def refresh(self, refresh_token):
        raise NotImplementedError

    @abstractmethod
    def get_login_history(self, access_token):
        raise NotImplementedError

    @abstractmethod
    def update_user(self, access_token: str, user: UserUpdate):
        raise NotImplementedError

    @abstractmethod
    def get_user(self, user_id: UUID | str):
        raise NotImplementedError


class AuthServiceImpl(AbstractAuthService):
    async def get_user(self, user_id: UUID | str):
        stmt = select(User).where(User.id == user_id)
        user: User = await self.session.scalar(stmt)
        return user

    async def register(self, user: UserRegistration):
        try:
            new_user = User(email=user.email, password=user.password, username=user.username)
            self.session.add(new_user)
            await self.session.flush()

            device = user.device_fingerprint
            new_device = Device(
                user_agent=device.user_agent,
                timezone=device.timezone,
                screen_width=device.screen_width,
                screen_height=device.screen_height,
                user_id=new_user.id,
            )
            self.session.add(new_device)

            access, refresh = self.token_handler.get_access_refresh_pair(user=new_user)
            new_refresh = RefreshToken(token=refresh, user_id=str(new_user.id))
            self.session.add(new_refresh)

            await self.session.commit()

            return SuccessfulAuth(access_token=access, refresh_token=refresh)
        except IntegrityError:
            await self.session.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already in use.")

    async def login(self, user_in: UserLogin):
        device_fingerprint = user_in.device_fingerprint
        password = user_in.password

        stmt = select(User).where(User.email == user_in.email)
        user: User = await self.session.scalar(stmt)

        if user is None or not user.is_password_valid(password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid information is providen.",
            )
        try:
            access, refresh = self.token_handler.get_access_refresh_pair(user)

            new_refresh = RefreshToken(token=refresh, user_id=user.id)
            self.session.add(new_refresh)

            stmt = insert(Device).values(
                user_agent=device_fingerprint.user_agent,
                timezone=device_fingerprint.timezone,
                screen_width=device_fingerprint.screen_width,
                screen_height=device_fingerprint.screen_height,
                user_id=user.id,
                last_login=datetime.utcnow(),
            )
            stmt = stmt.on_conflict_do_update(constraint="uq_device_details", set_={"last_login": datetime.utcnow()})
            await self.session.execute(stmt)

            await self.session.commit()

            return SuccessfulAuth(access_token=access, refresh_token=refresh)
        except IntegrityError:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Server error.",
            )

    async def login_by_credentials(self, email: str, password: str):
        stmt = select(User).where(User.email == email)
        user: User = await self.session.scalar(stmt)

        if user is None or not user.is_password_valid(password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid information is providen.",
            )
        try:
            access, refresh = self.token_handler.get_access_refresh_pair(user)

            new_refresh = RefreshToken(token=refresh, user_id=user.id)
            self.session.add(new_refresh)
            await self.session.commit()

            return SuccessfulAuth(access_token=access, refresh_token=refresh)
        except IntegrityError:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Server error.",
            )

    async def login_by_yandex(self, code: str, provider: YandexProvider, user_agent: str):
        result = await provider.register(code)
        if result is None:
            return HTTPStatus.BAD_REQUEST

        user_id, email = result[0], result[1]

        stmt = select(User).where(User.email == email)
        user: User = await self.session.scalar(stmt)

        try:
            access, refresh = self.token_handler.get_access_refresh_pair(user)

            new_refresh = RefreshToken(token=refresh, user_id=user.id)
            self.session.add(new_refresh)

            stmt = insert(Device).values(user_agent=user_agent, user_id=user.id, last_login=datetime.utcnow())
            stmt = stmt.on_conflict_do_update(constraint="uq_device_details", set_={"last_login": datetime.utcnow()})
            await self.session.execute(stmt)

            await self.session.commit()

            return SuccessfulAuth(access_token=access, refresh_token=refresh)
        except IntegrityError:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Server error.",
            )

    async def logout(self, access_token: str):
        access_decoded = self.token_handler.decode(access_token)
        time_left = self.token_handler.get_seconds_till_expiration(access_decoded)
        if access_decoded and time_left > 0:
            return await self.redis.set(access_decoded["user_id"], access_token, ex=time_left)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token.")

    async def refresh(self, refresh_token: str):
        refresh_token_decoded = self.token_handler.decode(refresh_token)
        user_id = refresh_token_decoded.get("user_id")

        stmt = select(RefreshToken).where(RefreshToken.user_id == user_id)
        refresh = await self.session.scalar(stmt)

        if refresh and refresh.token == refresh_token:
            new_access, new_refresh = self.token_handler.get_access_refresh_pair(user=refresh.user)
            new_refresh_entity = RefreshToken(token=new_refresh, user_id=user_id)
            self.session.add(new_refresh_entity)
            await self.session.commit()
            return SuccessfulAuth(access_token=new_access, refresh_token=new_refresh)

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token.")

    async def check_redis(self, access_token):
        access_token_decoded = self.token_handler.decode(access_token)
        user_id = access_token_decoded.get("user_id")
        old_access = await self.redis.get(user_id)
        if old_access and old_access.decode("utf-8") == access_token:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token.")
        return user_id

    async def get_login_history(self, access_token):
        user_id = await self.check_redis(access_token)
        stmt = select(Device).where(Device.user_id == user_id).order_by(Device.last_login.desc())
        last_devices_login = (await self.session.scalars(stmt)).all()

        historical_points = [
            DeviceFingerprint(
                user_agent=device.user_agent,
                screen_width=device.screen_width,
                screen_height=device.screen_height,
                timezone=device.timezone,
            )
            for device in last_devices_login
        ]

        return UserLoginHistory(historical_points=historical_points)

    async def update_user(self, access_token: str, user: UserUpdate):
        user_id = await self.check_redis(access_token)

        user_entity = await self.get_user(user_id)

        if user.old_password and not user_entity.is_password_valid(user.old_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Old password is incorrect.",
            )

        if user.username is not None:
            user_entity.username = user.username

        if user.new_password is not None:
            user_entity.password = generate_password_hash(user.new_password)

        self.session.add(user_entity)
        await self.session.commit()


def get_auth_service(
    db: AsyncSession = Depends(get_postgres_session), redis: Redis = Depends(get_redis)
) -> AbstractAuthService:
    token_encoder = JWTEncoder(secret=settings.jwt_secret)
    token_handler = JWTHandler(encoder=token_encoder)
    return AuthServiceImpl(session=db, token_handler=token_handler, redis=redis)

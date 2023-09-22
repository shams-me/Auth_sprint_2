from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from enum import Enum

from fastapi import HTTPException, status

from core.token_encoder import ITokenEncoder
from models.entity import User


class TokenMinutesLifetime(Enum):
    ACCESS = 15
    REFRESH = 60 * 24 * 10


class ITokenHandler(ABC):

    def __init__(self, encoder: ITokenEncoder):
        self.encoder = encoder

    @abstractmethod
    def encode(self, user: dict, duration: int):
        raise NotImplementedError

    @abstractmethod
    def decode(self, token: str):
        raise NotImplementedError

    @abstractmethod
    def get_access_refresh_pair(self, user: User):
        raise NotImplementedError

    @staticmethod
    def get_seconds_till_expiration(decoded: dict):
        return decoded.get('exp') - round(datetime.utcnow().timestamp())

    @staticmethod
    def _enhance_payload_with_time(user: dict, duration: TokenMinutesLifetime) -> dict:
        current_time = datetime.now(timezone.utc)
        expiration_time = current_time + timedelta(minutes=duration.value)
        user['iat'] = int(current_time.timestamp())
        user['exp'] = int(expiration_time.timestamp())
        return user

    @staticmethod
    def _is_active(payload: dict) -> bool:
        current_time = int(datetime.now(timezone.utc).timestamp())
        expiration_time = payload.get('exp')
        return expiration_time > current_time


class JWTHandler(ITokenHandler):

    def get_access_refresh_pair(self, user: User) -> tuple[str, str]:
        access_token = self.encode({'user_id': str(user.id), 'email': user.email}, TokenMinutesLifetime.ACCESS)
        refresh_token = self.encode({'user_id': str(user.id)}, TokenMinutesLifetime.REFRESH)
        return access_token, refresh_token

    def encode(self, user: dict, duration: TokenMinutesLifetime) -> str:
        payload = self._enhance_payload_with_time(user, duration)
        return self.encoder.encode(payload=payload)

    def decode(self, token: str) -> dict:
        payload = self.encoder.decode(token)
        if self._is_active(payload):
            return payload
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Expired token.")

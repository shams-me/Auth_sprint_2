from abc import ABC, abstractmethod

from models.entity import User


class OAuthBase(ABC):
    @abstractmethod
    def get_auth_url(self) -> str:
        raise NotImplementedError

    @abstractmethod
    async def register(self, code: str) -> User:
        raise NotImplementedError

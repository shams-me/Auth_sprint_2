from functools import lru_cache
from uuid import UUID

from fastapi import Depends
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_postgres_session
from models.entity import User


class UserRoleService:
    session: AsyncSession

    def __init__(self, session: AsyncSession):
        self.session = session

    async def assign_role(self, user_id: UUID, role_id: UUID) -> None:
        """Assign a role to user
        :param user_id: User ID
        :param role_id: Role ID
        :return: None
        """

        stmt = update(User).where(user_id=user_id).values(role_id=role_id)
        await self.session.execute(stmt)
        await self.session.commit()


@lru_cache()
def get_user_role_service(session: AsyncSession = Depends(get_postgres_session)) -> UserRoleService:
    return UserRoleService(session=session)

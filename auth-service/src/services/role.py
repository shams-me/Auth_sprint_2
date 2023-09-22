from functools import lru_cache
from uuid import UUID

from fastapi import Depends
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_postgres_session
from models.role import Role, Permission, RolePermission
from services.crud import CRUDBase


class RoleService(CRUDBase):
    session: AsyncSession

    def __init__(self, session: AsyncSession):
        super().__init__(Role, session)
        self.session = session

    async def create_permission(self, role_id: UUID, name: str) -> Permission:
        """Create a new permission
        :param role_id: Role ID
        :param name: Permission name
        :return: Permission
        """
        permission = Permission(name=name)
        self.session.add(permission)
        await self.session.commit()

        assign_permission = RolePermission(role_id=role_id, permission_id=permission.id)
        self.session.add(assign_permission)
        await self.session.commit()
        return permission

    async def assign_permission(self, role_id: UUID, permission_id: UUID) -> None:
        """Assign a permission to a role
        :param role_id: Role ID
        :param permission_id: Permission ID
        :return: None
        """
        assign_permission = RolePermission(role_id=role_id, permission_id=permission_id)
        self.session.add(assign_permission)
        await self.session.commit()

    async def revoke_permission(self, role_id: UUID, permission_id: UUID) -> None:
        """Revoke a permission from a role
        :param role_id: Role ID
        :param permission_id: Permission ID
        :return: None
        """
        stmt = delete(RolePermission).where(
            RolePermission.role_id == role_id and RolePermission.permission_id == permission_id
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def get_permissions(self, skip: int = 0, limit: int = 100) -> list[Permission]:
        """Get all permissions
        :param skip: Skip
        :param limit: Limit
        :return: List of permissions
        """
        stmt = select(Permission).offset((skip - 1) * limit).limit(limit)
        return (await self.session.scalars(stmt)).all()


@lru_cache()
def get_role_service(session: AsyncSession = Depends(get_postgres_session)) -> RoleService:
    return RoleService(session=session)

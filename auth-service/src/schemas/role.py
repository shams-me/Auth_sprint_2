import enum
from uuid import UUID

from pydantic import BaseModel


class RoleOptions(str, enum.Enum):
    SUPERUSER = "superuser"
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"


class PermissionOptions(str, enum.Enum):
    ALL = "all"
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"


class PermissionIn(BaseModel):
    name: str


class PermissionOut(BaseModel):
    id: UUID
    name: str


class RoleIn(BaseModel):
    name: str


class RolePermissionOut(BaseModel):
    id: UUID
    role_id: UUID
    permission_id: UUID


class RoleOut(BaseModel):
    id: UUID
    name: str
    permissions: list[PermissionOut]

    class Config:
        from_attributes = True


class RolePermissionIn(BaseModel):
    role_id: UUID
    permission_id: UUID

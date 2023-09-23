import enum
import uuid
from typing import Optional

from sqlalchemy import (
    UUID,
    String,
    ForeignKey,
    Enum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class RoleEnum(enum.Enum):
    SUPERUSER = "superuser"
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"


class PermissionEnum(enum.Enum):
    ALL = "all"
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"


class Role(Base, TimestampMixin):
    """
    This class represents a Role in the application.

    Attributes:
        id (Mapped[UUID]): The unique identifier of the role.
        name (Mapped[Optional[str]]): The name of the role.

    Methods:
        __repr__(): Returns a string representation of the Role object.

    """

    __tablename__ = "roles"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[Optional[str]] = mapped_column(String(1024), Enum(RoleEnum), unique=True)
    permissions: Mapped[list["Permission"]] = relationship(
        "Permission", secondary="role_permissions", uselist=True, lazy="selectin"
    )

    def __repr__(self):
        return f"<Role {self.name}>"


class Permission(Base, TimestampMixin):
    """
    This class represents a Permission of role the application.

    Attributes:
        id (Mapped[UUID]): The unique identifier of the permission.
        name (Mapped[Optional[str]]): The name of the permission.

    Methods:
        __repr__(): Returns a string representation of the Role object.

    """
    __tablename__ = "permissions"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[Optional[str]] = mapped_column(String(1024), Enum(PermissionEnum))

    def __repr__(self):
        return f"<Permission {self.name}>"


class RolePermission(Base, TimestampMixin):
    """
    This class represents the relationship between a Role and a Permission.

    Attributes:
        id (Mapped[UUID]): The unique identifier of the role-permission relationship.
        role_id (Mapped[UUID]): The unique identifier of the role.
        permission_id (Mapped[UUID]): The unique identifier of the permission.

    Methods:
        __repr__(): Returns a string representation of the RolePermission object.

    """
    __tablename__ = "role_permissions"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_id: Mapped[UUID] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"))
    permission_id: Mapped[UUID] = mapped_column(ForeignKey("permissions.id", ondelete="CASCADE"))

    def __repr__(self):
        return f"<RolePermission {self.id}>"

import enum

from pydantic import BaseModel


class Roles(str, enum.Enum):
    SUPERUSER = "superuser"
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"


class Permissions(str, enum.Enum):
    ALL = "all"
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"


class User(BaseModel):
    user_id: str
    role: str
    email: str

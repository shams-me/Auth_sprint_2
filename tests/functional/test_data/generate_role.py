import enum


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

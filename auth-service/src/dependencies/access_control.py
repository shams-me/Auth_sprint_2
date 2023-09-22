from fastapi import Depends, HTTPException
from starlette import status

from dependencies.current_user import get_current_user
from models.entity import User
from schemas.role import PermissionOptions, RoleOptions


def access_control(roles: list[RoleOptions | None] = RoleOptions.SUPERUSER,
                   permissions: list[PermissionOptions | None] = PermissionOptions.ALL,
                   user: User = Depends(get_current_user)) -> bool:
    user_role = user.role
    user_permission = user_role.permissions

    if user_role.name == RoleOptions.SUPERUSER:
        return True

    if user_role.name in roles:
        if any(permission in user_permission for permission in permissions):
            return True

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have enough permissions")


def access_moderator(user: User = Depends(get_current_user)) -> bool:
    if user_role := user.role:
        if user_role.name in [RoleOptions.SUPERUSER, RoleOptions.MODERATOR]:
            return True

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have enough permissions")


def access_super_user(user: User = Depends(get_current_user)) -> bool:
    if user_role := user.role:
        if user_role.name == RoleOptions.SUPERUSER:
            return True

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have enough permissions")

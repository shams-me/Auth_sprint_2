from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.params import Query

from dependencies.access_control import access_super_user
from services.user_role import get_user_role_service, UserRoleService

router = APIRouter()


@router.post("/assign/{user_id}", summary="Assign a role to user", tags=["User roles"])
async def assign_user_role(
    user_id: UUID,
    role_id: UUID = Query(),
    model_service: UserRoleService = Depends(get_user_role_service),
    is_superuser: bool = Depends(access_super_user)
):
    return await model_service.assign_role(role_id=role_id, user_id=user_id)


@router.post("/revoke/{user_id}", summary="Revoke a role to user", tags=["User roles"])
async def revoke_user_role(
    user_id: UUID,
    role_id: UUID = Query(),
    model_service: UserRoleService = Depends(get_user_role_service),
    is_superuser: bool = Depends(access_super_user)
):
    return await model_service.assign_role(role_id=role_id, user_id=user_id)

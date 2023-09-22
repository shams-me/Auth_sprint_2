from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from dependencies.access_control import access_super_user, access_moderator
from schemas.role import RoleOut, RoleIn, RolePermissionIn, PermissionOptions, RoleOptions
from services.role import get_role_service, RoleService

router = APIRouter()


@router.post("", summary="Create a new role", response_model=RoleOut, tags=["CRUD roles"])
async def create_role(
    name: RoleOptions = Query(...),
    model_service: RoleService = Depends(get_role_service),
    is_superuser: bool = Depends(access_super_user)
) -> List[RoleOut]:
    return await model_service.create({"name": name})


@router.get("", summary="Get all roles", response_model=list[RoleOut], tags=["CRUD roles"])
async def get_roles(
    page_size: int = Query(50, ge=1, le=100, description="Number of roles per page"),
    page_number: int = Query(1, ge=1, description="Page number"),
    model_service: RoleService = Depends(get_role_service),
    user_allowed: bool = Depends(access_moderator)
) -> List[RoleOut]:
    count, roles = await model_service.get_multi(skip=(page_number - 1) * page_size, limit=page_size)
    return roles


@router.delete("/{role_id}", summary="Delete a role by ID", tags=["CRUD roles"])
async def delete_roles(
    role_id: UUID,
    model_service: RoleService = Depends(get_role_service),
    is_superuser: bool = Depends(access_super_user)
):
    return await model_service.delete(model_id=role_id)


@router.put("/{role_id}", summary="Update a role by ID", tags=["CRUD roles"])
async def update_roles(
    role_id: UUID,
    data: RoleIn = Depends(RoleIn),
    model_service: RoleService = Depends(get_role_service),
    is_superuser: bool = Depends(access_super_user)
):
    return await model_service.update(model_id=role_id, data=data)


@router.post("/{role_id}/permissions", summary="Assign a permission to a role", tags=["Work with permissions"])
async def assign_permission_to_role(
    role_id: UUID,
    permission: PermissionOptions = Query(...),
    model_service: RoleService = Depends(get_role_service),
    is_superuser: bool = Depends(access_super_user)
):
    return await model_service.create_permission(role_id=role_id, name=permission)


@router.post("/role-permissions", summary="Assign a permission to a role", tags=["Work with permissions"])
async def assign_permission_to_role_by_id(
    data: RolePermissionIn = Depends(),
    model_service: RoleService = Depends(get_role_service),
    is_superuser: bool = Depends(access_super_user)
):
    return await model_service.assign_permission(**data.model_dump())


@router.delete(
    "/role-permissions",
    summary="Revoke a permission from a role by role_id and permission_id",
    tags=["Work with permissions"]
)
async def revoke_assign_permission_to_role_by_id(
    data: RolePermissionIn = Depends(),
    model_service: RoleService = Depends(get_role_service),
    is_superuser: bool = Depends(access_super_user)
):
    return await model_service.revoke_permission(**data.model_dump())


@router.get("/permissions", summary="Get all permissions", tags=["Work with permissions"])
async def get_all_permissions(
    page_size: int = Query(50, ge=1, le=100, description="Number of roles per page"),
    page_number: int = Query(1, ge=1, description="Page number"),
    model_service: RoleService = Depends(get_role_service),
    user_allowed: bool = Depends(access_moderator)
):
    return await model_service.get_permissions(skip=page_number, limit=page_size)

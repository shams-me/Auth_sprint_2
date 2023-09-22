REGISTER_ENDPOINT = "/api/v1/auth/register"
LOGIN_ENDPOINT = "/api/v1/auth/login"
LOGOUT_ENDPOINT = "/api/v1/auth/logout"
REFRESH_ENDPOINT = "/api/v1/auth/refresh"
LOGIN_HISTORY_ENDPOINT = "/api/v1/auth/login-history"
USER_UPDATE_ENDPOINT = "/api/v1/auth/update"

ROLE_ENDPOINT = "/api/v1/roles"
DELETE_ROLE_ENDPOINT = "/api/v1/roles/{role_id}"
UPDATE_ROLE_ENDPOINT = "/api/v1/roles/{role_id}"

PERMISSION_ENDPOINT = "/api/v1/roles/permissions"
CREATE_PERMISSION_AND_ASSIGN = "/api/v1/roles/{role_id}/permissions"
ASSIGN_PERMISSION_ENDPOINT = "/api/v1/roles/role-permissions"
REVOKE_PERMISSION_ENDPOINT = "/api/v1/roles/role-permissions"

ASSIGN_ROLE_TO_USER_ENDPOINT = "/api/v1/user_roles/assign/{user_id}"
REVOKE_ROLE_TO_USER_ENDPOINT = "/api/v1/user_roles/revoke/{user_id}"

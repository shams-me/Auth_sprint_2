from http import HTTPStatus

import pytest

from tests.functional.test_data.generate_role import RoleEnum
from tests.functional.utils.endpoints import ROLE_ENDPOINT


@pytest.mark.parametrize(
    "name, expected_status",
    [
        (RoleEnum.MODERATOR.value, HTTPStatus.FORBIDDEN),
        (RoleEnum.USER.value, HTTPStatus.FORBIDDEN),
    ],
)
async def test_create_role_as_user(make_post_request, name, expected_status, tokens):
    access_token, _ = tokens
    role = {"name": name}
    status, body = await make_post_request(ROLE_ENDPOINT, params=role, jwt_token=access_token)

    assert status == expected_status


@pytest.mark.parametrize(
    "name, expected_status",
    [(RoleEnum.MODERATOR.value, HTTPStatus.OK), (RoleEnum.USER.value, HTTPStatus.OK)],
)
async def test_create_role_as_super_user(make_post_request, name, expected_status, super_user_tokens):
    access_token, _ = super_user_tokens
    role = {"name": name}
    status, body = await make_post_request(ROLE_ENDPOINT, params=role, jwt_token=access_token)

    assert status == expected_status


async def test_get_roles(make_get_request, super_user_tokens):
    access_token, _ = super_user_tokens
    status, body = await make_get_request(ROLE_ENDPOINT, jwt_token=access_token)

    assert status == HTTPStatus.OK

from asyncio import sleep
from http import HTTPStatus

import pytest

from tests.functional.test_data.generate_user import (
    generate_user_login_body,
    generate_user_registration_body,
)
from tests.functional.utils.endpoints import (
    LOGIN_ENDPOINT,
    LOGIN_HISTORY_ENDPOINT,
    LOGOUT_ENDPOINT,
    REFRESH_ENDPOINT,
    REGISTER_ENDPOINT,
    USER_UPDATE_ENDPOINT,
)
from tests.functional.utils.user_fields import DEFAULT_USER_PASSWORD, INITIAL_USER_EMAIL


@pytest.mark.parametrize(
    "email, expected_status",
    [
        (INITIAL_USER_EMAIL, [HTTPStatus.CONFLICT, HTTPStatus.OK]),
        ("new_user_email1@example.com", [HTTPStatus.CONFLICT, HTTPStatus.OK]),
        (INITIAL_USER_EMAIL, [HTTPStatus.CONFLICT]),
    ],
)
async def test_register_new_user(make_post_request, email, expected_status):
    new_user_data = generate_user_registration_body(email)
    status, body = await make_post_request(REGISTER_ENDPOINT, new_user_data)

    assert status in expected_status


async def test_register_new_user_empty_body_error(make_post_request):
    empty_body = {}
    status, body = await make_post_request(REGISTER_ENDPOINT, empty_body)

    assert status == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.parametrize(
    "email, expected_status",
    [
        (INITIAL_USER_EMAIL, HTTPStatus.OK),
        ("random_user@example.com", HTTPStatus.BAD_REQUEST),
    ],
)
async def test_login_successful(make_post_request, email, expected_status):
    login_data = generate_user_login_body(email)
    status, body = await make_post_request(LOGIN_ENDPOINT, login_data)
    assert status == expected_status


async def test_logout_token_valid(make_post_request, fresh_jwt):
    access_token, refresh_token = fresh_jwt
    status, body = await make_post_request(LOGOUT_ENDPOINT, jwt_token=access_token)
    assert status == HTTPStatus.OK


async def test_logout_token_invalid(make_post_request, invalid_access_jwt_token):
    status, body = await make_post_request(LOGOUT_ENDPOINT, jwt_token=invalid_access_jwt_token)
    assert status == HTTPStatus.BAD_REQUEST


async def test_logout_token_expired(make_post_request, expired_access_jwt_token):
    status, body = await make_post_request(LOGOUT_ENDPOINT, jwt_token=expired_access_jwt_token)
    assert status == HTTPStatus.BAD_REQUEST


async def test_refresh_token_expired(make_post_request, expired_refresh_jwt_token):
    status, body = await make_post_request(REFRESH_ENDPOINT, jwt_token=expired_refresh_jwt_token)
    assert status == HTTPStatus.BAD_REQUEST


async def test_refresh_token_invalid(make_post_request, invalid_refresh_jwt_token):
    status, body = await make_post_request(REFRESH_ENDPOINT, jwt_token=invalid_refresh_jwt_token)
    assert status == HTTPStatus.BAD_REQUEST


async def test_login_history_token_valid(make_get_request, valid_access_jwt_token):
    status, body = await make_get_request(LOGIN_HISTORY_ENDPOINT, jwt_token=valid_access_jwt_token)
    assert status == HTTPStatus.OK


async def test_login_history_token_invalid(make_get_request, invalid_access_jwt_token):
    status, body = await make_get_request(LOGIN_HISTORY_ENDPOINT, jwt_token=invalid_access_jwt_token)
    assert status == HTTPStatus.BAD_REQUEST


async def test_login_history_token_expired(make_get_request, expired_access_jwt_token):
    status, body = await make_get_request(LOGIN_HISTORY_ENDPOINT, jwt_token=expired_access_jwt_token)
    assert status == HTTPStatus.BAD_REQUEST


@pytest.mark.parametrize(
    "user_data, expected_status",
    [
        (
            {
                "username": "new_username",
                "old_password": "",
                "new_password": "",
                "new_password_confirmation": "",
            },
            HTTPStatus.OK,
        ),  # noqa: E121
        (
            {
                "username": "",
                "old_password": DEFAULT_USER_PASSWORD,
                "new_password": "new_password",
                "new_password_confirmation": "new_password",
            },
            HTTPStatus.OK,
        ),  # noqa: E121
        (
            {
                "username": "updated_username",
                "old_password": DEFAULT_USER_PASSWORD,
                "new_password": "new_password",
                "new_password_confirmation": "new_password",
            },
            HTTPStatus.OK,
        ),  # noqa: E121
        (
            {
                "username": "",
                "old_password": DEFAULT_USER_PASSWORD,
                "new_password": "new_pass",
                "new_password_confirmation": "new_password",
            },
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ),  # noqa: E121
        (
            {
                "username": "",
                "old_password": "string",
                "new_password": "new_pass",
                "new_password_confirmation": "new_pass",
            },
            HTTPStatus.BAD_REQUEST,
        ),  # noqa: E121
    ],
)
async def test_update_user_successful(make_patch_request, fresh_jwt, user_data, expected_status):
    access_token, refresh_token = fresh_jwt
    status, body = await make_patch_request(USER_UPDATE_ENDPOINT, user_data, jwt_token=access_token)
    assert status == expected_status


async def test_update_user_token_invalid(make_patch_request, invalid_access_jwt_token):
    json_data = {
        "username": "updated_username",
        "old_password": DEFAULT_USER_PASSWORD,
        "new_password": "new_password",
        "new_password_confirmation": "new_password",
    }
    status, body = await make_patch_request(USER_UPDATE_ENDPOINT, json_data, jwt_token=invalid_access_jwt_token)
    assert status == HTTPStatus.BAD_REQUEST


async def test_update_user_token_expired(make_patch_request, expired_access_jwt_token):
    json_data = {
        "username": "updated_username",
        "old_password": DEFAULT_USER_PASSWORD,
        "new_password": "new_password",
        "new_password_confirmation": "new_password",
    }
    status, body = await make_patch_request(USER_UPDATE_ENDPOINT, json_data, jwt_token=expired_access_jwt_token)
    assert status == HTTPStatus.BAD_REQUEST


async def test_refresh_token_valid(make_post_request, tokens):
    access_token, refresh_token = tokens
    await sleep(2)
    status, body = await make_post_request(REFRESH_ENDPOINT, jwt_token=refresh_token)
    assert status == HTTPStatus.OK

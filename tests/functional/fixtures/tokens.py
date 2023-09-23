import base64
import json
import uuid

import aiohttp
import pytest
import pytest_asyncio

from tests.functional.settings import test_settings
from tests.functional.test_data.generate_user import (
    generate_user_login_body,
    generate_user_registration_body,
)
from tests.functional.utils.endpoints import LOGIN_ENDPOINT, REGISTER_ENDPOINT


def modify_token_signature(token: str):
    header, payload, signature = token.split(".")
    payload_data = json.loads(base64.b64decode(payload + "=="))
    payload_data["exp"] = 1693606200
    modified_payload = base64.b64encode(json.dumps(payload_data).encode()).decode().rstrip("=")
    modified_token = f"{header}.{modified_payload}.{signature}"
    return modified_token


def modify_token_expiry(token: str):
    header, payload, signature = token.split(".")
    modified_signature = signature[::-1]
    modified_token = f"{header}.{payload}.{modified_signature}"
    return modified_token


async def register_new_user(make_post_request, email):
    new_user_data = generate_user_registration_body(email)
    status, body = await make_post_request(REGISTER_ENDPOINT, new_user_data)
    return status, body


async def login_user(make_post_request, email):
    login_data = generate_user_login_body(email)
    status, body = await make_post_request(LOGIN_ENDPOINT, login_data)
    return status, body


@pytest.fixture
async def fresh_jwt(make_post_request):
    email = "test_user_" + str(uuid.uuid4()) + "@example.com"
    status, body = await register_new_user(make_post_request, email)
    return body["access_token"], body["refresh_token"]


@pytest_asyncio.fixture(scope="session")
async def tokens(aiohttp_client: aiohttp.ClientSession):
    # Logic to obtain valid access and refresh tokens from your service
    email = "test_user_" + str(uuid.uuid4()) + "@example.com"
    json_data = generate_user_registration_body(email)

    headers = {"accept": "application/json", "Content-Type": "application/json"}

    url = test_settings.service_url + REGISTER_ENDPOINT

    async with aiohttp_client.post(url, json=json_data, headers=headers) as response:
        data = await response.json()
        return data["access_token"], data["refresh_token"]


@pytest.fixture(scope="session")
async def super_user_tokens(aiohttp_client: aiohttp.ClientSession):
    json_data = generate_user_login_body(email=test_settings.super_user_mail, password=test_settings.super_user_pass)
    headers = {"accept": "application/json", "Content-Type": "application/json"}

    url = test_settings.service_url + LOGIN_ENDPOINT

    async with aiohttp_client.post(url, json=json_data, headers=headers) as response:
        data = await response.json()

    return data["access_token"], data["refresh_token"]


@pytest.fixture
async def valid_access_jwt_token(tokens):
    return tokens[0]


@pytest.fixture
async def invalid_access_jwt_token(tokens):
    return modify_token_signature(tokens[0])


@pytest.fixture
async def expired_access_jwt_token(tokens):
    return modify_token_expiry(tokens[0])


@pytest.fixture
async def valid_refresh_jwt_token(tokens):
    return tokens[1]


@pytest.fixture
async def invalid_refresh_jwt_token(tokens):
    return modify_token_signature(tokens[1])


@pytest.fixture
async def expired_refresh_jwt_token(tokens):
    return modify_token_expiry(tokens[1])

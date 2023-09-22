import urllib

import aiohttp
import pytest

from tests.functional.settings import test_settings


@pytest.fixture
def make_get_request(aiohttp_client: aiohttp.ClientSession):

    async def _inner(endpoint: str, params: dict = None, jwt_token: str = None):
        url = test_settings.service_url + endpoint

        headers = {}

        if jwt_token:
            headers["Authorization"] = f"Bearer {jwt_token}"

        if params:
            encoded_params = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
            url = f"{url}?{encoded_params}"

        async with aiohttp_client.get(url, headers=headers) as response:
            body = await response.json()
            status = response.status
        return status, body

    return _inner


@pytest.fixture
def make_post_request(aiohttp_client: aiohttp.ClientSession):

    async def _inner(endpoint: str, json_data: dict = None, params: dict = None, jwt_token: str = None):
        url = test_settings.service_url + endpoint

        if params:
            encoded_params = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
            url = f"{url}?{encoded_params}"

        headers = {'accept': 'application/json', 'Content-Type': 'application/json'}
        if jwt_token:
            headers["Authorization"] = f"Bearer {jwt_token}"

        async with aiohttp_client.post(url, json=json_data, headers=headers) as response:
            body = await response.json()
            status = response.status
        return status, body

    return _inner


@pytest.fixture
def make_patch_request(aiohttp_client: aiohttp.ClientSession):

    async def _inner(endpoint: str, json_data: dict = None, jwt_token: str = None):
        url = test_settings.service_url + endpoint

        headers = {'accept': 'application/json', 'Content-Type': 'application/json'}

        if jwt_token:
            headers["Authorization"] = f"Bearer {jwt_token}"

        async with aiohttp_client.patch(url, json=json_data, headers=headers) as response:
            body = await response.json()
            status = response.status
        return status, body

    return _inner


@pytest.fixture
def make_delete_request(aiohttp_client: aiohttp.ClientSession):

    async def _inner(endpoint: str, json_data: dict = None, params: dict = None, jwt_token: str = None):
        url = test_settings.service_url + endpoint

        headers = {'accept': 'application/json', 'Content-Type': 'application/json'}

        if params:
            encoded_params = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
            url = f"{url}?{encoded_params}"

        if jwt_token:
            headers["Authorization"] = f"Bearer {jwt_token}"

        async with aiohttp_client.delete(url, json=json_data, headers=headers) as response:
            body = await response.json()
            status = response.status
        return status, body

    return _inner

import http
import logging

import jwt
import requests
from config.settings import AUTH_SERVICE_HOST, AUTH_SERVICE_PORT
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.core.handlers.wsgi import WSGIRequest
from requests.exceptions import RequestException, Timeout, TooManyRedirects

User = get_user_model()


class CustomBackend(BaseBackend):
    def authenticate(self, request: WSGIRequest, username: str = None, password: str = None):
        django_login_roles = {"superuser", "admin", "manager"}
        url = f"http://{AUTH_SERVICE_HOST}:{AUTH_SERVICE_PORT}/api/v1/auth/login"
        payload = {
            "email": username,
            "password": password,
            "device_fingerprint": {
                "user_agent": request.headers.get("User-Agent"),
                "screen_width": 0,
                "screen_height": 0,
                "timezone": request.headers.get("HTTP_TIMEZONE", "UTC"),
            },
        }

        try:
            response = requests.post(url, json=payload, headers={"X-Request-Id": request.headers.get("X-Request-Id")})
        except (TooManyRedirects, RequestException, Timeout):
            logging.error("Auth service not working!")
            return None

        if response.status_code != http.HTTPStatus.OK:
            return None

        access_token = response.json().get("access_token")

        if access_token is None:
            return None

        data = jwt.decode(access_token, options={"verify_signature": False})
        is_admin = data.get("role") in django_login_roles

        try:
            user, created = User.objects.get_or_create(id=data.get("user_id"))
            user.email = username
            user.verified = True
            user.is_active = True
            user.is_admin = is_admin
            user.save()
        except Exception:
            return None

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

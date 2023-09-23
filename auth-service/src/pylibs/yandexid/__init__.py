# -*- coding: utf-8 -*-
"""Yandex ID API wrapper

This module provides a wrapper for Yandex ID API.
Read more about Yandex ID API at https://yandex.ru/dev/id/doc/dg/api-id

Repository: https://github.com/LulzLoL231/yandexid
"""
from .__meta import __author__, __version__
from .yandexid.async_yandexid import AsyncYandexID
from .yandexid.yandexid import YandexID
from .yandexoauth.async_yandexoauth import AsyncYandexOAuth
from .yandexoauth.yandexoauth import YandexOAuth

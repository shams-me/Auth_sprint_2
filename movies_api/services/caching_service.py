import json
from abc import abstractmethod
from typing import Generic, List, Optional, TypeVar

import orjson
from backoff.backoff import backoff_public_methods
from cache_storage.cache_storage_protocol import CacheStorageProtocol
from core.config import settings
from models.film import Film
from models.genre import Genre
from models.person import Person
from opentelemetry import trace
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


@backoff_public_methods()
class CachingService(Generic[T]):
    def __init__(
        self, cache_storage: CacheStorageProtocol, prefix_plural: str, prefix_single: str, tracer: trace.Tracer
    ):
        self.cache_storage = cache_storage
        self.key_prefix_plural = prefix_plural
        self.key_prefix_single = prefix_single
        self.tracer = tracer

    async def get_instance_from_cache(self, instance_id: str) -> Optional[T]:
        with self.tracer.start_as_current_span("get-cache"):
            cache_key = f"{self.key_prefix_single}_{instance_id}"
            data = await self.cache_storage.get(cache_key)
            if not data:
                return None
            return self._parse_instance_from_data(data)

    async def get_list_from_cache(
        self,
        page_size: int,
        page_number: int,
        search: str | None = None,
        sort: str | None = None,
    ) -> List[T]:
        with self.tracer.start_as_current_span("get-cache"):
            cache_key = f"{self.key_prefix_plural}_{search or ''}_{sort or ''}_{page_size}_{page_number}"
            data = await self.cache_storage.get(cache_key)
            if not data:
                return None
            items = orjson.loads(data)
            return [self._parse_instance_from_data(item) for item in items]

    async def put_instance_to_cache(self, instance: T):
        with self.tracer.start_as_current_span("put-cache"):
            cache_key = f"{self.key_prefix_single}_{instance.id}"
            await self.cache_storage.set(
                cache_key,
                instance.model_dump_json(),
                settings.cache_expire_time,
            )

    async def put_list_to_cache(
        self,
        sort: str,
        page_size: int,
        page_number: int,
        instances: List[T],
        search: str | None = None,
    ):
        with self.tracer.start_as_current_span("put-cache"):
            cache_key = f"{self.key_prefix_plural}_{search or ''}_{sort or ''}_{page_size}_{page_number}"
            instances_json_list = [instance.model_dump_json() for instance in instances]
            instances_json_str = orjson.dumps(instances_json_list)
            await self.cache_storage.set(
                cache_key,
                instances_json_str,
                settings.cache_expire_time,
            )

    @abstractmethod
    def _parse_instance_from_data(self, data: str) -> T:
        raise NotImplementedError


class FilmCachingService(CachingService[Film]):
    def _parse_instance_from_data(self, data: str) -> Film:
        return Film.deserialize_cache(data)


class PersonCachingService(CachingService[Person]):
    def _parse_instance_from_data(self, data: str) -> Person:
        data_dict = json.loads(data)
        return Person.model_validate(data_dict)


class GenreCachingService(CachingService[Genre]):
    def _parse_instance_from_data(self, data: str) -> Genre:
        data_dict = json.loads(data)
        return Genre.model_validate(data_dict)

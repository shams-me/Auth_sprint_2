from functools import lru_cache
from typing import Optional

from cache_storage.cache_storage_protocol import CacheStorageProtocol
from db.elastic import get_elastic
from db.redis import get_redis
from db.tracer import get_tracer
from fastapi import Depends
from models.person import Person
from opentelemetry import trace
from search_engine.search_engine_protocol import SearchEngineProtocol

from .caching_service import PersonCachingService
from .search_service import PersonSearchService
from .searchable_model_service import SearchableModelService


@lru_cache()
def get_person_service(
    redis: CacheStorageProtocol = Depends(get_redis),
    elastic: SearchEngineProtocol = Depends(get_elastic),
    tracer: trace.Tracer = Depends(get_tracer),
) -> SearchableModelService:
    redis = PersonCachingService(cache_storage=redis, prefix_plural="persons", prefix_single="person", tracer=tracer)
    elastic = PersonSearchService(search_engine=elastic, index="persons")
    return SearchableModelService[Person](caching_service=redis, search_service=elastic)

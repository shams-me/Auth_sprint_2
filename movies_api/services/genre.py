from functools import lru_cache

from cache_storage.cache_storage_protocol import CacheStorageProtocol
from db.elastic import get_elastic
from db.redis import get_redis
from db.tracer import get_tracer
from fastapi import Depends
from models.genre import Genre
from opentelemetry import trace
from search_engine.search_engine_protocol import SearchEngineProtocol

from .caching_service import GenreCachingService
from .search_service import GenreSearchService
from .searchable_model_service import SearchableModelService


@lru_cache()
def get_genre_service(
    redis: CacheStorageProtocol = Depends(get_redis),
    elastic: SearchEngineProtocol = Depends(get_elastic),
    tracer: trace.Tracer = Depends(get_tracer),
) -> SearchableModelService:
    redis = GenreCachingService(cache_storage=redis, prefix_single="genre", prefix_plural="genres", tracer=tracer)
    elastic = GenreSearchService(search_engine=elastic, index="genres", tracer=tracer)
    return SearchableModelService[Genre](caching_service=redis, search_service=elastic)

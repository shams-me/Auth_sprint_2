from functools import lru_cache

from cache_storage.cache_storage_protocol import CacheStorageProtocol
from db.elastic import get_elastic
from db.redis import get_redis
from db.tracer import get_tracer
from fastapi import Depends
from models.film import Film
from opentelemetry import trace
from search_engine.search_engine_protocol import SearchEngineProtocol

from .caching_service import FilmCachingService
from .search_service import FilmSearchService
from .searchable_model_service import SearchableModelService


@lru_cache()
def get_film_service(
    redis: CacheStorageProtocol = Depends(get_redis),
    elastic: SearchEngineProtocol = Depends(get_elastic),
    tracer: trace.Tracer = Depends(get_tracer),
) -> SearchableModelService:
    redis = FilmCachingService(cache_storage=redis, prefix_plural="movies", prefix_single="movie", tracer=tracer)
    elastic = FilmSearchService(search_engine=elastic, index="movies", tracer=tracer)
    return SearchableModelService[Film](caching_service=redis, search_service=elastic)

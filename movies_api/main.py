from api.v1 import films, genres, persons
from core.config import settings
from db import elastic, redis
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse
from rate_limit.token_bucket import TokenBucket
from redis.asyncio import Redis

app = FastAPI(
    title=f"Read-only API for {settings.project_name}",
    description="Information about films, genres and people involved in the creation of works",
    version="1.0.0",
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
    # root_path="/movies"
)
token_bucket = TokenBucket(rate=1, capacity=10)


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if not token_bucket.acquire_token():
        raise ORJSONResponse(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too Many Requests")

    response = await call_next(request)
    return response


@app.on_event("startup")
async def startup():
    redis.redis = Redis(
        host=settings.redis_host,
        port=settings.redis_port,
    )
    elastic.es = AsyncElasticsearch(hosts=[settings.elastic_url])


@app.on_event("shutdown")
async def shutdown():
    await redis.redis.close()
    await elastic.es.close()


# Подключаем роутер к серверу, указав префикс /v1/films
app.include_router(
    films.router,
    prefix="/api/v1/films",
)
app.include_router(
    genres.router,
    prefix="/api/v1/genres",
)
app.include_router(
    persons.router,
    prefix="/api/v1/persons",
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)

from api.v1 import films, genres, persons
from core.config import settings
from db import elastic, redis
from db.tracer import get_tracer
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from redis.asyncio import Redis


def configure_tracer() -> None:
    jaeger_exporter = JaegerExporter(agent_host_name="jaeger", agent_port=6831)
    trace.set_tracer_provider(TracerProvider(resource=Resource.create({SERVICE_NAME: "movies-api"})))
    trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(jaeger_exporter))
    # Чтобы видеть трейсы в консоли
    trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))


configure_tracer()
app = FastAPI(
    title=f"Read-only API for {settings.project_name}",
    description="Information about films, genres and people involved in the creation of works",
    version="1.0.0",
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
    root_path="/movies",
)
FastAPIInstrumentor.instrument_app(app)


@app.middleware("http")
async def before_request(request: Request, call_next):
    request_id = request.headers.get("X-Request-Id")
    if not request_id:
        return ORJSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": "X-Request-Id is required"})
    tracer = await get_tracer()
    with tracer.start_as_current_span("movies-api") as span:
        span.set_attribute("http.request_id", request_id)
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

from api.v1 import auth, oauth, role, user_role
from core.config import settings
from db import postgres, redis
from db.tracer import get_tracer
from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from rate_limit.token_bucket import TokenBucket
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


def configure_tracer() -> None:
    if not settings.jaeger_enable_tracer:
        return-
    jaeger_exporter = JaegerExporter(agent_host_name=settings.jaeger_host, agent_port=settings.jaeger_port)
    trace.set_tracer_provider(TracerProvider(resource=Resource.create({SERVICE_NAME: "auth-service"})))
    trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(jaeger_exporter))
    # Чтобы видеть трейсы в консоли
    trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

app = FastAPI(
    title=f"Read-only API for {settings.project_name}.",
    description="Information about Authorisation and Roles.",
    version="1.0.0",
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    root_path="/auth",
    default_response_class=ORJSONResponse,
)
FastAPIInstrumentor.instrument_app(app)
token_bucket = TokenBucket(rate=settings.token_bucket_rate, capacity=settings.token_bucket_capacity)


@app.middleware("http")
async def before_request(request: Request, call_next):
    request_id = request.headers.get("X-Request-Id")
    if not request_id:
        return ORJSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": "X-Request-Id is required"})
    tracer: trace.Tracer = await get_tracer()
    with tracer.start_as_current_span("auth-api") as span:
        span.set_attribute("http.request_id", request_id)
        response = await call_next(request)
        return response


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

    engine = create_async_engine(settings.construct_sqlalchemy_url())
    postgres.session_maker = async_sessionmaker(engine, expire_on_commit=False)


@app.on_event("shutdown")
async def shutdown():
    await redis.redis.close()


app.include_router(auth.router, prefix="/api/v1/auth")
app.include_router(role.router, prefix="/api/v1/roles")
app.include_router(user_role.router, prefix="/api/v1/user_roles")
app.include_router(oauth.router, prefix="/api/v1/oauth")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=80)

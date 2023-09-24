from api.v1 import auth, oauth, role, user_role
from core.config import settings
from db import postgres, redis
from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


def configure_tracer() -> None:
    jaeger_exporter = JaegerExporter(agent_host_name="jaeger", agent_port=6831)
    trace.set_tracer_provider(TracerProvider(resource=Resource.create({SERVICE_NAME: "auth-service"})))
    trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(jaeger_exporter))
    # Чтобы видеть трейсы в консоли
    trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))


configure_tracer()
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


@app.middleware("http")
async def before_request(request: Request, call_next):
    response = await call_next(request)
    request_id = request.headers.get("X-Request-Id")
    if not request_id:
        return ORJSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": "X-Request-Id is required"})
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

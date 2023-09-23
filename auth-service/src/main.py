from api.v1 import auth, oauth, role, user_role
from core.config import settings
from db import postgres, redis
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

app = FastAPI(
    title=f"Read-only API for {settings.project_name}.",
    description="Information about Authorisation and Roles.",
    version="1.0.0",
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    # root_path="/auth",
    default_response_class=ORJSONResponse,
)


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

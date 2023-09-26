import os
from logging import config as logging_config

from core.logger import LOGGING
from pydantic import Field
from pydantic_settings import BaseSettings

logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):
    project_name: str = Field("movies", env="PROJECT_NAME")

    auth_service_host: str = Field("auth-api", env="AUTH_SERVICE_HOST")
    auth_service_port: str = Field(8000, env="AUTH_SERVICE_PORT")

    cache_expire_time: int = Field(300, env="CACHE_EXPIRE_TIME_IN_SECONDS")

    redis_host: str = Field("127.0.0.1", env="REDIS_PORT")
    redis_port: int = Field(6379, env="PROJECT_NAME")

    elastic_host: str = Field("127.0.0.1", env="ELASTIC_HOST")
    elastic_port: int = Field(9200, env="ELASTIC_PORT")
    elastic_schema: str = Field("http", env="ELASTIC_SCHEME")

    @property
    def auth_url_me(self) -> str:
        return f"http://{self.auth_service_host}:{self.auth_service_port}/auth/api/v1/auth/me"

    @property
    def elastic_url(self):
        return f"{self.elastic_schema}://{self.elastic_host}:{self.elastic_port}"


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
settings = Settings()

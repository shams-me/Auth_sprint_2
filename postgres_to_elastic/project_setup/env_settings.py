import logging

from pydantic import Field
from pydantic_settings import BaseSettings

logging.basicConfig(level=logging.INFO)


class Settings(BaseSettings):
    postgres_host: str = Field(default="127.0.0.1", env="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, env="POSTGRES_PORT")
    postgres_user: str = Field(default="auth", env="POSTGRES_USER")
    postgres_password: str = Field(default="123qwe", env="POSTGRES_PASSWORD")
    postgres_db: str = Field(default="auth_database", env="POSTGRES_DB")
    redis_host: str = Field(default="127.0.0.1", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    elastic_host: str = Field(default="elasticsearch", env="ELASTIC_HOST")
    elastic_port: int = Field(default=9200, env="ELASTIC_PORT")
    elastic_scheme: str = Field(default="http", env="ELASTIC_SCHEME")
    repeat_time_seconds: int = Field(default=60, env="REPEAT_TIME_SECONDS")

    @property
    def elastic_url(self):
        return f"{self.elastic_scheme}://{self.elastic_host}:{self.elastic_port}"

    @property
    def database_url(self):
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    @property
    def redis_url(self):
        return f"redis://{self.redis_host}:{self.redis_port}/0"

    class Config:
        env_file = "../../.env.example"

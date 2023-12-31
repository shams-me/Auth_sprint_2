import os
from logging import config as logging_config

from pydantic import Field
from pydantic_settings import BaseSettings

from .logger import LOGGING

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):
    project_name: str = Field("Authorisation", env="PROJECT_NAME")

    cache_expire_time: int = Field(600, env="CACHE_EXPIRE_TIME_IN_SECONDS")

    jwt_secret: str = Field("some_mega_encrypting_word", env="JWT_SECRET")

    enable_tracer: bool = Field(True, env="ENABLE_TRACER")

    YANDEX_CLIENT_ID: str = Field("5fae3168fba440d48acd176ccd9f4a85", env="YANDEX_CLIENT_ID")
    YANDEX_CLIENT_SECRET: str = Field("95f335c9847e4f93af00d7980a1b7c30", env="YANDEX_CLIENT_SECRET")
    YANDEX_REDIRECT_URI: str = Field(
        "http://localhost/auth/api/auth/login/yandex/redirect",
        env="YANDEX_REDIRECT_URI",
    )

    postgres_host: str = Field(default="127.0.0.1", env="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, env="POSTGRES_PORT")
    postgres_user: str = Field(default="postgres", env="POSTGRES_USER")
    postgres_password: str = Field(default="1", env="POSTGRES_PASSWORD")
    postgres_db: str = Field(default="test", env="POSTGRES_DB")

    jaeger_host: str = Field(default="jaeger")
    jaeger_port: int = Field(default=6831)
    jaeger_enable_tracer: bool = Field(default=True)
    super_user_pass: str = Field("some_mega_hard_pass", env="SUPER_USER_PASS")
    super_user_mail: str = Field("superuser@god.com", env="SUPER_USER_MAIL")

    jaeger_host: str = Field("jaeger", env="JAEGER_HOST")
    jaeger_port: int = Field(6831, env="JAEGER_PORT")

    service_host: str = Field("127.0.0.1")
    service_port: str | int = Field(8000)

    token_bucket_capacity: int = Field(default=10)
    token_bucket_rate: int = Field(default=1)

    @property
    def postgres_url(self):
        return f"{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    def construct_sqlalchemy_url(self, driver: str = "postgresql+asyncpg") -> str:
        user_creds = f"{self.postgres_user}:{self.postgres_password}"
        url = f"{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        return f"{driver}://{user_creds}@{url}"


settings = Settings()

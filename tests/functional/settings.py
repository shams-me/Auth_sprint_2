from pydantic import Field
from pydantic_settings import BaseSettings


class TestSettings(BaseSettings):
    redis_host: str = Field("127.0.0.1")
    redis_port: int = Field(6379)

    postgres_db: str = Field("auth")
    postgres_user: str = Field("admin")
    postgres_password: str = Field("admin")
    postgres_host: str = Field("127.0.0.1")
    postgres_port: int = Field(5432)

    super_user_pass: str = Field("superpass", env="SUPER_USER_PASS")
    super_user_mail: str = Field("superuser@gmail.com", env="SUPER_USER_MAIL")
    service_host: str = Field("127.0.0.1")
    service_port: str | int = Field(8000)

    @property
    def postgres_credentials(self) -> dict:
        return {
            "dbname": self.postgres_db,
            "user": self.postgres_user,
            "password": self.postgres_password,
            "host": self.postgres_host,
            "port": self.postgres_port,
        }

    @property
    def service_url(self):
        return f"http://{self.service_host}:{self.service_port}"


test_settings = TestSettings()

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    host: str = Field(default="localhost", alias="HOST")
    port: int = Field(default=8001, alias="PORT")
    environment: Literal["development", "production"] = Field(
        default="development", alias="ENVIRONMENT"
    )

    # Format: "amount/period" (e.g., "5/minute", "10/second", "100/hour")
    default_rate_limit: str = Field(default="1/second", alias="RATE_LIMIT")

    db_user: str = Field(default="postgres", alias="DB_USER")
    db_password: str = Field(default="1234", alias="DB_PASSWORD")
    db_host: str = Field(default="localhost", alias="DB_HOST")
    db_port: int = Field(default=5432, alias="DB_PORT")
    db_name: str = Field(default="templatedb", alias="DB_NAME")

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def database_url_sync(self) -> str:
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    jwt_secret_key: str = Field(default="myjwtsecretkey", alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )

    base_image_path: str = Field(
        default="./data/images",
        alias="BASE_IMAGE_PATH",
    )

    cors_origins: str = Field(default="http://localhost:3000", alias="CORS_ORIGINS")

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


settings = Settings()

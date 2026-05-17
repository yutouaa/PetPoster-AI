from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置，生产环境必须显式提供敏感配置。"""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = Field(default="development", alias="APP_ENV")
    api_title: str = "PetPoster AI API"
    api_prefix: str = "/api"

    database_url: str = Field(
        default="sqlite:///./petposter_dev.db",
        alias="DATABASE_URL"
    )

    admin_username: str = Field(default="admin", alias="ADMIN_USERNAME")
    admin_password: str = Field(default="admin123", alias="ADMIN_PASSWORD")
    admin_jwt_secret: str = Field(default="please-change-this-secret", alias="ADMIN_JWT_SECRET")
    admin_jwt_expires_minutes: int = Field(default=1440, alias="ADMIN_JWT_EXPIRES_MINUTES")

    cors_origins: str = Field(
        default="http://localhost:9527,http://127.0.0.1:9527,http://localhost:5173,http://127.0.0.1:5173",
        alias="CORS_ORIGINS"
    )

    rightcode_api_key: str = Field(
        default="",
        alias="RIGHTCODE_API_KEY"
    )
    rightcode_base_url: str = Field(
        default="https://www.right.codes/draw",
        alias="RIGHTCODE_BASE_URL"
    )
    rightcode_model: str = Field(default="gpt-image-2", alias="RIGHTCODE_MODEL")
    rightcode_timeout: int = Field(default=300, alias="RIGHTCODE_TIMEOUT")
    upload_dir: str = Field(default="./uploads", alias="UPLOAD_DIR")
    generated_image_dir: str = Field(default="./uploads", alias="GENERATED_IMAGE_DIR")
    public_base_url: str = Field(default="http://127.0.0.1:8000", alias="PUBLIC_BASE_URL")
    max_upload_size: int = Field(default=10485760, alias="MAX_UPLOAD_SIZE")

    @field_validator("admin_jwt_secret")
    @classmethod
    def validate_admin_jwt_secret(cls, value: str) -> str:
        if not value:
            raise ValueError("ADMIN_JWT_SECRET 不能为空")
        return value

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    def validate_production_secrets(self) -> None:
        if self.app_env != "production":
            return

        if self.admin_password == "admin123":
            raise ValueError("生产环境必须修改 ADMIN_PASSWORD")
        if self.admin_jwt_secret == "please-change-this-secret":
            raise ValueError("生产环境必须修改 ADMIN_JWT_SECRET")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.validate_production_secrets()
    return settings

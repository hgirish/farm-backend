from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    DB_URL: Optional[str]
    CLOUDINARY_SECRET_KEY: Optional[str]
    CLOUDINARY_API_KEY: Optional[str]
    CLOUDINARY_CLOUD_NAME: Optional[str]
    OPENAI_API_KEY: Optional[str]
    RESEND_API_KEY: Optional[str]
    AUTH_SECRET: Optional[str]
    TO_EMAIL: Optional[str]

    model_config = SettingsConfigDict(
        env_file=".env", extra="ignore"
    )

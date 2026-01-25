from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # ADMIN BOT
    admin_bot_token: str = Field(..., env="ADMIN_BOT_TOKEN")
    admin_telegram_id: int = Field(..., env="ADMIN_TELEGRAM_ID")

    # USER BOT
    user_bot_token: str = Field(..., env="USER_BOT_TOKEN")
    user_bot_username: str = Field(..., env="USER_BOT_USERNAME")

    # DATABASE
    db_host: str = Field(..., env="DB_HOST")
    db_port: int = Field(..., env="DB_PORT")
    db_name: str = Field(..., env="DB_NAME")
    db_user: str = Field(..., env="DB_USER")
    db_password: str = Field(..., env="DB_PASSWORD")

    # SYSTEM
    env: str = Field("dev", env="ENV")

    class Config:
        env_file = ".env"


settings = Settings()

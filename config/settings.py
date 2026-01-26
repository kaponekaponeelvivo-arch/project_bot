from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # =========================
    # ADMIN BOT
    # =========================
    admin_bot_token: str = Field(..., env="ADMIN_BOT_TOKEN")
    admin_telegram_id: int = Field(..., env="ADMIN_TELEGRAM_ID")

    # =========================
    # USER BOT
    # =========================
    user_bot_token: str = Field(..., env="USER_BOT_TOKEN")
    user_bot_username: str = Field(..., env="USER_BOT_USERNAME")

    # =========================
    # DATABASE (components)
    # =========================
    db_host: str = Field(..., env="DB_HOST")
    db_port: int = Field(..., env="DB_PORT")
    db_name: str = Field(..., env="DB_NAME")
    db_user: str = Field(..., env="DB_USER")
    db_password: str = Field(..., env="DB_PASSWORD")

    # =========================
    # SYSTEM
    # =========================
    env: str = Field("dev", env="ENV")

    @property
    def database_url(self) -> str:
        """
        Async database URL (for app)
        """
        return (
            f"postgresql+asyncpg://{self.db_user}:"
            f"{self.db_password}@{self.db_host}:"
            f"{self.db_port}/{self.db_name}"
        )

    @property
    def database_url_sync(self) -> str:
        """
        Sync database URL (for Alembic)
        """
        return (
            f"postgresql+psycopg2://{self.db_user}:"
            f"{self.db_password}@{self.db_host}:"
            f"{self.db_port}/{self.db_name}"
        )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

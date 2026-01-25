from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseModel):
    admin_bot_token: str
    environment: str = "local"


settings = Settings(
    admin_bot_token=os.getenv("ADMIN_BOT_TOKEN"),
    environment=os.getenv("ENVIRONMENT", "local")
)

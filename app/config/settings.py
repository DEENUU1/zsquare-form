from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv
from starlette.templating import Jinja2Templates

load_dotenv()


class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str = os.getenv("DATABASE_URL")
    TEMPLATES: Jinja2Templates = Jinja2Templates(directory="templates")
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DEBUG: str = os.getenv("DEBUG") == "True"
    OPENAI_APIKEY: str = os.getenv("OPENAI_APIKEY")


settings = Settings()

from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv
from starlette.templating import Jinja2Templates

load_dotenv()


class Settings(BaseSettings):
    TEMPLATES: Jinja2Templates = Jinja2Templates(directory="templates")
    DEBUG: str = os.getenv("DEBUG") == "True"
    API_URL: str = os.getenv("API_URL")


settings = Settings()

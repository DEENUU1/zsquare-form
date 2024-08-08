from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import logging
from views.router import router
from config.settings import settings


logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

if settings.DEBUG:
    app = FastAPI(
        debug=True
    )
else:
    app = FastAPI(
        docs_url=None,
        redoc_url=None,
        openapi_url=None
    )

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.exception_handler(404)
async def custom_404_handler(request, __):
    return settings.TEMPLATES.TemplateResponse("404.html", {"request": request})

app.include_router(router)

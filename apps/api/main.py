"""
DEMATELab API - Main application entry point.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

import matplotlib
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.v1.api import api_router
from config.settings_config import get_settings
from constants.app_constants import PORT, PROJECT_DETAILS, PROJECT_SETTINGS
from errors.error_handlers import error_handlers
from middleware.cache_control_middleware import CacheControlMiddleware
from utils.font_utils import font_registrar

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

# Charts are rendered without a display (object-oriented Figure API only) in the Qt app's Inter font.
matplotlib.use("Agg")
font_registrar.register_inter_fonts()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Log startup details; the API holds no clients to close."""
    settings = get_settings()
    logger.info("%s v%s (%s)", PROJECT_DETAILS["PROJECT_NAME"], PROJECT_DETAILS["VERSION"], settings.app_env)
    logger.info("API docs: http://localhost:%s%s", PORT, PROJECT_SETTINGS["API_DOCS_URL"])
    yield
    logger.info("Shutdown complete.")


app = FastAPI(
    title=PROJECT_DETAILS["PROJECT_NAME"],
    version=PROJECT_DETAILS["VERSION"],
    description=PROJECT_DETAILS["DESCRIPTION"],
    docs_url=PROJECT_SETTINGS["API_DOCS_URL"],
    redoc_url=PROJECT_SETTINGS["REDOC_URL"],
    openapi_url=PROJECT_SETTINGS["OPENAPI_URL"],
    lifespan=lifespan,
)

error_handlers.register(app)

app.add_middleware(CacheControlMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

app.include_router(api_router, prefix="/api/v1")


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=PORT, log_level="info", reload=True, reload_dirs=["."])

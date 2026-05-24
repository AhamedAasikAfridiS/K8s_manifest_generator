"""Auth service FastAPI application entry point."""

import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import Base, engine
from app.logging_config import setup_logging
from app.routers import auth, health

settings = get_settings()
setup_logging(settings.debug)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info("%s %s -> %s (%.2fms)", request.method, request.url.path, response.status_code, duration_ms)
    return response


@app.on_event("startup")
def on_startup() -> None:
    logger.info("Starting %s in %s mode", settings.app_name, settings.app_env)
    Base.metadata.create_all(bind=engine)


app.include_router(health.router)
app.include_router(auth.router)

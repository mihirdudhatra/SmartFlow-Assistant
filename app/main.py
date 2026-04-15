"""
app/main.py

FastAPI application factory for SmartFlow-Assistant.

All routers are registered here.  Running this file directly (via uvicorn)
starts the development server.
"""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from app.api.routes.assistant import router as assistant_router
from app.utils.logger import logger


# ---------------------------------------------------------------------------
# Lifespan event handler (replaces deprecated @app.on_event)
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    logger.info("SmartFlow Assistant starting up…")
    yield
    logger.info("SmartFlow Assistant shutting down…")


# ---------------------------------------------------------------------------
# Application instance
# ---------------------------------------------------------------------------

app = FastAPI(
    title="SmartFlow Assistant",
    description=(
        "AI-powered task assistant with Google Calendar integration.\n\n"
        "Send natural-language messages and the assistant will detect your "
        "intent and act accordingly."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# Register routers
# ---------------------------------------------------------------------------

app.include_router(assistant_router)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get("/health", tags=["health"], summary="Health check")
def health_check() -> dict:
    """Return a simple liveness probe response."""
    return {"status": "ok", "service": "SmartFlow Assistant"}

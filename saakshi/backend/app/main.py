"""Saakshi Forensic Platform Application Entrypoint.

Purpose: Main FastAPI service definition wiring all API routers, security middleware, and database lifecycle.
Inputs: Incoming HTTP client requests.
Outputs: Forensic platform REST API services.
Status: Implemented
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.analytics import router as analytics_router
from app.api.cases import router as cases_router
from app.api.devices import router as devices_router
from app.api.evidence import router as evidence_router
from app.api.health import router as health_router
from app.api.ledger import router as ledger_router
from app.api.recovery import router as recovery_router
from app.api.reports import router as reports_router
from app.api.timeline import router as timeline_router
from app.config import settings
from app.core.logging import logger
from app.db.base import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan managing database table creation and shutdown."""
    logger.info("Initializing Saakshi forensic engine in air-gapped mode: %s", settings.AIR_GAPPED_MODE)
    # Ensure tables are created for SQLite development/test setups
    Base.metadata.create_all(bind=engine)
    yield
    logger.info("Shutting down Saakshi forensic engine.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Vendor-Agnostic DVR/NVR Forensic Analysis Platform (SIH 2026, NTRO)",
    lifespan=lifespan,
)

# Air-gapped local cross-origin policy for Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health_router)
app.include_router(cases_router)
app.include_router(devices_router)
app.include_router(evidence_router)
app.include_router(recovery_router)
app.include_router(timeline_router)
app.include_router(analytics_router)
app.include_router(ledger_router)
app.include_router(reports_router)


@app.get("/")
def root() -> dict[str, str]:
    """Root platform greeting."""
    return {"message": "Saakshi Digital Forensic Platform is online.", "status": "ok"}

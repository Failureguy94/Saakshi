"""FrameProof Health & System Status Endpoint.

Purpose: Provide service health checks and air-gapped readiness confirmation.
Inputs: HTTP GET request.
Outputs: Service health JSON metadata.
Status: Implemented
"""

from fastapi import APIRouter

from app.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health")
def get_health() -> dict[str, str | bool]:
    """Return platform operational status and offline mode confirmation."""
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "offline_mode": settings.AIR_GAPPED_MODE,
    }

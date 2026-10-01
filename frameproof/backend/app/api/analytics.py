"""FrameProof Analytics & Tamper Detection API Router.

Purpose: Endpoints for forensic motion vectors, object detection, and video forgery analysis.
Inputs: Video segment IDs and analytics configurations.
Outputs: Detected events, bounding boxes, and tamper alerts.
Status: Stub
"""

from fastapi import APIRouter

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/events")
def list_events() -> None:
    """List forensic events detected across evidence segments.

    Raises:
        NotImplementedError: Forensic analytics endpoints are planned.
    """
    raise NotImplementedError("planned: video analytics and tamper detection query endpoints")

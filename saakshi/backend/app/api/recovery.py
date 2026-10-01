"""Saakshi Recovery & Carving API Router.

Purpose: Trigger and monitor Annex-B NAL carving, ring buffer recovery, and index extraction.
Inputs: Evidence ID, carving parameters, and sector boundary selections.
Outputs: Carving task status, discovered video segments, and extraction metrics.
Status: Stub
"""

from fastapi import APIRouter

router = APIRouter(prefix="/recovery", tags=["Recovery"])


@router.post("/carve")
def start_carving() -> None:
    """Trigger background Annex-B NAL carving on an evidence image.

    Raises:
        NotImplementedError: Video carving trigger endpoint is planned.
    """
    raise NotImplementedError("planned: video stream carving trigger and progress monitoring")

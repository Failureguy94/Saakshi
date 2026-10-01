"""FrameProof Devices API Router.

Purpose: Endpoints to attach and manage physical DVR/NVR hardware devices within a case.
Inputs: Hardware specifications and case IDs.
Outputs: Device registration records.
Status: Stub
"""

from fastapi import APIRouter

router = APIRouter(prefix="/devices", tags=["Devices"])


@router.get("")
def list_devices() -> None:
    """List physical devices registered in a case.

    Raises:
        NotImplementedError: Device management endpoints are planned.
    """
    raise NotImplementedError("planned: hardware device registration and querying")

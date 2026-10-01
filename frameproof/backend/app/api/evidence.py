"""FrameProof Evidence Images API Router.

Purpose: Register and verify forensic bit-stream disk images and compute dual digests.
Inputs: Evidence file paths and intake metadata.
Outputs: Registered evidence image records and computed cryptographic hashes.
Status: Stub
"""

from fastapi import APIRouter

router = APIRouter(prefix="/evidence", tags=["Evidence"])


@router.get("")
def list_evidence() -> None:
    """List forensic images associated with cases.

    Raises:
        NotImplementedError: Evidence listing and verification endpoints are planned.
    """
    raise NotImplementedError("planned: evidence image intake, hashing, and status endpoints")

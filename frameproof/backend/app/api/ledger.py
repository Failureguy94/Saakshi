"""FrameProof Custody Ledger & Audit Trail API Router.

Purpose: Endpoints to inspect, verify, and export the cryptographic chain of custody ledger.
Inputs: Case ID or evidence ID filters.
Outputs: Cryptographic custody records, Merkle roots, and chain verification status.
Status: Stub
"""

from fastapi import APIRouter

router = APIRouter(prefix="/ledger", tags=["Custody Ledger"])


@router.get("/verify")
def verify_custody() -> None:
    """Verify cryptographic integrity of custody log.

    Raises:
        NotImplementedError: Custody verification endpoint is planned.
    """
    raise NotImplementedError("planned: cryptographic chain of custody audit and verification endpoint")

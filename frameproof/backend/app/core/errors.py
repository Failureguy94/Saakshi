"""FrameProof Core Error Definitions.

Purpose: Define domain exceptions for forensic integrity, parsing, and pipeline failures.
Inputs: Error messages and context details.
Outputs: Typed exception hierarchy.
Status: Implemented
"""


class ForensicException(Exception):
    """Base exception for all FrameProof domain errors."""


class EvidenceTamperException(ForensicException):
    """Raised when evidence hash does not match recorded custody hash."""


class ReadOnlyViolationException(ForensicException):
    """Raised when an operation attempts to write to an evidence image."""


class CustodyVerificationException(ForensicException):
    """Raised when cryptographic chain of custody validation fails."""


class ProfileValidationException(ForensicException):
    """Raised when a vendor profile fails schema validation."""


class CarvingException(ForensicException):
    """Raised when Annex-B or ring buffer carving encounters a critical error."""

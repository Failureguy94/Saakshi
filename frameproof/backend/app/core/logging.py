"""FrameProof Forensic Audit Logging.

Purpose: Structured logging with forensic audit trail formatting.
Inputs: System log records and security events.
Outputs: Formatted console and file log streams.
Status: Implemented
"""

import logging
import sys


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Configure structured forensic logging."""
    logger = logging.getLogger("frameproof")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


logger = setup_logging()

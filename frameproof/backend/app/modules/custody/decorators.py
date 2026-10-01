"""FrameProof Evidence Access & Custody Tracking Decorators.

Purpose: Enforce read-only verification on evidence paths and automatically record custody events.
Inputs: Target forensic functions, evidence parameters, and execution context.
Outputs: Wrapped function ensuring read-only guarantees and logging to custody ledger.
Status: Implemented
"""

import functools
from collections.abc import Callable
from pathlib import Path
from typing import Any

from app.core.security import ReadOnlySecurityGuard
from app.modules.custody.chain import CustodyLog

# Global in-memory / configured custody log instance
_default_custody_log = CustodyLog()


def get_default_custody_log() -> CustodyLog:
    """Return the default custody log instance."""
    return _default_custody_log


def forensic_stage(
    action: str,
    evidence_path_param: str = "evidence_path",
    evidence_id_param: str = "evidence_id",
    actor_default: str = "SYSTEM_WORKER",
    custody_log: CustodyLog | None = None,
) -> Callable[..., Any]:
    """Decorator ensuring read-only access and automated custody logging.

    Args:
        action: Name of the forensic action (e.g. ACQUIRED, CARVED).
        evidence_path_param: Name of the keyword argument containing the evidence path.
        evidence_id_param: Name of keyword argument containing evidence ID.
        actor_default: Fallback actor if not passed in kwargs.
        custody_log: CustodyLog instance (defaults to shared global log).
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # 1. Assert read-only protection if evidence path is provided
            if evidence_path_param in kwargs:
                ev_path = kwargs[evidence_path_param]
                if ev_path:
                    ReadOnlySecurityGuard.assert_read_only_path(Path(ev_path))

            # 2. Execute the forensic operation
            result = func(*args, **kwargs)

            # 3. Log custody record
            log = custody_log or get_default_custody_log()
            ev_id = kwargs.get(evidence_id_param, "EVID-UNKNOWN")
            actor = kwargs.get("actor", actor_default)
            ev_hash = kwargs.get("evidence_hash", "0" * 64)

            log.append(
                actor=actor,
                action=action,
                evidence_id=str(ev_id),
                evidence_hash=str(ev_hash),
                details={"function": func.__name__},
            )

            return result

        return wrapper

    return decorator

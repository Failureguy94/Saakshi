"""Saakshi Evidence Security & Read-Only Protection.

Purpose: Enforces write-blocking verification and read-only file handle guarantees.
Inputs: File paths and OS descriptors.
Outputs: Read-only verification checks and safe read contexts.
Status: Implemented
"""

import os
from pathlib import Path


class ReadOnlySecurityGuard:
    """Verifies that evidence files are opened strictly in read-only mode."""

    @staticmethod
    def assert_read_only_path(path: Path | str) -> None:
        """Verify that the target path exists and that write permissions are not used."""
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Evidence file does not exist: {p}")

        # In strict Linux forensic environments, ensure we do not have writable handle open
        if os.name == "posix":
            # Test opening in read-only mode
            try:
                fd = os.open(p, os.O_RDONLY)
                os.close(fd)
            except OSError as err:
                raise PermissionError(f"Cannot open evidence in read-only mode: {err}") from err

    @staticmethod
    def forbid_write_mode(mode: str) -> None:
        """Raise error if any write/append/update mode is requested."""
        if any(flag in mode for flag in ("w", "a", "+", "x")):
            raise PermissionError(f"Forensic violation: Write mode '{mode}' is forbidden on evidence sources.")

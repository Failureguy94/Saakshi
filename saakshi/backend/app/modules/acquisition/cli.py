"""Saakshi Acquisition CLI.

Purpose:
    Command-line interface for forensic acquisition of disk images or block devices.
    Reads the source strictly read-only, computes dual MD5 + SHA-256 in one streaming
    pass, writes a custody log entry, and optionally verifies a previously computed
    hash to confirm image integrity.

Inputs:
    Evidence file path or block device path (read-only).
    Optional previous hash values for verification.

Outputs:
    HashResult (md5, sha256, byte_count) printed to stdout.
    Custody log entry appended to a JSONL file.
    Exit code 0 on success; 1 on verification mismatch or I/O error.

Status: Implemented.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from app.modules.acquisition.hashing import hash_file
from app.modules.custody.chain import CustodyLog


@click.group()
def cli() -> None:
    """Saakshi forensic acquisition toolkit."""


@cli.command("acquire")
@click.argument("image_path", type=click.Path(exists=True, readable=True, path_type=Path))
@click.option(
    "--out-dir",
    type=click.Path(file_okay=False, writable=True, path_type=Path),
    default=Path("."),
    show_default=True,
    help="Directory for custody log output.",
)
@click.option(
    "--case-id",
    default="UNKNOWN",
    show_default=True,
    help="Case identifier for custody log.",
)
@click.option(
    "--actor",
    default="forensic_officer",
    show_default=True,
    help="Acquiring officer / process identifier.",
)
@click.option(
    "--log-file",
    type=click.Path(dir_okay=False, path_type=Path),
    default=None,
    help="Path to JSONL custody log (default: <out-dir>/custody.jsonl).",
)
@click.option(
    "--verify-md5",
    default=None,
    help="Expected MD5 hex digest for integrity verification.",
)
@click.option(
    "--verify-sha256",
    default=None,
    help="Expected SHA-256 hex digest for integrity verification.",
)
@click.option(
    "--json-output",
    is_flag=True,
    default=False,
    help="Print result as JSON instead of human-readable text.",
)
def acquire(
    image_path: Path,
    out_dir: Path,
    case_id: str,
    actor: str,
    log_file: Path | None,
    verify_md5: str | None,
    verify_sha256: str | None,
    json_output: bool,
) -> None:
    """Hash and log acquisition of IMAGE_PATH (read-only, dual MD5 + SHA-256).

    When --verify-md5 or --verify-sha256 are supplied the command re-hashes the
    file and exits with code 1 if any digest mismatches, code 0 if all match.

    Example:
        saakshi acquire /dev/sdb --case-id CASE001 --actor sgt_sharma
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    custody_path = log_file or (out_dir / "custody.jsonl")

    try:
        result = hash_file(image_path)
    except PermissionError as exc:
        click.echo(f"ERROR: Cannot read {image_path}: {exc}", err=True)
        sys.exit(1)
    except FileNotFoundError:
        click.echo(f"ERROR: File not found: {image_path}", err=True)
        sys.exit(1)

    # ── Custody log ──────────────────────────────────────────────────────────
    log_obj = CustodyLog(log_path=custody_path)
    log_obj.append(
        actor=actor,
        action="ACQUIRE",
        evidence_id=str(image_path.resolve()),
        evidence_hash=result.sha256,
        details={
            "case_id": case_id,
            "image_path": str(image_path.resolve()),
            "md5": result.md5,
            "sha256": result.sha256,
            "byte_count": result.byte_count,
        },
    )

    # ── Output ───────────────────────────────────────────────────────────────
    output_data = {
        "image_path": str(image_path.resolve()),
        "md5": result.md5,
        "sha256": result.sha256,
        "byte_count": result.byte_count,
        "custody_log": str(custody_path.resolve()),
    }

    if json_output:
        click.echo(json.dumps(output_data, indent=2))
    else:
        click.echo(f"Image   : {image_path.resolve()}")
        click.echo(f"Bytes   : {result.byte_count:,}")
        click.echo(f"MD5     : {result.md5}")
        click.echo(f"SHA-256 : {result.sha256}")
        click.echo(f"Custody : {custody_path.resolve()}")

    # ── Verification ─────────────────────────────────────────────────────────
    mismatches: list[str] = []
    if verify_md5 and verify_md5.lower() != result.md5:
        mismatches.append(f"MD5 mismatch: expected {verify_md5}, got {result.md5}")
    if verify_sha256 and verify_sha256.lower() != result.sha256:
        mismatches.append(f"SHA-256 mismatch: expected {verify_sha256}, got {result.sha256}")

    if mismatches:
        for msg in mismatches:
            click.echo(f"MISMATCH: {msg}", err=True)
        sys.exit(1)

    if verify_md5 or verify_sha256:
        click.echo("VERIFIED: all digests match.")


@cli.command("verify")
@click.argument("custody_log", type=click.Path(exists=True, readable=True, path_type=Path))
@click.option("--json-output", is_flag=True, default=False, help="Print result as JSON.")
def verify(custody_log: Path, json_output: bool) -> None:
    """Verify the integrity of a CUSTODY_LOG JSONL file (detect tampering).

    Reads every entry in the chain and validates that each entry's
    prev_hash field matches the hash of the previous entry.  Exits with
    code 1 if tampering is detected.
    """
    from app.modules.custody.chain import CustodyLog

    log_obj = CustodyLog(log_path=custody_log)
    ok, detail = log_obj.verify()

    result = {
        "custody_log": str(custody_log.resolve()),
        "chain_valid": ok,
        "detail": detail,
    }

    if json_output:
        click.echo(json.dumps(result, indent=2))
    else:
        status = "VALID" if ok else "TAMPERED"
        click.echo(f"Chain status : {status}")
        click.echo(f"Detail       : {detail}")

    if not ok:
        sys.exit(1)


def main() -> None:
    """Entry point for the saakshi CLI tool."""
    cli()


if __name__ == "__main__":
    main()

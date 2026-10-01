"""FrameProof OEM Vendor Profile Loader.

Purpose: Parse, validate, and index YAML vendor profile specifications.
Inputs: Paths to vendor profile YAML files or directories.
Outputs: Dictionary mapping vendor IDs to validated VendorProfile instances.
Status: Implemented
"""

from pathlib import Path

import yaml

from app.modules.profiles.schema import VendorProfile


def load_profile(file_path: Path | str) -> VendorProfile:
    """Load and validate a single vendor profile YAML file.

    Args:
        file_path: Path to YAML file.

    Returns:
        Validated VendorProfile instance.

    Raises:
        FileNotFoundError: If profile file does not exist.
        ValueError: If YAML syntax is invalid or schema validation fails.
    """
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Vendor profile not found: {path}")

    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as err:
        raise ValueError(f"Invalid YAML in profile {path.name}: {err}") from err

    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping at root of profile {path.name}")

    return VendorProfile.model_validate(data)


def load_all_profiles(directory: Path | str) -> dict[str, VendorProfile]:
    """Scan directory and validate all YAML vendor profiles.

    Args:
        directory: Path to folder containing vendor YAML definitions.

    Returns:
        Dictionary mapping vendor_id to VendorProfile.
    """
    dir_path = Path(directory)
    if not dir_path.is_dir():
        raise FileNotFoundError(f"Profiles directory not found: {dir_path}")

    profiles: dict[str, VendorProfile] = {}
    for yaml_file in sorted(dir_path.glob("*.yaml")):
        profile = load_profile(yaml_file)
        profiles[profile.vendor_id] = profile

    return profiles

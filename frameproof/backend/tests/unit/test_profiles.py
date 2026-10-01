"""Unit tests for vendor profiles schema and loader."""

from pathlib import Path

import pytest

from app.modules.profiles.loader import load_all_profiles, load_profile
from app.modules.profiles.schema import VendorProfile

VENDORS_DIR = Path(__file__).parent.parent.parent / "app" / "modules" / "profiles" / "vendors"

EXPECTED_VENDORS = {
    "hikvision",
    "dahua",
    "cpplus",
    "uniview",
    "tplink",
    "honeywell",
    "godrej",
    "matrix",
    "generic",
}


def test_load_all_vendor_profiles() -> None:
    profiles = load_all_profiles(VENDORS_DIR)

    assert set(profiles.keys()) == EXPECTED_VENDORS

    for vendor_id, profile in profiles.items():
        assert isinstance(profile, VendorProfile)
        assert profile.vendor_id == vendor_id
        # Forensic honesty requirement: must be marked placeholder
        assert profile.status == "placeholder"
        assert len(profile.todo_fields) > 0
        assert profile.volume_layout.sector_size_bytes == 512


def test_load_single_profile() -> None:
    profile_path = VENDORS_DIR / "hikvision.yaml"
    profile = load_profile(profile_path)
    assert profile.vendor_id == "hikvision"
    assert profile.vendor_name == "Hikvision Digital Technology"


def test_load_missing_profile_raises() -> None:
    with pytest.raises(FileNotFoundError):
        load_profile(VENDORS_DIR / "nonexistent.yaml")

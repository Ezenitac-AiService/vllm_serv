"""
Unit tests for platform profiles loading in ConfigManager.
Validates loading and validation of target platform profiles (dev-rtx3060, legacy-i7-930-gtx1070).
"""

import pytest
from src.core.config_manager import ConfigManager


def test_get_platform_profiles():
    """T016 [US4]: Verifies loading all platform profiles from platform_profiles.json."""
    cm = ConfigManager()
    cm.invalidate_all_caches()
    profiles = cm.get_platform_profiles()

    assert "dev-rtx3060" in profiles
    assert "legacy-i7-930-gtx1070" in profiles
    assert "pascal-avx2-gtx1080ti" in profiles

    dev = profiles["dev-rtx3060"]
    assert dev["compute_capability"] == "8.6"
    assert dev["vram_mb"] == 12288
    assert dev["ram_gb"] == 16
    assert dev["expected_avx"] is True
    assert "192.168.0.0/16" in dev["network"]["allowed_subnets"]

    pascal = profiles["pascal-avx2-gtx1080ti"]
    assert pascal["ram_gb"] == 32
    assert "10.0.0.0/8" in pascal["network"]["allowed_subnets"]

    legacy = profiles["legacy-i7-930-gtx1070"]
    assert legacy["compute_capability"] == "6.1"
    assert legacy["ram_gb"] == 24
    assert legacy["vram_mb"] == 8192
    assert legacy["expected_avx"] is False
    assert "192.168.0.0/16" in legacy["network"]["allowed_subnets"]


def test_get_platform_profile_single():
    """T016 [US4]: Verifies retrieving a single profile by ID."""
    cm = ConfigManager()
    profile = cm.get_platform_profile("legacy-i7-930-gtx1070")
    assert profile is not None
    assert profile["gpu_name"] == "NVIDIA GeForce GTX 1070"
    assert profile["os_name"] == "Ubuntu Server 24.04 LTS"

    non_existent = cm.get_platform_profile("non-existent-profile")
    assert non_existent is None


def test_platform_profile_network_configurations():
    """T015 [US3]: Verifies network configuration block in platform profiles."""
    cm = ConfigManager()
    cm.invalidate_all_caches()
    profiles = cm.get_platform_profiles()

    for prof_id, prof in profiles.items():
        if "network" in prof:
            net = prof["network"]
            assert "bind_host" in net
            assert "allowed_subnets" in net


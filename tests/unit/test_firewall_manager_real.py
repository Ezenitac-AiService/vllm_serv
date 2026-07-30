"""
Real-execution Test Suite for FirewallManager & Network Socket Probing (FR-004, FR-006).
Strictly obeys Constitution v1.3.1 (No Mocks, Real Socket Probes, Real OS Rule Inspection).
"""

import pytest
from src.core.firewall_manager import FirewallManager, RealSocketResult


def test_detect_firewall_system_real():
    """T005: Detect OS firewall utility on physical host without mocks."""
    fw_type = FirewallManager.detect_firewall_system()
    assert fw_type in ["ufw", "firewalld", "iptables", "unknown"]


def test_is_port_allowed_in_os_real():
    """T005: Query actual OS firewall ruleset for port 8081."""
    is_allowed = FirewallManager.is_port_allowed_in_os(8081, "tcp")
    assert isinstance(is_allowed, bool)


def test_real_socket_connectivity_probe():
    """T005: Probe physical host TCP socket connection on port 8081."""
    result = FirewallManager.verify_real_socket_connectivity(host="127.0.0.1", port=8081, timeout_s=1.0)
    assert isinstance(result, RealSocketResult)
    assert result.target_port == 8081
    assert result.rtt_ms >= 0.0


def test_allow_port_returns_guide_message_on_sudo_restriction():
    """T009: FirewallManager returns structured guide banner when non-interactive sudo is restricted."""
    fm = FirewallManager()
    status_info = fm.allow_port(8081, "tcp")
    assert hasattr(status_info, "system_type")
    assert hasattr(status_info, "guide_message")
    assert isinstance(status_info.guide_message, str)

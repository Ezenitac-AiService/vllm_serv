"""OS Firewall management and port configuration utility.

Feature: 025-server-ip-management
"""

import logging
import shutil
import subprocess
from dataclasses import dataclass
from typing import List, Optional

logger = logging.getLogger(__name__)


@dataclass
class FirewallStatusInfo:
    """Represents OS firewall status and port allow attempt results."""
    system_type: str  # ufw, iptables, firewalld, unknown
    is_firewall_active: bool
    port_open_success: bool
    requires_sudo: bool
    guide_message: str


class FirewallManager:
    """Attempts to allow service ports (8081, 8089) via ufw/iptables and handles non-root permission exceptions gracefully."""

    @staticmethod
    def detect_firewall_system() -> str:
        """Detects available OS firewall management utility."""
        if shutil.which("ufw"):
            return "ufw"
        elif shutil.which("firewalld"):
            return "firewalld"
        elif shutil.which("iptables"):
            return "iptables"
        return "unknown"

    def allow_port(self, port: int, protocol: str = "tcp") -> FirewallStatusInfo:
        """Attempts to allow specified port in OS firewall."""
        fw_type = self.detect_firewall_system()

        if fw_type == "ufw":
            try:
                res = subprocess.run(
                    ["ufw", "allow", f"{port}/{protocol}"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if res.returncode == 0:
                    logger.info(f"[FirewallManager] Successfully allowed port {port}/{protocol} via ufw")
                    return FirewallStatusInfo(
                        system_type="ufw",
                        is_firewall_active=True,
                        port_open_success=True,
                        requires_sudo=False,
                        guide_message=f"Port {port}/{protocol} successfully allowed via ufw"
                    )
                else:
                    guide = f"⚠️ OS 방화벽(ufw) 개방을 위해 'sudo ufw allow {port}/{protocol}' 명령을 실행해 주세요."
                    logger.warning(f"[FirewallManager] ufw allow port {port} failed: {res.stderr.strip()}. {guide}")
                    return FirewallStatusInfo(
                        system_type="ufw",
                        is_firewall_active=True,
                        port_open_success=False,
                        requires_sudo=True,
                        guide_message=guide
                    )
            except Exception as e:
                guide = f"⚠️ OS 방화벽(ufw) 개방을 위해 'sudo ufw allow {port}/{protocol}' 명령을 실행해 주세요."
                logger.warning(f"[FirewallManager] ufw allow exception: {e}. {guide}")
                return FirewallStatusInfo(
                    system_type="ufw",
                    is_firewall_active=True,
                    port_open_success=False,
                    requires_sudo=True,
                    guide_message=guide
                )

        guide = f"⚠️ 서버 서비스 포트({port}/{protocol}) 접속을 허용하려면 OS 방화벽 설정을 확인해 주세요."
        return FirewallStatusInfo(
            system_type=fw_type,
            is_firewall_active=False,
            port_open_success=True,
            requires_sudo=False,
            guide_message=guide
        )

    def ensure_service_ports_open(self, ports: List[int]) -> List[FirewallStatusInfo]:
        """Attempts to allow a list of service ports."""
        results = []
        for port in ports:
            results.append(self.allow_port(port))
        return results

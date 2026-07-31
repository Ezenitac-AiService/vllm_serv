# Interface Contract: `src.core.firewall_manager.FirewallManager`

**Feature Branch**: `039-seed-pack-sudo-firewall-migration`  
**Artifact Path**: `specs/039-seed-pack-sudo-firewall-migration/contracts/firewall_manager_contract.md`  

---

## 1. Class API Contract

```python
class FirewallManager:
    @staticmethod
    def detect_firewall_system() -> str:
        """
        Detects installed & active OS firewall management utility.
        Returns: "ufw" | "firewalld" | "nftables" | "iptables" | "unknown"
        """

    @staticmethod
    def is_port_allowed_in_os(port: int, protocol: str = "tcp") -> bool:
        """
        Non-mocked OS firewall status detector.
        Parses actual OS firewall command output (ufw status, firewall-cmd, etc.).
        Returns True if rule exists or firewall is inactive.
        """

    @staticmethod
    def verify_real_socket_connectivity(host: str = "127.0.0.1", port: int = 8081, timeout_s: float = 3.0) -> RealSocketResult:
        """
        Performs actual physical TCP socket connection probe (Anti-Mock).
        """

    def allow_port(self, port: int, protocol: str = "tcp") -> FirewallStatusInfo:
        """
        Attempts to allow port via detected firewall system (ufw/firewalld/nftables/iptables).
        If sudo fails or is restricted, returns FirewallStatusInfo with requires_sudo=True
        and guide_message containing clear remediation command.
        """

    def generate_fallback_script(self, target_path: str = "scripts/configure_firewall.sh") -> str:
        """
        Generates executable standalone helper shell script for manual/sudo execution.
        Returns absolute path to generated script.
        """
```

---

## 2. Anti-Mock Discipline Rules (Constitution v1.3.1)

- Unit and integration tests for `FirewallManager` MUST NOT mock `subprocess.run` or `socket.create_connection` when evaluating OS rule status or network connectivity probes in `test_firewall_manager_real.py`.
- Non-mocked tests query actual Linux kernel firewall state and host sockets.

# Interface Contract: `scripts/configure_firewall.sh`

**Feature Branch**: `039-seed-pack-sudo-firewall-migration`  
**Artifact Path**: `specs/039-seed-pack-sudo-firewall-migration/contracts/configure_firewall_sh_contract.md`  

---

## 1. File Specification

- **Path**: `scripts/configure_firewall.sh`
- **Permissions**: Executable (`chmod +x scripts/configure_firewall.sh`)
- **Generation Source**: Generated dynamically by `setup.sh` or packaged in `make_seed_pack.sh`.

---

## 2. Synopsis & Capabilities

```bash
sudo ./scripts/configure_firewall.sh [PORTS...]
```

### Default Target Ports
If no arguments are supplied, defaults to `8081` (Dashboard/OpenAI API) and `8089` (Backend llama.cpp).

---

## 3. Detection & Rule Execution Contract

The script MUST execute the appropriate rule addition command depending on detected OS firewall backend:

1. **ufw**:
   ```bash
   ufw allow 8081/tcp
   ufw allow 8089/tcp
   ```
2. **firewalld**:
   ```bash
   firewall-cmd --permanent --add-port=8081/tcp
   firewall-cmd --permanent --add-port=8089/tcp
   firewall-cmd --reload
   ```
3. **nftables**:
   ```bash
   nft add rule inet filter input tcp dport { 8081, 8089 } accept
   ```
4. **iptables**:
   ```bash
   iptables -C INPUT -p tcp --dport 8081 -j ACCEPT 2>/dev/null || iptables -A INPUT -p tcp --dport 8081 -j ACCEPT
   iptables -C INPUT -p tcp --dport 8089 -j ACCEPT 2>/dev/null || iptables -A INPUT -p tcp --dport 8089 -j ACCEPT
   ```

---

## 4. Exit Codes

- `0`: All specified firewall rules successfully applied or firewall is inactive.
- `1`: Required root/sudo privileges missing when running script.

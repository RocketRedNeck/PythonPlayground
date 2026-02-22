# -*- coding: utf-8 -*-
"""
Linux macvlan setup for a single asset using pyroute2.

This mirrors the core logic of setup_emulator.sh for one device.
Requires root privileges and Linux.

Usage Examples:
    # Setup asset with host octet 10 (IP: 192.168.1.10)
    sudo python network_setup_single_asset.py --config emulator.conf --host-octet 10
    
    # Setup with custom macvlan interface name
    sudo python network_setup_single_asset.py --config emulator.conf --host-octet 10 --macvlan-name asset1
    
    # Setup for Pi-2 with different MAC vendor prefix
    sudo python network_setup_single_asset.py --config emulator.conf --host-octet 33 --pi-id 2
"""
from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

try:
    from pyroute2 import IPRoute
except ImportError as exc:  # pragma: no cover - import-time check
    raise ImportError("pyroute2 is required for macvlan setup") from exc


@dataclass
class SingleAssetConfig:
    network_interface: str
    base_ip: str
    host_octet: int
    mac_vendor: str
    macvlan_name: str = "macvlan1"
    prefix_len: int = 16
    avahi_enabled: bool = False
    device_name: Optional[str] = None
    announce_arp: bool = True

    @property
    def full_ip(self) -> str:
        return f"{self.base_ip}.{self.host_octet}"


class NetworkSetupError(RuntimeError):
    pass


def _run_cmd(args: list[str]) -> None:
    subprocess.run(args, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def _require_linux_root() -> None:
    if platform.system().lower() != "linux":
        raise NetworkSetupError("This setup only supports Linux.")
    geteuid = getattr(os, "geteuid", None)
    if geteuid is None or geteuid() != 0:
        raise NetworkSetupError("Root privileges are required for macvlan setup.")


def _set_sysctl() -> None:
    _run_cmd(["sysctl", "-w", "net.ipv4.conf.all.arp_ignore=1"])
    _run_cmd(["sysctl", "-w", "net.ipv4.conf.all.arp_announce=2"])


def _arp_announce(interface_name: str, ip_addr: str) -> None:
    if shutil.which("arping") is None:
        raise NetworkSetupError("arping is required to announce ARP entries.")
    _run_cmd(["arping", "-c", "2", "-f", "-A", "-I", interface_name, ip_addr])
    _run_cmd(["arping", "-c", "2", "-f", "-U", "-I", interface_name, ip_addr])


def _avahi_publish(ip_addr: str, device_name: str) -> None:
    if shutil.which("avahi-publish") is None:
        raise NetworkSetupError("avahi-publish is required for mDNS advertisement.")
    _run_cmd(["avahi-publish", "-a", f"{device_name}.local", ip_addr])


def setup_single_asset(config: SingleAssetConfig) -> str:
    """
    Create a macvlan interface, assign IP/MAC, and optionally announce via mDNS/ARP.

    Steps performed:
      1. Verify Linux OS and root privileges
      2. Set sysctl arp_ignore and arp_announce
      3. Create macvlan interface linked to parent (e.g., eth0)
      4. Delete any existing interface with same name
      5. Assign custom MAC address to macvlan (vendor + host_octet)
      6. Assign static IP to macvlan and bring it up
      7. Optionally publish via mDNS (avahi-publish)
      8. Force ARP announcements (arping -A and -U)

    Returns the configured IP address.
    
    Example:
        config = SingleAssetConfig(
            network_interface="eth0",
            base_ip="192.168.1",
            host_octet=10,
            mac_vendor="00:1C:42:01",
            macvlan_name="asset1",
        )
        ip = setup_single_asset(config)  # Returns "192.168.1.10"
    """
    _require_linux_root()
    _set_sysctl()

    ipr = IPRoute()
    try:
        parent_links = ipr.link_lookup(ifname=config.network_interface)
        if not parent_links:
            raise NetworkSetupError(f"Interface not found: {config.network_interface}")
        parent_index = parent_links[0]

        existing = ipr.link_lookup(ifname=config.macvlan_name)
        if existing:
            ipr.link("del", index=existing[0])

        ipr.link(
            "add",
            ifname=config.macvlan_name,
            kind="macvlan",
            link=parent_index,
            macvlan_mode="bridge",
        )

        local_id = config.host_octet
        mac = f"{config.mac_vendor}:{(local_id // 256):02x}:{(local_id % 256):02x}"
        link_idx = ipr.link_lookup(ifname=config.macvlan_name)[0]
        ipr.link("set", index=link_idx, address=mac)
        ipr.addr("add", index=link_idx, address=config.full_ip, prefixlen=config.prefix_len)
        ipr.link("set", index=link_idx, state="up")

    finally:
        ipr.close()

    if config.avahi_enabled:
        device_name = config.device_name or f"device-{config.host_octet:03d}"
        _avahi_publish(config.full_ip, device_name)

    if config.announce_arp:
        _arp_announce(config.network_interface, config.full_ip)

    return config.full_ip


def load_config_file(config_path: str | Path) -> dict[str, str]:
    """
    Load config from a bash-style .conf file with KEY=VALUE pairs.
    
    Handles quoted values and strips comments (lines starting with #).
    
    Example file (emulator.conf):
        PI_ID=1
        EMU_BASE_IP="192.168.1"
        NETWORK_INTERFACE="eth0"
        MAC_VENDOR="00:1C:42:${PI_ID}"
        AVAHI_ENABLED=true
    
    Returns a dict like:
        {"PI_ID": "1", "EMU_BASE_IP": "192.168.1", ...}
    """
    config = {}
    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            config[key] = val
    
    return config


def config_from_file(
    config_path: str | Path,
    host_octet: int,
    macvlan_name: str = "macvlan1",
    pi_id: Optional[int] = None,
) -> SingleAssetConfig:
    """
    Build a SingleAssetConfig from a conf file and host_octet.
    
    Reads emulator.conf-style format (KEY=VALUE pairs) and substitutes PI_ID
    in MAC_VENDOR if needed (e.g., "00:1C:42:${PI_ID}" -> "00:1C:42:01").
    
    Args:
        config_path: Path to emulator.conf or similar.
        host_octet: The IP host octet (4th octet) for this asset.
        macvlan_name: Override the macvlan interface name.
        pi_id: Override PI_ID from config (if substitution needed in MAC_VENDOR).
    
    Returns:
        Configured SingleAssetConfig ready for setup_single_asset().
    
    Example:
        # From emulator.conf with EMU_BASE_IP=192.168.1, MAC_VENDOR=00:1C:42:${PI_ID}
        config = config_from_file("emulator.conf", host_octet=10, pi_id=1)
        # Result: SingleAssetConfig(base_ip="192.168.1", host_octet=10,
        #                           mac_vendor="00:1C:42:01", full_ip="192.168.1.10")
    """
    conf = load_config_file(config_path)
    
    pi_id = pi_id or int(conf.get("PI_ID", "1"))
    base_ip = conf.get("EMU_BASE_IP", "192.168.1")
    network_interface = conf.get("NETWORK_INTERFACE", "eth0")
    mac_vendor = conf.get("MAC_VENDOR", "00:1C:42:01")
    avahi_enabled = conf.get("AVAHI_ENABLED", "false").lower() == "true"
    
    mac_vendor = mac_vendor.replace("${PI_ID}", str(pi_id)).replace(f"${{PI_ID}}", str(pi_id))
    
    device_name = f"device-{host_octet:03d}"
    
    return SingleAssetConfig(
        network_interface=network_interface,
        base_ip=base_ip,
        host_octet=host_octet,
        mac_vendor=mac_vendor,
        macvlan_name=macvlan_name,
        avahi_enabled=avahi_enabled,
        device_name=device_name,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Setup a single macvlan asset for emulation.",
        epilog="""
Examples:
  # Setup asset with host octet 10 (IP: 192.168.1.10, reads from emulator.conf)
  sudo python %(prog)s --config emulator.conf --host-octet 10
  
  # Setup with custom macvlan interface name (e.g., for multiple assets)
  sudo python %(prog)s --config emulator.conf --host-octet 10 --macvlan-name asset1
  
  # Setup for Pi-2 with different MAC vendor prefix from config
  sudo python %(prog)s --config emulator.conf --host-octet 33 --pi-id 2
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--config",
        type=str,
        default="emulator.conf",
        help="Path to emulator.conf (default: emulator.conf)",
    )
    parser.add_argument(
        "--host-octet",
        type=int,
        required=True,
        help="IP host octet (4th octet) for this asset (e.g., 10 for 192.168.1.10)",
    )
    parser.add_argument(
        "--macvlan-name",
        type=str,
        default="macvlan1",
        help="Name for the macvlan interface (default: macvlan1)",
    )
    parser.add_argument(
        "--pi-id",
        type=int,
        default=None,
        help="Override PI_ID from config (for MAC vendor substitution)",
    )
    
    args = parser.parse_args()
    
    try:
        config = config_from_file(
            args.config,
            args.host_octet,
            args.macvlan_name,
            args.pi_id,
        )
        ip_addr = setup_single_asset(config)
        print(f"✓ Setup complete: {config.macvlan_name} @ {ip_addr}")
    except NetworkSetupError as e:
        print(f"✗ Setup failed: {e}")
        exit(1)
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        exit(1)


if __name__ == "__main__":
    main()

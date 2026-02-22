#!/bin/bash

# Load config
source ./emulator.conf

echo "Setting up $NUM_DEVICES devices on Pi-$PI_ID..."

# Calculate IP range for this Pi
START_IP=$(( (PI_ID - 1) * NUM_DEVICES + 1 ))                           # Relative to base (1-32 for Pi-1, 33-64 for Pi-2, etc.)
START_NUM=$START_IP
END_NUM=$((START_IP + NUM_DEVICES - 1))

# Tools to announce the devices on the network so that they are visible to other devices
# Should be done at least once per RPi setup
# sudo apt update
# sudo apt install avahi-daemon avahi-utils
AVAHI_ENABLED=${AVAHI_ENABLED:-false}
if [[ "$AVAHI_ENABLED" == "true" ]]; then
  sudo systemctl restart avahi-daemon
  sleep 2 # Give it a moment to restart even if we will take some more time below
fi

# make sure that ARP announcements are automatic
# even if we will force it. I.e., we have multiple
# IP address on one NIC and don't want any "weird"
# behavior due to that fact and lack of network awareness
# If we want this to be permenant then add it to the /etc/sysctl.conf
# file starting from "net.ipv4..." and make sure to 'sudo sysctl -p'
# to ensure it has been run at least once.
# Otherwise, just perform this in the script here
# to avoid changing the base behavior until we want it.
sudo sysctl -w net.ipv4.conf.all.arp_ignore=1
sudo sysctl -w net.ipv4.conf.all.arp_announce=2

# Clean out any of the VLANs from a previous configuration run
echo Clearing all VLANs
for i in $(seq $START_NUM $END_NUM); do
  local_id=$((i - START_NUM + 1))
  mac=$(ip link show macvlan$local_id | grep 'link/ether' | awk '{print $2}')
  if [[ -n "$mac" ]]; then
    echo "CLEARING macvlan$local_id @ MAC: $mac @ IP: $BASE_IP.$i"  
    sudo ip link delete macvlan$local_id 2>/dev/null
  fi
done

# configure ip address we will claim statically on
# the one NIC at eth0.
# Each IP address will also be on a unique MAC so
# it appears truly unique.
# Really want 128 devices but Raspberry Pi may not tolerate more than 50
# The Broadcom Ethernet driver on Raspberry Pi OS has limitations:
# - Driver constraint - Broadcom's genet driver wasn't designed for hundreds of virtual interfaces
# - Interrupt handling - Each interface needs kernel resources
# - Memory pressure - 128 interfaces consume significant kernel memory
# - System I/O overhead - Pi's ARMv8 SoC can't handle the interrupt load
#
# Beyond ~50 interfaces, the driver becomes unstable and stops creating new ones.
# Configuration files should limit to 32 devices per Pi to avoid hitting this limit and ensure stability.

for i in $(seq $START_NUM $END_NUM); do
  # Create a macvlan (virtual LAN) with a unique MAC address
  local_id=$((i - START_NUM + 1))
  sudo ip link add macvlan$local_id link $NETWORK_INTERFACE type macvlan mode bridge

  # If we need to model some specific MAC address range
  # then uncomment the following
  # Set custom MAC (02:00:00:0X:YY:ZZ where X=Pi ID, YY:ZZ=device ID)
  # NOTE: 02, 06, 0A are all valid for the first byte of a locally administered MAC address
  # NOTE: Nokia/Alcatel range "00:14:69:%02x:%02x:%02x"
  # NOTE: Cisco range"00:00:0C:%02x:%02x:%02x"
  printf -v mac "$MAC_VENDOR:%02x:%02x" $((local_id/256)) $((local_id%256))
  sudo ip link set macvlan$local_id address $mac

  # Assign static IP
  full_ip="$BASE_IP.$i"
  sudo ip addr add $full_ip/16 dev macvlan$local_id

  # Assign to IP addresses to the VLAN MAC
  sudo ip link set macvlan$local_id up


  # Advertise via mDNS
  if [[ "$AVAHI_ENABLED" == "true" ]]; then
    device_name="device-$(printf "%03d" $i)"
    sudo avahi-publish -a "$device_name.local" $full_ip > /dev/null 2>&1 &
    sleep 0.05
  fi

  mac=$(ip link show macvlan$local_id | grep 'link/ether' | awk '{print $2}')
  echo "macvlan$local_id @ MAC: $mac @ IP: $full_ip"

  # Force an ARP ananouncement to make the device visible on the network immediately
  sudo arping -c 2 -f -A -I $NETWORK_INTERFACE $full_ip

  # Force an ARP update to ensure the IP is visible on the network immediately with the correct MAC address
  sudo arping -c 2 -f -U -I $NETWORK_INTERFACE $full_ip
done

wait
echo "Setup complete: $NUM_DEVICES devices on Pi-$PI_ID (IPs: $BASE_IP.$START_NUM to $BASE_IP.$END_NUM)"

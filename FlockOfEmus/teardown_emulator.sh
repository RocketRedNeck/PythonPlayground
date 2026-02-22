#!/bin/bash

# Load config
source ./emulator.conf

MGMT_CONN_NAME=${MGMT_CONN_NAME:-"emu-mgmt"}

# Calculate IP range for this Pi
START_IP=$(( (PI_ID - 1) * NUM_DEVICES + 1 ))
START_NUM=$START_IP
END_NUM=$((START_IP + NUM_DEVICES - 1))

# Clean out any of the VLANs from a previous configuration run
echo Clearing all VLANs
for i in $(seq $START_NUM $END_NUM); do
  local_id=$((i - START_NUM + 1))
  mac=$(ip link show macvlan$local_id | grep 'link/ether' | awk '{print $2}')
  if [[ -n "$mac" ]]; then
    echo "CLEARING macvlan$local_id @ MAC: $mac @ IP: $EMU_BASE_IP.$i"
    sudo ip link delete macvlan$local_id 2>/dev/null
  fi
done

# Revert ARP tuning to defaults
sudo sysctl -w net.ipv4.conf.all.arp_ignore=0
sudo sysctl -w net.ipv4.conf.all.arp_announce=0

# Remove NetworkManager connection if it exists
if command -v nmcli >/dev/null 2>&1; then
  if systemctl is-active --quiet NetworkManager; then
    if nmcli -t -f NAME con show | grep -Fxq "$MGMT_CONN_NAME"; then
      sudo nmcli con down "$MGMT_CONN_NAME"
      sudo nmcli con delete "$MGMT_CONN_NAME"
      echo "Removed NetworkManager connection: $MGMT_CONN_NAME"
    else
      echo "No NetworkManager connection named $MGMT_CONN_NAME found."
    fi
  else
    echo "NetworkManager is not active; nothing to revert."
  fi
else
  echo "nmcli not found; nothing to revert."
fi

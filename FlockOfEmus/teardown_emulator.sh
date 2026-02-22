#!/bin/bash

# Load config
source ./emulator.conf

MGMT_MACVLAN_NAME=${MGMT_MACVLAN_NAME:-"mgmt"}
MGMT_GATEWAY=${MGMT_GATEWAY:-""}

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

# Remove default route if it was set
if [[ -n "$MGMT_GATEWAY" ]]; then
  sudo ip route del default via "$MGMT_GATEWAY" dev "$MGMT_MACVLAN_NAME" 2>/dev/null
  echo "Removed default route via $MGMT_GATEWAY"
fi

# Remove management macvlan interface
echo "Clearing management interface $MGMT_MACVLAN_NAME"
sudo ip link delete "$MGMT_MACVLAN_NAME" 2>/dev/null
echo "Teardown complete: All macvlan interfaces removed"

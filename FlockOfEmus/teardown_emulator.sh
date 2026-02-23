#!/bin/bash

# Teardown emulator macvlan devices

# Load config
source ./emulator.conf

# Calculate IP range for this Pi
START_IP=$(( (PI_ID - 1) * NUM_DEVICES + 1 ))
START_NUM=$START_IP
END_NUM=$((START_IP + NUM_DEVICES - 1))

echo "Tearing down emulator devices on Pi-$PI_ID..."

# Clean out any of the VLANs from a previous configuration run
echo Clearing all emulator VLANs
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

echo "Emulator teardown complete on Pi-$PI_ID"

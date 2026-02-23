#!/bin/bash

# Teardown management macvlan interface

# Load config
source ./emulator.conf

MGMT_MACVLAN_NAME=${MGMT_MACVLAN_NAME:-"mgmt"}
MGMT_GATEWAY=${MGMT_GATEWAY:-""}

echo "Tearing down management interface on Pi-$PI_ID..."

# Remove default route if it was set
if [[ -n "$MGMT_GATEWAY" ]]; then
  sudo ip route del default via "$MGMT_GATEWAY" dev "$MGMT_MACVLAN_NAME" 2>/dev/null
  echo "Removed default route via $MGMT_GATEWAY"
fi

# Remove management macvlan interface
echo "Clearing management interface $MGMT_MACVLAN_NAME"
sudo ip link delete "$MGMT_MACVLAN_NAME" 2>/dev/null

echo "Management teardown complete on Pi-$PI_ID"

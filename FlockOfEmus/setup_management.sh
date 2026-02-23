#!/bin/bash

# Setup management macvlan interface for SSH/VNC access
# This should be run first, before setup_emulator.sh

# Load config
source ./emulator.conf

echo "Setting up management interface on Pi-$PI_ID..."

MGMT_PREFIX_LEN=${MGMT_PREFIX_LEN:-16}
MGMT_MACVLAN_NAME=${MGMT_MACVLAN_NAME:-"mgmt"}
MGMT_GATEWAY=${MGMT_GATEWAY:-""}

# Create management macvlan interface
echo "Setting up management interface $MGMT_MACVLAN_NAME..."

# Delete if it already exists
sudo ip link delete "$MGMT_MACVLAN_NAME" 2>/dev/null

# Create macvlan for management
sudo ip link add "$MGMT_MACVLAN_NAME" link "$NETWORK_INTERFACE" type macvlan mode bridge

# Set MAC address for management (using MAC_VENDOR with host_octet 0)
printf -v mgmt_mac "$MAC_VENDOR:00:00"
sudo ip link set "$MGMT_MACVLAN_NAME" address "$mgmt_mac"

# Bring up the interface
sudo ip link set "$MGMT_MACVLAN_NAME" up

# Add enabled management IP addresses
declare -A mgmt_subnets=(["10"]="MGMT_BASE_IP_10" ["172"]="MGMT_BASE_IP_172" ["192"]="MGMT_BASE_IP_192")
declare -A mgmt_enabled=(["10"]="MGMT_BASE_IP_10_ENABLED" ["172"]="MGMT_BASE_IP_172_ENABLED" ["192"]="MGMT_BASE_IP_192_ENABLED")

for prefix in 10 172 192; do
  base_var=${mgmt_subnets[$prefix]}
  enabled_var=${mgmt_enabled[$prefix]}
  enabled=${!enabled_var:-false}
  
  if [[ "$enabled" == "true" ]]; then
    base_ip=${!base_var}
    mgmt_ip="${base_ip}.$((PI_ID + 1))"
    sudo ip addr add "${mgmt_ip}/${MGMT_PREFIX_LEN}" dev "$MGMT_MACVLAN_NAME"
    echo "Management IP added: ${mgmt_ip}/${MGMT_PREFIX_LEN}"
  fi
done

echo "Management interface ready: $MGMT_MACVLAN_NAME @ MAC: $mgmt_mac"

# Set default route if gateway is configured
# Note: Gateway routing works best with the enabled 10.x subnet; other subnets are for SSH/VNC access only
if [[ -n "$MGMT_GATEWAY" ]]; then
  sudo ip route add default via "$MGMT_GATEWAY" dev "$MGMT_MACVLAN_NAME"
  echo "Default route set via $MGMT_GATEWAY on $MGMT_MACVLAN_NAME"
fi

echo "Management setup complete on Pi-$PI_ID"

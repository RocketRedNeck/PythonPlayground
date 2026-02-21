source ~/emulator.conf 2>/dev/null

BASE_IP=${BASE_IP:-"192.168.1"}
NETWORK_INTERFACE=${NETWORK_INTERFACE:-"eth0"}

for i in $(seq 1 128); do
  ip="$BASE_IP.$i"
  name="device-$(printf '%03d' $i)"

  if ping -c 1 -W 1 "$ip" > /dev/null 2>&1; then
    # Force ARP resolution and parse MAC directly from arping output
    ip neigh flush "$ip" > /dev/null 2>&1
    mac=$(arping -c 2 -w 2 -I "$NETWORK_INTERFACE" "$ip" 2>/dev/null | awk '/reply from/ {print $4; exit}')
    if [ -z "$mac" ]; then
      mac=$(ip -4 neigh show "$ip" dev "$NETWORK_INTERFACE" | awk '{print $5}')
    fi
    if [ -n "$mac" ]; then
      echo "$name: OK MAC=$mac"
    else
      echo "$name: OK MAC=UNKNOWN"
    fi
  else
    echo "$name: FAIL"
  fi
done
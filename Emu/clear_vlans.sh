#!/bin/bash

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
for i in $(seq 1 128); do
  mac=$(ip link show macvlan$i | grep 'link/ether' | awk '{print $2}')
  if [[ -n "$mac" ]]; then
    echo "CLEARING macvlan$i @ MAC: $mac @ IP: 192.168.1.$i"  
    sudo ip link delete macvlan$i 2>/dev/null
  fi
done


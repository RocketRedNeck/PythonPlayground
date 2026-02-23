#!/bin/bash

# Teardown all emulator and management interfaces

# Load config
source ./emulator.conf

echo "Tearing down all emulator and management interfaces on Pi-$PI_ID..."

# Teardown emulator devices
./teardown_emulator.sh

# Teardown management interface
./teardown_management.sh

echo "Complete teardown on Pi-$PI_ID finished"

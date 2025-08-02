#!/bin/bash

source "$CATKIN_WS/install/setup.bash"

# Start mosquitto broker
/usr/sbin/mosquitto &

# Print a message to help users
echo "ROS environment initialized. If you're running this on Windows:"
echo "1. Make sure you have an X server running (like VcXsrv or Xming)"
echo "2. Ensure your X server allows connections from network clients"
echo "3. Set DISPLAY environment variable correctly in your Docker run command"

exec "$@"
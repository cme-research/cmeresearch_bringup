#!/bin/bash

source "$CATKIN_WS/install/setup.bash"

#start mosquitto broker
/usr/sbin/mosquitto &

export __NV_PRIME_RENDER_OFFLOAD=1
export __GLX_VENDOR_LIBRARY_NAME=nvidia


exec "$@"

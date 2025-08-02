#!/bin/bash

source "$CATKIN_WS/install/setup.bash"

#start mosquitto broker
/usr/sbin/mosquitto &


exec "$@"

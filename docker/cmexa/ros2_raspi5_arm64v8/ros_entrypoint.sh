#!/bin/bash

source "/robot/ros2_ws/install/setup.bash"

/usr/bin/brickd &

export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export ROS_DOMAIN_ID=0

exec "$@"

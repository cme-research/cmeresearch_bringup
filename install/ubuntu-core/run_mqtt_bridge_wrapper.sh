#!/bin/bash

docker run --rm -it --network="host" cmerobotics/mqtt-bridge-wrapper-arm32v7:0.1 roslaunch mqtt_bridge_wrapper mqtt_bridge.launch

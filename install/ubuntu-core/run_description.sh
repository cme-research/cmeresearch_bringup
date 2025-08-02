#!/bin/bash

docker run --rm -it --network="host" cmerobotics/unico-description-arm32v7:1.0 roslaunch unico_description description.launch

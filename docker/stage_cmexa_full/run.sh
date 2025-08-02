# ldlidar-rviz Dockerfile

docker run -it --rm -e NVIDIA_VISIBLE_DEVICES=all -e NVIDIA_DRIVER_CAPABILITIES=all  --gpus all -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY --network="host" --privileged --device-cgroup-rule='c 189:* rmw' -v /dev/input/js0:/dev/input/js0 -v /home/cme/data:/robot/data cmexa/stagesimulation:1.0
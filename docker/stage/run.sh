# ldlidar-rviz Dockerfile

docker run -it --rm -e NVIDIA_VISIBLE_DEVICES=all -e NVIDIA_DRIVER_CAPABILITIES=all  --gpus all -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY --network="host" unico/stagesimulation:1.0
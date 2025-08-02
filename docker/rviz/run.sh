# ldlidar-rviz Dockerfile

docker run -it -e NVIDIA_VISIBLE_DEVICES=all -e NVIDIA_DRIVER_CAPABILITIES=all  --gpus all -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY --network="host" unico/ldlidar-rviz:1.0
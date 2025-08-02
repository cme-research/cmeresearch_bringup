# tinkerforge brickd Dockerfile

docker run -it --rm --network="host" --privileged --device-cgroup-rule='c 189:* rmw' -v /dev/bus/usb:/dev/bus/usb unico/brickd:1.0
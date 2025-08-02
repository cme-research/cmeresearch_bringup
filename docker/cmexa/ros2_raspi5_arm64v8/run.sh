# ros2 raspi5 cmexa Dockerfile

docker run -it --rm --name cmexa-robot --network="host"  --privileged --device-cgroup-rule='c 189:* rmw' -v /dev/input/js1:/dev/input/js1 cmeresearch/cmexa:1.0

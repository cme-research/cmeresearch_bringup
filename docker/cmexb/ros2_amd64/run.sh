# cmexa Dockerfile

docker run -it --rm --name cmexb-robot --network="host"  --privileged --device-cgroup-rule='c 189:* rmw' -v /dev/input/js0:/dev/input/js0 cmeresearch/cmexb:1.0

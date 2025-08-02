# cmexa Dockerfile

docker run -it --rm --name cmexa-robot --network="host"  --privileged --device-cgroup-rule='c 189:* rmw' -v /dev/input/js0:/dev/input/js0 cmeresearch/cmexa:1.0

# cmexa Dockerfile

docker run -it --rm --name cmexamini-robot --network="host"  --privileged --device-cgroup-rule='c 189:* rmw' -v /dev/input/js0:/dev/input/js0 cmeresearch/cmexamini:1.0

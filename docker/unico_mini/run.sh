# unico-mini Dockerfile

docker run -it --rm --name unico-robot --network="host"  --privileged --device-cgroup-rule='c 189:* rmw' -v /dev/input/js0:/dev/input/js0 unico/mini:1.0
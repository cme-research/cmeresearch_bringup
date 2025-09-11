# ros2 raspi5 cmexa Dockerfile

docker run -it \
  --rm --name cmexa-robot \
  --network="host" \
  --privileged \
  --device-cgroup-rule='c 189:* rmw' \
  -v /dev/input/js0:/dev/input/js0 \
  --device /dev/input \
  --group-add $(getent group input | cut -d: -f3) \
  cmeresearch/cmexa:1.0

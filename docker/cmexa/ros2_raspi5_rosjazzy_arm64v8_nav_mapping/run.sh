# ros2 raspi5 cmexa Dockerfile

docker run -it --rm \
  --name cmexa-robot \
  --network="host" \
  --privileged \
  --ipc=host \
  -v /dev/input:/dev/input \
  --device-cgroup-rule='c 189:* rmw' \
  --group-add $(getent group input | cut -d: -f3) \
  cmeresearch/cmexa:1.0


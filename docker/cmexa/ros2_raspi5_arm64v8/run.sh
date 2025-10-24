# ros2 raspi5 cmexa Dockerfile

docker run -it \
  --name cmexa-robot \
  --network="host" \
  --restart=always \
  --privileged \
  --ipc=host \
  -v /dev/input:/dev/input \
  --device-cgroup-rule='c 189:* rmw' \
  --group-add $(getent group input | cut -d: -f3) \
  cmeresearch/cmexa:1.0


# ros2 raspi5 cmexa Dockerfile

docker run -it \
  --rm --name cmexa-teleop \
  --network="host" \
  --ipc=host \
  -v /dev/input:/dev/input \
  --device-cgroup-rule='c 189:* rmw' \
  --group-add $(getent group input | cut -d: -f3) \
  cmeresearch/cmexa_teleop:1.0

# ros2 raspi5 cmexaiii Dockerfile

docker run -it --rm \
  --name cmexaiii-robot \
  --network="host" \
  --privileged \
  --ipc=host \
  -v /dev/input:/dev/input \
  --device-cgroup-rule='c 189:* rmw' \
  --group-add $(getent group input | cut -d: -f3) \
  cmeresearch/cmexaiii:1.0


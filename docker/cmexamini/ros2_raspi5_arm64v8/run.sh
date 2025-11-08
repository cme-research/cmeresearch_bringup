# ros2 raspi5 cmexamini Dockerfile

docker run -it \
  --rm \
  --name cmexamini-robot \
  --network="host" \
  --privileged \
  --ipc=host \
  -v /dev/input:/dev/input \
  --device-cgroup-rule='c 189:* rmw' \
  --group-add $(getent group input | cut -d: -f3) \
  cmeresearch/cmexamini:1.0


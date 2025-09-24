# ros2 raspi5 cmexa Dockerfile

docker run -it \
  --rm --name cmexa-robot \
  --network="host" \
  --privileged \
  --device /dev/input/js0 \
  cmeresearch/cmexa:1.0

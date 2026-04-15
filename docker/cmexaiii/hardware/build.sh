# Build CMEXAIII hardware image (run from workspace root: ~/ros2_ws/)

docker build . --tag cmeresearch/cmexaiii-hardware:1.0 \
  -f cmeresearch_bringup/docker/cmexaiii/hardware/Dockerfile

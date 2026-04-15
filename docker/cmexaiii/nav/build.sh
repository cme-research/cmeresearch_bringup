# Build CMEXAIII nav image (run from workspace root: ~/ros2_ws/)

docker build . --tag cmeresearch/cmexaiii-nav:1.0 \
  -f cmeresearch_bringup/docker/cmexaiii/nav/Dockerfile

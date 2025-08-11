# Start from a base image of Ubuntu 24
FROM ubuntu:noble

LABEL maintainer="Christian Ehrmann"
LABEL version="0.1"
LABEL description="CMEXA Brickd for Tinkerforge Bindings"

# USE BASH
SHELL ["/bin/bash", "-c"]

ENV DEBIAN_FRONTEND=noninteractive
RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

# upgrade and install build tools (catkin)
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends apt-utils \
    && apt-get install -y --no-install-recommends mesa-utils

RUN apt-get update \
    && apt-get install wget libusb-1.0-0 libgpiod2 procps systemd -y \
    && wget https://download.tinkerforge.com/apt/$(. /etc/os-release; echo $ID)/tinkerforge.asc -q -O - | tee /etc/apt/trusted.gpg.d/tinkerforge.asc > /dev/null \
    && echo "deb https://download.tinkerforge.com/apt/$(. /etc/os-release; echo $ID $VERSION_CODENAME) main" | tee /etc/apt/sources.list.d/tinkerforge.list \
    && apt-get update \
    && apt-get install brickd -y


RUN rm -rf /var/lib/apt/lists/*

# Always source ros_entrypoint.sh when launching bash (e.g. when attaching to container)
RUN echo "source /ros_entrypoint.sh" >> /root/.bashrc

COPY ./unico_bringup/docker/brickd/ros_entrypoint.sh /
RUN chmod +x /ros_entrypoint.sh

# correct spidev
COPY ./cmeresearch_bringup/docker/brickd/brickd.conf /etc/

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["bash"]

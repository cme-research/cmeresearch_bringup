# Start from a base image of Ubuntu 18.04
FROM ubuntu:18.04

LABEL maintainer="Christian Ehrmann"
LABEL version="0.1"
LABEL description="Unico Stage Simulation with RViz for Windows"

# USE BASH
SHELL ["/bin/bash", "-c"]

ENV DEBIAN_FRONTEND=noninteractive
RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

# upgrade and install build tools (catkin)
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends apt-utils \
    && apt-get install -y --no-install-recommends mesa-utils

# Install X11 utilities for display forwarding
RUN apt-get update && apt-get install -y \
    x11-apps \
    x11-utils \
    libgl1-mesa-glx \
    libgl1-mesa-dri

# workaround for snapshot keyring issue EOF distro
RUN apt-get update && apt-get install -y curl
RUN curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
RUN echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | tee /etc/apt/sources.list.d/ros.list > /dev/null

# Update the package repository and install the required packages
RUN apt-get update && apt-get install -y \
  ros-melodic-desktop-full \
  ros-melodic-image-transport \
  ros-melodic-image-transport-plugins \
  ros-melodic-pcl-ros \
  ros-melodic-libg2o \
  python-catkin-tools \
  python-rosdep \
  ros-melodic-rosbridge-suite

# Install mosquitto mqtt broker for navigation commands and odometry feedback
RUN apt-get update && apt-get install -y \
    mosquitto

# install the missing dependencies for ros-mqtt-bridge manually
RUN apt-get update && apt-get install -y python-pip
RUN pip install inject==3.5.4
RUN pip install paho-mqtt

ENV ROS_DISTRO=melodic
# Setup the environment variables to fix QT bug
ENV QT_X11_NO_MITSHM=1

# Create local catkin workspace
ENV CATKIN_WS=/robot/catkin_ws

#### unico_bringup ###
RUN mkdir -p /robot/catkin_ws/src/unico_bringup
COPY ./unico_bringup /robot/catkin_ws/src/unico_bringup

#### unico_description ###
RUN mkdir -p /robot/catkin_ws/src/unico_description
COPY ./unico_description /robot/catkin_ws/src/unico_description

#### unico_stage ###
RUN mkdir -p /robot/catkin_ws/src/unico_stage
COPY ./unico_stage /robot/catkin_ws/src/unico_stage

#### unico_environments ###
RUN mkdir -p /robot/catkin_ws/src/unico_environments
COPY ./unico_environments /robot/catkin_ws/src/unico_environments

# add package specific ros dependencies to workspace
RUN source /opt/ros/melodic/setup.bash \
    && cd /robot/catkin_ws/  \
    && rosdep init \
    && rosdep update --include-eol-distros \
    && rosdep fix-permissions \
    && rosdep install -y -r --from-paths src --ignore-src --rosdistro=melodic -y

RUN source /opt/ros/melodic/setup.bash \
    && cd /robot/catkin_ws/src \
    && catkin_init_workspace \
    && cd .. \
    && catkin config --install \
    && catkin build -DCMAKE_BUILD_TYPE=Release

# just leave install space inside container
RUN cd /robot/catkin_ws/ \
    && rm -rf build \
    && rm -rf devel \
    && rm -rf src

RUN rm -rf /var/lib/apt/lists/*

# Source the ROS environment setup script
RUN echo "source /opt/ros/$ROS_DISTRO/setup.bash" >> /root/.bashrc

# Always source ros_entrypoint.sh when launching bash (e.g. when attaching to container)
RUN echo "source /ros_entrypoint.sh" >> /root/.bashrc

COPY ./unico_bringup/logo.txt /
COPY ./unico_bringup/docker/stage_windows/ros_entrypoint.sh /
RUN chmod +x /ros_entrypoint.sh

ENV ROBOT=ash
ENV ROBOT_ENV=house
ENV ROS_HOSTNAME=localhost

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["roslaunch", "unico_bringup", "sim_robot_only_mqtt.launch"]
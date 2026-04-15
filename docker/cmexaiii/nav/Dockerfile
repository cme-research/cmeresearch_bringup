FROM ros:jazzy-ros-base-noble

LABEL maintainer="Christian Ehrmann"
LABEL version="1.0"
LABEL description="CMEXAIII nav stack: nav2, slam_toolbox. Switch modes via LAUNCH_FILE env var."

SHELL ["/bin/bash", "-c"]

ENV DEBIAN_FRONTEND=noninteractive
RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

RUN apt-get update && apt-get install --no-install-recommends -y \
    build-essential \
    git \
    python3-colcon-common-extensions \
    python3-colcon-mixin \
    python3-rosdep \
    python3-vcstool \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get -y install \
    curl \
    software-properties-common \
    vim \
    wget \
    && rm -rf /var/lib/apt/lists/*

RUN add-apt-repository universe

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y ros-dev-tools python3-rosdep \
    && rm -rf /var/lib/apt/lists/*

# CycloneDDS — required workaround for ROS2 on Raspberry Pi aarch64
RUN apt-get update \
    && apt-get install -y ros-jazzy-rmw-cyclonedds-cpp \
    && rm -rf /var/lib/apt/lists/*

ENV CATKIN_WS=/robot/ros2_ws

#### ROS packages ####
RUN mkdir -p /robot/ros2_ws/src/cmeresearch_bringup
COPY ./cmeresearch_bringup /robot/ros2_ws/src/cmeresearch_bringup

RUN mkdir -p /robot/ros2_ws/src/cmeresearch_msgs
COPY ./cmeresearch_msgs /robot/ros2_ws/src/cmeresearch_msgs

RUN mkdir -p /robot/ros2_ws/src/cmeresearch_environments
COPY ./cmeresearch_environments /robot/ros2_ws/src/cmeresearch_environments

# Install ROS dependencies (nav2_bringup and slam_toolbox come from cmeresearch_bringup's package.xml)
# Skip hardware-specific packages not present in this image
RUN source /opt/ros/jazzy/setup.bash \
    && cd /robot/ros2_ws \
    && apt-get update \
    && rosdep update \
    && rosdep fix-permissions \
    && rosdep install -y -r --from-paths src --ignore-src --rosdistro=jazzy \
       --skip-keys "rviz2 web_video_server" \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update
RUN source /opt/ros/jazzy/setup.bash \
    && cd /robot/ros2_ws \
    && colcon build

RUN cd /robot/ros2_ws \
    && rm -rf build log src

RUN rm -rf /var/lib/apt/lists/*

RUN echo "source /ros_entrypoint.sh" >> /root/.bashrc

COPY ./cmeresearch_bringup/docker/cmexaiii/nav/ros_entrypoint.sh /
RUN chmod +x /ros_entrypoint.sh

COPY ./cmeresearch_bringup/docker/cmexaiii/nav/cyclonedds.xml /

# Volume mount point for maps (used by localization mode)
RUN mkdir -p /maps

ENV ROBOT=cmexaiii

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["ros2", "launch", "cmeresearch_bringup", "cmexaiii_nav_mapping.launch.py"]

FROM arm64v8/ros:rolling-ros-base-noble

LABEL maintainer="Christian Ehrmann"
LABEL version="0.1"
LABEL description="Workspace for CMEXA Robot image for ROS2"

# USE BASH
SHELL ["/bin/bash", "-c"]

RUN apt-get update && apt-get install --no-install-recommends -y \
    build-essential \
    git \
    python3-colcon-common-extensions \
    python3-colcon-mixin \
    python3-rosdep \
    python3-vcstool \
    && rm -rf /var/lib/apt/lists/*

ENV DEBIAN_FRONTEND=noninteractive
RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

# install helpers and requirements
RUN apt-get update && apt-get -y install curl software-properties-common vim wget joystick
RUN add-apt-repository universe
#RUN curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
#RUN echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

# upgrade and install build tools (catkin)
# run all commands in one call is important

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y ros-dev-tools python3-rosdep


# workaround for ros2 not running on raspi aarch64 --> use other dds layer
# make sure to add export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp to sourceing file (or bashrc)
RUN apt-get update \
   && apt-get install -y ros-rolling-rmw-cyclonedds-cpp


# Create local catkin workspace
ENV CATKIN_WS=/robot/ros2_ws

#### cmeresearch_bringup ###
RUN mkdir -p /robot/ros2_ws/src/cmeresearch_bringup
COPY ./cmeresearch_bringup /robot/ros2_ws/src/cmeresearch_bringup

#### cmeresearch_description ###
RUN mkdir -p /robot/ros2_ws/src/cmeresearch_description
COPY ./cmeresearch_description /robot/ros2_ws/src/cmeresearch_description

#### cmeresearch_msgs ###
RUN mkdir -p /robot/ros2_ws/src/cmeresearch_msgs
COPY ./cmeresearch_msgs /robot/ros2_ws/src/cmeresearch_msgs

#### cmeresearch_environments ###
RUN mkdir -p /robot/ros2_ws/src/cmeresearch_environments
COPY ./cmeresearch_environments /robot/ros2_ws/src/cmeresearch_environments

#### cmexa_base ###
RUN mkdir -p /robot/ros2_ws/src/cmexa_base
COPY ./cmexa_base /robot/ros2_ws/src/cmexa_base

#### cmeresearch_stepper_driver ###
RUN mkdir -p /robot/ros2_ws/src/cmeresearch_stepper_driver
COPY ./cmeresearch_stepper_driver /robot/ros2_ws/src/cmeresearch_stepper_driver


#### joy2twist ###
RUN mkdir -p /robot/ros2_ws/src/joy2twist
COPY ./joy2twist /robot/ros2_ws/src/joy2twist

# 3d party non ros specific dependencies
# - tinkerforge bindings
RUN wget https://download.tinkerforge.com/apt/$(. /etc/os-release; echo $ID)/tinkerforge.gpg -q -O - | sudo tee /etc/apt/trusted.gpg.d/tinkerforge.gpg > /dev/null \
    && echo "deb https://download.tinkerforge.com/apt/$(. /etc/os-release; echo $ID $VERSION_CODENAME) main" | sudo tee /etc/apt/sources.list.d/tinkerforge.list \
    && apt-get update \
    && apt-get install python3-tinkerforge -y

# install brickd (tinkerforge daemon)
RUN apt-get update \
    && apt-get install brickd -y

# add package specific ros dependencies to workspace
RUN source /opt/ros/rolling/setup.bash \
    && cd /robot/ros2_ws/  \
#    && rosdep init \
    && rosdep update \
    && rosdep fix-permissions \
    && rosdep install -y -r --from-paths src --ignore-src --rosdistro=rolling -y


RUN apt-get update
RUN source /opt/ros/rolling/setup.bash \
    && cd /robot/ros2_ws \
    && colcon build

# just leave install space inside container
RUN cd /robot/ros2_ws/ \
    && rm -rf build \
    && rm -rf log \
    && rm -rf src

RUN rm -rf /var/lib/apt/lists/*

# Always source ros_entrypoint.sh when launching bash (e.g. when attaching to container)
RUN echo "source /ros_entrypoint.sh" >> /root/.bashrc

COPY ./cmeresearch_bringup/docker/cmexa/ros2_raspi5_arm64v8/ros_entrypoint.sh /
RUN chmod +x /ros_entrypoint.sh

# create folder for file sharing with host system for map data
RUN mkdir /robot/data
COPY ./cmeresearch_environments/envs/laboriii/ /robot/data/


ENV ROBOT=cmexa

ENTRYPOINT ["/ros_entrypoint.sh"]
#CMD ["ros2", "launch", "cmeresearch_bringup", "cmexa_omni.launch.py"]
CMD ["bash"]
FROM ros:melodic-ros-base

LABEL maintainer="Christian Ehrmann"
LABEL version="0.1"
LABEL description="Workspace for Unico Mini Robot image"

# USE BASH
SHELL ["/bin/bash", "-c"]

ENV DEBIAN_FRONTEND=noninteractive
RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

# workaround for snapshot keyring issue EOF distro
RUN rm /etc/apt/sources.list.d/ros1-snapshots.list
RUN apt-get update && apt-get install curl
RUN curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
RUN echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros.list > /dev/null

# upgrade and install build tools (catkin)
# run all commands in one call is important
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends apt-utils \
    && apt-get install -y python-catkin-tools

# Create local catkin workspace
ENV CATKIN_WS=/robot/catkin_ws

#### unico_bringup ###
RUN mkdir -p /robot/catkin_ws/src/unico_bringup
COPY ./unico_bringup /robot/catkin_ws/src/unico_bringup

#### unico_description ###
RUN mkdir -p /robot/catkin_ws/src/unico_description
COPY ./unico_description /robot/catkin_ws/src/unico_description

#### unico_msgs ###
RUN mkdir -p /robot/catkin_ws/src/unico_msgs
COPY ./unico_msgs /robot/catkin_ws/src/unico_msgs

#### ash_base ###
RUN mkdir -p /robot/catkin_ws/src/ash_base
COPY ./ash_base /robot/catkin_ws/src/ash_base

#### tfstepper_driver ###
RUN mkdir -p /robot/catkin_ws/src/tfstepper_driver
COPY ./tfstepper_driver /robot/catkin_ws/src/tfstepper_driver

#### unico_diff_controller ###
RUN mkdir -p /robot/catkin_ws/src/unico_diff_controller
COPY ./unico_diff_controller /robot/catkin_ws/src/unico_diff_controller


# 3d party non ros specific dependencies
# - tinkerforge bindings
RUN apt-get install -y wget \
    && wget https://download.tinkerforge.com/apt/$(. /etc/os-release; echo $ID)/tinkerforge.gpg -q -O - | sudo tee /etc/apt/trusted.gpg.d/tinkerforge.gpg > /dev/null \
    && echo "deb https://download.tinkerforge.com/apt/$(. /etc/os-release; echo $ID $VERSION_CODENAME) main" | sudo tee /etc/apt/sources.list.d/tinkerforge.list \
    && apt-get update \
    && apt-get install python-tinkerforge -y

# add package specific ros dependencies to workspace
RUN source /opt/ros/melodic/setup.bash \
    && cd /robot/catkin_ws/  \
    && rosdep update --include-eol-distros \
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

# Always source ros_entrypoint.sh when launching bash (e.g. when attaching to container)
RUN echo "source /ros_entrypoint.sh" >> /root/.bashrc

COPY ./unico_bringup/logo.txt /
COPY ./unico_bringup/docker/unico_mini/ros_entrypoint.sh /
RUN chmod +x /ros_entrypoint.sh

ENV ROBOT=unicomini
ENV ROS_HOSTNAME=localhost

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["roslaunch", "unico_bringup", "unico_mini.launch"]
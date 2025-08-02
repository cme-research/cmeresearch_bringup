FROM ros:melodic-ros-base

LABEL maintainer="Christian Ehrmann"
LABEL version="0.1"
LABEL description="ROS package for cam_web_video image"

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
COPY . /robot/catkin_ws/src/unico_bringup


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

COPY logo.txt /
COPY ros_entrypoint.sh /
RUN chmod +x /ros_entrypoint.sh

ENV ROBOT=ash
ENV ROS_HOSTNAME=localhost

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["roslaunch", "unico_bringup", "cam_web_video.launch"]
#CMD ["bash"]
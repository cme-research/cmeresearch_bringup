# Start from a base image of Ubuntu 18.04
FROM nvidia/opengl:1.0-glvnd-runtime-ubuntu18.04

ENV NVIDIA_DRIVER_CAPABILITIES=${NVIDIA_DRIVER_CAPABILITIES},display

ENV DEBIAN_FRONTEND=noninteractive
RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

RUN apt-get update && apt-get install -y --no-install-recommends \
        mesa-utils

# workaround for snapshot keyring issue EOF distro
#RUN rm /etc/apt/sources.list.d/ros1-snapshots.list
RUN apt-get update && apt-get install -y curl
RUN curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
RUN echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | tee /etc/apt/sources.list.d/ros.list > /dev/null

# Update the package repository and install the required packages
RUN apt-get update && apt-get install -y \
  ros-melodic-desktop-full \
  ros-melodic-image-transport \
  ros-melodic-image-transport-plugins \
  ros-melodic-pcl-ros \
  ros-melodic-libg2o

ENV ROS_DISTRO=melodic
# Setup the environment variables to fix QT bug
ENV QT_X11_NO_MITSHM=1

# Source the ROS environment setup script
RUN echo "source /opt/ros/$ROS_DISTRO/setup.bash" >> /root/.bashrc

CMD ["bash"]

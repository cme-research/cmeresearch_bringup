import os

from ament_index_python.packages import get_package_share_directory

import launch
import launch_ros.actions


def generate_launch_description():

    joy2twist_cfg_path = PathJoinSubstitution(
        [FindPackageShare("cmeresearch_bringup"), "config/cmexa/", "joy2twist.yaml"]
    )

    joy2twist_params_file_argument = DeclareLaunchArgument(
        "joy2twist_params_file",
        default_value=joy2twist_cfg_path,
        description="ROS2 parameters file to use with joy1twist node",
    )

    joy2twist_node = Node(
        package="joy2twist",
        executable="joy2twist",
        parameters=[LaunchConfiguration("joy2twist_params_file")],
        emulate_tty="true",
    )

    actions = [joy2twist_params_file_argument, joy2twist_node]

    return LaunchDescription(actions)
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    default_config_locks = os.path.join(get_package_share_directory('cmeresearch_bringup'),
                                        'config/cmexa', 'twist_mux_locks.yaml')
    default_config_topics = os.path.join(get_package_share_directory('cmeresearch_bringup'),
                                         'config/cmexa', 'twist_mux_topics.yaml')

    return LaunchDescription([
        DeclareLaunchArgument(
            'config_locks',
            default_value=default_config_locks,
            description='Default locks config file'),
        DeclareLaunchArgument(
            'config_topics',
            default_value=default_config_topics,
            description='Default topics config file'),
        DeclareLaunchArgument(
            'cmd_vel_out',
            default_value='/cmexa_base_mecanum_controller/cmd_vel',
            description='cmd vel output topic'),
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='False',
            description='Use simulation time'),
        Node(
            package='twist_mux',
            executable='twist_mux',
            output='screen',
            remappings={('/cmd_vel_out', LaunchConfiguration('cmd_vel_out'))},
            parameters=[
                {'use_sim_time': LaunchConfiguration('use_sim_time')},
                LaunchConfiguration('config_locks'),
                LaunchConfiguration('config_topics')]
        ),
        Node(
            package='twist_mux',
            executable='twist_marker',
            output='screen',
            remappings={('/twist', LaunchConfiguration('cmd_vel_out'))},
            parameters=[{
                'use_sim_time': LaunchConfiguration('use_sim_time'),
                'frame_id': 'base_link',
                'scale': 1.0,
                'vertical_position': 2.0}]),
    ])
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
import launch.substitutions
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    """cmexa-mini nav2 + slam_toolbox (MAPPING mode).

    Mirror of cmexaiii_nav_mapping.launch.py pointed at config/cmexamini/. Runs
    in the nav container; the hardware launch supplies /scan + odom TF.
    """
    declared_arguments = []

    declared_arguments.append(
        DeclareLaunchArgument('use_sim_time', default_value='False', description='Use simulation time'),
    )

    declared_arguments.append(
        DeclareLaunchArgument(
            "nav_config_filepath",
            default_value=launch.substitutions.TextSubstitution(text=os.path.join(
                get_package_share_directory('cmeresearch_bringup'), 'config/cmexamini/nav_params.yaml')),
            description="Path to nav2 params file",
        )
    )

    declared_arguments.append(
        DeclareLaunchArgument(
            "nav_map_filepath",
            default_value=launch.substitutions.TextSubstitution(text=os.path.join(
                get_package_share_directory('cmeresearch_environments'), 'envs/house/map.yaml')),
            description="Path to nav2 map yaml file",
        )
    )

    declared_arguments.append(
        DeclareLaunchArgument(
            "slam_config_filepath",
            default_value=launch.substitutions.TextSubstitution(text=os.path.join(
                get_package_share_directory('cmeresearch_bringup'), 'config/cmexamini/slam_params.yaml')),
            description="Path to slam_toolbox config file",
        )
    )

    nav_config_filepath = LaunchConfiguration("nav_config_filepath")
    nav_map_filepath = LaunchConfiguration("nav_map_filepath")
    use_sim_time = LaunchConfiguration("use_sim_time")
    slam_config_filepath = LaunchConfiguration("slam_config_filepath")

    nav2_launch_file_dir = os.path.join(get_package_share_directory('nav2_bringup'), 'launch')

    nav2_bringup = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([nav2_launch_file_dir, '/bringup_launch.py']),
        launch_arguments={
            'use_namespace': 'False',
            'map': nav_map_filepath,
            'use_sim_time': use_sim_time,
            'params_file': nav_config_filepath,
        }.items(),
    )

    slam_toolbox_launch_dir = os.path.join(get_package_share_directory('slam_toolbox'), 'launch')

    slam_toolbox = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([slam_toolbox_launch_dir, '/online_async_launch.py']),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'slam_params_file': slam_config_filepath,
        }.items(),
    )

    # Delay slam_toolbox startup to let the LiDAR come up and publish /scan.
    delayed_slam = TimerAction(period=10.0, actions=[slam_toolbox])

    # rosbridge WebSocket server for the web dashboard's live SLAM viewer.
    # Locked down: read-only /map subscription only (no cmd_vel, no services).
    rosbridge_websocket = Node(
        package='rosbridge_server',
        executable='rosbridge_websocket',
        name='rosbridge_websocket',
        output='screen',
        parameters=[{
            'port': 9090,
            'topics_glob': '[/map]',
            'services_glob': '[]',
            'params_glob': '[]',
        }],
    )

    return LaunchDescription(declared_arguments + [nav2_bringup, delayed_slam, rosbridge_websocket])

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
import launch.substitutions
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    declared_arguments = []

    declared_arguments.append(
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='False',
            description='Use simulation time'),
    )

    declared_arguments.append(
        DeclareLaunchArgument(
            "nav_config_filepath",
            default_value=launch.substitutions.TextSubstitution(text=os.path.join(
                get_package_share_directory('cmeresearch_bringup'), 'config/cmexaiii/nav_params.yaml')),
            description="Path to nav2 params file",
        )
    )

    # In localization mode the nav2 map comes from the volume-mounted /maps directory.
    # Save a map there first with: ros2 run nav2_map_server map_saver_cli -f /maps/cmexaiii_house
    declared_arguments.append(
        DeclareLaunchArgument(
            "nav_map_filepath",
            default_value='/maps/cmexaiii_house.yaml',
            description="Path to nav2 map yaml file (volume-mounted)",
        )
    )

    # slam_params_localization.yaml sets mode:localization and map_file_name:/maps/cmexaiii_house
    declared_arguments.append(
        DeclareLaunchArgument(
            "slam_config_filepath",
            default_value=launch.substitutions.TextSubstitution(text=os.path.join(
                get_package_share_directory('cmeresearch_bringup'),
                'config/cmexaiii/slam_params_localization.yaml')),
            description="Path to slam_toolbox localization config file",
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
        PythonLaunchDescriptionSource([slam_toolbox_launch_dir, '/localization_launch.py']),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'slam_params_file': slam_config_filepath,
        }.items(),
    )

    # Delay slam_toolbox startup to allow laser merger to stabilise
    delayed_slam = TimerAction(period=10.0, actions=[slam_toolbox])

    return LaunchDescription(declared_arguments + [nav2_bringup, delayed_slam])

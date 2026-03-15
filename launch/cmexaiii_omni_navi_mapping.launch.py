from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, RegisterEventHandler, IncludeLaunchDescription, GroupAction, TimerAction
from launch_ros.actions import Node, PushRosNamespace
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessExit
from launch.substitutions import Command, FindExecutable, PathJoinSubstitution, LaunchConfiguration, EnvironmentVariable
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import ComposableNodeContainer, Node
from launch_ros.descriptions import ComposableNode

from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare
import launch_ros.actions
import launch
import os

def generate_launch_description():
    # Declare arguments
    declared_arguments = []
    declared_arguments.append(
        DeclareLaunchArgument(
            "gui",
            default_value="false",
            description="Start RViz2 automatically with this launch file.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "use_mock_hardware",
            default_value="false",
            description="Start robot with mock hardware mirroring command to its states.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "robot",
            default_value=EnvironmentVariable("ROBOT", default_value="cmexa"),
            description="Name of the robot.",
        )
    )
    gui = LaunchConfiguration("gui")
    use_mock_hardware = LaunchConfiguration("use_mock_hardware")
    robot = LaunchConfiguration("robot")

    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            PathJoinSubstitution(
                [FindPackageShare("cmeresearch_description"), "urdf", robot, ["robot.urdf.xacro"]]
            ),
            " ",
            "use_mock_hardware:=",
            use_mock_hardware,
        ]
    )

    robot_description = {"robot_description": ParameterValue(robot_description_content, value_type=str)}

    robot_controllers = PathJoinSubstitution(
        [
            FindPackageShare("cmeresearch_description"),
            "config",
            robot,
            "base_mecanum_controllers.yaml",
        ]
    )

    control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[robot_controllers],
        output="both",
    )
    robot_state_pub_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="both",
        parameters=[
            robot_description,
        ],
    )

    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster"],
    )

    robot_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            ["base_mecanum_controller"],
            "--param-file",
            robot_controllers,
            "--controller-ros-args",
            "-r /base_mecanum_controller/reference:=/base_mecanum_controller/cmd_vel",
            "--activate"
        ],
    )

    # Delay start of joint_state_broadcaster after `robot_controller`
    # TODO(anyone): This is a workaround for flaky tests. Remove when fixed.
    delay_joint_state_broadcaster_after_robot_controller_spawner = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=robot_controller_spawner,
            on_exit=[joint_state_broadcaster_spawner],
        )
    )


    # from teleop_twist_joy.launch.py
    declared_arguments.append(
        DeclareLaunchArgument(
            "joy_config",
            default_value="joy2twist_ugv",
            description="Select configuration file for used joystick.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "joy_vel",
            default_value="/base_mecanum_controller/cmd_vel",
            description="Topic to publish cmd_vel from joystick.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "joy_dev",
            default_value="0",
            description="Param to specify joystick device id.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "publish_stamped_twist",
            default_value="true",
            description="Publish stamped twist instead of raw",
        )
    )
    joy_config = LaunchConfiguration("joy_config")
    joy_dev = LaunchConfiguration("joy_dev")

    declared_arguments.append(
        DeclareLaunchArgument(
            "config_filepath",
            default_value=[
                launch.substitutions.TextSubstitution(text=os.path.join(
                    get_package_share_directory('cmeresearch_bringup'), 'config/cmexaiii/', '')),
                joy_config, launch.substitutions.TextSubstitution(text='.yaml')],
            description="Create filepath to config file",
        )
    )

    config_filepath = LaunchConfiguration("config_filepath")

    joy_linux_node = Node(
        package="joy_linux",
        executable="joy_linux_node",
        emulate_tty="true",
        remappings=[("/diagnostics", "diagnostics")],
    )

    joy2twist_node = Node(
        package="joy2twist",
        executable="joy2twist",
        parameters=[config_filepath],
        emulate_tty="true",
        remappings=[("/cmd_vel", "/teleop/cmd_vel")],
    )


    tinkerforge_driver_front_left_stepper = Node(
        package='cmeresearch_stepper_driver',
        executable='stepper_driver_node',
        name='stepper_driver_left_stepper',
        remappings=[
            ('drive_input', '/cmexa_base/front_left/cmd_vel'),
            ('drive_output', '/cmexa_base/front_left/feedback')],
        parameters=[{'bricklet_host': 'localhost',
                     'bricklet_port': 4223,
                     'brick_position': 'a',
                     'step_resolution': 8,
                     'interpolation': True,
                     'acceleration': 10000,
                     'deceleration': 10000,
                     'steps_per_revolution': 200,
                     'mirror_direction': False,
                     'max_step_vel': 3000,
                     'wheel_name': 'front_left_wheel',
                     'hw_simulation': False,
                     'standstill_current': 200,
                     'motor_run_current': 800,
                     'standstill_delay_time': 300,
                     'power_down_time': 1000,
                     'stealth_threshold': 4000,
                     'coolstep_threshold': 6000,
                     'classic_threshold': 10000,
                     'high_velocity_chopper_mode': False
                     }]
    )

    tinkerforge_driver_front_right_stepper = Node(
        package='cmeresearch_stepper_driver',
        executable='stepper_driver_node',
        name='stepper_driver_right_stepper',
        remappings=[
            ('drive_input', '/cmexa_base/front_right/cmd_vel'),
            ('drive_output', '/cmexa_base/front_right/feedback')],
        parameters=[{'bricklet_host': 'localhost',
                     'bricklet_port': 4223,
                     'brick_position': 'b',
                     'step_resolution': 8,
                     'interpolation': True,
                     'acceleration': 10000,
                     'deceleration': 10000,
                     'steps_per_revolution': 200,
                     'mirror_direction': True,
                     'max_step_vel': 3000,
                     'wheel_name': 'front_right_wheel',
                     'hw_simulation': False,
                     'standstill_current': 200,
                     'motor_run_current': 800,
                     'standstill_delay_time': 300,
                     'power_down_time': 1000,
                     'stealth_threshold': 4000,
                     'coolstep_threshold': 6000,
                     'classic_threshold': 10000,
                     'high_velocity_chopper_mode': False
                     }]
    )


    tinkerforge_driver_rear_left_stepper = Node(
        package='cmeresearch_stepper_driver',
        executable='stepper_driver_node',
        name='stepper_driver_rear_left_stepper',
        remappings=[
            ('drive_input', '/cmexa_base/rear_left/cmd_vel'),
            ('drive_output', '/cmexa_base/rear_left/feedback')],
        parameters=[{'bricklet_host': 'localhost',
                     'bricklet_port': 4223,
                     'brick_position': 'c',
                     'step_resolution': 8,
                     'interpolation': True,
                     'acceleration': 10000,
                     'deceleration': 10000,
                     'steps_per_revolution': 200,
                     'mirror_direction': False,
                     'max_step_vel': 3000,
                     'wheel_name': 'rear_left_wheel',
                     'hw_simulation': False,
                     'standstill_current': 200,
                     'motor_run_current': 800,
                     'standstill_delay_time': 300,
                     'power_down_time': 1000,
                     'stealth_threshold': 4000,
                     'coolstep_threshold': 6000,
                     'classic_threshold': 10000,
                     'high_velocity_chopper_mode': False
                     }]
    )

    tinkerforge_driver_rear_right_stepper = Node(
        package='cmeresearch_stepper_driver',
        executable='stepper_driver_node',
        name='stepper_driver_rear_right_stepper',
        remappings=[
            ('drive_input', '/cmexa_base/rear_right/cmd_vel'),
            ('drive_output', '/cmexa_base/rear_right/feedback')],
        parameters=[{'bricklet_host': 'localhost',
                     'bricklet_port': 4223,
                     'brick_position': 'd',
                     'step_resolution': 8,
                     'interpolation': True,
                     'acceleration': 10000,
                     'deceleration': 10000,
                     'steps_per_revolution': 200,
                     'mirror_direction': True,
                     'max_step_vel': 3000,
                     'wheel_name': 'rear_right_wheel',
                     'hw_simulation': False,
                     'standstill_current': 200,
                     'motor_run_current': 800,
                     'standstill_delay_time': 300,
                     'power_down_time': 1000,
                     'stealth_threshold': 4000,
                     'coolstep_threshold': 6000,
                     'classic_threshold': 10000,
                     'high_velocity_chopper_mode': False
                     }]
    )

#   delay_teleop_joy_after_engine_spawner = RegisterEventHandler(
#        event_handler=OnProcessExit(
#            target_action=robot_controller_spawner,
#           on_exit=[joy_node],
#        )
#    )


    declared_arguments.append(
        DeclareLaunchArgument(
            "mqtt_bridge_config",
            default_value=[
                launch.substitutions.TextSubstitution(text=os.path.join(
                    get_package_share_directory('cmeresearch_bringup'), 'config/cmexaiii/', '')),
                'mqtt_bridge_params', launch.substitutions.TextSubstitution(text='.yaml')],
            description="Create filepath to config file",
        )
    )

    mqtt_bridge_config = LaunchConfiguration("mqtt_bridge_config")

    mqtt_bridge_node = Node(
        package="mqtt_bridge",
        executable="mqtt_bridge_node",
        name="mqtt_bridge_node",
        parameters=[mqtt_bridge_config],
        output="both",
    )



#    declared_arguments.append(
#        DeclareLaunchArgument(
#            "mqtt_client_config",
#            default_value=[
#               launch.substitutions.TextSubstitution(text=os.path.join(
#                    get_package_share_directory('cmeresearch_bringup'), 'config/cmexa/', '')),
#                'mqtt_client_params', launch.substitutions.TextSubstitution(text='.yaml')],
#            description="Create filepath to config file",
#        )
#    )

#    mqtt_client_config = LaunchConfiguration("mqtt_client_config")

#    mqtt_client_node = Node(
#        package="mqtt_client",
#        executable="mqtt_client",
#        name="mqtt_client",
#        parameters=[mqtt_client_config],
#        output="both",
#    )

    default_config_locks = os.path.join(get_package_share_directory('cmeresearch_bringup'),
                                         'config/cmexaiii', 'twist_mux_locks.yaml')
    default_config_topics = os.path.join(get_package_share_directory('cmeresearch_bringup'),
                                         'config/cmexaiii', 'twist_mux_topics.yaml')

    declared_arguments.append(
        DeclareLaunchArgument(
            "config_locks",
                default_value=default_config_locks,
                description="Create filepath to config file",
        )
    )

    declared_arguments.append(
        DeclareLaunchArgument(
            "config_topics",
                default_value=default_config_topics,
                description="Create filepath to config file",
        )
    )

    declared_arguments.append(
        DeclareLaunchArgument(
            'cmd_vel_out',
            default_value='/base_mecanum_controller/cmd_vel',
            description='cmd vel output topic'),
    )

    declared_arguments.append(
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='False',
            description='Use simulation time'),
    )

    twist_mux_node = Node(
        package='twist_mux',
        executable='twist_mux',
        output='screen',
        remappings=[('/cmd_vel_out', LaunchConfiguration('cmd_vel_out'))],
        parameters=[
            {'use_sim_time': LaunchConfiguration('use_sim_time')},
            LaunchConfiguration('config_locks'),
            LaunchConfiguration('config_topics')]
    )

    twist_mux_marker_node = Node(
            package='twist_mux',
            executable='twist_marker',
            output='screen',
            remappings=[('/twist', LaunchConfiguration('cmd_vel_out'))],
            parameters=[{
                'use_sim_time': LaunchConfiguration('use_sim_time'),
                'frame_id': 'base_link',
                'scale': 1.0,
                'vertical_position': 2.0}]
    )

    ldlidar_node_front_left = Node(
        package='ldlidar_stl_ros2',
        executable='ldlidar_stl_ros2_node',
        name='laser_front_left',
        output='screen',
        parameters=[
            {'product_name': 'LDLiDAR_LD19'},
            {'topic_name': 'scan_front_left'},
            {'frame_id': 'base_laser_front_left'},
            {'port_name': '/dev/ttyUSB1'},
            {'port_baudrate': 230400},
            {'laser_scan_dir': True},
            {'enable_angle_crop_func': True},
            {'angle_crop_min': 35.0},
            {'angle_crop_max': 135.0}
        ]
    )

    ldlidar_node_rear_right = Node(
        package='ldlidar_stl_ros2',
        executable='ldlidar_stl_ros2_node',
        name='laser_rear_right',
        output='screen',
        parameters=[
            {'product_name': 'LDLiDAR_LD19'},
            {'topic_name': 'scan_rear_right'},
            {'frame_id': 'base_laser_rear_right'},
            {'port_name': '/dev/ttyUSB0'},
            {'port_baudrate': 230400},
            {'laser_scan_dir': True},
            {'enable_angle_crop_func': True},
            {'angle_crop_min': 35.0},
            {'angle_crop_max': 135.0}
        ]
    )

#    # base_link to base_laser_front_left tf node
#    base_link_to_laser_tf_node_front_left = Node(
#        package='tf2_ros',
#        executable='static_transform_publisher',
#        name='base_link_to_base_laser_ld19_front_left',
#        arguments=['0.460', '0.257', '0.18', '0', '0', '0', 'base_link', 'base_laser_front_left']
#    )

#    # base_link to base_laser_rear_right tf node
#    base_link_to_laser_tf_node_rear_right = Node(
#        package='tf2_ros',
#        executable='static_transform_publisher',
#        name='base_link_to_base_laser_ld19_rear_right',
#        arguments=['-0.460', '-0.257', '0.18', '0', '0', '0', 'base_link', 'base_laser_rear_right']
#    )

    declared_arguments.append(
        DeclareLaunchArgument(
            "nav_config_filepath",
            default_value=[
                launch.substitutions.TextSubstitution(text=os.path.join(
                    get_package_share_directory('cmeresearch_bringup'), 'config/cmexaiii/', '')),
                "nav_params", launch.substitutions.TextSubstitution(text='.yaml')],
            description="Create filepath to config file",
        )
    )

    declared_arguments.append(
        DeclareLaunchArgument(
            "nav_map_filepath",
            default_value=[
                launch.substitutions.TextSubstitution(text=os.path.join(
                    get_package_share_directory('cmeresearch_environments'), 'envs/house/', '')),
                "map", launch.substitutions.TextSubstitution(text='.yaml')],
            description="Create filepath to config file",
        )
    )

    nav_config_filepath = LaunchConfiguration("nav_config_filepath")
    nav_map_filepath = LaunchConfiguration("nav_map_filepath")
    nav_use_sim_time = LaunchConfiguration("use_sim_time")

    nav2_launch_file_dir = os.path.join(get_package_share_directory('nav2_bringup'), 'launch')

    nav2_bringup = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([nav2_launch_file_dir, '/bringup_launch.py']),
        launch_arguments={
            'use_namespace': 'False',
            'map': nav_map_filepath,
            'use_sim_time': nav_use_sim_time,
            'params_file': nav_config_filepath}.items(),
    )

    declared_arguments.append(
        DeclareLaunchArgument(
            "slam_config_filepath",
            default_value=launch.substitutions.TextSubstitution(text=os.path.join(
                get_package_share_directory('cmeresearch_bringup'), 'config/cmexaiii/slam_params.yaml')),
            description="Path to slam_toolbox config file",
        )
    )

    slam_config_filepath = LaunchConfiguration("slam_config_filepath")

    slam_toolbox_launch_dir = os.path.join(get_package_share_directory('slam_toolbox'), 'launch')

    slam_toolbox = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([slam_toolbox_launch_dir, '/online_async_launch.py']),
        launch_arguments={
            'use_sim_time': nav_use_sim_time,
            'slam_params_file': slam_config_filepath,
        }.items(),
    )

    laser_merger_node = Node(
        package='dual_laser_merger',
        executable='dual_laser_merger_node',
        name='dual_laser_merger',
        parameters=[{
            'laser_1_topic': '/scan_front_left',
            'laser_2_topic': '/scan_rear_right',
            'merged_scan_topic': '/scan_combined',
            'target_frame': 'base_link',
            'laser_1_x_offset': 0.0,
            'laser_1_y_offset': 0.0,
            'laser_1_yaw_offset': 0.0,
            'laser_2_x_offset': -0.04,
            'laser_2_y_offset': 0.0,
            'laser_2_yaw_offset': 0.0,
            'tolerance': 0.01,
            'queue_size': 5,
            'angle_increment': 0.001,
            'scan_time': 0.067,
            'range_min': 0.01,
            'range_max': 25.0,
            'min_height': -1.0,
            'max_height': 1.0,
            'angle_min': -3.141592654,
            'angle_max': 3.141592654,
            'inf_epsilon': 1.0,
            'use_inf': True,
            'allowed_radius': 0.45,
            'enable_shadow_filter': True,
            'enable_average_filter': True,
        }],
        output='screen',
    )

    delayed_slam_after_laser_merger = TimerAction(
        period=10.0,  # seconds
        actions=[slam_toolbox]
    )

    nodes = [control_node,
             robot_state_pub_node,
             robot_controller_spawner,
             delay_joint_state_broadcaster_after_robot_controller_spawner,
             joy_linux_node,
             joy2twist_node,
             mqtt_bridge_node,
             twist_mux_node,
#             twist_mux_marker_node,
             tinkerforge_driver_front_left_stepper,
             tinkerforge_driver_front_right_stepper,
             tinkerforge_driver_rear_left_stepper,
             tinkerforge_driver_rear_right_stepper,
             ldlidar_node_front_left,
             ldlidar_node_rear_right,
             laser_merger_node,
             nav2_bringup,
             delayed_slam_after_laser_merger,

            ]

    return LaunchDescription(declared_arguments + nodes)

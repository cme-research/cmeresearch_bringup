from launch import LaunchDescription
from launch_ros.actions import Node
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, RegisterEventHandler, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessExit
from launch.substitutions import Command, FindExecutable, PathJoinSubstitution, LaunchConfiguration
from ament_index_python.packages import get_package_share_directory

from launch_ros.actions import Node
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
    gui = LaunchConfiguration("gui")
    use_mock_hardware = LaunchConfiguration("use_mock_hardware")

    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            PathJoinSubstitution(
                [FindPackageShare("cmeresearch_description"), "urdf", "cmexa/cmexa.urdf.xacro"]
            ),
            " ",
            "use_mock_hardware:=",
            use_mock_hardware,
        ]
    )

    robot_description = {"robot_description": robot_description_content}

    robot_controllers = PathJoinSubstitution(
        [
            FindPackageShare("cmeresearch_bringup"),
            "config",
            "cmexa/base_mecanum_controllers.yaml",
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
        parameters=[robot_description],
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
            "cmexa_base_mecanum_controller",
            "--param-file",
            robot_controllers,
            "--controller-ros-args",
            "-r /cmexa_base_mecanum_controller/reference:=/cmexa_base_mecanum_controller/cmd_vel",
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
            default_value="/cmexa_base_mecanum_controller/cmd_vel",
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
                    get_package_share_directory('cmeresearch_bringup'), 'config/cmexa/', '')),
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
        namespace='tf_drivers',
        executable='stepper_driver_node',
        name='cmexa_stepper_driver_left_stepper',
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
        namespace='tf_drivers',
        executable='stepper_driver_node',
        name='cmexa_stepper_driver_right_stepper',
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
        namespace='tf_drivers',
        executable='stepper_driver_node',
        name='cmexa_stepper_driver_rear_left_stepper',
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
        namespace='tf_drivers',
        executable='stepper_driver_node',
        name='cmexa_stepper_driver_rear_right_stepper',
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


#    declared_arguments.append(
#        DeclareLaunchArgument(
#            "mqtt_bridge_config",
#            default_value=[
#                launch.substitutions.TextSubstitution(text=os.path.join(
#                    get_package_share_directory('cmeresearch_bringup'), 'config/cmexa/', '')),
#                'mqtt_bridge_params', launch.substitutions.TextSubstitution(text='.yaml')],
#            description="Create filepath to config file",
#        )
#    )
#    mqtt_bridge_config = LaunchConfiguration("mqtt_bridge_config")

#    mqtt_bridge_node = Node(
#        package="mqtt_bridge",
#        executable="mqtt_bridge_node",
#        name="mqtt_bridge_node",
#        parameters=[mqtt_bridge_config],
#        output="both",
#    )



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
                                         'config/cmexa', 'twist_mux_locks.yaml')
    default_config_topics = os.path.join(get_package_share_directory('cmeresearch_bringup'),
                                         'config/cmexa', 'twist_mux_topics.yaml')

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
            default_value='/cmexa_base_mecanum_controller/cmd_vel',
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
        name='LD19_front_left',
        output='screen',
        parameters=[
            {'product_name': 'LDLiDAR_LD19'},
            {'topic_name': 'scan_front_left'},
            {'frame_id': 'base_laser_front_left'},
            {'port_name': '/dev/ttyUSB0'},
            {'port_baudrate': 230400},
            {'laser_scan_dir': True},
            {'enable_angle_crop_func': False},
            {'angle_crop_min': 135.0},
            {'angle_crop_max': 225.0}
        ]
    )

    ldlidar_node_rear_right = Node(
        package='ldlidar_stl_ros2',
        executable='ldlidar_stl_ros2_node',
        name='LD19_rear_right',
        output='screen',
        parameters=[
            {'product_name': 'LDLiDAR_LD19'},
            {'topic_name': 'scan_rear_right'},
            {'frame_id': 'base_laser_rear_right'},
            {'port_name': '/dev/ttyUSB1'},
            {'port_baudrate': 230400},
            {'laser_scan_dir': True},
            {'enable_angle_crop_func': False},
            {'angle_crop_min': 135.0},
            {'angle_crop_max': 225.0}
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
                    get_package_share_directory('cmeresearch_bringup'), 'config/cmexa/', '')),
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

    IncludeLaunchDescription(
        PythonLaunchDescriptionSource([nav2_launch_file_dir, '/bringup_launch.py']),
        launch_arguments={
            'map': nav_map_filepath,
            'use_sim_time': nav_use_sim_time,
            'params_file': nav_config_filepath}.items(),
    ),

    nodes = [control_node,
             robot_state_pub_node,
             robot_controller_spawner,
             delay_joint_state_broadcaster_after_robot_controller_spawner,
             joy_linux_node,
             joy2twist_node,
#             mqtt_bridge_node,
             twist_mux_node,
#             twist_mux_marker_node,
             tinkerforge_driver_front_left_stepper,
             tinkerforge_driver_front_right_stepper,
             tinkerforge_driver_rear_left_stepper,
             tinkerforge_driver_rear_right_stepper,
             ldlidar_node_front_left,
             ldlidar_node_rear_right,
#             base_link_to_laser_tf_node_front_left,
#            base_link_to_laser_tf_node_rear_right
            ]

    return LaunchDescription(declared_arguments + nodes)

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, RegisterEventHandler
from launch_ros.actions import Node
from launch.event_handlers import OnProcessExit
from launch.substitutions import Command, FindExecutable, PathJoinSubstitution, LaunchConfiguration, EnvironmentVariable
from ament_index_python.packages import get_package_share_directory
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare
import launch
import os


def generate_launch_description():
    """cmexa-mini (diff-drive) hardware/teleop bringup.

    Mirrors launch/cmexaiii_hardware.launch.py (the production mecanum robot) but
    for the smaller differential-drive mini:
      - diff_drive_controller instead of mecanum_drive_controller
      - a single forward LDLiDAR LD19 on /scan (no dual_laser_merger)
      - 2 TinkerForge steppers (front_right + rear_left) instead of 4
      - no tf_odom_relay: diff_drive_controller publishes odom->base_link TF
        itself (enable_odom_tf: true in the controller config)
    It keeps the full telemetry/webapp glue: mqtt_bridge, sm_robot, nav_status,
    system_stats, map_pose. The nav2/slam stack lives in
    cmexamini_nav_mapping.launch.py / cmexamini_nav_localization.launch.py.
    """
    declared_arguments = []
    declared_arguments.append(
        DeclareLaunchArgument(
            "gui", default_value="false",
            description="Start RViz2 automatically with this launch file.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "use_mock_hardware", default_value="false",
            description="Start robot with mock hardware mirroring command to its states.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "robot",
            default_value=EnvironmentVariable("ROBOT", default_value="cmexamini"),
            description="Name of the robot (selects urdf/<robot>/ and config/<robot>/).",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            'use_sim_time', default_value='False', description='Use simulation time'),
    )

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
            FindPackageShare("cmeresearch_bringup"),
            "config",
            robot,
            "cmexamini_base_diff_controllers.yaml",
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
            "cmexa_base_diff_controller",
            "--controller-manager", "/controller_manager",
            "--param-file", robot_controllers,
            "--activate",
        ],
    )

    delay_joint_state_broadcaster_after_robot_controller_spawner = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=robot_controller_spawner,
            on_exit=[joint_state_broadcaster_spawner],
        )
    )

    # Joystick
    declared_arguments.append(
        DeclareLaunchArgument(
            "joy_config", default_value="joy2twist_ugv",
            description="Select configuration file for used joystick.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "joy_vel", default_value="/cmexa_base_diff_controller/cmd_vel",
            description="Topic to publish cmd_vel from joystick.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "joy_dev", default_value="0",
            description="Param to specify joystick device id.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "publish_stamped_twist", default_value="true",
            description="Publish stamped twist instead of raw",
        )
    )
    joy_config = LaunchConfiguration("joy_config")

    declared_arguments.append(
        DeclareLaunchArgument(
            "config_filepath",
            default_value=[
                launch.substitutions.TextSubstitution(text=os.path.join(
                    get_package_share_directory('cmeresearch_bringup'), 'config/cmexamini/', '')),
                joy_config, launch.substitutions.TextSubstitution(text='.yaml')],
            description="Create filepath to joy2twist config file",
        )
    )
    config_filepath = LaunchConfiguration("config_filepath")

    joy_param_filepath = os.path.join(
        get_package_share_directory('cmeresearch_bringup'), 'config/cmexamini', 'joy.yaml')

    joy_linux_node = Node(
        package="joy_linux",
        executable="joy_linux_node",
        name="joy_linux_node",
        parameters=[joy_param_filepath],
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

    # MQTT bridge — the webapp lifeline (cmeresearch/cmexamini-001/...)
    mqtt_bridge_config = os.path.join(
        get_package_share_directory('cmeresearch_bringup'), 'config/cmexamini', 'mqtt_bridge_params.yaml')

    mqtt_bridge_node = Node(
        package="mqtt_bridge",
        executable="mqtt_bridge_node",
        name="mqtt_bridge_node",
        parameters=[mqtt_bridge_config],
        output="both",
    )

    # Twist mux
    default_config_locks = os.path.join(get_package_share_directory('cmeresearch_bringup'),
                                        'config/cmexamini', 'twist_mux_locks.yaml')
    default_config_topics = os.path.join(get_package_share_directory('cmeresearch_bringup'),
                                         'config/cmexamini', 'twist_mux_topics.yaml')

    declared_arguments.append(
        DeclareLaunchArgument("config_locks", default_value=default_config_locks,
                              description="Twist mux locks config"),
    )
    declared_arguments.append(
        DeclareLaunchArgument("config_topics", default_value=default_config_topics,
                              description="Twist mux topics config"),
    )
    declared_arguments.append(
        DeclareLaunchArgument('cmd_vel_out', default_value='/cmexa_base_diff_controller/cmd_vel',
                              description='cmd vel output topic'),
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

    # LiDAR — single forward-facing LDLiDAR LD19 on /scan, frame base_laser.
    # TODO(on-robot): confirm port_name (/dev/ttyUSB0 assumed) and, if the mount
    # is not level/forward, adjust base_laser in the URDF (not here).
    ldlidar_node = Node(
        package='ldlidar_stl_ros2',
        executable='ldlidar_stl_ros2_node',
        name='ldlidar',
        output='screen',
        parameters=[
            {'product_name': 'LDLiDAR_LD19'},
            {'topic_name': 'scan'},
            {'frame_id': 'base_laser'},
            {'port_name': '/dev/ttyUSB0'},
            {'port_baudrate': 230400},
            {'laser_scan_dir': True},
            {'enable_angle_crop_func': False},
        ]
    )

    # Stepper drivers — 2 driven wheels. Params preserved from the mini's
    # bench launch (cmexamini_diff.launch.py); `state` remap added so sm_robot
    # sees the drivers (otherwise it times out into Idle after 30 s).
    tinkerforge_driver_front_right_stepper = Node(
        package='cmeresearch_stepper_driver',
        namespace='tf_drivers',
        executable='stepper_driver_node',
        name='cmexa_stepper_driver_right_stepper',
        remappings=[
            ('drive_input', '/cmexa_base/front_right/cmd_vel'),
            ('drive_output', '/cmexa_base/front_right/feedback'),
            ('state', '/cmexa_base/front_right/state')],
        parameters=[{'bricklet_host': 'localhost',
                     'bricklet_port': 4223,
                     'brick_position': 'a',
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
        name='cmexa_stepper_driver_left_stepper',
        remappings=[
            ('drive_input', '/cmexa_base/rear_left/cmd_vel'),
            ('drive_output', '/cmexa_base/rear_left/feedback'),
            ('state', '/cmexa_base/rear_left/state')],
        parameters=[{'bricklet_host': 'localhost',
                     'bricklet_port': 4223,
                     'brick_position': 'b',
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

    # Robot state machine + telemetry (sm_robot, nav_status, system_stats).
    # driver_topics is scoped to the mini's 2 driven wheels; without it sm_robot
    # would wait for the 4-wheel default set and time out into Idle on boot.
    sm_robot_node = Node(
        package='cmeresearch_robot_state',
        executable='sm_robot_node',
        name='sm_robot',
        output='screen',
        parameters=[{
            'driver_topics': [
                '/cmexa_base/front_right/state',
                '/cmexa_base/rear_left/state',
            ],
            'init_timeout_sec': 30.0,
        }],
    )
    nav_status_node = Node(
        package='cmeresearch_robot_state',
        executable='nav_status_node',
        name='nav_status',
        output='screen',
    )
    system_stats_node = Node(
        package='cmeresearch_robot_state',
        executable='system_stats_node',
        name='system_stats',
        output='screen',
    )
    # Republishes map->base_link TF as /robot_pose (PoseStamped) for the
    # dashboard Position tile. Works in mapping (slam) and localization (AMCL).
    map_pose_node = Node(
        package='cmeresearch_robot_state',
        executable='map_pose_node',
        name='map_pose',
        output='screen',
    )

    nodes = [
        control_node,
        robot_state_pub_node,
        robot_controller_spawner,
        delay_joint_state_broadcaster_after_robot_controller_spawner,
        joy_linux_node,
        joy2twist_node,
        mqtt_bridge_node,
        twist_mux_node,
        ldlidar_node,
        tinkerforge_driver_front_right_stepper,
        tinkerforge_driver_rear_left_stepper,
        sm_robot_node,
        nav_status_node,
        system_stats_node,
        map_pose_node,
    ]

    return LaunchDescription(declared_arguments + nodes)

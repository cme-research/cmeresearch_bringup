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
                [FindPackageShare("cmeresearch_description"), "urdf", "cmexb/cmexb.urdf.xacro"]
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
            "cmexb/cmexb_base_diff_controllers.yaml",
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
            "cmexb_base_controller",
            "--param-file",
            robot_controllers,
            "--controller-ros-args",
            "-r /cmexb_base_diff_controller/reference:=/cmexb_base_diff_controller/cmd_vel",
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
            default_value="/cmexb_base_diff_controller/cmd_vel",
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
                    get_package_share_directory('cmeresearch_bringup'), 'config/cmexb/', '')),
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


    tinkerforge_driver_front_right_stepper = Node(
        package='cmeresearch_stepper_driver',
        namespace='tf_drivers',
        executable='stepper_driver_node',
        name='cmexb_stepper_driver_right_stepper',
        remappings=[
            ('drive_input', '/cmexa_base/front_right/cmd_vel'),
            ('drive_output', '/cmexa_base/front_right/feedback')],
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
        name='cmexb_stepper_driver_rear_left_stepper',
        remappings=[
            ('drive_input', '/cmexa_base/rear_left/cmd_vel'),
            ('drive_output', '/cmexa_base/rear_left/feedback')],
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

    default_config_locks = os.path.join(get_package_share_directory('cmeresearch_bringup'),
                                         'config/cmexb', 'twist_mux_locks.yaml')
    default_config_topics = os.path.join(get_package_share_directory('cmeresearch_bringup'),
                                         'config/cmexb', 'twist_mux_topics.yaml')

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
            default_value='/cmexb_base_diff_controller/cmd_vel',
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

    nodes = [control_node,
             robot_state_pub_node,
             robot_controller_spawner,
             delay_joint_state_broadcaster_after_robot_controller_spawner,
             joy_linux_node,
             joy2twist_node,
             twist_mux_node,
             twist_mux_marker_node,
             tinkerforge_driver_front_right_stepper,
             tinkerforge_driver_rear_left_stepper
            ]

    return LaunchDescription(declared_arguments + nodes)

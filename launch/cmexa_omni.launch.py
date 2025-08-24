from launch import LaunchDescription
from launch_ros.actions import Node
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, RegisterEventHandler
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
            default_value="true",
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
            "cmexa/cmexa_base_mecanum_controllers.yaml",
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
            default_value="logi_teleop",
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
                joy_config, launch.substitutions.TextSubstitution(text='.config.yaml')],
            description="Create filepath to config file",
        )
    )
    joy_node = Node(
        package="joy",
        executable="joy_node",
        name="joy_node",
        parameters=[{
            'device_id': joy_dev,
            'deadzone': 0.3,
            'autorepeat_rate': 20.0,
        }]
    )

    config_filepath = LaunchConfiguration("config_filepath")
    publish_stamped_twist = LaunchConfiguration("publish_stamped_twist")

    teleop_twist_joy = Node(
        package="teleop_twist_joy",
        executable="teleop_node",
        name="teleop_twist_joy_node",
        parameters=[config_filepath, {'publish_stamped_twist': publish_stamped_twist}],
        remappings={('cmd_vel', launch.substitutions.LaunchConfiguration('joy_vel'))},
    )

    tinkerforge_driver_front_left_stepper = Node(
        package='cmeresearch_stepper_driver',
        namespace='tf_drivers',
        executable='stepper_driver_node',
        name='cmexa_stepper_driver_left_stepper',
        remappings=[
            ('drive_input', '/cmexa_base/front_left/cmd_vel'),
            ('drive_output', '/cmexa_base/front_left/feedback')],
        parameters=[{'bricklet_host': '192.168.1.102',
                     'bricklet_port': 4223,
                     'brick_position': 'a',
                     'step_resolution': 8,
                     'interpolation': True,
                     'acceleration': 5000,
                     'deceleration': 5000,
                     'steps_per_revolution': 200,
                     'mirror_direction': False,
                     'gear_ratio': 5,
                     'max_step_vel': 3000,
                     'wheel_name': 'front_left_wheel',
                     'hw_simulation': False,
                     'standstill_current': 200,
                     'motor_run_current': 800,
                     'standstill_delay_time': 300,
                     'power_down_time': 1000,
                     'stealth_threshold': 2200,
                     'coolstep_threshold': 2500,
                     'classic_threshold': 3000,
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
        parameters=[{'bricklet_host': '192.168.1.102',
                     'bricklet_port': 4223,
                     'brick_position': 'b',
                     'step_resolution': 8,
                     'interpolation': True,
                     'acceleration': 5000,
                     'deceleration': 5000,
                     'steps_per_revolution': 200,
                     'mirror_direction': False,
                     'gear_ratio': 5,
                     'max_step_vel': 3000,
                     'wheel_name': 'front_right_wheel',
                     'hw_simulation': False,
                     'standstill_current': 200,
                     'motor_run_current': 800,
                     'standstill_delay_time': 300,
                     'power_down_time': 1000,
                     'stealth_threshold': 2200,
                     'coolstep_threshold': 2500,
                     'classic_threshold': 3000,
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
        parameters=[{'bricklet_host': '192.168.1.102',
                     'bricklet_port': 4223,
                     'brick_position': 'c',
                     'step_resolution': 8,
                     'interpolation': True,
                     'acceleration': 5000,
                     'deceleration': 5000,
                     'steps_per_revolution': 200,
                     'mirror_direction': False,
                     'gear_ratio': 5,
                     'max_step_vel': 3000,
                     'wheel_name': 'rear_left_wheel',
                     'hw_simulation': False,
                     'standstill_current': 200,
                     'motor_run_current': 800,
                     'standstill_delay_time': 300,
                     'power_down_time': 1000,
                     'stealth_threshold': 2200,
                     'coolstep_threshold': 2500,
                     'classic_threshold': 3000,
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
        parameters=[{'bricklet_host': '192.168.1.102',
                     'bricklet_port': 4223,
                     'brick_position': 'd',
                     'step_resolution': 8,
                     'interpolation': True,
                     'acceleration': 5000,
                     'deceleration': 5000,
                     'steps_per_revolution': 200,
                     'mirror_direction': False,
                     'gear_ratio': 5,
                     'max_step_vel': 3000,
                     'wheel_name': 'rear_right_wheel',
                     'hw_simulation': False,
                     'standstill_current': 200,
                     'motor_run_current': 800,
                     'standstill_delay_time': 300,
                     'power_down_time': 1000,
                     'stealth_threshold': 2200,
                     'coolstep_threshold': 2500,
                     'classic_threshold': 3000,
                     'high_velocity_chopper_mode': False
                     }]
    )

#   delay_teleop_joy_after_engine_spawner = RegisterEventHandler(
#        event_handler=OnProcessExit(
#            target_action=robot_controller_spawner,
#           on_exit=[joy_node],
#        )
#    )

    nodes = [control_node,
             robot_state_pub_node,
             robot_controller_spawner,
             delay_joint_state_broadcaster_after_robot_controller_spawner,
             joy_node,
             teleop_twist_joy,
             tinkerforge_driver_front_left_stepper,
             tinkerforge_driver_front_right_stepper,
             tinkerforge_driver_rear_left_stepper,
             tinkerforge_driver_rear_right_stepper
            ]

    return LaunchDescription(declared_arguments + nodes)

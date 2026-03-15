from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, RegisterEventHandler, IncludeLaunchDescription, GroupAction, TimerAction
from launch.substitutions import Command, FindExecutable, PathJoinSubstitution, LaunchConfiguration, EnvironmentVariable
from launch_ros.actions import ComposableNodeContainer, Node
from launch_ros.descriptions import ComposableNode
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue

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

    declared_arguments.append(
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='False',
            description='Use simulation time'),
    )

    nav_use_sim_time = LaunchConfiguration("use_sim_time")

    robot = LaunchConfiguration("robot")
    use_mock_hardware = LaunchConfiguration("use_mock_hardware")

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

    robot_state_pub_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="both",
        parameters=[
            robot_description,
        ],
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

    nodes = [
            robot_state_pub_node,
            ldlidar_node_front_left,
            ldlidar_node_rear_right,
            laser_merger_node,
            ]

    return LaunchDescription(declared_arguments + nodes)
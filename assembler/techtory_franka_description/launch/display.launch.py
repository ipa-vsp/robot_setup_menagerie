import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    # Declare arguments
    declared_arguments = []
    declared_arguments.append(
        DeclareLaunchArgument(
            "prefix",
            default_value="",
            description="Prefix for joint and link names.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "robot_type",
            default_value="fr3",
            description="Franka robot type: fr3, fer, fp3, etc.",
        )
    )

    # Initialize Arguments
    prefix = LaunchConfiguration("prefix")
    robot_type = LaunchConfiguration("robot_type")

    # Get URDF via xacro
    robot_description_content = ParameterValue(
        Command(
            [
                PathJoinSubstitution([FindExecutable(name="xacro")]),
                " ",
                PathJoinSubstitution(
                    [FindPackageShare("techtory_franka_description"), "urdf", "techtory_franka.urdf.xacro"]
                ),
                " ",
                "prefix:=",
                prefix,
                " ",
                "robot_type:=",
                robot_type,
                " ",
                "sim_type:=real",
            ]
        ),
        value_type=str
    )
    robot_description = {"robot_description": robot_description_content}

    rviz_config_file = PathJoinSubstitution(
        [FindPackageShare("techtory_franka_description"), "config", "view_robot.rviz"]
    )

    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="both",
        parameters=[robot_description],
    )

    joint_state_publisher_node = Node(
        package="joint_state_publisher_gui",
        executable="joint_state_publisher_gui",
    )

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="log",
        arguments=["-d", rviz_config_file],
    )

    nodes = [
        robot_state_publisher_node,
        joint_state_publisher_node,
        rviz_node,
    ]

    return LaunchDescription(declared_arguments + nodes)

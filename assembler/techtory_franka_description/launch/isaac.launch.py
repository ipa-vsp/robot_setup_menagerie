import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, OpaqueFunction, TimerAction
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue


def launch_setup(context, *args, **kwargs):
    prefix = LaunchConfiguration("prefix")
    robot_type = LaunchConfiguration("robot_type").perform(context)
    headless = LaunchConfiguration("headless").perform(context)

    pkg_share = get_package_share_directory("techtory_franka_description")
    usd_path = os.path.join(pkg_share, "urdf", "techtory_franka", "techtory_franka.usd")

    isaac_cmd = ["python3", "-m", "isaacsim", "--usd_path", usd_path]
    if headless == "true":
        isaac_cmd.append("--headless")

    isaac_sim_process = ExecuteProcess(cmd=isaac_cmd, output="screen")

    robot_description_content = Command(
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
            "sim_type:=isaac_sim",
        ]
    )
    robot_description = {"robot_description": ParameterValue(robot_description_content, value_type=str)}

    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="both",
        parameters=[{"use_sim_time": False}, robot_description],
    )

    controller_manager_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[
            robot_description,
            PathJoinSubstitution(
                [FindPackageShare("techtory_franka_description"), "config", "ros2_controllers.yaml"]
            ),
            {"use_sim_time": False},
        ],
        output="both",
    )

    spawner_joint_state_broadcaster = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster", "-c", "/controller_manager"],
    )

    spawner_arm_controller = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["arm_controller", "-c", "/controller_manager"],
    )

    spawner_hand_controller = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["hand_controller", "-c", "/controller_manager"],
    )

    return [
        isaac_sim_process,
        TimerAction(
            period=5.0,
            actions=[
                robot_state_publisher_node,
                controller_manager_node,
                spawner_joint_state_broadcaster,
                spawner_arm_controller,
                spawner_hand_controller,
            ],
        ),
    ]


def generate_launch_description():
    declared_arguments = [
        DeclareLaunchArgument(
            "prefix",
            default_value="",
            description="Prefix for joint and link names.",
        ),
        DeclareLaunchArgument(
            "robot_type",
            default_value="fr3",
            description="Franka robot type: fr3, fer, fp3, etc.",
        ),
        DeclareLaunchArgument(
            "headless",
            default_value="false",
            description="Run Isaac Sim without a GUI window.",
        ),
    ]

    return LaunchDescription(declared_arguments + [OpaqueFunction(function=launch_setup)])

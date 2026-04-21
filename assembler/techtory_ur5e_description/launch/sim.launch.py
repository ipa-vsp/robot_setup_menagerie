import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction, SetEnvironmentVariable
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue

def launch_setup(context, *args, **kwargs):
    # Initialize Arguments
    prefix = LaunchConfiguration("prefix")
    sim_type = LaunchConfiguration("sim_type").perform(context)
    
    # Environment variables for Gazebo
    # Gazebo Sim (Ignition) uses GZ_SIM_RESOURCE_PATH / IGN_GAZEBO_RESOURCE_PATH to find models and meshes.
    # We add all share folders in AMENT_PREFIX_PATH to these variables.
    ament_prefix_path = os.environ.get("AMENT_PREFIX_PATH", "")
    resource_paths = []
    if ament_prefix_path:
        for path in ament_prefix_path.split(os.pathsep):
            share_path = os.path.join(path, "share")
            if os.path.isdir(share_path):
                resource_paths.append(share_path)
    
    extra_gz_resource_path = os.pathsep.join(resource_paths)

    # Get URDF via xacro
    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            PathJoinSubstitution(
                [FindPackageShare("techtory_ur5e_description"), "urdf", "techtory_ur5e.urdf.xacro"]
            ),
            " ",
            "prefix:=",
            prefix,
            " ",
            "sim_type:=",
            sim_type,
        ]
    )
    robot_description = {"robot_description": ParameterValue(robot_description_content, value_type=str)}

    # Controller Manager
    controller_manager_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[
            robot_description,
            PathJoinSubstitution(
                [FindPackageShare("techtory_ur5e_description"), "config", "ros2_controllers.yaml"]
            ),
        ],
        output="both",
        condition=IfCondition("true") if sim_type == "real" else IfCondition("false"),
    )

    # Robot State Publisher
    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="both",
        parameters=[{"use_sim_time": True if sim_type != "real" else False}, robot_description],
    )

    # Simulation specific launches
    nodes = [robot_state_publisher_node]

    if sim_type == "real":
        nodes.append(controller_manager_node)
        # Add real hardware related nodes here if any
    
    elif sim_type == "mujoco":
        # Mujoco specific launch could be included here
        pass

    elif sim_type == "gazebo":
        # GZ nodes
        gz_spawn_entity = Node(
            package="ros_gz_sim",
            executable="create",
            output="screen",
            arguments=[
                "-string",
                robot_description_content,
                "-name",
                "techtory_ur5e",
                "-allow_renaming",
                "true",
            ],
        )

        gz_launch_description = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                [FindPackageShare("ros_gz_sim"), "/launch/gz_sim.launch.py"]
            ),
            launch_arguments={
                "gz_args": " -r -v 4 empty.sdf"
            }.items(),
        )

        # Make the /clock topic available in ROS
        gz_sim_bridge = Node(
            package="ros_gz_bridge",
            executable="parameter_bridge",
            arguments=[
                "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",
            ],
            output="screen",
        )

        nodes.extend([
            gz_spawn_entity, 
            gz_launch_description, 
            gz_sim_bridge,
            SetEnvironmentVariable("GZ_SIM_RESOURCE_PATH", extra_gz_resource_path),
            SetEnvironmentVariable("IGN_GAZEBO_RESOURCE_PATH", extra_gz_resource_path),
        ])

    elif sim_type == "isaac_sim":
        # Isaac Sim specific launch could be included here
        pass

    # Spawn controllers
    for controller in ["joint_state_broadcaster", "arm_controller"]:
        nodes.append(
            Node(
                package="controller_manager",
                executable="spawner",
                arguments=[controller, "-c", "/controller_manager"],
                parameters=[{"use_sim_time": True if sim_type != "real" else False}],
            )
        )

    return nodes

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
            "sim_type",
            default_value="real",
            description="Simulation type: real, mujoco, gazebo, isaac_sim.",
        )
    )

    return LaunchDescription(declared_arguments + [OpaqueFunction(function=launch_setup)])

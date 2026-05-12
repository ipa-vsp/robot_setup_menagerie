import os

from launch import LaunchDescription
from launch.actions import ExecuteProcess
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    pkg_share = get_package_share_directory('isaac_assembler')
    isaac_script = os.path.join(pkg_share, 'scripts', 'assemble_techtory_fr3.py')

    isaac_python = '/home/ipa326/ros_ws/arena/colcon_setup_ws/.venv/bin/python3'

    isaac_proc = ExecuteProcess(
        cmd=[isaac_python, isaac_script],
        additional_env={
            'ROS_DISTRO': os.environ.get('ROS_DISTRO', 'jazzy'),
            'AMENT_PREFIX_PATH': os.environ.get('AMENT_PREFIX_PATH', ''),
            'COLCON_PREFIX_PATH': os.environ.get('COLCON_PREFIX_PATH', ''),
            'PYTHONPATH': os.environ.get('PYTHONPATH', ''),
            'LD_LIBRARY_PATH': os.environ.get('LD_LIBRARY_PATH', ''),
            'DISPLAY': os.environ.get('DISPLAY', ':1'),
        },
        output='screen',
    )

    return LaunchDescription([isaac_proc])

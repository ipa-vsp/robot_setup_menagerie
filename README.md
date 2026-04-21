# Techtory ROS 2 Simulation Workspace

This workspace contains ROS 2 packages for simulation and control of various industrial robots (Franka, Cobotta, UR5e) in a Techtory cell environment.

## Installation

### Prerequisites

- ROS 2 (Humble or newer recommended)
- Gazebo Sim (Ignition Gazebo)
- `vcs` (vcstool)
- `rosdep`
- `colcon`

### Isaac Sim Setup

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv 
source .venv/bin/activate
pip install torch==2.10.0 --index-url https://download.pytorch.org/whl/cu130
pip install isaacsim[all,extscache]==6.0.0 --extra-index-url https://pypi.nvidia.com
```

### Workspace Setup

1. Create a workspace directory:
   ```bash
   mkdir -p ~/ros2_ws/src
   cd ~/ros2_ws
   ```

2. Import upstream repositories:
   Copy the `upstream.repos` file to the root of your workspace and run:
   ```bash
   vcs import src < upstream.repos
   ```

3. Install dependencies:
   ```bash
   rosdep update
   rosdep install --from-paths src --ignore-src -r -y
   ```

4. Build the workspace:
   ```bash
   colcon build --symlink-install
   ```

5. Source the workspace:
   ```bash
   source install/setup.bash
   ```

## Running Simulations

The following launch files start the robot state publisher, Gazebo simulation (if selected), and spawn the controllers.

### Franka FR3

To start the Franka simulation in Gazebo:
```bash
ros2 launch techtory_franka_description sim.launch.py sim_type:=gazebo
```

### Cobotta

To start the Cobotta simulation in Gazebo:
```bash
ros2 launch techtory_cobotta_description sim.launch.py sim_type:=gazebo
```

### UR5e

To start the UR5e simulation in Gazebo:
```bash
ros2 launch techtory_ur5e_description sim.launch.py sim_type:=gazebo
```

### Simulation Types

The `sim_type` argument supports the following values:
- `real`: For real hardware or mock components (default).
- `gazebo`: For Gazebo Sim (Ignition Gazebo).
- `mujoco`: For MuJoCo simulation.
- `isaac_sim`: For NVIDIA Isaac Sim.

### Additional Notes
- Isaac Sim import issues: 
   ```bash
   # Build ROS_PACKAGE_PATH from AMENT_PREFIX_PATH (converts ROS2 paths to ROS1-style)
   export ROS_PACKAGE_PATH=$(echo $AMENT_PREFIX_PATH | tr ':' '\n' | awk '{print $1"/share"}' | tr '\n' ':' | sed 's/:$//')
   ```

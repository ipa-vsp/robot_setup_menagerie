#!/usr/bin/env python3
import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from isaacsim import SimulationApp

def main():
    simulation_app = SimulationApp({
        "headless": False,
        "width": 1440,
        "height": 900,
    })

    import omni.kit.app
    from omni.isaac.core import World
    from spawners import add_world, add_techtory_workcell, add_fr3, add_shelf

    # Enable extensions
    ext_manager = omni.kit.app.get_app().get_extension_manager()
    ext_manager.set_extension_enabled_immediate("omni.graph.bundle.action", True)
    ext_manager.set_extension_enabled_immediate("omni.graph.nodes", True)
    ext_manager.set_extension_enabled_immediate("omni.isaac.core_nodes", True)
    ext_manager.set_extension_enabled_immediate("isaacsim.ros2.bridge", True)

    simulation_app.update()

    world = World(stage_units_in_meters=1.0)
    stage = world.scene.stage

    # Positions for Fr3 in Techtory workcell
    robot_spawn_position = np.array([-0.2, -0.7, 0.9])
    robot_rotation_deg = np.array([0.0, 0.0, 90.0])

    # Build the scene
    add_world(stage)
    add_techtory_workcell(stage, "/World/TechtoryWorkcell")
    add_shelf(stage, "/World/Shelf")
    fr3_robot = add_fr3(stage, "/World/Fr3", spawn_position=robot_spawn_position, spawn_rotation_deg=robot_rotation_deg)
    
    world.scene.add(fr3_robot)
    print("World fully composed with Techtory, Fr3, and Shelf")

    world.reset()

    while simulation_app.is_running():
        world.step(render=True)

    simulation_app.close()

if __name__ == "__main__":
    main()

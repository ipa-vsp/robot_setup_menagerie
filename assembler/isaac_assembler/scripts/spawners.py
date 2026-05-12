import os
import numpy as np
from pxr import UsdGeom, Gf, UsdLux, UsdShade, Sdf, UsdPhysics
from omni.isaac.core.utils.stage import add_reference_to_stage
from omni.isaac.core.robots import Robot

PKG_SHARE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def add_world(stage):
    """Creates base world settings with environment, lights, and flat grid"""
    default_prim_path = "/World"
    if not stage.GetPrimAtPath(default_prim_path):
        stage.DefinePrim(default_prim_path, "Xform")

    # Add dome light for environment lighting
    dome_light_path = "/World/DomeLight"
    dome_light = UsdLux.DomeLight.Define(stage, dome_light_path)
    dome_light.CreateIntensityAttr(800)

    # Add cylinder lights
    for i, pos in enumerate([Gf.Vec3d(3.8, -11.6, 15.0), Gf.Vec3d(-3.8, 11.6, 15.0)]):
        light_path = f"/World/CylinderLight{i+1}"
        cylinder_light = UsdLux.CylinderLight.Define(stage, light_path)
        cylinder_light.CreateIntensityAttr(200)
        cylinder_light.CreateRadiusAttr(5)
        cylinder_light.CreateLengthAttr(100)
        xform_api = UsdGeom.XformCommonAPI(stage.GetPrimAtPath(light_path))
        xform_api.SetTranslate(pos)
        xform_api.SetRotate(Gf.Vec3f(90.0, 90.0 if i==0 else 270.0, 0.0), UsdGeom.XformCommonAPI.RotationOrderXYZ)

    # Ground plane
    ground_plane_path = "/World/GroundPlane"
    ground_plane = UsdGeom.Mesh.Define(stage, ground_plane_path)
    ground_plane.CreatePointsAttr([(-50.0, -50.0, 0.0), (50.0, -50.0, 0.0), (50.0, 50.0, 0.0), (-50.0, 50.0, 0.0)])
    ground_plane.CreateFaceVertexCountsAttr([4])
    ground_plane.CreateFaceVertexIndicesAttr([0, 1, 2, 3])
    ground_plane.CreateNormalsAttr([(0.0, 0.0, 1.0)] * 4)
    ground_plane.SetNormalsInterpolation("vertex")

    # Blue material
    material_path = "/World/Materials/BlueMaterial"
    material = UsdShade.Material.Define(stage, material_path)
    shader = UsdShade.Shader.Define(stage, material_path + "/Shader")
    shader.CreateIdAttr("UsdPreviewSurface")
    shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set((0.05, 0.1, 0.35))
    material.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")
    UsdShade.MaterialBindingAPI(ground_plane).Bind(material)
    
    UsdPhysics.CollisionAPI.Apply(ground_plane.GetPrim())

def add_techtory_workcell(stage, prim_path: str):
    usd_path = os.path.join(PKG_SHARE, 'assets', 'workcells', 'techtory_cell.usd')
    workcell_prim = stage.DefinePrim(prim_path, "Xform")
    workcell_prim.GetReferences().AddReference(usd_path)
    print(f"Techtory workcell added at {prim_path}")

def add_fr3(stage, prim_path: str, spawn_position=np.array([0.0, 0.0, 0.0]), spawn_rotation_deg=np.array([0.0, 0.0, 0.0])):
    usd_path = os.path.join(PKG_SHARE, 'assets', 'robot', 'fr3.usd')
    add_reference_to_stage(usd_path=usd_path, prim_path=prim_path)
    
    prim = stage.GetPrimAtPath(prim_path)
    xform = UsdGeom.Xformable(prim)
    xform.ClearXformOpOrder()
    xform.AddTranslateOp().Set(Gf.Vec3d(*spawn_position.tolist()))
    xform.AddRotateXYZOp().Set(Gf.Vec3d(*spawn_rotation_deg.tolist()))
    
    return Robot(prim_path=prim_path, name="fr3")

def add_shelf(stage, prim_path: str, spawn_position=np.array([0.61, 0.27, 0.9]), spawn_rotation_deg=np.array([0.0, 0.0, 90.0])):
    usd_path = os.path.join(PKG_SHARE, 'assets', 'objects', 'shelf.usd')
    shelf_prim = stage.DefinePrim(prim_path, "Xform")
    shelf_prim.GetReferences().AddReference(usd_path)
    
    prim = stage.GetPrimAtPath(prim_path)
    xform = UsdGeom.Xformable(prim)
    xform.ClearXformOpOrder()
    xform.AddTranslateOp().Set(Gf.Vec3d(*spawn_position.tolist()))
    xform.AddRotateXYZOp().Set(Gf.Vec3d(*spawn_rotation_deg.tolist()))
    print(f"Shelf added at {prim_path}")

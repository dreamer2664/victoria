"""
bl.py -- Blender scene helpers: object creation from MeshBuilder, the shared
material library, studio lighting, camera rigs and export.

All geometry is authored in metres, Z up, +X forward, +Y to port.
"""

from __future__ import annotations

import math
import os

import bmesh
import bpy
import mathutils
import numpy as np
from mathutils import Vector

from .hull import MAT, MAT_NAMES


# --------------------------------------------------------------------------
# scene
# --------------------------------------------------------------------------


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.unit_settings.system = "METRIC"
    sc.unit_settings.scale_length = 1.0
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.render.film_transparent = False
    sc.view_settings.view_transform = "Filmic"
    return sc


def collection(name, parent=None):
    col = bpy.data.collections.new(name)
    (parent or bpy.context.scene.collection).children.link(col)
    return col


def obj_from_builder(mb, name, mats, col, smooth=True, auto_smooth=35.0):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    mb.to_bmesh(bm)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    for m in mats:
        me.materials.append(m)
    ob = bpy.data.objects.new(name, me)
    col.objects.link(ob)
    if smooth and len(me.polygons):
        for p in me.polygons:
            p.use_smooth = True
        # honour hard edges by angle (Blender 4.1+ operator)
        try:
            bpy.context.view_layer.objects.active = ob
            ob.select_set(True)
            bpy.ops.object.shade_smooth_by_angle(angle=math.radians(auto_smooth))
            ob.select_set(False)
        except Exception:
            pass
    return ob


def apply_modifiers(ob):
    bpy.context.view_layer.objects.active = ob
    for m in list(ob.modifiers):
        try:
            bpy.ops.object.modifier_apply(modifier=m.name)
        except Exception:
            pass


# --------------------------------------------------------------------------
# materials
# --------------------------------------------------------------------------


def _new_mat(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        if n.type != "OUTPUT_MATERIAL":
            nt.nodes.remove(n)
    out = nt.nodes["Material Output"]
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return m, nt, bsdf


def _set(bsdf, key, value):
    if key in bsdf.inputs:
        bsdf.inputs[key].default_value = value


def wood_material(name, base=(0.32, 0.17, 0.08), dark=(0.14, 0.07, 0.03), scale=6.0,
                  grain_scale=(14.0, 0.6, 0.6), rough=0.45, bump=0.22, varnish=True):
    """Procedural timber: long grain stretched along X, subtle colour variation,
    ring lines, and a varnish sheen.  Used for every plank, frame and seat."""
    m, nt, bsdf = _new_mat(name)
    tex = nt.nodes.new("ShaderNodeTexCoord")
    mapping = nt.nodes.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = grain_scale
    nt.links.new(tex.outputs["Object"], mapping.inputs["Vector"])

    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = scale
    noise.inputs["Detail"].default_value = 8.0
    noise.inputs["Roughness"].default_value = 0.62
    nt.links.new(mapping.outputs["Vector"], noise.inputs["Vector"])

    wave = nt.nodes.new("ShaderNodeTexWave")
    wave.wave_type = "BANDS"
    wave.bands_direction = "X"
    wave.inputs["Scale"].default_value = scale * 2.2
    wave.inputs["Distortion"].default_value = 6.0
    wave.inputs["Detail"].default_value = 3.0
    nt.links.new(mapping.outputs["Vector"], wave.inputs["Vector"])

    mixf = nt.nodes.new("ShaderNodeMix")
    mixf.data_type = "FLOAT"
    mixf.inputs[0].default_value = 0.35
    nt.links.new(noise.outputs["Fac"], mixf.inputs[2])
    nt.links.new(wave.outputs["Fac"], mixf.inputs[3])

    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.25
    ramp.color_ramp.elements[0].color = (*dark, 1.0)
    ramp.color_ramp.elements[1].position = 0.75
    ramp.color_ramp.elements[1].color = (*base, 1.0)
    nt.links.new(mixf.outputs[0], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])

    _set(bsdf, "Roughness", rough if not varnish else 0.32)
    _set(bsdf, "Coat Weight", 0.35 if varnish else 0.0)
    _set(bsdf, "Coat Roughness", 0.12)

    bmp = nt.nodes.new("ShaderNodeBump")
    bmp.inputs["Strength"].default_value = bump
    bmp.inputs["Distance"].default_value = 0.004
    nt.links.new(mixf.outputs[0], bmp.inputs["Height"])
    nt.links.new(bmp.outputs["Normal"], bsdf.inputs["Normal"])
    return m


def paint_material(name, color, rough=0.35, metallic=0.0, coat=0.25, grime=0.0):
    m, nt, bsdf = _new_mat(name)
    _set(bsdf, "Base Color", (*color, 1.0))
    _set(bsdf, "Roughness", rough)
    _set(bsdf, "Metallic", metallic)
    _set(bsdf, "Coat Weight", coat)
    if grime > 0:
        noise = nt.nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 12.0
        noise.inputs["Detail"].default_value = 6.0
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].color = (*[c * 0.72 for c in color], 1.0)
        ramp.color_ramp.elements[1].color = (*color, 1.0)
        nt.links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
        nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
        bmp = nt.nodes.new("ShaderNodeBump")
        bmp.inputs["Strength"].default_value = 0.08
        nt.links.new(noise.outputs["Fac"], bmp.inputs["Height"])
        nt.links.new(bmp.outputs["Normal"], bsdf.inputs["Normal"])
    return m


def metal_material(name, color, rough=0.28, metallic=1.0, aniso=0.0):
    m, nt, bsdf = _new_mat(name)
    _set(bsdf, "Base Color", (*color, 1.0))
    _set(bsdf, "Metallic", metallic)
    _set(bsdf, "Roughness", rough)
    if aniso:
        _set(bsdf, "Anisotropic", aniso)
    return m


def plain(name, color, rough=0.6, transmission=0.0, ior=1.45, emission=None):
    m, nt, bsdf = _new_mat(name)
    _set(bsdf, "Base Color", (*color, 1.0))
    _set(bsdf, "Roughness", rough)
    if transmission:
        _set(bsdf, "Transmission Weight", transmission)
        _set(bsdf, "IOR", ior)
    if emission:
        _set(bsdf, "Emission Color", (*emission[0], 1.0))
        _set(bsdf, "Emission Strength", emission[1])
    return m


def build_materials():
    """The shared material library.  Order must match boatgen.hull.MAT."""
    mats = {}
    mats["wood_out"] = wood_material("Teak_Exterior", base=(0.155, 0.058, 0.024), dark=(0.052, 0.018, 0.007),
                                    rough=0.28, bump=0.30)
    mats["wood_in"] = paint_material("Paint_Interior", (0.30, 0.275, 0.215), rough=0.62, coat=0.06, grime=0.35)
    mats["wood_timber"] = wood_material("Oak_Timber", base=(0.215, 0.108, 0.048), dark=(0.082, 0.038, 0.016),
                                        scale=9.0)
    mats["wood_deck"] = wood_material("Pine_Deck", base=(0.30, 0.20, 0.105), dark=(0.15, 0.095, 0.045),
                                      scale=11.0, rough=0.62)
    mats["paint_hull"] = paint_material("Hull_Black", (0.020, 0.021, 0.024), rough=0.22, coat=0.45, grime=0.5)
    mats["paint_white"] = paint_material("Boot_White", (0.72, 0.71, 0.66), rough=0.3, grime=0.3)
    mats["brass"] = metal_material("Brass", (0.76, 0.55, 0.20), rough=0.18)
    mats["iron"] = metal_material("CastIron", (0.055, 0.055, 0.06), rough=0.55, metallic=0.85)
    mats["steel"] = metal_material("Steel", (0.34, 0.35, 0.37), rough=0.30)
    mats["rope"] = plain("Rope", (0.42, 0.35, 0.22), rough=0.85)
    mats["canvas"] = paint_material("Canvas", (0.40, 0.365, 0.285), rough=0.82, coat=0.04, grime=0.45)
    mats["glass"] = plain("Gauge_Glass", (0.9, 0.9, 0.9), rough=0.05, transmission=0.9, ior=1.5)
    mats["copper"] = metal_material("Copper", (0.72, 0.38, 0.20), rough=0.25)
    mats["leather"] = plain("Leather", (0.18, 0.11, 0.07), rough=0.65)
    mats["coal"] = plain("Coal", (0.035, 0.035, 0.038), rough=0.75)
    mats["water"] = plain("BoilerWater", (0.10, 0.22, 0.26), rough=0.1, transmission=0.75)
    mats["red_lead"] = paint_material("RedLead", (0.35, 0.09, 0.05), rough=0.6, grime=0.4)
    return mats


def mats_list(mats):
    return [mats[n] for n in MAT_NAMES]


# --------------------------------------------------------------------------
# lighting + cameras
# --------------------------------------------------------------------------


def studio(world_strength=0.6, key_energy=900.0, area_size=6.0, backdrop=True, bg=(0.05, 0.055, 0.065), ground_z=-2.2):
    sc = bpy.context.scene
    world = bpy.data.worlds.new("World")
    sc.world = world
    world.use_nodes = True
    bg_node = world.node_tree.nodes["Background"]
    bg_node.inputs[0].default_value = (*bg, 1)
    bg_node.inputs[1].default_value = world_strength

    if backdrop:
        bpy.ops.mesh.primitive_plane_add(size=80, location=(0, 0, ground_z))
        plane = bpy.context.object
        plane.name = "Backdrop"
        m = bpy.data.materials.new("BackdropMat")
        m.use_nodes = True
        b = m.node_tree.nodes["Principled BSDF"]
        b.inputs["Base Color"].default_value = (0.16, 0.17, 0.19, 1)
        b.inputs["Roughness"].default_value = 0.65
        plane.data.materials.append(m)

    def area(name, loc, rot, energy, size, color=(1, 1, 1)):
        ld = bpy.data.lights.new(name, "AREA")
        ld.energy = energy
        ld.size = size
        ld.color = color
        # never let the lamp itself appear in frame: a softbox in shot reads as
        # a light leak across the water, not as illumination
        try:
            ob_tmp = None
            ld.cycles.is_caustics_light = False
        except Exception:
            pass
        ob = bpy.data.objects.new(name, ld)
        ob.visible_camera = False
        ob.location = loc
        ob.rotation_euler = rot
        bpy.context.scene.collection.objects.link(ob)
        return ob

    area("Key", (3.6, -4.2, 4.6), (math.radians(52), 0, math.radians(40)), key_energy, area_size)
    area("Fill", (-4.5, -3.0, 2.4), (math.radians(72), 0, math.radians(-52)), key_energy * 0.28, area_size * 1.5,
         (0.85, 0.92, 1.0))
    area("Rim", (-1.5, 5.0, 3.4), (math.radians(115), 0, math.radians(200)), key_energy * 0.55, area_size, (1.0, 0.96, 0.9))


def water_plane(z=0.0, size=3000.0):
    """A sea surface at the load waterline (z = 0 by the authoring convention).

    Dark, low-roughness, with a stretched noise bump so the surface reads as
    slow harbour water rather than a mirror.  Placed at z = 0 it also proves
    the published draught: the boat floats to exactly the waterline the
    hydrostatic calculation produced.
    """
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0, z))
    plane = bpy.context.object
    plane.name = "Water"
    m = bpy.data.materials.new("SeaWater")
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.010, 0.017, 0.024, 1)
    b.inputs["Roughness"].default_value = 0.30
    b.inputs["IOR"].default_value = 1.333
    # deliberately low: a studio softbox reflects off a big flat plane as a
    # long wedge, which reads as a light leak rather than as water
    b.inputs["Specular IOR Level"].default_value = 0.09

    tex = nt.nodes.new("ShaderNodeTexCoord")
    mapping = nt.nodes.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = (2.4, 5.5, 1.0)
    nt.links.new(tex.outputs["Object"], mapping.inputs["Vector"])
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 26.0
    noise.inputs["Detail"].default_value = 8.0
    noise.inputs["Roughness"].default_value = 0.55
    nt.links.new(mapping.outputs["Vector"], noise.inputs["Vector"])
    bmp = nt.nodes.new("ShaderNodeBump")
    bmp.inputs["Strength"].default_value = 0.22
    bmp.inputs["Distance"].default_value = 0.03
    nt.links.new(noise.outputs["Fac"], bmp.inputs["Height"])
    nt.links.new(bmp.outputs["Normal"], b.inputs["Normal"])
    plane.data.materials.append(m)
    return plane


def sea_studio(world_strength=2.6, bg=(0.088, 0.108, 0.138), key_energy=520.0):
    """Overcast-light rig for the boats afloat.

    Three big softboxes hung low over a dark sea throw long specular wedges
    across the water, which look like light leaks rather than like weather.
    This rig instead puts most of the light into a uniform sky and uses a
    single small key high above the boat, so the water reads as water and the
    hull still has form.
    """
    sc = bpy.context.scene
    world = bpy.data.worlds.new("SeaWorld")
    sc.world = world
    world.use_nodes = True
    bg_node = world.node_tree.nodes["Background"]
    bg_node.inputs[0].default_value = (*bg, 1)
    bg_node.inputs[1].default_value = world_strength

    def area(name, loc, rot, energy, size, color=(1, 1, 1)):
        ld = bpy.data.lights.new(name, "AREA")
        ld.energy = energy
        ld.size = size
        ld.color = color
        # never let the lamp itself appear in frame: a softbox in shot reads as
        # a light leak across the water, not as illumination
        try:
            ob_tmp = None
            ld.cycles.is_caustics_light = False
        except Exception:
            pass
        ob = bpy.data.objects.new(name, ld)
        ob.visible_camera = False
        ob.location = loc
        ob.rotation_euler = rot
        bpy.context.scene.collection.objects.link(ob)
        return ob

    # a low sun, kept small so its reflection in the water stays a sparkle
    # rather than a wedge across the frame
    area("Sun", (5.4, -5.6, 3.4), (math.radians(58), 0, math.radians(44)),
         key_energy * 2.6, 0.30, (1.0, 0.96, 0.90))
    # a soft wrap from above keeps the deck and canopy from going flat
    area("Key", (1.6, -2.2, 6.6), (math.radians(20), 0, math.radians(36)),
         key_energy * 0.7, 4.0)
    # No low fill. At the grazing angles a camera sees open water from, any
    # near-horizon lamp reflects almost totally (Fresnel) and paints a bright
    # parallelogram across the sea. The sky does the fill work instead.


def remove_water():
    for ob in list(bpy.data.objects):
        if ob.name == "Water":
            bpy.data.objects.remove(ob, do_unlink=True)


def camera(name, loc, look_at=(0, 0, 0.35), lens=62.0, ortho=None):
    cd = bpy.data.cameras.new(name)
    cd.lens = lens
    if ortho:
        cd.type = "ORTHO"
        cd.ortho_scale = ortho
    ob = bpy.data.objects.new(name, cd)
    ob.location = loc
    direction = Vector(look_at) - Vector(loc)
    ob.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.collection.objects.link(ob)
    return ob


def scene_bounds(objs=None):
    """World-space bounding box of the visible mesh objects."""
    import mathutils  # noqa: F401  (kept local so bl.py imports cleanly outside Blender)
    EXCLUDE = {"Backdrop", "Water", "Sea"}
    objs = objs or [o for o in bpy.context.scene.objects
                    if o.type == "MESH" and o.name not in EXCLUDE and not o.hide_render]
    mn = mathutils.Vector((1e9, 1e9, 1e9))
    mx = -mn
    for o in objs:
        for c in o.bound_box:
            p = o.matrix_world @ mathutils.Vector(c)
            mn = mathutils.Vector((min(mn[i], p[i]) for i in range(3)))
            mx = mathutils.Vector((max(mx[i], p[i]) for i in range(3)))
    return mn, mx


def frame_camera(name, direction, look_at=None, lens=70.0, margin=1.16, aspect=1.55,
                 roll=0.0):
    """Place a camera along `direction` from the model centre, far enough back
    that the whole boat sits inside `margin` of the frame."""
    mn, mx = scene_bounds()
    centre = (mn + mx) * 0.5
    target = mathutils.Vector(look_at) if look_at is not None else centre
    radius = (mx - mn).length * 0.5
    cd = bpy.data.cameras.new(name)
    cd.lens = lens
    cd.sensor_fit = "HORIZONTAL"
    cd.sensor_width = 36.0
    hfov = 2 * math.atan(cd.sensor_width / (2 * lens))
    vfov = 2 * math.atan(math.tan(hfov / 2) / aspect)
    fov = min(hfov, vfov)
    dist = radius / math.tan(fov / 2) * margin
    d = mathutils.Vector(direction).normalized()
    loc = target + d * dist
    ob = bpy.data.objects.new(name, cd)
    ob.location = loc
    q = (target - loc).to_track_quat("-Z", "Y")
    ob.rotation_euler = q.to_euler()
    bpy.context.scene.collection.objects.link(ob)
    return ob


def render(path, cam, res=(1600, 1000), samples=64, denoise=True):
    sc = bpy.context.scene
    sc.camera = cam
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.cycles.samples = samples
    sc.cycles.use_denoising = denoise
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.adaptive_threshold = 0.02
    sc.cycles.max_bounces = 6
    sc.cycles.diffuse_bounces = 3
    sc.cycles.glossy_bounces = 3
    sc.cycles.transmission_bounces = 4
    sc.cycles.caustics_reflective = False
    sc.cycles.caustics_refractive = False
    sc.render.filepath = path
    sc.render.image_settings.file_format = "PNG"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.render.render(write_still=True)


# --------------------------------------------------------------------------
# export
# --------------------------------------------------------------------------


def export_object(ob, path, fmt="glb"):
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    if fmt == "glb":
        bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", use_selection=True,
                                  export_apply=True, export_yup=True)
    elif fmt == "fbx":
        bpy.ops.export_scene.fbx(filepath=path, use_selection=True, object_types={"MESH"},
                                 apply_scale_options="FBX_SCALE_ALL", axis_forward="-Z", axis_up="Y",
                                 mesh_smooth_type="FACE", use_mesh_modifiers=True)


def join_objects(objs, name):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    ob = bpy.context.object
    ob.name = name
    return ob


def save_blend(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=path)

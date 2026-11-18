"""
bl2.py -- Blender plumbing for THEMISTOCLES-II: object creation from MB
builders, smoothing, UVs, cameras/lights, Cycles rendering, GLB/FBX export.
Requires bpy (Blender 4.2 headless).
"""
from __future__ import annotations
import bpy
import bmesh
import math
import json
import os
import numpy as np

from .mats2 import build_palette, water as water_material
from . import geom2 as G


# ---------------------------------------------------------------------------
# object creation
# ---------------------------------------------------------------------------

PALETTE_CACHE = []


def palette():
    global PALETTE_CACHE
    if not PALETTE_CACHE:
        PALETTE_CACHE = build_palette()
    return PALETTE_CACHE


def mb_to_object(mb, name, coll=None, palette_mats=None, smooth=True,
                 mat_remap=None, origin_at=None):
    """MeshBuilder -> Blender object.  Per-face palette index preserved.
    origin_at: world point that shall become the object's origin (moving
    parts: rowlock pivot, propeller hub, rudder pintle)."""
    if origin_at is not None:
        # MB.translated returns a copy; do not mutate the source mesh or
        # silently replace it with None if a different builder is supplied.
        mb = mb.translated(tuple(-np.asarray(origin_at, float)))
    me = bpy.data.meshes.new(name)
    verts = mb.verts
    faces = mb.faces
    me.from_pydata(verts, [], faces)
    me.update(calc_edges=True)
    pal = palette_mats or palette()
    for m in pal:
        me.materials.append(m)
    for poly in me.polygons:
        idx = mb.mat_indices[poly.index]
        if mat_remap:
            idx = mat_remap.get(idx, idx)
        poly.material_index = min(idx, len(pal) - 1)
        poly.use_smooth = smooth
    obj = bpy.data.objects.new(name, me)
    (coll or bpy.context.scene.collection).objects.link(obj)
    if origin_at is not None:
        obj.location = tuple(origin_at)
    # remove degenerate elements quietly
    bm = bmesh.new()
    bm.from_mesh(me)
    try:
        bmesh.ops.dissolve_degenerate(bm, dist=1e-6, edges=list(bm.edges))
        bm.to_mesh(me)
    except Exception:
        pass
    bm.free()
    # GEN-1: smooth shading used to run across every welded edge, so flat
    # boards with welded edges (benches, thwarts, transom, keel) shaded as
    # soft pillows.  Mark edges sharper than 35 deg as sharp (auto smooth).
    if smooth and hasattr(me, "set_sharp_from_angle"):
        me.set_sharp_from_angle(angle=math.radians(35.0))
    return obj


def join_mb(parts, name="Joined"):
    """Merge several MB builders into one (material indices kept)."""
    out = G.MB(name)
    for p in parts:
        out.append(p)
    return out


# ---------------------------------------------------------------------------
# scene / render rig
# ---------------------------------------------------------------------------

class RenderRig:
    def __init__(self, scene, sea=True, ground=False, res=(1280, 800),
                 samples=48, engine="CYCLES", studio=False, floor_z=-1.0):
        s = scene
        s.render.engine = engine
        s.render.resolution_x = res[0]
        s.render.resolution_y = res[1]
        s.render.resolution_percentage = 100
        s.render.image_settings.file_format = 'PNG'
        if engine == "CYCLES":
            s.cycles.samples = samples
            s.cycles.use_denoising = True
            s.cycles.device = 'CPU'
            s.cycles.use_adaptive_sampling = True
            s.cycles.adaptive_threshold = 0.02
        s.view_settings.look = 'AgX - Medium High Contrast'
        s.view_settings.exposure = -0.35
        # world: overcast sky
        w = bpy.data.worlds.get("TM2_World") or bpy.data.worlds.new("TM2_World")
        w.use_nodes = True
        nts = w.node_tree
        nts.nodes.clear()
        outn = nts.nodes.new("ShaderNodeOutputWorld")
        bgs = nts.nodes.new("ShaderNodeBackground")
        bgs.inputs[0].default_value = (0.055, 0.075, 0.105, 1.0)
        bgs.inputs[1].default_value = 1.2
        sky = nts.nodes.new("ShaderNodeTexSky")
        sky.sky_type = 'NISHITA'
        sky.sun_disc = False
        sky.sun_size = math.radians(3.0)
        sky.sun_intensity = 0.35
        sun_az = math.radians(200)
        sun_el = math.radians(32)
        sky.sun_elevation = sun_el
        sky.sun_rotation = sun_az
        tex = nts.nodes.new("ShaderNodeTexCoord")
        nts.links.new(tex.outputs["Generated"], sky.inputs["Vector"])
        lpath = nts.nodes.new("ShaderNodeLightPath")
        mixs = nts.nodes.new("ShaderNodeMixShader")
        bgs2 = nts.nodes.new("ShaderNodeBackground")
        bgs2.inputs[0].default_value = (0.0026, 0.0034, 0.0042, 1.0)
        bgs2.inputs[1].default_value = 1.0
        bgs.inputs[1].default_value = 0.85
        nts.links.new(sky.outputs["Color"], bgs.inputs[0])
        nts.links.new(bgs.outputs["Background"], mixs.inputs[1])
        nts.links.new(bgs2.outputs["Background"], mixs.inputs[2])
        nts.links.new(lpath.outputs["Is Camera Ray"], mixs.inputs[0])
        nts.links.new(mixs.outputs[0], outn.inputs[0])
        self.bg_cam = bgs2
        if not studio:
            # afloat: the camera sees the same overcast sky that lights the
            # boat (it used to see a near-black void above the horizon)
            bgs2.inputs[0].default_value = (0.20, 0.25, 0.31, 1.0)
            bgs2.inputs[1].default_value = 1.0
        s.world = w
        # lights: large soft key + cool fill + warm rim
        def area(name, loc, energy, size, color):
            L = bpy.data.objects.get(name)
            if L is None:
                bpy.ops.object.light_add(type='AREA', location=loc)
                L = bpy.context.object
                L.name = name
            L.data.energy = energy
            L.data.shape = 'DISK'
            L.data.size = size
            L.data.color = color
            if hasattr(L.data, 'visible_camera'):
                L.data.visible_camera = False
            # GEN-1: aim every lamp at the boat.  They used to be left at the
            # default orientation (straight down), so the low warm rim lamp
            # threw a bright pool on the studio floor that read as a lit
            # band / false horizon in the bow-on and stern-on views.
            from mathutils import Vector
            L.location = loc
            d = Vector((0.0, 0.0, 0.0)) - Vector(loc)
            L.rotation_mode = 'QUATERNION'
            L.rotation_quaternion = d.to_track_quat('-Z', 'Y')
            if hasattr(L.data, 'spread'):
                L.data.spread = math.radians(60.0)   # keep light off the cove walls
            return L
        area("TM2_Key", (6, -7, 9), 1900 * 0.38 * 0.32, 5.0, (1.0, 0.94, 0.86))
        area("TM2_Fill", (-5, 6, 5), 1400 * 0.32 * 0.45, 6.0, (0.75, 0.85, 1.0))
        area("TM2_Top", (-4.5, 5.0, 10.0), 2100 * 0.40 * 0.45,   # GEN-1: off the plan-view axis (specular glare)
             4.0, (0.95, 0.97, 1.0))
        area("TM2_Rim", (-7, -4, 5.0), 900 * 0.30 * 0.50, 3.0, (1.0, 0.85, 0.65))
        if studio:
            from .studio2 import cyclorama, tune_scene
            cyclorama(drop_z=floor_z)
            tune_scene(scene, exposure=-0.75)   # GEN-1: aimed lamps
        else:
            # GEN-1: afloat views are lit by sky + sun only.  The studio area
            # lamps reflect in open water as detached white discs.
            for nm in ("TM2_Key", "TM2_Fill", "TM2_Top", "TM2_Rim"):
                ob = bpy.data.objects.get(nm)
                if ob:
                    ob.hide_render = True
        # sun for crispness
        sun = bpy.data.objects.get("TM2_Sun")
        if sun is None:
            bpy.ops.object.light_add(type='SUN', location=(4, -3, 8))
            sun = bpy.context.object
            sun.name = "TM2_Sun"
        sun.data.energy = 0.55
        sun.data.angle = math.radians(24)
        sun.rotation_euler = (math.radians(58), 0, math.radians(38))
        if hasattr(sun.data, 'visible_camera'):
            sun.data.visible_camera = False
        # sea plane at z=0 (LWL)
        self.sea = None
        if sea:
            bpy.ops.mesh.primitive_plane_add(size=3000, location=(0, 0, 0))
            self.sea = bpy.context.object
            self.sea.name = "TM2_Sea"
            if studio:
                from .mats2 import solid
                self.sea.data.materials.append(solid("TM2_SeaFlat",
                    (0.10, 0.125, 0.15), rough=0.20, bump_scale=2.0, bump_str=0.10))
            else:
                self.sea.data.materials.append(water_material())
        self.ground = None
        if ground:
            bpy.ops.mesh.primitive_plane_add(size=80, location=(0, 0, -1.0))
            self.ground = bpy.context.object
            self.ground.name = "TM2_Ground"
            self.ground.data.materials.append(
                __import__("them2.mats2", fromlist=["solid"]).solid(
                    "TM2_GroundGrey", (0.16, 0.17, 0.19), rough=0.9))
        self.cam = None

    def camera(self, target, direction, dist=None, lens=58, name="TM2_Cam",
               fov_scale=1.0, margin=1.25, size_hint=None):
        """Place a camera looking along unit `direction` at target bounds."""
        cam = bpy.data.objects.get(name)
        if cam is None:
            cam_data = bpy.data.cameras.new(name)
            cam = bpy.data.objects.new(name, cam_data)
            bpy.context.scene.collection.objects.link(cam)
        d = np.asarray(direction, dtype=float)
        d = d / np.linalg.norm(d)
        t = np.asarray(target, dtype=float)
        radius = size_hint if size_hint else 6.0
        # fit: distance from bounding sphere radius and fov
        fov = math.atan(1.0 / (2 * lens * 0.018)) if False else None
        dfov = 2 * math.atan(18.0 / lens)   # 36mm full frame horizontal-ish
        need = radius * margin / math.tan(dfov / 2) * 1.02 * fov_scale
        pos = t + d * (dist or max(3.0, need))
        cam.location = tuple(pos)
        cam.data.lens = lens
        # track constraint to target empty
        tgt = bpy.data.objects.get(name + "_T")
        if tgt is None:
            tgt = bpy.data.objects.new(name + "_T", None)
            bpy.context.scene.collection.objects.link(tgt)
        tgt.location = tuple(t)
        con = None
        for c in cam.constraints:
            if c.name == "TM2Track":
                con = c
        if con is None:
            con = cam.constraints.new("TRACK_TO")
            con.name = "TM2Track"
        con.target = tgt
        bpy.context.scene.camera = cam
        self.cam = cam
        return cam

    def render(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        bpy.context.scene.render.filepath = path
        bpy.ops.render.render(write_still=True)


def set_sea_visible(vis):
    for nm in ("TM2_Sea",):
        o = bpy.data.objects.get(nm)
        if o:
            o.hide_viewport = not vis
            o.hide_render = not vis


# ---------------------------------------------------------------------------
# export
# ---------------------------------------------------------------------------

def ensure_uv(obj):
    me = obj.data
    if not me.uv_layers:
        uv = me.uv_layers.new(name="UVMap")
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.cube_project(cube_size=1.0, correct_aspect=True, scale_to_bounds=True)
    bpy.ops.object.mode_set(mode='OBJECT')
    obj.select_set(False)


def triangle_count(obj):
    me = obj.data
    me.calc_loop_triangles()
    return len(me.loop_triangles)


def decimate_to(obj, limit=19000):
    n = triangle_count(obj)
    if n <= limit:
        return n, False
    ratio = limit / n
    mod = obj.modifiers.new("Decim", 'DECIMATE')
    mod.ratio = ratio
    mod.use_collapse_triangulate = True
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=mod.name)
    return triangle_count(obj), True


def export_part(obj, out_dir, stem, decimate_limit=19000):
    ensure_uv(obj)
    tris, decimated = decimate_to(obj, decimate_limit)
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    glb = os.path.join(out_dir, stem + ".glb")
    fbx = os.path.join(out_dir, stem + ".fbx")
    bpy.ops.export_scene.gltf(filepath=glb, export_format='GLB',
                              use_selection=True, export_yup=True)
    bpy.ops.export_scene.fbx(filepath=fbx, use_selection=True,
                             axis_forward='-Z', axis_up='Y')
    b = obj.dimensions
    verts = np.empty(len(obj.data.vertices) * 3)
    obj.data.vertices.foreach_get("co", verts)
    return {
        "parts": [{
            "file_glb": stem + ".glb", "file_fbx": stem + ".fbx",
            "object": obj.name, "vertices": len(obj.data.vertices),
            "triangles": tris, "decimated": decimated,
            "dimensions_m": [round(v, 4) for v in b],
            "origin_m": [round(v, 4) for v in obj.matrix_world.translation],
        }]
    }


# ---------------------------------------------------------------------------
# mesh audit helpers (used by verify2)
# ---------------------------------------------------------------------------

def mesh_info(obj):
    me = obj.data
    me.calc_loop_triangles()
    nv = len(me.vertices)
    nf = len(me.polygons)
    ntr = len(me.loop_triangles)
    ng = sum(1 for p in me.polygons if len(p.vertices) > 4)
    return dict(verts=nv, faces=nf, tris=ntr, ngons=ng,
                dims=tuple(round(v, 4) for v in obj.dimensions))

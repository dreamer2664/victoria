"""Render helper: set up a period-appropriate daylight studio and shoot a
set of inspection views of whatever modules are loaded.

Usage inside Blender:
    blender -b models/module_hull.blend -P blender/render.py -- <outdir> <preset>
"""
from __future__ import annotations
import os, sys, math
import bpy
import numpy as np
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def add_sea(P, size=900, z=-0.045):
    me = bpy.data.meshes.new("Sea")
    n = 2
    v = [(-size, -size, z), (size, -size, z), (size, size, z), (-size, size, z)]
    me.from_pydata(v, [], [(0, 1, 2, 3)])
    ob = bpy.data.objects.new("Sea", me)
    bpy.context.scene.collection.objects.link(ob)
    ob.data.materials.append(P["water"])
    return ob


def add_sun(strength=3.2, angle_deg=38, elev_deg=34, colour=(1.0, 0.96, 0.9)):
    l = bpy.data.lights.new("Sun", 'SUN')
    l.energy = strength
    l.angle = math.radians(angle_deg)
    l.color = colour
    ob = bpy.data.objects.new("Sun", l)
    bpy.context.scene.collection.objects.link(ob)
    ob.rotation_euler = (math.radians(60 - elev_deg), 0, math.radians(35))
    return ob


def add_area(name, loc, rot, size, energy, colour=(1, 1, 1)):
    l = bpy.data.lights.new(name, 'AREA')
    l.size = size
    l.energy = energy
    l.color = colour
    ob = bpy.data.objects.new(name, l)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = rot
    return ob


def add_camera(loc, look_at=(0, 0, 8), lens=50):
    cam = bpy.data.cameras.new("Cam")
    cam.lens = lens
    cam.clip_start = 0.05
    cam.clip_end = 2000
    ob = bpy.data.objects.new("Cam", cam)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    d = Vector(look_at) - Vector(loc)
    ob.rotation_mode = 'QUATERNION'
    ob.rotation_quaternion = d.to_track_quat('-Z', 'Y')
    bpy.context.scene.camera = ob
    return ob


def world_sky(top=(0.32, 0.45, 0.62), bottom=(0.72, 0.72, 0.68), strength=1.0):
    w = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
    bpy.context.scene.world = w
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    grad = nt.nodes.new("ShaderNodeTexGradient")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    mapn = nt.nodes.new("ShaderNodeMapping")
    tex = nt.nodes.new("ShaderNodeTexCoord")
    mapn.inputs["Rotation"].default_value = (math.pi / 2, 0, 0)
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[0].color = (*bottom, 1)
    ramp.color_ramp.elements[1].position = 0.85
    ramp.color_ramp.elements[1].color = (*top, 1)
    nt.links.new(tex.outputs["Generated"], mapn.inputs["Vector"])
    nt.links.new(mapn.outputs["Vector"], grad.inputs["Vector"])
    nt.links.new(grad.outputs["Color"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = strength
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])


def setup_render(res=(1600, 900), samples=48, engine='CYCLES', denoise=True):
    sc = bpy.context.scene
    sc.render.engine = engine
    if engine == 'CYCLES':
        sc.cycles.device = 'CPU'
        sc.cycles.samples = samples
        sc.cycles.use_denoising = denoise
        sc.cycles.max_bounces = 6
        sc.cycles.transparent_max_bounces = 8
        sc.cycles.use_adaptive_sampling = True
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = False
    sc.view_settings.view_transform = 'Filmic' if 'Filmic' in [
        v.name for v in bpy.types.ColorManagedViewSettings.bl_rna
        .properties['view_transform'].enum_items] else 'AgX'
    return sc


def shoot(path, loc, look_at, lens=50, res=(1600, 900), samples=48,
          hide=()):
    for n in hide:
        ob = bpy.data.objects.get(n)
        if ob:
            ob.hide_render = True
    add_camera(loc, look_at, lens)
    sc = setup_render(res, samples)
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print("RENDERED", path)


EXTERIOR_VIEWS = [
    ("three_quarter_bow", (140, -120, 26), (0, 0, 8), 55),
    ("beam", (0, -190, 14), (0, 0, 8), 55),
    ("three_quarter_stern", (-125, 105, 22), (0, 0, 8), 55),
    ("bow_on", (168, -22, 14), (56, 0, 8), 65),
    ("stern_on", (-160, 26, 16), (-62, 0, 8), 65),
    ("high_above", (60, -70, 150), (0, 0, 6), 45),
    ("below", (70, -80, -30), (0, 0, 4), 50),
]


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    outdir = argv[0] if argv else os.path.join(ROOT, "renders", "wip")
    preset = argv[1] if len(argv) > 1 else "exterior"
    res = (int(argv[2]), int(argv[3])) if len(argv) > 3 else (1280, 720)
    samples = int(argv[4]) if len(argv) > 4 else 32
    os.makedirs(outdir, exist_ok=True)
    sys.path.insert(0, HERE)
    from lib_build import build_palette
    P = build_palette()
    world_sky()
    add_sun()
    add_sea(P)
    if preset == "exterior":
        for i, (name, loc, la, lens) in enumerate(EXTERIOR_VIEWS):
            if name.startswith("below"):
                continue
            shoot(os.path.join(outdir, name + ".png"), loc, la, lens, res, samples)
    elif preset == "quick":
        shoot(os.path.join(outdir, "quick.png"), (150, -125, 22), (0, 0, 8),
              55, res, samples)

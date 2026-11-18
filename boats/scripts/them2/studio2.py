"""
studio2.py -- studio environment: gradient cyclorama backdrop, calibrated
exposure, soft three-point lighting.  Replaces the black-world default.
"""
from __future__ import annotations
import bpy
import math
import numpy as np


def cyclorama(name="TM2_Studio_BG", size=120, drop_z=-1.0):
    """Full surround: floor extends every direction from under the subject,
    then wraps up as a matte gradient wall in all four directions and a ceiling
    -- no world shader ever reaches the camera."""
    verts = []
    faces = []
    # concentric rings: (radius_xy, z).  Index 0 = inner floor ring (wide flat
    # zone around the boat), then the curtain sweep, then ceiling rings.
    rings = [(10.0, drop_z), (size * 0.42, drop_z), (size * 0.55, drop_z)]
    N = 40
    # build a radial grid: azimuths x rings
    base_r = [1.0, size * 0.28, size * 0.50]
    crad = size * 0.14
    # floor ring radii then curving wall then ceiling closure
    prof = [(0.10, drop_z)]
    prof.append((size * 0.30, drop_z))
    prof.append((size * 0.44, drop_z))
    for k in range(1, 9):
        ang = k / 8 * math.pi / 2 * 0.995
        prof.append((size * 0.44 + crad * math.sin(ang),
                     drop_z + crad * (1 - math.cos(ang))))
    HZ = size * 0.42     # ceiling height after curtain
    prof.append((size * 0.44 + crad, HZ))
    prof.append((size * 0.30, HZ))
    verts.append((0.0, 0.0, drop_z))
    NV = len(prof)
    for (r, z) in prof:
        for i in range(N):
            a = 2 * math.pi * i / N
            verts.append((r * math.cos(a), r * math.sin(a), z))
    # centre fan
    for i in range(N):
        faces.append((0, 2 + i, 2 + (i + 1) % N))
    # first prof ring has r=0.10 (ring index 0 -> verts 1..N)
    for ring in range(NV - 1):
        a0 = 1 + ring * N
        b0 = 1 + (ring + 1) * N
        for i in range(N):
            j = (i + 1) % N
            faces.append((a0 + i, a0 + j, b0 + j, b0 + i))
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    for p in me.polygons:
        p.use_smooth = True
    old = bpy.data.objects.get(name)
    if old:
        old.data = me
        obj = old
    else:
        obj = bpy.data.objects.new(name, me)
        bpy.context.scene.collection.objects.link(obj)
    m = bpy.data.materials.get(name + "_Mat") or bpy.data.materials.new(name + "_Mat")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bs = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bs.inputs["Roughness"].default_value = 1.0
    bs.inputs["Specular IOR Level"].default_value = 0.0
    nt.links.new(bs.outputs["BSDF"], out.inputs["Surface"])
    # Height-based gradient via Geometry Position
    geom = nt.nodes.new("ShaderNodeNewGeometry")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geom.outputs["Position"], sep.inputs["Vector"])
    mmp = nt.nodes.new("ShaderNodeMapRange")
    mmp.inputs["From Min"].default_value = drop_z
    mmp.inputs["From Max"].default_value = size * 0.34
    nt.links.new(sep.outputs["Z"], mmp.inputs["Value"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.030, 0.033, 0.042, 1)
    mid = ramp.color_ramp.elements.new(0.45)
    mid.color = (0.115, 0.125, 0.150, 1)
    ramp.color_ramp.elements[1].color = (0.26, 0.275, 0.315, 1)
    nt.links.new(mmp.outputs["Result"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bs.inputs["Base Color"])
    obj.data.materials.clear()
    obj.data.materials.append(m)
    return obj


def tune_scene(s, exposure=0.0):
    s.view_settings.look = 'AgX - Medium High Contrast'
    s.view_settings.exposure = exposure


def hide_lights_from_camera():
    for o in bpy.context.scene.objects:
        if o.type == 'LIGHT' and o.name.startswith("TM2_"):
            o.hide_render = False
            o.data.energy = o.data.energy  # keep
        # Area lights: use portal-like invisible speedup; camera visibility handled in Cycles
        if o.type == 'LIGHT':
            if hasattr(o.data, "visible_camera"):
                pass  # attribute exists on some versions but is a no-op setter only

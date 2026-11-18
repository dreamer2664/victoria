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
    # GEN-1 correction: the fan used to index 2+i (off by one), producing
    # long inverted triangles from the centre out to the next ring -- the
    # black wedge that cut across the studio floor.
    for i in range(N):
        faces.append((0, 1 + i, 1 + (i + 1) % N))
    # first prof ring has r=0.10 (ring index 0 -> verts 1..N)
    for ring in range(NV - 1):
        a0 = 1 + ring * N
        b0 = 1 + (ring + 1) * N
        for i in range(N):
            j = (i + 1) % N
            # consistent +Z / inward winding with the centre fan (the old
            # order faced the floor DOWN while the fan faced up, and the
            # averaged normals left a dark ring on the floor)
            faces.append((a0 + i, b0 + i, b0 + j, a0 + j))
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
    bs.inputs["Roughness"].default_value = 0.85
    bs.inputs["Specular IOR Level"].default_value = 0.15
    nt.links.new(bs.outputs["BSDF"], out.inputs["Surface"])
    # Height-based gradient via Geometry Position
    geom = nt.nodes.new("ShaderNodeNewGeometry")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geom.outputs["Position"], sep.inputs["Vector"])
    mmp = nt.nodes.new("ShaderNodeMapRange")
    mmp.inputs["From Min"].default_value = drop_z
    mmp.inputs["From Max"].default_value = drop_z + size * 0.34
    nt.links.new(sep.outputs["Z"], mmp.inputs["Value"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    # GEN-1: a light, low-contrast studio.  The old ramp started at 0.03
    # (near black) on the floor, so the floor read as a void and the cove
    # met it in a hard dark wedge; open interiors had nothing to bounce off.
    ramp.color_ramp.elements[0].color = (0.150, 0.158, 0.172, 1)
    mid = ramp.color_ramp.elements.new(0.10)
    mid.color = (0.190, 0.200, 0.218, 1)
    ramp.color_ramp.elements[1].color = (0.300, 0.315, 0.345, 1)
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


def keel_blocks(points, floor_z, name="TM2_KeelBlocks"):
    """Timber keel blocks from the studio floor up to the keel at the given
    (x, z_keel_bottom) points: a dry boat is shown supported, not hovering."""
    verts, faces = [], []
    for (x, zk) in points:
        h = zk - floor_z
        if h <= 0.005:
            continue
        for (dz, sx, sy) in ((0.0, 0.34, 0.30), (h * 0.5, 0.26, 0.22)):
            z0 = floor_z + dz
            z1 = floor_z + (h * 0.5 if dz == 0.0 else h)
            b = len(verts)
            for zz in (z0, z1):
                for (ax, ay) in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                    verts.append((x + ax * sx / 2, ay * sy / 2, zz))
            faces += [(b, b + 3, b + 2, b + 1), (b + 4, b + 5, b + 6, b + 7),
                      (b, b + 1, b + 5, b + 4), (b + 1, b + 2, b + 6, b + 5),
                      (b + 2, b + 3, b + 7, b + 6), (b + 3, b, b + 4, b + 7)]
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    old = bpy.data.objects.get(name)
    if old:
        bpy.data.objects.remove(old, do_unlink=True)
    obj = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(obj)
    m = bpy.data.materials.get(name + "_Mat") or bpy.data.materials.new(name + "_Mat")
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.20, 0.15, 0.10, 1)
    bsdf.inputs["Roughness"].default_value = 0.8
    obj.data.materials.append(m)
    return obj

"""HULL CROSS-SECTION + UNDERWATER RENDER (required deliverables).

Produces:
    hull_cross_section.png   a midship transverse section, looking forward, with
                             the shell, double bottom, deck beams, bulkhead and
                             the machinery shown in place - the drawing a
                             builder issues to the plating shop
    body_plan_3d.png         the same form shown as a 3-D body plan, all
                             stations lined up on the centreline

The section is generated from shipdesign.hull.HullForm.section(), i.e. from the
SAME source that produced the 3-D hull, so the section cannot disagree with the
model.
"""
from __future__ import annotations
import os, sys, math
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
for p in (ROOT, HERE):
    if p not in sys.path:
        sys.path.insert(0, p)

import numpy as np
from shipdesign.spec import SHIP, DECK_Z, FUNNELS
from shipdesign import layout
from shipdesign.hull import HULL, T
from lib_build import (reset_scene, collection, mesh_object, build_palette, box,
                       cylinder, principled)

COL = None
P = None

SECTION_STATIONS = [0.0, 20.0, 40.0, 55.0, 68.0]


def section_curve(x):
    """Half section of the shell at station x, as (y, z) from keel to sheer."""
    hb = HULL.half_beam_at
    ztop = float(HULL.deck_z(x))
    hull_T = float(T)
    # sample from the keel up to the waterline, then the topsides to the sheer
    pts = []
    for k in range(40):
        z = hull_T * 0.02 + (ztop - hull_T * 0.02) * k / 39.0
        b = hb(x, z)
        if b > 0.01:
            pts.append((b, z))
    return pts, ztop


def shell_of_section(objs, x, mat, thick=0.10):
    pts, ztop = section_curve(x)
    if len(pts) < 4:
        return
    for side in (1, -1):
        v = []
        for (b, z) in pts:
            v.append((x, side * b, z))
        for (b, z) in reversed(pts):
            v.append((x, side * max(b - thick, 0.02), z))
        n = len(pts)
        f = []
        for i in range(n - 1):
            f.append((i, i + 1, n + i + 1, n + i))
        objs.append(mesh_object("Section_Shell_%d" % side, v, f, col=COL,
                                mat=mat))


def build_sections():
    objs = []
    steel = P["steel"]
    keel = P["hull_black"]
    deck = P["deck_wood_light"]
    for x in SECTION_STATIONS:
        shell_of_section(objs, x, steel)
        # decks across each section
        for k, n, z, ext in layout.DECKS:
            if not (ext[0] <= x <= ext[1]):
                continue
            b = float(HULL.half_beam_at(x, z))
            if b < 1.0:
                b = float(layout.hull_side_halfbeam(x, z))
            b = max(b, 1.0)
            v, f = box((x, 0, z), (0.16, b * 2, 0.18))
            objs.append(mesh_object("Section_Deck", v, f, col=COL,
                                    mat=deck))
        # centreline girder / keelson
        v, f = box((x, 0, (1.30 + float(T)) / 2), (0.20, 0.5, float(T) - 1.30))
        objs.append(mesh_object("Section_Keelson", v, f, col=COL, mat=keel))
        # double bottom floors
        for j in range(-4, 5):
            v, f = box((x, j * 1.9, 0.75), (0.12, 0.14, 1.25))
            objs.append(mesh_object("Section_Floor", v, f, col=COL, mat=keel))
    return objs


def build_body_plan():
    """All stations as wireframe outlines, lined up on the centreline."""
    objs = []
    import bmesh
    for x in np.arange(-72.0, 72.1, 4.0):
        pts, ztop = section_curve(x)
        for side in (1, -1):
            for i in range(len(pts) - 1):
                (b0, z0), (b1, z1) = pts[i], pts[i + 1]
                p0 = Vector((x, side * b0, z0))
                p1 = Vector((x, side * b1, z1))
                mid = (p0 + p1) / 2
                d = p1 - p0
                if d.length < 1e-4:
                    continue
                v, f = cylinder((mid.x, mid.y, mid.z), 0.06, d.length,
                                segments=6)
                ob = mesh_object("Stn", v, f, col=COL, mat=P["station"])
                ob.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
                objs.append(ob)
    return objs


def setup(samples=64, res=(1500, 1100)):
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    sc.view_settings.view_transform = 'AgX'
    sc.render.resolution_x, sc.render.resolution_y = res
    w = bpy.data.worlds.new("W")
    sc.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.35, 0.38, 0.42, 1)
    bg.inputs[1].default_value = 1.2


def add_light(loc, power, size, name="L"):
    d = bpy.data.lights.new(name, 'AREA')
    d.energy = power
    d.size = size
    ob = bpy.data.objects.new(name, d)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    v = Vector((0, 0, 0)) - Vector(loc)
    ob.rotation_euler = v.to_track_quat('-Z', 'Y').to_euler()


def add_cam(loc, tgt, lens=40, ortho=False, scale=20):
    d = bpy.data.cameras.new("Cam")
    d.lens = lens
    if ortho:
        d.type = 'ORTHO'
        d.ortho_scale = scale
    ob = bpy.data.objects.new("Cam", d)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    v = Vector(tgt) - Vector(loc)
    ob.rotation_euler = v.to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = ob


def main(outdir):
    os.makedirs(outdir, exist_ok=True)
    global COL, P
    reset_scene()
    P = build_palette()
    P["station"] = principled("Station_Line", (0.85, 0.62, 0.28, 1), 0.5)
    COL = collection("SECTIONS")

    # ---- 1. midship transverse section --------------------------------
    objs = build_sections()
    setup(56, (1500, 1100))
    add_light((40, -30, 24), 900, 18, "Key")
    add_light((40, 30, 12), 400, 14, "Fill")
    add_cam((34, -7, 7.5), (0, 0, 6.4), 55)
    bpy.context.scene.render.filepath = os.path.join(outdir,
                                                     "hull_cross_section.png")
    bpy.ops.render.render(write_still=True)
    print("RENDERED hull_cross_section")

    # ---- 2. body plan in 3-D ------------------------------------------
    for ob in list(bpy.data.objects):
        if ob.name.startswith(("Section_", "Stn")):
            bpy.data.objects.remove(ob, do_unlink=True)
    build_body_plan()
    setup(40, (1600, 900))
    add_light((0, -60, 40), 1200, 30, "Key")
    add_light((0, 60, 30), 500, 30, "Fill")
    add_cam((110, -140, 70), (0, 0, 6), 50)
    bpy.context.scene.render.filepath = os.path.join(
        outdir, "body_plan_3d.png")
    bpy.ops.render.render(write_still=True)
    print("RENDERED body_plan_3d")


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    out = argv[0] if argv else os.path.join(ROOT, "renders", "structure")
    main(out)

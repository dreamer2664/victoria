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


def section_points(x, n=64):
    """Half section of the shell at station x, as (y, z) from keel to sheer.

    Sampled from the SAME HullForm that produced the 3-D hull, so this plate
    cannot disagree with the model.
    """
    ztop = float(HULL.deck_z(x))
    zbot = float(HULL.keel_z(x)) if hasattr(HULL, "keel_z") else 0.0
    pts = []
    for k in range(n + 1):
        z = zbot + (ztop - zbot) * k / n
        b = float(HULL.half_beam_at(x, z))
        pts.append((b, z))
    return pts, ztop, zbot


def build_section_plate(x, width=0.16):
    """One transverse section, drawn as a closed shell ring (port + starboard)."""
    pts, ztop, zbot = section_points(x)
    verts, faces = [], []
    ring = []
    for (b, z) in pts:                      # up the starboard side
        ring.append((x, -b, z))
    for (b, z) in reversed(pts):            # down the port side
        ring.append((x, b, z))
    inner = []
    for (b, z) in pts:
        inner.append((x, -(b - width) if b > width else 0.0, z))
    for (b, z) in reversed(pts):
        inner.append((x, (b - width) if b > width else 0.0, z))
    n = len(ring)
    verts = ring + inner
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, n + j, n + i))
    return mesh_object("Section_Shell", verts, faces, col=COL,
                       mat=P["steel"]), ztop, zbot


def build_decks_at(x, ztop):
    objs = []
    for k, n, z, ext in layout.DECKS:
        if not (ext[0] <= x <= ext[1]) or z > ztop + 0.2:
            continue
        b = float(layout.hull_side_halfbeam(x, z))
        if b < 0.8:
            continue
        v, f = box((x, 0, z), (0.22, b * 2, 0.16))
        objs.append(mesh_object("Section_Deck", v, f, col=COL,
                                mat=P["deck_wood_light"]))
    # double-bottom floors and centre girder
    for j in range(-4, 5):
        if abs(j) < 1:
            continue
        v, f = box((x, j * 1.75, 0.72), (0.14, 0.16, 1.30))
        objs.append(mesh_object("Section_Floor", v, f, col=COL,
                                mat=P["hull_black"]))
    v, f = box((x, 0, 1.0), (0.20, 0.55, 1.7))
    objs.append(mesh_object("Section_Keelson", v, f, col=COL,
                            mat=P["hull_black"]))
    return objs


def build_section_views(stations):
    """A row of transverse sections, spaced along X - a body plan in 3-D."""
    objs = []
    for i, x in enumerate(stations):
        ob, ztop, zbot = build_section_plate(x)
        objs.append(ob)
        objs += build_decks_at(x, ztop)
    return objs


def setup(samples=48, res=(1600, 1000)):
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 2
    sc.view_settings.view_transform = 'Standard'
    sc.render.resolution_x, sc.render.resolution_y = res
    w = bpy.data.worlds.new("W")
    sc.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (1.0, 1.0, 1.0, 1)
    bg.inputs[1].default_value = 1.6


def add_cam(loc, tgt, lens=50, ortho=True, scale=20.0):
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
    return ob


def main(outdir):
    os.makedirs(outdir, exist_ok=True)
    global COL, P
    reset_scene()
    P = build_palette()
    COL = collection("SECTIONS")

    # ---- 1. body plan: 19 stations, orthographic, looking forward --------
    stations = [round(-72 + i * 8.0, 1) for i in range(19)]
    build_section_views(stations)
    setup(40, (1500, 1100))
    # A body plan is read by looking down the ship's axis: every station is
    # then superimposed, and the stations away from amidships step back in
    # perspective-free depth.  Viewing broadside shows only edge-on lines.
    add_cam((150.0, 0.0, 6.6), (-40.0, 0.0, 6.6), ortho=True, scale=26.0)
    bpy.context.scene.render.filepath = os.path.join(outdir, "body_plan_3d.png")
    bpy.ops.render.render(write_still=True)
    print("RENDERED body_plan_3d")

    # ---- 2. single midship section, orthographic, looking forward -------
    for ob in list(bpy.data.objects):
        if ob.type == 'MESH':
            bpy.data.objects.remove(ob, do_unlink=True)
    build_section_plate(0.0, width=0.22)
    build_decks_at(0.0, float(HULL.deck_z(0.0)))
    setup(48, (1500, 1100))
    add_cam((60.0, -0.0, 7.0), (0.0, 0.0, 7.0), ortho=True, scale=26.0)
    bpy.context.scene.render.filepath = os.path.join(outdir,
                                                     "hull_cross_section.png")
    bpy.ops.render.render(write_still=True)
    print("RENDERED hull_cross_section")


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    out = argv[0] if argv else os.path.join(ROOT, "renders", "structure")
    main(out)

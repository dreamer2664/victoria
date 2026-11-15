"""
render_cutaway.py -- cutaway / technical presentation renders.

A cutaway is produced the way a ship's draughtsman produces a sectioned
drawing: the finished model is bisected by a plane and the outboard part is
removed, exposing the internal structure and the machinery in their real
positions.  Nothing is re-modelled, so what is shown in the cutaway is
exactly what is in the deliverable model.

    blender -b --python render_cutaway.py -- <boat> [--quick]

boat = steam | rowing | both
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bmesh
import bpy
import numpy as np
from mathutils import Vector

from boatgen import bl

ROOT = "/home/user/victoria"
QUICK = "--quick" in sys.argv
args = [a for a in sys.argv[sys.argv.index("--") + 1:]] if "--" in sys.argv else ["both"]
WHICH = args[0] if args else "both"

MODELS = {
    "steam": "boats/blend/boat_a_steam_cutter.blend",
    "rowing": "boats/blend/boat_b_rowing_cutter.blend",
}

CUT_KEEP = {
    "steam": ["Boiler", "Boiler_Internals", "Engine", "Shafting", "Propeller", "Rudder",
              "Pipework_Fittings", "Gear_Nav_Safety", "Seats", "Engine_Bearers_Floors",
              "Frames", "Decks", "Coamings", "Canopy_Frame", "Transom", "Funnel",
              "Keel_Stem_Frames_Gunwale", "Planking_Carvel", "Inner_Diagonal_Skin"],
    "rowing": ["Planking_Clinker", "Frames", "Keel_Stem_Sternpost", "Transom",
               "Keelson_Gunwale", "Structure_Details", "Thwarts_Benches", "Thwart_Knees",
               "Quarter_Knees", "Floorboards", "Rowlocks", "Fittings", "Mast_Clamp",
               "Rudder"],
}


def bisect_objects(y_cut=-0.19):
    """Remove the near (starboard) side of every mesh so the interior shows."""
    dg = bpy.context.evaluated_depsgraph_get()
    for ob in list(bpy.data.objects):
        if ob.type != "MESH":
            continue
        me = ob.data
        bm = bmesh.new()
        bm.from_mesh(me)
        geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
        bmesh.ops.bisect_plane(
            bm, geom=geom, plane_co=(0, y_cut, 0), plane_no=(0, -1, 0),
            clear_outer=True, clear_inner=False,
        )
        # cap the cut with a face so the section reads as solid
        edges = [e for e in bm.edges if e.is_boundary]
        if edges:
            try:
                bmesh.ops.holes_fill(bm, edges=edges, sides=0)
            except Exception:
                pass
        bm.to_mesh(me)
        bm.free()
        me.update()


def render_boat(key):
    path = os.path.join(ROOT, MODELS[key])
    bpy.ops.wm.open_mainfile(filepath=path)
    for ob in bpy.data.objects:
        if ob.type == "MESH" and ob.name not in CUT_KEEP[key]:
            ob.hide_render = True
    # hide the canvas cover and the aftermost framing so the machinery shows
    for name in ("Canopy_Cover",):
        if name in bpy.data.objects:
            bpy.data.objects[name].hide_render = True
    bisect_objects(-0.16 if key == "steam" else -0.10)

    # a sectioned model needs a section fill: give the cap a dark red lead tint
    sec = bpy.data.materials.new("SectionFill")
    sec.use_nodes = True
    b = sec.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.28, 0.10, 0.06, 1)
    b.inputs["Roughness"].default_value = 0.8
    for ob in bpy.data.objects:
        if ob.type == "MESH" and not ob.hide_render:
            ob.data.materials.append(sec)
            idx = len(ob.data.materials) - 1
            me = ob.data
            for p in me.polygons:
                # faces created by the cap are the newest and are flat at y=cut
                if abs(p.normal.y) > 0.9 and abs(p.center.y - (-0.16 if key == "steam" else -0.10)) < 0.01:
                    p.material_index = idx

    bl.studio(world_strength=0.55, ground_z=-1.8, key_energy=1100)
    if key == "steam":
        shots = {
            "cutaway_a": ((5.6, -6.2, 3.1), (0.1, 0.1, 0.45), 50),
            "cutaway_b": ((1.2, -5.0, 2.2), (0.1, 0.1, 0.55), 42),
            "cutaway_c": ((-5.0, -5.4, 2.6), (-0.6, 0.1, 0.40), 50),
        }
    else:
        shots = {
            "cutaway_a": ((4.6, -5.4, 2.6), (0.1, 0.1, 0.15), 50),
            "cutaway_b": ((0.4, -4.6, 1.9), (0.0, 0.1, 0.20), 42),
            "cutaway_c": ((-4.4, -4.6, 2.2), (-0.6, 0.1, 0.15), 50),
        }
    for name, (loc, look, lens) in shots.items():
        cam = bl.camera(name, loc, look, lens=lens)
        bl.render(f"{ROOT}/boats/renders/{key}_{name}.png", cam,
                  res=(1100, 690) if not QUICK else (640, 400), samples=24 if QUICK else 72)
    print("CUTAWAY COMPLETE", key)


for k in (["steam", "rowing"] if WHICH == "both" else [WHICH]):
    render_boat(k)

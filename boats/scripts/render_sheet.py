"""
render_sheet.py -- the published multi-angle render set for each boat.

Opens the finished .blend, frames every camera from the real bounding box of
the model, and writes a consistent set of views so the two boats can be
compared side by side.

    blender -b --python render_sheet.py -- [steam|rowing|both] [--quick]
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bpy
from mathutils import Vector

from boatgen import bl

ROOT = "/home/user/victoria"
ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
QUICK = "--quick" in ARGS
ARGS = [a for a in ARGS if not a.startswith("--")]
WHICH = ARGS[0] if ARGS else "both"

BLENDS = {
    "steam": "boats/blend/boat_a_steam_cutter.blend",
    "rowing": "boats/blend/boat_b_rowing_cutter.blend",
}

# direction vectors are from the boat towards the camera
VIEWS = {
    "hero": dict(direction=(0.62, -0.72, 0.34), lens=72, look=(0, 0, 0.10)),
    "broadside": dict(direction=(0.0, -1.0, 0.045), lens=85, look=(0, 0, 0.16)),
    "bow_quarter": dict(direction=(0.88, -0.46, 0.22), lens=72, look=(0.9, 0, 0.14)),
    "stern_quarter": dict(direction=(-0.86, -0.50, 0.26), lens=72, look=(-0.9, 0, 0.14)),
    "from_above": dict(direction=(0.18, -0.36, 1.0), lens=68, look=(0, 0, 0.10)),
    "bow_on": dict(direction=(1.0, -0.16, 0.10), lens=85, look=(1.4, 0, 0.20)),
}


def setup_grade():
    sc = bpy.context.scene
    sc.view_settings.view_transform = "AgX"
    try:
        sc.view_settings.look = "AgX - Medium High Contrast"
    except Exception:
        pass
    sc.view_settings.exposure = 0.20
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.use_denoising = True
    sc.render.film_transparent = False


def render_boat(key):
    bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT, BLENDS[key]))
    # drop any cameras/lights from the build so the studio set is the only one
    for ob in list(bpy.data.objects):
        if ob.type in {"CAMERA", "LIGHT"}:
            bpy.data.objects.remove(ob, do_unlink=True)
    for ob in list(bpy.data.objects):
        if ob.name == "Backdrop":
            bpy.data.objects.remove(ob, do_unlink=True)

    sc = bpy.context.scene
    sc.world = None
    # a sea surface at the load waterline, lit by a soft overcast sky: the boat
    # then floats at exactly the draught the hydrostatics published
    bl.sea_studio()
    bl.water_plane(0.0, 4000.0)
    setup_grade()

    for name, v in VIEWS.items():
        cam = bl.frame_camera(f"{key}_{name}", v["direction"], look_at=v["look"],
                              lens=v["lens"], margin=1.10, aspect=1.55)
        bl.render(f"{ROOT}/boats/renders/{key}_{name}.png",
                  cam, res=(720, 465) if QUICK else (1240, 800),
                  samples=16 if QUICK else 88)

    # a machinery / interior detail view
    if key == "steam":
        bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT, BLENDS[key]))
        for ob in list(bpy.data.objects):
            if ob.type in {"CAMERA", "LIGHT"}:
                bpy.data.objects.remove(ob, do_unlink=True)
        for ob in list(bpy.data.objects):
            if ob.name == "Backdrop":
                bpy.data.objects.remove(ob, do_unlink=True)
        if "Canopy_Cover" in bpy.data.objects:
            bpy.data.objects["Canopy_Cover"].hide_render = True
        sc = bpy.context.scene
        sc.world = None
        bl.sea_studio(world_strength=2.3, key_energy=460.0)
        bl.water_plane(0.0, 4000.0)
        setup_grade()
        cam = bl.frame_camera("steam_machinery", (0.55, -0.80, 0.42),
                              look_at=(0.0, 0, 0.75), lens=62, margin=0.62, aspect=1.55)
        cam.location = cam.location * 0.86
        bl.render(f"{ROOT}/boats/renders/steam_machinery.png", cam,
                  res=(720, 465) if QUICK else (1240, 800),
                  samples=16 if QUICK else 88)
    print("SHEET COMPLETE", key)


for k in (["steam", "rowing"] if WHICH == "both" else [WHICH]):
    render_boat(k)

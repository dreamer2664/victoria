"""
render2.py -- THEMISTOCLES-II render driver.

Usage:
  blender -b <blend> --python render2.py -- --out <dir> --prefix rowing2 \
      [--views hero,broadside,...] [--quick] [--hide "Planking*|Sea"] \
      [--only "Engine|Boiler"] [--target x,y,z] [--sea 0]
Views are framed from the bounds of the visible boat parts (no hand-placed
cameras):  camera = bounds_centre + direction * fitted_distance.
"""
import os, sys, re, math, json
import numpy as np
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from them2 import bl2

VIEWS = {
    "broadside":      dict(dir=(0.02, -1.0, 0.16), lens=58, margin=1.10, hint=None),
    "bow_quarter":    dict(dir=(1.0, -0.95, 0.52), lens=52, margin=1.15),
    "stern_quarter":  dict(dir=(-1.0, -0.85, 0.48), lens=52, margin=1.15),
    "bow_on":         dict(dir=(1.0, 0.0, 0.14), lens=62, margin=1.10),
    "stern_on":       dict(dir=(-1.0, 0.0, 0.18), lens=62, margin=1.10),
    "top":            dict(dir=(0.10, 0.0, 1.0), lens=52, margin=0.95),
    "underside":      dict(dir=(0.55, -0.75, -1.0), lens=52, margin=1.20),
    "interior":       dict(dir=(0.35, -0.75, 1.0), lens=46, margin=0.85),
    "hero":           dict(dir=(0.9, -1.05, 0.50), lens=54, margin=1.14),
    "profile_high":   dict(dir=(0.25, -1.0, 0.55), lens=60, margin=1.15),
    "construction":   dict(dir=(0.75, -0.85, 0.60), lens=50, margin=1.20),
}


def scene_bounds():
    lo = np.array([1e9] * 3)
    hi = -lo.copy()
    for o in bpy.context.scene.objects:
        if o.type != 'MESH' or o.hide_render or not o.visible_get():
            continue
        if o.name.startswith("TM2_"):
            continue
        mw = np.array(o.matrix_world)
        for c in o.bound_box:
            v = mw[:3, :3] @ np.array(c) + mw[:3, 3]
            lo = np.minimum(lo, v)
            hi = np.maximum(hi, v)
    return lo, hi


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--prefix", default="boat")
    ap.add_argument("--views", default="broadside,bow_quarter,stern_quarter,bow_on,top,underside,interior,hero")
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--hide", default="")
    ap.add_argument("--only", default="")
    ap.add_argument("--target", default="")
    ap.add_argument("--sea", type=int, default=1)
    ap.add_argument("--studio", type=int, default=1)
    ap.add_argument("--res", default="")
    args = ap.parse_args(argv)

    s = bpy.context.scene
    bpy.data.objects.remove(bpy.data.objects.get("TM2_Studio_BG"), do_unlink=True) if bpy.data.objects.get("TM2_Studio_BG") else None
    pats_hide = [re.compile(p) for p in args.hide.split("|") if p] if args.hide else []
    pat_only = re.compile(args.only) if args.only else None
    for o in s.objects:
        if o.type != 'MESH':
            continue
        if o.name.startswith("TM2_"):
            continue
        hide = False
        if pat_only and not pat_only.search(o.name):
            hide = True
        if not hide and any(p.search(o.name) for p in pats_hide):
            hide = True
        o.hide_render = hide
        o.hide_viewport = hide

    rig = bl2.RenderRig(s, sea=bool(args.sea),
                        res=(960, 600) if args.quick else (1360, 850),
                        samples=16 if args.quick else 56,
                        studio=bool(args.studio))
    if not args.sea:
        bl2.set_sea_visible(False)

    lo, hi = scene_bounds()
    centre = (lo + hi) / 2
    radius = float(np.linalg.norm(hi - lo) / 2)

    os.makedirs(args.out, exist_ok=True)
    views = [v for v in args.views.split(",") if v]
    boat_objs = [o for o in bpy.context.scene.objects
                 if o.type == 'MESH' and not o.name.startswith("TM2_")]
    for vname in views:
        v = VIEWS[vname]
        tgt = centre
        if args.target:
            tgt = np.array([float(x) for x in args.target.split(",")])
        lift = 0.0
        saved_world_col = None
        if vname == "underside":
            # hoist the boat clear of the floor so the below-camera sees the run
            lift = max(1.6, (hi[2] - lo[2]) * 1.6)
            for o in boat_objs:
                o.location.z += lift
            tgt = centre + np.array([0, 0, lift])
            # remove the studio shell + brighten the world for the low camera
            for nm in ("TM2_Studio_BG", "TM2_Sea"):
                ob = bpy.data.objects.get(nm)
                if ob:
                    ob.hide_render = True
            w = bpy.context.scene.world
            if w and w.use_nodes:
                for node in w.node_tree.nodes:
                    if node.bl_idname == "ShaderNodeMixShader":
                        bg = node.inputs[2].links[0].from_node \
                            if node.inputs[2].is_linked else None
                        if bg is not None:
                            saved_world_col = tuple(bg.inputs[0].default_value)
                            bg.inputs[0].default_value = (0.28, 0.34, 0.42, 1.0)
                            bg.inputs[1].default_value = 1.0
        rig.camera(tgt, v["dir"], lens=v.get("lens", 54),
                   margin=v.get("margin", 1.15), size_hint=radius)
        rig.render(os.path.join(args.out, f"{args.prefix}_{vname}.png"))
        if lift:
            for o in boat_objs:
                o.location.z -= lift
            for nm in ("TM2_Studio_BG", "TM2_Sea"):
                ob = bpy.data.objects.get(nm)
                if ob:
                    ob.hide_render = False
        print("RENDERED", vname)


if __name__ == "__main__":
    main()

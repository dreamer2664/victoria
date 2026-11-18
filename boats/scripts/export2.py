"""
export2.py -- export every part of a built boat to GLB + FBX and write the
per-boat spec JSON (hydrostatics, pivots, weights, principal dims) for the
Roblox client and the LEONIDAS-II integration spec.

Usage: blender -b <blend> --python export2.py -- --out <dir> --meta <meta.json>
                                                  --class rowing_cutter_25ft
"""
import os, sys, json, math
import numpy as np
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from them2 import bl2


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--meta", required=True)
    ap.add_argument("--cls", required=True)
    ap.add_argument("--limit", type=int, default=19000)
    args = ap.parse_args(argv)

    os.makedirs(args.out, exist_ok=True)
    with open(args.meta) as f:
        meta = json.load(f)

    parts = {}
    combined = []
    for o in bpy.context.scene.objects:
        if o.type != 'MESH' or o.name.startswith("TM2_"):
            continue
        o.hide_set(False)
    objs = [o for o in bpy.context.scene.objects
            if o.type == 'MESH' and not o.name.startswith("TM2_")]
    for o in objs:
        o.name = o.name.replace("|", "_").replace(" ", "_")
        m = bl2.export_part(o, args.out, o.name.lower(), decimate_limit=args.limit)
        parts[o.name] = m["parts"][0]
    # combined single-mesh boat
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=os.path.join(args.out, args.cls + ".glb"),
                              export_format='GLB', use_selection=True, export_yup=True)
    bpy.ops.export_scene.fbx(filepath=os.path.join(args.out, args.cls + ".fbx"),
                             use_selection=True, axis_forward='-Z', axis_up='Y')

    spec = {
        "class": args.cls,
        "frame_of_reference": {
            "origin": "design waterline amidships (Z=0 = LOADED waterline this generation)",
            "axes": "+X = bow, +Y = starboard, +Z = up",
            "units": "metres",
        },
        "hydrostatics": {"loaded": meta["loaded"], "light": meta["light"]},
        "weights_kg": meta["weights"],
        "pivots": meta["pivots"],
        "parts": parts,
    }
    with open(os.path.join(args.out, args.cls + "_export_meta.json"), "w") as f:
        json.dump(spec, f, indent=2)
    tot_tris = sum(p["triangles"] for p in parts.values())
    print("EXPORTED", args.cls, len(parts), "parts,", tot_tris, "tris total")


if __name__ == "__main__":
    main()

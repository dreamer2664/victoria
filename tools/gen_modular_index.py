#!/usr/bin/env python3
"""
gen_modular_index.py -- writes assets/modular/index.json, the modular kit catalogue.

For every prototype it records the measured bounding box in metres, the triangle
count, the instance count, the GLB filename and the documented connection
convention. This is the machine-readable companion to README.md section 4.

    blender -b --factory-startup -noaudio --python tools/gen_modular_index.py
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "blender", "lib"))
sys.path.insert(0, os.path.join(ROOT, "blender", "ports"))
sys.path.insert(0, os.path.join(ROOT, "blender"))

import bpy
import bsetup
import portsite as site

# class -> (connection point, convention)
KIT_CLASS = {
    "quay": ("coping line, centre of the 24 m module",
             "place at 24 m centres along a water edge; rz chooses which way the land lies"),
    "bldg": ("SW footprint corner at world 0, door on the street side",
             "footprint rectangle is authoritative; doors face the street named in meta"),
    "crane": ("base plate centre at QUAY_Z", "rz = working direction; +X is the crane's reach"),
    "bollard": ("base plate centre at QUAY_Z", "16-20 m centres along a berth"),
    "lamp": ("base plate centre at QUAY_Z", "26-44 m centres along a street"),
    "slip": ("origin at the low (water) end", "rz=-90 turns the ways onto an E-W frontage"),
    "dock": ("SW corner of the dock rectangle", "depth is measured DOWN FROM THE COPING"),
    "rail": ("first sleeper centre at QUAY_Z", "runs along +X or +Z of the prototype"),
    "stack": ("base centre at QUAY_Z", "free placement, keep 1 m from a wall"),
}

PREFIX_CLASS = [
    ("quay", "quay"), ("bollard", "bollard"), ("capstan", "bollard"),
    ("lamp", "lamp"), ("pole", "lamp"), ("crane", "crane"), ("titan", "crane"),
    ("sheerlegs", "crane"), ("staithe", "stack"), ("coalhoist", "crane"),
    ("slip", "slip"), ("dock", "dock"), ("rail", "rail"),
    ("timber", "stack"), ("plates", "stack"), ("cargo", "stack"), ("wagon", "rail"),
    ("ground", "quay"),
]


def classify(name):
    low = name.lower()
    for prefix, cls in PREFIX_CLASS:
        if prefix in low:
            return cls
    return "bldg"


def main():
    index = {"scale": {"studs_per_metre": 1 / 0.28, "note": "1 Roblox stud = 0.28 m"},
             "ports": {}}

    for port, modname in (("a", "port_a"), ("b", "port_b")):
        sc = bsetup.reset_scene()
        bsetup.make_materials()
        coll = bsetup.ensure_coll("KIT")
        R = bsetup.Registry()
        audit = site.LayoutAuditor()
        mod = __import__(modname)
        meta = mod.build(R, coll, audit)

        entries = []
        for name, ob in sorted(R.proto.items()):
            me = ob.data
            if not len(me.vertices):
                continue
            xs = [v.co.x for v in me.vertices]
            ys = [v.co.y for v in me.vertices]
            zs = [v.co.z for v in me.vertices]
            tris = sum(max(1, len(p.vertices) - 2) for p in me.polygons)
            cls = classify(name)
            conn, how = KIT_CLASS[cls]
            entries.append({
                "name": name,
                "class": cls,
                "glb": "assets/glb/%s/%s.glb" % (port, name),
                "size_m": [round(max(xs) - min(xs), 2),
                           round(max(ys) - min(ys), 2),
                           round(max(zs) - min(zs), 2)],
                "size_studs": [round((max(xs) - min(xs)) / 0.28, 1),
                               round((max(ys) - min(ys)) / 0.28, 1),
                               round((max(zs) - min(zs)) / 0.28, 1)],
                "min_m": [round(min(xs), 2), round(min(ys), 2), round(min(zs), 2)],
                "triangles": tris,
                "instances": R.counts.get(name, 0),
                "connection_point": conn,
                "connection_convention": how,
                "shipped": name != "_PROXY_liner",
            })
        index["ports"][port] = {"name": meta["port"], "prototypes": entries,
                                "count": len(entries)}

    out = os.path.join(ROOT, "assets", "modular", "index.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(index, open(out, "w"), indent=1)
    for p, d in index["ports"].items():
        print("port %s: %d prototypes, %d instances"
              % (p, d["count"], sum(e["instances"] for e in d["prototypes"])))
    print("wrote", out)


if __name__ == "__main__" or True:
    main()

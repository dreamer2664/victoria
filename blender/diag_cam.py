"""Report what a camera actually sees: first hit + divergence of rays."""
import bpy, sys, os
from mathutils import Vector
ROOT = "/home/user/victoria"
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "blender"))
from shipdesign.spec import DECK_Z
from shipdesign import layout

def first_hit(loc, direction, skip=()):
    best = None
    d = Vector(direction).normalized()
    for ob in bpy.data.objects:
        if ob.type != 'MESH' or ob.name in skip:
            continue
        inv = ob.matrix_world.inverted()
        o = inv @ Vector(loc); dd = (inv.to_3x3() @ d).normalized()
        try:
            ok, hit, n, i = ob.ray_cast(o, dd)
        except Exception:
            continue
        if ok:
            p = ob.matrix_world @ hit
            dist = (p - Vector(loc)).length
            if best is None or dist < best[0]:
                best = (dist, ob.name, tuple(round(c, 2) for c in p))
    return best

def report(name, deck, dz, loc, tgt):
    z = DECK_Z[deck]; ceil = layout.room_ceiling_z(deck)[1]
    L = (loc[0], loc[1], min(z + dz, ceil - 0.2))
    T = (tgt[0], tgt[1], z + tgt[2] if len(tgt) > 2 else z)
    h = first_hit(L, (Vector(T) - Vector(L)))
    print("%-18s deck %-7s z=%.2f ceil=%.2f  cam=%s  first hit: %s"
          % (name, deck, z, ceil, tuple(round(c,2) for c in L), h))

report("library", "prom", 1.70, (25.0, -1.2), (12.0, 0.0))
report("grand_stair", "saloon", 1.70, (8.6, -2.0), (-4.0, 0.4))
report("smoking", "prom", 1.70, (-11.0, -2.4), (-22.0, 0.0))
report("dining", "saloon", 1.65, (-10.0, -1.0), (-42.0, 0.0))

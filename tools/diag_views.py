import bpy, sys
sys.path.insert(0, "/home/user/victoria")
sys.path.insert(0, "/home/user/victoria/blender")
import render_interiors as R
from mathutils import Vector

for n in ("stateroom", "third_class", "galley"):
    v = R.VIEWS[n]
    L = v["loc"]; T = v["target"]
    d = (Vector(T) - Vector(L)).normalized()
    best = None
    for ob in bpy.data.objects:
        if ob.type != 'MESH':
            continue
        inv = ob.matrix_world.inverted()
        try:
            ok, h, nn, i = ob.ray_cast(inv @ Vector(L),
                                       (inv.to_3x3() @ d).normalized())
        except Exception:
            continue
        if ok:
            p = ob.matrix_world @ h
            dist = (p - Vector(L)).length
            if best is None or dist < best[0]:
                best = (round(dist, 2), ob.name)
    print(n, "loc", [round(c, 2) for c in L], "tgt", [round(c, 2) for c in T],
          "hit", best)

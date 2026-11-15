import bpy, sys
sys.path.insert(0, "/home/user/victoria")
sys.path.insert(0, "/home/user/victoria/blender")
from mathutils import Vector
from shipdesign.spec import DECK_Z

for deck, x in (("saloon", 17.0), ("saloon", -50.0), ("main", 20.0),
                ("prom", 20.0), ("lower", 60.0)):
    z = DECK_Z[deck]
    origin = Vector((x, 0.0, z + 2.0))       # cast DOWN from inside the room
    best = None
    for ob in bpy.data.objects:
        if ob.type != 'MESH':
            continue
        inv = ob.matrix_world.inverted()
        try:
            ok, hit, n, i = ob.ray_cast(inv @ origin, Vector((0, 0, -1)))
        except Exception:
            continue
        if ok:
            p = ob.matrix_world @ hit
            dist = (p - origin).length
            if best is None or dist < best[0]:
                best = (round(dist, 2), ob.name, round(p.z, 2))
    print("FLOOR deck=%-7s x=%6.1f  z=%.2f -> %s" % (deck, x, z, best))

"""Build the whole modular library once and render a defail sheet for inspection.

blender -b --factory-startup -noaudio --python blender/test_assets.py
"""
import os, sys, math, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "lib"))

import bpy
from mathutils import Vector
import core, bsetup, parts as P, bldg, maritime, machinery
from core import MeshBuilder

OUT = os.path.abspath(os.path.join(HERE, "..", "renders", "_tests"))
os.makedirs(OUT, exist_ok=True)

t0 = time.time()
sc = bsetup.reset_scene()
bsetup.make_materials()
coll = bsetup.ensure_coll("TEST")
print("materials:", len(bsetup._MATS))

R = bsetup.Registry()

# ---------------------------------------------------------------- definitions
def def_assets():
    mb = MeshBuilder(); bldg.warehouse(mb, 0, 0, 34, 20, floors=4, hoist_side="S",
                                       hoist_bays=(1, 4)); R.define("warehouse_A", mb, bevel=0.02)
    mb = MeshBuilder(); bldg.warehouse(mb, 0, 0, 26, 17, floors=3, wall="brick_buff",
                                       roof="hip", hoist_side="E", hoist_bays=(2,)); R.define("warehouse_B", mb, bevel=0.02)
    mb = MeshBuilder(); bldg.transit_shed(mb, 0, 0, 44, 22); R.define("transit_shed", mb, bevel=0.02)
    mb = MeshBuilder(); bldg.custom_house(mb, 0, 0, 58, 32); R.define("custom_house", mb, bevel=0.02)
    mb = MeshBuilder(); bldg.station_shed(mb, 0, 0, 52, 19); R.define("station_shed", mb, bevel=0.02)
    mb = MeshBuilder(); bldg.office_block(mb, 0, 0, 30, 16, floors=4); R.define("office_block", mb, bevel=0.02)
    mb = MeshBuilder(); bldg.pump_house(mb, 0, 0, 16, 12); R.define("pump_house", mb, bevel=0.02)
    mb = MeshBuilder(); bldg.engineering_shop(mb, 0, 0, 46, 24); R.define("engineering_shop", mb, bevel=0.02)
    mb = MeshBuilder(); bldg.moulding_loft(mb, 0, 0, 50, 18); R.define("moulding_loft", mb, bevel=0.02)
    mb = MeshBuilder(); bldg.time_office(mb, 0, 0, 9, 6.5); R.define("time_office", mb, bevel=0.02)

    mb = MeshBuilder()
    maritime.quay_wall(mb, "X", 0, 0, 40, +1)
    for i in range(4):
        maritime.bollard(mb, 5 + i * 10, 1.6, 4.0)
        maritime.capstan(mb, 8 + i * 10, 3.0, 4.0)
    R.define("quay_run", mb, bevel=0.0)

    mb = MeshBuilder(); maritime.graving_dock(mb, 0, 0, 200, 24.4); R.define("graving_dock", mb)
    mb = MeshBuilder(); maritime.caisson(mb, 0, 0, 24.4, 4.0); R.define("caisson", mb)
    mb = MeshBuilder(); maritime.slipway(mb, 0, 0, 26, 120); R.define("slipway", mb)
    mb = MeshBuilder(); maritime.pontoon(mb, 0, 0, 20, 120); R.define("pontoon", mb)
    mb = MeshBuilder(); maritime.gangway_bridge(mb, 0, 0, 4.0, 26, 1.6); R.define("gangway_bridge", mb)

    mb = MeshBuilder(); machinery.hydraulic_crane(mb, 0, 0, 4.0); R.define("crane_hydraulic", mb)
    mb = MeshBuilder(); machinery.titan_crane(mb, 0, 0, 4.0); R.define("titan_crane", mb)
    mb = MeshBuilder(); machinery.coal_hoist(mb, 0, 0, 4.0); R.define("coal_hoist", mb)
    mb = MeshBuilder(); machinery.steam_crane(mb, 0, 0, 4.0); R.define("steam_crane", mb)
    mb = MeshBuilder(); machinery.tank_loco(mb, 0, 0, 4.0); R.define("tank_loco", mb)
    mb = MeshBuilder(); machinery.wagon(mb, 0, 0, 4.0); R.define("wagon", mb)
    mb = MeshBuilder(); machinery.gas_lamp(mb, 0, 0, 4.0); R.define("gas_lamp", mb)
    mb = MeshBuilder(); machinery.telegraph_pole(mb, 0, 0, 4.0); R.define("telegraph_pole", mb)
    mb = MeshBuilder(); machinery.gangway(mb, 0, 0, 4.0, 1.0, 9.0); R.define("gangway", mb)
    mb = MeshBuilder(); machinery.rail_track(mb, 0, 0, 60, 0, 4.0); R.define("rail_track", mb)


def_assets()
print("defined prototypes:", len(R.proto))
tot_v = 0
for n, ob in R.proto.items():
    me = ob.data
    tris = sum(max(1, len(p.vertices) - 2) for p in me.polygons)
    tot_v += tris
    print(f"  {n:18s} verts={len(me.vertices):6d} tris={tris:6d}")
print("library tris total:", tot_v)

# ---------------------------------------------------------------- lay out a strip
for i, name in enumerate([n for n in R.proto]):
    pass
layout = [
    ("warehouse_A", 0, 0, 0), ("warehouse_B", 40, 0, 0), ("transit_shed", 72, 0, 0),
    ("custom_house", 124, 0, 0), ("office_block", 0, 60, 0), ("station_shed", 36, 60, 0),
    ("pump_house", 95, 60, 0), ("engineering_shop", 120, 60, 0),
    ("moulding_loft", 0, 120, 0), ("time_office", 56, 120, 0),
    ("titan_crane", 80, 130, 0), ("crane_hydraulic", 100, 130, 0), ("steam_crane", 112, 130, 0),
    ("coal_hoist", 126, 130, 0), ("tank_loco", 145, 128, 0), ("wagon", 145, 138, 0),
    ("gas_lamp", 90, 150, 0), ("telegraph_pole", 96, 150, 0), ("gangway", 104, 150, 0),
    ("quay_run", 0, 165, 0),
]
for n, x, y, rz in layout:
    R.place(n, x, y, 0, rz)

# ground
bsetup.add_ground(coll, -40, -40, 220, 220, z=-0.05, matname="setts")
bsetup.add_sun(coll, 145, 40, 3.2)
bsetup.setup_world(0.30)
bsetup.setup_compositor_haze()

print("build time", round(time.time() - t0, 1), "s")

# ---------------------------------------------------------------- render
cams = [
    ("lib_overview", (74, -105, 62), (72, 80, 8), 30),
    ("lib_warehouse", (28, -34, 14), (34, 6, 10), 42),
    ("lib_civic", (128, -46, 18), (152, 12, 14), 40),
    ("lib_industry", (72, 96, 22), (128, 70, 10), 35),
]
for name, loc, la, lens in cams:
    c = bsetup.add_camera(coll, loc, la, lens, name)
    p = bsetup.render_to(os.path.join(OUT, name + ".png"), c,
                         res=(1280, 720), samples=40)
    print("rendered", p, round(time.time() - t0, 1), "s")
print("DONE", round(time.time() - t0, 1))

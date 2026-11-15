"""Fast low-res iteration render: builds a couple of assets and shoots them.

blender -b --factory-startup -noaudio --python blender/quick.py
"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "lib"))
import bpy, bsetup, bldg, maritime, machinery
from core import MeshBuilder

OUT = "/tmp/q"
sc = bsetup.reset_scene()
bsetup.make_materials()
coll = bsetup.ensure_coll("Q")
R = bsetup.Registry()

mb = MeshBuilder(); bldg.warehouse(mb, 0, 0, 34, 20, floors=4, hoist_bays=(1, 4)); R.define("wh", mb, bevel=0.02)
mb = MeshBuilder(); bldg.custom_house(mb, 0, 0, 58, 32); R.define("ch", mb, bevel=0.02)
mb = MeshBuilder(); bldg.transit_shed(mb, 0, 0, 40, 20); R.define("ts", mb, bevel=0.02)
mb = MeshBuilder()
maritime.quay_wall(mb, "X", 0, 0, 40, +1)
for i in range(4):
    maritime.bollard(mb, 5 + i * 10, 1.6, 4.0)
R.define("q", mb)
mb = MeshBuilder(); machinery.hydraulic_crane(mb, 0, 0, 4.0); R.define("cr", mb)

R.place("wh", 0, 0); R.place("ch", 46, 0); R.place("ts", 0, 34)
R.place("q", 0, -30); R.place("cr", -8, -22, 4.0)
bsetup.add_ground(coll, -60, -70, 160, 120, z=-0.05, matname="setts")
bsetup.add_water(coll, -60, -70, 160, -31, z=0.0)
bsetup.add_sun(coll, 280, 30, 3.6)
bsetup.add_fill(coll, 95, 26, 1.25)
bsetup.setup_world(1.05)
bsetup.setup_compositor_haze()
for i, (loc, la, lens) in enumerate([
        ((10, -52, 12), (24, 10, 8), 40),
        ((-20, -20, 6), (5, 5, 9), 35),
        ((30, 60, 30), (30, 10, 6), 40)]):
    c = bsetup.add_camera(coll, loc, la, lens, "c%d" % i)
    bsetup.render_to(os.path.join(OUT, "q%d.png" % i), c, res=(900, 506), samples=24)
print("done")

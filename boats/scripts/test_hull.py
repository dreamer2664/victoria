"""test_hull.py -- rapid form check for the two hulls (development tool)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bpy

from boatgen import bl
from boatgen.geom import MeshBuilder
from boatgen.hull import MAT, HullDesign, build_clinker_planking, build_frames, build_gunwale, build_keel

OUT = "/home/user/victoria/boats/renders/_wip"

designs = {
    "rowing": HullDesign(
        "rowing_cutter",
        loa=7.620,
        bmax=0.950,
        sheer_pts=[(0.0, 0.720), (0.08, 0.655), (0.20, 0.575), (0.35, 0.525),
                   (0.55, 0.500), (0.75, 0.505), (0.90, 0.545), (1.0, 0.600)],
        keel_pts=[(0.0, 0.330), (0.06, 0.090), (0.14, -0.180), (0.24, -0.400),
                  (0.36, -0.545), (0.50, -0.575), (0.62, -0.565), (0.74, -0.490),
                  (0.84, -0.360), (0.92, -0.160), (1.0, 0.060)],
        hb_pts=[(0.0, 0.030), (0.10, 0.460), (0.25, 0.780), (0.40, 0.940),
                (0.55, 1.000), (0.70, 0.960), (0.85, 0.820), (0.95, 0.620), (1.0, 0.430)],
        full_fwd=1.10, full_aft=1.85, round_fwd=1.45, round_aft=2.20,
        flare_fwd=0.09, flare_aft=0.02, stem_rake=0.09, stern_rake=0.16,
    ),
    "steam": HullDesign(
        "steam_cutter",
        loa=7.620,
        bmax=1.105,
        sheer_pts=[(0.0, 0.760), (0.10, 0.680), (0.30, 0.575), (0.55, 0.520),
                   (0.75, 0.520), (0.90, 0.560), (1.0, 0.640)],
        keel_pts=[(0.0, 0.300), (0.07, 0.050), (0.18, -0.290), (0.32, -0.560),
                  (0.50, -0.660), (0.66, -0.650), (0.80, -0.520), (0.90, -0.330),
                  (1.0, -0.010)],
        hb_pts=[(0.0, 0.055), (0.09, 0.500), (0.22, 0.820), (0.40, 0.970),
                (0.58, 1.000), (0.75, 0.985), (0.88, 0.900), (1.0, 0.600)],
        full_fwd=1.25, full_aft=2.05, round_fwd=1.50, round_aft=2.45,
        flare_fwd=0.11, flare_aft=0.03, stem_rake=0.11, stern_rake=0.20,
        transom_frac=0.58,
    ),
}

which = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else "rowing"
hull = designs[which]

bl.reset_scene()
mats = bl.build_materials()
mlist = bl.mats_list(mats)
col = bl.collection("Hull")

mb = MeshBuilder("planking")
build_clinker_planking(mb, hull, n_strakes=11, thickness=0.016, lap=0.007)
mb.mirror_y()
bl.obj_from_builder(mb, "Planking", mlist, col)

mb = MeshBuilder("gunwale")
build_gunwale(hull, mb, mat=MAT["wood_timber"])
build_keel(hull, mb)
mb.mirror_y()
bl.obj_from_builder(mb, "Gunwale_Keel", mlist, col)

mb = MeshBuilder("frames")
build_frames(mb, hull, spacing=0.14, plank_thickness=0.016)
mb.mirror_y()
bl.obj_from_builder(mb, "Frames", mlist, col)

print("VERTS", sum(len(o.data.vertices) for o in col.objects),
      "FACES", sum(len(o.data.polygons) for o in col.objects))
print("CHECK", hull.stability_check())

bl.studio(world_strength=0.55)
cams = {
    "q": bl.camera("q", (5.2, -6.6, 3.0), (0, 0, 0.05), lens=52),
    "side": bl.camera("side", (0.0, -9.0, 0.15), (0, 0, 0.15), ortho=8.4),
    "bow": bl.camera("bow", (7.4, -1.8, 1.5), (0, 0, 0.15), lens=70),
}
for k, c in cams.items():
    bl.render(f"{OUT}/{which}_{k}.png", c, res=(900, 560), samples=28)
print("DONE")

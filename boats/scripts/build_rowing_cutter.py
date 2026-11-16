"""
build_rowing_cutter.py -- BOAT B, the 25 ft clinker (lapstrake) rowing cutter.

Run headless:
    blender -b --python build_rowing_cutter.py -- [--quick] [--no-render]

Produces:
    boats/blend/boat_b_rowing_cutter.blend
    boats/exports/rowing_cutter.glb  (+ per-part GLB for moving parts)
    boats/renders/*.png

Construction evidence (see HISTORICAL_EVIDENCE.md):
  * RMG SLR1818 -- clinker ship's rowing cutter, 8 thwarts, stern and side
    benches, slatted floors, hoisting eyes on the keelson.
  * RMG SLR0772 -- 1:24 cutter c.1838, plank on frame, 5 thwarts, rudder and
    tiller, mast clamp, rowlocks cut in the top strake, 12 oars.
  * RMG J0780 -- '10-oared 25 ft Cutter' plan, Isaac Watts.
  * Kipling Society / ORG 1905 boat establishment -- cutters are double
    banked: two men to a thwart, one oar each; 25 ft cutter pulls 8-10 men.
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bpy
import numpy as np
from mathutils import Matrix, Vector

from boatgen import bl, parts, specs
from boatgen.geom import MeshBuilder, cyl, lerp, torus, unit
from boatgen.hull import (
    MAT,
    solid_between_sections,
    build_frames,
    build_gunwale,
    build_rubbing_strake,
    build_stem_band,
    build_keel,
    build_keelson,
    build_stem,
    build_sternpost,
    clear_y,
    half_breadth_at,
    build_transom,
    build_clinker_planking,
)

QUICK = "--quick" in sys.argv
NO_RENDER = "--no-render" in sys.argv
ROOT = "/home/user/victoria"
HULL = specs.ROW_CUTTER

# --------------------------------------------------------------------------
# layout
# --------------------------------------------------------------------------
XI_THWARTS = [0.235, 0.345, 0.455, 0.565, 0.675]      # 5 thwarts, 10 oars
XI_STERN_BENCH = 0.845
XI_MAST = 0.165
OAR_LEN = 3.66
CUTTER_NUMBER = "12"                                   # ship's boat number

bl.reset_scene()
mats = bl.build_materials()
mlist = bl.mats_list(mats)


def _register(m):
    """MAT values are slot indices, so a material created after the base list
    was built is appended to it and its index returned."""
    mlist.append(m)
    return len(mlist) - 1
col_hull = bl.collection("Hull")
col_structure = bl.collection("Structure")
col_furniture = bl.collection("Furniture")
col_gear = bl.collection("Gear")
col_moving = bl.collection("MovingParts")


def make(builder, name, collection, mirror=False, smooth=True, auto_smooth=35.0):
    mb = MeshBuilder(name)
    builder(mb)
    if mirror:
        mb.mirror_y()
    ob = bl.obj_from_builder(mb, name, mlist, collection, smooth=smooth,
                             auto_smooth=auto_smooth)
    print(f"  [{name}] verts={len(ob.data.vertices)} faces={len(ob.data.polygons)}")
    return ob


def origin_to(ob, pivot):
    """Move the object origin to `pivot` without moving the geometry -- so the
    part can be rotated about its real mechanical axis in Roblox."""
    pivot = Vector(pivot)
    ob.data.transform(Matrix.Translation(-pivot))
    ob.location = pivot


# --------------------------------------------------------------------------
# 1. planking -- 11 clinker strakes, bottom three painted
# --------------------------------------------------------------------------
# A working boat's bottom was painted (red lead / black) and the topsides
# varnished; three strakes of the bottom lie below the load waterline.
strake_mats = []
for k in range(11):
    f = (k + 0.5) / 11
    z = lerp(HULL.keel_z(0.5), HULL.sheer_z(0.5), f)
    if z < -0.16:
        strake_mats.append(MAT["paint_hull"])
        continue
    # Every strake is a different tree.  Give each its own slightly different
    # timber so the planking reads as eleven separate boards rather than one
    # varnished skin -- the tone shifts are small, but they are what the eye
    # actually uses to count strakes at a distance.
    v = 0.955 + 0.09 * ((k * 7) % 5) / 4.0
    warm = 1.0 + 0.06 * ((k * 3) % 4 - 1.5) / 1.5
    # Varnished clinker, strake by strake: a boat department that varnished its
    # steam cutter's topsides black and white would paint this one too, and
    # that was tried -- but the lap shadows carry the form far better over warm
    # varnished larch than under paint, and the two boats are already told apart
    # by their ends, their oars and their machinery.  Kept varnished, with the
    # strake tones varied so eleven laps do not read as one moulded shell.
    strake_mats.append(_register(bl.wood_material(
        f"Wood_Strake_{k:02d}",
        base=(0.32 * v * warm, 0.17 * v, 0.08 * v / warm),
        dark=(0.14 * v, 0.07 * v, 0.03 * v),
        rough=0.44, bump=0.24)))

make(
    lambda mb: build_clinker_planking(
        mb, HULL, n_strakes=11, thickness=0.019, lap=0.013, xi0=0.0015,
        n_xi=70, butt_length=2.9, xi1=0.9995, mat_out=strake_mats,
        mat_in=[MAT["wood_out"]] * 11,
    ),
    "Planking_Clinker",
    col_hull,
    mirror=True,
    # a clinker lap meets the strake below at a shallow angle; at the default
    # 35 degrees the shading smooths straight over it and the hull renders as
    # one skin.  At 20 the laps catch light the way overlapped planks do.
    auto_smooth=20.0,
)

# --------------------------------------------------------------------------
# 2. frames (steamed oak timbers) + structure
# --------------------------------------------------------------------------
make(lambda mb: build_frames(mb, HULL, spacing=0.142, depth=0.034, width=0.024,
                             xi0=0.028, xi1=0.972, t0=0.015, t1=0.955,
                             plank_thickness=0.019),
     "Frames", col_structure, mirror=True)

make(lambda mb: (
    # stem apron (bow) and transom knee (stern): solid timber only in the
    # narrow wedges where the planking cannot close the hull
    solid_between_sections(mb, HULL, np.linspace(0.001, 0.042, 6), 0.020, MAT["wood_timber"]),
    solid_between_sections(mb, HULL, np.linspace(0.966, 0.999, 5), 0.020, MAT["wood_timber"]),
    build_stem_band(HULL, mb, r=0.017, n=14),
                      build_keel(HULL, mb, width=0.105, depth=0.080),
                 build_stem(HULL, mb, width=0.115, depth=0.115),
                 build_sternpost(HULL, mb, width=0.082, depth=0.095)),
     "Keel_Stem_Sternpost", col_structure)

make(lambda mb: build_transom(HULL, mb, t_lo=0.03, t_top=0.972), "Transom", col_structure)

make(lambda mb: (build_keelson(HULL, mb, width=0.090, height=0.070, xi0=0.055, xi1=0.945),
                 build_gunwale(HULL, mb, xi0=0.006, xi1=0.994)),
     "Keelson_Gunwale", col_structure, mirror=True)

# apron + mast step + inwale
def _structure_details(mb):
    # apron running up the inside of the stem
    pts, nrm = [], []
    for i in range(14):
        t = lerp(0.30, 0.97, i / 13)
        p = HULL.inner(0.075, t, 0.02)
        pts.append(p)
        nrm.append(unit(np.array([1.0, 0.0, 0.25])))
    parts.breast_hook(mb, HULL, xi=0.085, drop=0.13)
    # mast step: a block on the keelson
    p = HULL.surface(XI_MAST, 0.06)
    mb.add_box((p[0], 0, p[2] + 0.075), (0.24, 0.20, 0.10), mat=MAT["wood_timber"])
    mb.add_box((p[0], 0, p[2] + 0.135), (0.14, 0.10, 0.03), mat=MAT["wood_timber"])
    # inwale rail inside the sheer
    for side in (1,):
        xs = np.linspace(0.05, 0.95, 60)
        grid = np.zeros((len(xs), 4, 3))
        for i, xi in enumerate(xs):
            p = HULL.surface(xi, 0.955)
            n = HULL.normal(xi, 0.955)
            n = unit(np.array([n[0] * 0.2, n[1], 0.0]))
            a = p - n * 0.045
            b = a - n * 0.028
            grid[i, 0] = a + np.array([0, 0, 0.0])
            grid[i, 1] = a + np.array([0, 0, -0.052])
            grid[i, 2] = b + np.array([0, 0, -0.052])
            grid[i, 3] = b + np.array([0, 0, 0.0])
        mb.add_grid(grid, MAT["wood_timber"], close_v=True)


make(_structure_details, "Structure_Details", col_structure, mirror=True)

# --------------------------------------------------------------------------
# 3. thwarts, benches, knees, floorboards
# --------------------------------------------------------------------------
def _seating(mb):
    for xi in XI_THWARTS:
        parts.thwart_plank(mb, HULL, xi, top_drop=0.145, width=0.250, thick=0.044,
                           end_inset=0.030)
    parts.bench(mb, HULL, XI_STERN_BENCH, top_drop=0.155, width=0.36, thick=0.045,
                inset=0.045)
    # side benches in the stern sheets
    for xi in (0.790, 0.845, 0.900):
        z = HULL.sheer_z(xi) - 0.30
        x = HULL.x_of(xi)
        half = half_breadth_at(HULL, xi, z) - 0.02
        for s in (-1, 1):
            mb.add_box((x, s * half * 0.82, z), (0.145, half * 0.36, 0.038),
                       mat=MAT["wood_timber"])
    # stern sheets platform (gratings the coxswain stands on)
    xi = 0.905
    z = HULL.sheer_z(xi) - 0.42
    half = half_breadth_at(HULL, xi, z) - 0.02
    mb.add_box((HULL.x_of(xi), 0, z), (0.30, half * 1.7, 0.032), mat=MAT["wood_deck"])


make(_seating, "Thwarts_Benches", col_furniture)

make(lambda mb: [parts.thwart_knee(mb, HULL, xi, side=s) for xi in XI_THWARTS for s in (-1, 1)],
     "Thwart_Knees", col_furniture)

make(lambda mb: (parts.quarter_knee(mb, HULL, side=1),
                 parts.quarter_knee(mb, HULL, side=-1)),
     "Quarter_Knees", col_furniture)

make(lambda mb: parts.floor_gratings(mb, HULL, 0.27, 0.73, n_slats=7, slat_w=0.098,
                                    thick=0.026, t=0.085),
     "Floorboards", col_furniture)

# --------------------------------------------------------------------------
# 4. rowlocks
# --------------------------------------------------------------------------
def _rowlocks(mb):
    for xi in XI_THWARTS:
        p = HULL.surface(xi, 0.985)
        n = HULL.normal(xi, 0.985)
        parts.rowlock(mb, p + np.array([0, 0, 0.028]), n)


make(_rowlocks, "Rowlocks", col_gear, mirror=True)

# --------------------------------------------------------------------------
# 5. moving parts: 10 oars, rudder + tiller
# --------------------------------------------------------------------------
OARS_STOWED = "--oars-out" not in sys.argv
oar_meshes = []


def _oar_mesh():
    mb = MeshBuilder("Oar")
    parts.oar(mb, length=OAR_LEN, inboard=1.10)
    return mb


def rowlock_pivot(xi, side):
    """Where the oar turns: in the throat of the crutch on the gunwale.

    This is the pivot the game rotates the oar about, so the object's origin has
    to be here -- not at the stowed position inboard, which is where it used to
    be.  Every oar in the boat was pivoting about a point on top of a thwart.
    """
    p = HULL.surface(xi, 0.985)
    return np.array([p[0], side * (p[1] + 0.012), p[2] + 0.052])


def place_oar(name, xi, side, outboard_angle_deg=38.0, feather_deg=8.0):
    """Place an oar in its rowlock.  side=+1 port, -1 starboard."""
    p = HULL.surface(xi, 0.985)
    pivot = np.array([p[0], side * (p[1] + 0.012), p[2] + 0.085])
    mb = _oar_mesh()
    # local +X (outboard along the loom) -> rotated about Z by psi
    psi = math.radians(90.0 + outboard_angle_deg) if side > 0 else math.radians(90.0 - outboard_angle_deg)
    rot = np.array([[math.cos(psi), -math.sin(psi), 0], [math.sin(psi), math.cos(psi), 0], [0, 0, 1]])
    # feather: rotate about the loom axis
    phi = math.radians(feather_deg)
    axis = rot[:, 0]
    c, s = math.cos(phi), math.sin(phi)
    K = np.array([[0, -axis[2], axis[1]], [axis[2], 0, -axis[0]], [-axis[1], axis[0], 0]])
    R = rot @ (np.eye(3) * c + s * K + (1 - c) * np.outer(axis, axis))
    v = np.array(mb.verts)
    v = v @ R.T + pivot
    mb.verts = [tuple(x) for x in v]
    ob = bl.obj_from_builder(mb, name, mlist, col_moving)
    origin_to(ob, pivot)
    return ob


def stow_oar(name, xi, side, index):
    """Oars stowed fore-and-aft on the thwarts, the state of a ship's boat on
    passage -- but pivoted in the rowlock, not at the stowage position.

    Two separate things went wrong here.  The oars lay at a fixed offset from
    the centreline in a hull that closes in at both ends, so the blades stood
    out through the planking; and the object origin sat at the stow position,
    so the rowing animation turned every oar about a point on a thwart instead
    of about its rowlock.
    """
    origin = rowlock_pivot(xi, side)
    zc = HULL.sheer_z(xi) - 0.105 + 0.018 * (index % 2)
    px = -1.35 + 0.10 * (index // 2)
    ycap = clear_y(HULL, px - 1.10, px + OAR_LEN - 1.10, zc, clear=0.11)
    y = side * min(0.30 + 0.075 * index, ycap)
    mb = _oar_mesh()
    roll = math.radians(90.0)       # blade flat, as stowed
    R = np.array([[1, 0, 0], [0, math.cos(roll), -math.sin(roll)],
                  [0, math.sin(roll), math.cos(roll)]])
    v = np.array(mb.verts) @ R.T + np.array([px, y, zc])
    mb.verts = [tuple(x) for x in v]
    ob = bl.obj_from_builder(mb, name, mlist, col_moving)
    origin_to(ob, origin)
    return ob


oar_objects = []
for i, xi in enumerate(XI_THWARTS):
    for j, (side, tag) in enumerate(((1, "P"), (-1, "S"))):
        if OARS_STOWED:
            oar_objects.append(stow_oar(f"Oar_{tag}{i+1}", xi, side, i + j))
        else:
            oar_objects.append(place_oar(f"Oar_{tag}{i+1}", xi, side))

# rudder hung on the sternpost, pivot on the pintle axis
def _build_rudder(name):
    mb = MeshBuilder(name)
    parts.rudder(mb, HULL, length=1.05, width=0.34)
    # pivot at the rudder head, on the after face of the sternpost
    p = HULL.surface(1.0, 0.985)
    pivot = np.array([p[0] - 0.010, 0.0, p[2] - 0.05])
    v = np.array(mb.verts) + pivot          # into world space
    mb.verts = [tuple(x) for x in v]
    ob = bl.obj_from_builder(mb, name, mlist, col_moving)
    origin_to(ob, pivot)
    return ob


rudder_ob = _build_rudder("Rudder")

# --------------------------------------------------------------------------
# 6. fittings & gear
# --------------------------------------------------------------------------
def _fittings(mb):
    # hoisting eyes on the keelson (SLR1818 has exactly these fore and aft)
    for x, tag in ((1.95, "fwd"), (-1.60, "aft")):
        k = HULL.surface(HULL.xi_of(x), 0.03)
        parts.eye_bolt(mb, np.array([x, 0.0, k[2] + 0.075]), direction=(0, 0, 1), scale=1.25)
    # stem ring (painter) and stern eye
    p = HULL.surface(0.012, 0.80)
    parts.eye_bolt(mb, np.array([p[0] - 0.10, 0.0, p[2]]), direction=(-1, 0, 0), scale=1.1)
    p = HULL.surface(0.995, 0.72)
    parts.eye_bolt(mb, np.array([p[0] + 0.10, 0.0, p[2]]), direction=(1, 0, 0), scale=1.0)
    # gunwale rubbing strake / oar notches already in the capping
    # boat hook stowed along the starboard gunwale, inboard of the planking.
    # Two things go wrong with this: sat outboard of the sheer it reads as a
    # blade lying on the topsides, and since the hook runs forward from its
    # butt, a hook started abreast the fore thwart puts its head 0.6 m outside
    # the bow.  Cap the offset by the narrowest station the hook passes.
    zh = HULL.sheer_z(HULL.xi_of(1.15)) - 0.075
    yh = -clear_y(HULL, 1.15, 1.15 + 1.75, zh, clear=0.065)
    parts.boat_hook(mb, np.array([1.15, yh, zh]), length=1.75)
    # bilge pump beside the after thwart, on the starboard side of the keelson
    p = HULL.surface(HULL.xi_of(-2.15), 0.10)
    parts.bilge_pump(mb, np.array([p[0], -0.24, p[2] + 0.02]), height=0.50)
    # painter, flaked down on the foredeck
    for k in range(6):
        c = np.array([2.20 - 0.055 * k, 0.10 + 0.030 * (k % 2), HULL.sheer_z(0.20) - 0.02 + 0.012 * k])
        torus(mb, c, 0.135, 0.014, seg=18, rseg=5, mat=MAT["rope"])
    # bailer
    p = HULL.surface(0.62, 0.12)
    cyl(mb, (p[0], 0.30, p[2] + 0.05), (p[0], 0.30, p[2] + 0.16), 0.075, seg=14,
        mat=MAT["wood_deck"], r1=0.090)


make(_fittings, "Fittings", col_gear)


def _fenders(mb):
    """Coir fenders on the port side, hung over the topsides.

    Their own object, because a fender hanging plumb outside a hull that curves
    in below it is meant to be outside the planking -- and every other piece of
    gear is not.
    """
    for x in (0.9, -0.7):
        p = HULL.surface(HULL.xi_of(x), 0.98)
        parts.fender(mb, np.array([p[0], p[1] + 0.07, p[2] - 0.30]))


make(_fenders, "Fenders", col_gear)


def _mast_clamp(mb):
    """Mast clamp / partners: a beam across the boat on the bow thwart with a
    square hole for the mast.  SLR0772 shows exactly this fitting where a
    single mast could be stepped for sailing."""
    p = HULL.surface(XI_MAST, 0.90)
    z = HULL.sheer_z(XI_MAST) - 0.115
    # the clamp is a beam across the boat, so its length is the breadth of the
    # hull at the height it is bolted, not at the sheer above it
    half = min(p[1] * 0.96, clear_y(HULL, p[0] - 0.09, p[0] + 0.09, z - 0.070, clear=0.008))
    # two cheek pieces leaving a 90 mm square mast hole at the centreline
    for s in (-1, 1):
        y0, y1 = s * 0.045, s * half
        mb.add_box((p[0], (y0 + y1) * 0.5, z - 0.035),
                   (0.16, abs(y1 - y0), 0.070), mat=MAT["wood_timber"])
    # fore-and-aft cheeks closing the hole
    for dx in (-0.045, 0.045):
        mb.add_box((p[0] + dx, 0, z - 0.035), (0.070, 0.090, 0.070), mat=MAT["wood_timber"])


make(_mast_clamp, "Mast_Clamp", col_gear)

# --------------------------------------------------------------------------
# 7. report + save
# --------------------------------------------------------------------------
allobs = [o for c in (col_hull, col_structure, col_furniture, col_gear, col_moving)
          for o in c.objects]
tot_v = sum(len(o.data.vertices) for o in allobs)
tot_f = sum(len(o.data.polygons) for o in allobs)
print(f"TOTAL verts={tot_v} faces={tot_f} objects={len(allobs)}")

bpy.context.scene["boat_name"] = "25 ft Clinker Rowing Cutter"
bpy.context.scene["loa_m"] = HULL.loa
bpy.context.scene["stud_per_m"] = specs.STUD_PER_M

bl.save_blend(f"{ROOT}/boats/blend/boat_b_rowing_cutter.blend")

# exports
if not QUICK:
    bl.export_object(bl.join_objects([o for c in (col_hull, col_structure) for o in c.objects],
                                     "Hull_Export"), f"{ROOT}/boats/exports/rowing_cutter_hull.glb", "glb")
    print("EXPORTED hull glb")

# --------------------------------------------------------------------------
# 8. renders
# --------------------------------------------------------------------------
if not NO_RENDER:
    bl.studio(world_strength=0.5, ground_z=-1.6)
    shots = {
        "hero": ((10.0, -12.5, 5.6), (0.0, 0, 0.05), 50),
        "broadside": ((0.0, -14.0, 0.9), (0, 0, 0.35), None),
        "bow_quarter": ((10.5, -6.5, 3.2), (0.5, 0, 0.0), 55),
        "stern_quarter": ((-10.0, -6.0, 3.0), (-0.6, 0, 0.0), 55),
        "from_above": ((2.0, -5.0, 15.0), (0.0, 0, 0.0), 45),
        "stern_on": ((-11.5, -0.3, 0.9), (0.0, 0, 0.1), 55),
    }
    for name, (loc, look, lens) in shots.items():
        if lens is None:
            cam = bl.camera(name, loc, look, ortho=8.5)
        else:
            cam = bl.camera(name, loc, look, lens=lens)
        bl.render(f"{ROOT}/boats/renders/rowing_{name}.png", cam,
                  res=(1200, 750) if not QUICK else (640, 400), samples=24 if QUICK else 72)
print("BUILD COMPLETE")

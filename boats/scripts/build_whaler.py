"""
build_whaler.py -- BOAT C, the 27 ft double-ended clinker whaler (c.1890).

Run headless:
    blender -b --python build_whaler.py -- [--quick] [--no-render]

Produces:
    boats/blend/boat_c_whaler.blend
    boats/exports/whaler_hull.glb
    boats/renders/whaler_*.png

Why this boat
-------------
The other two are a steamer and a pulling cutter, both with transoms.  A
whaler is the third member of a Victorian liner's boat outfit and the only one
of the three that is *double ended*: pointed stem and pointed stern, no
transom at all.  That shape is not decoration -- the boat was developed for
whaling, where you have to be able to back off a fish without turning the boat
round, and it survived into naval service for exactly that reason.

Documented figures (RN whaler type, in service from the 1890s):
    length 27 ft (8.230 m), beam 6 ft (1.829 m), draught 1 ft 5 in (0.432 m)
    with the plate up, normal load 20.5 cwt (1021 kg), 27 persons capacity,
    clinker built, drop keel, five oars single banked -- three one side, two
    the other -- 16 ft 6 in mainmast, 13 ft mizzen, 15 ft 3 in yard.
Sources are listed in HISTORICAL_EVIDENCE.md.
"""

import argparse
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bpy
import numpy as np
from mathutils import Matrix, Vector

from boatgen import bl, parts, specs
from boatgen.geom import MeshBuilder, cyl, lerp, sphere, torus, unit
from boatgen.hull import (
    MAT,
    build_clinker_planking,
    build_frames,
    build_gunwale,
    build_keel,
    build_keelson,
    build_stem,
    build_sternpost,
    clear_y,
    half_breadth_at,
    solid_between_sections,
)

QUICK = "--quick" in sys.argv
NO_RENDER = "--no-render" in sys.argv
ROOT = "/home/user/victoria"
HULL = specs.WHALER

# --------------------------------------------------------------------------
# layout
# --------------------------------------------------------------------------
N_STRAKES = 9
XI_THWARTS = [0.285, 0.420, 0.555, 0.690]
XI_STERN_SHEETS = 0.830
XI_MAINMAST = 0.420
XI_MIZZEN = 0.735
XI_CB_FWD, XI_CB_AFT = 0.335, 0.520      # centreboard case

OAR_LEN = 5.18          # 17 ft service oar, as the RN whaler pulled
OAR_BOW = 4.88          # the bowman's oar is a foot shorter
MAINMAST_LEN = 16.5 * specs.FOOT
MIZZEN_LEN = 13.0 * specs.FOOT
MAIN_YARD_LEN = 15.25 * specs.FOOT
MIZZEN_YARD_LEN = 10.5 * specs.FOOT

bl.reset_scene()
mats = bl.build_materials()
mlist = bl.mats_list(mats)


def _register(m):
    if m not in mlist:
        mlist.append(m)
    return len(mlist) - 1


col_hull = bl.collection("Hull")
col_structure = bl.collection("Structure")
col_furniture = bl.collection("Furniture")
col_gear = bl.collection("Gear")
col_rig = bl.collection("Rig")
col_moving = bl.collection("Moving_Parts")


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
    pivot = Vector(pivot)
    ob.data.transform(Matrix.Translation(-pivot))
    ob.location = pivot


# --------------------------------------------------------------------------
# 1. planking -- 9 clinker strakes, bottom three painted
# --------------------------------------------------------------------------
# Elm-built, varnished above the waterline and painted below, which is how a
# naval whaler was finished: the paint is the part that takes the beach.
strake_mats = []
for k in range(N_STRAKES):
    f = (k + 0.5) / N_STRAKES
    z = lerp(HULL.keel_z(0.5), HULL.sheer_z(0.5), f)
    if z < -0.17:
        strake_mats.append(MAT["paint_hull"])
        continue
    v = 0.94 + 0.10 * ((k * 5) % 5) / 4.0
    warm = 1.0 + 0.05 * ((k * 3) % 4 - 1.5) / 1.5
    strake_mats.append(_register(bl.wood_material(
        f"Elm_Strake_{k:02d}",
        base=(0.30 * v * warm, 0.185 * v, 0.095 * v / warm),
        dark=(0.13 * v, 0.075 * v, 0.035 * v),
        rough=0.46, bump=0.25)))

make(
    lambda mb: build_clinker_planking(
        mb, HULL, n_strakes=N_STRAKES, thickness=0.018, lap=0.012,
        xi0=0.0012, n_xi=76, butt_length=2.6, xi1=0.9988,
        mat_out=strake_mats, mat_in=[MAT["wood_out"]] * N_STRAKES,
    ),
    "Planking_Clinker",
    col_hull,
    mirror=True,
    auto_smooth=20.0,
)

# --------------------------------------------------------------------------
# 2. keel and the two stems -- both ends are stem-shaped
# --------------------------------------------------------------------------
make(lambda mb: (
    build_keel(HULL, mb, width=0.098, depth=0.076),
    build_stem(HULL, mb, width=0.104, depth=0.106, head_rise=0.050),
    # No transom: the after end is a counter-stem, exactly like the bow.
    build_sternpost(HULL, mb, width=0.100, depth=0.102, t0=-0.02, t1=0.996),
    # deadwood filling the wedges the planking cannot close at either end
    solid_between_sections(mb, HULL, np.linspace(0.001, 0.030, 6), 0.018, MAT["wood_timber"]),
    solid_between_sections(mb, HULL, np.linspace(0.972, 0.999, 5), 0.018, MAT["wood_timber"]),
), "Keel_Stems", col_structure)

make(lambda mb: build_frames(mb, HULL, spacing=0.148, depth=0.032, width=0.023,
                            xi0=0.030, xi1=0.972, t0=0.012, t1=0.955,
                            plank_thickness=0.018, end_fade=0.34),
     "Frames", col_structure, mirror=True)

make(lambda mb: (build_keelson(HULL, mb, width=0.086, height=0.066, xi0=0.05,
                                xi1=0.95, end_taper=0.42),
                 build_gunwale(HULL, mb, out_width=0.044, in_width=0.086,
                               height=0.032, xi0=0.006, xi1=0.994)),
     "Keelson_Gunwale", col_structure, mirror=True)


def _structure_details(mb):
    """Inwales, both aprons, mast steps and the centreboard bed."""
    # inwale rail inside the sheer
    xs = np.linspace(0.05, 0.95, 60)
    grid = np.zeros((len(xs), 4, 3))
    for i, xi in enumerate(xs):
        p = HULL.surface(xi, 0.955)
        n = HULL.normal(xi, 0.955)
        n = unit(np.array([n[0] * 0.2, n[1], 0.0]))
        a = p - n * 0.042
        b = a - n * 0.026
        grid[i, 0] = a
        grid[i, 1] = a + np.array([0, 0, -0.048])
        grid[i, 2] = b + np.array([0, 0, -0.048])
        grid[i, 3] = b
    mb.add_grid(grid, MAT["wood_timber"], close_v=True)
    # aprons up both stems -- a double-ender has two of everything
    parts.breast_hook(mb, HULL, xi=0.082, drop=0.125)
    # main and mizzen steps on the keelson
    for xi, size in ((XI_MAINMAST, (0.26, 0.22, 0.10)), (XI_MIZZEN, (0.20, 0.17, 0.08))):
        p = HULL.surface(xi, 0.055)
        mb.add_box((p[0], 0.0, p[2] + 0.075), size, None, MAT["wood_timber"])
    # bed logs either side of the centreboard case
    p0 = HULL.surface(XI_CB_FWD, 0.05)
    p1 = HULL.surface(XI_CB_AFT, 0.05)
    for s in (-1, 1):
        mb.add_box(((p0[0] + p1[0]) * 0.5, s * 0.105, p0[2] + 0.045),
                   (abs(p0[0] - p1[0]), 0.045, 0.055), None, MAT["wood_timber"])


make(_structure_details, "Structure_Details", col_structure, mirror=True)

# --------------------------------------------------------------------------
# 3. centreboard trunk and plate
# --------------------------------------------------------------------------
def _centreboard(mb):
    x_f = HULL.x_of(XI_CB_FWD)
    x_a = HULL.x_of(XI_CB_AFT)
    z_keel = HULL.keel_z(0.5)
    z_bot = z_keel + 0.20          # clear of the rising floor of the hull
    z_top = z_keel + 0.58
    # trunk: two cheeks a plate's width apart, capped
    for s in (-1, 1):
        mb.add_box(((x_f + x_a) * 0.5, s * 0.045, (z_bot + z_top) * 0.5),
                   (abs(x_a - x_f), 0.020, z_top - z_bot), None, MAT["wood_timber"])
    mb.add_box(((x_f + x_a) * 0.5, 0.0, z_top + 0.012), (abs(x_a - x_f), 0.110, 0.024),
               None, MAT["wood_timber"])
    # head of the plate, standing up out of the trunk, with its lifting handle
    mb.add_box(((x_f + x_a) * 0.5, 0.0, z_top + 0.075), (0.28, 0.026, 0.090),
               None, MAT["iron"])
    rod_z = z_top + 0.125
    cyl(mb, ((x_f + x_a) * 0.5, 0.0, z_top + 0.11),
        ((x_f + x_a) * 0.5, 0.0, rod_z), 0.011, seg=8, mat=MAT["steel"])
    cyl(mb, ((x_f + x_a) * 0.5 - 0.07, 0.0, rod_z),
        ((x_f + x_a) * 0.5 + 0.07, 0.0, rod_z), 0.011, seg=8, mat=MAT["wood_timber"])
    # pivot bolt through both cheeks
    pz = z_bot + 0.06
    cyl(mb, (x_a - 0.05, -0.062, pz), (x_a - 0.05, 0.062, pz), 0.012, seg=8,
        mat=MAT["brass"])


make(_centreboard, "Centreboard", col_structure)

# --------------------------------------------------------------------------
# 4. thwarts, stern sheets, floorboards, knees
# --------------------------------------------------------------------------
def _seating(mb):
    for xi in XI_THWARTS:
        parts.thwart_plank(mb, HULL, xi, top_drop=0.140, width=0.245, thick=0.042,
                           end_inset=0.030)
    # stern sheets: the coxswain's bench, set athwartships right aft
    parts.bench(mb, HULL, XI_STERN_SHEETS, top_drop=0.150, width=0.34, thick=0.044,
                inset=0.050)
    # the pulling benches: side benches either side of the centreboard trunk
    for xi in (0.600, 0.665):
        z = HULL.sheer_z(xi) - 0.285
        x = HULL.x_of(xi)
        half = half_breadth_at(HULL, xi, z) - 0.02
        for s in (-1, 1):
            mb.add_box((x, s * half * 0.80, z), (0.135, half * 0.34, 0.036),
                       None, MAT["wood_timber"])


make(_seating, "Thwarts_Benches", col_furniture)

make(lambda mb: [parts.thwart_knee(mb, HULL, xi, side=s)
                 for xi in XI_THWARTS for s in (-1, 1)],
     "Thwart_Knees", col_furniture)

make(lambda mb: parts.floor_gratings(mb, HULL, 0.20, 0.80, n_slats=7, slat_w=0.088,
                                    thick=0.024, t=0.075),
     "Floorboards", col_furniture)

# --------------------------------------------------------------------------
# 5. masts, yards and rigging
# --------------------------------------------------------------------------
def _mast(mb, xi, length, r_base, r_head, rake=0.02):
    p = HULL.surface(xi, 0.055)
    base = np.array([p[0], 0.0, p[2] + 0.10])
    top = base + np.array([-rake * length, 0.0, length])
    n = 8
    for i in range(n):
        a = i / n
        b = (i + 1) / n
        pa = lerp(base, top, a)
        pb = lerp(base, top, b)
        ra = lerp(r_base, r_head, a ** 0.8)
        rb = lerp(r_base, r_head, b ** 0.8)
        cyl(mb, pa, pb, ra, seg=12, mat=MAT["wood_timber"], r1=rb)
    # truck and its sheave
    cyl(mb, top, top + np.array([-0.02, 0, 0.05]), r_head * 1.25, seg=12,
        mat=MAT["wood_timber"])
    torus(mb, top + np.array([-0.02, 0, 0.065]), r_head * 0.9, 0.008, seg=10,
          rseg=5, mat=MAT["brass"])
    return base, top


def _yard(mb, x, centre_z, length, r=0.046, sail=True):
    """A yard crossed on the mast, with its sail furled and gasketed along it.

    A boat lying in the davits stows her canvas: the yard is up, the sail is
    rolled down on top of it and stopped with rope gaskets.  Modelling the
    bare spar alone reads as a scaffold pole.
    """
    a = np.array([x, -length * 0.5, centre_z])
    b = np.array([x, length * 0.5, centre_z])
    n = 6
    for i in range(n):
        f0, f1 = i / n, (i + 1) / n
        ya = lerp(a[1], b[1], f0)
        yb = lerp(a[1], b[1], f1)
        ra = r * (0.62 + 0.38 * math.sin(math.pi * f0))
        rb = r * (0.62 + 0.38 * math.sin(math.pi * f1))
        cyl(mb, (x, ya, centre_z), (x, yb, centre_z), ra, seg=10,
            mat=MAT["wood_timber"], r1=rb)
    if not sail:
        return
    # the furled sail sits on top of the yard as a fat bundle
    m = 9
    for i in range(m):
        f0, f1 = i / m, (i + 1) / m
        ya = lerp(a[1] * 0.92, b[1] * 0.92, f0)
        yb = lerp(a[1] * 0.92, b[1] * 0.92, f1)
        rr = 0.030 + 0.062 * math.sin(math.pi * (f0 + f1) * 0.5) ** 0.6
        cyl(mb, (x + 0.010, ya, centre_z + rr * 0.72),
            (x + 0.010, yb, centre_z + rr * 0.72), rr, seg=10,
            mat=MAT["canvas"], r1=rr)
    # rope gaskets stopping the bundle to the yard
    for k in range(1, 8):
        f = k / 8.0
        y = lerp(a[1] * 0.90, b[1] * 0.90, f)
        torus(mb, (x + 0.010, y, centre_z + 0.052), 0.062, 0.008, seg=12, rseg=5,
              axis="Y", mat=MAT["rope"])
    # slings holding the yard to the mast
    torus(mb, (x, 0.0, centre_z), r * 1.35, 0.010, seg=14, rseg=5, axis="Z",
          mat=MAT["rope"])


def _rig(mb):
    main_base, main_top = _mast(mb, XI_MAINMAST, MAINMAST_LEN, 0.055, 0.032)
    miz_base, miz_top = _mast(mb, XI_MIZZEN, MIZZEN_LEN, 0.046, 0.026)
    # yard hoisted just below each masthead, furled sail bent to it
    _yard(mb, main_top[0] - 0.15, main_top[2] - 0.34, MAIN_YARD_LEN, sail=True)
    _yard(mb, miz_top[0] - 0.11, miz_top[2] - 0.28, MIZZEN_YARD_LEN, sail=True)
    # mast hoops, which is what actually holds a lug yard to its mast
    for top, zs in ((main_top, (-0.34, -0.72, -1.10)), (miz_top, (-0.28, -0.62))):
        for dz in zs:
            torus(mb, (top[0] - 0.01, 0.0, top[2] + dz), 0.062, 0.011, seg=14,
                  rseg=5, axis="Z", mat=MAT["rope"])
    # shrouds: two a side per mast, to the gunwale
    for xi, top, n_sh in ((XI_MAINMAST, main_top, 2), (XI_MIZZEN, miz_top, 1)):
        for s in (-1, 1):
            for k in range(n_sh):
                xi_land = xi + (0.055 if k == 0 else 0.085)
                pl = HULL.surface(xi_land, 0.985)
                foot = np.array([pl[0], s * (pl[1] - 0.010), pl[2] + 0.020])
                head = np.array([top[0], s * 0.045, top[2] - 0.10 - 0.03 * k])
                mb.add_tube(np.array([foot, head]), 0.006, segments=5,
                            mat=MAT["rope"], caps=False)
    # forestay from the mainmast head to the bow, and a mizzen stay aft
    bow = HULL.surface(0.010, 0.86)
    mb.add_tube(np.array([[main_top[0], 0.0, main_top[2] - 0.06],
                          [bow[0], 0.0, bow[2] + 0.02]]), 0.006, segments=5,
                mat=MAT["rope"], caps=False)
    stern = HULL.surface(0.990, 0.86)
    mb.add_tube(np.array([[miz_top[0], 0.0, miz_top[2] - 0.06],
                          [stern[0], 0.0, stern[2] + 0.02]]), 0.006, segments=5,
                mat=MAT["rope"], caps=False)
    # running rigging: halyards led down and belayed at the mast feet
    for top, base in ((main_top, main_base), (miz_top, miz_base)):
        mb.add_tube(np.array([[top[0] + 0.02, 0.0, top[2] - 0.02],
                              [base[0] + 0.10, 0.16, base[2] + 0.15]]),
                    0.005, segments=5, mat=MAT["rope"], caps=False)


make(_rig, "Masts_Yards_Rigging", col_rig)

# --------------------------------------------------------------------------
# 6. rowlocks -- five, single banked
# --------------------------------------------------------------------------
OAR_STATIONS = [(0.285, 1), (0.420, 1), (0.555, 1), (0.420, -1), (0.690, -1)]


def _rowlocks(mb):
    for xi, s in OAR_STATIONS:
        p = HULL.surface(xi, 0.985)
        n = HULL.normal(xi, 0.985)
        parts.rowlock(mb, np.array([p[0], s * p[1], p[2] + 0.026]), n * np.array([s, s, 1]))


make(_rowlocks, "Rowlocks", col_gear)

# --------------------------------------------------------------------------
# 7. oars -- five, stowed fore and aft when the boat is in the davits
# --------------------------------------------------------------------------
OARS_STOWED = "--oars-out" not in sys.argv
oar_objects = []


def _oar_mesh(length):
    mb = MeshBuilder("Oar")
    parts.oar(mb, length=length, inboard=1.16, blade_len=0.70, blade_w=0.150)
    return mb


def place_oar(name, xi, side, outboard_angle_deg=36.0, feather_deg=8.0, length=OAR_LEN):
    p = HULL.surface(xi, 0.985)
    pivot = np.array([p[0], side * (p[1] + 0.012), p[2] + 0.082])
    mb = _oar_mesh(length)
    psi = math.radians(90.0 + outboard_angle_deg) if side > 0 else math.radians(90.0 - outboard_angle_deg)
    rot = np.array([[math.cos(psi), -math.sin(psi), 0], [math.sin(psi), math.cos(psi), 0], [0, 0, 1]])
    phi = math.radians(feather_deg)
    axis = rot[:, 0]
    c, s = math.cos(phi), math.sin(phi)
    K = np.array([[0, -axis[2], axis[1]], [axis[2], 0, -axis[0]], [-axis[1], axis[0], 0]])
    R = rot @ (np.eye(3) * c + s * K + (1 - c) * np.outer(axis, axis))
    v = np.array(mb.verts) @ R.T + pivot
    mb.verts = [tuple(x) for x in v]
    ob = bl.obj_from_builder(mb, name, mlist, col_moving)
    origin_to(ob, pivot)
    return ob


def _max_y(x0, x1, z, clear):
    """Widest |y| a stowed oar can take without its blades leaving the hull."""
    return clear_y(HULL, x0, x1, z, clear=clear)


def rowlock_pivot(xi, side):
    """The throat of the crutch: the point the oar actually turns about, and
    therefore the point the game must rotate it about."""
    p = HULL.surface(xi, 0.985)
    return np.array([p[0], side * (p[1] + 0.012), p[2] + 0.052])


def stow_oar(name, xi, side, index, length=OAR_LEN):
    p = HULL.surface(xi, 0.80)
    # oars lie on top of the thwarts, which is how they are actually stowed
    zc = HULL.sheer_z(xi) - 0.112 + 0.019 * (index % 2)
    px = -1.55 + 0.06 * index
    ycap = _max_y(px - 1.16, px + length - 1.16, zc, 0.10)
    pivot = np.array([px, side * min(0.30 + 0.085 * index, ycap), zc])
    mb = _oar_mesh(length)
    roll = math.radians(90.0)
    R = np.array([[1, 0, 0], [0, math.cos(roll), -math.sin(roll)], [0, math.sin(roll), math.cos(roll)]])
    v = np.array(mb.verts) @ R.T + pivot
    mb.verts = [tuple(x) for x in v]
    ob = bl.obj_from_builder(mb, name, mlist, col_moving)
    # origin in the rowlock, geometry at the stowage position
    origin_to(ob, rowlock_pivot(xi, side))
    return ob


for i, (xi, s) in enumerate(OAR_STATIONS):
    tag = "P" if s > 0 else "S"
    length = OAR_BOW if i == 0 else OAR_LEN
    if OARS_STOWED:
        oar_objects.append(stow_oar(f"Oar_{tag}{i + 1}", xi, s, i, length))
    else:
        oar_objects.append(place_oar(f"Oar_{tag}{i + 1}", xi, s, length=length))

# --------------------------------------------------------------------------
# 8. rudder and tiller
# --------------------------------------------------------------------------
def _rudder(mb):
    """A whaler's rudder hangs on the counter-stem, following its rake.

    Rather than place the blade by eye, the after-most point of the hull is
    sampled at each height and the blade is set a fixed distance aft of it --
    which is the only way to be sure a raked stem and a raked rudder do not
    end up inside one another.
    """
    z_keel = HULL.keel_z(1.0)
    sheer = HULL.sheer_z(1.0)

    def aft_x_at(z):
        # +X is forward, so the after-most point of the hull is its *minimum*
        # x.  The blade is set a fixed distance aft of that.
        best = 1e9
        for t in np.linspace(0.0, 1.0, 80):
            q = HULL.surface(1.0, t)
            if abs(q[2] - z) < 0.10:
                best = min(best, q[0])
        return best

    z_lo = z_keel + 0.14
    z_hi = sheer - 0.10
    zs = [z_lo + (z_hi - z_lo) * i / 5 for i in range(6)]
    grid = np.zeros((len(zs), 2, 3))
    for i, z in enumerate(zs):
        x = aft_x_at(z) - 0.055
        grid[i, 0] = (x, -0.011, z)
        grid[i, 1] = (x, 0.011, z)
    mb.add_grid(grid, MAT["wood_out"], close_v=True)
    # stock above the sheer, and the tiller for the coxswain
    xs = aft_x_at(z_hi) - 0.055
    cyl(mb, (xs, 0, z_hi), (xs, 0, z_hi + 0.14), 0.024, seg=10, mat=MAT["wood_timber"])
    cyl(mb, (xs, 0, z_hi + 0.115), (xs + 0.62, 0, z_hi + 0.175), 0.021, seg=10,
        mat=MAT["wood_timber"], r1=0.016)
    # pintles, on the after face of the stem
    for z in (z_lo + 0.10, z_hi - 0.18):
        cyl(mb, (aft_x_at(z) - 0.052, -0.024, z), (aft_x_at(z) - 0.052, 0.024, z),
            0.009, seg=8, mat=MAT["steel"])


make(_rudder, "Rudder", col_moving)

# --------------------------------------------------------------------------
# 9. fittings
# --------------------------------------------------------------------------
def _fittings(mb):
    # hoisting eyes through the keelson, fore and aft of the centreboard case
    for x in (1.85, -1.85):
        k = HULL.surface(HULL.xi_of(x), 0.03)
        parts.eye_bolt(mb, np.array([x, 0.0, k[2] + 0.070]), direction=(0, 0, 1), scale=1.2)
    # painter ring and stern ring
    p = HULL.surface(0.014, 0.78)
    parts.eye_bolt(mb, np.array([p[0] - 0.10, 0.0, p[2]]), direction=(-1, 0, 0), scale=1.1)
    p = HULL.surface(0.986, 0.78)
    parts.eye_bolt(mb, np.array([p[0] + 0.10, 0.0, p[2]]), direction=(1, 0, 0), scale=1.0)
    # boat hook and bailer, stowed as in the cutter.  The hook runs forward
    # from its butt, so it has to start well aft of the bow or its head stands
    # out through the planking: it lies on the thwarts, head forward.
    zh = HULL.sheer_z(HULL.xi_of(1.00)) - 0.105
    yh = -_max_y(1.00, 2.90, zh, 0.06)
    parts.boat_hook(mb, np.array([1.00, yh, zh]), length=1.90)
    p = HULL.surface(0.62, 0.12)
    yb = min(0.28, half_breadth_at(HULL, 0.62, p[2] + 0.05) - 0.105)
    cyl(mb, (p[0], yb, p[2] + 0.05), (p[0], yb, p[2] + 0.17), 0.075, seg=14,
        mat=MAT["wood_deck"], r1=0.092)
    # A whaler's working gear: a line tub and a water breaker.  The tub is the
    # boat's defining piece of equipment -- the whale line is flaked into it so
    # it runs out clear -- and the breaker is what keeps five men alive on a
    # long pull.  Both are things you can see from outside the boat, which is
    # what separates a modelled ship's boat from a modelled hull.
    x_t = HULL.x_of(0.585)
    pt = HULL.surface(0.585, 0.10)
    # the tub is 0.29 m across, so it sits where the bilge is, not against the
    # planking: clamped by the hull, like every other piece of loose gear
    y_t = min(0.17, clear_y(HULL, x_t - 0.15, x_t + 0.15, pt[2] + 0.055, clear=0.15))
    cyl(mb, (x_t, y_t, pt[2] + 0.055), (x_t, y_t, pt[2] + 0.235), 0.125, seg=18,
        mat=MAT["wood_deck"], r1=0.145)
    for k in range(4):
        torus(mb, (x_t, y_t, pt[2] + 0.215 + 0.016 * k), 0.088 - 0.010 * k, 0.0135,
              seg=20, rseg=6, axis="Z", mat=MAT["rope"])
    # breaker: a wooden water cask with three brass hoops, lashed under the
    # stern sheets
    xb = HULL.x_of(0.80)
    pb = HULL.surface(0.80, 0.11)
    # keep the cask inboard of the planking: at 80% of the length the hull has
    # closed to 0.30 m half-breadth at the bilge, and a 0.105 m cask set 0.19 m
    # off the centreline stood 105 mm out through the topsides
    yb = -min(0.19, clear_y(HULL, xb - 0.11, xb + 0.11, pb[2] + 0.06, clear=0.115))
    cyl(mb, (xb, yb, pb[2] + 0.02), (xb, yb, pb[2] + 0.30), 0.105, seg=16,
        mat=MAT["wood_deck"], r1=0.105)
    for zz in (0.07, 0.15, 0.23):
        cyl(mb, (xb, yb, pb[2] + zz), (xb, yb, pb[2] + zz + 0.014), 0.109, seg=16,
            mat=MAT["brass"])
    # boat's compass in its box, on the stern-sheets platform
    xcc = HULL.x_of(0.755)
    zcc = HULL.sheer_z(0.755) - 0.150
    mb.add_box((xcc, 0.30, zcc + 0.045), (0.17, 0.17, 0.09), mat=MAT["wood_timber"])
    cyl(mb, (xcc, 0.30, zcc + 0.09), (xcc, 0.30, zcc + 0.10), 0.065, seg=16, mat=MAT["brass"])
    # grapnel stowed forward of the centreboard case, standing on the bottom
    # boards: a whaler's anchor is a grapnel, and it is the one heavy item of
    # gear she carries, so it lives where two men can reach it
    xg = 1.34
    pg = HULL.surface(HULL.xi_of(xg), 0.13)
    parts.grapnel(mb, np.array([xg, 0.0, pg[2] + 0.012]), scale=0.85)


make(_fittings, "Fittings", col_gear)


def _fenders(mb):
    """A coir fender each side, hanging over the topsides for coming alongside.

    Kept in its own object because this is the one piece of gear that is
    *meant* to be outside the planking, and the interference check treats
    Fittings as gear that must be inside the boat.
    """
    for s in (-1, 1):
        p = HULL.surface(HULL.xi_of(0.55), 0.975)
        parts.fender(mb, np.array([p[0], s * (p[1] + 0.07), p[2] - 0.28]),
                     mat=MAT["rope"], length=0.44, r=0.062)


make(_fenders, "Fenders", col_gear)

# --------------------------------------------------------------------------
# report + save
# --------------------------------------------------------------------------
allobs = [o for c in (col_hull, col_structure, col_furniture, col_gear, col_rig, col_moving)
          for o in c.objects]
tot_v = sum(len(o.data.vertices) for o in allobs)
tot_f = sum(len(o.data.polygons) for o in allobs)
print(f"TOTAL verts={tot_v} faces={tot_f} objects={len(allobs)}")

bpy.context.scene["boat_name"] = "27 ft Double-ended Whaler"
bpy.context.scene["loa_m"] = HULL.loa
bpy.context.scene["stud_per_m"] = specs.STUD_PER_M

bl.save_blend(f"{ROOT}/boats/blend/boat_c_whaler.blend")

if not QUICK:
    bl.export_object(bl.join_objects([o for c in (col_hull, col_structure) for o in c.objects],
                                     "Hull_Export"),
                     f"{ROOT}/boats/exports/whaler_hull.glb", "glb")
    print("EXPORTED hull glb")

if not NO_RENDER:
    bl.studio(world_strength=0.5, ground_z=-1.6)
    shots = {
        "hero": ((10.5, -13.0, 6.0), (0.0, 0, 0.9), 50),
        "broadside": ((0.0, -15.0, 1.4), (0, 0, 1.0), None),
        "bow_quarter": ((11.0, -6.8, 3.4), (0.5, 0, 0.6), 55),
        "stern_quarter": ((-10.6, -6.2, 3.2), (-0.6, 0, 0.6), 55),
        "from_above": ((2.0, -5.0, 16.0), (0.0, 0, 0.2), 45),
    }
    for name, (loc, look, lens) in shots.items():
        if lens is None:
            cam = bl.camera(name, loc, look, ortho=9.2)
        else:
            cam = bl.camera(name, loc, look, lens=lens)
        bl.render(f"{ROOT}/boats/renders/whaler_{name}.png", cam,
                  res=(1200, 750) if not QUICK else (640, 400),
                  samples=24 if QUICK else 72)
print("BUILD COMPLETE")

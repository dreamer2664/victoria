"""
build_steam_cutter.py -- BOAT A, the 25 ft steam cutter of 1888.

Reconstruction of RMG NPC9572 'Proposed 25ft Steam Cutter' (Dangerfield Lith.,
18 January 1888, drawn at 1:16, showing inboard profile, plan and midship
section) developed into a complete, operable steamboat: double-skin hull,
boiler, engine, shafting, screw, rudder, canopy, seating and all gear.

Run headless:
    blender -b --python build_steam_cutter.py -- [--quick] [--no-render]
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bpy
import numpy as np
from mathutils import Matrix, Vector

from boatgen import bl, layout, machinery, parts, specs
from boatgen.geom import MeshBuilder, cyl, lerp, sphere, torus, unit
from boatgen.hull import (
    MAT,
    build_carvel_planking,
    build_diagonal_skin,
    build_frames,
    build_gunwale,
    build_rubbing_strake,
    build_stem_band,
    plank_panel,
    build_keel,
    build_keelson,
    build_stem,
    build_sternpost,
    build_transom,
    clear_y,
    half_breadth_at,
    solid_between_sections,
)

QUICK = "--quick" in sys.argv
NO_RENDER = "--no-render" in sys.argv
ROOT = "/home/user/victoria"
HULL = specs.STEM_CUTTER

# --------------------------------------------------------------------------
# installation layout (all measured from the hull, so it follows the design)
# --------------------------------------------------------------------------
from boatgen.layout import STEAM as LAYOUT          # one source of truth

X_BOILER = LAYOUT["boiler"]["x"]
X_ENGINE = LAYOUT["engine"]["x"]
# the bunker sits abaft the boiler, forward of the engine, where the fireman
# works -- it used to be at x = +1.62, in the forward passenger cockpit
X_BUNKER = LAYOUT["bunker"]["x"]
X_SCREW = -3.42
Z_SHAFT_CRANK = None      # computed below
Y_BEARER = 0.42
DECK_DROP = 0.115

bl.reset_scene()
mats = bl.build_materials()
mlist = bl.mats_list(mats)


def _register(m):
    """MAT values are slot indices, so any material created after the base
    list was built is appended to it and its index returned."""
    mlist.append(m)
    return len(mlist) - 1
col_hull = bl.collection("Hull")
col_structure = bl.collection("Structure")
col_deck = bl.collection("Deck_Canopy")
col_mach = bl.collection("Machinery")
col_furn = bl.collection("Furniture")
col_gear = bl.collection("Gear")
col_moving = bl.collection("MovingParts")


def make(builder, name, collection, mirror=False, smooth=True, thickness=None):
    mb = MeshBuilder(name)
    builder(mb)
    if mirror:
        mb.mirror_y()
    ob = bl.obj_from_builder(mb, name, mlist, collection, smooth=smooth)
    n_ngon = bl.triangulate_ngons(ob)
    if thickness:
        bl.solidify(ob, thickness)
    print(f"  [{name}] verts={len(ob.data.vertices)} faces={len(ob.data.polygons)}"
          + (f" ngons->tris={n_ngon}" if n_ngon else ""))
    return ob


def origin_to(ob, pivot):
    pivot = Vector(pivot)
    ob.data.transform(Matrix.Translation(-pivot))
    ob.location = pivot


def floor_z(x):
    """Inside bottom of the hull at a given x."""
    xi = HULL.xi_of(x)
    return HULL.inner(xi, 0.02, 0.020)[2]


def sheer_at(x):
    return HULL.sheer_z(HULL.xi_of(x))


# --------------------------------------------------------------------------
# 1. hull: carvel outer skin over a double-diagonal inner skin
# --------------------------------------------------------------------------
N_STRAKES = 13
carvel_mats = [MAT["paint_white"] if k >= N_STRAKES - 2 else
               (MAT["paint_hull"] if k >= 2 else MAT["red_lead"]) for k in range(N_STRAKES)]
make(lambda mb: build_carvel_planking(mb, HULL, n_strakes=N_STRAKES, thickness=0.020, xi0=0.004,
                                      xi1=0.9995, n_xi=76, mat_out=carvel_mats,
                                      mat_in=MAT["wood_timber"], seam=0.0022),
     "Planking_Carvel", col_hull, mirror=True)

make(lambda mb: (build_diagonal_skin(mb, HULL, n_strips=15, width=0.062, slope=1.9, direction=1,
                                     inset=0.024, thickness=0.011, xi0=0.02, xi1=0.98,
                                     mat=MAT["wood_timber"]),
                 # the second diagonal is laid on the first, not through it, and
                 # the frames are then fastened *over* both: planking 0-24 mm,
                 # first diagonal 24-35, second 35-46, timbers 46-86.  The
                 # 70 mm inset this started with pushed the skin inboard of the
                 # frames instead of stacking the boat properly, which still cut
                 # 11 727 triangle pairs through them.
                 build_diagonal_skin(mb, HULL, n_strips=15, width=0.062, slope=1.9, direction=-1,
                                     inset=0.035, thickness=0.011, xi0=0.02, xi1=0.98,
                                     mat=MAT["wood_timber"])),
     "Inner_Diagonal_Skin", col_hull, mirror=True)

# --------------------------------------------------------------------------
# 2. structure
# --------------------------------------------------------------------------
make(lambda mb: build_frames(mb, HULL, spacing=0.152, depth=0.040, width=0.028, xi0=0.026,
                             xi1=0.974, t0=0.010, t1=0.950, plank_thickness=0.048,
                             # 22 stations across the section: enough for a
                             # smooth bilge in the cutaways, few enough that the
                             # timbers stay under the 19 000-triangle export
                             # budget without being decimated
                             n_t=22),
     "Frames", col_structure, mirror=True)

make(lambda mb: (
    solid_between_sections(mb, HULL, np.linspace(0.001, 0.048, 6), 0.026, MAT["wood_timber"]),
    solid_between_sections(mb, HULL, np.linspace(0.960, 0.999, 5), 0.026, MAT["wood_timber"]),
    build_keel(HULL, mb, width=0.115, depth=0.090),
    build_stem(HULL, mb, width=0.120, depth=0.120),
    build_sternpost(HULL, mb, width=0.095, depth=0.110),
    build_keelson(HULL, mb, width=0.100, height=0.080, xi0=0.05, xi1=0.95),
    build_gunwale(HULL, mb, out_width=0.045, in_width=0.090, height=0.034, xi0=0.006, xi1=0.994),
    build_rubbing_strake(HULL, mb, t=0.905, r=0.019, xi0=0.045, xi1=0.955, offset=0.006),
    build_stem_band(HULL, mb, r=0.020, n=16),
), "Keel_Stem_Frames_Gunwale", col_structure, mirror=True)

make(lambda mb: build_transom(HULL, mb, t_lo=0.02, t_top=0.975), "Transom", col_structure)

# engine bearers, boiler seating, floors
def _bearer_ends():
    """How far forward the engine bearers can run and stay inside the planking.

    They are straight timbers at a fixed spacing, and the hull closes in on
    them: run to x = 1.35, the outer edge of the starboard bearer stands
    152 mm out through the bottom planking -- invisible under water, obvious
    the moment the model is sectioned.
    """
    # measured at the bottom of the bearer, where the bilge is tightest: the
    # bearer is 180 mm deep and its lower arris is what stands out
    for x in np.arange(1.60, 0.10, -0.02):
        if half_breadth_at(HULL, HULL.xi_of(x), floor_z(x) + 0.04, n=40) >= Y_BEARER + 0.16:
            return float(x)
    return 0.40


def _bearers(mb):
    xf = _bearer_ends()
    for s in (-1, 1):
        xs = np.linspace(xf, -1.55, 22)
        grid = np.zeros((len(xs), 4, 3))
        for i, x in enumerate(xs):
            z = floor_z(x) + 0.12
            zb, zt = z - 0.09, z + 0.09
            # a bearer standing in the bilge has its lower outboard arris
            # chamfered, not square: the bilge is 0.44 m half-breadth there, so
            # a square section 0.47 m wide stands 61 mm out through the bottom.
            # Follow the bilge instead, as the shipwright did.
            out_b = min(Y_BEARER + 0.05,
                        half_breadth_at(HULL, HULL.xi_of(x), zb, n=40) - 0.012)
            grid[i, 0] = (x, s * (Y_BEARER - 0.05), zb)
            grid[i, 1] = (x, s * out_b, zb)
            grid[i, 2] = (x, s * (Y_BEARER + 0.05), zt)
            grid[i, 3] = (x, s * (Y_BEARER - 0.05), zt)
        mb.add_grid(grid, MAT["wood_timber"], close_v=True)
    # cross floors under the bearers
    for x in np.arange(min(1.3, xf), -1.6, -0.28):
        z = floor_z(x)
        # measure the breadth at the underside of the floor, not above it: a
        # hull narrows downward, so taking the width 0.16 m up the topsides
        # makes the floor timber 69 mm too long at the bilge
        half = half_breadth_at(HULL, HULL.xi_of(x), z + 0.072, n=48) * 0.94
        mb.add_box((x, 0, z + 0.10), (0.09, half * 1.95, 0.055), mat=MAT["wood_timber"])
    # boiler foundation ring
    z0 = floor_z(X_BOILER) + 0.155
    cyl(mb, (X_BOILER, 0, z0 - 0.02), (X_BOILER, 0, z0 + 0.05), 0.46, seg=28, mat=MAT["iron"])


make(_bearers, "Engine_Bearers_Floors", col_structure)

# --------------------------------------------------------------------------
# 3. decks, coamings, thwarts, canopy
# --------------------------------------------------------------------------
X_FOREDECK_AFT = 3.10
X_FOREDECK_FWD = 3.80
X_COAMING_FWD = 1.35
X_COAMING_AFT = -1.55


# Deck boards: three timbers cycling, so the deck reads as planking.
deck_mats = []
for i, (v, w) in enumerate(((1.00, 1.00), (0.93, 1.05), (0.87, 0.96))):
    deck_mats.append(_register(bl.wood_material(
        f"Pine_Deck_{i}", base=(0.30 * v * w, 0.20 * v, 0.105 * v / w),
        dark=(0.15 * v, 0.095 * v, 0.045 * v), rough=0.52, bump=0.26)))


def _decks(mb):
    """Side decks, foredeck and after deck, laid as individual boards.

    The boards have real caulking gaps and slightly different timbers; a
    single-surface slab with a wood texture reads as a painted floor from
    every angle, which is what a deck must never do.
    """
    # --- side decks: two boards a side, following the sheer ---
    xs = np.linspace(-3.55, 3.62, 48)
    for s in (-1, 1):
        def edge(x, s=s):
            xi = HULL.xi_of(x)
            z = HULL.sheer_z(xi) - DECK_DROP
            outer = half_breadth_at(HULL, xi, z - 0.02, n=48) - 0.020
            inner = max(0.10, outer - 0.16)
            return (s * min(inner, outer), s * outer)

        plank_panel(mb, xs, edge,
                    lambda x: HULL.sheer_z(HULL.xi_of(x)) - DECK_DROP,
                    deck_mats, thick=0.032, n_planks=2, gap=0.006)
    # --- foredeck: laid board by board across the full breadth ---
    xs = np.linspace(X_FOREDECK_AFT, X_FOREDECK_FWD, 20)

    def fedge(x):
        xi = HULL.xi_of(x)
        z = HULL.sheer_z(xi) - DECK_DROP
        # breadth at the deck's own level: measuring 70 mm above it reads the
        # topsides where they are wider and stands the deck edge out through
        # the planking abreast the bow
        half = half_breadth_at(HULL, xi, z - 0.02, n=48) - 0.020
        return (-half, half)

    plank_panel(mb, xs, fedge,
                lambda x: HULL.sheer_z(HULL.xi_of(x)) - DECK_DROP,
                deck_mats, thick=0.032, gap=0.005)
    for i in range(len(xs) - 1):  # deck beams underneath
        x = xs[i]
        half = half_breadth_at(HULL, HULL.xi_of(x), sheer_at(x) - 0.05)
        mb.add_box((x, 0, HULL.sheer_z(HULL.xi_of(x)) - DECK_DROP - 0.045),
                   (0.06, half * 1.9, 0.05), None, MAT["wood_timber"])
    # --- after deck ---
    xs2 = np.linspace(-3.62, -2.85, 12)

    def aedge(x):
        xi = HULL.xi_of(x)
        z = HULL.sheer_z(xi) - DECK_DROP
        half = half_breadth_at(HULL, xi, z - 0.02, n=48) - 0.020
        return (-half, half)

    plank_panel(mb, xs2, aedge,
                lambda x: HULL.sheer_z(HULL.xi_of(x)) - DECK_DROP,
                deck_mats, thick=0.032, gap=0.005)


make(_decks, "Decks", col_deck)


def _coamings(mb):
    """Coaming round the engine and boiler space, which carries the canopy."""
    for x, x2 in ((X_COAMING_FWD, X_COAMING_AFT),):
        pass
    for x in (X_COAMING_FWD, X_COAMING_AFT):
        xi = HULL.xi_of(x)
        z = HULL.sheer_z(xi) - DECK_DROP
        half = half_breadth_at(HULL, xi, z + 0.10) - 0.02
        mb.add_box((x, 0, z + 0.055), (0.075, half * 1.92, 0.11), mat=MAT["wood_timber"])
    # longitudinal coaming/seat backs both sides
    for s in (-1, 1):
        xs = np.linspace(X_COAMING_FWD, X_COAMING_AFT, 12)
        grid = np.zeros((len(xs), 4, 3))
        for i, x in enumerate(xs):
            xi = HULL.xi_of(x)
            z = HULL.sheer_z(xi) - DECK_DROP
            outer = half_breadth_at(HULL, xi, z + 0.10) - 0.02
            inner = outer - 0.075
            grid[i, 0] = (x, s * outer, z)
            grid[i, 1] = (x, s * inner, z)
            grid[i, 2] = (x, s * inner, z + 0.16)
            grid[i, 3] = (x, s * outer, z + 0.16)
        mb.add_grid(grid, MAT["wood_timber"], close_v=True)


make(_coamings, "Coamings", col_deck)


def _seating(mb):
    """Four moulded thwarts, each landing on cleats rather than floating.

    A seat that is a plain box hanging in the air is the single most common
    "3D model" tell in a small boat; the eye wants to see what holds it up.
    Each plank here is crowned and tapered like a real thwart, sits on two
    cleats let into the frames, and the two wide passenger thwarts carry a
    centre stanchion down to the keelson.
    """
    seats = ((2.30, 0.26, True), (1.78, 0.26, True),
             (-2.55, 0.30, False), (-1.95, 0.24, False))
    for x, width, has_post in seats:
        xi = HULL.xi_of(x)
        drop = DECK_DROP + 0.16
        ys, z_top = parts.thwart_plank(mb, HULL, xi, top_drop=drop, width=width,
                                       thick=0.045, mat=MAT["wood_timber"],
                                       end_inset=0.035)
        half = max(abs(ys[0]), abs(ys[-1]))
        # cleats under each end, let into the frames
        for s_ in (-1, 1):
            mb.add_box((x, s_ * (half - 0.055), z_top - 0.045 - 0.017),
                       (width * 0.9, 0.075, 0.032), None, MAT["wood_timber"])
        # centre stanchion on the two wide thwarts
        if has_post:
            z_floor = floor_z(x) + 0.03
            mb.add_box((x, 0.0, (z_floor + z_top - 0.045) * 0.5),
                       (0.055, 0.055, max(0.08, (z_top - 0.045) - z_floor)),
                       None, MAT["wood_timber"])
    # back-rest of the after seat
    xi = HULL.xi_of(-2.42)
    z = HULL.sheer_z(xi) - DECK_DROP - 0.15
    half = half_breadth_at(HULL, xi, z) - 0.03
    mb.add_box((-2.42, 0, z + 0.16), (0.05, half * 1.90, 0.20), None, MAT["wood_timber"])
    for s_ in (-1, 1):  # its two arms, so it is not a slab on nothing
        mb.add_box((-2.42, s_ * (half * 0.86), z + 0.06), (0.05, 0.05, 0.20),
                   None, MAT["wood_timber"])


make(_seating, "Seats", col_furn)


def _floorboards(mb):
    """Gratings in the after cockpit.

    Forward of the coaming the boat is decked; aft of it the passengers stood
    on the bare planking over the bilge, which is both cold and a trip hazard.
    A boat with a first-class cockpit has bottom boards in it.
    """
    parts.floor_gratings(mb, HULL, 0.575, 0.775, n_slats=5, slat_w=0.090, thick=0.024,
                         t=0.085, lift=0.045)
    parts.floor_gratings(mb, HULL, 0.245, 0.375, n_slats=3, slat_w=0.080, thick=0.022,
                         t=0.085, lift=0.040)


make(_floorboards, "Floorboards", col_furn)

# canopy: a canvas hood carried on the coaming round the machinery, with
# brass stanchions and a curved top -- the "canopy over the engine and boiler"
# described for 25-32 ft steam cutters (Kipling Society / ORG 1905 notes).
CANOPY_X = (1.32, -1.52)
CANOPY_RISE = 0.30


def _canopy_geom(x):
    """Deck level, coaming top height and the coaming's inner half-width."""
    xi = HULL.xi_of(x)
    z_deck = HULL.sheer_z(xi) - DECK_DROP
    z_coam = z_deck + 0.11
    outer = half_breadth_at(HULL, xi, z_deck + 0.10) - 0.02
    return z_coam, outer - 0.075


def _canopy_frame(mb):
    x0, x1 = CANOPY_X
    for x in np.linspace(x0, x1, 6):
        z_coam, half = _canopy_geom(x)
        pts = []
        for f in np.linspace(-1, 1, 15):
            zc = z_coam + CANOPY_RISE * math.sqrt(max(0.0, 1.0 - 0.90 * f ** 2))
            pts.append(np.array([x, f * half, zc]))
        mb.add_tube(np.array(pts), 0.013, segments=8, mat=MAT["brass"])
        # short stanchions from the coaming up to the hoop
        for sgn in (-1, 1):
            p0 = np.array([x, sgn * half * 0.99, z_coam - 0.02])
            p1 = np.array([x, sgn * half, z_coam + 0.02])
            cyl(mb, p0, p1, 0.015, seg=8, mat=MAT["brass"])
    # longitudinal strings
    for f in (-0.62, -0.22, 0.22, 0.62):
        pts = []
        for x in np.linspace(x0, x1, 9):
            z_coam, half = _canopy_geom(x)
            zc = z_coam + CANOPY_RISE * math.sqrt(max(0.0, 1.0 - 0.90 * f ** 2))
            pts.append(np.array([x, f * half, zc]))
        mb.add_tube(np.array(pts), 0.009, segments=6, mat=MAT["brass"])


make(_canopy_frame, "Canopy_Frame", col_deck)


def _canopy_cover(mb):
    """Painted canvas hood: tensioned over the hoops, sagging between them,
    seamed every 0.42 m, laced down to the coaming and finished with a
    scalloped valance."""
    x0, x1 = CANOPY_X
    n_x, n_f = 25, 23
    xs = np.linspace(x0, x1, n_x)
    fs = np.linspace(-1, 1, n_f)
    hoop_x = np.linspace(x0, x1, 6)

    def sag(x):
        """Canvas droops between the hoops that carry it."""
        d = np.min(np.abs(hoop_x - x))
        return -0.026 * (d / (hoop_x[1] - hoop_x[0]))       # up to 26 mm of droop

    grid = np.zeros((n_x, n_f, 3))
    for i, x in enumerate(xs):
        z_coam, half = _canopy_geom(x)
        edge_pull = 0.010 * (1.0 - abs(x - 0.5 * (x0 + x1)) / (0.5 * (x1 - x0)))
        for j, f in enumerate(fs):
            zc = z_coam + CANOPY_RISE * math.sqrt(max(0.0, 1.0 - 0.90 * f ** 2))
            # a slight lengthwise dip towards the middle, and a ripple across
            ripple = 0.006 * math.sin(f * math.pi * 3.0) * (1 - f * f)
            grid[i, j] = (x, f * half, zc + 0.010 + sag(x) + ripple + edge_pull)
    mb.add_grid(grid, MAT["canvas"])

    # seams: raised strips down the length of the hood
    for f in (-0.66, -0.33, 0.0, 0.33, 0.66):
        strip = np.zeros((n_x, 3, 3))
        for i, x in enumerate(xs):
            z_coam, half = _canopy_geom(x)
            zc = z_coam + CANOPY_RISE * math.sqrt(max(0.0, 1.0 - 0.90 * f ** 2)) + 0.010 + sag(x)
            for k, dy in enumerate((-0.008, 0.0, 0.008)):
                bulge = 0.004 if k == 1 else 0.0
                strip[i, k] = (x, f * half + dy, zc + bulge)
        mb.add_grid(strip, MAT["canvas"])

    # valance, hanging in scallops from the two edges
    for j in (0, n_f - 1):
        sgn = -1 if j == 0 else 1
        strip = np.zeros((n_x, 3, 3))
        for i, x in enumerate(xs):
            p = grid[i, j]
            scallop = 0.022 * (0.5 + 0.5 * math.cos((x - x0) * math.pi * 5.0))
            strip[i, 0] = (p[0], p[1], p[2] + 0.002)
            strip[i, 1] = (p[0], p[1] * 0.985, p[2] - 0.10 - scallop)
            strip[i, 2] = (p[0], p[1] * 0.965, p[2] - 0.115 - scallop * 0.6)
        mb.add_grid(strip, MAT["canvas"])

    # end curtains fore and aft
    for i in (0, n_x - 1):
        strip = np.zeros((n_f, 2, 3))
        for j in range(n_f):
            p = grid[i, j]
            strip[j, 0] = (p[0], p[1], p[2] + 0.002)
            strip[j, 1] = (p[0] + (0.07 if i == 0 else -0.07), p[1] * 0.955, p[2] - 0.20)
        mb.add_grid(strip, MAT["canvas"])

    # lacing: short ties from the valance down onto the coaming
    for i in range(0, n_x, 2):
        x = xs[i]
        z_coam, half = _canopy_geom(x)
        for sgn in (-1, 1):
            p0 = np.array([x, sgn * half * 0.975, z_coam + 0.012])
            p1 = np.array([x + 0.012, sgn * half * 0.93, z_coam - 0.035])
            cyl(mb, p0, p1, 0.0045, seg=6, mat=MAT["rope"])
        # grommets along the edge
        cyl(mb, (x, half * 0.98, z_coam + 0.02), (x, half * 0.98, z_coam + 0.028),
            0.010, seg=8, mat=MAT["brass"])


make(_canopy_cover, "Canopy_Cover", col_deck, thickness=0.0035)

# --------------------------------------------------------------------------
# 4. machinery
# --------------------------------------------------------------------------
Z_FLOOR_MID = floor_z(X_BOILER)
BOILER_H = 0.860
Z_BOILER_TOP = Z_FLOOR_MID + 0.16 + BOILER_H


def _boiler(mb):
    machinery.boiler(mb, (X_BOILER, 0.0, Z_FLOOR_MID + 0.16),
                     r=LAYOUT["boiler"]["r"], height=LAYOUT["boiler"]["h"])


make(_boiler, "Boiler", col_mach)

make(lambda mb: machinery.boiler_cutaway(mb, (X_BOILER, 0.0, Z_FLOOR_MID + 0.16),
                                         r=LAYOUT["boiler"]["r"],
                                         height=LAYOUT["boiler"]["h"]),
     "Boiler_Internals", col_mach)

Z_CRANK = floor_z(X_ENGINE) + 0.46
make(lambda mb: machinery.engine(mb, (X_ENGINE, 0.0, Z_CRANK)), "Engine", col_mach)

# funnel through the canopy
FUNNEL_TOP = sheer_at(X_BOILER) + 0.95
FUNNEL_BASE = Z_BOILER_TOP + 0.10
make(lambda mb: machinery.funnel(mb, (LAYOUT["funnel"]["x"], 0.0, FUNNEL_BASE),
                                 FUNNEL_TOP, r_bottom=0.080,
                                 r_top=LAYOUT["funnel"]["r"], rake_x=0.05),
     "Funnel", col_deck)

# shafting + screw + stern tube
P_CRANK = np.array([X_ENGINE - 0.34, 0.0, Z_CRANK])
P_SCREW = np.array([X_SCREW, 0.0, -0.45])
make(lambda mb: (machinery.shaft_line(mb, P_CRANK, P_SCREW, 0.024),
                 machinery.stern_tube(mb, lerp(P_CRANK, P_SCREW, 0.80), lerp(P_CRANK, P_SCREW, 0.99)),
                 # stern bracket
                 cyl(mb, (X_SCREW - 0.06, 0, -0.42),
                     (X_SCREW - 0.06, 0, HULL.keel_z(HULL.xi_of(X_SCREW)) + 0.03),
                     0.030, seg=12, mat=MAT["iron"]),
                 cyl(mb, (X_SCREW - 0.20, 0, -0.30), (X_SCREW + 0.10, 0, -0.30), 0.018, seg=10,
                     mat=MAT["iron"])),
     "Shafting", col_mach)

screw_ob = make(lambda mb: machinery.propeller(mb, (0, 0, 0), dia=machinery.SCREW_DIA,
                                               blades=2), "Propeller", col_moving)
origin_to(screw_ob, (0, 0, 0))
screw_ob.location = Vector(P_SCREW)

# rudder: steel plate aft of the screw
RUDDER_X = -3.62


def _rudder_ob():
    """Plate rudder hung on the transom: the stock passes down through the
    counter, the blade hangs below it aft of the screw, so the screw gets
    clean water and the blade never touches the planking."""
    mb = MeshBuilder("Rudder")
    pivot = np.array([RUDDER_X, 0.0, sheer_at(RUDDER_X) - 0.10])
    n = 9
    z_top, z_bot = 0.04, -0.60
    grid = np.zeros((n, 4, 3))
    for i in range(n):
        f = i / (n - 1)
        z = z_top + (z_bot - z_top) * f
        # blade widens a little towards the heel, as a plate rudder does
        w = 0.155 + 0.035 * f
        th = 0.011 * (1 - 0.25 * f)
        grid[i, 0] = (-0.015, th, z)
        grid[i, 1] = (-w, th, z)
        grid[i, 2] = (-w, -th, z)
        grid[i, 3] = (-0.015, -th, z)
    mb.add_grid(grid, MAT["paint_hull"], close_v=True)
    # stock, passing up through the counter to the tiller
    cyl(mb, (0, 0, 0.04), (0, 0, 0.10), 0.030, seg=12, mat=MAT["steel"])
    cyl(mb, (0, 0, 0.10), (0, 0, 0.06), 0.036, seg=12, mat=MAT["steel"])
    # tiller, reaching forward into the boat
    cyl(mb, (0, 0, 0.06), (1.02, -0.05, 0.15), 0.030, seg=10, mat=MAT["wood_timber"], r1=0.024)
    # pintles
    for z in (-0.06, -0.30, -0.54):
        cyl(mb, (-0.015, -0.03, z), (0.03, -0.03, z), 0.011, seg=8, mat=MAT["steel"])
    v = np.array(mb.verts) + pivot
    mb.verts = [tuple(p) for p in v]
    ob = bl.obj_from_builder(mb, "Rudder", mlist, col_moving)
    origin_to(ob, pivot)
    return ob


rudder_ob = _rudder_ob()

# --------------------------------------------------------------------------
# 5. pipework, valves, controls
# --------------------------------------------------------------------------


def _pipes(mb):
    # main steam: boiler stop valve -> engine valve chest
    machinery.pipe_run(mb, [(X_BOILER + 0.10, 0.0, Z_BOILER_TOP + 0.30),
                            (X_BOILER + 0.10, 0.0, Z_BOILER_TOP + 0.10),
                            (X_BOILER + 0.10, 0.28, Z_BOILER_TOP - 0.06),
                            (X_ENGINE + 0.10, 0.30, Z_CRANK + 0.62),
                            (X_ENGINE + 0.02, 0.22, Z_CRANK + 0.55)], r=0.017, lagging=True)
    # exhaust: engine -> funnel base
    machinery.pipe_run(mb, [(X_ENGINE, 0.20, Z_CRANK + 0.30),
                            (X_ENGINE + 0.40, 0.16, Z_CRANK + 0.42),
                            (X_BOILER - 0.25, 0.02, Z_BOILER_TOP - 0.20)], r=0.030, lagging=True)
    # feed: tank -> pump -> boiler check valve
    machinery.pipe_run(mb, [(-1.95, -0.30, floor_z(-1.95) + 0.14),
                            (-1.20, -0.34, floor_z(-1.20) + 0.20),
                            (X_ENGINE + 0.05, -0.28, Z_CRANK - 0.12),
                            (X_BOILER - 0.30, -0.24, Z_FLOOR_MID + 0.50)], r=0.012,
                       mat=MAT["copper"])
    # blow-down to the skin fitting
    machinery.pipe_run(mb, [(X_BOILER - 0.32, -0.22, Z_FLOOR_MID + 0.24),
                            (X_BOILER - 0.55, -0.30, Z_FLOOR_MID + 0.10),
                            (X_BOILER - 0.72, -0.34, Z_FLOOR_MID + 0.04)], r=0.013,
                       mat=MAT["copper"])
    # valves & controls
    machinery.valve(mb, (X_BOILER + 0.10, 0.0, Z_BOILER_TOP + 0.28), (0, 0, 1), 1.15)  # stop valve
    machinery.valve(mb, (X_ENGINE + 0.02, 0.22, Z_CRANK + 0.55), (0, 0, 1), 0.8)       # regulator
    machinery.gauge(mb, (X_BOILER + 0.34, 0.10, Z_BOILER_TOP - 0.20), (1, 0.2, 0.1))
    machinery.whistle(mb, (X_BOILER + 0.16, 0.30, Z_BOILER_TOP - 0.02), (0, 1, 0.2))
    # throttle/reversing console by the engineer's seat
    for x, z0 in ((-1.30, 0.0),):
        pass
    # feed water tank aft under the floor boards.  A box that fills the bilge
    # has to be sized from the bilge: 0.70 m wide is right amidships and 116 mm
    # too wide at its after end, where the hull has closed in.
    xt = -1.95
    zt = floor_z(xt) + 0.09
    yt = min(0.35, clear_y(HULL, xt - 0.28, xt + 0.28, zt - 0.09, clear=0.03))
    mb.add_box((xt, 0.0, zt), (0.55, yt, 0.18), mat=MAT["copper"])
    # coal bunker, abaft the boiler and forward of the engine: a riveted iron
    # bin with the coal standing proud of its open top, where a fireman can
    # reach over it with the shovel
    k = LAYOUT["bunker"]
    z = floor_z(k["x"]) + 0.14
    yb = min(0.39, clear_y(HULL, k["x"] - k["hx"], k["x"] + k["hx"], z, clear=0.03))
    mb.add_box((k["x"], 0.0, z + 0.14), (2 * k["hx"], yb, 0.36), mat=MAT["iron"])
    mb.add_box((k["x"], 0.0, z + 0.31), (2 * k["hx"] - 0.03, yb - 0.02, 0.05),
               mat=MAT["coal"])
    # its hinged lid, standing open against the boiler
    mb.add_box((k["x"] + k["hx"] - 0.02, 0.0, z + 0.44), (0.02, yb - 0.02, 0.20),
               mat=MAT["iron"])


make(_pipes, "Pipework_Fittings", col_mach)


# --------------------------------------------------------------------------
# 6. loose gear, navigation and safety equipment
# --------------------------------------------------------------------------
def _gear(mb):
    # hoisting eyes on the keelson (davit slings)
    for x in (2.05, -1.55):
        z = floor_z(x) + 0.09
        parts.eye_bolt(mb, np.array([x, 0.0, z]), direction=(0, 0, 1), scale=1.35)
    # stem ring and stern eye
    p = HULL.surface(0.012, 0.80)
    parts.eye_bolt(mb, np.array([p[0] - 0.12, 0.0, p[2]]), direction=(-1, 0, 0), scale=1.15)
    p = HULL.surface(0.99, 0.72)
    parts.eye_bolt(mb, np.array([p[0] + 0.12, 0.0, p[2]]), direction=(1, 0, 0), scale=1.0)
    # fenders both sides
    for s in (-1, 1):
        for x in (1.9, -1.9):
            xi = HULL.xi_of(x)
            p = HULL.surface(xi, 0.97)
            zf = HULL.sheer_z(xi) - 0.34
            hs = half_breadth_at(HULL, xi, zf)
            parts.fender(mb, np.array([x, s * (hs + 0.075), zf]), mat=MAT["rope"],
                         length=0.46, r=0.065)
    # boat hook stowed on the port side deck
    xh = 1.05
    zh = sheer_at(xh) - DECK_DROP + 0.055
    cyl(mb, (xh, 0.42, zh), (xh - 1.9, 0.42, zh + 0.02), 0.020, seg=10, mat=MAT["wood_timber"])
    cyl(mb, (xh - 1.9, 0.42, zh + 0.02), (xh - 1.99, 0.42, zh + 0.045), 0.013, seg=8, mat=MAT["steel"])
    sphere(mb, (xh - 2.0, 0.42, zh + 0.05), 0.020, seg=8, rings=6, mat=MAT["steel"])
    # Lifebuoy: a cork ring lashed FLAT on the canopy roof, which is where one
    # is actually kept on an open launch -- not standing on its edge in mid-air
    # over the canvas, which is what a ring placed by height alone does.
    xb = -0.55
    z_coam, half = _canopy_geom(xb)
    z_roof = z_coam + CANOPY_RISE + 0.010
    torus(mb, (xb, 0.0, z_roof + 0.052), 0.20, 0.052, seg=26, rseg=9, axis="Z",
          mat=MAT["canvas"])
    # four short lashings round the ring and through the canvas eyelets
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        lx, ly = 0.215 * math.cos(a), 0.215 * math.sin(a)
        cyl(mb, (xb + lx * 0.75, ly * 0.75, z_roof + 0.030),
            (xb + lx, ly, z_roof + 0.075), 0.007, seg=6, mat=MAT["rope"])
    # stove-in bailer + bucket
    p = HULL.surface(0.70, 0.16)
    cyl(mb, (p[0], -0.35, p[2] + 0.06), (p[0], -0.35, p[2] + 0.20), 0.085, seg=14,
        mat=MAT["wood_deck"], r1=0.10)
    # four oars stowed along the side benches, blades forward -- a steam
    # cutter rows as well as steams, and oars are what she is first away with
    # when the boiler is cold
    for k, s_ in enumerate((1, -1)):
        for j in range(2):
            xi = HULL.xi_of(2.35 - 0.55 * j)
            p = HULL.surface(xi, 0.86)
            pivot = np.array([2.55 - 0.55 * j, s_ * (0.52 + 0.075 * k),
                              HULL.sheer_z(xi) - DECK_DROP - 0.115 + 0.021 * k])
            omb = MeshBuilder("Oar")
            parts.oar(omb, length=3.30, inboard=0.95, blade_len=0.55,
                      blade_w=0.145, pivot_origin=False)
            roll = math.radians(92.0)
            R = np.array([[1, 0, 0], [0, math.cos(roll), -math.sin(roll)],
                          [0, math.sin(roll), math.cos(roll)]])
            # local +X runs aft (blades forward means the oar points -X)
            yaw = math.pi
            Ry = np.array([[math.cos(yaw), -math.sin(yaw), 0], [math.sin(yaw), math.cos(yaw), 0], [0, 0, 1]])
            mb.append_builder(omb, offset=pivot + np.array([-1.30, 0, 0]), rot=Ry @ R)
    # grapnel stowed forward on the starboard side deck
    xg = 2.95
    zg = sheer_at(xg) - DECK_DROP + 0.03
    parts.grapnel(mb, np.array([xg, -0.42, zg]), scale=0.9)
    # compass box on the foredeck
    xc = 3.30
    zc = sheer_at(xc) - DECK_DROP + 0.03
    mb.add_box((xc, 0, zc + 0.05), (0.22, 0.22, 0.10), mat=MAT["wood_timber"])
    cyl(mb, (xc, 0, zc + 0.10), (xc, 0, zc + 0.13), 0.085, seg=18, mat=MAT["brass"])
    cyl(mb, (xc, 0, zc + 0.13), (xc, 0, zc + 0.135), 0.075, seg=18, mat=MAT["glass"])
    # sidelights: brass housings with red to port and green to starboard.  The
    # housing was carrying the colour, and the starboard one was painted hull
    # black because no green existed in the palette -- the lens is the coloured
    # part, and both housings are brass.
    # A sidelight is a lamp on a bracket at the gunwale, outboard of the
    # canopy: on a pedestal, high enough that the light is not hidden by the
    # coaming or the canvas.  Mounting it flat on top of the canopy roof (where
    # it started) is not how one is fitted and it read as a green box lying on
    # the sailcloth.
    for s, lens in ((1, MAT["glass_red"]), (-1, MAT["glass_green"])):
        xl = 1.10
        yl = s * 0.93
        zs = sheer_at(xl)
        mb.add_box((xl, yl, zs + 0.012), (0.11, 0.10, 0.024), mat=MAT["brass"])
        cyl(mb, (xl, yl, zs + 0.024), (xl, yl, zs + 0.235), 0.020, seg=12, mat=MAT["brass"])
        zl = zs + 0.305
        mb.add_box((xl, yl, zl), (0.108, 0.096, 0.130), mat=MAT["brass"])
        # a hooded lens facing forward-outboard, as a sidelight is built
        cyl(mb, (xl + 0.052, yl - s * 0.008, zl + 0.012),
            (xl + 0.076, yl - s * 0.010, zl + 0.012), 0.042, seg=14, mat=MAT["brass"])
        cyl(mb, (xl + 0.075, yl - s * 0.010, zl + 0.012),
            (xl + 0.080, yl - s * 0.010, zl + 0.012), 0.033, seg=14, mat=lens)
        # hood over the lens, and a small vent cap on the lamp
        mb.add_box((xl + 0.048, yl - s * 0.008, zl + 0.062), (0.078, 0.086, 0.012),
                   mat=MAT["brass"])
        cyl(mb, (xl, yl, zl + 0.065), (xl, yl, zl + 0.098), 0.030, seg=12, mat=MAT["brass"])
    # shovel & poker for the stokehold, and the slice stowed against the boiler
    cyl(mb, (-0.15, -0.55, floor_z(-0.15) + 0.06), (0.35, -0.55, floor_z(-0.15) + 0.30), 0.014,
        seg=8, mat=MAT["steel"])
    mb.add_box((0.36, -0.55, floor_z(-0.15) + 0.31), (0.14, 0.16, 0.02), mat=MAT["steel"])
    cyl(mb, (0.05, 0.44, floor_z(0.05) + 0.05), (0.05, 0.44, floor_z(0.05) + 0.62), 0.013,
        seg=8, mat=MAT["steel"])
    # a coil of mooring line, flaked down on the foredeck where the bowman
    # handles it -- a boat with a painter ring and no line is a boat that has
    # never been made fast
    xc, yc = 2.62, 0.34
    zc0 = sheer_at(xc) - DECK_DROP + 0.020
    for ring, (r, n) in enumerate(((0.115, 3), (0.075, 2))):
        for i in range(n):
            torus(mb, (xc, yc, zc0 + 0.012 + 0.016 * ring), r - 0.010 * i,
                  0.0105, seg=22, rseg=7, axis="Z", mat=MAT["rope"])


make(_gear, "Gear_Nav_Safety", col_gear)

# morse/tiller connection: a small steering quadrant is already on the rudder

# --------------------------------------------------------------------------
# 7. report and save
# --------------------------------------------------------------------------
allobs = [o for c in (col_hull, col_structure, col_deck, col_mach, col_furn, col_gear, col_moving)
          for o in c.objects]
print(f"TOTAL verts={sum(len(o.data.vertices) for o in allobs)} "
      f"faces={sum(len(o.data.polygons) for o in allobs)} objects={len(allobs)}")
print(f"LAYOUT boiler_x={X_BOILER} engine_x={X_ENGINE} crank_z={Z_CRANK:.3f} "
      f"screw={P_SCREW} funnel_top={FUNNEL_TOP:.3f}")

bpy.context.scene["boat_name"] = "25 ft Steam Cutter (1888)"
bpy.context.scene["loa_m"] = HULL.loa
bpy.context.scene["stud_per_m"] = specs.STUD_PER_M
bl.save_blend(f"{ROOT}/boats/blend/boat_a_steam_cutter.blend")

if not QUICK:
    hull_objs = [o for c in (col_hull, col_structure, col_deck) for o in c.objects]
    bl.export_object(bl.join_objects(hull_objs, "Hull_Export"),
                     f"{ROOT}/boats/exports/steam_cutter_hull.glb", "glb")
    print("EXPORTED steam hull glb")

# --------------------------------------------------------------------------
# 8. renders
# --------------------------------------------------------------------------
if not NO_RENDER:
    bl.studio(world_strength=0.5, ground_z=-1.7)
    shots = {
        "hero": ((10.4, -12.6, 5.4), (0.0, 0, 0.30), 50),
        "broadside": ((0.0, -14.5, 0.9), (0, 0, 0.45), None),
        "bow_quarter": ((10.6, -6.8, 3.2), (0.6, 0, 0.25), 55),
        "stern_quarter": ((-10.2, -6.2, 3.0), (-0.8, 0, 0.25), 55),
        "from_above": ((2.0, -5.0, 15.0), (0.0, 0, 0.2), 45),
        "machinery": ((3.2, -3.0, 2.4), (0.2, 0, 0.55), 45),
    }
    for name, (loc, look, lens) in shots.items():
        if lens is None:
            cam = bl.camera(name, loc, look, ortho=8.8)
        else:
            cam = bl.camera(name, loc, look, lens=lens)
        bl.render(f"{ROOT}/boats/renders/steam_{name}.png", cam,
                  res=(1200, 750) if not QUICK else (640, 400), samples=24 if QUICK else 72)
print("BUILD COMPLETE")

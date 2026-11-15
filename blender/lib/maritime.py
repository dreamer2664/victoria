"""
maritime.py -- dock and waterfront infrastructure.

Everything structural on the water's edge: quay walls, coping, bollards, capstans,
ladders, fenders, the graving docks with their caissons, and the building slips.
"""
import math
from core import MeshBuilder, QUAY_Z, SILL_Z, DOCK_BED_Z
import parts as P


# ================================================================ quay wall
def quay_wall(mb, axis, fixed, u0, u1, inward, top_z=QUAY_Z, bed_z=DOCK_BED_Z,
              face="granite", coping_w=1.05, batter=0.045, fender=True,
              ladders=True, ladder_every=34.0, rings=True, ring_every=17.0):
    """A Victorian masonry quay wall seen from the water: coped edge, battered face,
    projecting fender course, recessed ladders and mooring rings."""
    mp = P.wmap(axis, fixed, inward)

    # main face, battered: lean the wall back as it rises
    steps = 8
    for i in range(steps):
        za = bed_z + (top_z - bed_z) * i / steps
        zb = bed_z + (top_z - bed_z) * (i + 1) / steps
        da = batter * (top_z - za)          # further out (toward water) lower down
        db = batter * (top_z - zb)
        P.slab(mb, mp, u0, u1, za, zb, -da, 0.0 + (-db) + 1.6, face)
    # solid fill behind the face so the quay reads as ground, not a skin
    P.slab(mb, mp, u0, u1, bed_z, top_z - 0.55, 1.4, 3.2, "rubble")

    # coping: granite blocks with a chamfered water-side arris
    P.slab(mb, mp, u0, u1, top_z - 0.55, top_z, -0.28, coping_w, "granite")
    P.slab(mb, mp, u0, u1, top_z - 0.62, top_z - 0.55, -0.34, coping_w, "granite")
    if fender:
        P.slab(mb, mp, u0, u1, top_z - 1.35, top_z - 0.55, -0.34, 0.0, "granite")
        P.slab(mb, mp, u0, u1, top_z - 1.55, top_z - 1.35, -0.42, 0.0, "granite")
    # below-water fender course
    P.slab(mb, mp, u0, u1, 0.85, 1.35, -0.22, 0.2, "granite")

    if ladders:
        n = max(1, int((u1 - u0) / ladder_every))
        for i in range(n):
            uu = u0 + (u1 - u0) * (i + 0.5) / n
            dock_ladder(mb, mp, uu, 0.0, top_z - 0.55)
    if rings:
        n = max(1, int((u1 - u0) / ring_every))
        for i in range(n):
            uu = u0 + (u1 - u0) * (i + 0.5) / n
            mooring_ring(mb, mp, uu, top_z - 2.15)


def dock_ladder(mb, mp, u, z_bottom, z_top, mat="iron"):
    """Recessed iron ladder set into a quay or dock wall."""
    w = 0.52
    P.slab(mb, mp, u - w / 2 - 0.08, u + w / 2 + 0.08, z_bottom, z_top, -0.28, -0.06, "black")
    for du in (-w / 2, w / 2):
        P.slab(mb, mp, u + du - 0.03, u + du + 0.03, z_bottom, z_top, -0.24, -0.20, mat)
    z = z_bottom + 0.30
    while z < z_top - 0.2:
        P.slab(mb, mp, u - w / 2, u + w / 2, z - 0.022, z + 0.022, -0.26, -0.22, mat)
        z += 0.30


def mooring_ring(mb, mp, u, z, r=0.22, mat="iron"):
    """Cast mooring ring on a wall plate."""
    P.slab(mb, mp, u - 0.30, u + 0.30, z - 0.26, z + 0.26, -0.16, -0.05, mat)
    # ring: 10 segments in a circle lying against the wall
    n = 10
    for i in range(n):
        a0 = 2 * math.pi * i / n
        a1 = 2 * math.pi * (i + 1) / n
        p0 = mp(u + math.cos(a0) * r, z + math.sin(a0) * r, -0.20)
        p1 = mp(u + math.cos(a1) * r, z + math.sin(a1) * r, -0.20)
        mb.add_beam(p0, p1, 0.075, 0.075, mat)


# ================================================================ furniture
def bollard(mb, x, y, z, mat="iron", h=1.05, style="liverpool"):
    """Cast-iron mooring bollard. The 'liverpool' style is a waisted post with a
    bulbous collar; used along every British dock quay of the period."""
    mb.add_cyl(x, y, z, z + 0.12, 0.42, "granite", seg=10)          # stone pad
    if style == "liverpool":
        mb.add_cyl(x, y, z + 0.12, z + 0.26, 0.30, mat, seg=12)
        mb.add_cyl(x, y, z + 0.26, z + 0.55, 0.19, mat, seg=12, r2=0.22)
        mb.add_cyl(x, y, z + 0.55, z + h, 0.30, mat, seg=12, r2=0.26)
        mb.add_disc(x, y, z + h + 0.001, 0.30, mat, seg=12)
        mb.add_cyl(x, y, z + h, z + h + 0.05, 0.30, mat, seg=12, r2=0.10)
    else:                                                            # cannon style
        mb.add_cyl(x, y, z + 0.12, z + h, 0.16, mat, seg=10, r2=0.19)
        mb.add_cyl(x, y, z + h, z + h + 0.10, 0.19, mat, seg=10, r2=0.10)


def capstan(mb, x, y, z, mat="iron", h=1.0):
    """Wrought-iron hand capstan with four handspike sockets."""
    mb.add_cyl(x, y, z, z + 0.10, 0.55, "granite", seg=12)
    mb.add_cyl(x, y, z + 0.10, z + 0.18, 0.42, mat, seg=14)
    mb.add_cyl(x, y, z + 0.18, z + h * 0.72, 0.26, mat, seg=14, r2=0.30)
    mb.add_cyl(x, y, z + h * 0.72, z + h, 0.36, mat, seg=14, r2=0.24)
    mb.add_disc(x, y, z + h + 0.001, 0.24, mat, seg=14)
    for i in range(4):
        a = math.pi / 2 * i + math.pi / 8
        px, py = x + math.cos(a) * 0.34, y + math.sin(a) * 0.34
        mb.add_beam((px, py, z + h * 0.80),
                    (x + math.cos(a) * 0.62, y + math.sin(a) * 0.62, z + h * 0.80),
                    0.09, 0.09, mat)


def timber_fender(mb, x, y, z, z_top=1.5, w=0.30, d=0.25, mat="timber"):
    """Vertical timber fender on a wharf face; several stacked one above another."""
    mb.add_box_c(x, y, z + (z_top - z) / 2, d, w, z_top - z, mat)
    mb.add_box_c(x, y, z_top, d + 0.06, w + 0.06, 0.10, "iron")


def fender_float(mb, x, y, z, length=6.0, axis="Y"):
    """Timber cambered fender float between ship and quay."""
    if axis == "Y":
        mb.add_box_c(x, y, z + 0.12, 0.55, length, 0.45, "timber")
        mb.add_box_c(x, y, z + 0.42, 0.62, length * 0.98, 0.14, "timber")
    else:
        mb.add_box_c(x, y, z + 0.12, length, 0.55, 0.45, "timber")
        mb.add_box_c(x, y, z + 0.42, length * 0.98, 0.62, 0.14, "timber")


# ================================================================ landing stage
def pontoon(mb, x0, y0, x1, y1, z_deck=1.35, thickness=1.5, lanes=2):
    """A floating landing stage: timber/steel pontoon with a gull-wing canopy roof,
    booking shelters and mooring bridles. Modelled on the Liverpool landing stage
    as illustrated in Ocean Steamships (1891), pl. p.191."""
    mb.add_box(x0, y0, z_deck - thickness, x1, y1, z_deck, "steel_plate")
    mb.add_box(x0, y0, z_deck - thickness - 0.35, x1, y1, z_deck - thickness, "black")
    # deck planking
    mb.add_box(x0 - 0.1, y0 - 0.1, z_deck, x1 + 0.1, y1 + 0.1, z_deck + 0.06, "plank",
               top="plank")
    # kerb / nosing along the water edge
    mb.add_box(x0 - 0.15, y0 - 0.15, z_deck, x0 + 0.25, y1 + 0.15, z_deck + 0.22, "iron")
    # columns + canopy over the covered walk
    n = max(2, int((y1 - y0) / 6.0))
    for i in range(n + 1):
        cy = y0 + (y1 - y0) * i / n
        for cx in (x0 + 1.4, x1 - 1.4):
            mb.add_cyl(cx, cy, z_deck, z_deck + 3.9, 0.10, "iron", seg=8)
    # gull-wing roof: two sloped panels
    zr = z_deck + 3.9
    xm = (x0 + x1) / 2
    mb.add_quad((x0 - 0.5, y0, zr), (xm, y0, zr + 0.75), (xm, y1, zr + 0.75),
                (x0 - 0.5, y1, zr), "canvas")
    mb.add_quad((xm, y0, zr + 0.75), (x1 + 0.5, y0, zr), (x1 + 0.5, y1, zr),
                (xm, y1, zr + 0.75), "canvas")
    # valance / scalloped edge
    mb.add_box(x0 - 0.55, y0, zr - 0.25, x0 - 0.45, y1, zr + 0.05, "canvas")
    mb.add_box(x1 + 0.45, y0, zr - 0.25, x1 + 0.55, y1, zr + 0.05, "canvas")
    # ticket shelter
    mb.add_box(x1 - 4.5, y0 + 3.0, z_deck, x1 - 1.2, y1 - 3.0, z_deck + 2.9, "timber")
    mb.add_box(x1 - 4.8, y0 + 2.7, z_deck + 2.9, x1 - 0.9, y1 - 2.7, z_deck + 3.05, "slate")
    mb.add_quad_uv((x1 - 4.52, y0 + 3.05, z_deck + 2.0), (x1 - 4.52, y1 - 3.05, z_deck + 2.0),
                   (x1 - 4.52, y1 - 3.05, z_deck + 2.75), (x1 - 4.52, y0 + 3.05, z_deck + 2.75),
                   "sign_booking_office")
    # gas lamps on the canopy columns
    for i in range(n + 1):
        cy = y0 + (y1 - y0) * i / n
        mb.add_cyl(x1 - 1.4, cy, zr + 0.1, zr + 0.55, 0.05, "iron", seg=6)
        mb.add_cyl(x1 - 1.4, cy, zr + 0.55, zr + 0.92, 0.14, "lamp_glow", seg=8, r2=0.09)
    return dict(deck=z_deck, zroof=zr + 0.75)


def gangway_bridge(mb, x0, y0, z_low, x1, z_high, width=3.6, canopy=True,
                   side="Y", lattice=True):
    """The great shore-to-pontoon gangway bridges at Liverpool: an inclined bridge
    with lattice parapets and a glazed/awning canopy on iron standards.
    Shoreside end at (x0) with deck z_low, pontoon end at (x1) with z_high."""
    length = abs(x1 - x0)
    sgn = 1 if x1 > x0 else -1

    def pt(t, d=0.0, z_off=0.0, side_off=0.0):
        xx = x0 + (x1 - x0) * t
        zz = z_low + (z_high - z_low) * t + z_off
        if side == "Y":
            return (xx + d, y0 + side_off, zz)
        return (y0 + side_off, xx + d, zz)

    n = max(3, int(length / 2.6))
    # deck
    for i in range(n):
        t0, t1 = i / n, (i + 1) / n
        mb.add_quad(pt(t0, 0, 0, -width / 2), pt(t1, 0, 0, -width / 2),
                    pt(t1, 0, 0, width / 2), pt(t0, 0, 0, width / 2), "plank")
        mb.add_quad(pt(t0, 0, -0.22, width / 2), pt(t1, 0, -0.22, width / 2),
                    pt(t1, 0, -0.22, -width / 2), pt(t0, 0, -0.22, -width / 2), "timber")
        # side fascia
        for s in (-1, 1):
            mb.add_quad(pt(t0, 0, 0, s * width / 2), pt(t0, 0, -0.22, s * width / 2),
                        pt(t1, 0, -0.22, s * width / 2), pt(t1, 0, 0, s * width / 2),
                        "iron")
    # parapets: standards + lattice diagonals + handrail
    for s in (-1, 1):
        for i in range(n + 1):
            t = i / n
            mb.add_beam(pt(t, 0, 0, s * width / 2), pt(t, 0, 1.05, s * width / 2),
                        0.07, 0.07, "iron")
        for hz in (1.05, 0.55):
            mb.add_beam(pt(0, 0, hz, s * width / 2), pt(1, 0, hz, s * width / 2),
                        0.06, 0.06, "iron")
        if lattice:
            for i in range(n):
                t0, t1 = i / n, (i + 1) / n
                mb.add_beam(pt(t0, 0, 0.10, s * width / 2), pt(t1, 0, 0.95, s * width / 2),
                            0.035, 0.035, "iron")
                mb.add_beam(pt(t0, 0, 0.95, s * width / 2), pt(t1, 0, 0.10, s * width / 2),
                            0.035, 0.035, "iron")
    if canopy:
        for s in (-1, 1):
            for i in range(0, n + 1, 2):
                t = i / n
                mb.add_beam(pt(t, 0, 0, s * width / 2), pt(t, 0, 3.1, s * width / 2 * 0.92),
                            0.07, 0.07, "iron")
            mb.add_beam(pt(0, 0, 3.05, s * width / 2 * 0.92),
                        pt(1, 0, 3.05, s * width / 2 * 0.92), 0.06, 0.10, "iron")
        # awning surface, cambered
        for i in range(n):
            t0, t1 = i / n, (i + 1) / n
            for s0, s1 in ((-1, 0), (0, 1)):
                w0 = width / 2 * 0.95
                mb.add_quad(
                    pt(t0, 0, 3.35 + 0.25 * (1 - abs(s0)), s0 * w0),
                    pt(t0, 0, 3.35 + 0.25 * (1 - abs(s1)), s1 * w0),
                    pt(t1, 0, 3.35 + 0.25 * (1 - abs(s1)), s1 * w0),
                    pt(t1, 0, 3.35 + 0.25 * (1 - abs(s0)), s0 * w0), "canvas")
    return dict(length=length)


# ================================================================ graving dock
def graving_dock(mb, x0, y0, length, width, depth=9.6, coping="granite",
                 altar_steps=3, altar_w=2.4, entrance="N", stairs=True,
                 keel_blocks=True, caissons=()):
    """A Victorian graving (dry) dock of the Belfast type.

    Modelled on the researched Alexandra Dock (1885-89, 800 ft x 80 ft, the largest
    dry dock in the world when opened, arranged to be worked in three sections by
    caissons). The dock is oriented along Y; `entrance` gives the river end.
    """
    x1, y1 = x0 + width, y0 + length
    # `depth` is measured DOWN FROM THE COPING, which is how graving docks are
    # specified (a "26 ft dock" means water over the sill, not floor elevation).
    floor_z = QUAY_Z - depth
    t = 1.8

    # ---- floor of the dock (granite altar blocks throughout)
    mb.add_box(x0, y0, floor_z - 0.6, x1, y1, floor_z, "granite")
    # ---- side walls with stepped altars (the tiers a ship's bilge rests against)
    for side, (fx0, fx1) in (("W", (x0, x0 + t)), ("E", (x1 - t, x1))):
        n = altar_steps
        for i in range(n):
            zt = floor_z + 0.65 * (i + 1)
            inset = altar_w * (1 - (i + 1) / (n + 0.6))
            if side == "W":
                a = x0 + inset
                mb.add_box(a, y0, floor_z, fx1, y1, zt, "granite")
            else:
                b = x1 - inset
                mb.add_box(fx0, y0, floor_z, b, y1, zt, "granite")
        # upper vertical wall from the last altar to coping
        zt = floor_z + 0.65 * n
        mb.add_box(fx0, y0, zt, fx1, y1, QUAY_Z - 0.55, "rubble")
        # granite coping at ground level
        if side == "W":
            mb.add_box(x0 - 0.3, y0, QUAY_Z - 0.55, x0 + 1.5, y1, QUAY_Z, coping)
        else:
            mb.add_box(x1 - 1.5, y0, QUAY_Z - 0.55, x1 + 0.3, y1, QUAY_Z, coping)
    # ---- end walls
    for endl, yy in (("S", y0), ("N", y1)):
        mb.add_box(x0, yy - 0.0 if endl == "N" else yy - t, floor_z,
                   x1, yy + t if endl == "N" else yy + 0.0, QUAY_Z - 0.55, "rubble")
    mb.add_box(x0, y0 - t, QUAY_Z - 0.55, x1, y0, QUAY_Z, coping)
    # ---- caisson stops: intermediate grooves dividing the dock into sections
    for frac in caissons:
        yy = y0 + length * frac
        mb.add_box(x0, yy - 0.9, floor_z, x0 + 2.2, yy + 0.9, QUAY_Z - 1.2, "granite")
        mb.add_box(x1 - 2.2, yy - 0.9, floor_z, x1, yy + 0.9, QUAY_Z - 1.2, "granite")
    # ---- keel blocks down the centre line
    if keel_blocks:
        nb = int(length / 4.2)
        for i in range(nb):
            yy = y0 + length * (i + 0.5) / nb
            if yy < y0 + 4 or yy > y1 - 4:
                continue
            mb.add_box_c((x0 + x1) / 2, yy, floor_z + 0.85, 1.5, 1.4, 1.7, "timber")
            mb.add_box_c((x0 + x1) / 2, yy, floor_z + 0.12, 1.9, 1.8, 0.24, "timber")
    # ---- stairways down the altars
    if stairs:
        for k in range(3):
            yy = y0 + length * (0.22 + 0.26 * k)
            _dock_stair(mb, x1 - t - 0.6, yy, floor_z, QUAY_Z, altar_steps, altar_w)
    # ---- bollards along both copings
    nb = int(length / 12.0)
    for i in range(nb + 1):
        yy = y0 + 2.0 + (length - 4.0) * i / nb
        bollard(mb, x0 + 0.55, yy, QUAY_Z)
        bollard(mb, x1 - 0.55, yy, QUAY_Z)
    return dict(floor_z=floor_z, x0=x0, y0=y0, x1=x1, y1=y1)


def _dock_stair(mb, x, y, z_bottom, z_top, n_altar, altar_w, width=1.6):
    """A stone stair cut into the dock altar."""
    n = max(6, int((z_top - z_bottom) / 0.28))
    rise = (z_top - z_bottom) / n
    run = 0.30
    for i in range(n):
        zz = z_bottom + rise * i
        mb.add_box(x - width / 2, y + run * i, zz, x + width / 2, y + run * (i + 1) + 0.02,
                   zz + rise, "granite")


def caisson(mb, x0, y0, width, height, thickness=1.6, draft_end=False):
    """A hollow steel caisson gate -- a floating vessel in its own right that is
    warped into the dock entrance and pumped to seat itself on the sill.
    (H&W registered their Hamilton Dock caisson of 1867 as hull no. 50.)"""
    mb.add_box(x0, y0, -4.0, x0 + width, y0 + thickness, height, "steel_plate")
    mb.add_box(x0 + 0.6, y0 - 0.25, 0.8, x0 + width - 0.6, y0 + thickness + 0.25,
               1.05, "iron")          # working deck / walkway
    # rubbing timbers and sealing strip
    mb.add_box(x0, y0 - 0.12, -3.6, x0 + width, y0, 1.0, "timber")
    for i in range(int(width / 1.6)):
        mb.add_box_c(x0 + 0.9 + i * 1.6, y0 + thickness / 2, 1.35, 0.55, thickness + 0.6, 0.45, "iron")
    mb.add_box(x0, y0 - 0.2, -4.2, x0 + width, y0 + thickness + 0.2, -3.7, "timber")
    return dict(deck=1.05, width=width)


# ================================================================ slipways
def slipway(mb, x0, y0, width, length, angle_deg=2.6, top_z=3.2, end_z=-6.0,
            rails=3, keel_block=True):
    """A building slip: inclined ways running into the water, with keel and bilge
    ways, timber shoring pack and side staging. Slips of this kind lined the
    Harland & Wolff frontage -- as many as fifteen vessels at once at Fairfield."""
    ang = math.radians(angle_deg)
    mb.add_box(x0, y0, end_z - 0.4, x0 + width, y0 + length, end_z + 0.1, "rubble")
    # inclined deck
    n = 10
    for i in range(n):
        t0, t1 = i / n, (i + 1) / n
        zz0 = end_z + (top_z - end_z) * t0
        zz1 = end_z + (top_z - end_z) * t1
        mb.add_quad((x0, y0 + length * t0, zz0), (x0 + width, y0 + length * t0, zz0),
                    (x0 + width, y0 + length * t1, zz1), (x0, y0 + length * t1, zz1),
                    "plank")
        mb.add_quad((x0 + width, y0 + length * t0, zz0), (x0, y0 + length * t0, zz0),
                    (x0, y0 + length * t1, zz1 - 0.55), (x0 + width, y0 + length * t1, zz1 - 0.55),
                    "rubble")
    # way rails (the greased slides the cradle runs on)
    for k in range(rails):
        bx = x0 + width * (0.5 + (k - (rails - 1) / 2) * 0.30)
        for i in range(n):
            t0, t1 = i / n, (i + 1) / n
            zz0 = end_z + (top_z - end_z) * t0 + 0.08
            zz1 = end_z + (top_z - end_z) * t1 + 0.08
            mb.add_quad((bx - 0.13, y0 + length * t0, zz0), (bx + 0.13, y0 + length * t0, zz0),
                        (bx + 0.13, y0 + length * t1, zz1), (bx - 0.13, y0 + length * t1, zz1),
                        "iron")
    # shoring props either side (as in the Umbria launching plate)
    import random
    rnd = random.Random(7)
    for k in range(int(length / 3.4)):
        yy = y0 + 3.0 + k * 3.4
        t = (yy - y0) / length
        zz = end_z + (top_z - end_z) * t
        for s in (-1, 1):
            px = x0 + width / 2 + s * (width * 0.34)
            mb.add_beam((px, yy, zz), (px + s * 1.1, yy, zz + rnd.uniform(4.5, 7.0)),
                        0.16, 0.16, "timber")
    # side staging platforms
    for s in (-1, 1):
        px = x0 + width / 2 + s * width * 0.52
        mb.add_box(px - 0.5, y0 + 4, top_z + 1.2, px + 0.5, y0 + length * 0.8, top_z + 1.35, "plank")
        for k in range(int(length / 5.0)):
            yy = y0 + 4 + k * 5.0
            if yy > y0 + length * 0.8:
                break
            mb.add_beam((px, yy, end_z + (top_z - end_z) * ((yy - y0) / length)),
                        (px, yy, top_z + 1.2), 0.13, 0.13, "timber")
    return dict(angle=angle_deg, top_z=top_z, end_z=end_z)

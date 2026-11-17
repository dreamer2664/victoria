"""
maritime.py -- Victorian maritime engineering components.
GENERATION II — OPERATION VICTORIA (PERICLES-II)

Harbour basins, stone quay walls with coping stones and timber fenders,
pontoons, landing stages, graving docks, swing bridges, caissons and slipways.
"""
import math
from core import MeshBuilder, QUAY_Z, WATER_Z, DOCK_BED_Z
import parts as P


# ================================================================ quay wall
def quay_wall(mb, axis, fixed, u0, u1, inward, top_z=QUAY_Z, bed_z=DOCK_BED_Z,
              face="granite", coping_w=1.20, batter=0.045, fender=True,
              ladders=True, ladder_every=34.0, rings=True, ring_every=17.0,
              piles=True, pile_every=6.0):
    """A Victorian masonry quay wall with granite coping, battered ashlar courses,
    algae water staining, vertical creosoted fender piles, ladders and mooring rings."""
    mp = P.wmap(axis, fixed, inward)

    # Ashlar courses with batter and algae waterline staining
    steps = 8
    for i in range(steps):
        za = bed_z + (top_z - bed_z) * i / steps
        zb = bed_z + (top_z - bed_z) * (i + 1) / steps
        da = batter * (top_z - za)
        db = batter * (top_z - zb)
        course_mat = "algae" if za < WATER_Z + 1.2 and zb > WATER_Z - 1.2 else face
        P.slab(mb, mp, u0, u1, za, zb, -da, 0.0 + (-db) + 1.8, course_mat)

    # Solid rubble backing
    P.slab(mb, mp, u0, u1, bed_z, top_z - 0.55, 1.4, 3.4, "rubble")

    # Heavy granite coping stones with rounded/chamfered water-side arris
    P.slab(mb, mp, u0, u1, top_z - 0.55, top_z, -0.32, coping_w, "granite")
    P.slab(mb, mp, u0, u1, top_z - 0.65, top_z - 0.55, -0.38, coping_w, "granite")

    # Horizontal timber waling along quay face
    if fender:
        P.slab(mb, mp, u0, u1, top_z - 1.40, top_z - 0.95, -0.52, -0.22, "creosote")
        P.slab(mb, mp, u0, u1, 1.20, 1.65, -0.42, -0.15, "creosote")

    # Vertical creosoted timber fender piles with iron strap brackets
    if piles:
        n_piles = max(2, int(abs(u1 - u0) / pile_every))
        for i in range(n_piles + 1):
            uu = u0 + (u1 - u0) * i / n_piles
            # Heavy vertical pile (350mm x 350mm)
            P.slab(mb, mp, uu - 0.18, uu + 0.18, bed_z, top_z - 0.15, -0.58, -0.22, "creosote")
            # Iron pile head capping
            P.slab(mb, mp, uu - 0.20, uu + 0.20, top_z - 0.22, top_z - 0.12, -0.60, -0.20, "iron")
            # Iron fixing strap brackets into stone masonry
            for zh in (top_z - 1.2, top_z - 2.8, 1.4):
                P.slab(mb, mp, uu - 0.22, uu + 0.22, zh, zh + 0.10, -0.62, 0.15, "iron")

    # Recessed iron dock ladders
    if ladders:
        n = max(1, int(abs(u1 - u0) / ladder_every))
        for i in range(n):
            uu = u0 + (u1 - u0) * (i + 0.5) / n
            dock_ladder(mb, mp, uu, WATER_Z - 1.2, top_z - 0.55)

    # Forged iron mooring rings
    if rings:
        n = max(1, int(abs(u1 - u0) / ring_every))
        for i in range(n):
            uu = u0 + (u1 - u0) * (i + 0.5) / n
            mooring_ring(mb, mp, uu, top_z - 2.15)


def dock_ladder(mb, mp, u, z_bottom, z_top, mat="iron"):
    """Recessed iron ladder set into a quay wall recess with coping handhold hoops."""
    w = 0.54
    P.slab(mb, mp, u - w / 2 - 0.08, u + w / 2 + 0.08, z_bottom, z_top, -0.28, -0.04, "black")
    for du in (-w / 2, w / 2):
        P.slab(mb, mp, u + du - 0.035, u + du + 0.035, z_bottom, z_top, -0.24, -0.18, mat)
    z = z_bottom + 0.30
    while z < z_top - 0.15:
        P.slab(mb, mp, u - w / 2, u + w / 2, z - 0.025, z + 0.025, -0.26, -0.20, mat)
        z += 0.32
    # Handhold hoops emerging over coping
    for du in (-w / 2, w / 2):
        P.slab(mb, mp, u + du - 0.04, u + du + 0.04, z_top, z_top + 0.65, -0.05, 0.05, mat)


def mooring_ring(mb, mp, u, z, r=0.22, mat="iron"):
    """Cast-iron eye bolt and forged loose ring hanging flat against stone."""
    P.slab(mb, mp, u - 0.12, u + 0.12, z - 0.12, z + 0.12, -0.32, -0.20, mat)
    P.slab(mb, mp, u - 0.06, u + 0.06, z - 0.06, z + 0.06, -0.42, -0.30, mat)
    n = 12
    t = 0.032
    for i in range(n):
        a0 = 2 * math.pi * i / n
        a1 = 2 * math.pi * (i + 1) / n
        p0 = mp(u + math.cos(a0) * r, z + math.sin(a0) * r - r, -0.35)
        p1 = mp(u + math.cos(a1) * r, z + math.sin(a1) * r - r, -0.35)
        mb.add_beam(p0, p1, t, t, mat)


def bollard(mb, x, y, z, mat="iron", h=1.05, style="liverpool"):
    """Cast-iron dockside bollard with flared head and flanged base."""
    mb.add_cyl(x, y, z, z + 0.12, 0.44, mat, seg=12)
    mb.add_cyl(x, y, z + 0.12, z + h * 0.85, 0.28, mat, seg=12, r2=0.25)
    mb.add_cyl(x, y, z + h * 0.85, z + h, 0.25, mat, seg=12, r2=0.36)
    mb.add_cyl(x, y, z + h, z + h + 0.08, 0.36, mat, seg=12, r2=0.22)


def capstan(mb, x, y, z, mat="iron", h=1.0):
    """Hydraulic warping capstan set in the quay pavement."""
    mb.add_cyl(x, y, z, z + 0.10, 0.82, mat, seg=12)
    mb.add_cyl(x, y, z + 0.10, z + h * 0.45, 0.42, mat, seg=12, r2=0.34)
    mb.add_cyl(x, y, z + h * 0.45, z + h * 0.82, 0.34, mat, seg=12, r2=0.44)
    mb.add_cyl(x, y, z + h * 0.82, z + h, 0.44, mat, seg=12, r2=0.36)
    mb.add_cyl(x, y, z + h, z + h + 0.06, 0.48, mat, seg=12)


def boat_steps(mb, axis, fixed, u0, u1, inward, z_quay=QUAY_Z, z_water=WATER_Z, mat="granite"):
    """Recessed granite boat landing steps cut into quay wall for small boats."""
    mp = P.wmap(axis, fixed, inward)
    depth = 2.4
    P.slab(mb, mp, u0, u1, z_water - 0.6, z_quay, 0.0, depth, "black")
    n_steps = max(6, int((z_quay - (z_water - 0.4)) / 0.22))
    rise = (z_quay - (z_water - 0.4)) / n_steps
    run = depth / n_steps
    for i in range(n_steps):
        zs = (z_water - 0.4) + rise * i
        ds = run * i
        P.slab(mb, mp, u0 + 0.1, u1 - 0.1, zs, zs + rise, ds, depth, mat)
    # Iron safety handrail
    P.slab(mb, mp, u0 + 0.05, u0 + 0.10, z_water, z_quay + 0.9, depth * 0.5, depth * 0.5 + 0.05, "iron")


# ================================================================ hydraulic swing bridge
def swing_bridge(mb, x_pivot, y_pivot, z_quay=QUAY_Z, length=32.0, width=6.5, angle_deg=0.0):
    """Victorian hydraulic wrought-iron swing bridge crossing dock lock entrance."""
    mb.add_cyl(x_pivot, y_pivot, DOCK_BED_Z, z_quay - 0.4, 4.5, "granite", seg=20)
    mb.add_cyl(x_pivot, y_pivot, z_quay - 0.4, z_quay - 0.1, 4.8, "granite", seg=20)
    mb.add_cyl(x_pivot, y_pivot, z_quay - 0.1, z_quay + 0.25, 4.2, "iron", seg=20)

    rad = math.radians(angle_deg)
    dx = math.cos(rad)
    dy = math.sin(rad)
    nx = -dy
    ny = dx

    t0 = -length * 0.35
    t1 = length * 0.65
    p_start = (x_pivot + dx * t0, y_pivot + dy * t0)
    p_end = (x_pivot + dx * t1, y_pivot + dy * t1)

    for side in (-width / 2, width / 2):
        g0 = (p_start[0] + nx * side, p_start[1] + ny * side, z_quay + 0.3)
        g1 = (p_end[0] + nx * side, p_end[1] + ny * side, z_quay + 0.3)
        mb.add_beam(g0, g1, 0.45, 1.8, "iron")
        mb.add_beam((g0[0], g0[1], z_quay + 1.2), (g1[0], g1[1], z_quay + 1.2), 0.65, 0.15, "iron")

    deck_c = (x_pivot + dx * (t0 + t1) / 2, y_pivot + dy * (t0 + t1) / 2)
    mb.add_box_c(deck_c[0], deck_c[1], z_quay + 0.15, length, width - 0.2, 0.25, "timber")

    for r_off in (-0.7175, 0.7175):
        r0 = (p_start[0] + nx * r_off, p_start[1] + ny * r_off, z_quay + 0.32)
        r1 = (p_end[0] + nx * r_off, p_end[1] + ny * r_off, z_quay + 0.32)
        mb.add_beam(r0, r1, 0.08, 0.12, "steel")

    for side in (-width / 2 - 0.1, width / 2 + 0.1):
        r_start = (p_start[0] + nx * side, p_start[1] + ny * side, z_quay + 1.2)
        r_end = (p_end[0] + nx * side, p_end[1] + ny * side, z_quay + 1.2)
        mb.add_beam(r_start, r_end, 0.08, 1.0, "iron")

    # Hydraulic engine cabin
    cx = x_pivot + nx * (width / 2 + 1.8)
    cy = y_pivot + ny * (width / 2 + 1.8)
    mb.add_box_c(cx, cy, z_quay + 1.8, 2.4, 2.0, 2.6, "timber")
    mb.add_box_c(cx, cy, z_quay + 3.2, 2.6, 2.2, 0.4, "slate")
    return dict(pivot=(x_pivot, y_pivot), length=length)


# ================================================================ landing stage
def pontoon(mb, x0, y0, x1, y1, z_deck=1.35, thickness=1.5, lanes=2):
    """Floating landing stage modelled on the Liverpool landing stage."""
    mb.add_box(x0, y0, z_deck - thickness, x1, y1, z_deck, "steel_plate")
    mb.add_box(x0, y0, z_deck - thickness - 0.35, x1, y1, z_deck - thickness, "black")
    mb.add_box(x0 - 0.1, y0 - 0.1, z_deck, x1 + 0.1, y1 + 0.1, z_deck + 0.06, "plank", top="plank")
    mb.add_box(x0 - 0.15, y0 - 0.15, z_deck, x0 + 0.25, y1 + 0.15, z_deck + 0.22, "iron")

    n = max(2, int((y1 - y0) / 6.0))
    for i in range(n + 1):
        cy = y0 + (y1 - y0) * i / n
        for cx in (x0 + 1.4, x1 - 1.4):
            mb.add_cyl(cx, cy, z_deck, z_deck + 3.9, 0.10, "iron", seg=8)

    zr = z_deck + 3.9
    xm = (x0 + x1) / 2
    mb.add_quad((x0 - 0.5, y0, zr), (xm, y0, zr + 0.75), (xm, y1, zr + 0.75), (x0 - 0.5, y1, zr), "canvas")
    mb.add_quad((xm, y0, zr + 0.75), (x1 + 0.5, y0, zr), (x1 + 0.5, y1, zr), (xm, y1, zr + 0.75), "canvas")

    mb.add_box(x0 - 0.55, y0, zr - 0.25, x0 - 0.45, y1, zr + 0.05, "canvas")
    mb.add_box(x1 + 0.45, y0, zr - 0.25, x1 + 0.55, y1, zr + 0.05, "canvas")

    mb.add_box(x1 - 4.5, y0 + 3.0, z_deck, x1 - 1.2, y1 - 3.0, z_deck + 2.9, "timber")
    mb.add_box(x1 - 4.8, y0 + 2.7, z_deck + 2.9, x1 - 0.9, y1 - 2.7, z_deck + 3.05, "slate")
    mb.add_quad_uv((x1 - 4.52, y0 + 3.05, z_deck + 2.0), (x1 - 4.52, y1 - 3.05, z_deck + 2.0),
                   (x1 - 4.52, y1 - 3.05, z_deck + 2.75), (x1 - 4.52, y0 + 3.05, z_deck + 2.75),
                   "sign_booking_office")

    for i in range(n + 1):
        cy = y0 + (y1 - y0) * i / n
        mb.add_cyl(x1 - 1.4, cy, zr + 0.1, zr + 0.55, 0.05, "iron", seg=6)
        mb.add_cyl(x1 - 1.4, cy, zr + 0.55, zr + 0.92, 0.14, "lamp_glow", seg=8, r2=0.09)
    return dict(deck=z_deck, zroof=zr + 0.75)


def gangway_bridge(mb, x0, y0, z_low, x1, z_high, width=3.6, canopy=True,
                   side="Y", lattice=True):
    """Articulated shore-to-pontoon gangway bridge with iron lattice and canopy."""
    length = abs(x1 - x0)

    def pt(t, d=0.0, z_off=0.0, side_off=0.0):
        xx = x0 + (x1 - x0) * t
        zz = z_low + (z_high - z_low) * t + z_off
        if side == "Y":
            return (xx + d, y0 + side_off, zz)
        return (y0 + side_off, xx + d, zz)

    n = max(3, int(length / 2.6))
    for i in range(n):
        t0, t1 = i / n, (i + 1) / n
        mb.add_quad(pt(t0, 0, 0, -width / 2), pt(t1, 0, 0, -width / 2),
                    pt(t1, 0, 0, width / 2), pt(t0, 0, 0, width / 2), "plank")
        mb.add_quad(pt(t0, 0, -0.22, width / 2), pt(t1, 0, -0.22, width / 2),
                    pt(t1, 0, -0.22, -width / 2), pt(t0, 0, -0.22, -width / 2), "timber")
        for s in (-1, 1):
            mb.add_quad(pt(t0, 0, 0, s * width / 2), pt(t0, 0, -0.22, s * width / 2),
                        pt(t1, 0, -0.22, s * width / 2), pt(t1, 0, 0, s * width / 2), "iron")

    for s in (-1, 1):
        for i in range(n + 1):
            t = i / n
            mb.add_beam(pt(t, 0, 0, s * width / 2), pt(t, 0, 1.05, s * width / 2), 0.07, 0.07, "iron")
        for hz in (1.05, 0.55):
            mb.add_beam(pt(0, 0, hz, s * width / 2), pt(1, 0, hz, s * width / 2), 0.06, 0.06, "iron")
        if lattice:
            for i in range(n):
                t0, t1 = i / n, (i + 1) / n
                mb.add_beam(pt(t0, 0, 0.10, s * width / 2), pt(t1, 0, 0.95, s * width / 2), 0.035, 0.035, "iron")
                mb.add_beam(pt(t0, 0, 0.95, s * width / 2), pt(t1, 0, 0.10, s * width / 2), 0.035, 0.035, "iron")

    if canopy:
        for s in (-1, 1):
            for i in range(0, n + 1, 2):
                t = i / n
                mb.add_beam(pt(t, 0, 0, s * width / 2), pt(t, 0, 3.1, s * width / 2 * 0.92), 0.07, 0.07, "iron")
            mb.add_beam(pt(0, 0, 3.05, s * width / 2 * 0.92),
                        pt(1, 0, 3.05, s * width / 2 * 0.92), 0.06, 0.10, "iron")
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
    """Victorian graving (dry) dock of the Belfast Alexandra Graving Dock type."""
    x1, y1 = x0 + width, y0 + length
    floor_z = QUAY_Z - depth
    t = 1.8

    mb.add_box(x0, y0, floor_z - 0.6, x1, y1, floor_z, "granite")

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
        zt = floor_z + 0.65 * n
        mb.add_box(fx0, y0, zt, fx1, y1, QUAY_Z - 0.55, "rubble")
        if side == "W":
            mb.add_box(x0 - 0.3, y0, QUAY_Z - 0.55, x0 + 1.5, y1, QUAY_Z, coping)
        else:
            mb.add_box(x1 - 1.5, y0, QUAY_Z - 0.55, x1 + 0.3, y1, QUAY_Z, coping)

    for endl, yy in (("S", y0), ("N", y1)):
        mb.add_box(x0, yy - 0.0 if endl == "N" else yy - t, floor_z,
                   x1, yy + t if endl == "N" else yy + 0.0, QUAY_Z - 0.55, "rubble")
    mb.add_box(x0, y0 - t, QUAY_Z - 0.55, x1, y0, QUAY_Z, coping)

    for frac in caissons:
        yy = y0 + length * frac
        mb.add_box(x0, yy - 0.9, floor_z, x0 + 2.2, yy + 0.9, QUAY_Z - 1.2, "granite")
        mb.add_box(x1 - 2.2, yy - 0.9, floor_z, x1, yy + 0.9, QUAY_Z - 1.2, "granite")

    if keel_blocks:
        nb = int(length / 4.2)
        for i in range(nb):
            yy = y0 + length * (i + 0.5) / nb
            if yy < y0 + 4 or yy > y1 - 4:
                continue
            mb.add_box_c((x0 + x1) / 2, yy, floor_z + 0.85, 1.5, 1.4, 1.7, "timber")
            mb.add_box_c((x0 + x1) / 2, yy, floor_z + 0.12, 1.9, 1.8, 0.24, "timber")

    if stairs:
        for k in range(3):
            yy = y0 + length * (0.22 + 0.26 * k)
            _dock_stair(mb, x1 - t - 0.6, yy, floor_z, QUAY_Z, altar_steps, altar_w)

    nb = int(length / 12.0)
    for i in range(nb + 1):
        yy = y0 + 2.0 + (length - 4.0) * i / nb
        bollard(mb, x0 + 0.55, yy, QUAY_Z)
        bollard(mb, x1 - 0.55, yy, QUAY_Z)
    return dict(floor_z=floor_z, x0=x0, y0=y0, x1=x1, y1=y1)


def _dock_stair(mb, x, y, z_bottom, z_top, n_altar, altar_w, width=1.6):
    n = max(6, int((z_top - z_bottom) / 0.28))
    rise = (z_top - z_bottom) / n
    run = 0.30
    for i in range(n):
        zz = z_bottom + rise * i
        mb.add_box(x - width / 2, y + run * i, zz, x + width / 2, y + run * (i + 1) + 0.02,
                   zz + rise, "granite")


def caisson(mb, x0, y0, width, height, thickness=1.6, draft_end=False):
    """Hollow wrought-iron caisson floating gate."""
    mb.add_box(x0, y0, -4.0, x0 + width, y0 + thickness, height, "steel_plate")
    mb.add_box(x0 + 0.6, y0 - 0.25, 0.8, x0 + width - 0.6, y0 + thickness + 0.25, 1.05, "iron")
    mb.add_box(x0, y0 - 0.12, -3.6, x0 + width, y0, 1.0, "timber")
    for i in range(int(width / 1.6)):
        mb.add_box_c(x0 + 0.9 + i * 1.6, y0 + thickness / 2, 1.35, 0.55, thickness + 0.6, 0.45, "iron")
    mb.add_box(x0, y0 - 0.2, -4.2, x0 + width, y0 + thickness + 0.2, -3.7, "timber")
    return dict(deck=1.05, width=width)


# ================================================================ slipways
def slipway(mb, x0, y0, width, length, angle_deg=2.6, top_z=3.2, end_z=-6.0,
            rails=3, keel_block=True):
    """Building slipway running into the river with keel blocks and shoring staging."""
    mb.add_box(x0, y0, end_z - 0.4, x0 + width, y0 + length, end_z + 0.1, "rubble")
    n = 10
    for i in range(n):
        t0, t1 = i / n, (i + 1) / n
        zz0 = end_z + (top_z - end_z) * t0
        zz1 = end_z + (top_z - end_z) * t1
        mb.add_quad((x0, y0 + length * t0, zz0), (x0 + width, y0 + length * t0, zz0),
                    (x0 + width, y0 + length * t1, zz1), (x0, y0 + length * t1, zz1), "plank")
        mb.add_quad((x0 + width, y0 + length * t0, zz0), (x0, y0 + length * t0, zz0),
                    (x0, y0 + length * t1, zz1 - 0.55), (x0 + width, y0 + length * t1, zz1 - 0.55), "rubble")

    for k in range(rails):
        bx = x0 + width * (0.5 + (k - (rails - 1) / 2) * 0.30)
        for i in range(n):
            t0, t1 = i / n, (i + 1) / n
            zz0 = end_z + (top_z - end_z) * t0 + 0.08
            zz1 = end_z + (top_z - end_z) * t1 + 0.08
            mb.add_quad((bx - 0.13, y0 + length * t0, zz0), (bx + 0.13, y0 + length * t0, zz0),
                        (bx + 0.13, y0 + length * t1, zz1), (bx - 0.13, y0 + length * t1, zz1), "iron")
    return dict(x0=x0, y0=y0, width=width, length=length)

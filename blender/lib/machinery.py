"""
machinery.py -- dockside plant, coal handling, railway and street furniture.

Period detail that separates a working 1889 dock from a decorated one: hydraulic
jigger cranes, coal staithes with wagon hoists, travelling portal cranes, hand
capstans, gas standards and the standard-gauge dock railway that threaded through
every British port (the Mersey Docks estate alone ran 104 miles of it).
"""
import math
import random
from core import MeshBuilder, QUAY_Z
import parts as P

GAUGE = 1.435          # standard gauge, metres
SLEEPER = 2.60         # sleeper length


# ================================================================ cranes
def hydraulic_crane(mb, x, y, z, reach=5.4, height=5.6, capacity_t=3,
                    colour="paint_green", hook_z=None):
    """A hydraulic jigger crane: fixed cast-iron column, curved plate jib, tie rod,
    pulley block and hook. The ubiquitous general-purpose dock crane of the 1880s."""
    mb.add_cyl(x, y, z, z + 0.30, 1.05, "granite", seg=12)
    mb.add_cyl(x, y, z + 0.30, z + 0.62, 0.78, "iron", seg=14)
    mb.add_cyl(x, y, z + 0.62, z + height, 0.50, colour, seg=14, r2=0.40)
    mb.add_cyl(x, y, z + height, z + height + 0.22, 0.55, "iron", seg=14)
    # curved jib: quadratic arc from the column head out to full reach
    n = 8
    prev = None
    for i in range(n + 1):
        t = i / n
        r = 0.55 + (reach - 0.55) * t
        zz = z + height - 0.9 * t * t - 0.35 * t
        p = (x + math.cos(math.radians(0)) * r, y + math.sin(math.radians(0)) * r, zz)
        if prev:
            mb.add_beam(prev, p, 0.34, 0.30, colour)
        prev = p
    tip = prev
    # jib plates: a second, thinner rib below to read as a fabrcated plate jib
    prev2 = None
    for i in range(n + 1):
        t = i / n
        r = 0.55 + (reach - 0.55) * t
        zz = z + height - 0.9 * t * t - 0.35 * t - 0.55
        p = (x + r, y, zz)
        if prev2:
            mb.add_beam(prev2, p, 0.30, 0.14, colour)
        prev2 = p
    # tie rod back to the column head
    mb.add_beam((x, y, z + height + 0.1), (tip[0], tip[1], tip[2] - 0.15), 0.10, 0.10, "iron")
    # hoist rope, block and hook
    hz = hook_z if hook_z is not None else z + 1.2
    mb.add_beam((tip[0], tip[1], tip[2] - 0.1), (tip[0], tip[1], hz + 0.55), 0.035, 0.035, "black")
    mb.add_box_c(tip[0], tip[1], hz + 0.32, 0.30, 0.22, 0.42, "iron")
    mb.add_beam((tip[0], tip[1], hz + 0.10), (tip[0], tip[1], hz - 0.18), 0.07, 0.07, "iron")
    mb.add_cyl(tip[0], tip[1], hz - 0.34, hz - 0.18, 0.11, "iron", seg=8, r2=0.13)
    # operator's hand wheel
    mb.add_cyl(x - 0.6, y, z + 1.4, z + 1.5, 0.26, "paint_red", seg=10)
    return dict(tip=tip, height=height, reach=reach)


def coal_hoist(mb, x, y, z, height=6.2, reach=4.6):
    """Hydraulic coal hoist: cage lifts a wagon to the tipping cradle, the coal runs
    down chutes into a collier or barge. Replaces the older manual 'coal drops'."""
    mb.add_box_c(x, y, z + 0.35, 3.0, 3.0, 0.7, "granite")
    for dx in (-1.2, 1.2):
        for dy in (-1.2, 1.2):
            mb.add_beam((x + dx, y + dy, z + 0.7), (x + dx, y + dy, z + height),
                        0.22, 0.22, "iron")
    for hz in (z + height, z + height * 0.55):
        for dy in (-1.2, 1.2):
            mb.add_beam((x - 1.2, y + dy, hz), (x + 1.2, y + dy, hz), 0.16, 0.20, "iron")
        for dx in (-1.2, 1.2):
            mb.add_beam((x + dx, y - 1.2, hz), (x + dx, y + 1.2, hz), 0.16, 0.20, "iron")
    # tipping cradle
    mb.add_box_c(x, y, z + 2.1, 2.7, 2.9, 0.35, "iron")
    mb.add_beam((x, y - 2.4, z + 2.1), (x, y - 0.9, z + 2.6), 0.30, 0.22, "iron")
    # chute out over the water
    mb.add_beam((x, y - 1.0, z + height * 0.72), (x, y - reach, z + height * 0.30),
                1.30, 0.55, "iron")
    mb.add_beam((x, y - reach + 0.8, z + height * 0.36), (x, y - reach, z + height * 0.30),
                1.10, 0.45, "iron")
    # machinery house
    mb.add_box_c(x + 2.4, y + 1.6, z + 1.5, 2.0, 2.2, 3.0, "brick_soot")
    mb.add_box_c(x + 2.4, y + 1.6, z + 3.05, 2.3, 2.5, 0.12, "slate")
    return dict(height=height)


def coal_staithe(mb, x0, y0, length, width, z=QUAY_Z, h=3.0, drops=6):
    """Raised timber/stone coal staithe with wagon drops and bunker pockets."""
    mb.add_box(x0, y0, z, x0 + width, y0 + length, z + h * 0.55, "rubble")
    mb.add_box(x0 - 0.2, y0, z + h * 0.55, x0 + width + 0.2, y0 + length, z + h * 0.72, "granite")
    # timber deck and side cheek walls
    mb.add_box(x0, y0, z + h * 0.72, x0 + width, y0 + length, z + h, "plank")
    for i in range(drops):
        yy = y0 + length * (i + 0.5) / drops
        # the drop: a chute mouth in the quay edge
        mb.add_box(x0 + width * 0.15, yy - 0.7, z + 0.35, x0 + width * 0.85, yy + 0.7, z + h * 0.72, "coal")
        mb.add_beam((x0 + width * 0.2, yy, z + h * 0.6), (x0 + width * 0.2, yy, z + 0.3), 0.9, 0.12, "iron")
    # rails along the staithe top for the wagons
    rail_track(mb, x0 + width * 0.5, y0, x0 + width * 0.5, y0 + length, z + h)


def titan_crane(mb, x, y, z, span=15.0, height=21.0, jib=16.0, side="X"):
    """A travelling portal (Titan) crane on rails: two legs, a lattice girder, a
    slewing cantilever jib and a counterweight box. The heavy lift of the era."""
    def leg(px, py):
        for dx in (-0.55, 0.55):
            for dy in (-0.55, 0.55):
                mb.add_beam((px + dx, py + dy, z), (px + dx, py + dy, z + height),
                            0.35, 0.35, "iron")
        for hz in (z + 0.4, z + height * 0.5, z + height):
            mb.add_beam((px - 0.55, py - 0.55, hz), (px + 0.55, py - 0.55, hz), 0.16, 0.16, "iron")
            mb.add_beam((px + 0.55, py - 0.55, hz), (px + 0.55, py + 0.55, hz), 0.16, 0.16, "iron")
            mb.add_beam((px + 0.55, py + 0.55, hz), (px - 0.55, py + 0.55, hz), 0.16, 0.16, "iron")
            mb.add_beam((px - 0.55, py + 0.55, hz), (px - 0.55, py - 0.55, hz), 0.16, 0.16, "iron")
        # bogie
        mb.add_box_c(px, py, z + 0.5, 1.9, 1.9, 0.9, "iron")
        for k in range(4):
            mb.add_cyl(px + (-0.6 + 0.4 * k), py, z + 0.15, z + 0.15, 0.32, "iron", seg=8, axis="X")
    if side == "X":
        leg(x - span / 2, y); leg(x + span / 2, y)
        p0 = (x - span / 2, y, z + height)
        p1 = (x + span / 2, y, z + height)
    else:
        leg(x, y - span / 2); leg(x, y + span / 2)
        p0 = (x, y - span / 2, z + height)
        p1 = (x, y + span / 2, z + height)
    # lattice girder
    for dz in (0.0, 1.1):
        mb.add_beam((p0[0], p0[1], p0[2] + dz), (p1[0], p1[1], p1[2] + dz), 0.55, 0.16, "iron")
    n = int(span / 1.6)
    for i in range(n):
        t0, t1 = i / n, (i + 1) / n
        a = (p0[0] + (p1[0] - p0[0]) * t0, p0[1] + (p1[1] - p0[1]) * t0, p0[2] + 0.1)
        b = (p0[0] + (p1[0] - p0[0]) * t1, p0[1] + (p1[1] - p0[1]) * t1, p0[2] + 1.0)
        mb.add_beam(a, b, 0.10, 0.10, "iron")
    # slewing jib on the girder
    jx = x
    mb.add_cyl(jx, y, z + height + 1.1, z + height + 2.0, 0.75, "iron", seg=10)
    jz = z + height + 1.8
    mb.add_beam((jx, y, jz), (jx + jib, y, jz + 1.6), 0.9, 0.3, "iron")
    mb.add_beam((jx, y, jz + 0.6), (jx + jib * 0.55, y, jz + 1.3), 0.14, 0.14, "iron")
    mb.add_beam((jx, y, jz), (jx - 4.5, y, jz), 1.2, 0.35, "iron")
    mb.add_box_c(jx - 5.0, y, jz - 0.4, 2.4, 1.8, 1.4, "iron")
    # cab
    mb.add_box_c(jx + 2.0, y + 1.1, jz + 0.3, 2.0, 1.7, 2.0, "paint_green")
    mb.add_box_c(jx + 2.0, y + 1.95, jz + 0.9, 1.5, 0.08, 1.0, "glass")
    # hook
    mb.add_beam((jx + jib, y, jz + 1.5), (jx + jib, y, z + 6.0), 0.05, 0.05, "black")
    mb.add_box_c(jx + jib, y, z + 5.6, 0.34, 0.26, 0.5, "iron")
    return dict(jib=jib, height=height)


def sheer_legs(mb, x, y, z, height=16.0, spread=5.0, reach=7.0):
    """Two timber sheer legs with a back stay -- the heavy-lift of small yards."""
    for s in (-1, 1):
        mb.add_beam((x + s * 0.5, y, z), (x + s * 1.1, y - spread, z + height),
                    0.55, 0.55, "timber")
    mb.add_beam((x + 1.1, y - spread, z + height), (x, y + reach, z + 1.2), 0.22, 0.22, "rope")
    mb.add_beam((x - 1.1, y - spread, z + height), (x, y + reach, z + 1.2), 0.22, 0.22, "rope")
    mb.add_beam((x, y, z + height * 0.62), (x, y + reach, z + 1.2), 0.18, 0.18, "rope")
    mb.add_box_c(x, y - spread + 1.2, z + 2.0, 3.6, 3.0, 0.4, "timber")


def steam_crane(mb, x, y, z, angle=0.0, jib=7.0):
    """Rail-mounted steam crane: vertical boiler, cab, sloped jib, on a 4-wheel chassis."""
    ca, sa = math.cos(angle), math.sin(angle)
    mb.add_box_c(x, y, z + 0.75, 6.2, 2.6, 0.6, "iron")
    for dx in (-2.4, 2.4):
        for dy in (-0.72, 0.72):
            mb.add_cyl(x + dx, y + dy * 1.0, z + 0.15, z + 0.55, 0.42, "iron", seg=10, axis="X")
    mb.add_box_c(x, y, z + 1.35, 4.2, 2.3, 0.6, "paint_green")
    # boiler
    bx, by = x - 1.2, y
    mb.add_cyl(bx, by, z + 1.6, z + 3.9, 0.62, "paint_green", seg=14)
    mb.add_cyl(bx, by, z + 3.9, z + 4.6, 0.16, "black", seg=10, r2=0.22)
    mb.add_cyl(bx, by, z + 2.9, z + 3.1, 0.68, "brass", seg=14)
    # cab
    mb.add_box_c(x + 1.5, y, z + 2.1, 2.2, 2.2, 2.6, "paint_green")
    mb.add_box_c(x + 1.5, y + 1.12, z + 2.6, 1.5, 0.06, 1.1, "glass")
    # jib
    tipx, tipy = x + ca * jib, y + sa * jib
    mb.add_beam((x + 0.4, y, z + 2.6), (tipx, tipy, z + 4.4), 0.5, 0.35, "paint_green")
    mb.add_beam((tipx, tipy, z + 4.4), (tipx, tipy, z + 1.4), 0.04, 0.04, "black")
    mb.add_box_c(tipx, tipy, z + 1.2, 0.26, 0.2, 0.36, "iron")


# ================================================================ railway
def rail_track(mb, x0, y0, x1, y1, z=QUAY_Z, gauge=GAUGE, sleeper_mat="timber",
               sleepers=True, ballast=True):
    """A length of standard-gauge permanent way."""
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy)
    if L < 0.1:
        return
    ux, uy = dx / L, dy / L
    px, py = -uy, ux
    if ballast:
        for i in range(int(L / 2.4) + 1):
            t0 = min(1.0, i * 2.4 / L)
            t1 = min(1.0, (i + 1) * 2.4 / L)
            a = (x0 + dx * t0, y0 + dy * t0); b = (x0 + dx * t1, y0 + dy * t1)
            mb.add_quad((a[0] + px * 1.6, a[1] + py * 1.6, z - 0.02),
                        (b[0] + px * 1.6, b[1] + py * 1.6, z - 0.02),
                        (b[0] - px * 1.6, b[1] - py * 1.6, z - 0.02),
                        (a[0] - px * 1.6, a[1] - py * 1.6, z - 0.02), "coal")
    if sleepers:
        n = max(2, int(L / 0.72))
        for i in range(n):
            t = (i + 0.5) / n
            cx, cy = x0 + dx * t, y0 + dy * t
            mb.add_beam((cx - px * SLEEPER / 2, cy - py * SLEEPER / 2, z + 0.03),
                        (cx + px * SLEEPER / 2, cy + py * SLEEPER / 2, z + 0.03),
                        0.24, 0.13, sleeper_mat)
    for s in (-1, 1):
        ox, oy = px * s * gauge / 2, py * s * gauge / 2
        mb.add_beam((x0 + ox, y0 + oy, z + 0.16), (x1 + ox, y1 + oy, z + 0.16),
                    0.075, 0.14, "iron")


def buffer_stop(mb, x, y, z, angle=0.0):
    mb.add_box_c(x, y, z + 0.55, 1.9, 1.0, 0.7, "paint_red")
    mb.add_beam((x - 0.7, y - 0.7, z), (x - 0.7, y, z + 0.9), 0.18, 0.18, "iron")
    mb.add_beam((x + 0.7, y - 0.7, z), (x + 0.7, y, z + 0.9), 0.18, 0.18, "iron")


def wagon(mb, x, y, z, angle=0.0, kind="mineral"):
    """A wooden-bodied 8-ton mineral wagon or a covered goods van."""
    ca, sa = math.cos(angle), math.sin(angle)

    def w(lx, ly, lz):
        return (x + lx * ca - ly * sa, y + lx * sa + ly * ca, z + lz)

    L, W = 5.2, 2.4
    if kind == "mineral":
        mb.add_box(w(-L / 2, -W / 2, 0.95)[0] - 0.0, 0, 0, 0, 0, 0, "timber") if False else None
        # body: articulated open box
        corners = [w(-L / 2, -W / 2, 0.95), w(L / 2, -W / 2, 0.95), w(L / 2, W / 2, 0.95),
                   w(-L / 2, W / 2, 0.95)]
        top = [w(-L / 2, -W / 2, 2.35), w(L / 2, -W / 2, 2.35), w(L / 2, W / 2, 2.35),
               w(-L / 2, W / 2, 2.35)]
        mb.add_quad(corners[0], corners[1], top[1], top[0], "timber")
        mb.add_quad(corners[1], corners[2], top[2], top[1], "timber")
        mb.add_quad(corners[2], corners[3], top[3], top[2], "timber")
        mb.add_quad(corners[3], corners[0], top[0], top[3], "timber")
        mb.add_quad(w(-L / 2 + 0.15, -W / 2 + 0.15, 1.9), w(L / 2 - 0.15, -W / 2 + 0.15, 1.9),
                    w(L / 2 - 0.15, W / 2 - 0.15, 1.9), w(-L / 2 + 0.15, W / 2 - 0.15, 1.9), "coal")
        # underframe
        mb.add_box_c(x, y, z + 0.85, L, W - 0.15, 0.18, "iron")
    else:
        mb.add_box_c(x, y, z + 1.65, L, W, 2.3, "timber")
        mb.add_box_c(x, y, z + 2.85, L + 0.1, W + 0.1, 0.14, "canvas")
        mb.add_box_c(x, y, z + 0.85, L, W - 0.15, 0.18, "iron")
    for dx in (-1.7, 1.7):
        for dy in (-W / 2 + 0.05, W / 2 - 0.05):
            p = w(dx, dy, 0.62)
            mb.add_cyl(p[0], p[1], z + 0.24, z + 1.0, 0.42, "iron", seg=10, axis="X")
            # wheel tyre
            mb.add_cyl(p[0], p[1], z + 0.26, z + 0.36, 0.44, "black", seg=10, axis="X")


def tank_loco(mb, x, y, z, angle=0.0):
    """A small 0-6-0 saddle-tank dock locomotive (the standard dock shunter)."""
    ca, sa = math.cos(angle), math.sin(angle)

    def w(lx, ly, lz):
        return (x + lx * ca - ly * sa, y + lx * sa + ly * ca, z + lz)

    L, W = 8.4, 2.6
    mb.add_box_c(x, y, z + 1.05, L, W, 0.5, "black")           # frames
    mb.add_cyl(x, y, z + 1.85, z + 2.75, 0.98, "paint_green", seg=16)   # boiler
    mb.add_cyl(x, y, z + 2.75, z + 2.95, 0.62, "black", seg=12)         # smokebox
    mb.add_cyl(x - 2.9, y, z + 2.6, z + 3.9, 0.30, "black", seg=12, r2=0.42)  # chimney
    mb.add_cyl(x + 1.1, y, z + 2.6, z + 3.05, 0.45, "brass", seg=12)    # dome
    mb.add_box_c(x, y, z + 2.95, L * 0.72, W * 0.92, 0.55, "paint_green")  # saddle tank
    mb.add_box_c(x + 3.1, y, z + 2.15, 2.0, W, 2.6, "paint_green")      # cab
    mb.add_box_c(x + 3.1, y, z + 3.5, 2.2, W + 0.1, 0.16, "black")
    for dx in (-2.6, 0.0, 2.6):
        for dy in (-W / 2, W / 2):
            p = w(dx, dy, 0.70)
            mb.add_cyl(p[0], p[1], z + 0.24, z + 1.16, 0.46, "iron", seg=12, axis="X")
    mb.add_box_c(x + 4.2, y, z + 1.1, 0.4, 1.2, 0.3, "iron")


# ================================================================ street
def gas_lamp(mb, x, y, z, h=4.2, mat="iron"):
    """A cast-iron gas standard with a four-pane lantern and ladder rest."""
    mb.add_cyl(x, y, z, z + 0.22, 0.32, "granite", seg=10)
    mb.add_cyl(x, y, z + 0.22, z + 0.62, 0.20, mat, seg=12, r2=0.15)
    mb.add_cyl(x, y, z + 0.62, z + h, 0.10, mat, seg=10, r2=0.075)
    # decorative collar
    mb.add_cyl(x, y, z + h - 0.55, z + h - 0.30, 0.15, mat, seg=10)
    # ladder rest arm
    mb.add_beam((x, y, z + h - 1.3), (x + 0.42, y, z + h - 1.28), 0.05, 0.05, mat)
    # lantern
    zb = z + h
    mb.add_cyl(x, y, zb, zb + 0.10, 0.26, mat, seg=6)
    for i in range(4):
        a = math.pi / 2 * i + math.pi / 4
        px, py = x + math.cos(a) * 0.22, y + math.sin(a) * 0.22
        mb.add_beam((px, py, zb + 0.08), (px, py, zb + 0.78), 0.035, 0.035, mat)
    mb.add_cyl(x, y, zb + 0.18, zb + 0.68, 0.18, "lamp_glow", seg=8)
    mb.add_cyl(x, y, zb + 0.78, zb + 0.96, 0.30, mat, seg=6, r2=0.06)
    mb.add_cyl(x, y, zb + 0.96, zb + 1.06, 0.05, mat, seg=6)


def telegraph_pole(mb, x, y, z, h=8.5, arms=2):
    mb.add_cyl(x, y, z, z + h, 0.16, "timber", seg=8, r2=0.11)
    for i in range(arms):
        zz = z + h - 0.6 - i * 0.95
        mb.add_beam((x - 1.1, y, zz), (x + 1.1, y, zz), 0.10, 0.10, "timber")
        for k in range(4):
            px = x - 0.95 + 0.63 * k
            mb.add_cyl(px, y, zz + 0.05, zz + 0.24, 0.055, "glass", seg=6)


def fingerpost(mb, x, y, z, h=3.4):
    mb.add_cyl(x, y, z, z + h, 0.075, "iron", seg=8)
    for i, (dz, ang) in enumerate(((0.35, 0.0), (0.05, math.pi * 0.5))):
        mb.add_beam((x, y, z + h - dz), (x + math.cos(ang) * 1.5, y + math.sin(ang) * 1.5,
                                        z + h - dz), 0.05, 0.32, "paint_white")
    mb.add_cyl(x, y, z + h, z + h + 1.1, 0.055, "iron", seg=8, r2=0.02)


def paving_area(mb, x0, y0, x1, y1, z, mat="setts", kerb=False, kerb_mat="granite"):
    """Carriageway/setts paving with an optional granite kerb along the +Y edge."""
    mb.add_quad((x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z), mat)
    if kerb:
        mb.add_box(x0, y1 - 0.05, z - 0.16, x1, y1 + 0.32, z + 0.10, kerb_mat)
        mb.add_quad((x0, y1 + 0.32, z + 0.10), (x1, y1 + 0.32, z + 0.10),
                    (x1, y1 + 0.32, z - 0.16), (x0, y1 + 0.32, z - 0.16), kerb_mat)


def drain_gully(mb, x, y, z, mat="iron"):
    mb.add_box_c(x, y, z - 0.02, 0.62, 0.45, 0.10, mat)
    for i in range(6):
        mb.add_beam((x - 0.28, y - 0.18 + i * 0.072, z + 0.05),
                    (x + 0.28, y - 0.18 + i * 0.072, z + 0.05), 0.03, 0.03, "black")


def weighbridge_house(mb, x, y, z, w=3.4, d=2.8, h=3.2):
    mb.add_box(x, y, z, x + w, y + d, z + h, "brick_buff")
    mb.add_gable_roof(x, y, x + w, y + d, z + h, 34, "slate", gable="Y", overhang=0.25)
    P.wmap("X", y, 1)
    mp = P.wmap("X", y, 1)
    P.sash_window(mb, mp, x + 1.0, x + 2.4, z + 1.1, z + 2.5, 0.35, panes_x=2, panes_y=2)


def gangway(mb, x, y, z_low, z_high, length, width=1.6, side="X", netting=True):
    """A ship's brow: an inclined timber gangway with rope handlines and side netting
    -- the working counterpart to the passenger bridges on the landing stage."""
    sgn = 1 if z_high > z_low else -1
    n = 8
    for i in range(n):
        t0, t1 = i / n, (i + 1) / n
        z0 = z_low + (z_high - z_low) * t0
        z1 = z_low + (z_high - z_low) * t1
        if side == "X":
            a = (x + length * t0, y - width / 2, z0); b = (x + length * t0, y + width / 2, z0)
            c = (x + length * t1, y + width / 2, z1); d = (x + length * t1, y - width / 2, z1)
        else:
            a = (x - width / 2, y + length * t0, z0); b = (x + width / 2, y + length * t0, z0)
            c = (x + width / 2, y + length * t1, z1); d = (x - width / 2, y + length * t1, z1)
        mb.add_quad(a, b, c, d, "plank")
        mb.add_quad(d, c, b, a, "timber")
    # rope handlines
    for s in (-1, 1):
        if side == "X":
            p0 = (x, y + s * width / 2, z_low + 0.95); p1 = (x + length, y + s * width / 2, z_high + 0.95)
        else:
            p0 = (x + s * width / 2, y, z_low + 0.95); p1 = (x + s * width / 2, y + length, z_high + 0.95)
        mb.add_beam(p0, p1, 0.045, 0.045, "rope")
        for k in range(5):
            t = k / 4
            if side == "X":
                base = (x + length * t, y + s * width / 2, z_low + (z_high - z_low) * t)
            else:
                base = (x + s * width / 2, y + length * t, z_low + (z_high - z_low) * t)
            mb.add_beam(base, (base[0], base[1], base[2] + 0.95), 0.035, 0.035, "iron")
    if netting:
        for k in range(int(length / 0.6)):
            t = k * 0.6 / length
            if side == "X":
                base = (x + length * t, y - width / 2, z_low + (z_high - z_low) * t)
                mb.add_beam(base, (base[0], base[1], base[2] - 0.55), 0.02, 0.02, "rope")


def winch(mb, x, y, z, mat="iron"):
    """A small hand/steam dockside winch for warping and hauling."""
    mb.add_box_c(x, y, z + 0.22, 1.5, 0.9, 0.44, mat)
    mb.add_cyl(x, y, z + 0.42, z + 0.52, 0.34, mat, seg=12, axis="Y")     # rope drum
    mb.add_cyl(x, y, z + 0.52, z + 0.62, 0.26, mat, seg=12, axis="Y")
    mb.add_beam((x + 0.6, y, z + 0.5), (x + 1.05, y, z + 0.95), 0.06, 0.06, mat)
    mb.add_cyl(x + 1.05, y, z + 0.95, z + 1.0, 0.16, mat, seg=8, axis="Y")


def crate(mb, x, y, z, s=0.9, r=0.0, mat="timber"):
    import math as _m
    c, sn = _m.cos(r), _m.sin(r)
    pts = [(-s / 2, -s / 2), (s / 2, -s / 2), (s / 2, s / 2), (-s / 2, s / 2)]
    lo = [(x + px * c - py * sn, y + px * sn + py * c, z) for px, py in pts]
    hi = [(x + px * c - py * sn, y + px * sn + py * c, z + s) for px, py in pts]
    for i in range(4):
        j = (i + 1) % 4
        mb.add_quad(lo[i], lo[j], hi[j], hi[i], mat)
    mb.add_quad(hi[0], hi[1], hi[2], hi[3], mat)
    mb.add_quad(lo[3], lo[2], lo[1], lo[0], mat)


def barrel(mb, x, y, z, h=0.95, r=0.30, mat="timber"):
    mb.add_cyl(x, y, z, z + h * 0.18, r * 0.86, mat, seg=12)
    mb.add_cyl(x, y, z + h * 0.18, z + h * 0.82, r, mat, seg=12)
    mb.add_cyl(x, y, z + h * 0.82, z + h, r * 0.86, mat, seg=12)
    for k in (0.20, 0.80):
        mb.add_cyl(x, y, z + h * k, z + h * k + 0.05, r * 1.02, "iron", seg=12)


def bale(mb, x, y, z, w=1.2, d=0.8, h=0.7, r=0.0, mat="canvas"):
    import math as _m
    c, sn = _m.cos(r), _m.sin(r)
    pts = [(-w / 2, -d / 2), (w / 2, -d / 2), (w / 2, d / 2), (-w / 2, d / 2)]
    lo = [(x + px * c - py * sn, y + px * sn + py * c, z) for px, py in pts]
    hi = [(x + px * c - py * sn, y + px * sn + py * c, z + h) for px, py in pts]
    for i in range(4):
        j = (i + 1) % 4
        mb.add_quad(lo[i], lo[j], hi[j], hi[i], mat)
    mb.add_quad(hi[0], hi[1], hi[2], hi[3], mat)
    # hoop straps
    for k in (0.28, 0.72):
        mb.add_box_c(x, y, z + h * k, w + 0.03, d + 0.03, 0.05, "iron")


def cargo_stack(mb, x, y, z, seed=1, spread=7.0):
    """A working stack of crates, barrels and bales in a cargo shed or on a quay."""
    rnd = random.Random(seed)
    for i in range(rnd.randint(5, 9)):
        px = x + rnd.uniform(-spread / 2, spread / 2)
        py = y + rnd.uniform(-spread / 2, spread / 2)
        k = rnd.random()
        r = rnd.uniform(0, 3.14)
        if k < 0.45:
            layers = rnd.randint(1, 3)
            s = rnd.choice([0.8, 0.9, 1.05])
            for L in range(layers):
                crate(mb, px, py, z + L * s, s=s, r=r, mat="timber")
        elif k < 0.75:
            for L in range(rnd.randint(1, 2)):
                barrel(mb, px + L * 0.1, py, z + L * 0.95, r=0.30, mat="timber")
        else:
            bale(mb, px, py, z, r=r, mat="canvas")


def coal_barge(mb, x, y, z, length=0.0, axis="Y"):
    """An open hopper barge of the type warped alongside to coal a liner
    (Ocean Steamships, 1891: eight barges of 250-300 tons coaled a big
    greyhound in about four and a half days)."""
    L, W = 22.0, 4.6
    if axis == "Y":
        mb.add_box(x - W / 2, y, z - 0.9, x + W / 2, y + L, z + 0.55, "steel_plate")
        mb.add_box(x - W / 2 + 0.25, y + 0.4, z + 0.55, x + W / 2 - 0.25, y + L - 0.4, z + 1.1, "coal")
        mb.add_box(x - W / 2 - 0.1, y + L - 2.2, z + 0.55, x + W / 2 + 0.1, y + L, z + 1.35, "timber")
    else:
        mb.add_box(x, y - W / 2, z - 0.9, x + L, y + W / 2, z + 0.55, "steel_plate")
        mb.add_box(x + 0.4, y - W / 2 + 0.25, z + 0.55, x + L - 0.4, y + W / 2 - 0.25, z + 1.1, "coal")


def plate_stack(mb, x, y, z, seed=1):
    """Stacks of steel plate in a shipyard plate yard."""
    rnd = random.Random(seed)
    for s in range(rnd.randint(2, 4)):
        px = x + rnd.uniform(-4, 4)
        py = y + rnd.uniform(-3, 3)
        h = rnd.uniform(0.5, 1.4)
        r = rnd.uniform(-0.15, 0.15)
        crate(mb, px, py, z, s=1.0, r=r, mat="steel_plate")
        mb.add_box(px - 2.6, py - 1.1, z, px + 2.6, py + 1.1, z + h, "steel_plate")
        # packers between plates
        for k in range(int(h / 0.28)):
            mb.add_box(px - 2.2, py - 1.3, z + 0.28 * k, px + 2.2, py + 1.3,
                       z + 0.28 * k + 0.05, "timber")


def keel_blocks(mb, x, y0, y1, z, spacing=4.2):
    """A line of keel blocks along a slip or dock floor."""
    n = max(1, int((y1 - y0) / spacing))
    for i in range(n):
        yy = y0 + (y1 - y0) * (i + 0.5) / n
        mb.add_box_c(x, yy, z + 0.85, 1.5, 1.4, 1.7, "timber")
        mb.add_box_c(x, yy, z + 0.12, 1.9, 1.8, 0.24, "timber")

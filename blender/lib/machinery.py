"""
machinery.py -- dockside plant, coal handling, railway and street furniture.
GENERATION II — OPERATION VICTORIA (PERICLES-II)

Period-authentic 1889 British dockside equipment:
  * Armstrong hydraulic portal cranes straddling quayside railway lines
  * Day, Summers & Co. 80-ton tubular masting sheer legs (Carrickmore Berth 1)
  * Hydraulic jigger cranes and coal hoists
  * Standard-gauge dock railway permanent way, buffer stops, mineral wagons and saddle-tank locos
  * Dray carts, gas lamps, telegraph poles and period cargo dressing
"""
import math
import random
from core import MeshBuilder, QUAY_Z
import parts as P

GAUGE = 1.435          # standard gauge, metres
SLEEPER = 2.60         # sleeper length


# ================================================================ hydraulic portal cranes
def armstrong_portal_crane(mb, x, y, z=QUAY_Z, reach=9.5, hook_z=None, jib_angle=48.0):
    """William Armstrong & Co. hydraulic portal crane.

    Straddles the quayside railway track on a 4-legged arched wrought-iron portal,
    allowing mineral wagons and locomotives to pass underneath unimpeded.
    Revolving superstructure with hydraulic jigger hoisting cylinder and lattice jib.
    """
    span = 4.2      # portal track gauge
    leg_h = 4.8     # portal clearance height

    # 4 legs and flanged track wheels
    for dx in (-1.8, 1.8):
        for dy in (-span / 2, span / 2):
            px, py = x + dx, y + dy
            # Wheel bogie box on rail
            mb.add_box_c(px, py, z + 0.35, 1.1, 0.45, 0.45, "iron")
            mb.add_cyl(px - 0.32, py, z + 0.15, z + 0.15, 0.28, "steel", seg=12, axis="X")
            mb.add_cyl(px + 0.32, py, z + 0.15, z + 0.15, 0.28, "steel", seg=12, axis="X")
            # Tapering box-girder leg rising to portal deck
            mb.add_beam((px, py, z + 0.55), (x + dx * 0.72, y + dy * 0.72, z + leg_h), 0.32, 0.32, "iron")

    # Portal deck and arched clearance girders
    mb.add_box_c(x, y, z + leg_h + 0.25, 4.4, span + 0.4, 0.5, "iron")
    # Arched portal clearance ribs underneath
    for dx in (-1.4, 1.4):
        mb.add_beam((x + dx, y - span / 2 * 0.7, z + leg_h), (x + dx, y + span / 2 * 0.7, z + leg_h),
                    0.25, 0.35, "iron")

    # Circular roller path and turntable
    tz = z + leg_h + 0.5
    mb.add_cyl(x, y, tz, tz + 0.25, 1.6, "iron", seg=16)

    # Crane revolving deck and machinery house
    dz = tz + 0.25
    mb.add_box_c(x, y, dz + 0.3, 4.2, 2.6, 0.55, "paint_green")
    # Rear counterweight ballast box
    mb.add_box_c(x - 1.5, y, dz + 1.1, 1.4, 2.2, 1.2, "iron")
    # Glazed operator's cabin with control levers
    mb.add_box_c(x + 0.6, y + 0.65, dz + 1.2, 1.8, 1.1, 1.8, "timber")
    mb.add_box_c(x + 0.6, y + 1.22, dz + 1.4, 1.4, 0.08, 0.9, "glass")

    # Hydraulic jigger cylinder (inclined along back stay)
    mb.add_cyl(x - 0.8, y, dz + 0.6, dz + 2.8, 0.32, "iron", seg=10)

    # Curved lattice jib
    jib_rad = math.radians(jib_angle)
    jib_len = 11.2
    tip_x = x + math.cos(jib_rad) * jib_len
    tip_z = dz + math.sin(jib_rad) * jib_len
    # Twin lattice chords
    for dy in (-0.55, 0.55):
        mb.add_beam((x + 1.1, y + dy, dz + 0.6), (tip_x, y + dy * 0.25, tip_z), 0.22, 0.22, "paint_green")
        # Internal cross lacing
        n_lace = 6
        for i in range(n_lace):
            t0, t1 = i / n_lace, (i + 1) / n_lace
            p0 = (x + 1.1 + (tip_x - (x + 1.1)) * t0, y + dy * (1.0 - 0.75 * t0), dz + 0.6 + (tip_z - (dz + 0.6)) * t0)
            p1 = (x + 1.1 + (tip_x - (x + 1.1)) * t1, y + dy * (1.0 - 0.75 * t1), dz + 0.6 + (tip_z - (dz + 0.6)) * t1)
            mb.add_beam(p0, p1, 0.06, 0.06, "iron")

    # Jib head pulley wheel
    mb.add_cyl(tip_x, y, tip_z - 0.1, tip_z + 0.1, 0.38, "iron", seg=12, axis="Y")

    # Hoisting chain and forged cargo hook
    hz = hook_z if hook_z is not None else z + 1.8
    mb.add_beam((tip_x, y, tip_z), (tip_x, y, hz + 0.6), 0.035, 0.035, "black")
    mb.add_box_c(tip_x, y, hz + 0.45, 0.32, 0.26, 0.35, "iron")
    mb.add_cyl(tip_x, y, hz + 0.12, hz + 0.30, 0.14, "steel", seg=10)
    return dict(tip=(tip_x, y, tip_z), reach=reach)


def day_summers_sheer_legs(mb, x, y, z=QUAY_Z, height=28.0, spread=12.0, overhang=9.0):
    """Day, Summers & Co. 80-ton tubular masting sheer legs (c. 1889).

    Standard British heavy-lift equipment for fitting marine boilers, triple-expansion
    engines and lower masts into ocean steamships.
    Two hollow raked tubular wrought-iron front legs pinned at the quay edge,
    with a massive steam-driven screw back-stay leg running to a ground bed.
    """
    # Quay edge pivot pins for front legs
    p_left = (x - spread / 2, y, z + 0.6)
    p_right = (x + spread / 2, y, z + 0.6)
    for px in (p_left, p_right):
        mb.add_box_c(px[0], px[1], z + 0.3, 1.8, 1.8, 0.6, "granite")
        mb.add_cyl(px[0], px[1], z + 0.5, z + 0.8, 0.55, "iron", seg=12, axis="X")

    # Apex pin over water
    p_apex = (x, y + overhang, z + height)

    # Front tubular iron legs (diameter 1.1m tapering to 0.75m)
    mb.add_beam(p_left, p_apex, 1.05, 1.05, "paint_green")
    mb.add_beam(p_right, p_apex, 1.05, 1.05, "paint_green")
    # Cross tie and diagonal brace between front legs
    p_mid_l = (p_left[0] + (p_apex[0] - p_left[0]) * 0.45, p_left[1] + (p_apex[1] - p_left[1]) * 0.45, z + height * 0.45)
    p_mid_r = (p_right[0] + (p_apex[0] - p_right[0]) * 0.45, p_right[1] + (p_apex[1] - p_right[1]) * 0.45, z + height * 0.45)
    mb.add_beam(p_mid_l, p_mid_r, 0.45, 0.45, "paint_green")

    # Back-stay leg running back to steam screw bed
    p_bed = (x, y - 22.0, z + 0.8)
    mb.add_beam(p_apex, p_bed, 1.15, 1.15, "paint_green")

    # Horizontal steam screw engine trough on quay
    mb.add_box_c(x, y - 18.0, z + 0.45, 3.2, 14.0, 0.9, "granite")
    mb.add_box_c(x, y - 18.0, z + 0.95, 2.2, 12.0, 0.35, "iron")
    # Massive forged steel worm screw shaft
    mb.add_cyl(x, y - 18.0, z + 1.1, z + 1.1, 0.32, "steel", seg=12, axis="Y")

    # Winding steam engine house
    mb.add_box_c(x + 5.2, y - 18.0, z + 2.2, 4.5, 5.5, 4.4, "brick_red")
    mb.add_gable_roof(x + 5.2 - 2.25, y - 18.0 - 2.75, x + 5.2 + 2.25, y - 18.0 + 2.75,
                      z + 4.4, 32, "slate", gable="Y", end_mat="brick_red")
    # Steam boiler iron chimney
    mb.add_cyl(x + 6.4, y - 16.5, z + 4.4, z + 12.5, 0.42, "iron", seg=10)

    # 8-part pulley blocks and 80-ton forged hook hanging over water
    mb.add_box_c(p_apex[0], p_apex[1], p_apex[2] - 1.2, 1.4, 1.2, 1.6, "iron")
    # Heavy multi-part steel wire falls
    hook_z = z + 3.2
    for fo in (-0.35, 0.0, 0.35):
        mb.add_beam((p_apex[0] + fo, p_apex[1], p_apex[2] - 1.8),
                    (p_apex[0] + fo, p_apex[1], hook_z + 1.4), 0.045, 0.045, "black")
    # Lower travelling block and forged steel ramshorn hook
    mb.add_box_c(p_apex[0], p_apex[1], hook_z + 1.1, 1.2, 1.0, 1.4, "iron")
    mb.add_cyl(p_apex[0], p_apex[1], hook_z + 0.2, hook_z + 0.5, 0.28, "steel", seg=10)
    mb.add_torus(p_apex[0], p_apex[1], hook_z - 0.2, 0.42, 0.12, "steel") if hasattr(mb, "add_torus") else \
        mb.add_cyl(p_apex[0], p_apex[1], hook_z - 0.4, hook_z + 0.2, 0.45, "steel", seg=12)
    return dict(apex=p_apex, capacity_t=80)


def titan_crane(mb, x, y, z, span=15.0, height=21.0, jib=16.0, side="X"):
    """Compatibility bridge: delegates to Day, Summers sheer legs for authentic 1889 heavy lift."""
    return day_summers_sheer_legs(mb, x, y, z, height=28.0, spread=12.0, overhang=9.0)


def hydraulic_crane(mb, x, y, z, reach=5.4, height=5.6, capacity_t=3,
                    colour="paint_green", hook_z=None):
    """Hydraulic jigger crane with curved plate jib."""
    mb.add_cyl(x, y, z, z + 0.30, 1.05, "granite", seg=12)
    mb.add_cyl(x, y, z + 0.30, z + 0.62, 0.78, "iron", seg=14)
    mb.add_cyl(x, y, z + 0.62, z + height, 0.50, colour, seg=14, r2=0.40)
    mb.add_cyl(x, y, z + height, z + height + 0.22, 0.55, "iron", seg=14)
    n = 8
    prev = None
    for i in range(n + 1):
        t = i / n
        r = 0.55 + (reach - 0.55) * t
        zz = z + height - 0.9 * t * t - 0.35 * t
        p = (x + r, y, zz)
        if prev:
            mb.add_beam(prev, p, 0.34, 0.30, colour)
        prev = p
    tip = prev
    mb.add_beam((x, y, z + height + 0.1), (tip[0], tip[1], tip[2] - 0.15), 0.10, 0.10, "iron")
    hz = hook_z if hook_z is not None else z + 1.2
    mb.add_beam((tip[0], tip[1], tip[2] - 0.1), (tip[0], tip[1], hz + 0.55), 0.035, 0.035, "black")
    mb.add_box_c(tip[0], tip[1], hz + 0.32, 0.30, 0.22, 0.42, "iron")
    mb.add_beam((tip[0], tip[1], hz + 0.10), (tip[0], tip[1], hz - 0.18), 0.07, 0.07, "iron")
    mb.add_cyl(tip[0], tip[1], hz - 0.34, hz - 0.18, 0.11, "iron", seg=8, r2=0.13)
    mb.add_cyl(x - 0.6, y, z + 1.4, z + 1.5, 0.26, "paint_red", seg=10)
    return dict(tip=tip, height=height, reach=reach)


def coal_hoist(mb, x, y, z, height=6.2, reach=4.6):
    """Hydraulic coal hoist: lifts a wagon to the tipping cradle."""
    mb.add_box_c(x, y, z + 0.35, 3.0, 3.0, 0.7, "granite")
    for dx in (-1.2, 1.2):
        for dy in (-1.2, 1.2):
            mb.add_beam((x + dx, y + dy, z + 0.7), (x + dx, y + dy, z + height), 0.22, 0.22, "iron")
    for hz in (z + height, z + height * 0.55):
        for dy in (-1.2, 1.2):
            mb.add_beam((x - 1.2, y + dy, hz), (x + 1.2, y + dy, hz), 0.16, 0.20, "iron")
        for dx in (-1.2, 1.2):
            mb.add_beam((x + dx, y - 1.2, hz), (x + dx, y + 1.2, hz), 0.16, 0.20, "iron")
    mb.add_box_c(x, y, z + 2.1, 2.7, 2.9, 0.35, "iron")
    mb.add_beam((x, y - 2.4, z + 2.1), (x, y - 0.9, z + 2.6), 0.30, 0.22, "iron")
    mb.add_beam((x, y - 1.0, z + height * 0.72), (x, y - reach, z + height * 0.30), 1.30, 0.55, "iron")
    mb.add_beam((x, y - reach + 0.8, z + height * 0.36), (x, y - reach, z + height * 0.30), 1.10, 0.45, "iron")
    mb.add_box_c(x + 2.4, y + 1.6, z + 1.5, 2.0, 2.2, 3.0, "brick_soot")
    mb.add_box_c(x + 2.4, y + 1.6, z + 3.05, 2.3, 2.5, 0.12, "slate")
    return dict(height=height)


def coal_staithe(mb, x0, y0, length, width, z=QUAY_Z, h=3.0, drops=6):
    """Raised timber/stone coal staithe with wagon drops and bunker pockets."""
    mb.add_box(x0, y0, z, x0 + width, y0 + length, z + h * 0.55, "rubble")
    mb.add_box(x0 - 0.2, y0, z + h * 0.55, x0 + width + 0.2, y0 + length, z + h * 0.72, "granite")
    mb.add_box(x0, y0, z + h * 0.72, x0 + width, y0 + length, z + h, "plank")
    for i in range(drops):
        yy = y0 + length * (i + 0.5) / drops
        mb.add_box(x0 + width * 0.15, yy - 0.7, z + 0.35, x0 + width * 0.85, yy + 0.7, z + h * 0.72, "coal")
        mb.add_beam((x0 + width * 0.2, yy, z + h * 0.6), (x0 + width * 0.2, yy, z + 0.3), 0.9, 0.12, "iron")
    rail_track(mb, x0 + width * 0.5, y0, x0 + width * 0.5, y0 + length, z + h)


def steam_crane(mb, x, y, z, angle=0.0, jib=7.0):
    """Rail-mounted steam crane with vertical cross-tube boiler and curved jib."""
    ca, sa = math.cos(angle), math.sin(angle)
    mb.add_box_c(x, y, z + 0.75, 6.2, 2.6, 0.6, "iron")
    for dx in (-2.4, 2.4):
        for dy in (-0.72, 0.72):
            mb.add_cyl(x + dx, y + dy * 1.0, z + 0.15, z + 0.55, 0.42, "iron", seg=10, axis="X")
    mb.add_box_c(x, y, z + 1.35, 4.2, 2.3, 0.6, "paint_green")
    bx, by = x - 1.2, y
    mb.add_cyl(bx, by, z + 1.6, z + 3.9, 0.62, "paint_green", seg=14)
    mb.add_cyl(bx, by, z + 3.9, z + 4.6, 0.16, "black", seg=10, r2=0.22)
    mb.add_cyl(bx, by, z + 2.9, z + 3.1, 0.68, "brass", seg=14)
    mb.add_box_c(x + 1.5, y, z + 2.1, 2.2, 2.2, 2.6, "paint_green")
    mb.add_box_c(x + 1.5, y + 1.12, z + 2.6, 1.5, 0.06, 1.1, "glass")
    tipx, tipy = x + ca * jib, y + sa * jib
    mb.add_beam((x + 0.4, y, z + 2.6), (tipx, tipy, z + 4.4), 0.5, 0.35, "paint_green")
    mb.add_beam((tipx, tipy, z + 4.4), (tipx, tipy, z + 1.4), 0.04, 0.04, "black")
    mb.add_box_c(tipx, tipy, z + 1.2, 0.26, 0.2, 0.36, "iron")


# ================================================================ railway
def rail_track(mb, x0, y0, x1, y1, z=QUAY_Z, gauge=GAUGE, sleeper_mat="timber",
               sleepers=True, ballast=True):
    """Standard-gauge dock permanent way."""
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
                    0.075, 0.14, "steel")


def buffer_stop(mb, x, y, z, angle=0.0):
    mb.add_box_c(x, y, z + 0.55, 1.9, 1.0, 0.7, "paint_red")
    mb.add_beam((x - 0.7, y - 0.7, z), (x - 0.7, y, z + 0.9), 0.18, 0.18, "iron")
    mb.add_beam((x + 0.7, y - 0.7, z), (x + 0.7, y, z + 0.9), 0.18, 0.18, "iron")


def wagon(mb, x, y, z, angle=0.0, kind="mineral"):
    """Wooden-bodied 8-ton mineral wagon or covered goods van."""
    ca, sa = math.cos(angle), math.sin(angle)

    def w(lx, ly, lz):
        return (x + lx * ca - ly * sa, y + lx * sa + ly * ca, z + lz)

    L, W = 5.2, 2.4
    if kind == "mineral":
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
        mb.add_box_c(x, y, z + 0.85, L, W - 0.15, 0.18, "iron")
    else:
        mb.add_box_c(x, y, z + 1.65, L, W, 2.3, "timber")
        mb.add_box_c(x, y, z + 2.85, L + 0.1, W + 0.1, 0.14, "canvas")
        mb.add_box_c(x, y, z + 0.85, L, W - 0.15, 0.18, "iron")
    for dx in (-1.7, 1.7):
        for dy in (-W / 2 + 0.05, W / 2 - 0.05):
            p = w(dx, dy, 0.62)
            mb.add_cyl(p[0], p[1], z + 0.24, z + 1.0, 0.42, "iron", seg=10, axis="X")
            mb.add_cyl(p[0], p[1], z + 0.26, z + 0.36, 0.44, "black", seg=10, axis="X")


def tank_loco(mb, x, y, z, angle=0.0):
    """Small 0-6-0 saddle-tank dock locomotive shunter."""
    ca, sa = math.cos(angle), math.sin(angle)

    def w(lx, ly, lz):
        return (x + lx * ca - ly * sa, y + lx * sa + ly * ca, z + lz)

    L, W = 8.4, 2.6
    mb.add_box_c(x, y, z + 1.05, L, W, 0.5, "black")
    mb.add_cyl(x, y, z + 1.85, z + 2.75, 0.98, "paint_green", seg=16)
    mb.add_cyl(x, y, z + 2.75, z + 2.95, 0.62, "black", seg=12)
    mb.add_cyl(x - 2.9, y, z + 2.6, z + 3.9, 0.30, "black", seg=12, r2=0.42)
    mb.add_cyl(x + 1.1, y, z + 2.6, z + 3.05, 0.45, "brass", seg=12)
    mb.add_box_c(x, y, z + 2.95, L * 0.72, W * 0.92, 0.55, "paint_green")
    mb.add_box_c(x + 3.1, y, z + 2.15, 2.0, W, 2.6, "paint_green")
    mb.add_box_c(x + 3.1, y, z + 3.5, 2.2, W + 0.1, 0.16, "black")
    for dx in (-2.6, 0.0, 2.6):
        for dy in (-W / 2, W / 2):
            p = w(dx, dy, 0.70)
            mb.add_cyl(p[0], p[1], z + 0.24, z + 1.16, 0.46, "iron", seg=12, axis="X")
    mb.add_box_c(x + 4.2, y, z + 1.1, 0.4, 1.2, 0.3, "iron")


# ================================================================ street & port dressing
def gas_lamp(mb, x, y, z, h=4.2, mat="iron"):
    """Cast-iron gas standard with lantern and ladder rest."""
    mb.add_cyl(x, y, z, z + 0.22, 0.32, "granite", seg=10)
    mb.add_cyl(x, y, z + 0.22, z + 0.62, 0.20, mat, seg=12, r2=0.15)
    mb.add_cyl(x, y, z + 0.62, z + h, 0.10, mat, seg=10, r2=0.075)
    mb.add_cyl(x, y, z + h - 0.55, z + h - 0.30, 0.15, mat, seg=10)
    mb.add_beam((x, y, z + h - 1.3), (x + 0.42, y, z + h - 1.28), 0.05, 0.05, mat)
    zb = z + h
    mb.add_cyl(x, y, zb, zb + 0.10, 0.26, mat, seg=6)
    for i in range(4):
        a = math.pi / 2 * i + math.pi / 4
        px, py = x + math.cos(a) * 0.22, y + math.sin(a) * 0.22
        mb.add_beam((px, py, zb + 0.08), (px, py, zb + 0.78), 0.035, 0.035, mat)
    mb.add_cyl(x, y, zb + 0.18, zb + 0.68, 0.18, "lamp_glow", seg=8)
    mb.add_cyl(x, y, zb + 0.78, zb + 0.96, 0.30, mat, seg=6, r2=0.06)
    mb.add_cyl(x, y, zb + 0.96, zb + 1.06, 0.05, mat, seg=6)


def dray_cart(mb, x, y, z=QUAY_Z, rz=0.0):
    """Horse-drawn wooden flatbed dray cart with iron-tyred spoked wheels and shafts."""
    rad = math.radians(rz)
    ca, sa = math.cos(rad), math.sin(rad)

    def rot(lx, ly, lz):
        return (x + lx * ca - ly * sa, y + lx * sa + ly * ca, z + lz)

    # Flatbed timber deck
    mb.add_box_c(rot(0, 0, 1.1)[0], rot(0, 0, 1.1)[1], z + 1.1, 4.2, 2.1, 0.14, "timber")
    # Low side stakes
    for sx in (-1.8, -0.6, 0.6, 1.8):
        for sy in (-1.05, 1.05):
            p = rot(sx, sy, 1.35)
            mb.add_box_c(p[0], p[1], z + 1.35, 0.10, 0.10, 0.45, "timber")
    # Iron-tyred large rear wheels
    for sy in (-1.18, 1.18):
        p = rot(-0.6, sy, 0.75)
        mb.add_cyl(p[0], p[1], z + 0.15, z + 1.35, 0.62, "timber", seg=12, axis="Y")
        mb.add_cyl(p[0], p[1], z + 0.15, z + 1.35, 0.64, "iron", seg=12, axis="Y")
    # Small front wheels
    for sy in (-1.10, 1.10):
        p = rot(1.5, sy, 0.55)
        mb.add_cyl(p[0], p[1], z + 0.15, z + 0.95, 0.42, "timber", seg=12, axis="Y")
        mb.add_cyl(p[0], p[1], z + 0.15, z + 0.95, 0.44, "iron", seg=12, axis="Y")
    # Forward horse shafts
    p_shaft_l = rot(2.8, -0.45, 0.9)
    p_shaft_r = rot(2.8, 0.45, 0.9)
    mb.add_beam(rot(1.8, -0.45, 0.9), p_shaft_l, 0.08, 0.08, "timber")
    mb.add_beam(rot(1.8, 0.45, 0.9), p_shaft_r, 0.08, 0.08, "timber")


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
    mp = P.wmap("X", y, 1)
    P.sash_window(mb, mp, x + 1.0, x + 2.4, z + 1.1, z + 2.5, 0.35, panes_x=2, panes_y=2)


def gangway(mb, x, y, z_low, z_high, length, width=1.6, side="X", netting=True):
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


def winch(mb, x, y, z, mat="iron"):
    mb.add_box_c(x, y, z + 0.22, 1.5, 0.9, 0.44, mat)
    mb.add_cyl(x, y, z + 0.42, z + 0.52, 0.34, mat, seg=12, axis="Y")
    mb.add_cyl(x, y, z + 0.52, z + 0.62, 0.26, mat, seg=12, axis="Y")
    mb.add_beam((x + 0.6, y, z + 0.5), (x + 1.05, y, z + 0.95), 0.06, 0.06, mat)
    mb.add_cyl(x + 1.05, y, z + 0.95, z + 1.0, 0.16, mat, seg=8, axis="Y")


def plate_stack(mb, x, y, z=QUAY_Z, w=6.0, d=2.4):
    """Stack of rolled steel hull plates resting on timber dunnage baulks."""
    for dx in (-w * 0.35, 0.0, w * 0.35):
        mb.add_box_c(x + dx, y, z + 0.12, 0.28, d + 0.4, 0.24, "timber")
    pz = z + 0.24
    for i in range(8):
        mb.add_box_c(x, y, pz + 0.02, w, d, 0.04, "steel_plate")
        pz += 0.05


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
    # Stencilled shipping iron corner straps
    for cr in (lo[0], lo[1], lo[2], lo[3]):
        mb.add_beam(cr, (cr[0], cr[1], cr[2] + s), 0.04, 0.04, "black")


def barrel(mb, x, y, z, h=0.95, r=0.30, mat="timber"):
    mb.add_cyl(x, y, z, z + h * 0.18, r * 0.86, mat, seg=12)
    mb.add_cyl(x, y, z + h * 0.18, z + h * 0.82, r, mat, seg=12)
    mb.add_cyl(x, y, z + h * 0.82, z + h, r * 0.86, mat, seg=12)
    for k in (0.18, 0.42, 0.62, 0.82):
        mb.add_cyl(x, y, z + h * k, z + h * k + 0.04, r * 1.02, "iron", seg=12)


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
    for k in (0.28, 0.72):
        mb.add_box_c(x, y, z + h * k, w + 0.03, d + 0.03, 0.05, "iron")


def cargo_stack(mb, x, y, z, seed=1, spread=7.0):
    """Working stack of crates, barrels and bales."""
    rnd = random.Random(seed)
    for i in range(rnd.randint(6, 11)):
        px = x + rnd.uniform(-spread / 2, spread / 2)
        py = y + rnd.uniform(-spread / 2, spread / 2)
        k = rnd.random()
        r = rnd.uniform(0, 3.14)
        if k < 0.42:
            layers = rnd.randint(1, 3)
            s = rnd.choice([0.8, 0.95, 1.1])
            for L in range(layers):
                crate(mb, px, py, z + L * s, s=s, r=r, mat="timber")
        elif k < 0.72:
            for L in range(rnd.randint(1, 2)):
                barrel(mb, px + L * 0.1, py, z + L * 0.95, r=0.32, mat="timber")
        else:
            layers = rnd.randint(1, 2)
            for L in range(layers):
                bale(mb, px, py, z + L * 0.7, r=r, mat="canvas")

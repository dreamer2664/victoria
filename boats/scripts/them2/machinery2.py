"""
machinery2.py -- THEMISTOCLES-II steam plant + boat machinery fittings.

Boat frame: X aft(+)->bow(-? no: Hull2 X = bow +, stern -).  Here all placement
functions take explicit boat-space coordinates.  Complex parts are built in a
local frame (local x = starboard, y = forward, z = up) and then rotated by
`rot` (radians about Z) and translated by `offset` using MB.append.

Palette slots used here: 3 brass, 4 iron(black), 5 galvanised, 10 iron_paint,
14 copper, 15 steel, 16 lagging, 17 coal, 18 fire, 19 gauge glass, 20 red lead,
21 teak cleading.
"""
from __future__ import annotations
import math
import numpy as np
from .geom2 import (MB, unit, lerp, clamp, cyl, sphere, dome, torus, rivet_row,
                    rot_z, rot_axis, superellipse_section)


# ---------------------------------------------------------------------------
# small repeaters
# ---------------------------------------------------------------------------

def flange(mb, c, r, h, mat=10, holes=6, bolt_r=None, up=(0, 0, 1)):
    cyl(mb, [c[0], c[1], c[2] - h / 2], [c[0], c[1], c[2] + h / 2], r, seg=12, mat=mat)
    br = bolt_r or r * 0.78
    for i in range(holes):
        a = 2 * math.pi * i / holes
        p = [c[0] + br * math.cos(a), c[1] + br * math.sin(a), c[2] + h / 2 + 0.004]
        dome(mb, p, 0.005, seg=6, rings=3, mat=mat)


def flange_pipe(mb, path_pts, r, mat=14, flange_every=2, up=(0, 0, 1)):
    out = MB()
    out.add_tube(path_pts, r, segments=12, mat=mat)
    for i in range(1, len(path_pts) - 1, flange_every):
        p = path_pts[i]
        d = unit(np.asarray(path_pts[min(i + 1, len(path_pts) - 1)]) - np.asarray(path_pts[i - 1]))
        pa = (np.asarray(p) - d * 0.008).tolist()
        pb = (np.asarray(p) + d * 0.008).tolist()
        cyl(out, pa, pb, r * 1.35, seg=12, mat=mat)
        for sgn in (-1, 1):
            pp = (np.asarray(p) + d * (sgn * 0.012) + np.array(up) * r * 1.1).tolist()
            dome(out, pp, 0.004, seg=6, rings=3, mat=mat)
    out.append(MB())  # keep chain
    return out


def hand_wheel(mb, center, r, up=(0, 0, 1), mat=3):
    c = np.asarray(center, float)
    u = unit(np.asarray(up, float))
    cyl(mb, (c - u * 0.03).tolist(), (c + u * 0.03).tolist(), 0.009, seg=8, mat=mat)
    t = MB()
    torus(t, c.tolist(), r, 0.0075, seg=14, rseg=5, axis=u.tolist(), mat=mat)
    # two in-plane basis vectors for the spokes
    ref = np.array([0.0, 0, 1]) if abs(u[2]) < 0.9 else np.array([1.0, 0, 0])
    e1 = unit(np.cross(u, ref))
    e2 = unit(np.cross(u, e1))
    for i in range(4):
        a = i * math.pi / 2 + math.pi / 4
        p1 = (c + (e1 * math.cos(a) + e2 * math.sin(a)) * r).tolist()
        t.add_tube([c.tolist(), p1], 0.005, segments=6, mat=mat)
    mb.append(t)


def globe_valve(center, up=(0, 0, 1), out_dir=(1, 0, 0), size=1.0, mat=3):
    mb = MB()
    u = np.asarray(up, float); o = np.asarray(out_dir, float)
    c = np.asarray(center, float)
    mb.add_lathe([(0, 0.028 * size), (0.012, 0.028 * size),
                  (0.020 * size, 0.026 * size), (0.028 * size, 0.020 * size),
                  (0.030 * size, 0.012 * size), (0.026 * size, 0.006 * size),
                  (0.018 * size, 0.0), (0.008 * size, 0.002)], segments=12,
                 axis="Z", center=c, mat=mat)
    top = c + u * 0.075 * size
    cyl(mb, (c + u * 0.018 * size).tolist(), top.tolist(), 0.007 * size, seg=8, mat=mat)
    wheel_c = (c + u * 0.095 * size).tolist()
    hand_wheel(mb, wheel_c, 0.045 * size, up=u, mat=mat)
    in_a = (c - o * 0.055 * size).tolist(); in_b = (c - o * 0.020 * size).tolist()
    out_a = (c + o * 0.020 * size).tolist(); out_b = (c + o * 0.055 * size).tolist()
    cyl(mb, in_a, in_b, 0.012 * size, seg=10, mat=mat)
    cyl(mb, out_a, out_b, 0.012 * size, seg=10, mat=mat)
    for pp in (in_a, out_b):
        flange(mb, pp, 0.022 * size, 0.006, mat=mat, holes=4)
    return mb


def lagged_pipe(mb, path, r=0.030, mat_lag=16, mat_band=3, band_spacing=0.16,
                knot_path=None):
    """Canvas-lagged pipe: slightly sagging natural path (via Bézier per
    segment), one-piece modelling wax & canvas lagging w/ brass bands."""
    pts = list(map(lambda p: np.asarray(p, float), path))
    mb.add_tube(pts, r, segments=12, mat=mat_lag)
    L = 0.0
    seg = 0
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        d = b - a
        Ln = float(np.linalg.norm(d))
        u = d / Ln
        k = band_spacing - (L % band_spacing)
        while k < Ln:
            p0 = a + u * (k - 0.006); p1 = a + u * (k + 0.006)
            cyl(mb, p0.tolist(), p1.tolist(), r * 1.10, seg=12, mat=mat_band)
            k += band_spacing
        # unions: hexagonal nipple at each bend
        if i > 0:
            pa = a - u * 0.012; pb = a + u * 0.012
            cyl(mb, pa.tolist(), pb.tolist(), r * 1.22, seg=6, mat=3)
            pa2 = pb; pb2 = a + u * 0.024
            cyl(mb, pb.tolist(), pb2.tolist(), r * 1.05, seg=12, mat=mat_lag)
        L += Ln
    return mb


# ---------------------------------------------------------------------------
# gauge glass + dial + safety valves + whistle
# ---------------------------------------------------------------------------

def gauge_glass(center, h=0.30, mat_glass=19, mat_brass=3, mat_dark=11):
    mb = MB()
    z0 = center[2]
    cyl(mb, (center[0], center[1], z0 - h / 2), (center[0], center[1], z0 + h / 2),
        0.007, seg=10, mat=mat_glass)
    for sgn in (-1, 1):
        cyl(mb, (center[0] - 0.028, center[1], z0 + sgn * (h / 2 - 0.01)),
            (center[0] + 0.028, center[1], z0 + sgn * (h / 2 - 0.01)), 0.010,
            seg=8, mat=mat_brass)
        cyl(mb, (center[0] + 0.02, center[1], z0 + sgn * (h / 2 + 0.03)),
            (center[0], center[1], z0 + sgn * (h / 2 + 0.03)), 0.009, seg=8,
            mat=mat_brass)
        sphere(mb, (center[0], center[1], z0 + sgn * (h / 2 - 0.01)), 0.011, seg=8,
               rings=4, mat=mat_brass)
    # drain cock below
    cyl(mb, (center[0], center[1], z0 - h / 2 - 0.02), (center[0] + 0.03, center[1], z0 - h / 2 - 0.02),
        0.008, seg=8, mat=mat_brass)
    hand_wheel(mb, (center[0] + 0.045, center[1], z0 - h / 2 - 0.02), 0.018,
               up=(0, 0, 1), mat=mat_dark)
    return mb


def steam_gauge(center, r=0.085, up=(0, 0, 1), mat_brass=3, mat_card=11, mat_ink=4):
    mb = MB()
    u = np.asarray(up, float); c = np.asarray(center, float)
    cyl(mb, (c - u * 0.018).tolist(), (c + u * 0.018).tolist(), r * 1.08, seg=18, mat=mat_brass)
    torus(mb, (c + u * 0.016).tolist(), r * 0.96, 0.006, seg=18, rseg=5,
          axis=u.tolist(), mat=mat_brass)
    cyl(mb, (c + u * 0.018).tolist(), (c + u * 0.019).tolist(), r * 0.95, seg=18,
        mat=mat_card)
    # engraved tick marks + pointers (two-needle gauge)
    for i in range(16):
        a = math.radians(-120 + i * 240 / 15)
        pA = (c + np.array([r * 0.78 * math.cos(a), r * 0.78 * math.sin(a), 0]) + u * 0.0195).tolist()
        pB = (c + np.array([r * 0.88 * math.cos(a), r * 0.88 * math.sin(a), 0]) + u * 0.0195).tolist()
        mb.add_tube([pA, pB], 0.0014, segments=3, mat=mat_ink)
    # centre pin + red needle at ~40% and blue at ~75%
    cyl(mb, (c + u * 0.02).tolist(), (c + u * 0.024).tolist(), 0.004, seg=6, mat=mat_ink)
    n1_a = math.radians(-120 + 0.40 * 240); n2_a = math.radians(-120 + 0.75 * 240)
    for a, rr, col in ((n1_a, r * 0.72, 12), (n2_a, r * 0.66, 9)):
        pN = (c + np.array([rr * math.cos(a), rr * math.sin(a), 0]) + u * 0.022).tolist()
        pC = (c + u * 0.022).tolist()
        mb.add_tube([pC, pN], 0.0022, segments=3, mat=col)
        sphere(mb, pC, 0.008, seg=6, rings=4, mat=mat_ink)
    # syphon pigtail below (copper)
    pc0 = (c - u * 0.040).tolist()
    pts = []
    for i in range(9):
        a = i / 8 * 2 * math.pi * 1.2
        pts.append([c[0] + 0.025 * math.cos(a), c[1] + 0.025 * math.sin(a),
                    c[2] - 0.04 - i * 0.009])
    mb.add_tube([pc0] + pts + [[c[0] + 0.025, c[1], c[2] - 0.155]], 0.005, segments=8,
                mat=14)
    return mb


def safety_valve_ramsbottom(c, mat_brass=3, mat_iron=4):
    mb = MB()
    mb.add_lathe([(0, 0.038), (0.030, 0.038), (0.036, 0.028), (0.034, 0.016),
                  (0.030, 0.012), (0.030, 0.0)], segments=14, axis="Z",
                 center=c, mat=mat_brass)
    for sgn, dx in ((1, 0.020), (-1, -0.020)):
        cyl(mb, (c[0] + dx, c[1], c[2] + 0.038), (c[0] + dx, c[1], c[2] + 0.012),
            0.0145, seg=10, mat=mat_brass)
        cyl(mb, (c[0] + dx, c[1], c[2] + 0.038), (c[0] + dx, c[1], c[2] + 0.052),
            0.0035, seg=6, mat=mat_iron)
    cyl(mb, (c[0] - 0.055, c[1], c[2] + 0.052), (c[0] + 0.055, c[1], c[2] + 0.052),
        0.008, seg=8, mat=mat_iron)
    # spring + eye handles
    torus(mb, (c[0] - 0.055, c[1] + 0.012, c[2] + 0.052), 0.012, 0.0035, seg=8, rseg=4,
          axis=(1, 0, 0), mat=mat_iron)
    torus(mb, (c[0] + 0.055, c[1] + 0.012, c[2] + 0.052), 0.012, 0.0035, seg=8, rseg=4,
          axis=(1, 0, 0), mat=mat_iron)
    cyl(mb, (c[0] - 0.008, c[1] - 0.006, c[2] + 0.046), (c[0] + 0.008, c[1] + 0.006, c[2] + 0.06),
        0.0035, seg=6, mat=mat_iron)
    return mb


def whistle(c, mat=3):
    mb = MB()
    mb.add_lathe([(0, 0.0), (0.008, 0.0), (0.008, 0.16), (0.011, 0.165), (0.011, 0.19),
                  (0.006, 0.195), (0.0, 0.195)], segments=12, axis="Z", center=c, mat=mat)
    cyl(mb, (c[0] + 0.012, c[1], c[2] + 0.155), (c[0] + 0.016, c[1], c[2] + 0.155), 0.003, seg=6, mat=mat)
    return mb


def feed_check_valve(c, mat=3):
    mb = MB()
    mb.add_lathe([(0, 0.030), (0.026, 0.030), (0.030, 0.020), (0.028, 0.010),
                  (0.020, 0.006), (0.0, 0.006)], segments=12, axis="Z", center=c, mat=mat)
    hand_wheel(mb, [c[0], c[1], c[2] + 0.048], 0.030, mat=mat)
    cyl(mb, (c[0], c[1], c[2] + 0.030), (c[0], c[1], c[2] + 0.052), 0.006, seg=8, mat=mat)
    return mb


def boiler_mountings(base_face_pt, top_pt, shell_r, mat_brass=3, mat_iron=4):
    """
    Boiler mountings: gauge glass + steam gauge + Ramsbottom safety +
    whistle, all on the shell top band facing the stoker position.
    face_pt = boat-space point on the boiler face (fire door) side.
    """
    mb = MB()
    fx, fy, fz = base_face_pt
    tx, ty, tz = top_pt
    gg = gauge_glass((fx + 0.30 * 0.55, fy + 0.02, fz + 0.42), h=0.30)
    mb.append(gg)
    mb.append(steam_gauge((fx + 0.10, fy - 0.07, fz + 0.55), r=0.085))
    mb.append(safety_valve_ramsbottom((tx - 0.18, ty, tz + 0.015)))
    mb.append(whistle((tx - 0.30, ty, tz + 0.015)))
    mb.append(feed_check_valve((tx + 0.14, ty - 0.12, tz + 0.012)))
    return mb


# ---------------------------------------------------------------------------
# the vertical multitubular boiler (lagged, teak cleading, fire door open)
# ---------------------------------------------------------------------------

def vertical_boiler(center, dia=0.72, h_shell=0.86, mat_iron=10, mat_brass=3,
                    mat_coal=17, mat_fire=18, mat_lag=16, mat_clead=21):
    """
    Watertube-style vertical cylindrical boiler: base stays + ash-pit opening,
    fire door (open, coals glowing inside), lagged shell bands, top dome with
    mountings' bases.  Returns dict with face_pt and top_pt (boat space).
    """
    cx, cy, cz = center
    mb = MB()
    R = dia / 2
    # base bed: heavy wrought sole plate on the bearers
    mb.add_lathe([(0, 0), (R * 0.98 * 0, 0), (R * 1.04, 0.0), (R * 1.04, 0.045),
                  (R * 0.96, 0.055), (R * 0.96, 0.06), (0, 0.06)], segments=24,
                 axis="Z", center=(cx, cy, cz), mat=mat_iron)
    # ash pit + furnace door opening (dark cavity w/ coals)
    mb.add_lathe([(R * 0.60, 0.06), (R * 0.96, 0.06), (R * 0.96, 0.20),
                  (R * 0.78, 0.26), (R * 0.62, 0.30)], segments=24, axis="Z",
                 center=(cx, cy, cz), mat=mat_fire, cap_lo=True)
    # cladding: teak cleading between brass bands, slight bulge lagging
    prof = []
    n_sk = 9
    for i in range(n_sk):
        f = i / (n_sk - 1)
        rr = R * (1.02 + 0.04 * math.sin(f * math.pi))
        prof.append((rr, 0.28 + f * h_shell + 0.02))
    mb.add_lathe(prof, segments=20, axis="Z", center=(cx, cy, cz), mat=mat_clead)
    # teak cleading: separate staves between the bands
    for i in range(20):
        a0 = 2 * math.pi * (i / 20) + 0.06
        for k in range(6):
            f0, f1 = k / 6, (k + 1) / 6
            zz0 = cz + 0.30 + f0 * h_shell + 0.008
            zz1 = cz + 0.30 + f1 * h_shell - 0.008
            rfm = lambda f: R * (1.02 + 0.045 * math.sin(f * math.pi)) * 0.995
            p0 = [cx + rfm(f0) * math.cos(a0), cy + rfm(f0) * math.sin(a0), zz0]
            p1 = [cx + rfm(f1) * math.cos(a0), cy + rfm(f1) * math.sin(a0), zz1]
            pa = np.array(p0); pb = np.array(p1)
            pm = (pa + pb) / 2
            g = np.array([[pa - np.array([0, 0, 0]), pb - np.array([0, 0, 0])],
                          [pa - np.array([0, 0, 0]), pb - np.array([0, 0, 0])]])
            # vertical slat: thin box aligned to the mid-plane
            mb.add_tube([p0, p1], R * 0.048, segments=10, mat=mat_clead,
                        radii=[R * 0.048 * (1 - 0.05 * abs(0.5 - q) * 0) for q in (0, 1)])
    # brass bands at 6 heights (inc. bottom + top rim)
    for k in range(7):
        f = k / 6
        z = cz + 0.30 + f * h_shell
        rr = R * (1.02 + 0.04 * math.sin(f * math.pi))
        cyl(mb, (cx, cy, z - 0.009), (cx, cy, z + 0.009), rr * 1.010, seg=22,
            mat=mat_brass)
    # holding-down stays bolted into bed every 30deg
    for i in range(12):
        a = 2 * math.pi * i / 12
        x = cx + R * 0.92 * math.cos(a)
        y = cy + R * 0.92 * math.sin(a)
        cyl(mb, (x, y, cz + 0.02), (x, y, cz + 0.30), 0.011, seg=8, mat=mat_iron)
        dome(mb, (x, y, cz + 0.28), 0.006, seg=6, rings=3, mat=mat_brass)
    # fire door on the forward side (Y+ local = +cy): hinged, latched open,
    # dark furnace behind with a heap of glowing coals
    door_y = cy + R * 0.99
    door_z = cz + 0.16
    # door frame
    torus(mb, (cx, door_y, door_z), R * 0.42, 0.014, seg=18, rseg=5,
          axis=(0, 1, 0), mat=mat_iron)
    # door leaf open 105deg
    leaf = MB()
    leaf.add_lathe([(R * 0.42, 0.0), (R * 0.42, 0.016)], segments=18, axis="Y",
                   center=(cx - R * 0.46, door_y + 0.02, door_z), mat=mat_iron)
    # hinges + latch
    cyl(leaf, (cx - R * 0.46, door_y + 0.01, door_z + 0.12),
        (cx - R * 0.46, door_y + 0.05, door_z + 0.12), 0.010, seg=8, mat=mat_brass)
    cyl(leaf, (cx - R * 0.46, door_y + 0.01, door_z - 0.10),
        (cx - R * 0.46, door_y + 0.05, door_z - 0.10), 0.010, seg=8, mat=mat_brass)
    mb.append(leaf)
    # glowing coals
    import random
    rnd = random.Random(42)
    for _ in range(26):
        th = rnd.uniform(0, 2 * math.pi)
        rr = rnd.uniform(0, R * 0.45)
        px = cx + rr * math.cos(th)
        py = cy + rr * math.sin(th) * 0.6 + R * 0.30
        pz = cz + 0.08 + rnd.uniform(0, 0.07)
        s = rnd.uniform(0.018, 0.040)
        np.random.seed(1)
        mb.add_ico(px, py, pz, s, mat=mat_fire if rnd.random() < 0.35 else mat_coal)
    # steam pipe exit top (to engine) and trumpet feed
    cyl(mb, (cx, cy, cz + 0.30 + h_shell + 0.06), (cx, cy - 0.12, cz + 0.30 + h_shell + 0.10),
        0.040, seg=12, mat=mat_brass)
    face_pt = (cx, door_y, cz + 0.16)
    top_pt = (cx, cy, cz + 0.30 + h_shell + 0.13)
    return {"mb": mb, "face_pt": list(face_pt), "top_pt": list(top_pt),
            "shell_r": R, "base_z": cz}


# ---------------------------------------------------------------------------
# the compound vertical engine with Stephenson link
# ---------------------------------------------------------------------------

def vertical_engine(center, n_cyl=2, mat_iron=10, mat_steel=15, mat_brass=3):
    """
    Twin compound vertical engine on raised bedplate: two trunk guide columns,
    cylinders (HP+LP), crank webs, eccentrics and Stephenson links, reversing
    lever, condenser with leather apron guard.  local y = fwd, z up.
    Returns dict {"mb":..., "pivots":{...}}.
    """
    cx, cy, cz = center
    mb = MB()
    p = {}
    # bedplate
    mb.add_box((cx, cy, cz - 0.05), (0.56, 0.42, 0.10), mat=mat_iron, chamfer=0.015)
    bolts = []
    for sx in (-0.22, 0.22):
        for sy in (-0.16, 0.16):
            bolts.append([(cx + sx, cy + sy, cz + 0.002), (cx + sx, cy + sy, cz + 0.03)])
    for b0, b1 in bolts:
        cyl(mb, b0, b1, 0.011, seg=6, mat=mat_brass)
    hn = [0.55 if n_cyl == 2 else 0.50] * n_cyl
    hh = 0.60
    cyl_h = 0.42
    offs = np.linspace(-(n_cyl - 1) / 2, (n_cyl - 1) / 2, n_cyl)
    cols = []
    for i, frac in enumerate(offs):
        x0 = cx + frac * 0.30
        # front and rear columns (channels)
        for sgn in (-1, 1):
            ycol = cy + sgn * 0.10
            chan = MB()
            chan.add_box((x0, ycol, cz + cyl_h / 2 + 0.02), (0.055, 0.04, cyl_h),
                         mat=mat_iron)
            mb.append(chan)
        # trunk guide crosshead rails between columns
        mb.add_box((x0, cy, cz + 0.33), (0.06, 0.26, 0.14), mat=mat_iron)
        # cylinder lagged barrel: teak cleading cover (21) over lagging bands
        rc = 0.148 if i == 0 else 0.180
        cyl(mb, (x0, cy, cz + cyl_h + 0.06), (x0, cy, cz + cyl_h + 0.42), rc,
            seg=14, mat=16)
        for fac in (0.10, 0.35, 0.60, 0.85):
            zz = cz + cyl_h + 0.06 + fac * 0.36
            cyl(mb, (x0, cy, zz - 0.006), (x0, cy, zz + 0.006), rc * 1.02, seg=14,
                mat=mat_brass)
        torus(mb, (x0, cy, cz + cyl_h + 0.425), rc * 1.0, 0.007, seg=14, rseg=4,
              axis="Z", mat=mat_brass)
        cyl(mb, (x0, cy, cz + cyl_h + 0.42), (x0, cy, cz + cyl_h + 0.445), rc * 0.98,
            seg=14, mat=mat_iron)
        # cylinder top + bottom covers
        torus(mb, (x0, cy, cz + cyl_h + 0.42), 0.120 if i else 0.160, 0.008,
              seg=16, rseg=5, axis="Z", mat=mat_brass)
        # gland/piston rod
        cyl(mb, (x0, cy, cz + cyl_h + 0.42), (x0, cy, cz + cyl_h + 0.02), 0.016,
            seg=10, mat=mat_steel)
        # crosshead block + guide
        mb.add_box((x0, cy, cz + 0.30), (0.07, 0.10, 0.05), mat=mat_steel)
        # connecting rod down to crank
        cyl(mb, (x0, cy, cz + 0.28), (x0, cy, cz - 0.09), 0.013, seg=8, mat=mat_steel)
        # crank web + journal at bed
        cg = np.array([x0, cy + (0.05 if i % 2 == 0 else -0.05), cz - 0.105])
        web = MB()
        web.add_box(cg.tolist(), (0.018, 0.10, 0.09), mat=mat_iron)
        mb.append(web, rot=rot_axis((0, 1, 0), math.radians(90 if i % 2 == 0 else -90)),
                  offset=(0, 0, 0))
        cyl(mb, cg.tolist(), (cg + np.array([0, 0.055, 0])).tolist(), 0.020, seg=10,
            mat=mat_steel)
        cols.append(cg)
        # Stephenson link: rod + two block eccentrics + curved slotted link
        zlink = cz - 0.04
        cyl(mb, (x0, cy + 0.155, cz + 0.06), (x0, cy + 0.155, cz - 0.16), 0.008, seg=6,
            mat=mat_steel)
        mb.add_box((x0, cy + 0.155, cz - 0.16), (0.020, 0.030, 0.16), mat=mat_iron)
        for sgn2 in (-1, 1):
            cyl(mb, (x0, cy + 0.14, zlink + sgn2 * 0.05), (x0, cy + 0.17, zlink + sgn2 * 0.05),
                0.012, seg=8, mat=mat_brass)
    # reversing lever with brass quadrant
    lever = MB()
    lever.add_tube([(cx + 0.32, cy - 0.05, cz - 0.10), (cx + 0.32, cy - 0.05, cz + 0.40)],
                   0.011, segments=8, mat=mat_steel)
    lever.add_box((cx + 0.32, cy - 0.05, cz + 0.44), (0.05, 0.024, 0.05), mat=mat_brass,
                  chamfer=0.01)
    mb.append(lever)
    # hand wheel for throttle at the engine front side
    hand_wheel(mb, [cx - 0.20, cy + 0.22, cz + 0.28], 0.10, up=(0, 1, 0), mat=mat_brass)
    # small polished steel ram pump on the side (direct acting)
    cyl(mb, (cx + 0.24, cy + 0.10, cz + 0.18), (cx + 0.24, cy - 0.02, cz + 0.18), 0.020,
        seg=10, mat=mat_steel)
    cyl(mb, (cx + 0.24, cy - 0.02, cz + 0.18), (cx + 0.24, cy - 0.14, cz + 0.18), 0.013,
        seg=8, mat=mat_steel)
    # surface condenser box under crank (leather apron ahead)
    mb.add_box((cx, cy - 0.02, cz - 0.14), (0.44, 0.30, 0.10), mat=mat_iron)
    p["crank_x"] = [round(cx + o * 0.30, 3) for o in offs]
    p["bed_z"] = round(cz - 0.05, 3)
    return {"mb": mb, "pivots": p}


# ---------------------------------------------------------------------------
# shaft, bracket, propeller
# ---------------------------------------------------------------------------

def shaft_line(hull, eng_pt, exit_xi, mat_bronze=3, mat_shaft=15, mat_iron=10):
    """
    Propeller shaft from engine bed to stern tube exit: steel shaft with
    plummer blocks on the bearers, universal coupling, stern tube with
    stuffing box, three-bolt bracket on the counter, two-blade propeller nut.
    eng_pt = boat-space crank centre (x, y, z).  exit_xi where it exits.
    Returns {"mb", "end_pt", "axis_dir"}.
    """
    mb = MB()
    x0, y0, z0 = eng_pt
    xi = exit_xi
    x1 = hull.X(xi)
    z1 = hull.keel_z(xi) + 0.06
    y1 = 0.0
    axis = unit(np.array([x1 - x0, y1 - y0, z1 - z0]))
    L = float(np.linalg.norm(np.array([x1 - x0, y1 - y0, z1 - z0])))
    mb.add_tube([(x0, y0, z0), (x1, y1, z1)], 0.024, segments=10, mat=mat_shaft)
    # coupling flanges
    n_fl = max(1, int(L / 0.60))
    for k in range(1, n_fl + 1):
        pk = lerp(np.array(eng_pt), np.array([x1, y1, z1]), 0.06 + k / (n_fl + 1) * 0.9)
        pa = pk - axis * 0.010; pb = pk + axis * 0.010
        cyl(mb, pa.tolist(), pb.tolist(), 0.045, seg=10, mat=mat_iron)
    # square shaft gland at stern tube (brass)
    cyl(mb, (x1 - axis[0] * 0.03, y1 - axis[1] * 0.03 - 0.0, z1 - axis[2] * 0.03),
        (x1 - axis[0] * 0.05 - 0.04, y1 - 0.04 * axis[1], z1 - axis[2] * 0.05 - 0.005),
        0.034, seg=6, mat=mat_bronze)
    end_pt = (x1 + axis[0] * 0.10, y1 + axis[1] * 0.10, z1 + axis[2] * 0.10)
    return {"mb": mb, "end_pt": list(end_pt), "axis_dir": list(axis),
            "exit_pt": [x1, y1, z1]}


def stern_bracket(hull, end_pt, axis_dir, mat_iron=4, mat_bronze=3):
    """A-frame stern bracket + rudder support shoe on the counter."""
    mb = MB()
    ex, ey, ez = end_pt
    ax = np.asarray(axis_dir, float)
    # strut from hull underbody to shaft end
    xi = clamp((hull.loa / 2 - ex) / hull.loa, 0, 1)
    ki = hull.keel_z(xi) - 0.10
    p0 = np.array([ex + ax[0] * 0.10, 0, ki])
    p1 = np.array([ex, 0, ez])
    mb.add_box(((p0 + p1) / 2).tolist(),
               (0.05, 0.03, abs(p0[2] - p1[2]) + 0.06), mat=mat_iron, chamfer=0.006)
    torus(mb, (ex - 0.0, 0, ez), 0.045, 0.011, seg=10, rseg=5, axis=ax.tolist(), mat=mat_bronze)
    return mb


def propeller_two_blade(center, axis_dir, d=0.60, pitch=0.80, mat=3,
                        nb=2, seg=64):
    """Helically-swept two-blade propeller (Admiralty pattern w/ palms)."""
    c = np.asarray(center, float)
    ax = unit(np.asarray(axis_dir, float))
    hub_r = d * 0.09
    mb = MB()
    cyl(mb, (c - ax * 0.07).tolist(), (c + ax * 0.07).tolist(), hub_r, seg=12, mat=mat)
    dome(mb, (c + ax * 0.08).tolist(), 0.028, seg=8, rings=4, mat=mat)
    u1 = unit(np.cross(ax, [0, 0, 1]) if abs(ax[2]) < 0.9 else np.cross(ax, [1, 0, 0]))
    u2 = unit(np.cross(ax, u1))
    n_seg = 11
    for b in range(nb):
        bA = b * math.pi + 0.12
        root_hat = math.cos(bA) * u1 + math.sin(bA) * u2
        pts = []
        for i in range(n_seg):
            t = i / (n_seg - 1)
            r = hub_r * 1.15 + t * (d / 2 - hub_r * 1.15)
            ang = bA + pitch * t * 0.16
            blade_dir = math.cos(ang) * u1 + math.sin(ang) * u2
            p = c + blade_dir * r + ax * (t * 0.05 * pitch)
            pts.append(p)
        prof = []
        for i, pp in enumerate(pts):
            t = i / (n_seg - 1)
            chord = d * (0.10 + 0.05 * math.sin(t * math.pi))
            prof.append((chord * 0.5, chord * 0.5 * 0.0))
        mb.add_blade(pts, widths=[p[0] for p in prof], mat=mat,
                     axis=unit(np.array(root_hat)))
    return mb


# ---------------------------------------------------------------------------
# feed tank, hand pump, fire irons, coal bunker
# ---------------------------------------------------------------------------

def feed_tank(center, r=0.16, l=0.42, mat_copper=14, mat_brass=3):
    mb = MB()
    cx, cy, cz = center
    cyl(mb, (cx - l / 2, cy, cz), (cx + l / 2, cy, cz), r, seg=18, mat=mat_copper)
    for sgn in (-1, 1):
        x = cx + sgn * l / 2 * 0.999
        mb.add_lathe([(0, 0), (r, 0), (r, 0.012), (r * 0.85, 0.05), (0, 0.055)],
                     segments=18, axis="X", center=(x, cy, cz), mat=mat_copper)
        ton = [(cx + sgn * (l/2+0.012), cy, cz + 0), (cx + sgn * (l/2+0.05), cy, cz + 0.05)]
    # rivets around girth seams
    for f in (0.0, 0.5, 1.0):
        xr = cx - l / 2 + f * l
        pr = [(xr, cy + r * math.sin(a), cz + r * math.cos(a))
              for a in np.linspace(0, 2 * math.pi, 14, endpoint=False)]
        rivet_row(mb, np.array(pr), None, 0.04, 0.0045, 0.010, mat=mat_brass)
    # mountings: float gauge glass at end + filling cap + outlet
    cyl(mb, (cx + l / 2 + 0.02, cy + 0.06, cz + 0.02), (cx + l / 2 + 0.06, cy + 0.06, cz + 0.06),
        0.020, seg=10, mat=mat_brass)
    dome(mb, (cx + l / 2 + 0.06, cy + 0.06, cz + 0.06), 0.028, seg=10, rings=4, mat=mat_brass)
    cyl(mb, (cx - l / 2 - 0.01, cy, cz - r * 0.6), (cx - l / 2 - 0.05, cy - 0.04, cz - r * 0.7),
        0.012, seg=8, mat=mat_brass)
    return mb


def hand_pump(center, mat_brass=3, mat_iron=10, r=0.045, h=0.5):
    mb = MB()
    cx, cy, cz = center
    cyl(mb, (cx, cy, cz), (cx, cy, cz + h * 0.75), r, seg=12, mat=mat_brass)
    torus(mb, (cx, cy, cz + h * 0.75), r * 1.05, 0.009, seg=10, rseg=5, axis="Z", mat=mat_brass)
    cyl(mb, (cx, cy, cz + h * 0.75), (cx, cy, cz + h), r * 0.62, seg=10, mat=mat_brass)
    # lever arm with pivot pin
    cyl(mb, (cx - 0.02, cy, cz + h), (cx + 0.30, cy, cz + h - 0.10), 0.013, seg=8, mat=mat_iron)
    sphere(mb, (cx + 0.30, cy, cz + h - 0.10), 0.022, seg=8, rings=4, mat=mat_iron)
    cyl(mb, (cx - 0.02, cy, cz + h), (cx - 0.02, cy, cz + h + 0.14), 0.011, seg=8, mat=mat_iron)
    # spout down to tank
    cyl(mb, (cx - 0.04, cy + 0.02, cz + 0.18), (cx - 0.10, cy - 0.02, cz + 0.02), 0.014, seg=8, mat=mat_brass)
    return mb


def fire_irons(center, mat=10):
    """Slice bar, pricker, rake and ash shovel standing in a neat row;
    wooden handles, business ends down on the floor."""
    mb = MB()
    cx, cy, cz = center
    tools = [("slice", 0.62), ("pricker", 0.55), ("rake", 0.58)]
    for i, (nm, ln) in enumerate(tools):
        bx = cx + i * 0.055
        # shaft
        a = np.array([bx, cy, cz + ln])
        b = np.array([bx + 0.02, cy, cz + 0.06])
        cyl(mb, a.tolist(), b.tolist(), 0.005, seg=6, mat=mat)
        # T-handle on top
        cyl(mb, [bx - 0.03, cy, cz + ln], [bx + 0.03, cy, cz + ln], 0.007, seg=6, mat=mat)
        # working end
        if nm == "slice":
            mb.add_plate([(-0.02, 0), (0.02, 0), (0.02, 0.05), (-0.02, 0.05)], 0.004,
                         origin=(bx - 0.002, cy, cz + 0.03), mat=mat,
                         basis=((1, 0, 0), (0, 0, 1), (0, 1, 0)))
        else:
            for k in range(2 if nm == "rake" else 1):
                cyl(mb, [bx + 0.02, cy - 0.02 + k * 0.04, cz + 0.06],
                    [bx + 0.06, cy - 0.02 + k * 0.04, cz + 0.0], 0.004, seg=5, mat=mat)
    # shovel laid on the floor beside
    bx = cx + 0.26
    mb.add_box((bx, cy, cz + 0.01), (0.11, 0.15, 0.006), mat=mat, chamfer=0.005)
    cyl(mb, (bx - 0.055, cy, cz + 0.01), (bx - 0.30, cy, cz + 0.03), 0.008, seg=6, mat=0)
    sphere(mb, (bx - 0.315, cy, cz + 0.033), 0.014, seg=6, rings=4, mat=0)
    return mb


def coal_bunker(hull, xi_range=(0.60, 0.72), mat_iron=10, mat_coal=17):
    """Coal bunker: low sheet-iron bin abreast the boiler, coal heaped in,
    panelled sides with rivets; lid open ajar."""
    mb = MB()
    xi0, xi1 = xi_range
    x0, x1 = hull.X(xi0), hull.X(xi1)
    xmid = (x0 + x1) / 2
    z0 = hull.keel_z((xi0 + xi1) / 2) + 0.16
    z1 = z0 + 0.30
    y_half = min(hull.W * 0.47, 0.46)
    # U profile: bottom plate + side walls + end plates, top rim angles
    mb.add_box((xmid, 0, z0 + 0.012), (x1 - x0, y_half * 2, 0.024), mat=mat_iron,
               chamfer=0.002)
    for (p0, wd, hh) in (((x0, -y_half), 0, 0),
                         ((x0, y_half), 0, 0), ((x0, 0), 0, 0), ((x1, 0), 0, 0)):
        pass
    mb.add_box(((x0 + x1) / 2, -y_half + 0.006, z0 + (z1 - z0) / 2),
               (x1 - x0, 0.012, z1 - z0), mat=mat_iron, chamfer=0.002)
    mb.add_box(((x0 + x1) / 2,  y_half - 0.006, z0 + (z1 - z0) / 2),
               (x1 - x0, 0.012, z1 - z0), mat=mat_iron, chamfer=0.002)
    mb.add_box((x0 + 0.006, 0, (z0 + z1) / 2),
               (0.012, y_half * 2 - 0.024, z1 - z0), mat=mat_iron, chamfer=0.002)
    mb.add_box((x1 - 0.006, 0, (z0 + z1) / 2),
               (0.012, y_half * 2 - 0.024, z1 - z0), mat=mat_iron, chamfer=0.002)
    # top rim angles + rivets
    for sgn in (-1, 1):
        pts = [(x0 + 0.01, sgn * y_half, z1), (x1 - 0.01, sgn * y_half, z1)]
        mb.add_tube(pts, 0.008, segments=6, mat=mat_iron, caps=False, oval=(1.6, 1.0))
        nd = 9
        for i in range(nd):
            xr = x0 + 0.02 + (x1 - x0 - 0.04) * i / (nd - 1)
            dome(mb, (xr, sgn * y_half - 0.001, z1 - 0.02), 0.006, seg=6, rings=3,
                 mat=mat_iron, squash=0.5)
    # coal heap
    rnd = np.random.RandomState(7)
    for _ in range(130):
        px = rnd.uniform(x0 + 0.05, x1 - 0.05)
        py = rnd.uniform(-y_half * 0.8, y_half * 0.8)
        heap = 0.20 * math.exp(-((px - xmid) ** 2 / 0.20) - (py ** 2) / 0.08)
        mb.add_ico(px, py, z0 + 0.03 + heap * rnd.uniform(0.3, 1.0),
                   rnd.uniform(0.020, 0.050), mat=mat_coal)
    # lid propped open against the forward bulkhead
    lid = MB()
    lid.add_box((x0 + 0.10, -y_half + 0.05, z1 + 0.07), (0.30, 0.05, 0.12),
                mat=mat_iron, chamfer=0.003)
    cyl(mb, (x0 + 0.08, -y_half + 0.05, z1), (x0 + 0.08, -y_half + 0.10, z1), 0.008,
        seg=8, mat=3)
    mb.append(lid)
    return mb


# ---------------------------------------------------------------------------
# funnel, guy stays, helm station, steering chain, state cabin, sidelights,
# canopy tracks, dagger boards, ensign, bell, harpoon/tub, centreboard
# ---------------------------------------------------------------------------

def funnel(base, top_r=0.10, r=0.115, mat_iron=10, mat_brass=3, h=1.42,
           mat_cap=21):
    mb = MB()
    bx, by, bz = base
    zb = bz
    zt = bz + h
    # base flange on boiler top
    cyl(mb, (bx, by, zb - 0.02), (bx, by, zb + 0.03), r * 1.35, seg=18, mat=mat_brass)
    # lower casing: teak cleading over lagging, brass banjo at top
    for i in range(10):
        f = i / 9
        z = zb + 0.03 + f * (h * 0.32)
        cyl(mb, (bx, by, z - h * 0.32 / 9 * 0.5), (bx, by, z + h * 0.32 / 9 * 0.5),
            r * (1.02 + 0.07 * math.sin(f * math.pi)), seg=14, mat=21, caps=True)
    torus(mb, (bx, by, zb + h * 0.34), r * 1.06, 0.008, seg=14, rseg=4, axis="Z", mat=3)
    # steam pipe casing: iron flue with brass banjo at top + guy stays
    cyl(mb, (bx, by, zb + 0.35 * bz * 0 + h * 0.32), (bx, by, zt - 0.02), r * 0.62, seg=14,
        mat=mat_iron)
    # sliding extended section
    cyl(mb, (bx, by, zt - 0.04), (bx, by, min(zt + 0.16, zt + 0.16)), r * 0.66, seg=14, mat=mat_iron)
    torus(mb, (bx, by, zt + 0.16), r * 0.66, 0.010, seg=14, rseg=5, axis="Z", mat=mat_brass)
    dome(mb, (bx, by, zt + 0.175), r * 0.30, seg=10, rings=4, mat=mat_iron)
    # spark-arrestor wire cage at mouth (fine bars)
    torus(mb, (bx, by, zt + 0.175), r * 0.30, 0.006, seg=12, rseg=3, axis="Z", mat=mat_brass)
    for i in range(8):
        aa = 2 * math.pi * i / 8
        mb.add_tube([(bx + r * 0.30 * math.cos(aa), by + r * 0.30 * math.sin(aa), zt + 0.175),
                     (bx, by, zt + 0.24)], 0.004, segments=4, mat=mat_brass)
    # guy stays (galvanised wire): two fore, one aft w/ bottle screws
    stays = [(0.9, 0.0, -0.9), (0.9, 0.9, -0.6), (0.9, -0.9, -0.6), (0.9, 0.0, 0.95)]
    for (fz, dy, dx) in stays:
        zg = zb + h * fz
        p0 = np.array([bx, by, zg])
        p1 = np.array([bx - dx, by + dy, zb + 0.28])
        mb.add_tube([p0.tolist(), p1.tolist()], 0.005, segments=6, mat=5)
        cyl(mb, (p1 - np.array([0, 0, 0.05])).tolist(), p1.tolist(), 0.008, seg=6, mat=3)
        cyl(mb, (p1 - np.array([0, 0, 0.02])).tolist(), p1.tolist(), 0.013, seg=13 if False else 6, mat=3)
        cyl(mb, (p1 + unit(p0 - p1) * 0.10).tolist(), p1.tolist(), 0.006, seg=6, mat=3)
    return {"mb": mb, "top_pt": [bx, by, zt + 0.24]}


def helm_station(hull, x_helm, mat_brass=3):
    """Steering wheel + pedestal + chart of the ship & barometer behind."""
    mb = MB()
    p = {}
    z0 = hull.keel_z(0.86) + 0.30
    # pedestal: box w/ hidden chains
    mb.add_box((x_helm, 0, z0 + 0.22), (0.14, 0.10, 0.44), mat=0, chamfer=0.012)
    cyl(mb, (x_helm, 0, z0 + 0.44), (x_helm, 0, z0 + 0.58), 0.022, seg=8, mat=mat_brass)
    # wheel on transverse axle
    xc = (x_helm, 0, z0 + 0.62)
    torus(mb, xc, 0.24, 0.012, seg=20, rseg=5, axis=(1, 0, 0), mat=mat_brass)
    for i in range(6):
        a = i / 6 * 2 * math.pi
        p1 = [0.0, 0.24 * math.cos(a), 0.24 * math.sin(a)]
        mb.add_tube([(x_helm, 0, z0 + 0.62),
                     [x_helm, 0.245 * math.cos(a), z0 + 0.62 + 0.245 * math.sin(a)]],
                    0.008, segments=6, mat=mat_brass)
        sphere(mb, [x_helm, 0.245 * math.cos(a), z0 + 0.62 + 0.245 * math.sin(a)],
               0.012, seg=6, rings=4, mat=3)
    # barrel-guard: small drum with enamel ship chart + barometer above
    torus(mb, (x_helm + 0.10, 0, z0 + 0.72), 0.04, 0.006, seg=12, rseg=4, axis=(1, 0, 0), mat=3)
    cyl(mb, (x_helm + 0.10, 0, z0 + 0.72), (x_helm + 0.10, 0, z0 + 0.72), 0.038, seg=12,
        mat=11)
    p["wheel"] = [x_helm, 0, z0 + 0.62]
    return mb, p


def steering_chain(hull, mat=5):
    """Chain-and-rod steering run from pedal/helm to aft quadrant."""
    mb = MB()
    # not modelling the full run; add quadrant chains over the beam at stern
    zq = hull.sheer_z(0.97) - 0.12
    xq = hull.X(0.97)
    pts = [(xq - 0.40 + 0.40 * math.cos(a), s * (0.40 * math.sin(a)), zq - 0.02)
           for s in (1, -1) for a in np.linspace(0, math.pi, 8)]
    mb.add_tube(pts[:8], 0.007, segments=6, mat=mat)
    mb.add_tube(pts[8:], 0.007, segments=6, mat=mat)
    return mb


def state_cabin(hull, xi_range=(0.80, 0.985), mat=21, mat_roof=21):
    """Teak state cabin: panelled side walls inside the gunnels, cambered roof,
    fore bulkhead w/ panelled door + brass knob, curb + skylight."""
    mb = MB()
    xi0, xi1 = xi_range
    info = {}
    n = 24
    xis = np.linspace(xi0, xi1, n)
    z_floor = hull.keel_z((xi0 + xi1) / 2) + 0.18
    z_wall_top = z_floor + 0.58
    # ---- side walls (both sides): vertical quads hugging the inside skin ----
    for sgn in (-1, 1):
        grid = np.zeros((n, 2, 3))
        for i, xi in enumerate(xis):
            pin = hull.section_pt(xi, 0.86, -0.10)
            grid[i, 0] = [pin[0], sgn * abs(pin[1]) * 0.82, z_floor]
            grid[i, 1] = [pin[0], sgn * abs(pin[1]) * 0.82, z_wall_top]
        mb.add_grid(grid, mat)
        # door frames: stiles/rail moulding strips on each wall
        for i in range(0, n, max(1, n // 6)):
            cyl(mb, tuple(grid[i, 0]), tuple(grid[i, 1]), 0.009, seg=6, mat=21)
    # ---- cambered roof (double-curved) ----------------------------------------
    roof = np.zeros((n, 3, 3))
    for i, xi in enumerate(xis):
        pin = hull.section_pt(xi, 0.86, -0.10)
        hw = abs(pin[1]) * 0.82
        xr = pin[0]
        for k in range(3):
            t2 = (k - 1) * 1.0
            zc = z_wall_top + 0.10 * (1 - t2 * t2 * 0.55)
            roof[i, k] = [xr, t2 * hw, zc]
    # roof: lower layer wall-top minus camber, upper = cambered walk-on roof
    mb_top = MB()
    mb_top.add_grid(roof[:, :, :], mat_roof)
    roof_b = roof.copy(); roof_b[:, :, 2] -= 0.020
    mb_b = MB(); mb_b.add_grid(roof_b, mat_roof)
    gridn = ring = None
    # weld edges: stitch the two faces' boundary
    mb.append(mb_top)
    mb.append(mb_b)
    # skylight + curb on the roof
    mb.add_box((hull.X((xi0 + xi1) / 2), 0, z_wall_top + 0.115), (0.46, 0.30, 0.035),
               mat=21, chamfer=0.012)
    # fore bulkhead w/ panelled door (plate outline in Y-Z plane via basis)
    xh = hull.X(xi1)
    pin0 = hull.section_pt(xi1, 0.86, -0.10)
    hw0 = abs(pin0[1]) * 0.82
    mb.add_plate([(-hw0, z_floor), (hw0, z_floor), (hw0, z_wall_top), (-hw0, z_wall_top)],
                 0.030, origin=(xh, 0, 0), mat=mat,
                 basis=((0, 1, 0), (0, 0, 1), (1, 0, 0)))
    mb.add_plate([(-0.15, z_floor + 0.02), (0.15, z_floor + 0.02), (0.15, z_floor + 0.56),
                  (-0.15, z_floor + 0.56)], 0.020, origin=(xh - 0.026, 0, 0), mat=0,
                 basis=((0, 1, 0), (0, 0, 1), (1, 0, 0)))
    dome(mb, (xh - 0.040, -0.11, z_floor + 0.34), 0.012, seg=6, rings=3, mat=3)
    info["door_x"] = round(xh, 3)
    return {"mb": mb, "info": info}


def glazed_skylight(center, size=(0.46, 0.30), h=0.085, mat=21, mat_brass=3,
                    mat_glass=9):
    """Glazed cabin skylight on its curb: cambered top with four glass panes
    in brass bars, end cheeks, and a brass ridge strip."""
    cx, cy, cz = center
    sx, sy = size
    mb = MB("Glazed_Skylight")
    # curb rails
    mb.add_box((cx, cy - sy / 2 + 0.012, cz + 0.025), (sx, 0.024, 0.05), mat=mat)
    mb.add_box((cx, cy + sy / 2 - 0.012, cz + 0.025), (sx, 0.024, 0.05), mat=mat)
    mb.add_box((cx - sx / 2 + 0.012, cy, cz + 0.025), (0.024, sy, 0.05), mat=mat)
    mb.add_box((cx + sx / 2 - 0.012, cy, cz + 0.025), (0.024, sy, 0.05), mat=mat)
    # cambered glass: two panes each side of a brass ridge, tilted 7 deg
    ang = math.radians(7)
    zr = cz + 0.05
    for sgny in (-1, 1):
        for sgnx in (-1, 1):
            mb.add_box((cx + sgnx * sx * 0.25, cy + sgny * sy * 0.235,
                        zr + 0.018),
                       (sx / 2 - 0.030, sy / 2 - 0.030, 0.006), mat=mat_glass,
                       rot=rot_axis((1, 0, 0), -sgny * ang))
    # ridge + glazing bars
    mb.add_box((cx, cy, zr + 0.031), (sx, 0.018, 0.016), mat=mat_brass,
               chamfer=0.005)
    mb.add_box((cx, cy - sy * 0.48, zr + 0.010), (sx, 0.012, 0.012),
               mat=mat_brass)
    mb.add_box((cx, cy + sy * 0.48, zr + 0.010), (sx, 0.012, 0.012),
               mat=mat_brass)
    mb.add_box((cx, cy, zr + 0.020), (0.014, sy, 0.014), mat=mat_brass,
               rot=rot_axis((1, 0, 0), 0))
    return mb


def ventilator_mushroom(base, r=0.070, h=0.34, mat=10, mat_in=20):
    """Mushroom ventilator on a short coaming: neck, dished cap on three
    legs, red-lead painted underside, crown knob."""
    bx, by, bz = base
    mb = MB("Ventilator")
    cyl(mb, (bx, by, bz - 0.010), (bx, by, bz + 0.005), r * 0.72, seg=14,
        mat=mat)                                   # coaming flange
    cyl(mb, (bx, by, bz), (bx, by, bz + h), r * 0.44, seg=12, mat=mat)
    torus(mb, (bx, by, bz + h), r * 0.44, 0.007, seg=12, rseg=4, axis="Z",
          mat=mat)
    # cap: dished dome, red underneath, held on three legs
    cyl(mb, (bx, by, bz + h + 0.012), (bx, by, bz + h + 0.020), r * 0.98,
        seg=14, mat=mat_in)
    dome(mb, (bx, by, bz + h + 0.030), r, seg=16, rings=6, mat=mat,
         squash=0.45)
    for k in range(3):
        a = math.radians(k * 120 + 30)
        px, py = bx + r * 0.80 * math.cos(a), by + r * 0.80 * math.sin(a)
        cyl(mb, (px, py, bz + h - 0.005), (px, py, bz + h + 0.028), 0.0045,
            seg=6, mat=mat)
    sphere(mb, (bx, by, bz + h + 0.030 + r * 0.45), 0.010, seg=8, rings=5,
           mat=mat)
    return mb


def floor_plates(x0, x1, y_half, z, pw=0.34, mat=26):
    """Chequer-plate steel sole plates through the machinery space."""
    mb = MB("Floor_Plates")
    n = max(1, int((x1 - x0) / pw))
    for i in range(n):
        cx = x0 + (i + 0.5) * (x1 - x0) / n
        mb.add_box((cx, 0, z), ((x1 - x0) / n - 0.012, y_half * 2, 0.007),
                   mat=mat, chamfer=0.004)
    return mb


def engine_guard_rail(x0, x1, y_half, z0, h=0.40, mat=3):
    """Polished brass guard rail around the machinery bay: six stanchions
    with globe tops and two horizontal rails, corners eased."""
    mb = MB("Engine_Guard")
    e = 0.06                                   # corner ease
    per = [(x0 + e, -y_half), (x1 - e, -y_half), (x1, -y_half + e),
           (x1, y_half - e), (x1 - e, y_half), (x0 + e, y_half),
           (x0, y_half - e), (x0, -y_half + e)]
    for zrail in (z0 + h, z0 + h * 0.55):
        pts = [np.array([px, py, zrail]) for px, py in per]
        pts.append(pts[0].copy())
        mb.add_tube(pts, 0.0105, segments=8, mat=mat)
    for px, py in per[::2]:
        cyl(mb, (px, py, z0), (px, py, z0 + h), 0.0085, seg=8, mat=mat)
        sphere(mb, (px, py, z0 + h), 0.013, seg=8, rings=5, mat=mat)
        cyl(mb, (px, py, z0 - 0.004), (px, py, z0 + 0.012), 0.016, seg=10,
            mat=mat)
    return mb


def sidelight_pair(hull):
    """Port/starboard sidelights in brass housings at the bow."""
    mb = MB()
    from .parts2 import sidelight
    xi = 0.07
    t = hull.arc_to_t(xi, 0.90)
    p = hull.section_pt(xi, t, 0.0)
    mb.append(sidelight((p[0], -abs(p[1]) + 0.02, p[2] + 0.10), side="port"))
    mb.append(sidelight((p[0], abs(p[1]) - 0.02, p[2] + 0.10), side="stbd"))
    return mb


def canopy_tracks(hull):
    """Brass awning/carriage grooves along both gunwales for future canopy."""
    mb = MB()
    for sgn in (-1, 1):
        pts = []
        for xi in np.linspace(0.18, 0.86, 20):
            t = hull.arc_to_t(xi, 0.985)
            p = hull.section_pt(xi, t, 0.0)
            pts.append((p[0], sgn * (abs(p[1]) + 0.008), p[2] + 0.020))
        mb.add_tube(pts, 0.010, segments=6, mat=3)
    return mb


def dagger_boards_stowed(center):
    """Two canvas dagger boards (canopy extensions) stowed on the side bench."""
    mb = MB()
    cx, cy, cz = center
    for i, sgn in enumerate((-1, 1)):
        z = cz + i * 0.03
        mb.add_box((cx, cy + sgn * 0.05, z), (1.30, 0.24, 0.028), mat=8, chamfer=0.01)
        # hemming + ties
        for k in range(5):
            x = cx - 0.60 + k * 0.30
            torus(mb, (x, cy + sgn * 0.05, z), 0.145, 0.006, seg=10, rseg=4, axis="Z", mat=7)
    return mb


def engine_bearer(hull, xi0, xi1, width=0.075, top_z=None, mat=2, mat_iron=4):
    """Heavy fore-and-aft machinery bearer: sided 3 in tapered timber sweep laid
    over the keelson, with holding-down bolts through the floors."""
    mb = MB()
    n = 14
    xis = np.linspace(xi0, xi1, n)
    z_top = top_z
    for sgn in (-1, 1):
        for k in range(n - 1):
            xi_a, xi_b = xis[k], xis[k + 1]
            za = hull.section_pt(xi_a, 0.03, -0.005)
            zb = hull.section_pt(xi_b, 0.03, -0.005)
            depth = 0.14 - 0.08 * (k / (n - 2))
            yoff = sgn * (width / 2 + 0.045)
            pA0 = [za[0], yoff, za[2]]
            pA1 = [zb[0], yoff, zb[2]]
            pB0 = [za[0], yoff, za[2] + depth]
            pB1 = [zb[0], yoff, zb[2] + depth]
            g = mb.add_grid(np.array([[pA0, pA1], [pA0, pA1]]), mat)
            mb.add_box(((za[0] + zb[0]) / 2, yoff, (za[2] + zb[2]) / 2 + depth / 2),
                       (abs(zb[0] - za[0]), width, depth + 0.02), mat=mat,
                       chamfer=0.004)
        # bolt heads
        for xi in np.linspace(xi0 + 0.05, xi1 - 0.05, 5):
            p = hull.section_pt(xi, 0.03, -0.005)
            dome(mb, (p[0], sgn * (width / 2 + 0.045), p[2] + 0.15), 0.011, seg=6,
                 rings=3, mat=mat_iron)
    return mb

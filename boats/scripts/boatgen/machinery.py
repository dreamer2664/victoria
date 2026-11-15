"""
machinery.py -- the steam plant of the 25 ft steam cutter.

Every component is modelled where it actually has to be to work:
  * a vertical fire-tube boiler with firebox, grate, fire tubes, smoke box and
    funnel base, riveted shell, safety valve, stop valve, gauge glass, try
    cocks, feed check valve and blow-down;
  * an inverted single-cylinder launch engine: cylinder, piston rod, guide
    bars, crosshead, connecting rod, crankshaft, crank, flywheel, eccentric
    and Stephenson link reversing gear, slide valve in its chest, drain cocks;
  * an inclined propeller shaft with couplings, a stern-tube gland and a
    two-bladed screw;
  * the steam, exhaust and feed pipe runs that actually connect them.

Sizes are those of a small 1880s launch plant: bore 5 1/2 in (140 mm), stroke
6 in (152 mm), about 5 ihp at 350 rpm on 100-120 psi, screw 16 in (0.41 m)
diameter.  These are consistent with the boat's size and with the compound
plant of the surviving Admiralty steam cutters of the 1890s.
"""

from __future__ import annotations

import math

import numpy as np

from .geom import bolt_row, cyl, lerp, sphere, torus, unit
from .hull import MAT

BORE = 0.140
STROKE = 0.152
SCREW_DIA = 0.34


# --------------------------------------------------------------------------
# boiler
# --------------------------------------------------------------------------


def boiler(mb, base, r=0.430, height=1.150, mat=MAT["iron"], copper=MAT["copper"],
           brass=MAT["brass"], steel=MAT["steel"], rivet_mat=MAT["steel"], detail=True):
    """Vertical fire-tube boiler standing on `base` (its bottom centre).

    Drawn as a riveted cylindrical shell with a domed top, a firebox at the
    bottom, a smoke box and funnel spigot at the top, and the usual fittings.
    """
    bx, by, bz = base
    seg = 32
    # ---- shell (with a slight barrel) ----
    prof = []
    n = 14
    for i in range(n + 1):
        f = i / n
        z = f * height
        rr = r * (1.0 - 0.06 * f) + 0.012 * math.sin(f * math.pi)
        prof.append((rr, z))
    mb.add_lathe(prof, segments=seg, center=(bx, by, bz), mat=mat)
    # domed top
    dome = [(r * math.cos(a), height + 0.10 * math.sin(a)) for a in np.linspace(0, math.pi / 2, 8)]
    mb.add_lathe(dome, segments=seg, center=(bx, by, bz), mat=mat)
    # bottom plate + firebox ring
    cyl(mb, (bx, by, bz - 0.02), (bx, by, bz + 0.02), r * 0.98, seg=seg, mat=mat)
    # firebox: a riveted band at the bottom third
    prof2 = [(r * 1.005, 0.06), (r * 1.005, 0.36)]
    mb.add_lathe(prof2, segments=seg, center=(bx, by, bz), mat=mat)
    if detail:
        # riveted seam bands
        for zf in (0.10, 0.34, 0.58, 0.82, 0.97):
            ring = [(bx + r * 1.02 * math.cos(a), by + r * 1.02 * math.sin(a), bz + zf * height)
                    for a in np.linspace(0, 2 * math.pi, 24, endpoint=False)]
            for i in range(len(ring)):
                cyl(mb, ring[i], np.array(ring[i]) + np.array([0, 0, 0.012]), 0.009, seg=6, mat=rivet_mat)
        # vertical seams
        for ang in (0.3, 1.9, 3.4, 5.0):
            for k in range(14):
                zz = bz + 0.05 + k * 0.075
                a = ang
                p = (bx + r * 1.02 * math.cos(a), by + r * 1.02 * math.sin(a), zz)
                cyl(mb, p, np.array(p) + np.array([math.cos(a), math.sin(a), 0]) * 0.010, 0.008,
                    seg=6, mat=rivet_mat)
    # ---- fire door and ashpit door (facing aft, -X) ----
    fd = np.array([bx - r * 0.75, by, bz + 0.26])
    cyl(mb, fd, fd + np.array([-0.09, 0, 0]), 0.135, seg=16, mat=mat, r1=0.125)
    cyl(mb, fd + np.array([-0.10, 0, 0]), fd + np.array([-0.12, 0, 0]), 0.12, seg=16, mat=steel)
    # door hinges & catch
    for dz in (0.11, -0.11):
        cyl(mb, fd + np.array([-0.10, 0.115, dz]), fd + np.array([-0.10, 0.055, dz * 0.9]), 0.010,
            seg=8, mat=steel)
    cyl(mb, fd + np.array([-0.11, -0.10, 0]), fd + np.array([-0.16, -0.10, 0]), 0.012, seg=8, mat=steel)
    cyl(mb, fd + np.array([-0.16, -0.10, -0.07]), fd + np.array([-0.16, -0.10, 0.07]), 0.012, seg=8, mat=steel)
    # ashpit door, lower
    ad = np.array([bx - r * 0.72, by, bz + 0.09])
    cyl(mb, ad, ad + np.array([-0.08, 0, 0]), 0.10, seg=14, mat=mat, r1=0.095)
    # ---- funnel base / smoke box spigot ----
    cyl(mb, (bx, by, bz + height + 0.09), (bx, by, bz + height + 0.20), r * 0.42, seg=20, mat=mat,
        r1=r * 0.40)
    if detail:
        # ---- fittings ----
        # steam stop valve on the dome
        sv = np.array([bx + 0.10, by, bz + height + 0.14])
        cyl(mb, sv, sv + np.array([0, 0, 0.10]), 0.032, seg=12, mat=brass)
        cyl(mb, sv + np.array([0, 0, 0.10]), sv + np.array([0, 0, 0.16]), 0.050, seg=12, mat=brass, r1=0.045)
        torus(mb, sv + np.array([0, 0, 0.17]), 0.055, 0.009, seg=16, rseg=6, mat=brass)
        # safety valve (lever type) on the dome
        saf = np.array([bx - 0.14, by + 0.04, bz + height + 0.12])
        cyl(mb, saf, saf + np.array([0, 0, 0.07]), 0.030, seg=10, mat=brass)
        cyl(mb, saf + np.array([-0.09, 0, 0.085]), saf + np.array([0.09, 0, 0.085]), 0.008, seg=6, mat=brass)
        sphere(mb, saf + np.array([-0.10, 0, 0.085]), 0.026, seg=10, rings=6, mat=brass)
        # pressure gauge on a siphon at the front of the shell
        gp = np.array([bx + r * 0.72, by + 0.10, bz + height * 0.72])
        cyl(mb, gp, gp + np.array([0.10, 0.02, 0.02]), 0.012, seg=8, mat=brass)
        gc = gp + np.array([0.13, 0.03, 0.03])
        cyl(mb, gc, gc + np.array([0.05, 0, 0.0]), 0.052, seg=20, mat=brass)
        cyl(mb, gc + np.array([0.05, 0, 0]), gc + np.array([0.058, 0, 0]), 0.046, seg=20, mat=MAT["glass"])
        # water gauge glass
        for dz in (-0.07, 0.07):
            cyl(mb, np.array([bx - 0.10, by + r * 0.80, bz + height * 0.60 + dz]),
                np.array([bx - 0.10, by + r * 0.86, bz + height * 0.60 + dz]), 0.014, seg=8, mat=brass)
        cyl(mb, np.array([bx - 0.10, by + r * 0.86, bz + height * 0.60 - 0.07]),
            np.array([bx - 0.10, by + r * 0.86, bz + height * 0.60 + 0.07]), 0.011, seg=10, mat=MAT["glass"])
        # try cocks
        for k, dz in enumerate((-0.10, -0.04, 0.02)):
            p = np.array([bx - 0.16, by + r * 0.78, bz + height * 0.42 + dz])
            cyl(mb, p, p + np.array([0, 0.07, 0.02]), 0.010, seg=8, mat=brass)
        # feed check valve
        fv = np.array([bx + r * 0.55, by - 0.16, bz + 0.30])
        cyl(mb, fv, fv + np.array([0.07, 0, 0]), 0.026, seg=10, mat=brass)
        cyl(mb, fv + np.array([0.07, 0, 0]), fv + np.array([0.07, 0, 0.09]), 0.022, seg=10, mat=brass)
        # blow-down cock
        bd = np.array([bx - r * 0.55, by - 0.10, bz + 0.10])
        cyl(mb, bd, bd + np.array([-0.08, 0, -0.02]), 0.020, seg=8, mat=brass)
    return {"top": np.array([bx, by, bz + height + 0.20]), "base": np.array(base)}


def boiler_cutaway(mb, base, r=0.430, height=1.150, mat=MAT["red_lead"], firebox=MAT["iron"],
                   tube=MAT["copper"]):
    """Internal parts, modelled so the cutaway render shows a real boiler:
    grate, firebox, tube plate, fire tubes, and the water space."""
    bx, by, bz = base
    # grate (bars)
    for i in range(9):
        y = by - 0.22 + i * 0.055
        cyl(mb, (bx - 0.26, y, bz + 0.30), (bx + 0.26, y, bz + 0.30), 0.011, seg=6, mat=firebox)
    # firebox walls
    prof = [(0.30, 0.10), (0.30, 0.38)]
    mb.add_lathe(prof, segments=20, center=(bx, by, bz), mat=firebox)
    # tube plate
    cyl(mb, (bx, by, bz + 0.46), (bx, by, bz + 0.50), 0.34, seg=20, mat=firebox)
    # fire tubes (two rows of small tubes)
    for a in np.linspace(0, 2 * math.pi, 8, endpoint=False):
        x = bx + 0.20 * math.cos(a)
        y = by + 0.20 * math.sin(a)
        cyl(mb, (x, y, bz + 0.50), (x, y, bz + 0.92), 0.028, seg=8, mat=tube)
    for a in np.linspace(0, 2 * math.pi, 4, endpoint=False):
        x = bx + 0.06 * math.cos(a)
        y = by + 0.06 * math.sin(a)
        cyl(mb, (x, y, bz + 0.50), (x, y, bz + 0.92), 0.022, seg=8, mat=tube)


# --------------------------------------------------------------------------
# engine
# --------------------------------------------------------------------------


def engine(mb, origin, bore=BORE, stroke=STROKE, mat=MAT["iron"], brass=MAT["brass"],
           steel=MAT["steel"], copper=MAT["copper"], detail=True):
    """Inverted single-cylinder launch engine driving a longitudinal shaft.

    Layout (local coordinates relative to `origin`, the centre of the
    crankshaft, +X forward, +Z up):
        crank case / bedplate at the bottom, cylinder overhead on four
        columns, crosshead guides, connecting rod down to the crank pin,
        flywheel on the shaft, Stephenson link reversing gear outboard.
    """
    ox, oy, oz = origin
    R = stroke * 0.5
    cyl_h = 0.30
    # ---- bedplate ----
    mb.add_box((ox, oy, oz - R - 0.10), (0.66, 0.44, 0.055), mat=mat)
    for sx in (-0.26, 0.26):
        for sy in (-0.17, 0.17):
            mb.add_box((ox + sx, oy + sy, oz - R - 0.06), (0.09, 0.09, 0.09), mat=mat)
    # ---- columns carrying the cylinder ----
    for sx in (-0.20, 0.20):
        for sy in (-0.13, 0.13):
            cyl(mb, (ox + sx, oy + sy, oz - R - 0.04), (ox + sx, oy + sy, oz + 0.24), 0.017,
                seg=8, mat=mat)
    # ---- cylinder ----
    cz = oz + 0.35
    cyl(mb, (ox, oy, cz - cyl_h * 0.5), (ox, oy, cz + cyl_h * 0.5), bore * 0.5 + 0.028, seg=26,
        mat=mat)
    # cylinder covers with studs and nuts
    for zz in (cz - cyl_h * 0.5 - 0.015, cz + cyl_h * 0.5 + 0.015):
        cyl(mb, (ox, oy, zz - 0.012), (ox, oy, zz + 0.012), bore * 0.5 + 0.055, seg=26, mat=mat)
    if detail:
        for a in np.linspace(0, 2 * math.pi, 12, endpoint=False):
            p = np.array([ox + (bore * 0.5 + 0.042) * math.cos(a),
                          oy + (bore * 0.5 + 0.042) * math.sin(a), cz + cyl_h * 0.5 + 0.03])
            cyl(mb, p, p + np.array([0, 0, 0.012]), 0.007, seg=6, mat=steel)
    # piston rod + crosshead
    mb.add_box((ox, oy, cz - cyl_h * 0.5 - 0.10), (0.030, 0.030, 0.22), mat=steel)
    chz = oz + 0.08
    mb.add_box((ox, oy, chz), (0.075, 0.075, 0.055), mat=steel)
    # guide bars
    for sy in (-0.055, 0.055):
        mb.add_box((ox, oy + sy, chz + 0.075), (0.030, 0.020, 0.20), mat=steel)
    # ---- crankshaft along X ----
    for sgn in (-1, 1):
        cyl(mb, (ox + sgn * 0.10, oy, oz), (ox + sgn * 0.34, oy, oz), 0.020, seg=12, mat=steel)
    # crank webs and pin
    mb.add_box((ox - 0.055, oy, oz - R * 0.5), (0.055, 0.024, R + 0.045), mat=steel)
    mb.add_box((ox + 0.055, oy, oz - R * 0.5), (0.055, 0.024, R + 0.045), mat=steel)
    pin_z = oz - R
    cyl(mb, (ox - 0.06, oy - 0.035, pin_z), (ox + 0.06, oy - 0.035, pin_z), 0.019, seg=10, mat=steel)
    # connecting rod: crank pin -> crosshead
    mb.add_tube(np.array([[ox, oy - 0.035, pin_z], [ox, oy - 0.035, (pin_z + chz) * 0.5],
                          [ox, oy - 0.035, chz]]), 0.013, segments=8, mat=steel)
    mb.add_box((ox, oy - 0.035, pin_z), (0.055, 0.026, 0.055), mat=brass)
    # ---- flywheel (transverse plane) ----
    fw_x = ox - 0.30
    mb.add_lathe([(0.055, fw_x - 0.018), (0.245, fw_x - 0.018), (0.245, fw_x + 0.018),
                  (0.055, fw_x + 0.018)], segments=26, axis="X", center=(0, oy, oz), mat=mat)
    if detail:
        # spokes
        for a in np.linspace(0, 2 * math.pi, 6, endpoint=False):
            p0 = np.array([fw_x, oy, oz])
            p1 = np.array([fw_x, oy + 0.20 * math.cos(a), oz + 0.20 * math.sin(a)])
            cyl(mb, p0, p1, 0.012, seg=6, mat=mat)
    # ---- Stephenson link reversing gear ----
    ecc_x = ox + 0.26
    cyl(mb, (ecc_x, oy + 0.075, oz), (ecc_x, oy + 0.115, oz), 0.048, seg=16, mat=steel)
    # link (curved slotted arm) approximated by a bar
    mb.add_box((ecc_x, oy + 0.15, oz + 0.09), (0.028, 0.024, 0.20), mat=steel)
    # reversing lever in the boat's cockpit
    cyl(mb, (ecc_x, oy + 0.16, oz + 0.19), (ecc_x, oy + 0.30, oz + 0.55), 0.012, seg=8, mat=steel)
    sphere(mb, (ecc_x - 0.015, oy + 0.31, oz + 0.57), 0.026, seg=10, rings=6, mat=brass)
    # valve chest and slide valve gear
    vc = np.array([ox, oy + 0.115, cz + 0.02])
    mb.add_box(vc, (0.15, 0.10, 0.20), mat=mat)
    cyl(mb, vc + np.array([0, 0.05, 0.11]), vc + np.array([0, 0.05, 0.16]), 0.016, seg=8, mat=brass)
    # eccentric rod from the sheave up to the valve spindle
    mb.add_tube(np.array([[ecc_x, oy + 0.115, oz], [ecc_x, oy + 0.145, oz + 0.22],
                          [ox, oy + 0.155, oz + 0.30]]), 0.010, segments=8, mat=steel)
    # drain cocks on the cylinder
    for sy in (-1, 1):
        p = np.array([ox + 0.02, oy + sy * (bore * 0.5 + 0.03), cz - cyl_h * 0.5 + 0.02])
        cyl(mb, p, p + np.array([0, sy * 0.05, -0.02]), 0.010, seg=8, mat=brass)
    # lubricator cups
    for sy in (-0.06, 0.06):
        p = np.array([ox, oy + sy, cz + cyl_h * 0.5 + 0.03])
        cyl(mb, p, p + np.array([0, 0, 0.05]), 0.014, seg=8, mat=brass)
        sphere(mb, p + np.array([0, 0, 0.062]), 0.018, seg=8, rings=6, mat=MAT["glass"])
    return {"shaft_z": oz, "crank_x": ox}


# --------------------------------------------------------------------------
# shafting, propeller, rudder
# --------------------------------------------------------------------------


def shaft_line(mb, p0, p1, r=0.024, mat=MAT["steel"], couplings=(0.25, 0.75)):
    p0 = np.asarray(p0, dtype=float)
    p1 = np.asarray(p1, dtype=float)
    cyl(mb, p0, p1, r, seg=14, mat=mat)
    for f in couplings:
        c = lerp(p0, p1, f)
        d = unit(p1 - p0)
        cyl(mb, c - d * 0.012, c + d * 0.012, r * 2.1, seg=14, mat=mat)


def stern_tube(mb, p0, p1, r=0.045, mat=MAT["iron"], brass=MAT["brass"]):
    p0 = np.asarray(p0, dtype=float)
    p1 = np.asarray(p1, dtype=float)
    cyl(mb, p0, p1, r, seg=14, mat=mat)
    d = unit(p1 - p0)
    for f in (0.0, 0.45):
        c = lerp(p0, p1, f)
        cyl(mb, c - d * 0.03, c + d * 0.035, r * 0.72, seg=14, mat=brass)


def propeller(mb, hub, shaft_dir=(1, 0, 0), dia=SCREW_DIA, blades=2, mat=MAT["brass"],
              blade_mat=MAT["brass"]):
    """Screw propeller: boss, two cast blades with helical pitch and a slight
    skew, plus the retaining nut.  Local origin at the boss centre; the blades
    lie in the plane normal to `shaft_dir`."""
    hub = np.asarray(hub, dtype=float)
    d = unit(np.asarray(shaft_dir, dtype=float))
    a = unit(np.cross(d, [0, 1.0, 0])) if abs(d[1]) < 0.9 else unit(np.cross(d, [1.0, 0, 0]))
    b = np.cross(d, a)
    # boss
    cyl(mb, hub - d * 0.045, hub + d * 0.045, 0.045, seg=16, mat=mat, r1=0.038)
    cyl(mb, hub + d * 0.045, hub + d * 0.062, 0.028, seg=12, mat=mat, r1=0.022)  # nut
    for k in range(blades):
        ang = 2 * math.pi * k / blades + 0.35
        radial = math.cos(ang) * a + math.sin(ang) * b
        tangent = -math.sin(ang) * a + math.cos(ang) * b
        # blade: lofted sections along the radius with a helical twist
        n = 7
        grid = np.zeros((n, 5, 3))
        for i in range(n):
            f = i / (n - 1)
            r = lerp(0.048, dia * 0.5, f)
            chord = lerp(0.10, 0.135, math.sin(f * math.pi * 0.8))
            thick = lerp(0.020, 0.008, f)
            twist = math.radians(38 + 16 * f)          # blade angle, coarser at the root
            for j, (cu, cv) in enumerate(((-0.5, 0.0), (-0.28, 0.5), (0.0, 1.0), (0.28, 0.5), (0.5, 0.0))):
                # chord runs fore-and-aft (along d), thickness across the tangent
                p = (hub + radial * r
                     + d * (cu * chord * math.cos(twist))
                     + tangent * (cu * chord * math.sin(twist))
                     + d * 0.0
                     + (radial * 0 + tangent * 0)
                     + (d * math.cos(twist) * 0)
                     )
                p = p + (math.sin(twist) * (cv * thick * 0.5)) * (-d) + (cv * thick * 0.5) * math.cos(twist) * tangent
                grid[i, j] = p
        mb.add_grid(grid, blade_mat)
        mb.add_grid(grid[:, ::-1], blade_mat)


def rudder_steam(mb, hull, length=0.85, width=0.36, mat=MAT["iron"], steel=MAT["steel"]):
    """Rudder for the steam cutter: a steel plate rudder hung on the sternpost,
    with tiller.  Built in world coordinates (hull included for the pivot)."""
    pass  # implemented in the build script where the geometry is known


def pipe_run(mb, pts, r=0.014, mat=MAT["copper"], flange_mat=MAT["brass"], lagging=False):
    pts = np.array(pts, dtype=float)
    mb.add_tube(pts, r, segments=10, mat=mat, caps=True)
    for p in (pts[0], pts[-1]):
        cyl(mb, p, p + unit(pts[-1] - pts[0]) * 0.02, r * 1.9, seg=10, mat=flange_mat)


def valve(mb, pos, direction=(0, 0, 1), size=1.0, mat=MAT["brass"], wheel=True):
    p = np.asarray(pos, dtype=float)
    d = unit(direction)
    cyl(mb, p, p + d * 0.05 * size, 0.028 * size, seg=12, mat=mat)
    cyl(mb, p + d * 0.05 * size, p + d * 0.075 * size, 0.040 * size, seg=12, mat=mat)
    if wheel:
        c = p + d * 0.10 * size
        n1 = unit(np.cross(d, [0, 1.0, 0])) if abs(d[1]) < 0.9 else unit(np.cross(d, [1.0, 0, 0]))
        n2 = np.cross(d, n1)
        pts = [c + 0.045 * size * (math.cos(a) * n1 + math.sin(a) * n2)
               for a in np.linspace(0, 2 * math.pi, 15)]
        mb.add_tube(np.array(pts), 0.006 * size, segments=6, mat=mat, caps=False)
        for a in np.linspace(0, 2 * math.pi, 4, endpoint=False):
            cyl(mb, c, c + 0.045 * size * (math.cos(a) * n1 + math.sin(a) * n2), 0.005 * size,
                seg=6, mat=mat)


def gauge(mb, pos, normal=(1, 0, 0), face=0.055, mat=MAT["brass"]):
    p = np.asarray(pos, dtype=float)
    d = unit(normal)
    cyl(mb, p, p + d * 0.035, face, seg=20, mat=mat)
    cyl(mb, p + d * 0.035, p + d * 0.043, face * 0.85, seg=20, mat=MAT["glass"])
    # bezel
    torus(mb, p + d * 0.040, face * 0.9, 0.006, seg=20, rseg=5, mat=mat)


def whistle(mb, pos, direction=(0, 1, 0), mat=MAT["brass"]):
    p = np.asarray(pos, dtype=float)
    d = unit(direction)
    cyl(mb, p, p + d * 0.03, 0.026, seg=12, mat=mat)
    cyl(mb, p + d * 0.03, p + d * 0.10, 0.030, seg=12, mat=mat)
    cyl(mb, p + d * 0.10, p + d * 0.12, 0.034, seg=12, mat=mat)


def funnel(mb, base, top_z, r_bottom=0.088, r_top=0.105, mat=MAT["iron"], band=MAT["brass"],
           rake_x=0.10, stays=True):
    """Short raked funnel with a brass band and a wire stay."""
    bx, by, bz = base
    top = np.array([bx + rake_x, by, top_z])
    bot = np.array([bx, by, bz])
    cyl(mb, bot, top, r_bottom, seg=20, mat=mat, r1=r_top)
    torus(mb, top - np.array([0.01, 0, 0.03]), r_top * 1.02, 0.012, seg=20, rseg=6, mat=band)
    # collar at the deck
    cyl(mb, bot + np.array([0, 0, -0.02]), bot + np.array([0, 0, 0.05]), r_bottom * 1.35, seg=20, mat=mat)
    if stays:
        for sy in (-1, 1):
            p0 = bot + np.array([0, sy * r_bottom * 0.9, 0.12])
            p1 = np.array([top[0] - 0.02, top[1] + sy * r_top * 0.9, top_z - 0.16])
            # a stay would foul the canopy; the funnel is stayed to the canopy
            # frame instead -- modelled as a clamp band
            torus(mb, lerp(p0, p1, 0.55), r_top * 1.06, 0.008, seg=16, rseg=5, mat=band)

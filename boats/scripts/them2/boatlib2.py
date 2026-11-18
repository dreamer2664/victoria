"""
boatlib2.py -- shared placement logic: thwarts, rowlocks, oar stowage,
benches, gratings, sailing rig (stowed), and the standard boat's gear set.

All functions take the Hull2 design object and return (MB, info dict)/objects.
"""
from __future__ import annotations
import math
import numpy as np
from .geom2 import (MB, unit, lerp, clamp, cyl, sphere, dome, torus, rivet_row,
                    rot_x, rot_y, rot_z, rot_axis, superellipse_section)
from . import structure2 as st
from . import parts2 as P

X = np.array([1.0, 0, 0]); Y = np.array([0.0, 1, 0]); Z = np.array([0.0, 0, 1.0])


def z_at_arc(hull, xi, f_arc, off=0.0):
    t = hull.arc_to_t(xi, f_arc)
    return hull.section_pt(xi, t, off)


def thwart_layout(hull, stations_x, z_top=0.145, thk=0.028, width=0.24,
                  mat=0, mat_knee=2):
    """Thwarts spanning the planking with rounded ends and hanging knees."""
    mb = MB("Thwarts")
    knees = MB("Thwart_Knees")
    risers = MB("Risers")
    lay = []
    for xs in stations_x:
        xi = clamp((hull.loa / 2 - xs) / hull.loa, 0.02, 0.98)
        # width of inside planking at z_top
        dep = hull.depth(xi)
        t = clamp((z_top - hull.keel_z(xi)) / dep, 0.05, 0.95)
        pin = hull.section_pt(xi, t, -0.060)
        hw = abs(pin[1]) - 0.01
        w2 = width / 2
        outl = [(-hw + 0.04, -w2), (hw - 0.04, -w2)]
        for k in range(5):
            a = k / 4 * math.pi / 2
            outl.append((hw - 0.04 + 0.04 * math.cos(a), w2 - 0.04 + 0.04 * math.sin(a)))
        outl.append((-hw + 0.04, w2))
        for k in range(5):
            a = k / 4 * math.pi / 2
            outl.append((-hw + 0.04 - 0.04 * math.cos(a), -w2 + 0.04 * math.cos(math.pi / 2 - a)))
        mb.add_plate(outl, thk, plane="XY", origin=(xs, 0, z_top - thk), mat=mat)
        # edge moulding strip on the thwart face
        for sgn in (-1, 1):
            cyl(mb, (xs - hw + 0.02, sgn * w2, z_top - 0.002),
                (xs + hw - 0.02, sgn * w2, z_top - 0.002), 0.005, seg=8, mat=mat_knee,
                caps=True)
        # riser strips under the ends (fastened inside frames)
        for sgn in (-1, 1):
            rn = MB()
            t_in = t
            p0 = hull.section_pt(xi - 0.10, t_in, -0.058)
            p1 = hull.section_pt(xi + 0.10, t_in, -0.058)
            y0 = sgn * abs(p0[1]); y1 = sgn * abs(p1[1])
            risers.add_box(((p0[0] + p1[0]) / 2, (y0 + y1) / 2, z_top - 0.028),
                           (0.28, 0.016, 0.050), mat=mat_knee, chamfer=0.004)
            # hanging knee: standing arm under thwart + hanging leg down the side
            y_edge = sgn * (hw - 0.10)
            out = [(y_edge, 0.0), (y_edge - sgn * 0.20, 0.0),
                   (y_edge - sgn * 0.20, -0.05),
                   (y_edge - sgn * 0.08, -0.10),
                   (y_edge - sgn * 0.03, -0.28), (y_edge - sgn * 0.07, -0.28),
                   (y_edge - sgn * 0.11, -0.08), (y_edge, -0.05)]
            kb = MB()
            kb.add_plate(out, 0.028, origin=(xs - 0.014, 0, z_top - thk - 0.004),
                         mat=mat_knee, basis=(Y, Z, X))
            knees.append(kb)
        lay.append({"x": xs, "z": z_top, "half_w": hw, "xi": xi})
    return {"thwarts": mb, "knees": knees, "risers": risers, "layout": lay}


def rowlocks(hull, stations_x, z_pad, sides=(-1, 1), mat_socket=3, mat_crutch=5):
    """Swivel rowlocks screwed to pads on the gunwale cap at each station."""
    mb = MB("Rowlocks")
    pivots = []
    for xs in stations_x:
        xi = clamp((hull.loa / 2 - xs) / hull.loa, 0.0, 1.0)
        t = hull.arc_to_t(xi, 0.995)
        p = hull.section_pt(xi, t, 0.0)
        for sgn in sides:
            # throat position on the gunwale top, centred for the crutch fork
            y = sgn * (abs(p[1]) + 0.004)
            zt = p[2] + 0.052
            # pivot (oar bearing) at the crutch throat: between the horns
            pivots.append({"x": xs, "y": y, "z": zt, "side": sgn,
                           "pos": np.array([xs, y, zt])})
            sp = P.rowlock_crutch((xs, y, p[2] + 0.030), mat_socket=mat_socket,
                                  mat_crutch=mat_crutch)
            mb.append(sp)
    return mb, pivots


def build_oar_set(hull, pivots, length=3.66, inboard_frac=0.34, stow_z=None,
                  mat_wood=0):
    """
    Full set of oars, STOWED fore-and-aft in the boat (davit condition):
    handles on the thwarts forward, blades over the after benches.  Object
    origin stays at the rowlock pivot for animation; returns per-oar MBs and
    pivots.
    """
    oars = []
    for i, piv in enumerate(pivots):
        oar, gear = P.oar_builder(length=length, inboard_frac=inboard_frac,
                                  mat_wood=mat_wood)
        sgn = piv["side"]
        # rotation: +Y (oar outboard) -> -X (blade aft): R_z(+90 deg)
        R = rot_z(math.pi / 2)
        inb = length * inboard_frac
        rest_z = stow_z if stow_z is not None else 0.16
        # stow position: handle fwd, stacked in alternating layers by row
        layer = piv["side"]  # port/starboard stacks sit slightly apart
        slot = (i % 5)
        dx = 0.12 * ((slot) % 2)     # tiny fan between adjacent oars
        pivot_world = np.array([piv["x"], piv["y"], piv["z"]])
        # stowed origin in boat coords: handle rests on/forward of the thwart
        # ahead of its rowlock; blade tip must stay aboard (stern bench).
        loa = getattr(hull, "loa", 7.6)
        sx = piv["x"] + 0.50 - inb
        sx = max(sx, (-loa / 2 + 0.25) + (length - inb))   # keep blade tip fwd of stern
        sx = min(sx, (loa / 2 - 0.20) - inb)               # keep handle tip aft of bow
        stow = np.array([sx + dx,
                         sgn * min(abs(piv["y"]) - 0.42, 0.25 + 0.05 * slot),
                         rest_z])
        merged = MB("Oar")
        merged.append(oar, offset=stow, rot=R)
        merged.append(gear, offset=stow, rot=R)

        oars.append({"mb": merged, "pivot": pivot_world, "side": sgn,
                     "station_x": piv["x"]})
    return oars


def rigging_stowed(hull, specs, mat_spar=24, mat_canvas=8, mat_rope=7):
    """
    Two- or three-spar dipping lug rig carried stowed in the boat (davit
    condition): masts, lug yards with furled sails (canvas bundles lashed with
    gaskets), and a boom for the main.  Laid fore-and-aft on the thwarts.
    Returns list of MBs.
    """
    out = []
    loa = hull.loa
    zl = 0.24
    # --- masts (tapered poles, leathered at the partners) -------------------
    for (lbl, xl, ll, rr) in specs.get("masts", []):
        mb = MB("Mast_" + lbl)
        p0 = np.array([xl - ll * 0.45, 0.10 if "main" in lbl else -0.06, zl])
        p1 = np.array([xl + ll * 0.55, 0.10 if "main" in lbl else -0.06, zl])
        if xl - ll * 0.45 < -loa / 2 + 0.2:
            p0[0] = -loa / 2 + 0.2
            p1[0] = p0[0] + ll
        mb.add_tube([p0, p1], rr, segments=12, mat=mat_spar,
                    radii=[rr * (1.0 - 0.45 * i / 11) for i in range(12)])
        # leather bands
        for fr in (0.52, 0.62):
            pc = lerp(p0, p1, fr)
            cyl(mb, pc - X * 0.02, pc + X * 0.02, rr * 1.05, seg=10, mat=6)
        sphere(mb, p1, rr * 0.62, seg=8, rings=5, mat=mat_spar)
        out.append(mb)
    # --- yards with furled sails --------------------------------------------
    for (lbl, yl, rr, sail_h) in specs.get("yards", []):
        mb = MB("Yard_" + lbl)
        x_mid = specs.get("yard_x", 0.0) + (0.10 if "fore" in lbl else 0.0)
        p0 = np.array([x_mid - yl / 2, 0.02 if "main" in lbl else -0.10, zl + 0.07])
        p1 = np.array([x_mid + yl / 2, 0.02 if "main" in lbl else -0.10, zl + 0.07])
        mb.add_tube([p0, p1], rr, segments=10, mat=mat_spar,
                    radii=[rr * (1.0 - 0.4 * i / 11) for i in range(12)])
        # furled sail: canvas sausage hugging the yard with slight sags
        n = 16
        rad = []
        for i in range(n):
            s = i / (n - 1)
            rad.append(0.055 * (0.82 + 0.35 * math.sin(s * math.pi)))
        path = []
        for i in range(n):
            s = i / (n - 1)
            sag = 0.03 * math.sin(s * math.pi) * (1 + 0.4 * math.sin(s * 6))
            path.append(lerp(p0, p1, s) + np.array([0, 0, -rr - rad[i] + 0.012 - sag * 0.3]))
        mb.add_tube(path, 1.0, segments=10, radii=rad, mat=mat_canvas)
        # gaskets (stops) around the bundle
        for fr in np.linspace(0.08, 0.92, 7):
            pc = lerp(p0, p1, fr)
            rr2 = rad[min(n - 1, int(fr * (n - 1)))]
            torus(mb, (pc[0], pc[1], pc[2]), rr2 * 1.0, 0.006, seg=12, rseg=4,
                  axis="X", mat=mat_rope)
            mb.add_tube([pc + np.array([0, 0, -rr2 - 0.02]),
                         pc + np.array([0, 0.05, -rr2 - 0.10])], 0.005, segments=6,
                        mat=mat_rope)
        # peak and tack lacing eyes
        for fr, en in ((0.05, -1), (0.95, 1)):
            pc = lerp(p0, p1, fr)
            cyl(mb, pc - X * 0.015, pc + X * 0.015, rr * 1.1, seg=8, mat=6)
        out.append(mb)
    return out


def lifting_eyes(hull, xs_list, z, mat=5):
    """Forged galvanised lifting eyes through-bolted to the keelson."""
    mb = MB("Lifting_Eyes")
    for xs in xs_list:
        cyl(mb, (xs, 0, z - 0.16), (xs, 0, z + 0.02), 0.014, seg=10, mat=mat)
        torus(mb, (xs, 0, z + 0.055), 0.045, 0.013, seg=14, rseg=7, axis="Y", mat=mat)
        cyl(mb, (xs - 0.02, 0, z - 0.165), (xs + 0.02, 0, z - 0.165), 0.026, seg=10,
            mat=mat)
        for sgn in (-1, 1):
            dome(mb, (xs + sgn * 0.026, 0, z - 0.165), 0.013, seg=8, rings=4, mat=mat,
                 squash=0.4, up=X * sgn)
    return mb


def standard_gear(hull, kind="rowing"):
    """
    The boat's loose gear, per the HMS Bombay model outfit list:
    painter, anchors/grapnel, fenders, boat hooks, baler, bucket, breaker.
    Returns list of (name, MB).
    """
    loa = hull.loa
    zfloor = hull.keel_z(0.5) + 0.14
    gear = []
    gear.append(("Painter", P.painter_coil((loa / 2 - 0.75, 0.20, zfloor + 0.10))))
    if kind == "rowing":
        gear.append(("Grapnel", P.grapnel((-loa / 2 + 0.95, -0.30, zfloor + 0.02),
                                          s=0.95)))
    else:
        gear.append(("Anchor", P.stocked_anchor((-loa / 2 + 1.05, -0.30, zfloor),
                                                scale=0.9)))
    # fenders hung outside the gunwale (stowed alongside on both beams)
    fends = MB("Fenders")
    for i, xf in enumerate((loa * 0.28, loa * 0.02, -loa * 0.24)):
        for sgn in (-1, 1):
            xi = clamp((loa / 2 - xf) / loa, 0.0, 1.0)
            t = hull.arc_to_t(xi, 0.995)
            p = hull.section_pt(xi, t, 0.0)
            f = P.fender((xf, sgn * (abs(p[1]) + 0.06), p[2] + 0.02))
            fends.append(f)
    gear.append(("Fenders", fends))
    # boat hooks laid along the side benches
    bh = MB("BoatHooks")
    for i, sgn in enumerate((-1, 1)):
        b = P.boat_hook((0.2, sgn * 0.42, zfloor + 0.06 + 0.03 * i), length=loa * 0.62,
                        along=X)
        bh.append(b)
    gear.append(("BoatHooks", bh))
    gear.append(("Baler", P.baler((-loa / 4, 0.28, zfloor + 0.09))))
    gear.append(("Bucket", P.bucket((-loa / 4 + 0.3, -0.22, zfloor))))
    gear.append(("Breaker", P.breaker((0.45, 0.0, zfloor + 0.14), r=0.115, l=0.38)))
    return gear


def side_bench_pair(hull, at_stern=True, z=0.30, width=0.30, thk=0.025,
                    xi_range=(0.02, 0.20), mat=0):
    """Stern or bow sheets: side benches along the inside, thwart-ship knees."""
    mb = MB("SideBenches")
    supports = MB("Bench_Knees")
    n = 24
    xis = np.linspace(xi_range[0], xi_range[1], n)
    for side in (-1, 1):
        grid = np.zeros((n, 2, 3))
        for i, xi in enumerate(xis):
            dep = hull.depth(xi)
            t = clamp((z - hull.keel_z(xi)) / dep, 0.1, 0.9)
            pin = hull.section_pt(xi, t, -0.056)
            yin = abs(pin[1])
            grid[i, 0] = [pin[0], side * (yin - width), z]
            grid[i, 1] = [pin[0], side * yin, z]
        bo = mb.add_grid(grid, mat)
        grid_d = grid.copy(); grid_d[:, :, 2] -= thk
        bi = mb.add_grid(grid_d, mat)
        for i in range(n - 1):
            mb.add_face([bo + i * 2, bi + i * 2, bi + (i + 1) * 2, bo + (i + 1) * 2], mat)
            mb.add_face([bo + (i + 1) * 2 + 1, bi + (i + 1) * 2 + 1, bi + i * 2 + 1,
                         bo + i * 2 + 1], mat)
        mb.add_face([bo, bi, bi + 1, bo + 1], mat)
        b0 = bo + (n - 1) * 2; b1 = bi + (n - 1) * 2
        mb.add_face([b0, b1, b1 + 1, b0 + 1], mat)
        # support knees every ~0.35 m
        for xs in np.linspace(hull.X(xi_range[1]) + 0.15, hull.X(xi_range[0]) - 0.15,
                              max(2, int(abs(xi_range[1] - xi_range[0]) * hull.loa / 0.35))):
            xi = clamp((hull.loa / 2 - xs) / hull.loa, 0.0, 1.0)
            dep = hull.depth(xi)
            t = clamp((z - hull.keel_z(xi)) / dep, 0.1, 0.9)
            pin = hull.section_pt(xi, t, -0.055)
            yin = abs(pin[1])
            out = [(side * yin, 0.0), (side * (yin - width * 0.8), 0.0),
                   (side * (yin - width * 0.8), -0.05), (side * (yin - 0.1), -0.12),
                   (side * (yin - 0.06), -0.20), (side * yin, -0.16)]
            supports.add_plate(out, 0.024, origin=(xs - 0.012, 0, z - thk),
                               mat=mat, basis=(Y, Z, X))
    return mb, supports


def mast_step_clamp(hull, x_step, z_kelson, thwart_x=None, mat_iron=4, mat_wood=2):
    """Mast step (wood block with socket on the keelson) + iron half-band mast
    clamp on the bow thwart."""
    mb = MB("Mast_Fit")
    mb.add_box((x_step, 0, z_kelson + 0.05), (0.20, 0.16, 0.10), mat=mat_wood,
               chamfer=0.006)
    cyl(mb, (x_step, 0, z_kelson + 0.09), (x_step, 0, z_kelson + 0.11), 0.035,
        seg=12, mat=mat_wood)
    if thwart_x is not None:
        # iron clamp band on the thwart face: half ring + two screw lugs
        zc = 0.10 + 0.01
        pts = []
        for i in range(9):
            a = math.pi - math.pi * i / 8
            pts.append([thwart_x + 0.02 * math.cos(a), 0.0, zc + 0.05 * math.sin(a) * 1.0])
        # clamp stands proud of the thwart's forward face
        pts = [[p[0], -0.125, p[2] + 0.06] for p in pts]
        mb.add_tube(pts, 0.009, segments=8, mat=mat_iron, caps=False, oval=(1.6, 1.0))
        for sgn in (-1, 1):
            mb.add_box((thwart_x + sgn * 0.035, -0.122, zc + 0.055), (0.05, 0.016, 0.035),
                       mat=mat_iron, chamfer=0.003)
    return mb

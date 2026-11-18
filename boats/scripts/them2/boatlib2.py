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


def _inner_y(hull, xi, z, off):
    """Half-breadth of the surface `off` (outward m) at height z, station xi."""
    dep = hull.depth(xi)
    t = clamp((z - hull.keel_z(xi)) / dep, 0.0, 1.0)
    return abs(hull.section_pt(xi, t, off)[1])


def thwart_layout(hull, stations_x, z_top=0.145, thk=0.028, width=0.24,
                  mat=0, mat_knee=2, frame_face=-0.050):
    """Thwarts spanning the boat athwartships, landing on risers, with grown
    hanging knees whose legs follow the planking down.

    GEN-1 corrections (THEMISTOCLES-III):
    * the plate outline is (athwartships, fore-and-aft); it used to be built
      in default XY, so every 'thwart' lay fore-and-aft and the five of them
      overlapped down the boat as one long board (the black cockpit slots);
    * the thwart ends now reach the frame faces and BEAR on the risers
      (they used to stop 4 mm short, beside the riser, carried by nothing);
    * the knee leg follows the inside of the planking (it used to hang
      130-210 mm inboard of the side, in mid air).
    `frame_face`: outward offset of the inboard face of the timbers.
    """
    mb = MB("Thwarts")
    knees = MB("Thwart_Knees")
    risers = MB("Risers")
    lay = []
    # explicit, right-handed plate basis: u = athwartships (+Y),
    # v = fore-and-aft (-X), thickness = +Z   (Y x -X = +Z)
    TB = (Y, -X, Z)
    for xs in stations_x:
        xi = clamp((hull.loa / 2 - xs) / hull.loa, 0.02, 0.98)
        zb = z_top - thk
        hw = min(_inner_y(hull, xi, zb, frame_face),
                 _inner_y(hull, xi, z_top, frame_face)) + 0.004
        w2 = width / 2
        r = 0.035
        outl = [(-hw, -w2 + r), (-hw + r, -w2), (hw - r, -w2), (hw, -w2 + r),
                (hw, w2 - r), (hw - r, w2), (-hw + r, w2), (-hw, w2 - r)]
        mb.add_plate(outl, thk, origin=(xs, 0, zb), mat=mat, basis=TB)
        # rounded edge mouldings along the fore and after edges (athwartships)
        for sgn in (-1, 1):
            cyl(mb, (xs + sgn * w2, -hw + 0.03, z_top - 0.006),
                (xs + sgn * w2, hw - 0.03, z_top - 0.006), 0.006, seg=8, mat=mat,
                caps=True)
        for sgn in (-1, 1):
            # riser: a fore-and-aft strip on the frame faces, its top at the
            # thwart's underside, so the thwart end rests on it
            rh, rt = 0.050, 0.018
            xa, xb = xs - 0.30, xs + 0.30
            # GEN-1: the riser follows the frame faces in 0.10 m lengths --
            # as two straight 0.3 m boxes its forward end stood out through
            # the planking where the bow narrows.
            segs = np.linspace(xa, xb, 7)
            for (x0, x1) in zip(segs[:-1], segs[1:]):
                xm = (x0 + x1) / 2
                ys = []
                for xx in (x0, x1):
                    xim = clamp((hull.loa / 2 - xx) / hull.loa, 0.0, 1.0)
                    ys.append(min(_inner_y(hull, xim, zb - rh, frame_face),
                                  _inner_y(hull, xim, zb, frame_face)))
                yf = min(ys)
                risers.add_box((xm, sgn * (yf - rt / 2 + 0.002), zb - rh / 2),
                               (x1 - x0 + 0.002, rt, rh), mat=mat_knee, chamfer=0.003)
            # hanging knee in the athwartships plane at the thwart's centre:
            # arm under the thwart, throat, leg down the inside of the planking
            leg = 0.26
            zs = np.linspace(zb, zb - leg, 7)
            side = [(_inner_y(hull, xi, z, frame_face - 0.018) , z) for z in zs]
            arm = 0.22
            prof = []
            prof.append((side[0][0] - arm, zb))          # arm tip, top
            prof.append((side[0][0], zb))                # top at the side
            prof += [(y, z) for (y, z) in side[1:]]      # down the planking
            yl, zl = side[-1]
            prof.append((yl - 0.032, zl + 0.004))        # leg toe
            # inner edge of leg rising back up, then the throat curve to the arm
            for k in range(5, 0, -1):
                y, z = side[k]
                f = (zb - z) / leg
                prof.append((y - 0.034 - 0.05 * (1 - f) ** 3, z))
            prof.append((side[0][0] - 0.12, zb - 0.045))
            prof.append((side[0][0] - arm, zb - 0.030))  # arm tip, underside
            prof = [(sgn * y, z) for (y, z) in prof]
            if sgn < 0:
                prof = prof[::-1]
            kb = MB()
            kb.add_plate(prof, 0.032, origin=(xs - 0.016, 0, 0), mat=mat_knee,
                         basis=(Y, Z, X))
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
        sy = min(abs(piv["y"]) - 0.42, 0.25 + 0.05 * slot)
        # GEN-1: the aftmost oars' blades ran out through the quarters where
        # the boat narrows.  Slide each stowed oar fore-and-aft (and if need
        # be closer to the centreline) until blade tip AND handle are aboard
        # with the blade's half-width as clearance.
        for _try in range(8):
            p0 = np.array([sx + dx - (length - inb), sgn * sy, rest_z])
            p1 = np.array([sx + dx + inb, sgn * sy, rest_z])
            q0, q1 = _fit_inside(hull, p0.copy(), p1.copy(), 0.085)
            if abs((q1[0] - q0[0]) - length) < 1e-6:
                sx = q1[0] - inb - dx
                break
            sy = max(0.06, sy - 0.05)
        stow = np.array([sx + dx, sgn * sy, rest_z])
        merged = MB("Oar")
        merged.append(oar, offset=stow, rot=R)
        merged.append(gear, offset=stow, rot=R)

        oars.append({"mb": merged, "pivot": pivot_world, "side": sgn,
                     "station_x": piv["x"]})
    return oars


def _x_limits_inside(hull, y, z, clear=0.03):
    """Fore and aft x between which the point (x, y, z) is inside the
    planking (inner face) with `clear` clearance -- used to keep long stowed
    gear inside the fine ends (GEN-1)."""
    def inside(xi):
        # half-breadth of the inner planking surface at height z
        lo, hi = 0.0, 1.0
        if hull.section_pt(xi, 1.0, -0.02)[2] < z:
            return False
        if hull.section_pt(xi, 0.0, -0.02)[2] > z:
            return False
        for _ in range(20):
            md = 0.5 * (lo + hi)
            if hull.section_pt(xi, md, -0.02)[2] < z:
                lo = md
            else:
                hi = md
        return abs(hull.section_pt(xi, 0.5 * (lo + hi), -0.02)[1]) >= abs(y) + clear
    xs = np.linspace(0.0, 1.0, 121)
    ok = [xi for xi in xs if inside(xi)]
    return hull.X(max(ok)), hull.X(min(ok))      # (aft x, fwd x)


def _fit_inside(hull, p0, p1, r):
    """Slide a straight spar p0->p1 (along +X) fore/aft so both ends are
    inside the boat; shorten only if it cannot fit."""
    xa0, xf0 = _x_limits_inside(hull, p0[1], p0[2], clear=r + 0.02)
    xa1, xf1 = _x_limits_inside(hull, p1[1], p1[2], clear=r + 0.02)
    xa, xf = max(xa0, xa1), min(xf0, xf1)
    L = p1[0] - p0[0]
    if L > xf - xa:
        p0[0], p1[0] = xa, xf
    elif p1[0] > xf:
        p1[0] = xf; p0[0] = xf - L
    elif p0[0] < xa:
        p0[0] = xa; p1[0] = xa + L
    return p0, p1


def rigging_stowed(hull, specs, mat_spar=24, mat_canvas=8, mat_rope=7):
    """
    Two- or three-spar dipping lug rig carried stowed in the boat (davit
    condition): masts, lug yards with furled sails (canvas bundles lashed with
    gaskets), and a boom for the main.  Laid fore-and-aft on the thwarts.
    Returns list of MBs.
    """
    out = []
    loa = hull.loa
    zl = specs.get("z", 0.24)
    # --- masts (tapered poles, leathered at the partners) -------------------
    for (lbl, xl, ll, rr) in specs.get("masts", []):
        mb = MB("Mast_" + lbl)
        p0 = np.array([xl - ll * 0.45, 0.10 if "main" in lbl else -0.06, zl])
        p1 = np.array([xl + ll * 0.55, 0.10 if "main" in lbl else -0.06, zl])
        if xl - ll * 0.45 < -loa / 2 + 0.2:
            p0[0] = -loa / 2 + 0.2
            p1[0] = p0[0] + ll
        # GEN-1: the rowing cutter's foremast ran 0.1 m out through the stem
        p0, p1 = _fit_inside(hull, p0, p1, rr)
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
        p0, p1 = _fit_inside(hull, p0, p1, 0.07)
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


def standard_gear(hull, kind="rowing", zfloor=None, z_thwart=None, hook_x=0.6,
                  board_fn=None):
    """
    The boat's loose gear, per the HMS Bombay model outfit list:
    painter, anchors/grapnel, fenders, boat hooks, baler, bucket, breaker.
    Returns list of (name, MB).
    """
    loa = hull.loa
    if zfloor is None:
        zfloor = hull.keel_z(0.5) + 0.14
    gear = []
    # GEN-1: the painter is coiled down on the starboard bow sheet (settled on
    # the sloping planking of the fine bow it rode up to the gunwale)
    xp = hull.X(0.095)
    yp = -(_inner_y(hull, 0.095, 0.30, -0.056) - 0.15)
    gear.append(("Painter", P.painter_coil((xp, yp, 0.30 + 0.012))))
    if kind == "rowing":
        # GEN-1: stowed on the bottom boards near the centreline, abaft the
        # stroke thwart (at y=-0.30 near the stern its flukes stood out
        # through the planking)
        gear.append(("Grapnel", P.grapnel((-loa / 2 + 2.05, -0.16, zfloor + 0.004), lie=True,
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
    # boat hooks.  GEN-1: they were 0.62*LOA (4.9 m) long and laid at
    # y=+-0.42 just above the bottom boards, so both ends ran out through
    # the planking at the fine bow and stern.  Now 10 ft (3.05 m) service
    # hooks, stowed fore-and-aft ON the thwarts outboard of the oars.
    bh = MB("BoatHooks")
    zt = z_thwart if z_thwart is not None else zfloor + 0.30
    for i, sgn in enumerate((-1, 1)):
        b = P.boat_hook((hook_x, sgn * 0.50, zt + 0.0145), length=3.05, along=X)
        bh.append(b)
    gear.append(("BoatHooks", bh))
    gear.append(("Baler", P.baler((-loa / 4, 0.28, zfloor + 0.09))))
    gear.append(("Bucket", P.bucket((-loa / 4 + 0.3, -0.22, zfloor))))
    gear.append(("Breaker", P.breaker((0.45, 0.0, zfloor + 0.14), r=0.115, l=0.38)))
    if board_fn is not None:
        rf = rest_fn(hull, board_fn)
        for name, gmb in gear:
            if name in ("Grapnel", "Anchor", "Baler", "Bucket", "Breaker"):
                settle(gmb, rf)
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
            # GEN-1: the knee's outboard edge follows the planking down (it
            # was vertical, so on a flared hull it stood out through the side)
            yz = lambda dz: min(_inner_y(hull, clamp(xi + dd, 0.0, 1.0), z - thk + dz, -0.060)
                                for dd in (-0.0025, 0.0, 0.0025))
            y0, y10, y20 = yz(0.0), yz(-0.10), yz(-0.20)
            out = [(side * y0, 0.0), (side * (y0 - width * 0.8), 0.0),
                   (side * (y0 - width * 0.8), -0.05), (side * (y10 - 0.10), -0.12),
                   (side * (y20 - 0.04), -0.20), (side * y20, -0.20),
                   (side * y10, -0.10)]
            if side < 0:
                out = out[::-1]
            supports.add_plate(out, 0.024, origin=(xs - 0.012, 0, z - thk),
                               mat=mat, basis=(Y, Z, X))
    return mb, supports


def bottom_boards(hull, xi0=0.15, xi1=0.85, z_off=0.155, board_w=0.078,
                  gap=0.008, rise=0.20, mat=1, y0=0.058, n_boards=5,
                  z_fn=None, max_climb=0.11, max_lift=0.32, z_ref=None):
    """Loose-laid bottom boards port + starboard of the keelson, following
    the deadrise, in lift-out lengths (service pattern).

    GEN-1 correction: the butt joints of all boards used to fall at the same
    two stations with 0.15 m gaps, and the inboard board stopped 47 mm short
    of the keelson -- together they read as black voids across and along the
    boat.  Joints are now 6 mm, staggered board by board, and the inboard
    board butts to the keelson cap.
    `z_fn(x, y)` (optional) gives the board underside height at a point --
    used to land the boards on the floors instead of on a guessed offset."""
    mb = MB("Bottom_Boards")
    loa = hull.loa
    butts = [(0.33, 0.67), (0.22, 0.56), (0.42, 0.78), (0.28, 0.62), (0.38, 0.72)]
    for sgn in (-1, 1):
        for k in range(n_boards):
            y = sgn * (y0 + board_w / 2 + k * (board_w + gap))
            shrink = 1.0 - 0.07 * k
            xa = loa / 2 - (0.5 + (xi1 - 0.5) * shrink) * loa
            xb = loa / 2 - (0.5 + (xi0 - 0.5) * shrink) * loa
            if z_fn is not None:
                # GEN-1: trim each board where the bottom turns up into the
                # bilge / fine ends -- untrimmed, the outboard boards of the
                # whaler climbed the planking to the waterline at their ends.
                def _ok(xx):
                    return (z_fn(xx, abs(y)) - z_fn(xx, y0) <= max_climb and
                            z_fn(xx, abs(y)) <= z_ref + max_lift)
                if z_ref is None:
                    z_ref = z_fn(0.0, y0)
                xm = 0.5 * (xa + xb)
                if not _ok(xm):
                    continue
                for end in ("a", "b"):
                    xe = xa if end == "a" else xb
                    lo_, hi_ = xm, xe          # lo_ ok, find limit toward hi_
                    if not _ok(xe):
                        for _ in range(30):
                            md = 0.5 * (lo_ + hi_)
                            if _ok(md):
                                lo_ = md
                            else:
                                hi_ = md
                        xe = lo_
                    if end == "a":
                        xa = xe
                    else:
                        xb = xe
                if abs(xb - xa) < 0.40:
                    continue
            cuts = [0.0] + list(butts[k % len(butts)]) + [1.0]
            for c0, c1 in zip(cuts[:-1], cuts[1:]):
                f0 = c0 + (0.003 if c0 > 0 else 0.0)
                f1 = c1 - (0.003 if c1 < 1 else 0.0)
                pa = np.array([lerp(xa, xb, f0), y, 0.0])
                pb = np.array([lerp(xa, xb, f1), y, 0.0])
                for pp in (pa, pb):
                    if z_fn is not None:
                        pp[2] = z_fn(pp[0], abs(y)) + 0.008
                    else:
                        pp[2] = hull.keel_z((loa / 2 - pp[0]) / loa) + z_off + rise * abs(y)
                mid = (pa + pb) / 2
                L = float(np.linalg.norm(pb - pa))
                ang = math.atan2(float(pb[2] - pa[2]), float(pb[0] - pa[0]))
                mb.add_box(tuple(mid), (L, board_w, 0.016), mat=mat,
                           rot=rot_axis((0, 1, 0), -ang), chamfer=0.003)
    return mb


def stern_backrest(hull, xi=0.950, z0=0.315, h=0.15, mat=1, mat_st=3):
    """Cambered back board across the stern sheets on brass stanchions."""
    mb = MB("Stern_Backrest")
    x = hull.X(xi)
    hw = abs(hull.section_pt(xi, 0.90, -0.10)[1]) * 0.78
    n = 5
    ys = np.linspace(-hw, hw, n + 1)
    pts = []
    for y in ys:
        pts.append(np.array([x - 0.05 * (y / hw) ** 2, y,
                             z0 + h + 0.03 * (y / hw) ** 2]))
    for i in range(n):
        p0, p1 = pts[i], pts[i + 1]
        mid = (p0 + p1) / 2
        L = float(np.linalg.norm(p1 - p0))
        ang = math.atan2(float(p1[2] - p0[2]), float(p1[1] - p0[1]))
        mb.add_box(tuple(mid), (0.016, L, 0.055), mat=mat,
                   rot=rot_axis((1, 0, 0), ang))
    for y in (-hw * 0.7, 0.0, hw * 0.7):
        top = z0 + h + 0.03 * (y / hw) ** 2
        cyl(mb, (x - 0.05 * (y / hw) ** 2, y, z0),
            (x - 0.05 * (y / hw) ** 2, y, top - 0.02), 0.009, seg=8, mat=mat_st)
    return mb


def stem_fairlead(hull, aft=False, mat=3):
    """Brass fairlead sheave + pin on the stemhead (or sternpost) for the
    painter, so the rope does not chafe the wood."""
    if aft:
        x = -hull.loa / 2 + 0.06
        z = hull.sheer_z(0.98) - 0.02
    else:
        x = hull.loa / 2 - 0.045
        z = hull.sheer_z(0.02) - 0.02
    mb = MB("Stem_Fairlead")
    mb.add_box((x, 0, z), (0.05, 0.024, 0.045), mat=mat, chamfer=0.008)
    cyl(mb, (x, -0.020, z + 0.012), (x, 0.020, z + 0.012), 0.020, seg=12, mat=mat)
    cyl(mb, (x, -0.027, z + 0.012), (x, 0.027, z + 0.012), 0.005, seg=8, mat=4)
    return mb


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


def z_on_surface(hull, x, y, off):
    """Height of the hull surface at outward offset `off` where its
    half-breadth equals y, at longitudinal position x (bisection in t).
    Used to land loose-laid boards and gear on the floors of the boat."""
    xi = clamp((hull.loa / 2 - x) / hull.loa, 0.0, 1.0)
    lo, hi = 0.0, 1.0
    if abs(hull.section_pt(xi, 0.0, off)[1]) >= y and hull.section_pt(xi, 0.0, off)[1] >= 0:
        return hull.section_pt(xi, 0.0, off)[2]
    for _ in range(40):
        mid = (lo + hi) / 2
        if hull.section_pt(xi, mid, off)[1] < y:
            lo = mid
        else:
            hi = mid
    return hull.section_pt(xi, (lo + hi) / 2, off)[2]


def floor_top_fn(hull, thk, floor_depth=0.075):
    """z_fn for bottom_boards: top of the floors (timber + floor moulding)."""
    off = -thk - floor_depth
    return lambda x, y: z_on_surface(hull, x, max(y, 0.0), off)


def rest_fn(hull, board_fn=None, board_ymax=0.49, thk=0.016):
    """Height a loose object can rest at, at (x, |y|): on the bottom boards
    where they are laid, never below the inner face of the planking."""
    def f(x, y):
        y = abs(y)
        z = z_on_surface(hull, x, max(y, 0.0), -thk - 0.002)
        if board_fn is not None and y <= board_ymax:
            z = max(z, board_fn(x, y) + 0.024)
        return z
    return f


def settle(mb, zfun, clear=0.002, n_probe=160):
    """GEN-1: land a loose item ON whatever it rests on.  Gear used to be
    placed at a single fixed 'zfloor' height, so anything off the centreline
    (baler, bucket, grapnel flukes, painter coil) went down through the
    deadrise of the bottom boards and out through the planking.
    Moves the whole mesh vertically so its lowest probe vertices just touch."""
    if not mb.verts:
        return mb
    V = np.array(mb.verts)
    order = np.argsort(V[:, 2])
    probe = V[order[:n_probe]]
    dz = max(zfun(float(p[0]), float(p[1])) - float(p[2]) for p in probe) + clear
    mb.verts = [(float(a), float(b), float(c) + dz) for a, b, c in V]
    return mb

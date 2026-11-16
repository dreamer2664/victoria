"""
parts.py -- reusable boat fittings: oars, rowlocks, thwarts, knees, rudder,
floor gratings, fenders, eyes and hooks.

Everything here is sized from the boat it belongs to, so the same functions
serve both hulls.
"""

from __future__ import annotations

import math

import numpy as np

from .geom import MeshBuilder, cyl, lerp, sphere, torus, unit
from .hull import MAT


# --------------------------------------------------------------------------
# oars
# --------------------------------------------------------------------------


def oar(mb, length=3.66, inboard=1.10, blade_len=0.62, blade_w=0.155, loom_r=0.024,
        pivot_origin=True, mat=MAT["wood_timber"], leather_mat=MAT["leather"]):
    """A Service oar built in local space.

    Local axes: +X outboard along the oar, +Z up, blade in the XY plane.
    With pivot_origin the origin sits at the leather/collar, i.e. exactly in
    the rowlock -- which is the pivot the Roblox rowing animation rotates
    about.

    Dimensions follow a 12 ft Service oar: 3.66 m overall, 1.10 m inboard of
    the collar, 0.62 m blade.
    """
    x0 = -inboard if pivot_origin else 0.0
    x1 = x0 + length
    # loom: handle -> collar (slightly thicker at the collar), then outboard
    n = 10
    xs = np.linspace(x0, x1 - blade_len, n)
    for i in range(n - 1):
        r = lerp(0.030, loom_r, i / (n - 1))
        cyl(mb, (xs[i], 0, 0), (xs[i + 1], 0, 0), r, seg=10, mat=mat)
    # leather sleeve at the collar
    cyl(mb, (-0.11, 0, 0), (0.13, 0, 0), loom_r + 0.006, seg=12, mat=leather_mat)
    # button (to stop the oar sliding inboard)
    cyl(mb, (-0.20, 0, 0), (-0.15, 0, 0), loom_r + 0.019, seg=12, mat=mat)
    # handle/grip
    cyl(mb, (x0, 0, 0), (x0 + 0.16, 0, 0), 0.028, seg=10, mat=mat)
    # blade: tapered flat paddle, slightly curved
    xb0 = x1 - blade_len
    nb = 9
    grid = np.zeros((nb, 5, 3))
    for i in range(nb):
        f = i / (nb - 1)
        x = lerp(xb0, x1, f)
        w = blade_w * 0.5 * (0.42 + 0.58 * math.sin(min(1.0, f * 1.12) * math.pi * 0.5))
        th = lerp(loom_r * 1.05, 0.010, f ** 0.7)
        camber = 0.012 * math.sin(f * math.pi) ** 0.6
        grid[i, 0] = (x, -w, 0)
        grid[i, 1] = (x, -w * 0.55, th * 0.55 + camber)
        grid[i, 2] = (x, 0, th + camber)
        grid[i, 3] = (x, w * 0.55, th * 0.55 + camber)
        grid[i, 4] = (x, w, 0)
    mb.add_grid(grid, mat)
    mb.add_grid(grid[:, ::-1] * np.array([1, 1, -1]), mat)
    # close the blade edges
    for j, flip in ((0, True), (4, False)):
        strip = np.stack([grid[:, j], grid[::-1, j] * np.array([1, 1, -1])], axis=1)
        mb.add_grid(strip, mat, flip=flip)


def rowlock(mb, pos, normal, mat=MAT["brass"], bronze=True):
    """Swivel rowlock: socket plate let into the gunwale, crutch, and the
    fore-and-aft pin.  (Cutters of this date used either iron thole pins or
    swivel rowlocks; the 1838 model shows notches cut in the top strake --
    both are represented here: notch in the capping, bronze socket in it.)"""
    n = unit(normal)
    pos = np.asarray(pos, dtype=float)
    # socket plate
    cyl(mb, pos - np.array([0, 0, 0.012]), pos + np.array([0, 0, 0.010]), 0.030, seg=12, mat=mat)
    # stem of the rowlock
    cyl(mb, pos + np.array([0, 0, 0.008]), pos + np.array([0, 0, 0.062]), 0.013, seg=10, mat=mat)
    # U crutch (two arms + base)
    top = pos + np.array([0, 0, 0.105])
    cyl(mb, pos + np.array([0, 0, 0.055]), top, 0.010, seg=8, mat=mat)
    for s in (-1, 1):
        cyl(mb, top, top + np.array([s * 0.038, 0, 0.030]), 0.008, seg=8, mat=mat)
    cyl(mb, top + np.array([-0.038, 0, 0.030]), top + np.array([0.038, 0, 0.030]), 0.008, seg=8, mat=mat)


# --------------------------------------------------------------------------
# structure
# --------------------------------------------------------------------------


def thwart_plank(mb, hull, xi, top_drop=0.135, width=0.255, thick=0.042, mat=MAT["wood_timber"],
                 end_inset=0.012, crown=0.010, n_y=17):
    """A rower's thwart: a plank spanning the boat, landing on the inwales."""
    p_c = hull.surface(xi, 0.94)
    # seats hang below the sheer line by `top_drop`, never above it
    z_top = hull.sheer_z(xi) - top_drop
    # half width measured at the height of the seat
    half = 0.0
    for t in np.linspace(0.5, 1.0, 60):
        p = hull.surface(xi, t)
        if p[2] <= z_top:
            half = p[1]
    half -= end_inset
    ys = np.linspace(-half, half, n_y)
    grid = np.zeros((n_y, 4, 3))
    for i, y in enumerate(ys):
        f = abs(y) / max(half, 1e-6)
        w = width * (1.0 - 0.10 * f ** 4)
        z = z_top + crown * (1.0 - f ** 2)
        grid[i, 0] = (p_c[0] - w * 0.5, y, z - thick)
        grid[i, 1] = (p_c[0] + w * 0.5, y, z - thick)
        grid[i, 2] = (p_c[0] + w * 0.5, y, z)
        grid[i, 3] = (p_c[0] - w * 0.5, y, z)
    base = mb.add_grid(grid, mat, close_v=True)
    mb.add_face([base + i for i in range(4)][::-1], mat)
    end = base + 4 * (n_y - 1)
    mb.add_face([end + i for i in range(4)], mat)
    return ys, z_top


def thwart_knee(mb, hull, xi, side=1, mat=MAT["wood_timber"], drop=0.20, inset=0.012):
    """Small hanging knee under the end of a thwart.

    The knee hangs down the inside of the planking, so its outer face has to
    follow the hull as the topsides fall away -- a knee built as a vertical
    slab stands 40 mm proud of a boat's side by the time it reaches the bottom
    of its drop, which is exactly how one of these ends up poking through the
    planking in a hull that is narrow at that station.
    """
    from .hull import half_breadth_at
    p = hull.surface(xi, 0.86)
    x = p[0]
    z0 = hull.sheer_z(xi) - 0.135
    z1 = z0 - drop
    y0 = side * max(half_breadth_at(hull, xi, z0) - inset, 0.02)
    y1 = side * max(half_breadth_at(hull, xi, z1) - inset, 0.02)
    t = 0.020 * (1 if side >= 0 else -1)
    mb.add_prism(
        np.array([[x - 0.020, y0 - t, z0], [x + 0.020, y0 - t, z0],
                  [x + 0.020, y0, z0], [x - 0.020, y0, z0]]),
        np.array([[x - 0.020, y1 - t, z1], [x + 0.020, y1 - t, z1],
                  [x + 0.020, y1, z1], [x - 0.020, y1, z1]]),
        mat=mat,
    )


def bench(mb, hull, xi, top_drop=0.16, width=0.34, thick=0.045, mat=MAT["wood_timber"], n_y=17,
          inset=0.010):
    return thwart_plank(mb, hull, xi, top_drop=top_drop, width=width, thick=thick, mat=mat,
                        end_inset=inset, n_y=n_y)


def floor_gratings(mb, hull, xi0, xi1, n_slats=5, slat_w=0.095, thick=0.024, t=0.10,
                   mat=MAT["wood_deck"], gap=0.022, lift=0.055):
    """Slatted wooden floor ('bottom boards') resting on cleats.

    The boards sit `lift` clear of the planking so that bilge water can run
    under them and air can get at the frames -- the arrangement visible in the
    reference model, and the reason a boat's floor is slatted rather than
    solid.
    """
    xs = np.linspace(xi0, xi1, 26)
    for k in range(n_slats):
        fy = -1.0 + 2.0 * k / (n_slats - 1) if n_slats > 1 else 0.0
        pts = []
        for xi in xs:
            p = hull.surface(xi, t)
            pts.append(np.array([p[0], fy * p[1] * 0.80, p[2] + lift]))
        pts = np.array(pts)
        # cleats under the boards
        for f in (0.18, 0.82):
            i = int(f * (len(pts) - 1))
            c = pts[i]
            mb.add_box(c + np.array([0, 0, -lift * 0.5 - 0.004]),
                       np.array([0.045, slat_w * 0.55, lift * 0.5]), None, mat)
        grid = np.zeros((len(pts), 4, 3))
        for i, p in enumerate(pts):
            grid[i, 0] = p + np.array([-0.02, -slat_w * 0.5, 0.0])
            grid[i, 1] = p + np.array([0.02, -slat_w * 0.5, 0.0])
            grid[i, 2] = p + np.array([0.02, slat_w * 0.5, 0.0])
            grid[i, 3] = p + np.array([-0.02, slat_w * 0.5, 0.0])
        # top surface then thickness
        top = grid.copy()
        bot = grid.copy()
        bot[:, :, 2] -= thick
        mb.add_grid(top, mat)
        mb.add_grid(bot[:, ::-1], mat)
        for j, flip in ((0, True), (3, False)):
            strip = np.stack([top[:, j], bot[:, j]], axis=1)
            mb.add_grid(strip, mat, flip=flip)
        for i, flip in ((0, True), (len(pts) - 1, False)):
            strip = np.stack([top[i, :], bot[i, :]], axis=1)
            mb.add_grid(strip, mat, flip=flip)


def quarter_knee(mb, hull, mat=MAT["wood_timber"], side=1):
    """Curved knee joining the transom to the sheer strake."""
    pts = []
    for i in range(12):
        f = i / 11
        # an arc from the transom face out to the gunwale
        t = lerp(0.62, 0.99, f)
        p = hull.surface(0.985, t)
        p = np.array([p[0] - 0.02 * math.sin(f * math.pi), p[1] * side, p[2]])
        pts.append(p)
    pts = np.array(pts)
    grid = np.zeros((len(pts), 4, 3))
    for i, p in enumerate(pts):
        w = lerp(0.075, 0.055, i / (len(pts) - 1))
        grid[i, 0] = p + np.array([-w, -0.012, 0])
        grid[i, 1] = p + np.array([w, -0.012, 0])
        grid[i, 2] = p + np.array([w, 0.012, 0])
        grid[i, 3] = p + np.array([-w, 0.012, 0])
    mb.add_grid(grid, mat, close_v=True)


def breast_hook(mb, hull, mat=MAT["wood_timber"], xi=0.075, half_width=None, drop=0.11, thick=0.035):
    """Breast hook: the knee that ties the two sides of the stem together."""
    p = hull.surface(xi, 0.95)
    half = half_width or p[1] * 0.95
    n = 13
    ys = np.linspace(-half, half, n)
    top = np.zeros((n, 3))
    bot = np.zeros((n, 3))
    for i, y in enumerate(ys):
        f = abs(y) / max(half, 1e-6)
        x = p[0] + 0.035 * (1 - f ** 2)
        top[i] = (x, y, p[2] - 0.02)
        bot[i] = (x - 0.01, y, p[2] - 0.02 - drop * (1 - 0.45 * f ** 2))
    grid = np.stack([top, bot], axis=1)          # (n, 2, 3) aft face
    mb.add_grid(grid, mat)
    back = grid.copy()
    back[:, :, 0] -= thick
    mb.add_grid(back[:, ::-1], mat)
    for j, flip in ((0, True), (1, False)):
        strip = np.stack([grid[:, j], back[:, j]], axis=1)
        mb.add_grid(strip, mat, flip=flip)
    for i, flip in ((0, True), (n - 1, False)):
        strip = np.stack([grid[i, :], back[i, :]], axis=1)
        mb.add_grid(strip, mat, flip=flip)


def rudder(mb, hull, mat=MAT["wood_timber"], iron=MAT["iron"], length=0.95, width=0.30):
    """Rudder & tiller for the pulling cutter, hung on the sternpost.

    Built in *pivot-local* space: origin on the pintle axis at the head of
    the rudder, +X forward (towards the bow), +Z up.  The object is then
    placed at the head so the Roblox script can swing it about its real axis.
    """
    # blade: a tapered board hanging below the head
    n = 12
    grid = np.zeros((n, 6, 3))
    for i in range(n):
        f = i / (n - 1)
        z = -f * length
        # width grows a little towards the bottom, then tapers to the heel
        w = width * (0.55 + 0.45 * math.sin(min(1.0, f * 1.05) * math.pi * 0.5))
        if f > 0.85:
            w *= 1.0 - 0.35 * (f - 0.85) / 0.15
        th = 0.042 * (1 - 0.45 * f)
        grid[i, 0] = (-w * 0.85, 0, z)
        grid[i, 1] = (-w * 0.15, 0, z)
        grid[i, 2] = (0.02, th * 0.5, z)
        grid[i, 3] = (0.02, -th * 0.5, z)
        grid[i, 4] = (-w * 0.15, 0, z) - np.array([0, 0, 0.0001])
        grid[i, 5] = (-w * 0.85, 0, z)
    blade = grid[:, :4, :]
    mb.add_grid(blade, mat, close_v=True)
    back = blade.copy()
    back[:, :, 0] += 0.030
    mb.add_grid(back[:, ::-1], mat)
    # head / stock
    cyl(mb, (0, 0, 0.10), (0, 0, -0.03), 0.033, seg=12, mat=mat)
    # tiller: socketed into the head, running forward
    t0 = np.array([0.0, 0, 0.075])
    t1 = np.array([0.92, 0, 0.045])
    cyl(mb, t0, t1, 0.030, seg=10, mat=mat, r1=0.026)
    cyl(mb, t1, t1 + np.array([0.13, 0, 0.006]), 0.028, seg=10, mat=mat, r1=0.021)
    # pintle & gudgeon straps
    for z in (-0.06, -0.42, -0.80):
        cyl(mb, (-0.02, -0.035, z), (0.035, -0.035, z), 0.010, seg=8, mat=iron)


# --------------------------------------------------------------------------
# fittings
# --------------------------------------------------------------------------


def eye_bolt(mb, pos, direction=(0, 1, 0), mat=MAT["steel"], ring=True, scale=1.0):
    pos = np.asarray(pos, dtype=float)
    d = unit(direction)
    cyl(mb, pos - d * 0.03, pos + d * 0.055 * scale, 0.011 * scale, seg=10, mat=mat)
    if ring:
        c = pos + d * (0.075 * scale)
        # a ring in the plane perpendicular to d
        R = 0.030 * scale
        n1 = unit(np.cross(d, [0, 0, 1.0])) if abs(d[2]) < 0.9 else unit(np.cross(d, [1.0, 0, 0]))
        n2 = np.cross(d, n1)
        pts = [c + R * (math.cos(a) * n1 + math.sin(a) * n2) for a in np.linspace(0, 2 * math.pi, 17)]
        mb.add_tube(np.array(pts), 0.007 * scale, segments=8, mat=mat, caps=False)
    else:
        torus(mb, pos + d * 0.05, 0.028 * scale, 0.007 * scale, seg=16, rseg=6, mat=mat)


def boat_hook(mb, pos, length=1.9, mat=MAT["wood_timber"], metal=MAT["steel"]):
    pos = np.asarray(pos, dtype=float)
    cyl(mb, pos, pos + np.array([length, 0, 0]), 0.020, seg=10, mat=mat)
    tip = pos + np.array([length, 0, 0])
    cyl(mb, tip, tip + np.array([0.09, 0, 0.02]), 0.012, seg=8, mat=metal)
    sphere(mb, tip + np.array([0.10, 0, 0.03]), 0.018, seg=8, rings=6, mat=metal)


def grapnel(mb, pos, scale=1.0, mat=MAT["iron"], ring_mat=MAT["steel"]):
    """Small boat's grapnel: shank, four curved arms, crown, and a shackle.

    A ship's boat does not carry a bower anchor; it carries an iron grapnel
    light enough for two men to row out and hook on with.
    """
    p = np.asarray(pos, dtype=float)
    L = 0.42 * scale
    arm = 0.20 * scale
    # shank
    cyl(mb, p, p + np.array([0, 0, L]), 0.018 * scale, seg=8, mat=mat)
    # crown
    cyl(mb, p + np.array([0, 0, -0.02 * scale]), p + np.array([0, 0, 0.03 * scale]),
        0.030 * scale, seg=10, mat=mat)
    # four arms, curving up and out
    for k in range(4):
        a = math.pi * 0.5 * k + math.pi * 0.25
        d = np.array([math.cos(a), math.sin(a), 0.0])
        pts = []
        for i in range(5):
            f = i / 4.0
            pts.append(p + d * (arm * f) + np.array([0, 0, 0.10 * scale * math.sin(f * math.pi * 0.85)]))
        mb.add_tube(np.array(pts), 0.013 * scale, segments=6, mat=mat, caps=True)
        # fluke
        tip = pts[-1]
        cyl(mb, tip, tip + np.array([0, 0, 0.05 * scale]), 0.020 * scale, seg=6, mat=mat, r1=0.006)
    # shackle at the head
    torus(mb, p + np.array([0, 0, L + 0.02 * scale]), 0.030 * scale, 0.009 * scale,
          seg=12, rseg=5, axis="Y", mat=ring_mat)


def bilge_pump(mb, pos, height=0.55, mat=MAT["brass"], wood=MAT["wood_timber"]):
    """Elm-tree pump / brass pump: barrel, cap, spear rod and a brake handle."""
    p = np.asarray(pos, dtype=float)
    cyl(mb, p, p + np.array([0, 0, 0.06]), 0.055, seg=14, mat=mat)      # foot
    cyl(mb, p + np.array([0, 0, 0.05]), p + np.array([0, 0, height]), 0.042, seg=14, mat=mat)
    cyl(mb, p + np.array([0, 0, height]), p + np.array([0, 0, height + 0.05]), 0.052, seg=14, mat=mat)
    # spear rod and handle
    cyl(mb, p + np.array([0, 0, height + 0.02]), p + np.array([0, 0, height + 0.30]),
        0.012, seg=8, mat=MAT["steel"])
    h = p + np.array([0, 0, height + 0.31])
    cyl(mb, h, h + np.array([0.19, 0, 0.02]), 0.014, seg=8, mat=wood)
    cyl(mb, h + np.array([0.19, 0, 0.02]), h + np.array([0.23, 0, 0.025]), 0.020, seg=8, mat=wood)
    # discharge elbow
    el = np.array([p[0] + 0.05, p[1], p[2] + height - 0.10])
    cyl(mb, el, el + np.array([0.10, 0, 0]), 0.020, seg=10, mat=mat)
    cyl(mb, el + np.array([0.10, 0, 0]), el + np.array([0.10, 0, 0.06]), 0.020, seg=10, mat=mat)


def fender(mb, pos, mat=MAT["canvas"], rope=MAT["rope"], length=0.55, r=0.075):
    pos = np.asarray(pos, dtype=float)
    # A coir fender is a fat sausage with rounded ends, not a lens: full
    # diameter for the middle third, then a fast round-off.  The old sine
    # profile tapered the whole way and read as a peel hanging on the topsides.
    n = 14
    prof = []
    for i in range(n + 1):
        f = i / n
        t = abs(2.0 * f - 1.0)            # 0 at the middle, 1 at each end
        rr = r * math.sqrt(max(0.0, 1.0 - t ** 6)) if t > 0.62 else r
        prof.append((max(rr, 0.006), -length * 0.5 + length * f))
    mb.add_lathe(prof, segments=18, center=pos, mat=mat)
    cyl(mb, pos + np.array([0, 0, length * 0.5]), pos + np.array([0, 0, length * 0.5 + 0.10]), 0.008,
        seg=6, mat=rope)

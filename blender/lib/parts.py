"""
parts.py -- reusable Victorian architectural components.

A "wall map" is a function p(u, z, d) -> (x, y, z) where
    u = distance along the wall, z = height, d = depth measured inward from the
    outer wall face.  This lets one facade routine serve all four orientations.
"""
import math
from core import MeshBuilder


# ---------------------------------------------------------------- wall maps
def wmap(axis, fixed, inward=+1):
    if axis == "X":          # wall runs along X, sits at y = fixed
        return lambda u, z, d: (u, fixed + inward * d, z)
    return lambda u, z, d: (fixed + inward * d, u, z)   # axis == 'Y'


def slab(mb, mp, u0, u1, z0, z1, d0, d1, mat, top=None):
    """Axis-aligned slab in wall-local space (this is the workhorse of every facade).

    Winding is consistent for inward = +1; objects are normal-recalculated on
    creation, so mirrored walls come out right too.
    """
    A = mp(u0, z0, d0); B = mp(u1, z0, d0); C = mp(u1, z1, d0); D = mp(u0, z1, d0)
    E = mp(u0, z0, d1); F = mp(u1, z0, d1); G = mp(u1, z1, d1); H = mp(u0, z1, d1)
    mb.add_quad(A, B, C, D, mat)          # outer face
    mb.add_quad(F, E, H, G, mat)          # inner face
    mb.add_quad(E, F, B, A, mat)          # bottom
    mb.add_quad(C, G, H, D, top or mat)   # top
    mb.add_quad(B, F, G, C, mat)          # +u end
    mb.add_quad(E, A, D, H, mat)          # -u end


def spans_minus(u0, u1, holes):
    """Given hole intervals inside [u0,u1], return the solid spans."""
    out = []
    cur = u0
    for a, b in sorted(holes):
        if a > cur + 1e-6:
            out.append((cur, min(a, u1)))
        cur = max(cur, b)
    if cur < u1 - 1e-6:
        out.append((cur, u1))
    return [(a, b) for a, b in out if b - a > 1e-5]


# ---------------------------------------------------------------- window
def sash_window(mb, mp, u0, u1, z0, z1, depth, mat_frame="paint_white",
                mat_glass="glass", panes_x=2, panes_y=2, bars=True, blind=False):
    """Recessed sash window with real reveal, frame and glazing bars."""
    if blind:
        # bricked-up opening: recessed brick panel + a blind arch above
        slab(mb, mp, u0 + 0.04, u1 - 0.04, z0 + 0.04, z1 - 0.04, 0.06, depth * 0.55, "brick_soot")
        return
    gd = depth * 0.62                      # glass plane depth
    # reveal lining (jambs, head, sill) -- this is what gives the opening depth
    t = 0.055
    slab(mb, mp, u0, u0 + t, z0, z1, 0.0, depth, "paint_white")
    slab(mb, mp, u1 - t, u1, z0, z1, 0.0, depth, "paint_white")
    slab(mb, mp, u0, u1, z1 - t, z1, 0.0, depth, "paint_white")
    slab(mb, mp, u0, u1, z0, z0 + t, 0.0, depth, "paint_white")
    # glass
    slab(mb, mp, u0 + t, u1 - t, z0 + t, z1 - t, gd, gd + 0.012, mat_glass)
    if not bars:
        return
    # frame + glazing bars, slightly proud of the glass
    b = 0.028
    fd = gd - 0.03
    w = u1 - u0 - 2 * t
    h = z1 - z0 - 2 * t
    for i in range(1, panes_x):
        uu = u0 + t + w * i / panes_x
        slab(mb, mp, uu - b / 2, uu + b / 2, z0 + t, z1 - t, fd, fd + 0.03, mat_frame)
    for j in range(1, panes_y):
        zz = z0 + t + h * j / panes_y
        th = 0.045 if j == panes_y // 2 else b          # heavier meeting rail
        slab(mb, mp, u0 + t, u1 - t, zz - th / 2, zz + th / 2, fd, fd + 0.03, mat_frame)


def stone_sill(mb, mp, u0, u1, z0, mat="sandstone", proj=0.09, thick=0.075):
    slab(mb, mp, u0 - 0.03, u1 + 0.03, z0 - thick, z0, -proj, 0.10, mat)


def window_hood(mb, mp, u0, u1, z1, mat="sandstone", proj=0.12, thick=0.10):
    slab(mb, mp, u0 - 0.05, u1 + 0.05, z1, z1 + thick, -proj, 0.12, mat)


def segmental_arch(mb, mp, u_c, half_w, z_spring, rise, depth,
                   mat_ring="brick_soot", mat_tympanum="paint_white",
                   ring_w=0.22, voussoirs=9, proud=0.035):
    """A real brick segmental arch: curved ring of voussoirs over a recessed tympanum."""
    # tympanum: vertical strips filling between the arch curve and the rectangle head
    n = 24
    crown = z_spring + rise
    for i in range(n):
        a0 = -half_w + 2 * half_w * i / n
        a1 = -half_w + 2 * half_w * (i + 1) / n
        am = (a0 + a1) / 2
        # circular segment approximation
        r = (half_w ** 2 + rise ** 2) / (2 * rise) if rise > 1e-4 else 1e9
        zc = z_spring + rise - r
        inside = r * r - am * am
        y = zc + math.sqrt(inside) if inside > 0 else z_spring
        y = min(y, crown)
        if crown - y > 0.004:
            slab(mb, mp, u_c + a0, u_c + a1, y, crown, depth * 0.30, depth * 0.42, mat_tympanum)
    # voussoirs: boxes rotated along the arc
    r_in = (half_w ** 2 + rise ** 2) / (2 * rise) if rise > 1e-4 else 1e9
    zc = z_spring + rise - r_in
    for k in range(voussoirs):
        t0 = math.pi - (k + 0.06) / voussoirs * math.pi
        t1 = math.pi - (k + 0.94) / voussoirs * math.pi
        # param by angle across the arch
        a0 = math.cos(t0) * half_w
        a1 = math.cos(t1) * half_w
        y0 = zc + math.sqrt(max(0.0, r_in ** 2 - a0 ** 2))
        y1 = zc + math.sqrt(max(0.0, r_in ** 2 - a1 ** 2))
        y0, y1 = min(y0, crown), min(y1, crown)
        umin, umax = min(a0, a1), max(a0, a1)
        zm = min(y0, y1)
        slab(mb, mp, u_c + umin, u_c + umax, zm, max(y0, y1) + ring_w, -proud, depth * 0.5, mat_ring)


def flat_lintel(mb, mp, u0, u1, z1, mat="sandstone", depth=0.25, thick=0.18, proud=0.03):
    slab(mb, mp, u0 - 0.04, u1 + 0.04, z1, z1 + thick, -proud, depth, mat)


# ---------------------------------------------------------------- doors
def door(mb, mp, u0, u1, z0, z1, depth, mat_panel="timber", mat_frame="paint_green",
         planks=4, fanlight=False):
    t = 0.07
    slab(mb, mp, u0, u0 + t, z0, z1, 0.0, depth * 0.6, mat_frame)
    slab(mb, mp, u1 - t, u1, z0, z1, 0.0, depth * 0.6, mat_frame)
    slab(mb, mp, u0, u1, z1 - t, z1, 0.0, depth * 0.6, mat_frame)
    zt = z1 - (0.55 if fanlight else t)
    if fanlight:
        slab(mb, mp, u0 + t, u1 - t, zt, z1 - t, depth * 0.45, depth * 0.47, "glass_lit")
    slab(mb, mp, u0 + t, u1 - t, z0, zt, depth * 0.42, depth * 0.50, mat_panel)
    # plank lines
    w = u1 - u0 - 2 * t
    for i in range(1, planks):
        uu = u0 + t + w * i / planks
        slab(mb, mp, uu - 0.012, uu + 0.012, z0, zt, depth * 0.38, depth * 0.42, "black")


def hoist_door(mb, mp, u0, u1, z0, z1, depth, mat="timber"):
    """Warehouse loading door: tall boarded opening + projecting cathead hoist beam."""
    t = 0.08
    slab(mb, mp, u0 + t, u1 - t, z0 + 0.05, z1 - t, depth * 0.30, depth * 0.40, mat)
    slab(mb, mp, u0, u0 + t, z0, z1, 0.0, depth * 0.6, "iron")
    slab(mb, mp, u1 - t, u1, z0, z1, 0.0, depth * 0.6, "iron")
    slab(mb, mp, u0, u1, z1 - t, z1, 0.0, depth * 0.6, "iron")
    for i in range(1, 6):
        uu = u0 + t + (u1 - u0 - 2 * t) * i / 6
        slab(mb, mp, uu - 0.01, uu + 0.01, z0 + 0.05, z1 - t, depth * 0.28, depth * 0.30, "black")
    # cathead beam + pulley block
    uc = (u0 + u1) / 2
    mp_ = mp
    slab(mb, mp_, uc - 0.10, uc + 0.10, z1 + 0.15, z1 + 0.30, -0.95, 0.10, "timber")
    mb.add_box_c(*mp_(uc, z1 + 0.22, -0.85)[:2], 0.22, 0.22, 0.30, "iron") if False else None
    p = mp(uc, z1 + 0.22, -0.85)
    mb.add_box_c(p[0], p[1], p[2], 0.24, 0.24, 0.32, "iron")


# ---------------------------------------------------------------- horizontal features
def string_course(mb, mp, u0, u1, z, mat="sandstone", h=0.16, proj=0.075, depth=0.30):
    slab(mb, mp, u0, u1, z, z + h, -proj, depth, mat)


def cornice(mb, mp, u0, u1, z, mat="sandstone", proj=0.34, h=0.30, brackets=True, ustep=1.5):
    """Projecting cornice with dentils/brackets -- the single most Victorian detail."""
    slab(mb, mp, u0, u1, z, z + h * 0.55, -proj * 0.55, 0.35, mat)
    slab(mb, mp, u0, u1, z + h * 0.55, z + h, -proj, 0.35, mat)
    slab(mb, mp, u0, u1, z + h, z + h + 0.09, -proj * 1.06, 0.30, mat)   # top drip
    if brackets:
        n = max(1, int((u1 - u0) / ustep))
        for i in range(n):
            uu = u0 + (u1 - u0) * (i + 0.5) / n
            slab(mb, mp, uu - 0.055, uu + 0.055, z - 0.14, z + h * 0.55, -proj * 0.8, 0.12, mat)


def quoin(mb, mp, z0, z1, u_edge, mat="sandstone", w=0.55, h=0.30, outward=-1):
    """Alternating stone quoins at a building corner."""
    z = z0
    i = 0
    while z < z1:
        cw = w if i % 2 == 0 else w * 0.62
        if outward < 0:
            slab(mb, mp, u_edge, u_edge + cw, z, min(z + h, z1), -0.025, 0.30, mat)
        else:
            slab(mb, mp, u_edge - cw, u_edge, z, min(z + h, z1), -0.025, 0.30, mat)
        z += h
        i += 1


def plinth(mb, mp, u0, u1, z0, h=0.55, mat="brick_blue", proj=0.05):
    slab(mb, mp, u0, u1, z0, z0 + h, -proj, 0.40, mat)


def parapet(mb, mp, u0, u1, z_top, h=0.85, mat="brick_soot", cap="granite", thick=0.30):
    slab(mb, mp, u0, u1, z_top, z_top + h, 0.0, thick, mat)
    slab(mb, mp, u0, u1, z_top + h, z_top + h + 0.08, -0.04, thick + 0.04, cap)


def railing(mb, mp, u0, u1, z, mat="iron", h=1.05, spacing=1.8):
    """Cast-iron railing: posts, two rails, close-set balusters."""
    n = max(1, int((u1 - u0) / spacing))
    for i in range(n + 1):
        uu = u0 + (u1 - u0) * i / n
        slab(mb, mp, uu - 0.035, uu + 0.035, z, z + h, 0.35, 0.42, mat)
    for zz in (z + h - 0.06, z + 0.18):
        slab(mb, mp, u0, u1, zz, zz + 0.05, 0.36, 0.41, mat)
    nb = int((u1 - u0) / 0.14)
    for i in range(nb):
        uu = u0 + (u1 - u0) * (i + 0.5) / nb
        slab(mb, mp, uu - 0.011, uu + 0.011, z + 0.20, z + h - 0.06, 0.375, 0.395, mat)


def downpipe(mb, mp, u, z0, z1, mat="iron"):
    p0 = mp(u, z0, 0.02); p1 = mp(u, z1, 0.02)
    for a, b in ((0.0, 1.0),):
        pass
    mb.add_beam(p0, p1, 0.10, 0.10, mat)


def chimney_stack(mb, x, y, z0, h, w=1.1, d=0.8, mat="brick_soot", pots=3):
    mb.add_box_c(x, y, z0 + h / 2, w, d, h, mat)
    mb.add_box_c(x, y, z0 + h + 0.06, w + 0.16, d + 0.16, 0.12, "sandstone")
    for i in range(pots):
        px = x - w / 2 + w * (i + 0.5) / pots
        mb.add_cyl(px, y, z0 + h + 0.12, z0 + h + 0.55, 0.11, "terracotta", seg=8)


def clock_face(mb, x, y, z, r=0.55, axis="Y", mat="paint_white"):
    n = 16
    for i in range(n):
        a0 = 2 * math.pi * i / n
        a1 = 2 * math.pi * (i + 1) / n
        if axis == "Y":
            mb.add_tri((x, y, z), (x + math.cos(a0) * r, y, z + math.sin(a0) * r),
                       (x + math.cos(a1) * r, y, z + math.sin(a1) * r), mat)
        else:
            mb.add_tri((x, y, z), (x, y + math.cos(a0) * r, z + math.sin(a0) * r),
                       (x, y + math.cos(a1) * r, z + math.sin(a1) * r), mat)
    mb.add_box_c(x if axis == "Y" else x - 0.03, y - 0.03 if axis == "Y" else y, z + 0.20,
                 0.05, 0.05, 0.40, "black")
    mb.add_box_c(x if axis == "Y" else x - 0.05, y - 0.05 if axis == "Y" else y, z + 0.12,
                 0.28, 0.05, 0.05, "black")


# ---------------------------------------------------------------- wall panel
def wall_panel(mb, axis, fixed, u0, u1, z0, z1, thick, inward, mat,
               holes=(), top_mat=None):
    """Solid wall pierced by rectangular openings, built as horizontal bands.

    This is the correct way to get real window openings without boolean modifiers
    (booleans on 200+ buildings would be both slow and topologically fragile).
    """
    mp = wmap(axis, fixed, inward)
    hs = [(h[0], h[1], h[2], h[3]) for h in holes]      # (u0,u1,z0,z1)
    zs = sorted({z0, z1} | {h[2] for h in hs} | {h[3] for h in hs})
    zs = [z for z in zs if z0 - 1e-6 <= z <= z1 + 1e-6]
    for i in range(len(zs) - 1):
        za, zb = zs[i], zs[i + 1]
        if zb - za < 1e-5:
            continue
        cut = [(h[0], h[1]) for h in hs
               if h[2] <= za + 1e-4 and h[3] >= zb - 1e-4]
        for a, b in spans_minus(u0, u1, cut):
            slab(mb, mp, a, b, za, zb, 0.0, thick, mat, top=top_mat)
    return mp

"""
parts.py -- reusable Victorian architectural components.
GENERATION II — OPERATION VICTORIA (PERICLES-II)

A "wall map" is a function p(u, z, d) -> (x, y, z) where
    u = distance along the wall, z = height, d = depth measured inward from the
    outer wall face (d < 0 is proud/outward). This lets one facade routine serve
    all four orientations.
"""
import math
from core import MeshBuilder


# ---------------------------------------------------------------- wall maps
def wmap(axis, fixed, inward=+1):
    if axis == "X":          # wall runs along X, sits at y = fixed
        return lambda u, z, d: (u, fixed + inward * d, z)
    return lambda u, z, d: (fixed + inward * d, u, z)   # axis == 'Y'


def slab(mb, mp, u0, u1, z0, z1, d0, d1, mat, top=None):
    """Axis-aligned slab in wall-local space."""
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


# ---------------------------------------------------------------- windows
def sash_window(mb, mp, u0, u1, z0, z1, depth, mat_frame="paint_white",
                mat_glass="glass", panes_x=2, panes_y=2, bars=True, blind=False):
    """Recessed Victorian multi-pane sash window with true reveal depth, frame and glazing bars."""
    if blind:
        slab(mb, mp, u0 + 0.04, u1 - 0.04, z0 + 0.04, z1 - 0.04, 0.06, depth * 0.55, "brick_soot")
        return
    gd = depth * 0.65                      # glass plane depth
    t = 0.065                              # reveal frame thickness
    # reveal jambs, head, sill
    slab(mb, mp, u0, u0 + t, z0, z1, 0.0, depth, mat_frame)
    slab(mb, mp, u1 - t, u1, z0, z1, 0.0, depth, mat_frame)
    slab(mb, mp, u0, u1, z1 - t, z1, 0.0, depth, mat_frame)
    slab(mb, mp, u0, u1, z0, z0 + t, 0.0, depth, mat_frame)
    # glass pane
    slab(mb, mp, u0 + t, u1 - t, z0 + t, z1 - t, gd, gd + 0.015, mat_glass)
    if not bars:
        return
    # meeting rail and glazing bars
    b = 0.032
    fd = gd - 0.035
    w = u1 - u0 - 2 * t
    h = z1 - z0 - 2 * t
    for i in range(1, panes_x):
        uu = u0 + t + w * i / panes_x
        slab(mb, mp, uu - b / 2, uu + b / 2, z0 + t, z1 - t, fd, fd + 0.035, mat_frame)
    for j in range(1, panes_y):
        zz = z0 + t + h * j / panes_y
        th = 0.055 if j == panes_y // 2 else b
        slab(mb, mp, u0 + t, u1 - t, zz - th / 2, zz + th / 2, fd, fd + 0.035, mat_frame)


def stone_sill(mb, mp, u0, u1, z0, mat="sandstone", proj=0.10, thick=0.085):
    slab(mb, mp, u0 - 0.04, u1 + 0.04, z0 - thick, z0, -proj, 0.12, mat)


def window_hood(mb, mp, u0, u1, z1, mat="sandstone", proj=0.14, thick=0.11):
    slab(mb, mp, u0 - 0.06, u1 + 0.06, z1, z1 + thick, -proj, 0.14, mat)


def segmental_arch(mb, mp, u_c, half_w, z_spring, rise, depth,
                   mat_ring="brick_red", mat_tympanum="brick_soot",
                   ring_w=0.24, voussoirs=7, proud=0.035):
    """Brick segmental arch with keystone and voussoirs."""
    crown = z_spring + rise
    n = 16
    for i in range(n):
        a0 = -half_w + 2 * half_w * i / n
        a1 = -half_w + 2 * half_w * (i + 1) / n
        am = (a0 + a1) / 2
        r = (half_w ** 2 + rise ** 2) / (2 * rise) if rise > 1e-4 else 1e9
        zc = z_spring + rise - r
        inside = r * r - am * am
        y = zc + math.sqrt(inside) if inside > 0 else z_spring
        y = min(y, crown)
        if crown - y > 0.005:
            slab(mb, mp, u_c + a0, u_c + a1, y, crown, depth * 0.30, depth * 0.45, mat_tympanum)

    r_in = (half_w ** 2 + rise ** 2) / (2 * rise) if rise > 1e-4 else 1e9
    zc = z_spring + rise - r_in
    for k in range(voussoirs):
        t0 = math.pi - (k + 0.05) / voussoirs * math.pi
        t1 = math.pi - (k + 0.95) / voussoirs * math.pi
        a0 = math.cos(t0) * half_w
        a1 = math.cos(t1) * half_w
        y0 = min(crown, zc + math.sqrt(max(0.0, r_in ** 2 - a0 ** 2)))
        y1 = min(crown, zc + math.sqrt(max(0.0, r_in ** 2 - a1 ** 2)))
        umin, umax = min(a0, a1), max(a0, a1)
        zm = min(y0, y1)
        slab(mb, mp, u_c + umin, u_c + umax, zm, max(y0, y1) + ring_w, -proud, depth * 0.5, mat_ring)

    # Central keystone
    slab(mb, mp, u_c - 0.12, u_c + 0.12, crown - 0.05, crown + ring_w + 0.08, -proud - 0.02, depth * 0.55, "sandstone")


def flat_lintel(mb, mp, u0, u1, z1, mat="sandstone", depth=0.25, thick=0.20, proud=0.035):
    slab(mb, mp, u0 - 0.06, u1 + 0.06, z1, z1 + thick, -proud, depth, mat)


# ---------------------------------------------------------------- doors & hoists
def door(mb, mp, u0, u1, z0, z1, depth, mat_panel="timber", mat_frame="paint_green",
         planks=4, fanlight=False):
    t = 0.08
    slab(mb, mp, u0, u0 + t, z0, z1, 0.0, depth * 0.6, mat_frame)
    slab(mb, mp, u1 - t, u1, z0, z1, 0.0, depth * 0.6, mat_frame)
    slab(mb, mp, u0, u1, z1 - t, z1, 0.0, depth * 0.6, mat_frame)
    zt = z1 - (0.55 if fanlight else t)
    if fanlight:
        slab(mb, mp, u0 + t, u1 - t, zt, z1 - t, depth * 0.45, depth * 0.47, "glass_lit")
    slab(mb, mp, u0 + t, u1 - t, z0, zt, depth * 0.42, depth * 0.50, mat_panel)
    w = u1 - u0 - 2 * t
    for i in range(1, planks):
        uu = u0 + t + w * i / planks
        slab(mb, mp, uu - 0.012, uu + 0.012, z0, zt, depth * 0.38, depth * 0.42, "black")
    # Cast iron door knob / latch
    uc = (u0 + u1) / 2
    slab(mb, mp, uc + 0.25, uc + 0.32, z0 + 1.0, z0 + 1.08, depth * 0.30, depth * 0.42, "brass")


def hoist_door(mb, mp, u0, u1, z0, z1, depth, mat="timber"):
    """Warehouse loading door: vertical boarded double doors + projecting cathead hoist."""
    t = 0.09
    uc = (u0 + u1) / 2
    # Heavy timber outer frame
    slab(mb, mp, u0, u0 + t, z0, z1, 0.0, depth * 0.7, "paint_green")
    slab(mb, mp, u1 - t, u1, z0, z1, 0.0, depth * 0.7, "paint_green")
    slab(mb, mp, u0, u1, z1 - t, z1, 0.0, depth * 0.7, "paint_green")
    # Paired double doors
    slab(mb, mp, u0 + t, uc - 0.01, z0 + 0.04, z1 - t, depth * 0.35, depth * 0.46, mat)
    slab(mb, mp, uc + 0.01, u1 - t, z0 + 0.04, z1 - t, depth * 0.35, depth * 0.46, mat)
    # Iron strap hinges (top and bottom on both leaves)
    for zh in (z0 + 0.35, z1 - t - 0.45):
        slab(mb, mp, u0 + t, u0 + (u1 - u0) * 0.38, zh, zh + 0.06, depth * 0.30, depth * 0.35, "iron")
        slab(mb, mp, u1 - (u1 - u0) * 0.38, u1 - t, zh, zh + 0.06, depth * 0.30, depth * 0.35, "iron")
    # Locking bar across center
    slab(mb, mp, uc - 0.25, uc + 0.25, z0 + (z1 - z0) * 0.5, z0 + (z1 - z0) * 0.5 + 0.06,
         depth * 0.28, depth * 0.35, "iron")

    # Projecting cathead timber beam + pulley + hanging chain
    p_beam = mp(uc, z1 + 0.35, -1.25)
    slab(mb, mp, uc - 0.12, uc + 0.12, z1 + 0.20, z1 + 0.40, -1.30, 0.20, "timber")
    # Angled iron diagonal brace
    p_wall = mp(uc, z1 - 0.60, 0.0)
    mb.add_beam(p_wall, p_beam, 0.08, 0.08, "iron")
    # Pulley housing & wheel
    mb.add_box_c(p_beam[0], p_beam[1], p_beam[2] - 0.15, 0.24, 0.24, 0.28, "iron")
    # Hanging hoist chain & hook
    mb.add_beam((p_beam[0], p_beam[1], p_beam[2] - 0.28),
                (p_beam[0], p_beam[1], z0 + 0.8), 0.03, 0.03, "black")
    mb.add_box_c(p_beam[0], p_beam[1], z0 + 0.72, 0.16, 0.12, 0.22, "iron")


# ---------------------------------------------------------------- horizontal features
def string_course(mb, mp, u0, u1, z, mat="sandstone", h=0.18, proj=0.085, depth=0.30):
    slab(mb, mp, u0, u1, z, z + h, -proj, depth, mat)


def cornice(mb, mp, u0, u1, z, mat="sandstone", proj=0.36, h=0.32, brackets=True, ustep=1.4):
    """Projecting cornice with dentils/brackets."""
    slab(mb, mp, u0, u1, z, z + h * 0.55, -proj * 0.55, 0.35, mat)
    slab(mb, mp, u0, u1, z + h * 0.55, z + h, -proj, 0.35, mat)
    slab(mb, mp, u0, u1, z + h, z + h + 0.10, -proj * 1.08, 0.30, mat)   # top drip
    if brackets:
        n = max(1, int((u1 - u0) / ustep))
        for i in range(n):
            uu = u0 + (u1 - u0) * (i + 0.5) / n
            slab(mb, mp, uu - 0.065, uu + 0.065, z - 0.16, z + h * 0.55, -proj * 0.8, 0.12, mat)


def dentil_course(mb, mp, u0, u1, z, mat="brick_red", step=0.22, proj=0.05):
    """Corbelled brick dentil course under eaves."""
    slab(mb, mp, u0, u1, z, z + 0.08, -proj * 0.4, 0.30, mat)
    n = max(1, int((u1 - u0) / step))
    for i in range(n):
        uu = u0 + (u1 - u0) * (i + 0.5) / n
        slab(mb, mp, uu - 0.05, uu + 0.05, z + 0.08, z + 0.22, -proj, 0.25, mat)
    slab(mb, mp, u0, u1, z + 0.22, z + 0.28, -proj * 0.6, 0.30, mat)


def quoin(mb, mp, z0, z1, u_edge, mat="sandstone", w=0.55, h=0.32, outward=-1):
    """Alternating stone quoins at a building corner."""
    z = z0
    i = 0
    while z < z1:
        cw = w if i % 2 == 0 else w * 0.65
        if outward < 0:
            slab(mb, mp, u_edge, u_edge + cw, z, min(z + h, z1), -0.03, 0.30, mat)
        else:
            slab(mb, mp, u_edge - cw, u_edge, z, min(z + h, z1), -0.03, 0.30, mat)
        z += h
        i += 1


def plinth(mb, mp, u0, u1, z0, h=0.65, mat="brick_blue", proj=0.065):
    slab(mb, mp, u0, u1, z0, z0 + h, -proj, 0.45, mat)
    # Chamfered stone plinth capping
    slab(mb, mp, u0, u1, z0 + h, z0 + h + 0.08, -proj * 1.15, 0.40, "granite")


def parapet(mb, mp, u0, u1, z_top, h=0.90, mat="brick_soot", cap="granite", thick=0.35):
    slab(mb, mp, u0, u1, z_top, z_top + h, 0.0, thick, mat)
    slab(mb, mp, u0, u1, z_top + h, z_top + h + 0.10, -0.05, thick + 0.05, cap)


def railing(mb, mp, u0, u1, z, mat="iron", h=1.05, spacing=1.8):
    """Cast-iron railing: standards, top rail, intermediate rail, balusters."""
    n = max(1, int((u1 - u0) / spacing))
    for i in range(n + 1):
        uu = u0 + (u1 - u0) * i / n
        slab(mb, mp, uu - 0.04, uu + 0.04, z, z + h, 0.35, 0.43, mat)
    for zz in (z + h - 0.05, z + 0.18):
        slab(mb, mp, u0, u1, zz, zz + 0.05, 0.36, 0.41, mat)
    nb = int((u1 - u0) / 0.14)
    for i in range(nb):
        uu = u0 + (u1 - u0) * (i + 0.5) / nb
        slab(mb, mp, uu - 0.012, uu + 0.012, z + 0.20, z + h - 0.05, 0.375, 0.395, mat)


def downpipe(mb, mp, u, z0, z1, mat="iron"):
    """Cast-iron rainwater downpipe with ornate hopper head at top and shoe at bottom."""
    p0 = mp(u, z0, -0.08)
    p1 = mp(u, z1 - 0.45, -0.08)
    # Main circular pipe
    mb.add_cyl(p0[0], p0[1], z0, z1 - 0.45, 0.055, mat, seg=8)
    # Pipe brackets / ears every 2.2 m
    h = z1 - z0 - 0.45
    nb = max(1, int(h / 2.2))
    for i in range(nb + 1):
        zb = z0 + h * i / nb
        pb = mp(u, zb, 0.0)
        mb.add_box_c(pb[0], pb[1], zb, 0.22, 0.22, 0.06, mat)
    # Rainwater hopper head at eaves
    ph = mp(u, z1 - 0.22, -0.09)
    mb.add_box_c(ph[0], ph[1], z1 - 0.22, 0.34, 0.30, 0.40, mat)
    mb.add_box_c(ph[0], ph[1], z1 - 0.04, 0.38, 0.34, 0.08, mat)
    # Shoe bend at pavement level
    ps = mp(u, z0 + 0.12, -0.14)
    mb.add_cyl(ps[0], ps[1], z0, z0 + 0.18, 0.06, mat, seg=8)


def chimney_stack(mb, x, y, z0, h, w=1.2, d=0.9, mat="brick_soot", pots=3):
    """Brick chimney stack with corbelled crown and cylindrical terracotta pots."""
    mb.add_box_c(x, y, z0 + h / 2, w, d, h, mat)
    # Corbelled oversailing courses
    mb.add_box_c(x, y, z0 + h - 0.18, w + 0.08, d + 0.08, 0.08, mat)
    mb.add_box_c(x, y, z0 + h - 0.08, w + 0.16, d + 0.16, 0.08, "sandstone")
    mb.add_box_c(x, y, z0 + h + 0.04, w + 0.22, d + 0.22, 0.08, "sandstone")
    # Terracotta pots
    for i in range(pots):
        px = x - w / 2 + w * (i + 0.5) / pots
        mb.add_cyl(px, y, z0 + h + 0.08, z0 + h + 0.65, 0.12, "terracotta", seg=8)


def clock_face(mb, x, y, z, r=0.60, axis="Y", mat="paint_white"):
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
    mb.add_box_c(x if axis == "Y" else x - 0.03, y - 0.03 if axis == "Y" else y, z + 0.22,
                 0.05, 0.05, 0.44, "black")
    mb.add_box_c(x if axis == "Y" else x - 0.05, y - 0.05 if axis == "Y" else y, z + 0.14,
                 0.30, 0.05, 0.05, "black")


# ---------------------------------------------------------------- wall panel
def wall_panel(mb, axis, fixed, u0, u1, z0, z1, thick, inward, mat,
               holes=(), top_mat=None):
    """Solid wall pierced by rectangular openings, built as horizontal bands."""
    if not holes:
        mp = wmap(axis, fixed, inward)
        slab(mb, mp, u0, u1, z0, z1, 0.0, thick, mat, top=top_mat)
        return

    z_cuts = {z0, z1}
    for h in holes:
        z_cuts.add(max(z0, min(z1, h[2])))
        z_cuts.add(max(z0, min(z1, h[3])))
    z_sorted = sorted(z_cuts)

    mp = wmap(axis, fixed, inward)

    for i in range(len(z_sorted) - 1):
        za, zb = z_sorted[i], z_sorted[i + 1]
        if zb - za < 1e-5:
            continue
        zm = (za + zb) / 2
        active_holes = [(h[0], h[1]) for h in holes if h[2] <= zm <= h[3]]
        spans = spans_minus(u0, u1, active_holes)
        for ua, ub in spans:
            slab(mb, mp, ua, ub, za, zb, 0.0, thick, mat,
                 top=(top_mat if abs(zb - z1) < 1e-4 else None))

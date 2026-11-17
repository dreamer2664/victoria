"""
bldg.py -- Victorian maritime building generators.
GENERATION II — OPERATION VICTORIA (PERICLES-II)

Every generator builds a complete asset in local metres with its origin at the
south-west ground corner, so it can be dropped straight into a layout grid.
"""
import math
from core import MeshBuilder
import parts as P


# ================================================================ helpers
def perimeter(x0, y0, x1, y1):
    """Four (axis, fixed, u0, u1, inward) wall definitions for a rectangular block."""
    return [
        ("X", y0, x0, x1, +1, "S"),
        ("X", y1, x0, x1, -1, "N"),
        ("Y", x0, y0, y1, +1, "W"),
        ("Y", x1, y0, y1, -1, "E"),
    ]


def _bay_centres(u0, u1, bay, margin=0.0):
    w = (u1 - u0) - 2 * margin
    n = max(1, int(round(w / bay)))
    step = w / n
    return [u0 + margin + step * (i + 0.5) for i in range(n)], step


def sign_board(mb, mp, u, z, w, h, tex, d=0.045):
    """A painted board fixed flat to a wall, with a light frame."""
    P.slab(mb, mp, u - w / 2 - 0.06, u + w / 2 + 0.06, z - h / 2 - 0.06, z + h / 2 + 0.06,
           -d - 0.03, -0.005, "timber")
    a = mp(u - w / 2, z - h / 2, -d)
    b = mp(u + w / 2, z - h / 2, -d)
    c = mp(u + w / 2, z + h / 2, -d)
    dd = mp(u - w / 2, z + h / 2, -d)
    mb.add_quad_uv(a, b, c, dd, tex)


# ================================================================ 1. WAREHOUSE
def warehouse(mb, x0, y0, w, d, floors=4, ground_h=4.2, h_floor=3.35,
              bay=3.55, wall="brick_soot", trim="sandstone",
              roof="gable", pitch=36, hoist_side="S", hoist_bays=(1,),
              parapet_h=0.95, plinth_h=0.60, chimney=True, blind_ratio=0.0):
    """A Liverpool/Bristol/Belfast multi-storey dock warehouse with authentic depth."""
    x1, y1 = x0 + w, y0 + d
    t = 0.45                                   # wall thickness
    z_top = ground_h + h_floor * (floors - 1)
    z_par = z_top

    sides = perimeter(x0, y0, x1, y1)

    for axis, fixed, u0, u1, inward, tag in sides:
        mp = P.wmap(axis, fixed, inward)
        cs, step = _bay_centres(u0, u1, bay, margin=0.75)
        holes = []
        # ground floor: cart/dray openings
        for i, uc in enumerate(cs):
            ww = min(1.9, step * 0.52)
            zt = ground_h - 0.55
            holes.append((uc - ww / 2, uc + ww / 2, 0.9, zt))
        # upper floors: sash windows
        for f in range(1, floors):
            z0 = ground_h + h_floor * (f - 1) + 0.95
            z1 = z0 + 1.95
            for uc in cs:
                ww = min(1.42, step * 0.42)
                holes.append((uc - ww / 2, uc + ww / 2, z0, z1))
        # hoist doors: full-height openings on nominated side
        if tag == hoist_side:
            for b in hoist_bays:
                if b < len(cs):
                    uc = cs[b]
                    for f in range(floors):
                        z0 = (0.9 if f == 0 else ground_h + h_floor * (f - 1) + 0.35)
                        z1 = (ground_h - 0.55 if f == 0
                              else ground_h + h_floor * f - 0.55)
                        holes.append((uc - 1.35, uc + 1.35, z0, z1))

        holes = [(max(u0 + 0.3, a), min(u1 - 0.3, b), c, e) for a, b, c, e in holes]
        holes = [h for h in holes if h[1] > h[0] and h[3] > h[2]]
        P.wall_panel(mb, axis, fixed, u0, u1, 0.0, z_par, t, inward, wall, holes)

        # ---- decoration & openings
        P.plinth(mb, mp, u0, u1, 0.0, h=plinth_h, mat="brick_blue", proj=0.06)
        for i, uc in enumerate(cs):
            ww = min(1.9, step * 0.52)
            P.segmental_arch(mb, mp, uc, ww / 2 + 0.16, ground_h - 0.55,
                             0.52, t, mat_ring=trim, mat_tympanum="brick_blue",
                             voussoirs=7)
            P.slab(mb, mp, uc - ww / 2 + 0.09, uc + ww / 2 - 0.09, 0.9, ground_h - 0.62,
                   t * 0.30, t * 0.36, "timber")
            for k in range(1, 6):
                uu = uc - ww / 2 + 0.09 + (ww - 0.18) * k / 6
                P.slab(mb, mp, uu - 0.012, uu + 0.012, 0.9, ground_h - 0.62,
                       t * 0.28, t * 0.30, "black")
        for f in range(1, floors):
            z0 = ground_h + h_floor * (f - 1) + 0.95
            for uc in cs:
                ww = min(1.42, step * 0.42)
                blind = ((i * 7 + f * 3) % 11 == 0)
                P.sash_window(mb, mp, uc - ww / 2, uc + ww / 2, z0, z0 + 1.95, t,
                              panes_x=2, panes_y=2, blind=blind)
                P.stone_sill(mb, mp, uc - ww / 2, uc + ww / 2, z0, trim)
                P.window_hood(mb, mp, uc - ww / 2, uc + ww / 2, z0 + 1.95, trim,
                              proj=0.10, thick=0.09)
            P.string_course(mb, mp, u0, u1, z0 - 0.18, trim, h=0.14, proj=0.06)

        if tag == hoist_side:
            for b in hoist_bays:
                if b >= len(cs):
                    continue
                uc = cs[b]
                for f in range(floors):
                    z0 = (0.9 if f == 0 else ground_h + h_floor * (f - 1) + 0.35)
                    z1 = (ground_h - 0.55 if f == 0 else ground_h + h_floor * f - 0.55)
                    P.hoist_door(mb, mp, uc - 1.35, uc + 1.35, z0, z1, t)

        # Quoins and Cornice
        P.quoin(mb, mp, plinth_h, z_par - 0.3, u0 + 0.30, trim, outward=+1)
        P.quoin(mb, mp, plinth_h, z_par - 0.3, u1 - 0.30, trim, outward=-1)
        P.dentil_course(mb, mp, u0, u1, z_par - 0.65, mat="brick_red")
        P.cornice(mb, mp, u0, u1, z_par - 0.34, trim, proj=0.36, h=0.34, ustep=step)
        P.parapet(mb, mp, u0, u1, z_par, h=parapet_h, mat=wall, cap="granite")

        # Cast-iron rainwater downpipes
        P.downpipe(mb, mp, u0 + 1.2, 0.0, z_par - 0.34)
        P.downpipe(mb, mp, u1 - 1.2, 0.0, z_par - 0.34)

    # Interior core
    mb.add_box(x0 + 0.55, y0 + 0.55, 0.0, x1 - 0.55, y1 - 0.55,
               z_par - 0.32, "interior")

    # Roof with solid gables
    if roof == "gable":
        mb.add_gable_roof(x0, y0, x1, y1, z_par, pitch, "slate",
                          gable=("X" if w >= d else "Y"), overhang=0.32,
                          end_mat=wall)
    elif roof == "hip":
        mb.add_hip_roof(x0, y0, x1, y1, z_par, pitch, "slate", overhang=0.32)

    mb.add_box(x0 + 0.2, y0 + 0.2, z_par - 0.30, x1 - 0.2, y1 - 0.2, z_par, "timber")

    # Roof lights and chimneys
    if w > 18:
        lx = (x0 + x1) / 2
        ry = (y0 + y1) / 2
        rise = (min(w, d) / 2) * math.tan(math.radians(pitch))
        for k in (-1, 1):
            cx = lx + k * min(w, d) * 0.22
            mb.add_box_c(cx, ry, z_par + rise * 0.55, 2.4, 5.0, 1.1, "slate")
            mb.add_box_c(cx, ry, z_par + rise * 0.55 + 0.62, 1.9, 4.5, 0.10, "glass")
    if chimney:
        P.chimney_stack(mb, x0 + 0.9, y1 - 0.9, z_par, 3.6, 0.95, 0.75, wall, pots=3)

    return dict(kind="warehouse", x0=x0, y0=y0, w=w, d=d, floors=floors, z_top=z_par)


# ================================================================ 2. TRANSIT SHED
def transit_shed(mb, x0, y0, w, d, h_eave=6.2, bay=4.6, wall="brick_buff",
                 open_side="S", roof_pitch=32, roof="gable", doors=2,
                 interior=True, lantern=True):
    """A single-storey cargo/passenger transit shed with continuous cart doors and queen-post trusses."""
    x1, y1 = x0 + w, y0 + d
    t = 0.40
    sides = perimeter(x0, y0, x1, y1)
    for axis, fixed, u0, u1, inward, tag in sides:
        mp = P.wmap(axis, fixed, inward)
        cs, step = _bay_centres(u0, u1, 5.6)
        holes = []
        if tag == open_side:
            for uc in cs:
                ww = min(3.9, step * 0.66)
                holes.append((uc - ww / 2, uc + ww / 2, 0.0, h_eave - 1.15))
        else:
            for uc in cs:
                ww = min(2.4, step * 0.44)
                holes.append((uc - ww / 2, uc + ww / 2, 1.55, h_eave - 1.35))
        P.wall_panel(mb, axis, fixed, u0, u1, 0.0, h_eave, t, inward, wall, holes)
        P.plinth(mb, mp, u0, u1, 0.0, h=0.5, mat="brick_blue", proj=0.05)
        for uc in cs:
            if tag == open_side:
                ww = min(3.9, step * 0.66)
                P.segmental_arch(mb, mp, uc, ww / 2 + 0.18, h_eave - 1.15, 0.62, t,
                                 mat_ring="brick_blue", mat_tympanum=wall, voussoirs=9)
            else:
                ww = min(2.4, step * 0.44)
                P.sash_window(mb, mp, uc - ww / 2, uc + ww / 2, 1.55, h_eave - 1.35, t,
                              panes_x=3, panes_y=2)
                P.stone_sill(mb, mp, uc - ww / 2, uc + ww / 2, 1.55)
        P.string_course(mb, mp, u0, u1, h_eave - 0.30, "sandstone", h=0.22, proj=0.10)
        P.cornice(mb, mp, u0, u1, h_eave - 0.08, "sandstone", proj=0.28, h=0.26, ustep=2.0)
        P.downpipe(mb, mp, u0 + 1.0, 0.0, h_eave - 0.08)
        P.downpipe(mb, mp, u1 - 1.0, 0.0, h_eave - 0.08)

    z_r = h_eave
    if roof == "gable":
        z_r = mb.add_gable_roof(x0, y0, x1, y1, h_eave, roof_pitch, "slate",
                                gable=("X" if w >= d else "Y"), overhang=0.40, end_mat=wall)
    else:
        z_r = mb.add_hip_roof(x0, y0, x1, y1, h_eave, roof_pitch, "slate", overhang=0.40)

    if interior:
        _shed_interior(mb, x0, y0, x1, y1, h_eave, bay, z_r, lantern)
    else:
        mb.add_box(x0, y0, h_eave - 0.2, x1, y1, h_eave, "timber")
    return dict(kind="transit_shed", x0=x0, y0=y0, w=w, d=d, z_eave=h_eave, z_ridge=z_r)


def _shed_interior(mb, x0, y0, x1, y1, h_eave, bay, z_r, lantern=True):
    ncol = max(1, int((y1 - y0) / 5.5))
    for i in range(ncol):
        cy = y0 + (y1 - y0) * (i + 0.5) / ncol
        for cx in ((x0 + x1) / 2,):
            mb.add_cyl(cx, cy, 0.0, h_eave - 0.15, 0.17, "iron", seg=10, r2=0.14)
            mb.add_box_c(cx, cy, 0.12, 0.55, 0.55, 0.24, "granite")
            mb.add_box_c(cx, cy, h_eave - 0.22, 0.42, 0.42, 0.14, "iron")
    nt = max(1, int((x1 - x0) / bay))
    for i in range(nt + 1):
        tx = x0 + (x1 - x0) * i / nt
        _queen_truss(mb, tx, y0, y1, h_eave, z_r)
    for i in range(nt):
        for yy in (y0 + (y1 - y0) * 0.18, y0 + (y1 - y0) * 0.82):
            mb.add_beam((x0 + (x1 - x0) * i / nt, yy, h_eave + (z_r - h_eave) * 0.55),
                        (x0 + (x1 - x0) * (i + 1) / nt, yy, h_eave + (z_r - h_eave) * 0.55),
                        0.12, 0.18, "timber")
    if lantern:
        mb.add_box(x0 + 0.5, (y0 + y1) / 2 - 1.1, z_r - 0.05,
                   x1 - 0.5, (y0 + y1) / 2 + 1.1, z_r + 0.55, "iron")
        mb.add_box(x0 + 0.7, (y0 + y1) / 2 - 0.9, z_r + 0.55,
                   x1 - 0.7, (y0 + y1) / 2 + 0.9, z_r + 0.60, "glass")
    platform = y0 + (y1 - y0) * 0.12
    mb.add_box(x0 + 1.0, y0 + 0.5, 0.0, x1 - 1.0, platform, 1.05, "plank")
    mb.add_box(x0 + 1.0, platform - 0.06, 0.0, x1 - 1.0, platform, 1.05, "timber")


def _queen_truss(mb, tx, y0, y1, h_eave, z_r):
    ym = (y0 + y1) / 2
    tie = h_eave + 0.35
    mb.add_beam((tx, y0, tie), (tx, y1, tie), 0.11, 0.30, "timber")
    mb.add_beam((tx, y0, h_eave - 0.1), (tx, ym, z_r), 0.11, 0.26, "timber")
    mb.add_beam((tx, y1, h_eave - 0.1), (tx, ym, z_r), 0.11, 0.26, "timber")
    for k in (0.34, 0.66):
        yy = y0 + (y1 - y0) * k
        zz = h_eave + (z_r - h_eave) * (1 - abs(k - 0.5) * 2) * 0.92
        mb.add_beam((tx, yy, tie), (tx, yy, zz), 0.09, 0.16, "timber")
        mb.add_beam((tx, yy, zz), (tx, ym, z_r - 0.05), 0.08, 0.13, "timber")
    mb.add_beam((tx, ym, tie), (tx, ym, z_r), 0.08, 0.14, "timber")


# ================================================================ 3. CUSTOM HOUSE
def custom_house(mb, x0, y0, w=62.0, d=34.0, storeys=3, wall="sandstone"):
    """Civic Italianate Custom House with rusticated base, giant order, portico and dome."""
    x1, y1 = x0 + w, y0 + d
    gh = 6.4
    sh = 4.5
    z_top = gh + sh * (storeys - 1)
    t = 0.9
    for axis, fixed, u0, u1, inward, tag in perimeter(x0, y0, x1, y1):
        mp = P.wmap(axis, fixed, inward)
        cs, step = _bay_centres(u0, u1, 4.5, margin=1.2)
        holes = []
        for uc in cs:
            holes.append((uc - 0.98, uc + 0.98, 0.85, gh - 1.75))
            for f in range(1, storeys):
                z0 = gh + sh * (f - 1) + 1.05
                holes.append((uc - 0.95, uc + 0.95, z0, z0 + 2.55))
        P.wall_panel(mb, axis, fixed, u0, u1, 0.0, z_top, t, inward, wall, holes)
        zh = 0.0
        while zh < gh - 1.1:
            P.string_course(mb, mp, u0, u1, zh, wall, h=0.055, proj=0.030, depth=0.10)
            zh += 0.82
        for uc in cs:
            P.segmental_arch(mb, mp, uc, 1.12, gh - 1.75, 0.42, t,
                             mat_ring=wall, mat_tympanum=wall, voussoirs=9, ring_w=0.30)
            P.sash_window(mb, mp, uc - 0.98, uc + 0.98, 0.85, gh - 1.75, t, panes_x=3, panes_y=3)
            for f in range(1, storeys):
                z0 = gh + sh * (f - 1) + 1.05
                P.sash_window(mb, mp, uc - 0.95, uc + 0.95, z0, z0 + 2.55, t,
                              panes_x=2, panes_y=3)
                P.stone_sill(mb, mp, uc - 0.95, uc + 0.95, z0, wall, proj=0.14, thick=0.12)
                P.window_hood(mb, mp, uc - 0.95, uc + 0.95, z0 + 2.55, wall,
                              proj=0.20, thick=0.20)
        P.plinth(mb, mp, u0, u1, 0.0, h=0.75, mat="granite", proj=0.10)
        P.string_course(mb, mp, u0, u1, gh - 0.35, wall, h=0.40, proj=0.22, depth=0.5)
        P.string_course(mb, mp, u0, u1, z_top - 0.55, wall, h=0.30, proj=0.18)
        P.cornice(mb, mp, u0, u1, z_top - 0.12, wall, proj=0.62, h=0.55, ustep=2.2)
        P.railing(mb, mp, u0, u1, z_top + 0.42, "paint_white", h=1.0, spacing=2.0)
        P.string_course(mb, mp, u0, u1, z_top + 0.42, wall, h=0.18, proj=0.16, depth=0.7)

    mb.add_box(x0 + 0.95, y0 + 0.95, 0.0, x1 - 0.95, y1 - 0.95,
               z_top - 0.40, "interior")
    z_r = mb.add_hip_roof(x0, y0, x1, y1, z_top + 0.42, 22, "slate", overhang=0.5)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    _dome(mb, cx, cy, z_r - 0.4, 7.0)
    _portico(mb, cx, y0, gh, 8.6)
    return dict(kind="custom_house", x0=x0, y0=y0, w=w, d=d, z_top=z_top)


def _portico(mb, cx, y0, gh, half_w):
    for i in range(4):
        px = cx - half_w + 2 * half_w * i / 3
        mb.add_cyl(px, y0 - 1.6, 0.0, gh, 0.42, "sandstone", seg=12, r2=0.36)
        mb.add_box_c(px, y0 - 1.6, 0.18, 1.1, 1.1, 0.36, "sandstone")
        mb.add_box_c(px, y0 - 1.6, gh + 0.18, 1.0, 1.0, 0.36, "sandstone")
    mb.add_box(cx - half_w - 1.3, y0 - 2.6, gh, cx + half_w + 1.3, y0 - 0.2, gh + 0.95, "sandstone")
    zt = gh + 0.95
    mb.add_tri((cx - half_w - 1.3, y0 - 2.6, zt), (cx, y0 - 2.6, zt + 2.2),
               (cx + half_w + 1.3, y0 - 2.6, zt), "sandstone")
    mb.add_tri((cx + half_w + 1.3, y0 - 0.2, zt), (cx, y0 - 0.2, zt + 2.2),
               (cx - half_w - 1.3, y0 - 0.2, zt), "sandstone")
    mb.add_box_c(cx, y0 - 1.4, zt + 0.9, half_w * 2 + 2.6, 2.5, 0.5, "sandstone")
    mb.add_quad_uv((cx - 3.2, y0 - 2.62, zt + 0.15), (cx + 3.2, y0 - 2.62, zt + 0.15),
                   (cx + 3.2, y0 - 2.62, zt + 0.85), (cx - 3.2, y0 - 2.62, zt + 0.85),
                   "sign_custom_house")


def _dome(mb, cx, cy, z0, r):
    """Optimized lead-covered dome with lantern (under 8k tris)."""
    mb.add_cyl(cx, cy, z0, z0 + 3.2, r * 0.92, "sandstone", seg=16)
    for i in range(12):
        a = 2 * math.pi * i / 12
        mb.add_cyl(cx + math.cos(a) * r * 0.86, cy + math.sin(a) * r * 0.86,
                   z0 + 0.1, z0 + 3.1, 0.20, "sandstone", seg=6)
    mb.add_cyl(cx, cy, z0 + 3.2, z0 + 3.7, r * 0.98, "sandstone", seg=16)
    rings = 8
    seg = 16
    for i in range(rings):
        t0, t1 = i / rings, (i + 1) / rings
        r0 = r * math.cos(t0 * math.pi / 2) * 0.96
        r1 = r * math.cos(t1 * math.pi / 2) * 0.96
        zz0 = z0 + 3.7 + math.sin(t0 * math.pi / 2) * r * 1.02
        zz1 = z0 + 3.7 + math.sin(t1 * math.pi / 2) * r * 1.02
        mb.add_cyl(cx, cy, zz0, zz1, max(r0, 0.02), "lead", seg=seg,
                   r2=max(r1, 0.02), cap=False)
    for k in range(12):
        a = 2 * math.pi * k / 12
        for i in range(rings):
            t0, t1 = i / rings, (i + 1) / rings
            r0 = r * math.cos(t0 * math.pi / 2) * 0.96
            r1 = r * math.cos(t1 * math.pi / 2) * 0.96
            zz0 = z0 + 3.7 + math.sin(t0 * math.pi / 2) * r * 1.02
            zz1 = z0 + 3.7 + math.sin(t1 * math.pi / 2) * r * 1.02
            mb.add_beam((cx + math.cos(a) * r0, cy + math.sin(a) * r0, zz0),
                        (cx + math.cos(a) * r1, cy + math.sin(a) * r1, zz1),
                        0.09, 0.06, "lead")
    top = z0 + 3.7 + r * 1.02
    mb.add_cyl(cx, cy, top, top + 1.5, 0.75, "sandstone", seg=10)
    mb.add_cyl(cx, cy, top + 1.5, top + 2.4, 0.8, "glass", seg=10)
    mb.add_cyl(cx, cy, top + 2.4, top + 2.9, 0.15, "copper", seg=8, r2=0.02)
    mb.add_cyl(cx, cy, top + 2.9, top + 4.2, 0.03, "iron", seg=6)


# ================================================================ 4. STATION SHED
def station_shed(mb, x0, y0, w, d, tracks=2, h_spring=6.4, rise=3.2, bay=5.0,
                 wall="brick_buff", platform_h=1.05):
    """A single-span arched iron train shed with glazed ridge and side platforms."""
    x1, y1 = x0 + w, y0 + d
    t = 0.42
    z_eave = h_spring
    for axis, fixed, u0, u1, inward, tag in perimeter(x0, y0, x1, y1):
        mp = P.wmap(axis, fixed, inward)
        cs, step = _bay_centres(u0, u1, 4.4)
        holes = []
        for uc in cs:
            holes.append((uc - 0.95, uc + 0.95, 1.15, z_eave - 1.25))
        P.wall_panel(mb, axis, fixed, u0, u1, 0.0, z_eave, t, inward, wall, holes)
        P.plinth(mb, mp, u0, u1, 0.0, h=0.55, mat="brick_blue", proj=0.05)
        for uc in cs:
            P.sash_window(mb, mp, uc - 0.95, uc + 0.95, 1.15, z_eave - 1.25, t,
                          panes_x=2, panes_y=3)
            P.segmental_arch(mb, mp, uc, 1.12, z_eave - 1.25, 0.42, t,
                             mat_ring="brick_blue", mat_tympanum=wall, voussoirs=7)
        P.cornice(mb, mp, u0, u1, z_eave - 0.10, "sandstone", proj=0.26, h=0.24, ustep=2.0)

    for axis, fixed, u0, u1, inward, tag, inw in (("X", y0, x0, x1, +1, "S", +1),
                                                  ("X", y1, x0, x1, -1, "N", -1)):
        mp = P.wmap(axis, fixed, inward)
        hole_w = 2.4 + tracks * 4.6
        cxu = (x0 + x1) / 2
        P.wall_panel(mb, axis, fixed, u0, u1, z_eave, z_eave + rise + 0.6, t, inward, wall,
                     [(cxu - hole_w / 2, cxu + hole_w / 2, z_eave, z_eave + rise - 0.3)])
        P.segmental_arch(mb, mp, cxu, hole_w / 2 + 0.2, z_eave, 1.0, t,
                         mat_ring="sandstone", mat_tympanum=wall, voussoirs=13)

    mb.add_box(x0 + 0.6, y0 + 0.6, 0.0, x1 - 0.6, y1 - 0.6, 0.02, "interior")
    nt = max(2, int((x1 - x0) / bay))
    for i in range(nt + 1):
        tx = x0 + (x1 - x0) * i / nt
        _arch_rib(mb, tx, x0, x1, y0, y1, h_spring, rise, section=0.28, mat="iron")
    _arch_shell(mb, x0, y0, x1, y1, h_spring, rise, nt)

    for k, yy in enumerate((y0 + 3.0, y1 - 3.0)):
        mb.add_box(x0 + 0.4, yy - 2.2, 0.0, x1 - 0.4, yy + 2.2, platform_h, "granite", top="plank")
        mb.add_box(x0 + 0.4, yy - 2.2, platform_h - 0.16, x1 - 0.4, yy + 2.2, platform_h, "granite")
        mb.add_box(x0 + 0.4, yy - 2.28, platform_h - 0.10, x1 - 0.4, yy - 2.20, platform_h + 0.01, "plank")
    return dict(kind="station_shed", x0=x0, y0=y0, w=w, d=d, z_ridge=h_spring + rise)


def _arch_rib(mb, tx, x0, x1, y0, y1, h_spring, rise, section=0.26, mat="iron"):
    n = 12
    for i in range(n):
        a0 = math.pi * i / n
        a1 = math.pi * (i + 1) / n
        p0 = (tx, (y0 + y1) / 2 - math.cos(a0) * (y1 - y0) / 2, h_spring + math.sin(a0) * rise)
        p1 = (tx, (y0 + y1) / 2 - math.cos(a1) * (y1 - y0) / 2, h_spring + math.sin(a1) * rise)
        mb.add_beam(p0, p1, section, section, mat)


def _arch_shell(mb, x0, y0, x1, y1, h_spring, rise, nt):
    n = 12
    for i in range(n):
        a0 = math.pi * i / n
        a1 = math.pi * (i + 1) / n
        ya = (y0 + y1) / 2 - math.cos(a0) * (y1 - y0) / 2
        yb = (y0 + y1) / 2 - math.cos(a1) * (y1 - y0) / 2
        za = h_spring + math.sin(a0) * rise
        zb = h_spring + math.sin(a1) * rise
        glazed = 0.30 < (i + 0.5) / n < 0.70
        m = "glass" if glazed else "slate"
        for k in range(nt):
            xa = x0 + (x1 - x0) * k / nt
            xb = x0 + (x1 - x0) * (k + 1) / nt
            mb.add_quad((xa, ya, za + 0.02), (xb, ya, za + 0.02),
                        (xb, yb, zb + 0.02), (xa, yb, zb + 0.02), m)


# ================================================================ 5. OFFICE / TERRACE
def office_block(mb, x0, y0, w, d, floors=4, ground_h=4.4, h_floor=3.5,
                 wall="stucco", trim="sandstone", shopfront=True, bays=None,
                 roof_pitch=34):
    """Commercial dock office terrace with pilasters, cornice and slate mansard."""
    x1, y1 = x0 + w, y0 + d
    t = 0.42
    z_top = ground_h + h_floor * (floors - 1)
    sides = perimeter(x0, y0, x1, y1)
    for axis, fixed, u0, u1, inward, tag in sides:
        mp = P.wmap(axis, fixed, inward)
        cs, step = _bay_centres(u0, u1, bays or 3.2, margin=0.6)
        holes = []
        for uc in cs:
            if shopfront:
                holes.append((uc - 1.30, uc + 1.30, 0.65, ground_h - 0.95))
            else:
                holes.append((uc - 0.62, uc + 0.62, 0.05, 2.65))
            for f in range(1, floors):
                z0 = ground_h + h_floor * (f - 1) + 0.90
                ww = 0.75 if f > 1 else 0.85
                holes.append((uc - ww, uc + ww, z0, z0 + (2.15 if f > 1 else 2.35)))
        P.wall_panel(mb, axis, fixed, u0, u1, 0.0, z_top, t, inward, wall, holes)
        P.plinth(mb, mp, u0, u1, 0.0, h=0.42, mat="granite", proj=0.05)
        for uc in cs:
            if shopfront:
                P.slab(mb, mp, uc - 1.30, uc + 1.30, 0.05, 0.65, 0.02, 0.30, "brick_blue")
                P.slab(mb, mp, uc - 1.20, uc + 1.20, 0.65, ground_h - 1.55, t * 0.55, t * 0.58, "glass")
                P.slab(mb, mp, uc - 1.30, uc + 1.30, ground_h - 1.20, ground_h - 0.45, -0.06, 0.25, "timber")
            else:
                P.door(mb, mp, uc - 0.62, uc + 0.62, 0.05, 2.65, t, fanlight=True)
            for f in range(1, floors):
                z0 = ground_h + h_floor * (f - 1) + 0.90
                ww = 0.75 if f > 1 else 0.85
                P.sash_window(mb, mp, uc - ww, uc + ww, z0, z0 + (2.15 if f > 1 else 2.35), t, panes_x=2, panes_y=2)
                P.stone_sill(mb, mp, uc - ww, uc + ww, z0, trim)
        P.cornice(mb, mp, u0, u1, z_top - 0.22, trim, proj=0.42, h=0.36, ustep=step)
        P.downpipe(mb, mp, u0 + 0.8, 0.0, z_top - 0.22)
    mb.add_box(x0 + 0.5, y0 + 0.5, 0.0, x1 - 0.5, y1 - 0.5, z_top - 0.2, "interior")
    mb.add_gable_roof(x0, y0, x1, y1, z_top, roof_pitch, "slate",
                      gable=("X" if w >= d else "Y"), overhang=0.28, end_mat=wall)
    return dict(kind="office_block", x0=x0, y0=y0, w=w, d=d, z_top=z_top)


# ================================================================ 6. PUMPING HOUSE
def pump_house(mb, x0, y0, w=16.0, d=12.0, wall="brick_soot", chimney_h=26.0):
    """Graving-dock pumping engine house with round-arched windows and octagonal chimney."""
    x1, y1 = x0 + w, y0 + d
    h_eave = 8.5
    t = 0.55
    for axis, fixed, u0, u1, inward, tag in perimeter(x0, y0, x1, y1):
        mp = P.wmap(axis, fixed, inward)
        cs, step = _bay_centres(u0, u1, 4.2)
        holes = []
        for uc in cs:
            holes.append((uc - 1.05, uc + 1.05, 1.55, h_eave - 1.4))
        P.wall_panel(mb, axis, fixed, u0, u1, 0.0, h_eave, t, inward, wall, holes)
        for uc in cs:
            P.segmental_arch(mb, mp, uc, 1.05, h_eave - 1.4, 0.78, t,
                             mat_ring="brick_blue", mat_tympanum=wall, voussoirs=9, ring_w=0.32)
            P.sash_window(mb, mp, uc - 1.05, uc + 1.05, 1.55, h_eave - 1.4, t,
                          panes_x=3, panes_y=4)
        P.plinth(mb, mp, u0, u1, 0.0, h=0.7, mat="brick_blue", proj=0.07)
        P.cornice(mb, mp, u0, u1, h_eave - 0.20, "sandstone", proj=0.3, h=0.3, ustep=2.0)
        P.downpipe(mb, mp, u0 + 0.8, 0.0, h_eave - 0.20)
    mb.add_box(x0 + 0.65, y0 + 0.65, 0.0, x1 - 0.65, y1 - 0.65, h_eave - 0.2, "interior")
    mb.add_gable_roof(x0, y0, x1, y1, h_eave, 42, "slate", gable="Y", overhang=0.35, end_mat=wall)
    cx, cy = x0 + w - 3.0, y0 + 2.5
    seg = 8
    for i in range(10):
        t0, t1 = i / 10, (i + 1) / 10
        r0 = 1.55 * (1 - 0.42 * t0)
        r1 = 1.55 * (1 - 0.42 * t1)
        mb.add_cyl(cx, cy, t0 * chimney_h, t1 * chimney_h, r0, "brick_soot", seg=seg, r2=r1)
    mb.add_cyl(cx, cy, chimney_h, chimney_h + 0.5, 0.92, "sandstone", seg=seg)
    return dict(kind="pump_house", x0=x0, y0=y0, chimney=(cx, cy, chimney_h))


# ================================================================ 7. ENGINEERING SHOP
def engineering_shop(mb, x0, y0, w, d, wall="brick_soot", h_eave=9.5,
                     sawtooth=True, crane_gantry=True, chimney_h=22.0):
    """Plate/boiler/engineering shop with north-light sawtooth roof and gantry crane."""
    x1, y1 = x0 + w, y0 + d
    t = 0.5
    for axis, fixed, u0, u1, inward, tag in perimeter(x0, y0, x1, y1):
        mp = P.wmap(axis, fixed, inward)
        cs, step = _bay_centres(u0, u1, 4.8)
        holes = [(uc - 1.55, uc + 1.55, 1.3, h_eave - 1.1) for uc in cs]
        P.wall_panel(mb, axis, fixed, u0, u1, 0.0, h_eave, t, inward, wall, holes)
        for uc in cs:
            P.slab(mb, mp, uc - 1.55, uc + 1.55, 1.3, h_eave - 1.1, t * 0.55, t * 0.58, "glass")
            for k in range(1, 6):
                uu = uc - 1.55 + 3.1 * k / 6
                P.slab(mb, mp, uu - 0.035, uu + 0.035, 1.3, h_eave - 1.1, t * 0.50, t * 0.55, "iron")
            for k in range(1, 4):
                zz = 1.3 + (h_eave - 2.4) * k / 4
                P.slab(mb, mp, uc - 1.55, uc + 1.55, zz - 0.035, zz + 0.035, t * 0.50, t * 0.55, "iron")
            P.slab(mb, mp, uc - 1.55, uc - 1.48, 1.3, h_eave - 1.1, 0.0, t * 0.6, "iron")
            P.slab(mb, mp, uc + 1.48, uc + 1.55, 1.3, h_eave - 1.1, 0.0, t * 0.6, "iron")
        P.plinth(mb, mp, u0, u1, 0.0, h=0.9, mat="brick_blue", proj=0.06)
        P.string_course(mb, mp, u0, u1, h_eave - 0.45, "sandstone", h=0.28, proj=0.12)
        P.cornice(mb, mp, u0, u1, h_eave - 0.15, "sandstone", proj=0.30, h=0.28, ustep=2.4)
        P.downpipe(mb, mp, u0 + 1.2, 0.0, h_eave - 0.15)
        P.downpipe(mb, mp, u1 - 1.2, 0.0, h_eave - 0.15)

    mb.add_box(x0 + 0.6, y0 + 0.6, 0.0, x1 - 0.6, y1 - 0.6, h_eave - 0.4, "interior")
    if sawtooth:
        _sawtooth_roof(mb, x0, y0, x1, y1, h_eave)
    else:
        mb.add_gable_roof(x0, y0, x1, y1, h_eave, 26, "slate", gable="Y", overhang=0.3)
    if crane_gantry:
        for yy in (y0 + 1.6, y1 - 1.6):
            mb.add_box(x0, yy - 0.2, h_eave - 1.5, x1, yy + 0.2, h_eave - 1.2, "iron")
        mb.add_beam((x0 + (x1 - x0) * 0.35, y0 + 1.6, h_eave - 1.35),
                    (x0 + (x1 - x0) * 0.35, y1 - 1.6, h_eave - 1.35), 0.45, 0.55, "iron")
        mb.add_box_c(x0 + (x1 - x0) * 0.35, (y0 + y1) / 2, h_eave - 1.05, 1.5, 1.4, 0.8, "iron")
    cx, cy = x0 + 2.5, y1 - 2.5
    for i in range(8):
        t0, t1 = i / 8, (i + 1) / 8
        mb.add_cyl(cx, cy, t0 * chimney_h, t1 * chimney_h, 1.3 * (1 - 0.4 * t0),
                   "brick_soot", seg=8, r2=1.3 * (1 - 0.4 * t1))
    return dict(kind="engineering_shop", x0=x0, y0=y0, w=w, d=d, z_eave=h_eave)


def _sawtooth_roof(mb, x0, y0, x1, y1, z0, pitch=28, bay=6.0):
    """North-light sawtooth roof with completely solid triangular gable masonry ends."""
    n = max(1, int((y1 - y0) / bay))
    step = (y1 - y0) / n
    rise = step * math.tan(math.radians(pitch))
    for i in range(n):
        ya, yb = y0 + step * i, y0 + step * (i + 1)
        # sloped slate face
        mb.add_quad((x0, ya, z0 + rise), (x1, ya, z0 + rise), (x1, yb, z0), (x0, yb, z0), "slate")
        # vertical glazed face
        mb.add_quad((x0, ya, z0), (x1, ya, z0), (x1, ya, z0 + rise), (x0, ya, z0 + rise), "glass")
        for k in range(int((x1 - x0) / 2.0)):
            xx = x0 + 2.0 * k
            mb.add_beam((xx, ya, z0), (xx, ya, z0 + rise), 0.07, 0.07, "iron")
        # Solid triangular gable walls on west (x0) and east (x1)
        mb.add_tri((x0, ya, z0), (x0, yb, z0), (x0, ya, z0 + rise), "brick_soot")
        mb.add_tri((x1, ya, z0), (x1, ya, z0 + rise), (x1, yb, z0), "brick_soot")


# ================================================================ 8. MOULDING LOFT
def moulding_loft(mb, x0, y0, w, d, wall="brick_soot", h_eave=11.0):
    """The mould loft: long glazed-and-iron shed for full-scale ship drafting."""
    x1, y1 = x0 + w, y0 + d
    t = 0.45
    for axis, fixed, u0, u1, inward, tag in perimeter(x0, y0, x1, y1):
        mp = P.wmap(axis, fixed, inward)
        cs, step = _bay_centres(u0, u1, 4.5)
        holes = [(uc - 1.7, uc + 1.7, 1.6, h_eave - 1.2) for uc in cs]
        P.wall_panel(mb, axis, fixed, u0, u1, 0.0, h_eave, t, inward, wall, holes)
        for uc in cs:
            P.slab(mb, mp, uc - 1.7, uc + 1.7, 1.6, h_eave - 1.2, t * 0.5, t * 0.53, "glass")
            for k in range(1, 7):
                uu = uc - 1.7 + 3.4 * k / 7
                P.slab(mb, mp, uu - 0.03, uu + 0.03, 1.6, h_eave - 1.2, t * 0.46, t * 0.5, "iron")
        P.plinth(mb, mp, u0, u1, 0.0, h=1.4, mat="brick_blue", proj=0.05)
        P.cornice(mb, mp, u0, u1, h_eave - 0.2, "sandstone", proj=0.26, h=0.26, ustep=2.2)
        P.downpipe(mb, mp, u0 + 1.0, 0.0, h_eave - 0.2)
        P.downpipe(mb, mp, u1 - 1.0, 0.0, h_eave - 0.2)
    mb.add_box(x0 + 0.55, y0 + 0.55, 0.0, x1 - 0.55, y1 - 0.55, h_eave - 0.3, "plaster")
    mb.add_gable_roof(x0, y0, x1, y1, h_eave, 24, "glass",
                      gable=("X" if w >= d else "Y"), overhang=0.3, end_mat=wall)
    for i in range(int((x1 - x0) / 5.0) + 1):
        xx = x0 + 5.0 * i
        mb.add_beam((xx, y0, h_eave), (xx, (y0 + y1) / 2, h_eave + (y1 - y0) / 2 * 0.445),
                    0.14, 0.22, "iron")
        mb.add_beam((xx, y1, h_eave), (xx, (y0 + y1) / 2, h_eave + (y1 - y0) / 2 * 0.445),
                    0.14, 0.22, "iron")
    return dict(kind="moulding_loft", x0=x0, y0=y0, w=w, d=d, z_eave=h_eave)


# ================================================================ 9. TIME OFFICE
def time_office(mb, x0, y0, w=9.0, d=6.5, wall="brick_buff"):
    """Gatehouse / time office controlling access to the yard or quay."""
    x1, y1 = x0 + w, y0 + d
    h_eave = 5.0
    t = 0.4
    for axis, fixed, u0, u1, inward, tag in perimeter(x0, y0, x1, y1):
        mp = P.wmap(axis, fixed, inward)
        cs, step = _bay_centres(u0, u1, 3.0)
        holes = []
        for uc in cs:
            holes.append((uc - 0.55, uc + 0.55, 0.05, 2.35))
            holes.append((uc - 0.62, uc + 0.62, 2.9, 4.2))
        P.wall_panel(mb, axis, fixed, u0, u1, 0.0, h_eave, t, inward, wall, holes)
        for uc in cs:
            P.door(mb, mp, uc - 0.55, uc + 0.55, 0.05, 2.35, t, fanlight=True)
            P.sash_window(mb, mp, uc - 0.62, uc + 0.62, 2.9, 4.2, t, panes_x=2, panes_y=2)
            P.stone_sill(mb, mp, uc - 0.62, uc + 0.62, 2.9, "sandstone")
        P.cornice(mb, mp, u0, u1, h_eave - 0.16, "sandstone", proj=0.26, h=0.24, ustep=1.6)
        P.plinth(mb, mp, u0, u1, 0.0, h=0.45, mat="brick_blue")
    mb.add_box(x0 + 0.5, y0 + 0.5, 0.0, x1 - 0.5, y1 - 0.5, h_eave - 0.2, "interior")
    mb.add_hip_roof(x0, y0, x1, y1, h_eave, 34, "slate", overhang=0.35)
    P.clock_face(mb, (x0 + x1) / 2, y0 - 0.06, h_eave + 0.55, r=0.62, axis="Y")
    return dict(kind="time_office", x0=x0, y0=y0, w=w, d=d)


# ================================================================ 10. ACCUMULATOR TOWER
def accumulator_tower(mb, x0, y0, w=10.0, d=10.0, h_tower=26.0, wall="brick_red", trim="sandstone"):
    """Jesse Hartley style hydraulic accumulator tower (powers dockside cranes and gates)."""
    x1, y1 = x0 + w, y0 + d
    t = 0.65
    sides = perimeter(x0, y0, x1, y1)
    for axis, fixed, u0, u1, inward, tag in sides:
        mp = P.wmap(axis, fixed, inward)
        P.plinth(mb, mp, u0, u1, 0.0, h=1.4, mat="granite", proj=0.12)
        holes = []
        uc = (u0 + u1) / 2
        if tag == "S":
            holes.append((uc - 1.2, uc + 1.2, 0.0, 3.2))
        for zh in (6.0, 12.0, 18.0):
            holes.append((uc - 0.45, uc + 0.45, zh, zh + 1.8))
        P.wall_panel(mb, axis, fixed, u0, u1, 0.0, h_tower, t, inward, wall, holes)
        if tag == "S":
            P.segmental_arch(mb, mp, uc, 1.2, 3.2, 0.8, t, mat_ring=trim, mat_tympanum="timber")
            P.door(mb, mp, uc - 1.2, uc + 1.2, 0.0, 3.2, t)
        for zh in (6.0, 12.0, 18.0):
            P.sash_window(mb, mp, uc - 0.45, uc + 0.45, zh, zh + 1.8, t, panes_x=1, panes_y=2)
            P.stone_sill(mb, mp, uc - 0.45, uc + 0.45, zh, trim)
        P.quoin(mb, mp, 1.4, h_tower - 1.5, u0 + 0.4, trim, outward=+1)
        P.quoin(mb, mp, 1.4, h_tower - 1.5, u1 - 0.4, trim, outward=-1)
        P.string_course(mb, mp, u0, u1, 10.0, trim, h=0.25, proj=0.08)
        P.string_course(mb, mp, u0, u1, 19.0, trim, h=0.25, proj=0.08)
        P.cornice(mb, mp, u0, u1, h_tower - 1.2, trim, proj=0.55, h=0.75, ustep=1.2)
        P.parapet(mb, mp, u0, u1, h_tower, h=1.4, mat=wall, cap=trim)
        P.downpipe(mb, mp, u0 + 1.0, 0.0, h_tower - 1.2)

    mb.add_box(x0 + t, y0 + t, h_tower - 0.3, x1 - t, y1 - t, h_tower, "timber")
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    mb.add_cyl(cx, cy, 0.0, h_tower + 2.5, 2.2, "iron", seg=12)
    mb.add_cyl(cx, cy, h_tower + 2.5, h_tower + 4.0, 2.6, "iron", seg=12)
    return dict(kind="accumulator_tower", x0=x0, y0=y0, w=w, d=d, z_top=h_tower + 4.0)

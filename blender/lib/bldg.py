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


# ================================================================ 1B. PASSENGER TERMINAL
def passenger_terminal(mb, x0, y0, w=44.0, d=46.0, floors=3, wall="brick_buff", trim="sandstone"):
    """Dedicated Late-Victorian Ocean Passenger Liner Terminal building with full concourse interior."""
    x1, y1 = x0 + w, y0 + d
    gh = 5.2
    h_floor = 3.8
    z_top = gh + h_floor * (floors - 1)
    t = 0.55
    sides = perimeter(x0, y0, x1, y1)

    for axis, fixed, u0, u1, inward, tag in sides:
        mp = P.wmap(axis, fixed, inward)
        cs, step = _bay_centres(u0, u1, 3.8, margin=1.2)
        holes = []
        if tag == "W":
            cxu = (u0 + u1) / 2
            for off in (-4.2, 0.0, 4.2):
                holes.append((cxu + off - 1.3, cxu + off + 1.3, 0.0, 3.8))
            for uc in cs:
                if abs(uc - cxu) > 6.0:
                    holes.append((uc - 0.85, uc + 0.85, 1.1, gh - 1.2))
        else:
            for uc in cs:
                holes.append((uc - 0.85, uc + 0.85, 1.1, gh - 1.2))

        for f in range(1, floors):
            zf0 = gh + h_floor * (f - 1) + 1.0
            zf1 = zf0 + 2.2
            for uc in cs:
                holes.append((uc - 0.80, uc + 0.80, zf0, zf1))

        P.wall_panel(mb, axis, fixed, u0, u1, 0.0, z_top, t, inward, wall, holes)
        P.plinth(mb, mp, u0, u1, 0.0, h=0.8, mat="brick_blue", proj=0.08)

        if tag == "W":
            cxu = (u0 + u1) / 2
            for off in (-4.2, 0.0, 4.2):
                P.segmental_arch(mb, mp, cxu + off, 1.45, 3.8, 0.6, t, mat_ring=trim, mat_tympanum="timber")
                P.door(mb, mp, cxu + off - 1.3, cxu + off + 1.3, 0.0, 3.8, t)
            for uc in cs:
                if abs(uc - cxu) > 6.0:
                    P.sash_window(mb, mp, uc - 0.85, uc + 0.85, 1.1, gh - 1.2, t)
                    P.stone_sill(mb, mp, uc - 0.85, uc + 0.85, 1.1, trim)
        else:
            for uc in cs:
                P.sash_window(mb, mp, uc - 0.85, uc + 0.85, 1.1, gh - 1.2, t)
                P.stone_sill(mb, mp, uc - 0.85, uc + 0.85, 1.1, trim)

        for f in range(1, floors):
            zf0 = gh + h_floor * (f - 1) + 1.0
            for uc in cs:
                P.sash_window(mb, mp, uc - 0.80, uc + 0.80, zf0, zf0 + 2.2, t)
                P.stone_sill(mb, mp, uc - 0.80, uc + 0.80, zf0, trim)
                P.window_hood(mb, mp, uc - 0.80, uc + 0.80, zf0 + 2.2, trim)

        P.string_course(mb, mp, u0, u1, gh - 0.25, trim, h=0.35, proj=0.15)
        P.cornice(mb, mp, u0, u1, z_top - 0.15, trim, proj=0.55, h=0.65, ustep=1.8)
        P.parapet(mb, mp, u0, u1, z_top, h=1.1, mat=wall, cap=trim)
        P.downpipe(mb, mp, u0 + 0.9, 0.0, z_top)
        P.downpipe(mb, mp, u1 - 0.9, 0.0, z_top)

    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    mb.add_tri((x0 - 0.4, cy - 6.5, z_top + 1.1), (x0 - 0.4, cy, z_top + 3.9), (x0 - 0.4, cy + 6.5, z_top + 1.1), trim)
    mb.add_tri((x0 + 0.4, cy + 6.5, z_top + 1.1), (x0 + 0.4, cy, z_top + 3.9), (x0 + 0.4, cy - 6.5, z_top + 1.1), trim)
    mb.add_box_c(x0, cy, z_top + 1.2, 0.8, 13.5, 0.35, trim)
    P.clock_face(mb, x0 - 0.1, cy, z_top + 2.2, r=1.0, axis="X")

    mb.add_hip_roof(x0, y0, x1, y1, z_top + 1.1, 26, "slate", overhang=0.45)

    # ===== INTERIOR CONCOURSE (Ground Floor) =====
    mb.add_box(x0 + t, y0 + t, 0.0, x1 - t, y1 - t, 0.10, "granite", top="flags")
    tc_x = x1 - 5.5
    mb.add_box(tc_x, y0 + 6.0, 0.10, tc_x + 1.2, y1 - 6.0, 1.15, "timber", top="plank")
    for y_b in range(int(y0 + 9), int(y1 - 8), 5):
        mb.add_cyl(tc_x + 0.6, y_b, 1.15, 1.75, 0.03, "brass", seg=6)
        mb.add_beam((tc_x + 0.6, y_b - 1.8, 1.70), (tc_x + 0.6, y_b + 1.8, 1.70), 0.025, 0.025, "brass")
    for bx in (x0 + 12.0, x0 + 20.0, x0 + 28.0):
        for by in (y0 + 14.0, y1 - 18.0):
            mb.add_box_c(bx, by, 0.55, 6.0, 1.2, 0.45, "timber")
            mb.add_box_c(bx, by, 0.95, 6.0, 0.12, 0.45, "timber")
    for col_x in (x0 + 14.0, x0 + 26.0):
        for col_y in (y0 + 12.0, cy, y1 - 12.0):
            mb.add_cyl(col_x, col_y, 0.10, gh, 0.28, "iron", seg=12)
            mb.add_box_c(col_x, col_y, 0.25, 0.8, 0.8, 0.3, "iron")
            mb.add_box_c(col_x, col_y, gh - 0.2, 0.8, 0.8, 0.35, "iron")
    for ch_y in (y0 + 14.0, cy, y1 - 14.0):
        mb.add_cyl(cx - 4.0, ch_y, gh - 2.2, gh, 0.04, "brass", seg=6)
        mb.add_box_c(cx - 4.0, ch_y, gh - 2.3, 1.4, 1.4, 0.10, "brass")
        for a in (0, math.pi/2, math.pi, 3*math.pi/2):
            mb.add_cyl(cx - 4.0 + math.cos(a)*0.7, ch_y + math.sin(a)*0.7, gh - 2.6, gh - 2.2, 0.10, "lamp_glow", seg=6)
    mb.add_box(x0 + t, y0 + t, gh, x1 - t, y1 - t, gh + 0.28, "timber", top="plank")
    return dict(kind="passenger_terminal", x0=x0, y0=y0, w=w, d=d, z_top=z_top)


# ================================================================ 1C. BAGGAGE HALL
def baggage_hall(mb, x0, y0, w=60.0, d=26.0, h_eave=7.0, wall="brick_buff", trim="sandstone"):
    """Ocean liner baggage handling & sorting hall with full interior and monitor roof."""
    x1, y1 = x0 + w, y0 + d
    t = 0.50
    sides = perimeter(x0, y0, x1, y1)

    for axis, fixed, u0, u1, inward, tag in sides:
        mp = P.wmap(axis, fixed, inward)
        holes = []
        if tag in ("S", "N"):
            cs, step = _bay_centres(u0, u1, 6.0, margin=2.0)
            for i, uc in enumerate(cs):
                if i % 2 == 0:
                    holes.append((uc - 2.0, uc + 2.0, 0.0, 4.4))
                else:
                    holes.append((uc - 1.2, uc + 1.2, 2.0, 5.0))
        else:
            cs, step = _bay_centres(u0, u1, 4.5, margin=1.0)
            for uc in cs:
                holes.append((uc - 1.0, uc + 1.0, 1.6, 5.0))

        P.wall_panel(mb, axis, fixed, u0, u1, 0.0, h_eave, t, inward, wall, holes)
        P.plinth(mb, mp, u0, u1, 0.0, h=0.7, mat="brick_blue", proj=0.08)

        if tag in ("S", "N"):
            for i, uc in enumerate(cs):
                if i % 2 == 0:
                    P.segmental_arch(mb, mp, uc, 2.1, 4.4, 0.5, t, mat_ring="brick_blue", mat_tympanum=wall)
                    P.door(mb, mp, uc - 2.0, uc + 2.0, 0.0, 4.4, t, mat_panel="timber")
                else:
                    P.sash_window(mb, mp, uc - 1.2, uc + 1.2, 2.0, 5.0, t, panes_x=2, panes_y=3)
                    P.stone_sill(mb, mp, uc - 1.2, uc + 1.2, 2.0, trim)
        else:
            for uc in cs:
                P.sash_window(mb, mp, uc - 1.0, uc + 1.0, 1.6, 5.0, t, panes_x=2, panes_y=3)
                P.stone_sill(mb, mp, uc - 1.0, uc + 1.0, 1.6, trim)

        P.cornice(mb, mp, u0, u1, h_eave - 0.12, trim, proj=0.45, h=0.35, ustep=2.0)
        P.downpipe(mb, mp, u0 + 0.8, 0.0, h_eave)
        P.downpipe(mb, mp, u1 - 0.8, 0.0, h_eave)

    z_ridge = h_eave + 4.2
    mb.add_gable_roof(x0, y0, x1, y1, h_eave, 24, "slate", overhang=0.4, gable="X", end_mat=wall)
    mon_x0, mon_x1 = x0 + 4.0, x1 - 4.0
    cy = (y0 + y1) / 2
    mb.add_box(mon_x0, cy - 3.2, z_ridge - 0.8, mon_x1, cy + 3.2, z_ridge + 1.6, "glass_lit")
    mb.add_box(mon_x0 - 0.2, cy - 3.4, z_ridge + 1.55, mon_x1 + 0.2, cy + 3.4, z_ridge + 1.7, "lead")

    # ===== INTERIOR BAGGAGE HANDLING EQUIPMENT =====
    mb.add_box(x0 + t, y0 + t, 0.0, x1 - t, y1 - t, 0.10, "granite", top="flags")
    mb.add_box(x0 + 6.0, cy - 1.0, 0.10, x1 - 6.0, cy + 1.0, 1.15, "timber", top="plank")
    for sx in (x0 + 16.0, x1 - 16.0):
        mb.add_box(sx - 1.2, cy - 2.8, 0.10, sx + 1.2, cy - 1.4, 0.28, "iron")
        mb.add_cyl(sx + 1.0, cy - 2.1, 0.28, 1.6, 0.05, "iron", seg=8)
        mb.add_beam((sx + 0.4, cy - 2.1, 1.55), (sx + 1.6, cy - 2.1, 1.55), 0.06, 0.06, "brass")
    for k, lx in enumerate(range(int(x0 + 8), int(x1 - 8), 7)):
        mb.add_box(lx, cy + 1.8, 0.10, lx + 2.4, cy + 3.2, 0.85, "timber")
        mb.add_box(lx + 0.2, cy + 2.0, 0.85, lx + 1.8, cy + 3.0, 1.55, "canvas")
    for tx in range(int(x0 + 6), int(x1), 6):
        _queen_truss(mb, tx, y0 + t, y1 - t, h_eave, z_ridge)
        mb.add_cyl(tx, cy, h_eave + 0.5, h_eave + 2.0, 0.03, "iron", seg=6)
        mb.add_cyl(tx, cy, h_eave + 0.2, h_eave + 0.5, 0.14, "lamp_glow", seg=6)

    return dict(kind="baggage_hall", x0=x0, y0=y0, w=w, d=d, z_ridge=z_ridge)


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
    """Civic Italianate Custom House with rusticated base, giant order, portico, dome, and Long Room interior."""
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

    # ===== INTERIOR: THE LONG ROOM =====
    _customs_long_room(mb, x0, y0, w, d, gh, z_top)

    z_r = mb.add_hip_roof(x0, y0, x1, y1, z_top + 0.42, 22, "slate", overhang=0.5)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    _dome(mb, cx, cy, z_r - 0.4, 7.0)
    _portico(mb, cx, y0, gh, 8.6)
    return dict(kind="custom_house", x0=x0, y0=y0, w=w, d=d, z_top=z_top)


def _customs_long_room(mb, x0, y0, w, d, gh, z_top):
    """The central Victorian 'Long Room' of the Custom House with mahogany counter and dome columns."""
    cx, cy = (x0 + w / 2), (y0 + d / 2)
    # Ground floor slab
    mb.add_box(x0 + 1.0, y0 + 1.0, 0.0, x0 + w - 1.0, y0 + d - 1.0, 0.08, "granite", top="flags")
    # Upper floor gallery slab with central opening under dome
    mb.add_box(x0 + 1.0, y0 + 1.0, gh - 0.25, cx - 9.0, y0 + d - 1.0, gh, "plaster", top="plank")
    mb.add_box(cx + 9.0, y0 + 1.0, gh - 0.25, x0 + w - 1.0, y0 + d - 1.0, gh, "plaster", top="plank")
    mb.add_box(cx - 9.0, y0 + 1.0, gh - 0.25, cx + 9.0, cy - 8.0, gh, "plaster", top="plank")
    mb.add_box(cx - 9.0, cy + 8.0, gh - 0.25, cx + 9.0, y0 + d - 1.0, gh, "plaster", top="plank")
    # Central inspection counter
    counter_y = cy - 1.8
    mb.add_box(cx - 16.0, counter_y, 0.08, cx + 16.0, counter_y + 1.2, 1.15, "timber", top="plank")
    # Brass security rails on counter
    for ox in range(-14, 15, 4):
        mb.add_cyl(cx + ox, counter_y + 0.6, 1.15, 1.65, 0.025, "brass", seg=6)
        mb.add_beam((cx + ox - 1.8, counter_y + 0.6, 1.60), (cx + ox + 1.8, counter_y + 0.6, 1.60), 0.03, 0.03, "brass")
    # Clerks' high desks behind counter
    for ox in (-10.0, -2.0, 6.0, 14.0):
        mb.add_box(cx + ox - 1.4, counter_y + 2.2, 0.08, cx + ox + 1.4, counter_y + 3.4, 1.10, "timber")
        mb.add_box(cx + ox - 1.2, counter_y + 2.3, 1.10, cx + ox + 1.2, counter_y + 3.3, 1.30, "plank")
    # Tall bookshelves with customs folios along back wall
    back_y = y0 + d - 2.2
    mb.add_box(cx - 14.0, back_y, 0.08, cx + 14.0, back_y + 0.9, 4.2, "timber")
    # Fluted support columns under dome drum
    for dx in (-7.0, 7.0):
        for dy in (-6.0, 6.0):
            mb.add_cyl(cx + dx, cy + dy, 0.08, gh, 0.35, "sandstone", seg=12, r2=0.30)
            mb.add_box_c(cx + dx, cy + dy, 0.22, 0.9, 0.9, 0.28, "sandstone")
            mb.add_box_c(cx + dx, cy + dy, gh - 0.2, 0.85, 0.85, 0.35, "sandstone")
    # Hanging brass gas chandelier under dome
    mb.add_cyl(cx, cy, gh - 2.2, gh + 4.0, 0.04, "brass", seg=6)
    mb.add_box_c(cx, cy, gh - 2.3, 1.8, 1.8, 0.12, "brass")
    for ang in (0, math.pi/2, math.pi, 3*math.pi/2):
        lx, ly = cx + math.cos(ang) * 0.9, cy + math.sin(ang) * 0.9
        mb.add_cyl(lx, ly, gh - 2.6, gh - 2.2, 0.12, "lamp_glow", seg=8)


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
def station_shed(mb, x0, y0, w, d, tracks=2, h_spring=6.4, rise=3.4, bay=5.0,
                 wall="brick_buff", platform_h=1.05):
    """A monumental Victorian single-span arched iron train shed with solid slate roof,
    raised iron clerestory ridge monitor, and classical sandstone train portal gables.
    
    Tracks run along X (from West x0 to East x1).
    Arched barrel curves across Y (from South y0 to North y1).
    Gables and train portals are at x0 (West) and x1 (East).
    Side eaves walls are at y0 (South) and y1 (North).
    """
    x1, y1 = x0 + w, y0 + d
    cy = (y0 + y1) / 2
    t = 0.48
    z_eave = h_spring

    # --- SIDE EAVES WALLS (South y0 and North y1) ---
    for fixed_y, inward, tag in ((y0, +1, "S"), (y1, -1, "N")):
        mp = P.wmap("X", fixed_y, inward)
        cs, step = _bay_centres(x0, x1, 5.8)
        holes = [(uc - 1.10, uc + 1.10, 1.25, z_eave - 1.20) for uc in cs]
        P.wall_panel(mb, "X", fixed_y, x0, x1, 0.0, z_eave, t, inward, wall, holes)
        P.plinth(mb, mp, x0, x1, 0.0, h=0.65, mat="brick_blue", proj=0.06)
        for uc in cs:
            P.sash_window(mb, mp, uc - 1.10, uc + 1.10, 1.25, z_eave - 1.20, t,
                          panes_x=2, panes_y=3)
            P.segmental_arch(mb, mp, uc, 1.25, z_eave - 1.20, 0.45, t,
                             mat_ring="brick_blue", mat_tympanum=wall, voussoirs=7)
        P.string_course(mb, mp, x0, x1, z_eave - 1.35, "sandstone", h=0.22, proj=0.10)
        P.cornice(mb, mp, x0, x1, z_eave - 0.12, "sandstone", proj=0.32, h=0.28, ustep=2.4)
        # Cast-iron gutters along eaves
        fy_gut = fixed_y - 0.20 if inward == +1 else fixed_y + 0.20
        mb.add_box(x0 - 0.4, fy_gut - 0.12, z_eave - 0.22, x1 + 0.4, fy_gut + 0.12, z_eave - 0.06, "iron")

    # --- GABLE END SCREEN WALLS WITH TRAIN PORTAL ARCHES (West x0 and East x1) ---
    portal_w = 4.2 + tracks * 4.4  # width of central train entrance arch
    py0, py1 = cy - portal_w / 2, cy + portal_w / 2
    portal_h = z_eave + 0.75       # height of train portal opening

    for fixed_x, inward, tag in ((x0, +1, "W"), (x1, -1, "E")):
        mp = P.wmap("Y", fixed_x, inward)
        # Flanking solid brick screen walls up to z_eave
        # South flank: y0 to py0
        P.wall_panel(mb, "Y", fixed_x, y0, py0, 0.0, z_eave, t, inward, wall)
        P.plinth(mb, mp, y0, py0, 0.0, h=0.65, mat="brick_blue", proj=0.06)
        # North flank: py1 to y1
        P.wall_panel(mb, "Y", fixed_x, py1, y1, 0.0, z_eave, t, inward, wall)
        P.plinth(mb, mp, py1, y1, 0.0, h=0.65, mat="brick_blue", proj=0.06)

        # Dressed sandstone train portal jamb piers
        pj_x0 = fixed_x - 0.15 if inward == +1 else fixed_x - t - 0.10
        pj_x1 = fixed_x + t + 0.10 if inward == +1 else fixed_x + 0.15
        for jy in (py0, py1):
            mb.add_box(pj_x0, jy - 0.45, 0.0, pj_x1, jy + 0.45, portal_h, "sandstone")
            mb.add_box(pj_x0 - 0.05, jy - 0.52, portal_h - 0.35, pj_x1 + 0.05, jy + 0.52, portal_h, "granite")

        # Sandstone portal arch lintel / archivolt across the train entrance
        mb.add_box(pj_x0, py0 - 0.45, portal_h, pj_x1, py1 + 0.45, portal_h + 0.55, "sandstone")
        # Keystones
        mb.add_box_c(fixed_x, cy, portal_h + 0.28, t * 1.4, 0.70, 0.75, "granite")

        # Upper semicircular lunette screen wall above portal (closing the barrel end completely)
        # Semicircular lunette glazing with radial iron astragals
        n_lun = 14
        for i in range(n_lun):
            a0 = math.pi * i / n_lun
            a1 = math.pi * (i + 1) / n_lun
            ya = cy - math.cos(a0) * (y1 - y0) / 2
            yb = cy - math.cos(a1) * (y1 - y0) / 2
            za = z_eave + math.sin(a0) * rise
            zb = z_eave + math.sin(a1) * rise
            # Solid brick tympanum infill between horizontal portal lintel and arch curve
            z_bot = max(portal_h + 0.55, z_eave)
            if za > z_bot or zb > z_bot:
                z_mid = (za + zb) / 2
                if z_mid > z_bot + 0.2:
                    mb.add_quad((fixed_x, ya, z_bot), (fixed_x, yb, z_bot),
                                (fixed_x, yb, zb), (fixed_x, ya, za), wall)
                    # Reverse face for two-sided solid masonry
                    mb.add_quad((fixed_x, ya, za), (fixed_x, yb, zb),
                                (fixed_x, yb, z_bot), (fixed_x, ya, z_bot), wall)
        # Ornamental curved bargeboard arch along the gable rim
        for i in range(20):
            a0 = math.pi * i / 20
            a1 = math.pi * (i + 1) / 20
            ya = cy - math.cos(a0) * ((y1 - y0) / 2 + 0.2)
            yb = cy - math.cos(a1) * ((y1 - y0) / 2 + 0.2)
            za = z_eave + math.sin(a0) * (rise + 0.15)
            zb = z_eave + math.sin(a1) * (rise + 0.15)
            fx_rim = fixed_x - 0.22 if inward == +1 else fixed_x + 0.22
            mb.add_beam((fx_rim, ya, za), (fx_rim, yb, zb), 0.25, 0.35, "sandstone")

    # --- INTERIOR GROUND & PASSENGER PLATFORMS ---
    mb.add_box(x0 + 0.4, y0 + 0.4, 0.0, x1 - 0.4, y1 - 0.4, 0.08, "granite")
    # Platforms along South and North walls
    for k, yy in enumerate((y0 + 3.2, y1 - 3.2)):
        mb.add_box(x0 + 0.4, yy - 2.4, 0.0, x1 - 0.4, yy + 2.4, platform_h, "granite", top="flags")
        mb.add_box(x0 + 0.4, yy - 2.4, platform_h - 0.18, x1 - 0.4, yy + 2.4, platform_h, "granite")
        # Wooden safety coping strip
        mb.add_box(x0 + 0.4, yy - 2.46, platform_h - 0.12, x1 - 0.4, yy - 2.38, platform_h + 0.01, "plank")

    # --- ARCHED WROUGHT-IRON LATTICE RIBS ---
    nt = max(4, int((x1 - x0) / 6.0))
    for i in range(nt + 1):
        tx = x0 + (x1 - x0) * i / nt
        _arch_rib(mb, tx, x0, x1, y0, y1, h_spring, rise, section=0.28, mat="iron")

    # --- SOLID CURVED SLATE ROOF SHELL WITH RAISED CLERESTORY MONITOR ---
    _arch_shell(mb, x0, y0, x1, y1, h_spring, rise, nt)

    return dict(kind="station_shed", x0=x0, y0=y0, w=w, d=d, z_ridge=h_spring + rise + 1.2)


def _arch_rib(mb, tx, x0, x1, y0, y1, h_spring, rise, section=0.28, mat="iron"):
    """Wrought-iron arched lattice truss rib with double chords and cross-ties."""
    n = 12
    cy = (y0 + y1) / 2
    r_y = (y1 - y0) / 2
    for i in range(n):
        a0 = math.pi * i / n
        a1 = math.pi * (i + 1) / n
        # Outer chord
        p0 = (tx, cy - math.cos(a0) * r_y, h_spring + math.sin(a0) * rise)
        p1 = (tx, cy - math.cos(a1) * r_y, h_spring + math.sin(a1) * rise)
        mb.add_beam(p0, p1, section, section * 0.8, mat)
        # Inner chord (truss depth 0.45 m)
        q0 = (tx, cy - math.cos(a0) * (r_y - 0.42), h_spring + math.sin(a0) * (rise - 0.40))
        q1 = (tx, cy - math.cos(a1) * (r_y - 0.42), h_spring + math.sin(a1) * (rise - 0.40))
        mb.add_beam(q0, q1, section * 0.7, section * 0.7, mat)
        # Diagonal lattice web strut
        mb.add_beam(p0, q1, 0.06, 0.06, mat)


def _arch_shell(mb, x0, y0, x1, y1, h_spring, rise, nt):
    """Completely solid Welsh roofing slate barrel vault with raised clerestory monitor.
    
    Both top and underside faces are generated to guarantee 100% opaque, non-culled solid roof.
    Central apex features a raised Victorian louvred iron clerestory monitor with lead cap.
    """
    n = 16
    cy = (y0 + y1) / 2
    r_y = (y1 - y0) / 2
    z_apex = h_spring + rise

    for i in range(n):
        a0 = math.pi * i / n
        a1 = math.pi * (i + 1) / n
        ya = cy - math.cos(a0) * r_y
        yb = cy - math.cos(a1) * r_y
        za = h_spring + math.sin(a0) * rise
        zb = h_spring + math.sin(a1) * rise

        # Entire roof barrel is solid dark Welsh roofing slate
        m = "slate"
        for k in range(nt):
            xa = x0 + (x1 - x0) * k / nt
            xb = x0 + (x1 - x0) * (k + 1) / nt
            # Exterior top face (slate)
            mb.add_quad((xa, ya, za + 0.03), (xb, ya, za + 0.03),
                        (xb, yb, zb + 0.03), (xa, yb, zb + 0.03), m)
            # Interior underside face (whitewashed boarding - guarantees no see-through)
            mb.add_quad((xa, yb, zb + 0.01), (xb, yb, zb + 0.01),
                        (xb, ya, za + 0.01), (xa, ya, za + 0.01), "interior")

    # --- RAISED VICTORIAN CLERESTORY RIDGE MONITOR ---
    mon_w = 4.2       # width of central monitor along Y
    mon_h = 1.25      # height above roof apex
    my0, my1 = cy - mon_w / 2, cy + mon_w / 2
    mz_base = z_apex - 0.20
    mz_top = z_apex + mon_h

    # Longitudinal vertical clerestory sides with iron louvres / glazed lights
    for my, sgn in ((my0, -1), (my1, +1)):
        # Glazed / louvred vertical panel
        mb.add_quad((x0 + 0.6, my, mz_base), (x1 - 0.6, my, mz_base),
                    (x1 - 0.6, my, mz_top), (x0 + 0.6, my, mz_top), "glass")
        mb.add_quad((x0 + 0.6, my, mz_top), (x1 - 0.6, my, mz_top),
                    (x1 - 0.6, my, mz_base), (x0 + 0.6, my, mz_base), "glass")
        # Iron vertical glazing bars
        for k in range(int((x1 - x0) / 2.2)):
            xx = x0 + 1.2 + k * 2.2
            mb.add_beam((xx, my, mz_base), (xx, my, mz_top), 0.08, 0.08, "iron")
        # Iron sill and eaves plates
        mb.add_box(x0 + 0.4, my - 0.12, mz_base - 0.05, x1 - 0.4, my + 0.12, mz_base + 0.10, "iron")
        mb.add_box(x0 + 0.4, my - 0.12, mz_top - 0.08, x1 - 0.4, my + 0.12, mz_top + 0.08, "iron")

    # Monitor gables at West (x0) and East (x1)
    for mx in (x0 + 0.6, x1 - 0.6):
        mb.add_quad((mx, my0, mz_base), (mx, my1, mz_base),
                    (mx, my1, mz_top), (mx, my0, mz_top), "timber")
        mb.add_quad((mx, my0, mz_top), (mx, my1, mz_top),
                    (mx, my1, mz_base), (mx, my0, mz_base), "timber")

    # Monitor pitched roof with lead cap and ridge roll
    mz_ridge = mz_top + 0.45
    mb.add_quad((x0 + 0.4, my0 - 0.18, mz_top), (x1 - 0.4, my0 - 0.18, mz_top),
                (x1 - 0.4, cy, mz_ridge), (x0 + 0.4, cy, mz_ridge), "lead")
    mb.add_quad((x0 + 0.4, cy, mz_ridge), (x1 - 0.4, cy, mz_ridge),
                (x1 - 0.4, my1 + 0.18, mz_top), (x0 + 0.4, my1 + 0.18, mz_top), "lead")
    # Ridge roll and ornamental iron cresting
    mb.add_box(x0 + 0.2, cy - 0.12, mz_ridge - 0.05, x1 - 0.2, cy + 0.12, mz_ridge + 0.10, "lead")
    mb.add_box(x0 + 0.2, cy - 0.03, mz_ridge + 0.10, x1 - 0.2, cy + 0.03, mz_ridge + 0.42, "iron")


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

    # ===== WORKSHOP INTERIOR =====
    mb.add_box(x0 + 0.6, y0 + 0.6, 0.0, x1 - 0.6, y1 - 0.6, 0.08, "rubble", top="iron")
    lathe_y = y0 + 3.2
    mb.add_box(x0 + 8.0, lathe_y - 0.7, 0.08, min(x1 - 8.0, x0 + 18.0), lathe_y + 0.7, 0.85, "iron")
    mb.add_cyl(x0 + 8.6, lathe_y, 0.85, 1.45, 0.55, "steel_plate", seg=12, axis="X")
    mb.add_box(min(x1 - 9.5, x0 + 16.5), lathe_y - 0.5, 0.85, min(x1 - 8.5, x0 + 17.5), lathe_y + 0.5, 1.35, "iron")
    drill_x, drill_y = x0 + 22.0, y0 + 3.2
    if drill_x < x1 - 12.0:
        mb.add_box(drill_x - 0.8, drill_y - 0.8, 0.08, drill_x + 0.8, drill_y + 0.8, 0.35, "iron")
        mb.add_cyl(drill_x - 0.4, drill_y, 0.35, 2.8, 0.16, "iron", seg=8)
        mb.add_beam((drill_x - 0.4, drill_y, 2.3), (drill_x + 0.9, drill_y, 2.3), 0.18, 0.22, "steel_plate")
    forge_x, forge_y = x1 - 8.0, y0 + 3.5
    mb.add_box(forge_x - 1.5, forge_y - 1.2, 0.08, forge_x + 1.5, forge_y + 1.2, 0.85, "brick_blue")
    mb.add_box(forge_x - 1.2, forge_y - 0.9, 0.85, forge_x + 1.2, forge_y + 0.9, 0.95, "coal")
    mb.add_cyl(forge_x - 3.2, forge_y, 0.08, 0.65, 0.40, "timber", seg=8)
    mb.add_box_c(forge_x - 3.2, forge_y, 0.85, 0.95, 0.32, 0.38, "steel_plate")
    bench_y = y1 - 2.0
    mb.add_box(x0 + 6.0, bench_y - 0.5, 0.08, x1 - 6.0, bench_y + 0.5, 0.95, "timber", top="plank")
    for vx in (x0 + 10.0, x0 + 18.0, x0 + 26.0, x0 + 34.0):
        if vx < x1 - 6.0:
            mb.add_box_c(vx, bench_y - 0.4, 1.05, 0.28, 0.32, 0.22, "iron")

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
    """North-light sawtooth roof with completely solid triangular gable masonry ends and gutters."""
    n = max(1, int((y1 - y0) / bay))
    step = (y1 - y0) / n
    rise = step * math.tan(math.radians(pitch))
    for i in range(n):
        ya, yb = y0 + step * i, y0 + step * (i + 1)
        # sloped slate face (top and underside)
        mb.add_quad((x0, ya, z0 + rise), (x1, ya, z0 + rise), (x1, yb, z0), (x0, yb, z0), "slate")
        mb.add_quad((x0, yb, z0), (x1, yb, z0), (x1, ya, z0 + rise), (x0, ya, z0 + rise), "interior")
        # vertical glazed face (double-sided)
        mb.add_quad((x0, ya, z0), (x1, ya, z0), (x1, ya, z0 + rise), (x0, ya, z0 + rise), "glass")
        mb.add_quad((x0, ya, z0 + rise), (x1, ya, z0 + rise), (x1, ya, z0), (x0, ya, z0), "glass")
        for k in range(int((x1 - x0) / 2.0)):
            xx = x0 + 2.0 * k
            mb.add_beam((xx, ya, z0), (xx, ya, z0 + rise), 0.08, 0.08, "iron")
        # Solid triangular gable walls on west (x0) and east (x1) (both outward and inward normals)
        mb.add_tri((x0, ya, z0), (x0, yb, z0), (x0, ya, z0 + rise), "brick_soot")
        mb.add_tri((x0, ya, z0 + rise), (x0, yb, z0), (x0, ya, z0), "brick_soot")
        mb.add_tri((x1, ya, z0), (x1, ya, z0 + rise), (x1, yb, z0), "brick_soot")
        mb.add_tri((x1, yb, z0), (x1, ya, z0 + rise), (x1, ya, z0), "brick_soot")
        # Cast-iron valley gutter between bays
        mb.add_box(x0 - 0.2, yb - 0.14, z0 - 0.20, x1 + 0.2, yb + 0.14, z0 - 0.04, "iron")


# ================================================================ 8. MOULDING LOFT
def moulding_loft(mb, x0, y0, w, d, wall="brick_soot", h_eave=11.0):
    """The mould loft: long Victorian brick drafting loft with solid slate roof and raised glazed lantern."""
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

    # ===== MOULDING LOFT UPPER DRAFTING FLOOR =====
    mb.add_box(x0 + 0.5, y0 + 0.5, 0.0, x1 - 0.5, y1 - 0.5, 0.10, "granite")
    # Upper lofting floor slab
    z_loft = 5.2
    mb.add_box(x0 + 0.5, y0 + 0.5, z_loft - 0.25, x1 - 0.5, y1 - 0.5, z_loft, "whitewash", top="plank")
    # Drafting trestle tables
    cy = (y0 + y1) / 2
    for tx in (x0 + 8.0, x0 + 18.0, x0 + 28.0):
        if tx < x1 - 6.0:
            mb.add_box_c(tx, cy, z_loft + 0.45, 5.5, 2.2, 0.85, "timber")
            mb.add_box_c(tx, cy, z_loft + 0.90, 5.2, 1.8, 0.04, "canvas") # Blueprint parchment roll
    # Model half-hulls on South wall
    for hx in (x0 + 10.0, x0 + 20.0, x0 + 30.0):
        if hx < x1 - 6.0:
            mb.add_box_c(hx, y0 + 0.65, z_loft + 1.8, 4.2, 0.22, 0.9, "timber") # Half-hull model

    # Solid slate gable roof with watertight eave ceiling
    gable_axis = "X" if w >= d else "Y"
    z_ridge = mb.add_gable_roof(x0, y0, x1, y1, h_eave, 24, "slate",
                                gable=gable_axis, overhang=0.35, end_mat=wall)

    # Raised skylight monitor lantern along the ridge
    if gable_axis == "X":
        # Ridge runs parallel to X at cy
        lan_x0, lan_x1 = x0 + 3.0, x1 - 3.0
        lan_w = 2.6
        lan_h = 1.15
        lz0, lz1 = z_ridge - 0.15, z_ridge + lan_h
        ly0, ly1 = cy - lan_w / 2, cy + lan_w / 2
        for ly, sgn in ((ly0, -1), (ly1, +1)):
            mb.add_quad((lan_x0, ly, lz0), (lan_x1, ly, lz0),
                        (lan_x1, ly, lz1), (lan_x0, ly, lz1), "glass")
            mb.add_quad((lan_x0, ly, lz1), (lan_x1, ly, lz1),
                        (lan_x1, ly, lz0), (lan_x0, ly, lz0), "glass")
            for k in range(int((lan_x1 - lan_x0) / 2.0)):
                xx = lan_x0 + 1.0 + k * 2.0
                mb.add_beam((xx, ly, lz0), (xx, ly, lz1), 0.08, 0.08, "iron")
        for lx in (lan_x0, lan_x1):
            mb.add_quad((lx, ly0, lz0), (lx, ly1, lz0),
                        (lx, ly1, lz1), (lx, ly0, lz1), "timber")
        # Lead pitched roof over monitor
        mb.add_quad((lan_x0 - 0.2, ly0 - 0.15, lz1), (lan_x1 + 0.2, ly0 - 0.15, lz1),
                    (lan_x1 + 0.2, cy, lz1 + 0.35), (lan_x0 - 0.2, cy, lz1 + 0.35), "lead")
        mb.add_quad((lan_x0 - 0.2, cy, lz1 + 0.35), (lan_x1 + 0.2, cy, lz1 + 0.35),
                    (lan_x1 + 0.2, ly1 + 0.15, lz1), (lan_x0 - 0.2, ly1 + 0.15, lz1), "lead")
        mb.add_box(lan_x0 - 0.3, cy - 0.10, lz1 + 0.32, lan_x1 + 0.3, cy + 0.10, lz1 + 0.45, "lead")

    # Wrought-iron roof truss tie-beams across the loft
    for i in range(int((x1 - x0) / 5.0) + 1):
        xx = x0 + 5.0 * i
        mb.add_beam((xx, y0, h_eave), (xx, cy, z_ridge), 0.14, 0.22, "iron")
        mb.add_beam((xx, y1, h_eave), (xx, cy, z_ridge), 0.14, 0.22, "iron")
        mb.add_beam((xx, y0 + 0.5, h_eave), (xx, y1 - 0.5, h_eave), 0.10, 0.18, "iron")
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


# ================================================================ 12. PIERHEAD LIGHTHOUSE
def pierhead_lighthouse(mb, x, y, z=0.0, h_tower=14.0):
    """Late Victorian octagonal dressed granite pierhead lighthouse with lantern & fog bell."""
    mb.add_cyl(x, y, z, z + 0.6, 4.2, "granite", seg=8)
    mb.add_cyl(x, y, z + 0.6, z + 1.2, 3.8, "granite", seg=8)

    mb.add_cyl(x, y, z + 1.2, z + h_tower - 2.8, 3.4, "granite", seg=8, r2=2.3)

    mb.add_box_c(x, y - 3.4, z + 2.0, 1.3, 0.5, 2.4, "timber")
    mb.add_box_c(x, y - 3.45, z + 3.25, 1.6, 0.6, 0.4, "granite")

    for wz in (z + 4.5, z + 8.0):
        mb.add_box_c(x, y - 2.8 * (1 - (wz - z) / 28.0), wz, 0.45, 0.4, 0.9, "glass")

    z_gal = z + h_tower - 2.8
    mb.add_cyl(x, y, z_gal, z_gal + 0.6, 3.1, "granite", seg=8)
    for a in range(8):
        ang = a * math.pi / 4
        px = x + math.cos(ang) * 2.95
        py = y + math.sin(ang) * 2.95
        mb.add_cyl(px, py, z_gal + 0.6, z_gal + 1.7, 0.04, "iron", seg=6)
        ang_next = (a + 1) * math.pi / 4
        px_next = x + math.cos(ang_next) * 2.95
        py_next = y + math.sin(ang_next) * 2.95
        mb.add_beam((px, py, z_gal + 1.65), (px_next, py_next, z_gal + 1.65), 0.04, 0.04, "iron")
        mb.add_beam((px, py, z_gal + 1.15), (px_next, py_next, z_gal + 1.15), 0.03, 0.03, "iron")

    z_lan = z_gal + 0.6
    mb.add_cyl(x, y, z_lan, z_lan + 0.45, 2.2, "iron", seg=8)
    mb.add_cyl(x, y, z_lan + 0.45, z_lan + 2.45, 2.1, "glass", seg=8)
    mb.add_cyl(x, y, z_lan + 0.6, z_lan + 2.2, 0.95, "glass_lit", seg=12)
    mb.add_cyl(x, y, z_lan + 1.2, z_lan + 1.6, 1.25, "brass", seg=12)

    z_cup = z_lan + 2.45
    mb.add_cyl(x, y, z_cup, z_cup + 0.9, 2.25, "copper", seg=8, r2=0.3)
    mb.add_cyl(x, y, z_cup + 0.9, z_cup + 1.35, 0.35, "brass", seg=8)
    mb.add_cyl(x, y, z_cup + 1.35, z_cup + 2.3, 0.04, "brass", seg=6)

    p_bell_x, p_bell_y = x + 2.5, y
    mb.add_beam((x + 2.0, y, z_gal + 1.4), (p_bell_x + 0.4, y, z_gal + 1.4), 0.08, 0.08, "iron")
    mb.add_cyl(p_bell_x, p_bell_y, z_gal + 0.8, z_gal + 1.35, 0.28, "bronze", seg=8, r2=0.14)
    return dict(kind="pierhead_lighthouse", x=x, y=y, z=z, h=h_tower)


# ================================================================ 13. HARBOUR SIGNAL STATION
def harbour_signal_station(mb, x, y, z=0.0, w=7.2, d=7.2):
    """Harbour master's octagonal lookout tower with signal yardarm and storm warning cones."""
    h_bldg = 9.5
    mb.add_box_c(x, y, z + h_bldg * 0.5, w, d, h_bldg, "brick_buff")
    mb.add_box_c(x, y, z + 0.4, w + 0.2, d + 0.2, 0.8, "brick_blue")
    mb.add_box_c(x, y, z + 4.8, w + 0.15, d + 0.15, 0.35, "sandstone")
    mb.add_box_c(x, y, z + h_bldg - 0.2, w + 0.3, d + 0.3, 0.4, "sandstone")

    for dx in (-w * 0.5 - 0.02, w * 0.5 + 0.02):
        mb.add_box_c(x + dx * 0.9, y, z + 6.8, 0.08, d * 0.75, 2.2, "glass")
    for dy in (-d * 0.5 - 0.02, d * 0.5 + 0.02):
        mb.add_box_c(x, y + dy * 0.9, z + 6.8, w * 0.75, 0.08, 2.2, "glass")

    z_roof = z + h_bldg
    mb.add_hip_roof(x - w * 0.5, y - d * 0.5, x + w * 0.5, y + d * 0.5, z_roof, 28, "slate", overhang=0.4)

    z_mast = z_roof + 3.0
    mb.add_cyl(x, y, z_mast, z_mast + 11.0, 0.18, "timber", seg=8, r2=0.08)
    mb.add_beam((x - 4.2, y, z_mast + 8.5), (x + 4.2, y, z_mast + 8.5), 0.10, 0.10, "timber")
    for sx in (-3.8, 3.8):
        mb.add_beam((x + sx, y, z_mast + 8.5), (x, y, z_mast + 10.8), 0.03, 0.03, "iron")

    mb.add_cyl(x - 2.8, y, z_mast + 6.2, z_mast + 7.8, 0.45, "black", seg=8, r2=0.04)
    mb.add_cyl(x + 2.8, y, z_mast + 7.4, z_mast + 5.8, 0.45, "black", seg=8, r2=0.04)
    mb.add_cyl(x, y, z_mast + 11.0, z_mast + 11.6, 0.03, "brass", seg=6)
    mb.add_beam((x - 0.5, y, z_mast + 11.5), (x + 0.5, y, z_mast + 11.5), 0.04, 0.04, "brass")
    return dict(kind="harbour_signal_station", x=x, y=y, z=z)


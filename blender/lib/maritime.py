"""
maritime.py -- Victorian maritime engineering components.
GENERATION II — OPERATION VICTORIA (PERICLES-II)

Harbour basins, stone quay walls with coping stones and timber fenders,
pontoons, landing stages, graving docks, swing bridges, caissons and slipways.
"""
import math
from core import MeshBuilder, QUAY_Z, WATER_Z, DOCK_BED_Z
import parts as P


# ================================================================ quay wall
def quay_wall(mb, axis, fixed, u0, u1, inward, top_z=QUAY_Z, bed_z=DOCK_BED_Z,
              face="granite", coping_w=1.20, batter=0.045, fender=True,
              ladders=True, ladder_every=34.0, rings=True, ring_every=17.0,
              piles=True, pile_every=6.0):
    """A Victorian masonry quay wall with granite coping, battered ashlar courses,
    algae water staining, vertical creosoted fender piles, ladders and mooring rings."""
    mp = P.wmap(axis, fixed, inward)

    # Ashlar courses with batter and algae waterline staining
    steps = 8
    for i in range(steps):
        za = bed_z + (top_z - bed_z) * i / steps
        zb = bed_z + (top_z - bed_z) * (i + 1) / steps
        da = batter * (top_z - za)
        db = batter * (top_z - zb)
        course_mat = "algae" if za < WATER_Z + 1.2 and zb > WATER_Z - 1.2 else face
        P.slab(mb, mp, u0, u1, za, zb, -da, 0.0 + (-db) + 1.8, course_mat)

    # Solid rubble backing
    P.slab(mb, mp, u0, u1, bed_z, top_z - 0.55, 1.4, 3.4, "rubble")

    # Heavy granite coping stones with rounded/chamfered water-side arris
    P.slab(mb, mp, u0, u1, top_z - 0.55, top_z, -0.32, coping_w, "granite")
    P.slab(mb, mp, u0, u1, top_z - 0.65, top_z - 0.55, -0.38, coping_w, "granite")

    # Horizontal timber waling along quay face
    if fender:
        P.slab(mb, mp, u0, u1, top_z - 1.40, top_z - 0.95, -0.52, -0.22, "creosote")
        P.slab(mb, mp, u0, u1, 1.20, 1.65, -0.42, -0.15, "creosote")

    # Vertical creosoted timber fender piles with iron strap brackets
    if piles:
        n_piles = max(2, int(abs(u1 - u0) / pile_every))
        for i in range(n_piles + 1):
            uu = u0 + (u1 - u0) * i / n_piles
            # Heavy vertical pile (350mm x 350mm)
            P.slab(mb, mp, uu - 0.18, uu + 0.18, bed_z, top_z - 0.15, -0.58, -0.22, "creosote")
            # Iron pile head capping
            P.slab(mb, mp, uu - 0.20, uu + 0.20, top_z - 0.22, top_z - 0.12, -0.60, -0.20, "iron")
            # Iron fixing strap brackets into stone masonry
            for zh in (top_z - 1.2, top_z - 2.8, 1.4):
                P.slab(mb, mp, uu - 0.22, uu + 0.22, zh, zh + 0.10, -0.62, 0.15, "iron")

    # Recessed iron dock ladders
    if ladders:
        n = max(1, int(abs(u1 - u0) / ladder_every))
        for i in range(n):
            uu = u0 + (u1 - u0) * (i + 0.5) / n
            dock_ladder(mb, mp, uu, WATER_Z - 1.2, top_z - 0.55)

    # Forged iron mooring rings
    if rings:
        n = max(1, int(abs(u1 - u0) / ring_every))
        for i in range(n):
            uu = u0 + (u1 - u0) * (i + 0.5) / n
            mooring_ring(mb, mp, uu, top_z - 2.15)


def dock_ladder(mb, mp, u, z_bottom, z_top, mat="iron"):
    """Recessed iron ladder set into a quay wall recess with coping handhold hoops."""
    w = 0.54
    P.slab(mb, mp, u - w / 2 - 0.08, u + w / 2 + 0.08, z_bottom, z_top, -0.28, -0.04, "black")
    for du in (-w / 2, w / 2):
        P.slab(mb, mp, u + du - 0.035, u + du + 0.035, z_bottom, z_top, -0.24, -0.18, mat)
    z = z_bottom + 0.30
    while z < z_top - 0.15:
        P.slab(mb, mp, u - w / 2, u + w / 2, z - 0.025, z + 0.025, -0.26, -0.20, mat)
        z += 0.32
    # Handhold hoops emerging over coping
    for du in (-w / 2, w / 2):
        P.slab(mb, mp, u + du - 0.04, u + du + 0.04, z_top, z_top + 0.65, -0.05, 0.05, mat)


def mooring_ring(mb, mp, u, z, r=0.22, mat="iron"):
    """Cast-iron eye bolt and forged loose ring hanging flat against stone."""
    P.slab(mb, mp, u - 0.12, u + 0.12, z - 0.12, z + 0.12, -0.32, -0.20, mat)
    P.slab(mb, mp, u - 0.06, u + 0.06, z - 0.06, z + 0.06, -0.42, -0.30, mat)
    n = 12
    t = 0.032
    for i in range(n):
        a0 = 2 * math.pi * i / n
        a1 = 2 * math.pi * (i + 1) / n
        p0 = mp(u + math.cos(a0) * r, z + math.sin(a0) * r - r, -0.35)
        p1 = mp(u + math.cos(a1) * r, z + math.sin(a1) * r - r, -0.35)
        mb.add_beam(p0, p1, t, t, mat)


def bollard(mb, x, y, z, mat="iron", h=1.05, style="liverpool"):
    """Cast-iron dockside bollard with flared head and flanged base."""
    mb.add_cyl(x, y, z, z + 0.12, 0.44, mat, seg=12)
    mb.add_cyl(x, y, z + 0.12, z + h * 0.85, 0.28, mat, seg=12, r2=0.25)
    mb.add_cyl(x, y, z + h * 0.85, z + h, 0.25, mat, seg=12, r2=0.36)
    mb.add_cyl(x, y, z + h, z + h + 0.08, 0.36, mat, seg=12, r2=0.22)


def capstan(mb, x, y, z, mat="iron", h=1.0):
    """Hydraulic warping capstan set in the quay pavement."""
    mb.add_cyl(x, y, z, z + 0.10, 0.82, mat, seg=12)
    mb.add_cyl(x, y, z + 0.10, z + h * 0.45, 0.42, mat, seg=12, r2=0.34)
    mb.add_cyl(x, y, z + h * 0.45, z + h * 0.82, 0.34, mat, seg=12, r2=0.44)
    mb.add_cyl(x, y, z + h * 0.82, z + h, 0.44, mat, seg=12, r2=0.36)
    mb.add_cyl(x, y, z + h, z + h + 0.06, 0.48, mat, seg=12)


def boat_steps(mb, axis, fixed, u0, u1, inward, z_quay=QUAY_Z, z_water=WATER_Z, mat="granite"):
    """Recessed granite boat landing steps cut into quay wall for small boats."""
    mp = P.wmap(axis, fixed, inward)
    depth = 2.4
    P.slab(mb, mp, u0, u1, z_water - 0.6, z_quay, 0.0, depth, "black")
    n_steps = max(6, int((z_quay - (z_water - 0.4)) / 0.22))
    rise = (z_quay - (z_water - 0.4)) / n_steps
    run = depth / n_steps
    for i in range(n_steps):
        zs = (z_water - 0.4) + rise * i
        ds = run * i
        P.slab(mb, mp, u0 + 0.1, u1 - 0.1, zs, zs + rise, ds, depth, mat)
    # Iron safety handrail
    P.slab(mb, mp, u0 + 0.05, u0 + 0.10, z_water, z_quay + 0.9, depth * 0.5, depth * 0.5 + 0.05, "iron")


# ================================================================ hydraulic swing bridge
def swing_bridge(mb, x_pivot, y_pivot, z_quay=QUAY_Z, length=34.0, width=6.8, angle_deg=90.0):
    """Victorian hydraulic wrought-iron swing bridge crossing dock lock entrance.
    
    Spans squarely across the lock channel between North and South lock walls.
    Rests on heavy dressed granite abutments built into both lock entrance walls.
    Pivot pier sits in the lock channel with hydraulic turning engine cabin.
    Continuous rail track runs along the deck connecting both sides of the lock.
    """
    rad = math.radians(angle_deg)
    dx = math.cos(rad)
    dy = math.sin(rad)
    nx = -dy
    ny = dx

    t0 = -length / 2
    t1 = length / 2
    p_start = (x_pivot + dx * t0, y_pivot + dy * t0)
    p_end = (x_pivot + dx * t1, y_pivot + dy * t1)

    # --- CENTRAL GRANITE PIVOT PIER ---
    mb.add_cyl(x_pivot, y_pivot, DOCK_BED_Z, z_quay - 0.40, 4.5, "granite", seg=18)
    mb.add_cyl(x_pivot, y_pivot, z_quay - 0.40, z_quay - 0.10, 4.8, "granite", seg=18)
    mb.add_cyl(x_pivot, y_pivot, z_quay - 0.10, z_quay + 0.15, 4.2, "iron", seg=18)
    mb.add_cyl(x_pivot, y_pivot, z_quay + 0.15, z_quay + 0.45, 1.2, "steel", seg=12)

    # --- SHORE RESTING ABUTMENTS IN LOCK MASONRY ---
    for pt_abut, sgn in ((p_start, -1), (p_end, +1)):
        ax0 = pt_abut[0] - abs(nx) * (width / 2 + 1.2) - abs(dx) * 1.5
        ax1 = pt_abut[0] + abs(nx) * (width / 2 + 1.2) + abs(dx) * 1.5
        ay0 = pt_abut[1] - abs(ny) * (width / 2 + 1.2) - abs(dy) * 1.5
        ay1 = pt_abut[1] + abs(ny) * (width / 2 + 1.2) + abs(dy) * 1.5
        mb.add_box(min(ax0, ax1), min(ay0, ay1), DOCK_BED_Z,
                   max(ax0, ax1), max(ay0, ay1), z_quay - 0.15, "granite")
        # Heavy cast-iron bearing shoes and hydraulic wedge locking sockets
        for s in (-width / 2, width / 2):
            bx = pt_abut[0] + nx * s
            by = pt_abut[1] + ny * s
            mb.add_box_c(bx, by, z_quay - 0.05, 1.1, 1.1, 0.22, "iron")

    # --- MAIN FISHBELLY / HOGBACK THROUGH-TRUSS GIRDERS ---
    n_seg = 16
    for side in (-width / 2, width / 2):
        pts_bot = []
        pts_top = []
        for i in range(n_seg + 1):
            t = t0 + (t1 - t0) * i / n_seg
            px = x_pivot + dx * t + nx * side
            py = y_pivot + dy * t + ny * side
            # Parabolic hogback arch profile: ends 1.4m above deck, center 4.2m above deck
            parab = 1.0 - (t / (length / 2)) ** 2
            h_truss = 1.45 + parab * 2.85
            pts_bot.append((px, py, z_quay - 0.10))
            pts_top.append((px, py, z_quay + h_truss))

        # Bottom box tension chord
        for i in range(n_seg):
            mb.add_beam(pts_bot[i], pts_bot[i + 1], 0.45, 0.55, "iron")
        # Top compression arch boom
        for i in range(n_seg):
            mb.add_beam(pts_top[i], pts_top[i + 1], 0.40, 0.48, "iron")
        # Vertical posts & diagonal cross-ties
        for i in range(n_seg + 1):
            mb.add_beam(pts_bot[i], pts_top[i], 0.14, 0.14, "iron")
        for i in range(n_seg):
            mb.add_beam(pts_bot[i], pts_top[i + 1], 0.07, 0.07, "iron")
            mb.add_beam(pts_top[i], pts_bot[i + 1], 0.07, 0.07, "iron")

    # --- TRANSVERSE FLOORBEAMS & SOLID TIMBER DECK ---
    for i in range(n_seg + 1):
        t = t0 + (t1 - t0) * i / n_seg
        c0 = (x_pivot + dx * t - nx * (width / 2), y_pivot + dy * t - ny * (width / 2), z_quay - 0.12)
        c1 = (x_pivot + dx * t + nx * (width / 2), y_pivot + dy * t + ny * (width / 2), z_quay - 0.12)
        mb.add_beam(c0, c1, 0.30, 0.42, "iron")

    # Solid oak bridge deck
    for i in range(n_seg):
        t_a = t0 + (t1 - t0) * i / n_seg
        t_b = t0 + (t1 - t0) * (i + 1) / n_seg
        p00 = (x_pivot + dx * t_a - nx * (width / 2 - 0.1), y_pivot + dy * t_a - ny * (width / 2 - 0.1), z_quay + 0.10)
        p01 = (x_pivot + dx * t_b - nx * (width / 2 - 0.1), y_pivot + dy * t_b - ny * (width / 2 - 0.1), z_quay + 0.10)
        p11 = (x_pivot + dx * t_b + nx * (width / 2 - 0.1), y_pivot + dy * t_b - ny * (width / 2 - 0.1), z_quay + 0.10)
        p10 = (x_pivot + dx * t_a + nx * (width / 2 - 0.1), y_pivot + dy * t_a - ny * (width / 2 - 0.1), z_quay + 0.10)
        mb.add_quad(p00, p01, p11, p10, "plank")
        mb.add_quad(p10, p11, p01, p00, "timber")

    # Solid curb timbers / wheel guards along outer walkway edges
    for s in (-width / 2 + 0.25, width / 2 - 0.25):
        q0 = (p_start[0] + nx * s, p_start[1] + ny * s, z_quay + 0.22)
        q1 = (p_end[0] + nx * s, p_end[1] + ny * s, z_quay + 0.22)
        mb.add_beam(q0, q1, 0.22, 0.22, "timber")

    # --- CONTINUOUS STANDARD GAUGE RAILWAY TRACK ACROSS BRIDGE ---
    for r_off in (-0.7175, 0.7175):
        r0 = (p_start[0] + nx * r_off, p_start[1] + ny * r_off, z_quay + 0.22)
        r1 = (p_end[0] + nx * r_off, p_end[1] + ny * r_off, z_quay + 0.22)
        mb.add_beam(r0, r1, 0.08, 0.14, "steel")
    # Check rails inside running rails
    for c_off in (-0.62, 0.62):
        c0 = (p_start[0] + nx * c_off, p_start[1] + ny * c_off, z_quay + 0.20)
        c1 = (p_end[0] + nx * c_off, p_end[1] + ny * c_off, z_quay + 0.20)
        mb.add_beam(c0, c1, 0.06, 0.12, "steel")

    # --- CENTRAL PIVOT SUSPENSION TOWER & PORTAL ---
    for t_tw in (-2.2, 2.2):
        for s in (-width / 2, width / 2):
            px = x_pivot + dx * t_tw + nx * s
            py = y_pivot + dy * t_tw + ny * s
            mb.add_beam((px, py, z_quay), (px, py, z_quay + 5.2), 0.22, 0.22, "iron")
        # Overhead transverse tie frame
        pa = (x_pivot + dx * t_tw - nx * (width / 2), y_pivot + dy * t_tw - ny * (width / 2), z_quay + 5.0)
        pb = (x_pivot + dx * t_tw + nx * (width / 2), y_pivot + dy * t_tw - ny * (width / 2), z_quay + 5.0)
        mb.add_beam(pa, pb, 0.22, 0.28, "iron")

    # --- HYDRAULIC ENGINE CABIN ---
    cx = x_pivot + nx * (width / 2 + 2.2)
    cy = y_pivot + ny * (width / 2 + 2.2)
    # Cantilevered iron bracket support
    mb.add_box_c(cx, cy, z_quay - 0.2, 2.8, 2.4, 0.4, "iron")
    # Timber panelled cabin
    mb.add_box_c(cx, cy, z_quay + 1.4, 2.6, 2.2, 2.6, "timber")
    # Hipped slate roof with lead ridge roll
    mb.add_hip_roof(cx - 1.45, cy - 1.25, cx + 1.45, cy + 1.25, z_quay + 2.7, 28, "slate")
    # Glazed viewing windows
    mb.add_box_c(cx, cy - 1.12, z_quay + 1.5, 1.8, 0.08, 1.1, "glass")

    return dict(pivot=(x_pivot, y_pivot), length=length)


# ================================================================ landing stage
def pontoon(mb, x0, y0, x1, y1, z_deck=1.35, thickness=1.5, lanes=2):
    """Floating landing stage modelled on the Liverpool landing stage."""
    mb.add_box(x0, y0, z_deck - thickness, x1, y1, z_deck, "steel_plate")
    mb.add_box(x0, y0, z_deck - thickness - 0.35, x1, y1, z_deck - thickness, "black")
    mb.add_box(x0 - 0.1, y0 - 0.1, z_deck, x1 + 0.1, y1 + 0.1, z_deck + 0.06, "plank", top="plank")
    mb.add_box(x0 - 0.15, y0 - 0.15, z_deck, x0 + 0.25, y1 + 0.15, z_deck + 0.22, "iron")

    n = max(2, int((y1 - y0) / 6.0))
    for i in range(n + 1):
        cy = y0 + (y1 - y0) * i / n
        for cx in (x0 + 1.4, x1 - 1.4):
            mb.add_cyl(cx, cy, z_deck, z_deck + 3.9, 0.10, "iron", seg=8)

    zr = z_deck + 3.9
    xm = (x0 + x1) / 2
    mb.add_quad((x0 - 0.5, y0, zr), (xm, y0, zr + 0.75), (xm, y1, zr + 0.75), (x0 - 0.5, y1, zr), "canvas")
    mb.add_quad((xm, y0, zr + 0.75), (x1 + 0.5, y0, zr), (x1 + 0.5, y1, zr), (xm, y1, zr + 0.75), "canvas")

    mb.add_box(x0 - 0.55, y0, zr - 0.25, x0 - 0.45, y1, zr + 0.05, "canvas")
    mb.add_box(x1 + 0.45, y0, zr - 0.25, x1 + 0.55, y1, zr + 0.05, "canvas")

    mb.add_box(x1 - 4.5, y0 + 3.0, z_deck, x1 - 1.2, y1 - 3.0, z_deck + 2.9, "timber")
    mb.add_box(x1 - 4.8, y0 + 2.7, z_deck + 2.9, x1 - 0.9, y1 - 2.7, z_deck + 3.05, "slate")
    mb.add_quad_uv((x1 - 4.52, y0 + 3.05, z_deck + 2.0), (x1 - 4.52, y1 - 3.05, z_deck + 2.0),
                   (x1 - 4.52, y1 - 3.05, z_deck + 2.75), (x1 - 4.52, y0 + 3.05, z_deck + 2.75),
                   "sign_booking_office")

    for i in range(n + 1):
        cy = y0 + (y1 - y0) * i / n
        mb.add_cyl(x1 - 1.4, cy, zr + 0.1, zr + 0.55, 0.05, "iron", seg=6)
        mb.add_cyl(x1 - 1.4, cy, zr + 0.55, zr + 0.92, 0.14, "lamp_glow", seg=8, r2=0.09)
    return dict(deck=z_deck, zroof=zr + 0.75)


# ================================================================ landing stage gangway bridge
def gangway_bridge(mb, x0, y0, z_low, x1, z_high, width=3.8, canopy=True,
                   side="Y", lattice=True):
    """Articulated shore-to-pontoon landing stage bowstring lattice bridge.
    
    Includes massive dressed granite shore abutment pylons, cast-iron trunnion bearings,
    heavy wrought-iron bowstring lattice through-trusses, solid timber deck, curved zinc canopy,
    mid-span floating pontoon support bent, and pontoon-end roller bogie carriage on steel tracks.
    """
    length = abs(x1 - x0)
    z_shore = z_low
    z_pont = z_high

    # --- 1. SHORE ABUTMENT PYLONS & TRUNNION BEARINGS (at x = x0) ---
    for s in (-1, 1):
        py = y0 + s * (width / 2 + 1.15)
        # Heavy dressed granite pylon
        mb.add_box(x0 - 0.3, py - 0.75, 1.2, x0 + 2.8, py + 0.75, 7.8, "granite")
        # Moulded sandstone cap
        mb.add_box(x0 - 0.4, py - 0.85, 7.8, x0 + 2.9, py + 0.85, 8.2, "sandstone")
        # Cast-iron trunnion hinge pillow block
        mb.add_cyl(x0 + 0.1, y0 + s * (width / 2), z_shore + 0.20, z_shore + 0.48, 0.42, "iron", seg=12, axis="Y")
        mb.add_cyl(x0 - 0.2, y0 + s * (width / 2), z_shore + 0.34, z_shore + 0.34, 0.12, "steel", seg=8, axis="Y")

    # Overhead cast-iron arch tie portal across roadway entrance
    mb.add_beam((x0 + 0.5, y0 - width / 2 - 1.15, 7.4),
                (x0 + 0.5, y0 + width / 2 + 1.15, 7.4), 0.28, 0.45, "iron")

    # Granite / flagstone shore approach platform
    mb.add_box(x0, y0 - width / 2 - 0.2, z_shore - 0.25,
               x0 + 3.2, y0 + width / 2 + 0.2, z_shore + 0.12, "granite", top="flags")

    # --- 2. MAIN BOWSTRING THROUGH-TRUSS GIRDERS (x0 to x1) ---
    n = 16
    def pt(t, z_off=0.0, side_off=0.0):
        xx = x0 + (x1 - x0) * t
        zz = z_shore + (z_pont - z_shore) * t + z_off
        return (xx, y0 + side_off, zz)

    for s in (-1, 1):
        so = s * (width / 2)
        pts_bot = []
        pts_top = []
        for i in range(n + 1):
            t = i / n
            # Parabolic bowstring arch rise: 3.2 m above deck at midspan (t = 0.5)
            arch_h = 1.2 + 4.0 * t * (1.0 - t) * 2.8
            pts_bot.append(pt(t, 0.0, so))
            pts_top.append(pt(t, arch_h, so))

        # Bottom box tension chord
        for i in range(n):
            mb.add_beam(pts_bot[i], pts_bot[i + 1], 0.45, 0.55, "iron")
        # Top compression arch boom
        for i in range(n):
            mb.add_beam(pts_top[i], pts_top[i + 1], 0.40, 0.45, "iron")
        # Vertical struts & diagonal lattice cross-bracing
        for i in range(n + 1):
            mb.add_beam(pts_bot[i], pts_top[i], 0.12, 0.12, "iron")
        for i in range(n):
            mb.add_beam(pts_bot[i], pts_top[i + 1], 0.06, 0.06, "iron")
            mb.add_beam(pts_top[i], pts_bot[i + 1], 0.06, 0.06, "iron")

    # --- 3. TRANSVERSE FLOORBEAMS, TIMBER DECK & CURVED CANOPY ---
    for i in range(n + 1):
        t = i / n
        mb.add_beam(pt(t, -0.15, -width / 2), pt(t, -0.15, width / 2), 0.28, 0.38, "iron")

    for i in range(n):
        t0, t1 = i / n, (i + 1) / n
        # Solid timber deck
        mb.add_quad(pt(t0, 0.06, -width / 2 + 0.05), pt(t1, 0.06, -width / 2 + 0.05),
                    pt(t1, 0.06, width / 2 - 0.05), pt(t0, 0.06, width / 2 - 0.05), "plank")
        mb.add_quad(pt(t0, -0.06, width / 2 - 0.05), pt(t1, -0.06, width / 2 - 0.05),
                    pt(t1, -0.06, -width / 2 + 0.05), pt(t0, -0.06, -width / 2 + 0.05), "timber")

    # Overhead curved zinc/lead canopy
    if canopy:
        for i in range(n):
            t0, t1 = i / n, (i + 1) / n
            cz0 = 1.2 + 4.0 * t0 * (1.0 - t0) * 2.8 + 0.25
            cz1 = 1.2 + 4.0 * t1 * (1.0 - t1) * 2.8 + 0.25
            # North and South slopes of curved canopy roof
            p_nw = pt(t0, cz0, -width / 2 * 0.96)
            p_ne = pt(t1, cz1, -width / 2 * 0.96)
            p_cw0 = pt(t0, cz0 + 0.35, 0.0)
            p_ce0 = pt(t1, cz1 + 0.35, 0.0)
            p_sw = pt(t0, cz0, width / 2 * 0.96)
            p_se = pt(t1, cz1, width / 2 * 0.96)
            # Solid lead / zinc roofing
            mb.add_quad(p_nw, p_ne, p_ce0, p_cw0, "lead")
            mb.add_quad(p_cw0, p_ce0, p_se, p_sw, "lead")
            # Underside ceiling
            mb.add_quad(p_cw0, p_ce0, p_ne, p_nw, "timber")
            mb.add_quad(p_sw, p_se, p_ce0, p_cw0, "timber")
            # Eaves valance boards
            for s in (-1, 1):
                mb.add_beam(pt(t0, cz0 - 0.12, s * width / 2 * 0.96),
                            pt(t1, cz1 - 0.12, s * width / 2 * 0.96), 0.08, 0.22, "iron")

    # --- 4. MID-SPAN FLOATING PONTOON SUPPORT BENT (at x = -48.0, t = 0.5) ---
    t_mid = 0.5
    p_mid = pt(t_mid, 0.0, 0.0)
    p_mx, p_mz = p_mid[0], p_mid[2]
    # Intermediate iron pontoon float in the river
    mb.add_box(p_mx - 3.2, y0 - width / 2 - 1.8, -0.6,
               p_mx + 3.2, y0 + width / 2 + 1.8, 1.25, "iron")
    # Structural iron support trestle stool rising from pontoon deck to bridge underside
    mb.add_box(p_mx - 2.2, y0 - width / 2 - 0.6, 1.25,
               p_mx + 2.2, y0 + width / 2 + 0.6, p_mz - 0.22, "iron")
    # Timber rubbing fender around intermediate pontoon
    mb.add_box(p_mx - 3.4, y0 - width / 2 - 2.0, 0.2,
               p_mx + 3.4, y0 + width / 2 + 2.0, 1.35, "creosote")

    # --- 5. PONTOON-END ROLLER BOGIE CARRIAGE ON STEEL TRACKWAYS (at x = x1) ---
    # Flanged steel roller wheels and bearing pedestals
    for s in (-1, 1):
        so = s * (width / 2)
        wx, wy = x1, y0 + so
        # Dual steel roller wheels (front & back)
        for dx_w in (-0.55, 0.55):
            mb.add_cyl(wx + dx_w, wy, z_pont - 0.25, z_pont + 0.25, 0.32, "steel", seg=12, axis="Y")
        # Heavy cast-iron bearing horncheek carriage
        mb.add_box(wx - 0.95, wy - 0.22, z_pont - 0.15, wx + 0.95, wy + 0.22, z_pont + 0.35, "iron")
        # Steel rail trackway embedded in pontoon deck
        mb.add_box(x1 - 2.6, wy - 0.18, z_pont - 0.20, x1 + 2.6, wy + 0.18, z_pont - 0.02, "steel")
        # Heavy buffer stop blocks at track end
        mb.add_box(x1 - 2.8, wy - 0.22, z_pont - 0.20, x1 - 2.4, wy + 0.22, z_pont + 0.28, "iron")

    # Articulated transition apron flap onto pontoon deck
    mb.add_quad((x1, y0 - width / 2, z_pont + 0.08), (x1 - 2.2, y0 - width / 2, z_pont),
                (x1 - 2.2, y0 + width / 2, z_pont), (x1, y0 + width / 2, z_pont + 0.08), "plank")
    mb.add_quad((x1, y0 + width / 2, z_pont + 0.08), (x1 - 2.2, y0 + width / 2, z_pont),
                (x1 - 2.2, y0 - width / 2, z_pont), (x1, y0 - width / 2, z_pont + 0.08), "timber")

    return dict(length=length)


# ================================================================ graving dock
def graving_dock(mb, x0, y0, length, width, depth=9.6, coping="granite",
                 altar_steps=6, altar_w=3.4, entrance="N", stairs=True,
                 keel_blocks=True, caissons=()):
    """Victorian graving (dry) dock of the Belfast Alexandra Graving Dock type."""
    x1, y1 = x0 + width, y0 + length
    floor_z = QUAY_Z - depth
    t = 1.8

    mb.add_box(x0, y0, floor_z - 0.6, x1, y1, floor_z, "granite")

    step_h = (depth - 1.2) / altar_steps
    for side, (fx0, fx1) in (("W", (x0, x0 + t)), ("E", (x1 - t, x1))):
        n = altar_steps
        for i in range(n):
            zt = floor_z + step_h * (i + 1)
            inset = altar_w * (1 - (i + 1) / (n + 0.4))
            if side == "W":
                a = x0 + inset
                mb.add_box(a, y0, floor_z, fx1, y1, zt, "granite")
            else:
                b = x1 - inset
                mb.add_box(fx0, y0, floor_z, b, y1, zt, "granite")
        zt = floor_z + step_h * n
        mb.add_box(fx0, y0, zt, fx1, y1, QUAY_Z - 0.55, "rubble")
        if side == "W":
            mb.add_box(x0 - 0.3, y0, QUAY_Z - 0.55, x0 + 1.5, y1, QUAY_Z, coping)
        else:
            mb.add_box(x1 - 1.5, y0, QUAY_Z - 0.55, x1 + 0.3, y1, QUAY_Z, coping)

    for endl, yy in (("S", y0), ("N", y1)):
        mb.add_box(x0, yy - 0.0 if endl == "N" else yy - t, floor_z,
                   x1, yy + t if endl == "N" else yy + 0.0, QUAY_Z - 0.55, "rubble")
    mb.add_box(x0, y0 - t, QUAY_Z - 0.55, x1, y0, QUAY_Z, coping)

    for frac in caissons:
        yy = y0 + length * frac
        mb.add_box(x0, yy - 0.9, floor_z, x0 + 2.2, yy + 0.9, QUAY_Z - 1.2, "granite")
        mb.add_box(x1 - 2.2, yy - 0.9, floor_z, x1, yy + 0.9, QUAY_Z - 1.2, "granite")

    if keel_blocks:
        nb = int(length / 3.4)
        for i in range(nb):
            yy = y0 + length * (i + 0.5) / nb
            if yy < y0 + 4 or yy > y1 - 4:
                continue
            # Solid oak keel blocks on dock floor centerline
            mb.add_box_c((x0 + x1) / 2, yy, floor_z + 0.85, 1.6, 1.4, 1.7, "timber")
            mb.add_box_c((x0 + x1) / 2, yy, floor_z + 0.12, 2.0, 1.8, 0.24, "timber")

        # Heavy diagonal timber bilge shores propping vessel hull position
        nb_shores = int(length / 7.2)
        for i in range(nb_shores):
            yy = y0 + 6.0 + (length - 12.0) * (i + 0.5) / nb_shores
            mb.add_beam((x0 + altar_w * 0.65, yy, floor_z + depth * 0.42),
                        ((x0 + x1) / 2 - 2.0, yy, floor_z + 1.8), 0.28, 0.28, "timber")
            mb.add_beam((x1 - altar_w * 0.65, yy, floor_z + depth * 0.42),
                        ((x0 + x1) / 2 + 2.0, yy, floor_z + 1.8), 0.28, 0.28, "timber")

    if stairs:
        for k in range(3):
            yy = y0 + length * (0.22 + 0.26 * k)
            _dock_stair(mb, x1 - t - 0.6, yy, floor_z, QUAY_Z, altar_steps, altar_w)

    nb = int(length / 12.0)
    for i in range(nb + 1):
        yy = y0 + 2.0 + (length - 4.0) * i / nb
        bollard(mb, x0 + 0.55, yy, QUAY_Z)
        bollard(mb, x1 - 0.55, yy, QUAY_Z)
    return dict(floor_z=floor_z, x0=x0, y0=y0, x1=x1, y1=y1)


def _dock_stair(mb, x, y, z_bottom, z_top, n_altar, altar_w, width=1.6):
    n = max(6, int((z_top - z_bottom) / 0.28))
    rise = (z_top - z_bottom) / n
    run = 0.30
    for i in range(n):
        zz = z_bottom + rise * i
        mb.add_box(x - width / 2, y + run * i, zz, x + width / 2, y + run * (i + 1) + 0.02,
                   zz + rise, "granite")


def caisson(mb, x0, y0, width, height, thickness=1.6, draft_end=False):
    """Hollow wrought-iron caisson floating gate."""
    mb.add_box(x0, y0, -4.0, x0 + width, y0 + thickness, height, "steel_plate")
    mb.add_box(x0 + 0.6, y0 - 0.25, 0.8, x0 + width - 0.6, y0 + thickness + 0.25, 1.05, "iron")
    mb.add_box(x0, y0 - 0.12, -3.6, x0 + width, y0, 1.0, "timber")
    for i in range(int(width / 1.6)):
        mb.add_box_c(x0 + 0.9 + i * 1.6, y0 + thickness / 2, 1.35, 0.55, thickness + 0.6, 0.45, "iron")
    mb.add_box(x0, y0 - 0.2, -4.2, x0 + width, y0 + thickness + 0.2, -3.7, "timber")
    return dict(deck=1.05, width=width)


# ================================================================ slipways
def slipway(mb, x0, y0, width, length, angle_deg=2.6, top_z=3.2, end_z=-6.0,
            rails=3, keel_block=True):
    """Building slipway running into the river with keel blocks and shoring staging."""
    mb.add_box(x0, y0, end_z - 0.4, x0 + width, y0 + length, end_z + 0.1, "rubble")
    n = 10
    for i in range(n):
        t0, t1 = i / n, (i + 1) / n
        zz0 = end_z + (top_z - end_z) * t0
        zz1 = end_z + (top_z - end_z) * t1
        mb.add_quad((x0, y0 + length * t0, zz0), (x0 + width, y0 + length * t0, zz0),
                    (x0 + width, y0 + length * t1, zz1), (x0, y0 + length * t1, zz1), "plank")
        mb.add_quad((x0 + width, y0 + length * t0, zz0), (x0, y0 + length * t0, zz0),
                    (x0, y0 + length * t1, zz1 - 0.55), (x0 + width, y0 + length * t1, zz1 - 0.55), "rubble")

    for k in range(rails):
        bx = x0 + width * (0.5 + (k - (rails - 1) / 2) * 0.30)
        for i in range(n):
            t0, t1 = i / n, (i + 1) / n
            zz0 = end_z + (top_z - end_z) * t0 + 0.08
            zz1 = end_z + (top_z - end_z) * t1 + 0.08
            mb.add_quad((bx - 0.13, y0 + length * t0, zz0), (bx + 0.13, y0 + length * t0, zz0),
                        (bx + 0.13, y0 + length * t1, zz1), (bx - 0.13, y0 + length * t1, zz1), "iron")
    return dict(x0=x0, y0=y0, width=width, length=length)

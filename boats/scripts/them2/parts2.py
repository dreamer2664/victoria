"""
parts2.py -- boat's gear and furniture for THEMISTOCLES-II boats.

Material slots are symbolic indices, resolved to real materials per boat:
  0 main wood, 1 top/trim wood, 2 dark wood, 3 brass, 4 iron, 5 galvanized,
  6 leather, 7 rope, 8 canvas, 9 glass, 10 painted, 11 white, 12 red, 13 green
"""
from __future__ import annotations
import math
import numpy as np
from .geom2 import (MB, unit, lerp, clamp, smoothstep, cyl, sphere, dome, torus,
                    rope_coil, rivet_row, rot_axis, rot_x, rot_y, rot_z,
                    superellipse_section)

X = np.array([1.0, 0, 0]); Y = np.array([0.0, 1, 0]); Z = np.array([0.0, 0, 1])


# ---------------------------------------------------------------------------
# oars
# ---------------------------------------------------------------------------

def oar_builder(length=3.66, inboard_frac=0.34, blade_w=0.115,
                blade_len_frac=0.30, r_loom=0.024, mat_wood=0, mat_leather=6,
                mat_button=6):
    """
    One oar as (oar_mb, leather_mb), authored along +Y with the origin at the
    rowlock bearing point.  Handle in -Y, blade out +Y.
    Handles: rounded grip w/ knob, tapered octagonal loom, leather collar and
    turk's-head button at the rowlock, flat blade with centre ridge.
    """
    mb = MB("Oar")
    lea = MB("Oar_Gear")
    n = 30
    ss = np.linspace(0, 1, n)
    inb = length * inboard_frac

    def dims(s):
        xi = (s)  # 0 at rowlock -> 1 blade tip  (outboard, +Y)
        # blade region: from s=0.45 out
        bl = clamp((s - 0.42) / (1.0 - 0.42), 0.0, 1.0)
        # width & thickness
        w = r_loom * (1 - 0.10 * s)  # loom radius decay
        h = w
        if bl > 0:
            w = lerp(r_loom * 0.96, blade_w, math.sin(min(1.0, bl * 1.15) * math.pi / 2))
            if s > 0.97:
                w = lerp(blade_w, blade_w * 0.45, (s - 0.97) / 0.03)
            h = lerp(r_loom * 0.96, 0.010, min(1.0, bl * 1.6))
        return w, h

    path = []
    shapes = []
    frames_ = []
    for s in ss:
        y = s * (length - inb)
        w, h = dims(s)
        outb = y
        path.append([0, outb, 0])
        n_sect = lerp(2.0, 5.0, clamp((s - 0.42) / 0.1, 0, 1))
        shp = superellipse_section(w, h, n=n_sect, seg=12)
        frames_.append((np.array([0.0, 0, 1.0]), np.array([1.0, 0, 0])))
        shapes.append(shp)
    # inboard end (handle), continuing in -Y
    path_in = []
    shapes_in = []
    ss_in = np.linspace(0, 1, 10)
    for s in ss_in:
        y = -s * inb
        r = r_loom * (1.02 - 0.25 * s) if s < 0.90 else r_loom * 0.8
        if s > 0.985:
            r = r_loom * 0.75 * 1.15  # small knob
        path_in.append([0, y, 0])
        shapes_in.append(superellipse_section(r, r, n=2.0, seg=12))
    # assemble path: handle tip -> rowlock -> blade tip
    full_path = path_in[::-1] + path[1:]
    full_shapes = shapes_in[::-1] + shapes[1:]
    frames_all = [(np.array([0.0, 0, 1.0]), np.array([1.0, 0.0, 0.0]))] * len(full_path)
    mb.add_sweep(full_path, full_shapes, frames=frames_all)
    # blade ridge (spine along the blade back, on the upper face)
    ridge = []
    for s in np.linspace(0.50, 0.995, 14):
        y = s * (length - inb)
        w, h = dims(s)
        ridge.append([0, y, h + 0.0035])
    mb.add_tube(ridge, 0.004, segments=6, radii=[0.004 * (1 - 0.7 * k / 13) for k in range(14)])
    # leather collar (sleeve) + turk's-head button at the rowlock bearing
    lea.add_tube([[0, -0.12, 0], [0, 0.10, 0]], r_loom + 0.0025, segments=12,
                 mat=mat_leather)
    torus(lea, [0, 0.108, 0], r_loom + 0.004, 0.006, seg=14, rseg=6, axis="Y",
          mat=mat_button)
    # blanket stop inboard of the button: padded turk's head preventing the oar
    # from slipping through the rowlock when shipped
    torus(lea, [0, -0.135, 0], r_loom + 0.008, 0.011, seg=14, rseg=7, axis="Y",
          mat=mat_button)
    return mb, lea


def oar_stowed(boat_loa, side, xi_station, hull, thwart_z, blade_to_stern=True):
    """
    Position a stowed oar inside the boat: laid fore-and-aft, loom resting on
    the thwart nearest its station, blade aft along the side bench.  Returns
    (rotation, offset) placing the authored (origin-at-rowlock) oar.
    The stow follows the hull's inner line so nothing stands out through the
    planking.
    """
    sgn = 1.0 if side > 0 else -1.0
    from .hull2 import Hull2  # safety
    return None


# ---------------------------------------------------------------------------
# rowlocks (galvanised swivelling crutches in gunmetal sockets on pads)
# ---------------------------------------------------------------------------

def rowlock_crutch(pos, up=Z, r_horn=0.062, r_wire=0.0085, mat_socket=3,
                   mat_crutch=5, pad=(0.13, 0.06, 0.012)):
    """
    Swivel rowlock: gunmetal pad screwed to the gunwale cap, socket barrel,
    galvanised U-crutch with two horns and swivel pin.  `pos` = throat.
    Returns (fittings_mb, pin_top).  The oar pivots about pos/up.
    """
    mb = MB("Rowlock")
    px, py, pz = pos
    up = unit(up)
    # pad (rounded plate) on the gunwale, socket barrel under the crutch fork
    mb.add_box((px, py, pz - 0.030 - 0.004), pad, mat=mat_socket, chamfer=0.004)
    cyl(mb, (px, py, pz - 0.030), (px, py, pz - 0.002), 0.016, seg=12, mat=mat_socket)
    dome(mb, (px, py, pz - 0.001), 0.018, seg=10, rings=4, mat=mat_socket, squash=0.35)
    # four screws in the pad
    for dx in (-pad[0] * 0.38, pad[0] * 0.38):
        for dy in (-pad[1] * 0.30, pad[1] * 0.30):
            cyl(mb, (px + dx, py + dy, pz - 0.030), (px + dx, py + dy, pz - 0.026),
                0.004, seg=8, mat=mat_socket)
    # crutch: pin + stem + fork with two curved horns
    cyl(mb, (px, py, pz - 0.012), (px, py, pz + 0.012), r_wire * 0.85, seg=10,
        mat=mat_crutch)
    fork_z = pz + 0.012
    arms = []
    for sgn in (-1, 1):
        pts = []
        # horn sweeps up and inboard/outboard around a semicircle
        for k in range(9):
            a = (k / 8) * (math.pi * 0.52)
            r = r_horn
            ang = a
            yy = py + sgn * r * math.sin(ang) * 0.96
            zz = fork_z + r * (1 - math.cos(ang)) * 0.96
            pts.append([px, yy, zz])
        arms.append(pts)
    mb.add_tube(arms[0], r_wire, segments=8, mat=mat_crutch)
    mb.add_tube(arms[1], r_wire, segments=8, mat=mat_crutch)
    # horn tips: slightly flattened balls
    for sgn in (-1, 1):
        tip = arms[sgn][-1] if sgn == 1 else arms[0][-1]
    sphere(mb, arms[0][-1], r_wire * 1.35, seg=8, rings=5, mat=mat_crutch)
    sphere(mb, arms[1][-1], r_wire * 1.35, seg=8, rings=5, mat=mat_crutch)
    # cross tie between horn roots (the fork base)
    cyl(mb, arms[0][0], arms[1][0], r_wire, seg=8, mat=mat_crutch)
    cyl(mb, arms[0][1], arms[1][1], r_wire, seg=8, mat=mat_crutch)
    return mb


# ---------------------------------------------------------------------------
# rudder & tiller
# ---------------------------------------------------------------------------

def rudder_plate(hull, thk=0.028, mat=0, mat_iron=4):
    """
    Plate rudder hung on the sternpost/transom with pintles and gudgeons,
    stock through a trunk/head, long till with becket.  Pivot = pintle axis.
    Returns (mb, axis_point, axis_dir).
    """
    mb = MB("Rudder")
    xi = 1.0 if hull.transom else 0.97
    # rudder hangs aft of the stern plane
    x0 = hull.section_pt(1.0, 0.5, 0.0)[0] - (0.02 if hull.transom else 0.0)
    z_keel = hull.keel_z(0.97)
    z_top = hull.sheer_z(0.99) - 0.02
    # outline in X-Z plane: tapered blade, deeper at bottom (u measured aft of x0)
    out = [(0.0, z_top), (-0.26, z_top), (-0.30, z_top - 0.35),
           (-0.34, max(z_keel - 0.02, z_top - 0.62)), (-0.10, max(z_keel - 0.02, z_top - 0.62)),
           (0.0, z_keel + 0.02)]
    mb.add_plate(out, thk, plane="XZ", origin=(x0, -0.014, 0), mat=mat)
    # pintles on the blade straps + gudgeons on the sternpost
    z_p1 = lerp(z_keel, z_top, 0.12)
    z_p2 = lerp(z_keel, z_top, 0.55)
    for zp in (z_p1, z_p2):
        cyl(mb, (x0 + 0.002, 0, zp - 0.05), (x0 + 0.002, 0, zp + 0.05), 0.011,
            seg=10, mat=mat_iron)
        cyl(mb, (x0 - 0.035, 0, zp), (x0 + 0.02, 0, zp), 0.008, seg=8, mat=mat_iron)
    # stock up to the tiller level
    z_stock = z_top + 0.10
    cyl(mb, (x0 - 0.012, 0, z_top - 0.06), (x0 - 0.012, 0, z_stock + 0.03), 0.016,
        seg=12, mat=mat_iron)
    dome(mb, (x0 - 0.012, 0, z_stock + 0.03), 0.02, seg=10, rings=4, mat=mat_iron)
    # tiller: gently bowed, tapering toward the end, running FORWARD into the boat
    path = []
    for i in range(12):
        s = i / 11
        xx = x0 - 0.012 + s * 1.05
        zz = z_stock + 0.03 + math.sin(s * math.pi) * 0.02
        path.append([xx, 0, zz])
    mb.add_tube(path, 0.02, segments=10, mat=mat,
                radii=[0.028 * (1 - 0.6 * i / 11) for i in range(12)])
    sphere(mb, path[-1], 0.021, seg=10, rings=6, mat=mat, scale=(1.6, 1.0, 1.0))
    axis_pt = np.array([x0 + 0.002, 0, 0])
    return mb, axis_pt, Z.copy()


# ---------------------------------------------------------------------------
# rowing furniture: thwarts, knees, foot gratings, stretchers, lockers
# ---------------------------------------------------------------------------

def thwart(hull, xi, z_arc=0.52, thk=0.028, width=0.24, mat=0, mat_knee=2,
           knees=True, gap_ends=0.012, riser_thk=0.016, drop=0.0):
    """
    Shaped thwart spanning the inner planking faces, with rounded ends,
    edge chamfer, and hanging knees at alternate ends.  Riser assumed fitted
    (structure2.riser).  Returns the MB.
    """
    mb = MB("Thwarts")
    t_arc = hull.arc_to_t(xi, z_arc if z_arc < 1 else 0.52)
    off = -(0.048 + 0.011) + 0.004
    p1 = hull.section_pt(xi, t_arc, off)
    z = hull.section_pt(xi, t_arc, 0)[2] + drop
    hw = abs(p1[1]) - gap_ends
    # board with rounded ends: outline in plan
    n = 8
    outl = []
    w2 = width / 2
    for side in (-1, 1):
        pass
    outl = []
    outl.append((-hw + 0.05, -w2))
    outl.append((hw - 0.05, -w2))
    for k in range(5):
        a = (k / 4) * math.pi / 2
        outl.append((hw - 0.05 + 0.05 * math.cos(a), w2 - 0.05 + 0.05 * math.sin(a)))
    outl.append((-hw + 0.05, w2))
    for k in range(5):
        a = (k / 4) * math.pi / 2
        outl.append((-hw + 0.05 - 0.05 * math.sin(a), -w2 + 0.05 * math.cos(a)))
    outl = [(x, y) for x, y in outl]
    x_c = hull.X(xi)
    mb.add_plate(outl, thk, plane="XY", origin=(x_c, 0, z - thk / 2), mat=mat)
    if knees:
        for sgn in (-1, 1):
            for k in range(5):
                pass
    return mb, (x_c, hw, z)


def hanging_knee(hull, xi, z_top, sgn, rise_arm=0.30, mat=1):
    """
    Thwart knee: grown L with the standing arm under the thwart and the
    hanging leg following the planking down (clamped inside).
    """
    mb = MB("ThwartKnees")
    x = hull.X(xi)
    # hanging arm runs DOWN the inside face
    t_top = hull.arc_to_t(xi, 0.52)
    p_top = hull.section_pt(xi, t_top, -0.052)
    off = -0.056
    outline = []
    larm = 0.26
    darm = rise_arm
    # upright plate in YZ at x: standing arm s=0..larm toward centreline,
    # hanging arm down
    y0 = (abs(p_top[1]) - 0.02) * sgn
    out = [(y0 - larm * sgn * 0, 0.0)]
    out = []
    out.append((y0, 0.0))                                # under thwart at side
    out.append((y0 - sgn * larm, 0.0))                   # standing arm tip
    out.append((y0 - sgn * larm, -0.055))                # tip bottom (tapered)
    out.append((y0 - sgn * 0.10, -0.10))
    out.append((y0 - sgn * 0.02, -darm))                 # hanging arm bottom (tapered)
    out.append((y0 - sgn * 0.075, -darm))
    out.append((y0 - sgn * 0.115, -0.06))
    out.append((y0, -0.03))
    thk = 0.030
    basis = (np.array([0., 1, 0]), np.array([0., 0, 1]), np.array([1., 0, 0]))
    mb.add_plate(out, thk, basis=basis, origin=(x - thk / 2, 0, z_top + 0.012),
                 mat=mat)
    return mb


def foot_grating(x0, x1, y_half, z, slat_w=0.048, gap=0.020, rail=0.075,
                 thk=0.024, mat=0):
    """Slatted foot grating: two fore-aft rails + slats with gaps."""
    mb = MB("Floor_Gratings")
    for yy in (-y_half * 0.92, y_half * 0.92):
        mb.add_box(((x0 + x1) / 2, yy, z - thk / 2 + 0.004), (x1 - x0, rail, thk + 0.02),
                   mat=mat, chamfer=0.006)
    step = slat_w + gap
    nx = int((x1 - x0 - 0.05) / step)
    for i in range(nx):
        x = x0 + 0.03 + i * step + slat_w / 2
        mb.add_box((x, 0, z), (slat_w, 2 * y_half * 0.92 + rail, thk),
                   mat=mat, chamfer=0.004)
    return mb


def stretcher(hull, xi, z, w=0.30, mat=0):
    """Adjustable footrest board below a thwart, on two chock blocks."""
    mb = MB("Stretchers")
    x = hull.X(xi)
    mb.add_box((x, 0, z), (0.035, w, 0.012), mat=mat, chamfer=0.004)
    for sgn in (-1, 1):
        mb.add_box((x, sgn * (w / 2 - 0.03), z - 0.045), (0.04, 0.05, 0.08),
                   mat=mat, chamfer=0.004)
    return mb


def locker_box(center, size, mat=0, mat_wood=1, hinged_lid=True):
    """Storage locker with lid, hinges and hasp (bow/stern lockers)."""
    mb = MB("Locker")
    cx, cy, cz = center
    sx, sy, sz = size
    mb.add_box((cx, cy, cz), size, mat=mat, chamfer=0.008)
    if hinged_lid:
        mb.add_box((cx, cy, cz + sz / 2 + 0.010), (sx, sy, 0.020), mat=mat_wood,
                   chamfer=0.006)
        for dy in (-sy * 0.30, sy * 0.30):
            # strap hinges along the aft edge + hasp at front
            cyl(mb, (cx - sx / 2 - 0.002, cy + dy, cz + sz / 2 + 0.010),
                (cx - sx / 2 + 0.02, cy + dy, cz + sz / 2 + 0.010), 0.005, seg=8, mat=4)
        mb.add_box((cx + sx / 2 - 0.002, cy, cz + sz / 2 + 0.012), (0.006, 0.05, 0.02),
                   mat=4, chamfer=0.002)
    return mb


# ---------------------------------------------------------------------------
# gear: fenders, painter, anchors, boat hook, breaker, baler, bucket, lamps
# ---------------------------------------------------------------------------

def fender(center_hang, len_=0.34, r_rope=0.024, body_r=0.055, mat_rope=7,
           lanyard_len=0.42):
    """Rope fender hanging from the gunwale: lanyard + tapered rope body."""
    mb = MB("Fender")
    cx, cy, cz = center_hang
    top = (cx, cy, cz)
    bot = (cx, cy, cz - len_)
    # lanyard (eye splice at top)
    mb.add_tube([(cx, cy, cz + 0.05), (cx, cy, cz - lanyard_len * 0.98)],
                r_rope * 0.55, segments=8, mat=mat_rope)
    torus(mb, (cx, cy, cz + 0.05), 0.028, r_rope * 0.55, seg=12, rseg=6,
          axis="Y", mat=mat_rope)
    # body: flemished rope shell (stacked tori) tapering, hung from lanyard
    zt = cz - lanyard_len
    n = 8
    for i in range(n):
        s = i / (n - 1)
        rad = body_r * (0.75 + 0.45 * math.sin(s * math.pi * 0.92))
        torus(mb, (cx, cy, zt - i * r_rope * 1.9), rad, r_rope, seg=16, rseg=6,
              axis="Z", mat=mat_rope)
    dome(mb, (cx, cy, zt - n * r_rope * 1.9 + 0.01), body_r * 0.62, seg=10, rings=5,
         mat=mat_rope, squash=0.9)
    return mb


def painter_coil(center, R=0.13, r_rope=0.011, mat=7):
    """Coiled bow painter with standing end and eye."""
    mb = MB("Painter")
    rope_coil(mb, center, R, r_rope, coils=7, pitch=0.002, mat=mat, seg=24)
    cx, cy, cz = center
    mb.add_tube([(cx, cy, cz + 0.02), (cx + 0.30, cy + 0.02, cz + 0.02),
                 (cx + 0.34, cy + 0.02, cz + 0.06)], r_rope, segments=8, mat=mat)
    torus(mb, (cx + 0.34, cy + 0.02, cz + 0.06), 0.025, r_rope, seg=10, rseg=6,
          axis="Y", mat=mat)
    return mb


def stocked_anchor(center, scale=1.0, mat_iron=4, mat_wood=0):
    """Kedge anchor, Admiralty pattern: shank, arms with palms, wooden stock,
    ring + shackle.  Built upright, centre at the crown."""
    mb = MB("Anchor")
    cx, cy, cz = center
    s = scale
    shank_l = 0.85 * s
    cyl(mb, (cx, cy, cz), (cx, cy, cz + shank_l), 0.020 * s, seg=10, mat=mat_iron)
    # arms: two flukes swept up with palms
    for sgn in (-1, 1):
        pts = []
        for i in range(8):
            t = i / 7
            xx = cx + sgn * (0.42 * s) * (t ** 0.8)
            zz = cz + 0.06 * s + (0.30 * s) * (t ** 2.2)
            pts.append([xx, cy, zz])
        mb.add_tube(pts, 0.014 * s, segments=8, mat=mat_iron,
                    radii=[0.016 * s * (1 - 0.5 * i / 7) for i in range(8)])
        # palm (triangular fluke plate)
        tipx, _, tipz = pts[-1][0], cy, pts[-1][2]
        out = [(tipx, tipz), (tipx + sgn * 0.16 * s, tipz + 0.10 * s),
               (tipx + sgn * 0.03 * s, tipz + 0.16 * s)]
        mb.add_plate(out, 0.008 * s, plane="XZ", origin=(0, cy - 0.004 * s, 0),
                     mat=mat_iron, basis=(X, Z, -Y))
    # stock (wood, two cheeks) near the top
    z_st = cz + shank_l * 0.86
    mb.add_box((cx + 0.001, cy, z_st), (0.028 * s, 0.85 * s, 0.05 * s), mat=mat_wood,
               chamfer=0.004, rot=rot_x(0.0))
    # ring + shackle
    torus(mb, (cx, cy, cz + shank_l + 0.035 * s), 0.035 * s, 0.008 * s, seg=14,
          rseg=6, axis="Y", mat=mat_iron)
    cyl(mb, (cx, cy, cz + shank_l - 0.02 * s), (cx, cy, cz + shank_l + 0.02 * s),
        0.024 * s, seg=10, mat=mat_iron)
    return mb


def grapnel(center, s=1.0, mat_iron=5):
    """Small four-fluke grapnel (rowing boat kedge)."""
    mb = MB("Grapnel")
    cx, cy, cz = center
    shank = 0.5 * s
    cyl(mb, (cx, cy, cz), (cx, cy, cz + shank), 0.012 * s, seg=8, mat=mat_iron)
    for k in range(4):
        a = math.pi / 2 * k + math.pi / 4
        dx, dy = math.cos(a), math.sin(a)
        pts = []
        for i in range(7):
            t = i / 6
            r = 0.30 * s * (t ** 0.85)
            zz = cz + 0.05 * s + 0.24 * s * (t ** 2.3)
            pts.append([cx + dx * r, cy + dy * r, zz])
        mb.add_tube(pts, 0.010 * s, segments=7, mat=mat_iron)
        tip = pts[-1]
        dome(mb, tip, 0.014 * s, seg=8, rings=4, mat=mat_iron, squash=1.4, up=unit(np.array([dx, dy, 0.2])))
    torus(mb, (cx, cy, cz + shank + 0.02 * s), 0.022 * s, 0.006 * s, seg=12, rseg=6,
          axis="Y", mat=mat_iron)
    return mb


def boat_hook(center, length=2.6, r=0.014, mat_wood=0, mat_brass=3, along=X):
    """Boat hook: tapered ash pole, brass head with hook and point."""
    mb = MB("BoatHook")
    c = np.array(center)
    d = unit(along)
    p0 = c - d * length / 2
    p1 = c + d * length / 2
    mb.add_tube([p0, p1], r, segments=10, mat=mat_wood,
                radii=[r * (1 - 0.25 * i / 11) for i in range(12)] if False else None)
    # brass head: ball, spike, hook
    head = p1 - d * 0.06
    cyl(mb, head, p1 + d * 0.03, r * 1.15, seg=10, mat=mat_brass)
    sphere(mb, head - d * 0.01, r * 1.35, seg=10, rings=6, mat=mat_brass)
    cyl(mb, p1 + d * 0.03, p1 + d * 0.16, 0.006, seg=8, mat=mat_brass, r1=0.0015)
    dome(mb, p1 + d * 0.16, 0.003, seg=6, rings=4, mat=mat_brass, squash=2.0, up=d)
    hookpts = []
    for i in range(7):
        a = (i / 6) * math.pi * 0.8
        hookpts.append(p1 + d * (0.03 + 0.02 * math.cos(a)) + np.array([0, -0.06 * math.sin(a), 0]) * 0 + rot_axis(d, 1.57) @ np.array([0, -0.05 * math.sin(a), 0]))
    mb.add_tube(hookpts, 0.005, segments=7, mat=mat_brass)
    return mb


def breaker(center, r=0.13, l=0.42, mat=0, mat_iron=4):
    """Water breaker (barrico): staved cask with iron hoops, bung, becket."""
    mb = MB("Breaker")
    cx, cy, cz = center
    prof = []
    n = 9
    for i in range(n):
        t = i / (n - 1)
        rr = r * (0.82 + 0.30 * math.sin(t * math.pi))
        prof.append((rr, l * t))
    mb.add_lathe(prof, segments=16, axis="X", center=(cx - l / 2, cy, cz), mat=mat,
                 cap_lo=True, cap_hi=True)
    for fx in (0.12, 0.5, 0.88):
        xx = cx - l / 2 + l * fx
        t = fx
        rr = r * (0.82 + 0.30 * math.sin(t * math.pi))
        torus(mb, (xx, cy, cz), rr + 0.002, 0.006, seg=18, rseg=5, axis="X", mat=mat_iron)
    cyl(mb, (cx + l / 2 - 0.06, cy, cz + r * 0.5), (cx + l / 2 - 0.06, cy, cz + r * 0.5 + 0.015), 0.012, seg=8, mat=2)
    return mb


def bucket(center, r=0.11, h=0.20, mat=0, mat_iron=4):
    """Staved wooden bucket with iron hoops and rope becket."""
    mb = MB("Bucket")
    cx, cy, cz = center
    prof = [(r * (0.9 + 0.12 * i / 8), h * i / 8) for i in range(9)]
    prof = [(0, 0)] + prof[1:]
    prof.append((prof[-1][0] * 0.94, prof[-1][1]))
    prof.append((prof[1][0] * 0.94, prof[1][1]))
    prof.append((0, 0.012))
    mb.add_lathe(prof, segments=16, center=(cx, cy, cz), mat=mat)
    for fz in (0.30, 0.78):
        torus(mb, (cx, cy, cz + h * fz), r * (0.9 + 0.12 * fz) + 0.002, 0.005,
              seg=16, rseg=5, mat=mat_iron)
    # rope becket handle
    pts = []
    for i in range(9):
        a = math.pi * i / 8
        pts.append([cx, cy + r * 1.05 * math.cos(a), cz + h + r * 1.05 * math.sin(a)])
    mb.add_tube(pts, 0.008, segments=8, mat=7)
    return mb


def baler(center, mat=0):
    """Wooden baler: scoop with side handle."""
    mb = MB("Baler")
    cx, cy, cz = center
    r = 0.075
    prof = [(r * math.sin(math.pi / 2 * i / 6), -r * 0.55 * math.cos(math.pi / 2 * i / 6))
            for i in range(7)]
    mb.add_lathe(prof, segments=14, center=(cx, cy, cz))
    mb.add_tube([(cx, cy, cz + 0.02), (cx + 0.05, cy, cz + 0.19)], 0.013,
                segments=10, mat=mat)
    dome(mb, (cx + 0.05, cy, cz + 0.19), 0.016, seg=8, rings=4, mat=mat)
    return mb


# ---------------------------------------------------------------------------
# lamps & compass
# ---------------------------------------------------------------------------

def sidelight(center, side, mat_brass=3, mat_glass=9, mat_lens=None, scale=1.0):
    if isinstance(side, str):
        side = 1 if side.lower().startswith("stbd") or side.lower().startswith("star") else -1
    """
    Hooded brass sidelight: body, hood, fresnel lens (ribbed glass).
    side = +1 port (red) / -1 starboard (green).  Lens faces forward (+X).
    """
    mb = MB("Sidelight")
    cx, cy, cz = center
    s = scale
    # lamp body (brass drum, flat front ring)
    mb.add_lathe([(0.055 * s, -0.07 * s), (0.055 * s, 0.05 * s),
                  (0.045 * s, 0.055 * s)], segments=14, axis="X",
                 center=(cx - 0.09 * s, cy, cz), mat=mat_brass, cap_lo=True)
    # lens (ribbed glass): lathe disc with concentric ribs pointing forward
    lens_mat = mat_lens if mat_lens is not None else (12 if side > 0 else 13)
    prof = [(0.052 * s, -0.006 * s), (0.052 * s, 0.004 * s)]
    for k in range(4):
        prof.append((0.052 * s - (k + 1) * 0.010 * s, 0.004 * s))
        prof.append((0.052 * s - (k + 1) * 0.010 * s, 0.009 * s))
    prof.append((0.004 * s, 0.010 * s))
    mb.add_lathe(prof, segments=16, axis="X", center=(cx - 0.005 * s, cy, cz),
                 mat=lens_mat)
    # brass rim ring over the lens
    torus(mb, (cx - 0.002 * s, cy, cz), 0.053 * s, 0.005 * s, seg=16, rseg=5,
          axis="X", mat=mat_brass)
    # hood: half-cylinder visor above the lens
    prof = [(0.075 * s, 0), (0.075 * s, 0.05 * s)]
    hood = MB()
    n = 10
    grid = np.zeros((2, n, 3))
    for i, yoff in enumerate((0, 0.09 * s)):
        for j in range(n):
            a = math.pi * (j / (n - 1))
            grid[i, j] = [cx - 0.02 * s + 0, cy - 0.065 * s + (0.13 * s) * j / (n - 1),
                          cz + 0.03 * s + 0.035 * s * math.sin(math.pi * j / (n - 1)) + 0.02 * s]
    hood.add_grid(grid, mat_brass)
    mb.append(hood)
    # mounting bracket
    cyl(mb, (cx - 0.16 * s, cy, cz), (cx - 0.10 * s, cy, cz), 0.008 * s, seg=8,
        mat=mat_brass)
    mb.add_box((cx - 0.17 * s, cy, cz), (0.02 * s, 0.05 * s, 0.09 * s),
               mat=mat_brass, chamfer=0.003)
    return mb


def compass_binnacle(center, mat_brass=3, mat_glass=9, mat_card=11):
    """Boat compass: brass binnacle, domed glass, compass card with ticks."""
    mb = MB("Compass")
    cx, cy, cz = center
    # base + column + hood
    mb.add_lathe([(0.055, 0), (0.045, 0.02), (0.035, 0.03), (0.035, 0.11),
                  (0.050, 0.115), (0.052, 0.13), (0.045, 0.15), (0.02, 0.17),
                  (0.0, 0.175)], segments=16, center=center, mat=mat_brass)
    # glass dome
    sphere(mb, (cx, cy, cz + 0.145), 0.048, seg=16, rings=8, mat=mat_glass,
           scale=(1, 1, 0.55))
    # card inside
    mb.add_lathe([(0.0, 0.118), (0.040, 0.118), (0.040, 0.124), (0.0, 0.124)],
                 segments=16, center=center, mat=mat_card)
    for k in range(12):
        a = k * math.pi / 6
        mb.add_box((cx + 0.033 * math.cos(a), cy + 0.033 * math.sin(a), cz + 0.125),
                   (0.004, 0.010 if k % 3 else 0.016, 0.003), mat=12,
                   rot=rot_z(a + math.pi / 2))
    # lubber mark
    mb.add_box((cx + 0.050, cy, cz + 0.128), (0.012, 0.003, 0.004), mat=12)
    return mb


def lifebuoy(center, R=0.19, r=0.045, mat_canvas=8, mat_rope=7, side=None):
    """Cork lifebuoy with canvas cover, becket line and straps."""
    mb = MB("Lifebuoy")
    cx, cy, cz = center
    torus(mb, center, R, r, seg=20, rseg=9, axis="Y", mat=mat_canvas)
    for k in range(4):
        a = k * math.pi / 2 + math.pi / 4
        x = cx + R * math.cos(a)
        z = cz + R * math.sin(a)
        torus(mb, (x, cy, z), r + 0.004, 0.005, seg=10, rseg=5, axis="Y",
              mat=mat_rope)
    return mb


# ---------------------------------------------------------------------------
# appended: whaler/steam extras (THEMISTOCLES-II extension set)
# ---------------------------------------------------------------------------

def centreboard(center, lowered=True, mat=4, pivot_r=0.014):
    """Galvanised centreboard plate, shown lowered.  pivot at `center`."""
    mb = MB()
    cx, cy, cz = center
    # plate: rounded blade ~0.75 x 0.62, pivots at forward-top corner
    out = [(0.12, 0.02), (0.55, -0.06), (0.68, -0.18), (0.72, -0.55),
           (0.55, -0.62), (0.18, -0.55), (0.08, -0.30)]
    if not lowered:
        out = [(p[0], -p[1] * 0.12) for p in out]
    mb.add_plate(out, 0.012, plane="XZ", origin=(cx - 0.10, -0.006, cz), mat=mat)
    # pivot bolt with round head
    cyl(mb, (cx, -0.030, cz), (cx, 0.030, cz), pivot_r, seg=10, mat=3)
    for sgn in (-1, 1):
        dome(mb, (cx, sgn * 0.034, cz), 0.018, seg=8, rings=4, mat=3)
    return mb


def centreboard_case(hull, xi=0.48, length=1.55, mat=1):
    mb = MB()
    xs = hull.X(xi)
    z_fl = hull.keel_z(xi) + 0.12
    # case: oblong timber box with rounded ends stepped into the keelson
    mb.add_box((xs, 0, z_fl + 0.22), (length, 0.075, 0.44), mat=mat, chamfer=0.02)
    # brass pivot bolt heads + hoisting tackle at aft end
    cyl(mb, (xs - length / 2 + 0.12, -0.045, z_fl + 0.30),
        (xs - length / 2 + 0.12, 0.045, z_fl + 0.30), 0.017, seg=10, mat=3)
    for sgn in (-1, 1):
        dome(mb, (xs - length / 2 + 0.12, sgn * 0.049, z_fl + 0.30), 0.020, seg=8,
             rings=4, mat=3)
    torus(mb, (xs + length / 2 - 0.09, 0, z_fl + 0.46), 0.030, 0.009, seg=12, rseg=5,
          axis="Z", mat=4)
    return mb


def harpoon_sheathed(center, length=1.95, mat_wood=0, mat_iron=4, mat_sheath=8):
    """Harpoon lying along the boat: shaft w/ iron head (leather/canvas sheath)."""
    mb = MB()
    cx, cy, cz = center
    mb.add_tube([(cx - length / 2, cy, cz), (cx + length * 0.38, cy, cz)], 0.012,
                segments=8, mat=mat_wood, radii=[0.012 * (1 - 0.5 * i / 7) for i in range(8)])
    # socket + barb head w/ sheath
    cyl(mb, (cx + length * 0.38, cy, cz), (cx + length * 0.45, cy, cz), 0.010, seg=8,
        mat=mat_iron)
    mb.add_tube([(cx + length * 0.45, cy, cz), (cx + length * 0.52, cy, cz + 0.001)],
                0.016, segments=8, mat=mat_sheath,
                radii=[0.006, 0.022, 0.028, 0.026, 0.020, 0.014, 0.009, 0.0001])
    # toggle line eye
    torus(mb, (cx + length * 0.30, cy, cz), 0.014, 0.005, seg=8, rseg=4, axis="Y", mat=4)
    return mb


def line_tub(center, R=0.24, mat=0, mat_rope=7):
    """Whale-line tub: an open ash tub filled with coiled eye-spliced line."""
    mb = MB()
    cx, cy, cz = center
    mb.add_lathe([(0, 0), (R * 0.82, 0), (R * 0.80, 0.03), (R, 0.26), (R * 0.97, 0.30)],
                 segments=20, axis="Z", center=(cx, cy, cz), mat=mat, cap_lo=True)
    # iron hoops
    for f in (0.10, 0.75):
        torus(mb, (cx, cy, cz + 0.30 * f), R * (0.82 + 0.18 * f), 0.008, seg=18, rseg=4,
              axis="Z", mat=5)
    # coiled rope mound with upward eye
    coil = MB()
    for k in range(7):
        torus(coil, (cx, cy, cz + 0.26 + k * 0.012), R * (0.75 - 0.06 * k),
              0.032, seg=16, rseg=5, axis="Z", mat=mat_rope)
    cyl(coil, (cx, cy, cz + 0.35), (cx, cy, cz + 0.40), 0.020, seg=8, mat=mat_rope)
    mb.append(coil)
    return mb


def white_ensign(center, size=(0.56, 0.28), mat_flag=22, mat_red=12, mat_pole=4):
    """Furled White Ensign on a short ensign staff at the stern."""
    mb = MB("White_Ensign")
    cx, cy, cz = center
    # staff
    cyl(mb, (cx, cy, cz - 0.05), (cx, cy, cz + 0.42), 0.009, seg=8, mat=mat_pole)
    dome(mb, (cx, cy, cz + 0.44), 0.012, seg=8, rings=4, mat=3, squash=1.4)
    # furled flag: rolled bundle near the truck, with the red St George cross
    # roughly folded in: just a canvas roll + a hint of the bunting
    zf = cz + 0.36
    cyl(mb, (cx + 0.01, cy, zf - 0.11), (cx + 0.01 + size[0] * 0.5, cy, zf - 0.11),
        0.020, seg=8, mat=mat_flag)
    cyl(mb, (cx + 0.01, cy, zf - 0.11), (cx + 0.01 + size[0] * 0.12, cy, zf - 0.11),
        0.022, seg=8, mat=mat_red)
    # unfurled loose tail hanging down & streaming aft
    path = []
    import math as _m
    for i in range(10):
        s = i / 9
        path.append([cx + size[0] * 0.5 + s * 0.28 - 0.6 * s * s, cy,
                     zf - 0.11 - s * 0.06])
    mb.add_tube(path, 0.022, segments=6, mat=mat_flag,
                radii=[0.022 * (1 - 0.5 * i / 9) for i in range(10)])
    return mb

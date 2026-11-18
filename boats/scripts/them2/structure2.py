"""
structure2.py -- hull construction: planking, backbone, framing, joinery.

Every member is built against the Hull2 design surface, in metres.
Clinker offsets stack outward strake by strake (+thk per strake); the design
surface is the outer face of the sheer strake, so published beam is exact
where beam is measured.
"""

from __future__ import annotations
import math
import numpy as np
from .geom2 import (MB, unit, clamp, smoothstep, cyl, dome, torus,
                    rivet_row, rot_axis, superellipse_section)


# ---------------------------------------------------------------------------
# planking
# ---------------------------------------------------------------------------

def _strake_rows(hull, xi0, xi1, nx):
    if xi1 >= 1.0 and not hull.transom:
        xi1 = 1.0
    return np.linspace(xi0, xi1, nx)


def clinker_strakes(hull, n_strakes, thk, lap_frac=0.13, nx=61, npb=12,
                    taper_end=0.22, mat=0, mat_top=1, hood_start_ratio=0.020,
                    mat_inner=None):
    """
    n_strakes individual strake solids, lower (garboard) index 0 at the keel.
    Each strake covers the design girth between its land boundaries; the
    bottom edge drops below its own boundary by lap_frac of the visible width
    so it sits outboard of the strake below (the lap), and its outer face
    steps outward by thk per strake (clinker stack).
    hood_start_ratio: strakes begin where the half-breadth exceeds this*beam
    (the hood ends tuck into the stem rabbet, which the stem piece covers).
    """
    mb = MB("Planking_Clinker")
    inch = hood_start_ratio * hull.beam
    # find xi where the hull is wide enough to receive strakes
    xi0 = 0.0
    for xi in np.linspace(0, 0.08, 60):
        if hull.halfW(xi) * 2 >= inch:
            xi0 = xi
            break
    xis = _strake_rows(hull, xi0, 1.0, nx)
    # GEN-1 correction (THEMISTOCLES-III): strakes are CANTED, not stacked.
    # The old code stepped every strake a full thickness outward, so the
    # garboard of an 11-strake boat lay 160 mm inside the design surface:
    # the visible hull no longer matched the hydrostatic hull, and the frames
    # (built at one fixed offset) stood up to 160 mm clear of the topsides.
    # A real clinker strake is canted: its upper edge lies on the moulded
    # surface and its lower edge stands one thickness proud, lapping over the
    # strake below.  The outer face therefore runs from +thk (lower edge) to
    # 0 (upper edge); the inner face is one thickness inside that.
    if mat_inner is None:
        mat_inner = mat
    for j in range(n_strakes):
        f_lo = j / n_strakes - (lap_frac / n_strakes if j > 0 else 0.0)
        f_hi = (j + 1) / n_strakes
        outer = np.zeros((nx, npb, 3))
        inner = np.zeros((nx, npb, 3))
        for i, xi in enumerate(xis):
            # strake boundaries pinch toward the ends so hoods don't sliver
            pinch = 1.0
            pinch *= 1.0 - taper_end * smoothstep(0.10, 0.0, xi) * 0.25
            if not hull.transom:
                pinch *= 1.0 - taper_end * smoothstep(0.90, 1.0, xi) * 0.25
            lo = f_lo * pinch; hi = f_hi * pinch
            lo = clamp(lo, 0.0, 1.0); hi = clamp(hi, lo + 1e-3, 1.0)
            for q in range(npb):
                s_q = q / (npb - 1)                  # 0 = lower edge, 1 = upper
                f = lo + (hi - lo) * s_q
                t = hull.arc_to_t(xi, f)
                o = thk * (1.0 - s_q)
                outer[i, q] = hull.section_pt(xi, t, o)
                inner[i, q] = hull.section_pt(xi, t, o - thk + 0.0015)
        mjs = mat_top if j == n_strakes - 1 else mat
        base_o = mb.add_grid(outer, mjs)
        base_i = mb.add_grid(inner, mat_inner)
        # long edges
        for i in range(nx - 1):
            mb.add_face([base_o + i * npb, base_i + i * npb,
                         base_i + (i + 1) * npb, base_o + (i + 1) * npb], mat)
            # upper edge: seen only from INSIDE the boat (the strake above
            # laps over it outside), so it takes the interior material
            mb.add_face([base_o + (i + 1) * npb + npb - 1, base_i + (i + 1) * npb + npb - 1,
                         base_i + i * npb + npb - 1, base_o + i * npb + npb - 1], mat_inner)
        # end caps
        for q in range(npb - 1):
            mb.add_face([base_o + q, base_o + q + 1, base_i + q + 1, base_i + q], mat)
            b0 = base_o + (nx - 1) * npb + q
            b1 = base_i + (nx - 1) * npb + q
            mb.add_face([b0, b1, b1 + 1, b0 + 1], mat)
    return mb


def carvel_strakes(hull, n_strakes, thk, nx=61, npb=12, seam_frac=0.006,
                   mat=0, mat_top=1, hood_start_ratio=0.022):
    """Flush planking with caulking seams (recessed bevel between strakes)."""
    mb = MB("Planking_Carvel")
    inch = hood_start_ratio * hull.beam
    xi0 = 0.0
    for xi in np.linspace(0, 0.08, 60):
        if hull.halfW(xi) * 2 >= inch:
            xi0 = xi
            break
    xis = _strake_rows(hull, xi0, 1.0, nx)
    half_seam = seam_frac / 2.0
    for j in range(n_strakes):
        f_lo = j / n_strakes + (half_seam if j > 0 else 0.0)
        f_hi = (j + 1) / n_strakes - half_seam
        outer = np.zeros((nx, npb, 3))
        inner = np.zeros((nx, npb, 3))
        for i, xi in enumerate(xis):
            for q in range(npb):
                f = f_lo + (f_hi - f_lo) * q / (npb - 1)
                t = hull.arc_to_t(xi, f)
                outer[i, q] = hull.section_pt(xi, t, 0.0)
                inner[i, q] = hull.section_pt(xi, t, -thk)
        mjs = mat_top if j == n_strakes - 1 else mat
        base_o = mb.add_grid(outer, mjs)
        base_i = mb.add_grid(inner, mjs)
        for i in range(nx - 1):
            mb.add_face([base_o + i * npb, base_i + i * npb,
                         base_i + (i + 1) * npb, base_o + (i + 1) * npb], mat)
            mb.add_face([base_o + (i + 1) * npb + npb - 1, base_i + (i + 1) * npb + npb - 1,
                         base_i + i * npb + npb - 1, base_o + i * npb + npb - 1], mat)
        for q in range(npb - 1):
            mb.add_face([base_o + q, base_o + q + 1, base_i + q + 1, base_i + q], mat)
            b0 = base_o + (nx - 1) * npb + q
            b1 = base_i + (nx - 1) * npb + q
            mb.add_face([b0, b1, b1 + 1, b0 + 1], mat)
    return mb


def double_skin(hull, n_diag=26, spacing=0.085, nx=64, nt=26,
                mat_outer=0, mat_inner=21, thk_out=0.016, thk_in=0.010):
    """
    Double-diagonal shell for the steam cutter: outer smooth carvel skin
    (varnished mahogany look) plus ONE crossed-diagonal inner layer visible in
    the bilge.  (Second diagonal layer omitted: it would be hidden.)
    """
    out = MB("Outer_Carvel")
    # outer smooth skin: full-surface loft with tight seams
    xs = np.linspace(0, 1, nx)
    w = int(round(spacing / hull.loa * nx * nt * 0.10)) or 1
    rows = []
    for i, xi in enumerate(xs):
        pts = []
        for j in range(nt):
            t = j / (nt - 1)
            pts.append(hull.section_pt(xi, t, 0.0))
        rows.append(pts)
    grid = np.array(rows)
    b0 = out.add_grid(grid, mat_outer, close_v=False)
    # thickness: inner face (offset -thk_out)
    grid_i = np.zeros_like(grid)
    for i, xi in enumerate(xs):
        for j in range(nt):
            t = j / (nt - 1)
            grid_i[i, j] = hull.section_pt(xi, t, -thk_out)
    b1 = out.add_grid(grid_i, mat_inner, flip=True)
    # GEN-1 correction: close the shell into a solid.  The two faces used to
    # be loose sheets (624 boundary edges after mirroring), so the skin had
    # no edge at the sheer, the stem, the transom or the keel line.
    nxx, ntt = grid.shape[0], grid.shape[1]
    def _o(i, j): return b0 + i * ntt + j
    def _i(i, j): return b1 + i * ntt + j
    for i in range(nxx - 1):                    # keel line (j=0) and sheer (j=nt-1)
        out.add_face([_o(i, 0), _o(i + 1, 0), _i(i + 1, 0), _i(i, 0)], mat_outer)
        jt = ntt - 1
        out.add_face([_o(i + 1, jt), _o(i, jt), _i(i, jt), _i(i + 1, jt)], mat_outer)
    for j in range(ntt - 1):                    # stem (i=0) and transom (i=nx-1)
        out.add_face([_o(0, j + 1), _o(0, j), _i(0, j), _i(0, j + 1)], mat_outer)
        ie = nxx - 1
        out.add_face([_o(ie, j), _o(ie, j + 1), _i(ie, j + 1), _i(ie, j)], mat_outer)
    out2 = diagonal_skin(hull, 0.016, thk_in, slope=0.55, nplanks=n_diag,
                         width=0.085, xi_range=(0.10, 0.90), mat=mat_inner)
    skin = MB("Planking_DoubleDiagonal")
    skin.append(out)
    skin.append(out2)
    return skin


def diagonal_skin(hull, thk_out, thk, slope=0.55, nplanks=26, width=0.055,
                  xi_range=(0.07, 0.93), mat=0, name="Inner_Diagonal_Skin"):
    """
    Second skin of diagonal planks inside the outer planking, laid at +/-slope
    (two layers crossing), visible in the engine-room bilge and cutaways.
    Built against the inside face of the outer planking (offset -thk_out).
    """
    mb = MB(name)
    base_off = -thk_out
    for layer, sgn, doff in ((0, +1, -0.001), (1, -1, -thk - 0.001)):
        for k in range(nplanks):
            f_start = 0.06 + (0.86 - 0.06) * k / (nplanks - 1)
            f_start -= 0.5 * sgn * slope * (xi_range[1] - xi_range[0])
            pts_xi = np.linspace(xi_range[0], xi_range[1], 34)
            strips_o = np.zeros((34, 2, 3))
            strips_i = np.zeros((34, 2, 3))
            for i, xi in enumerate(pts_xi):
                f = f_start + sgn * slope * (xi - xi_range[0])
                f = clamp(f, 0.03, 0.93)
                fA = clamp(f - width / 2, 0.02, 0.94)
                fB = clamp(f + width / 2, 0.03, 0.95)
                for q, ff in enumerate((fA, fB)):
                    t = hull.arc_to_t(xi, ff)
                    strips_o[i, q] = hull.section_pt(xi, t, base_off + doff)
                    strips_i[i, q] = hull.section_pt(xi, t, base_off + doff - thk)
            bo = mb.add_grid(strips_o, mat)
            bi = mb.add_grid(strips_i, mat)
            for i in range(33):
                mb.add_face([bo + i * 2, bi + i * 2, bi + (i + 1) * 2, bo + (i + 1) * 2], mat)
                mb.add_face([bo + (i + 1) * 2 + 1, bi + (i + 1) * 2 + 1, bi + i * 2 + 1, bo + i * 2 + 1], mat)
            for q in range(1):
                mb.add_face([bo + q, bo + q + 1, bi + q + 1, bi + q], mat)
                b0 = bo + 33 * 2 + q; b1 = bi + 33 * 2 + q
                mb.add_face([b0, b1, b1 + 1, b0 + 1], mat)
    return mb


def _profile_frames(paths, fwd=True):
    """Sweep frames for a member running UP a stem/stern profile in the XZ
    plane: u lies in that plane normal to the path, pointing outboard of the
    end (forward at the stem, aft at a double-ender's stern); v is +-Y so that
    u x v follows the path (consistent face winding)."""
    P = np.asarray(paths, float)
    out = []
    for i in range(len(P)):
        d = unit(P[min(i + 1, len(P) - 1)] - P[max(i - 1, 0)])
        u = unit(np.cross(np.array([0.0, 1.0, 0.0]), d))   # Y x up = +X
        if not fwd:
            u = -u
        v = unit(np.cross(d, u))
        out.append((u, v))
    return out


# ---------------------------------------------------------------------------
# backbone: keel, stem, sternpost, transom
# ---------------------------------------------------------------------------

def keel_assembly(hull, sided=0.046, depth=0.10, hog_h=0.05, hog_w=0.10,
                  mat=0, taper_end=0.45):
    """Keel (hog-backed, sided tapering into stems) + inner hog/keelson bed."""
    mb = MB("Keel_Stem_Sternpost")
    n = 40
    xis = np.linspace(0, 1, n)
    # keel: lofted rectangular section under the keel line
    paths = []; shapes = []
    for xi in xis:
        x = hull.X(xi)
        zt = hull.keel_z(xi)
        w = sided / 2 * (1.0 - taper_end * (smoothstep(0.85, 1.0, xi)
                                           if hull.transom else smoothstep(0.72, 1.0, xi) + smoothstep(0.72, 0.0, xi) * 0 +
                                           smoothstep(0.06, 0.0, xi)))
        # rake of the ends: lift the keel bottom at the very ends
        lift = (smoothstep(0.965, 1.0, xi) * (0.35 * depth if hull.transom else 0.8 * depth)
                + smoothstep(0.035, 0.0, xi) * 0.55 * depth)
        paths.append([x, 0, zt - depth + lift])
        shapes.append(np.array([(-w, 0), (w, 0), (w, depth + 0.004 - lift),
                                (-w, depth + 0.004 - lift)]))
    # GEN-1 correction: the implicit transported sweep frame of a -X path
    # points its second axis DOWN, so the keel used to hang a full keel depth
    # below the hull with an open gap above it.  State the frame explicitly.
    KF = [(np.array([0.0, -1.0, 0.0]), np.array([0.0, 0.0, 1.0]))] * len(paths)
    mb.add_sweep(paths, shapes, frames=KF, mat=mat)
    # hog (inner keel above the keel inside the boat)
    paths = []; shapes = []
    for xi in xis:
        x = hull.X(xi)
        z = hull.keel_z(xi) + 0.004
        w = hog_w / 2 * (1.0 - 0.7 * (smoothstep(0.08, 0.0, xi) + smoothstep(0.92, 1.0, xi)))
        h = hog_h * (1.0 - 0.8 * (smoothstep(0.06, 0.0, xi) + smoothstep(0.94, 1.0, xi)))
        paths.append([x, 0, z])
        shapes.append(np.array([(-w, 0), (w, 0), (w, h), (-w, h)]))
    mb.add_sweep(paths, shapes, frames=KF, mat=mat)
    return mb


def stem_post(hull, moulded=0.10, sided=0.050, mat=0, name=None):
    """
    Curved stem piece swept along the hull's forward edge profile, with an
    apron backing it inside.  Covers all the plank hood ends.
    """
    mb = MB(name or "Stem_Post")
    n = 26
    ts = np.linspace(0.0, 1.0, n)
    paths = []; shapes = []
    for t in ts:
        p = hull.section_pt(0.0, t, 0.001)
        # stem stands proud of the plank ends a touch (cutwater)
        x = p[0] + 0.010
        m = moulded * (1.0 - 0.35 * t)
        w = sided / 2
        paths.append([x, 0, p[2]])
        shapes.append(np.array([(-m * 0.55, -w), (m * 0.45, -w), (m * 0.45, w),
                                (-m * 0.55, w)]))
    # GEN-1 correction: explicit frame (u = forward, normal to the stem line;
    # v = athwartships).  The implicit frame put the MOULDED dimension
    # athwartships, giving a stem twice as wide as it is deep.
    mb.add_sweep(paths, shapes, frames=_profile_frames(paths, fwd=True), mat=mat)
    # apron (backing the stem, inside the hull)
    paths = []; shapes = []
    for t in ts[2:-2]:
        p = hull.section_pt(0.02 + 0.02 * 0, t, -0.02)
        p = hull.section_pt(0.0, t, 0.001)
        m = moulded * (1.0 - 0.3 * t)
        w = (sided * 0.8) / 2
        paths.append([p[0] - moulded * 0.45, 0, p[2]])
        shapes.append(np.array([(-m * 0.5, -w), (m * 0.5, -w), (m * 0.5, w),
                                (-m * 0.5, w)]))
    mb.add_sweep(paths, shapes, frames=_profile_frames(paths, fwd=True), mat=mat)
    mb.mirror_y() if False else None
    return mb


def stern_post(hull, moulded=0.14, sided=0.055, mat=0):
    """Sternpost + deadwood for the double-ended whaler."""
    mb = MB("Stern_Post")
    n = 22
    ts = np.linspace(0.0, 1.0, n)
    paths = []; shapes = []
    for t in ts:
        p = hull.section_pt(1.0, t, 0.0)
        m = moulded * (1.0 - 0.5 * t)
        w = sided / 2
        paths.append([p[0] - 0.005, 0, p[2]])
        shapes.append(np.array([(-m * 0.45, -w), (m * 0.55, -w), (m * 0.55, w),
                                (-m * 0.45, w)]))
    mb.add_sweep(paths, shapes)
    return mb


def transom_plate(hull, thk=0.05, mat=0, mat_edge=1, framing=True):
    """
    Raked transom: plank plate closing the hull at xi=1, lying IN the raked
    transom plane, plus its inside framing (top rail, side and centre
    uprights).

    GEN-1 correction: the plate used to be built vertical at the x of the
    sheer, i.e. at the aftmost point of a RAKED stern, so it stood clear of
    the plank ends lower down; and its framing was placed aft of it, outside
    the boat.  Every vertex is now sheared onto the raked plane and the
    framing sits on the inboard face.
    """
    mb = MB("Transom")
    n = 25
    ts = np.linspace(0, 1, n)
    edge_s = [hull.section_pt(1.0, t, 0.002) for t in ts]
    edge_p = [hull.section_pt(1.0, t, 0.002) for t in ts[::-1]]
    outline = [(-p[1], p[2]) for p in edge_p] + [(p[1], p[2]) for p in edge_s]
    pts = np.array(outline)
    zmin = hull.keel_z(1.0) + 0.012
    keep = pts[pts[:, 1] >= zmin - 0.02]
    outline2 = [(y, z) for (y, z) in keep]
    z0 = hull.keel_z(1.0); z1 = hull.sheer_z(1.0)

    def x_end(z):
        t = clamp((z - z0) / max(1e-6, (z1 - z0)), 0.0, 1.0)
        return hull.section_pt(1.0, t, 0.0)[0]
    # plate spans x in [0, thk] (+X = inboard); bedded 12 mm into the plank ends
    mb.add_plate(outline2, thk, plane="YZ", origin=(-0.012, 0, 0), mat=mat)
    plate_nv = len(mb.verts)
    if framing:
        z_top = max(p[2] for p in edge_s)
        zr = z_top - 0.07
        y_top = abs(hull.section_pt(1.0, (zr - z0) / (z1 - z0), -0.03)[1])
        mb.add_box((thk - 0.012 + 0.030, 0, zr), (0.060, 2 * y_top * 0.96, 0.09),
                   mat=mat_edge, chamfer=0.008)
        for yy in (-0.40, 0.0, 0.40):
            yv = yy * 2 * y_top
            zb = zmin + 0.05 if yy == 0.0 else zmin + 0.25
            if yy != 0.0:
                # GEN-1: the side uprights' heels stood outside the V of the
                # transom (a dark block on each quarter).  Start each upright
                # where the transom is wide enough to hold it.
                tq = 0.0
                while tq < 0.95 and abs(hull.section_pt(1.0, tq, -0.03)[1]) < abs(yv) + 0.050:
                    tq += 0.01
                zb = max(zb, z0 + (z1 - z0) * tq + 0.01)
            mb.add_box((thk - 0.012 + 0.028, yv, (zr + zb) / 2),
                       (0.056, 0.070, (zr - zb)), mat=mat_edge, chamfer=0.006)
    # Shear onto the raked plane and bevel the inboard perimeter to the
    # actual hull at that face.  Using the after-face outline unchanged
    # across 52 mm of thickness left two corners outside the garboards.
    shaped = []
    for i, (x, y, z) in enumerate(mb.verts):
        xx = x + x_end(z)
        if i < plate_nv and x > 0:
            xi = clamp((hull.loa / 2 - xx) / hull.loa, 0.0, 1.0)
            lo, hi = 0.0, 1.0
            for _ in range(24):
                tm = (lo + hi) * 0.5
                if hull.section_pt(xi, tm, -0.018)[2] < z:
                    lo = tm
                else:
                    hi = tm
            lim = max(0.0, hull.section_pt(xi, (lo + hi) * 0.5, -0.018)[1])
            y = float(clamp(y, -lim, lim))
        shaped.append((xx, y, z))
    mb.verts = shaped
    return mb


# ---------------------------------------------------------------------------
# frames / timbers, floors
# ---------------------------------------------------------------------------

def frames(hull, n_planks, thk, spacing=0.16, siding=0.022, mould_lo=0.040,
           mould_hi=0.022, mat=0, t_lo=0.045, t_hi=0.985, floors_every=3,
           floor_extra=0.05, limber=True, stealer_ok=True, inside_off=None):
    """
    Bent timbers, one each side of the centreline per station, following the
    inside face of the planking -- including the clinker steps.  Every
    `floors_every`-th frame grows a floor (deeper moulding across the keel
    with a limber notch).
    """
    mb = MB("Frames")
    L = hull.loa
    n_fr = int(L / spacing)
    if inside_off is None:
        # GEN-1 correction: timbers land on the inner face of the (canted)
        # planking, one thickness in.  The old value, -(n-1)*thk - thk, put the
        # steam cutter's frames 0.43 m inside her shell.
        inside_off = -thk - 0.0015
    k = 0
    xi_list = np.linspace(0.055, 0.945 if hull.transom else 0.90, n_fr)
    for xi in xi_list:
        is_floor = (k % floors_every == 0)
        k += 1
        m_t = lambda t: (mould_lo + (mould_hi - mould_lo) * t
                         + (floor_extra * (1 - min(1.0, t / 0.25)) if is_floor else 0.0))
        n_pts = 30
        # GEN-1: in the narrow forefoot / heel the timber's heel ran out
        # through the garboards beside the stem; start each timber where the
        # inside of the planking is clear of the hog (|y| >= 0.06 m).
        t0 = t_lo
        while t0 < 0.5 and abs(hull.section_pt(xi, t0, inside_off)[1]) < 0.06:
            t0 += 0.01
        ts = np.linspace(t0, t_hi, n_pts)
        # path: on inside face of planking (with the clinker steps averaged out)
        pts = []
        depth = hull.depth(xi)
        dxi = 0.004
        for t in ts:
            p = hull.section_pt(xi, t, inside_off)
            # GEN-1: bevel allowance.  Toward the fine ends the planking runs
            # obliquely across the frame, so a timber laid on the surface at
            # its centre plane stood out through the planking at its fore or
            # after face.  Step it in by (siding/2) x the surface's normal
            # run-off per metre of length.
            nrm = unit(np.asarray(hull.section_normal(xi, t), float))
            pa = hull.section_pt(max(0.0, xi - dxi), t, inside_off)
            pb = hull.section_pt(min(1.0, xi + dxi), t, inside_off)
            dx = abs(pb[0] - pa[0])
            if dx > 1e-9:
                run = abs(float(np.dot(np.asarray(pb) - np.asarray(pa), nrm))) / dx
                p = np.asarray(p, float) - nrm * (siding / 2 * run + 0.001)
            pts.append(p)
        # rectangle cross-section: siding along X, moulding along inward normal
        shapes = []
        frames_ = []
        hws = hull.halfW(xi)
        for i, t in enumerate(ts):
            n_in = -hull.section_normal(xi, t)
            n_in[0] = 0
            n_in = unit(n_in)
            s2 = siding / 2
            mould = m_t(t)
            # limber notch: grind the lowest section flat near the keel
            # GEN-1 correction: siding is fore-and-aft (first shape axis),
            # moulding grows inward from the planking (second shape axis).
            # The old frame swapped them, so half of every timber stood out
            # through the planking.
            u3 = np.array([-1.0, 0.0, 0.0])
            v3 = n_in
            frames_.append((u3, v3))
            m = mould
            shapes.append(np.array([(-s2, 0), (s2, 0), (s2, m), (-s2, m)]))
        mb.add_sweep(pts, shapes, frames=frames_, mat=mat)
    return mb


def keelson(hull, depth=0.14, sided=0.075, mat=0, xi_range=(0.12, 0.88),
            cap_w=0.0):
    """Keelson: the inner keel, sided over the floors along the centreline."""
    mb = MB("Keelson")
    n = 30
    xis = np.linspace(xi_range[0], xi_range[1], n)
    paths = []; shapes = []
    z_top = None
    for xi in xis:
        x = hull.X(xi)
        z = hull.keel_z(xi) + 0.055
        d = depth * (1.0 - 0.55 * (smoothstep(xi_range[0] + 0.13, xi_range[0], xi) +
                                   smoothstep(xi_range[1] - 0.13, xi_range[1], xi)))
        # Bevel the heel into the fine V at each end.  A full-width
        # rectangular heel at keel+35 mm put its lower corners through the
        # garboards; keep the designed crown/height and taper only the foot.
        zbase = z - 0.02
        lo, hi = 0.0, 1.0
        for _ in range(24):
            tm = (lo + hi) * 0.5
            if hull.section_pt(xi, tm, -0.018)[2] < zbase:
                lo = tm
            else:
                hi = tm
        yin = hull.section_pt(xi, (lo + hi) * 0.5, -0.018)[1]
        foot = min(sided / 2, max(0.004, yin - 0.002))
        paths.append([x, 0, zbase])
        shapes.append(np.array([(-foot, 0), (foot, 0), (sided / 2, d),
                                (-sided / 2, d)]))
    # GEN-1 correction (shared root cause with the keel): with the implicit
    # frame the inner keelson was swept DOWNWARD through the bottom of the
    # boat.  Athwartships = -Y, depth = +Z (u x v = -X = path direction).
    KF = [(np.array([0.0, -1.0, 0.0]), np.array([0.0, 0.0, 1.0]))] * len(paths)
    mb.add_sweep(paths, shapes, frames=KF, mat=mat)
    if cap_w:
        # moulded cap on the keelson crown: the bottom boards butt to it
        cpaths = [[p[0], 0, p[2] + sh[2][1]] for p, sh in zip(paths, shapes)]
        cshape = [np.array([(-cap_w / 2, 0), (cap_w / 2, 0), (cap_w / 2 - 0.006, 0.016),
                            (-cap_w / 2 + 0.006, 0.016)])] * len(cpaths)
        mb.add_sweep(cpaths, cshape, frames=KF, mat=mat)
    return mb


# ---------------------------------------------------------------------------
# gunwale, inwale, cap rail, rubbing strake, stem band
# ---------------------------------------------------------------------------

def _sweep_along_surface(hull, f_arc, offset, n, shape_fn, xi0=0.02, xi1=0.98,
                         mat=0, flat_top=None):
    """Sweep a cross-section shape along the hull at a fixed arc fraction."""
    xis = np.linspace(xi0, xi1, n)
    pts = []
    frames_ = []
    shapes = []
    for xi in xis:
        t = hull.arc_to_t(xi, f_arc)
        p = hull.section_pt(xi, t, offset)
        outward = hull.section_normal(xi, t)
        up = np.array([0.0, 0.0, 1.0])
        frames_.append((outward, up))
        shp, ref = shape_fn(xi)
        shapes.append(shp + ref)
        pts.append(p)
    mb = MB("sweep")
    mb.add_sweep(pts, shapes, frames=frames_)
    return mb, pts


def gunwale_set(hull, n_planks, thk, cap_w=0.075, cap_h=0.028, rub_arc=0.78,
                rub_r=0.020, mat_cap=0, mat_inwale=1, mat_rub=2, o_top=None,
                rub_off=0.0):
    """
    Cap rail (moulded: rounded top), inwale (thick clamp inside) and a
    half-round rubbing strake outside.  Returns one MB (mirrored after).
    """
    if o_top is None:
        o_top = 0.0  # sheer strake outer face is the design surface
    mb = MB("Gunwale")
    # ---- cap rail: follows the sheer edge on top of planking+inwale
    n = 56
    # Run the rails into the stem rabbet.  Starting them at xi=0.03 left both
    # cap-rail ends visibly suspended well abaft of the stem once planking was
    # omitted for the construction view.  A short, tapered scarf keeps the
    # realistic full rail section clear of the centreline at the very fine end.
    xi_fwd = 0.002
    xis = np.linspace(xi_fwd, 0.97 if hull.transom else 0.94, n)
    pts = []; frames_ = []; shapes = []
    for xi in xis:
        t = hull.arc_to_t(xi, 0.995)
        p = hull.section_pt(xi, t, o_top + 0.002)
        nrm = hull.section_normal(xi, t)
        taper = clamp(xi / 0.035, 0.12, 1.0)
        # rail sits on the top edge: raise to sheer top + half height
        seg = superellipse_section(cap_w * taper / 2, cap_h * taper / 2, n=3.2, seg=12)
        shapes.append(seg)
        # local frame: u = outward normal (horizontal-ish), v = up
        u = unit(nrm - np.array([0, 0, nrm[2]]))
        if np.linalg.norm(u) < 1e-6:
            u = np.array([0, 1.0, 0])
        v = np.array([0.0, 0, 1.0])
        frames_.append((u, v))
        pts.append([p[0], p[1], p[2] + cap_h * 0.5 - 0.002])
    mb.add_sweep(pts, shapes, frames=frames_, mat=mat_cap)
    # ---- inwale
    xi_in = hull.arc_to_t(xis[0], 1.0)
    def shape_inwale(xi):
        return superellipse_section(0.020, 0.046 / 2, n=2.6, seg=10), np.array([0, 0])
    pts2 = []
    frames2 = []
    shapes2 = []
    for xi in xis:
        t = hull.arc_to_t(xi, 0.985)
        inn_off = -thk - 0.002
        p = hull.section_pt(xi, t, inn_off)
        nrm = hull.section_normal(xi, t)
        u = unit(nrm - np.array([0, 0, nrm[2]]))
        v = np.array([0.0, 0.0, 1.0])
        taper = clamp(xi / 0.035, 0.12, 1.0)
        pts2.append([p[0], p[1], p[2] - 0.012])
        shapes2.append(superellipse_section(0.022 * taper, 0.024 * taper, n=2.4, seg=10))
        frames2.append((-u, v))
    mb.add_sweep(pts2, shapes2, frames=frames2, mat=mat_inwale)
    # ---- rubbing strake (half-round beading outside)
    pts3 = []; frames3 = []; shapes3 = []
    for xi in xis:
        t = hull.arc_to_t(xi, rub_arc)
        # GEN-1 correction: on the outer face of the shell (the old stacked
        # offset buried the steam cutter's rubbing strake 80 mm inside it).
        p = hull.section_pt(xi, t, rub_off)
        nrm = unit(hull.section_normal(xi, t))
        u = unit(nrm - np.array([0, 0, nrm[2]]))
        v = np.array([0.0, 0.0, 1.0])
        taper = clamp(xi / 0.035, 0.12, 1.0)
        rr = rub_r * taper
        shapes3.append(np.array([(-rr, -rr * 0.4), (rr, -rr * 0.4),
                                 (rr, rr * 0.7), (0, rr), (-rr, rr * 0.7)]))
        frames3.append((u, v))
        pts3.append(p + nrm * 0.002 + np.array([0, 0, 0.004]))
    mb.add_sweep(pts3, shapes3, frames=frames3, mat=mat_rub)
    return mb


def stem_band(hull, r=0.011, mat=0):
    """Half-round bronze stem band on the cutwater."""
    mb = MB("Stem_Band")
    ts = np.linspace(0.02, 1.0, 22)
    path = []
    for t in ts:
        p = hull.section_pt(0.0, t, 0.02)
        path.append([p[0] + 0.018, 0, p[2]])
    mb.add_tube(path, r, segments=8, mat=mat)
    return mb


# ---------------------------------------------------------------------------
# internal support: risers, stringers, breasthooks, knees
# ---------------------------------------------------------------------------

def riser(hull, f_arc, h=0.05, thk=0.016, xi0=0.10, xi1=0.90, mat=0, n=44,
          inside_extra=0.002):
    """Thwart riser: a strip fastened inside the frames to carry thwarts."""
    mb = MB("Riser")
    xis = np.linspace(xi0, xi1, n)
    pts = []; frames_ = []; shapes = []
    inside_off = -0.048 - 0.011 - inside_extra
    for xi in xis:
        t = hull.arc_to_t(xi, f_arc)
        p = hull.section_pt(xi, t, inside_off)
        nrm = unit(hull.section_normal(xi, t))
        u = -nrm
        v = np.array([0.0, 0.0, 1.0])
        frames_.append((u, v))
        shapes.append(np.array([(-thk / 2, -h / 2), (thk / 2, -h / 2),
                                (thk / 2, h / 2), (-thk / 2, h / 2)]))
        pts.append(p + nrm * 0.004)
    mb.add_sweep(pts, shapes, frames=frames_)
    return mb


def side_bench(hull, f_z, width=0.34, thk=0.024, xi0=0.0, xi1=0.30, mat=0, n=30):
    """Side bench along the bows/stern sheets: horizontal board inboard of the
    planking, following the hull curve, supported from the frames."""
    mb = MB("SideBench")
    xis = np.linspace(xi0, xi1, n)
    grid = np.zeros((n, 2, 3))
    base_i = None
    for i, xi in enumerate(xis):
        t = hull.arc_to_t(xi, f_z)
        p = hull.section_pt(xi, t, -0.055)
        grid[i, 0] = [p[0], p[1], p[2]]
        z_top = hull.section_pt(xi, t, 0)[2]
        grid[i, 1] = [p[0], max(0.02, p[1] - width), z_top]
    # flatten to horizontal at the mean sheer-relative height
    z0 = np.mean([hull.section_pt(xi, hull.arc_to_t(xi, f_z), 0)[2] for xi in xis])
    for i in range(n):
        grid[i, 0][2] = z0
        grid[i, 1][2] = z0
    bo = mb.add_grid(grid, mat)
    grid_d = grid.copy()
    grid_d[:, :, 2] -= thk
    bi = mb.add_grid(grid_d, mat)
    for i in range(n - 1):
        mb.add_face([bo + i * 2, bi + i * 2, bi + (i + 1) * 2, bo + (i + 1) * 2], mat)
        mb.add_face([bo + (i + 1) * 2 + 1, bi + (i + 1) * 2 + 1, bi + i * 2 + 1, bo + i * 2 + 1], mat)
    mb.add_face([bo, bi, bi + 1, bo + 1], mat)
    b0 = bo + (n - 1) * 2; b1 = bi + (n - 1) * 2
    mb.add_face([b0, b1, b1 + 1, b0 + 1], mat)
    return mb, grid


def breasthook(hull, f_arc=0.96, length=0.55, thk=0.035, mat=0, ahead=False,
               xi_end=0.0):
    """V-shaped horizontal knee behind the stem (or at the stern for whaler)."""
    mb = MB("Breasthook")
    # The forward breasthook is a real closing knee: its apex must land in the
    # stem rabbet, not at an arbitrary first-plank station.  The former 0.012
    # station left a conspicuous, unsupported 90 mm fore-and-aft gap between
    # the knee/sheets and the stem when the shell was omitted for a construction
    # inspection.  Hull2 supplies a valid raked centreline profile at xi=0.
    xi0 = xi_end if xi_end > 0 else 0.0
    sgn = -1 if ahead else 1
    t = hull.arc_to_t(xi0, f_arc)
    z = hull.section_pt(xi0, t, 0)[2]
    if xi_end > 0.9:
        xi_base = xi_end
        xip = xi_end - length / hull.loa
    else:
        xi_base = 0.0
        xip = length / hull.loa
    pA = hull.section_pt(xi_base, hull.arc_to_t(xi_base, f_arc), -0.05)
    pB = hull.section_pt(xip, hull.arc_to_t(xip, f_arc), -0.06)
    outline = [(0.0, -pA[2]), ]
    # work in horizontal plane: outline = plan view (x,y) relative
    apex = (pA[0], 0.0)
    b1 = (pB[0], pB[1])
    b2 = (pB[0], -pB[1])
    outline = [apex, b1, (pB[0] - (0.03 if xip > xi_base else -0.03) * -sgn, 0.0), b2]
    mb.add_plate(outline, thk, plane="XY", origin=(0, 0, pA[2]), mat=mat)
    return mb


def knee_L(arm_a=0.30, arm_b=0.30, thk_arm=0.05, width=0.04, origin=(0, 0, 0),
           basis=None, mat=0, curve_n=6):
    """
    Grown knee: two tapered arms meeting in a smooth throat.  Built in its own
    vertical plane (basis: u=along arm a, v=up arm b).
    arms taper toward their tips; rounded crook inside.
    """
    mb = MB("Knee")
    a = arm_a; b = arm_b
    w_a = thk_arm
    pts2 = []
    # outer profile: from tip of arm a around the crook to tip of arm b
    for i in range(curve_n + 1):
        ang = (math.pi / 2) * i / curve_n
        r = 0.10 + 0.9 * (i / curve_n)
        pts2.append((a * math.cos(ang) * 1.0, -b * 0 + 0))  # placeholder replaced below
    # explicit L grown shape in (u horizontal, v vertical):
    out = [
        (a, 0.0), (a, w_a), (0.45 * a, w_a),
        (0.30 * a, 1.6 * w_a), (0.16 * a, 2.6 * w_a),
        (w_a * 1.2, 3.2 * w_a),
        (w_a * 0.9, b), (0.0, b),
    ]
    # scale upright to arm_b
    out = [(u, v * (b / max(1e-6, out[-1][1])) if out[-1][1] > 0 else v) for (u, v) in out]
    mb.add_plate(out, width, plane="XZ", origin=origin, mat=mat, basis=basis)
    return mb


# ---------------------------------------------------------------------------
# decks & coamings (steam cutter)
# ---------------------------------------------------------------------------

def deck_panel(hull, xi0, xi1, f_bot, z_off=0.0, thk=0.022, mat=0,
               margin=0.045, planks=True, plank_w=0.10):
    """
    Fore/after deck: horizontal planked panel bounded inboard by the hull
    plan at deck height.  `margin` sets the covering-board width at the edge.
    Planks run fore-and-aft with seams.
    """
    mb = MB("Deck")
    n = 26
    xis = np.linspace(xi0, xi1, n)
    edge = []
    for xi in xis:
        t = hull.arc_to_t(xi, f_bot)
        p = hull.section_pt(xi, t, -0.06)
        edge.append([p[0], p[1] - margin, p[2]])
    zd = np.mean([e[2] for e in edge]) + z_off
    xs = [e[0] for e in edge]
    ys = [e[1] for e in edge]
    E = np.array([[x, y, zd] for x, y in zip(xs, ys)])
    if not planks:
        # single slab following edge (cheap)
        outline = [(e[0], e[1]) for e in E] + [(E[-1][0], 0.0), (E[0][0], 0.0)][::1]
        mb.add_plate([(x - E[0][0], y) for (x, y) in outline], thk, plane="XY",
                     origin=(E[0][0], 0, zd - thk), mat=mat)
        return mb, zd
    # planked: fill between edge curve and centreline king plank with
    # fore-aft planks; find half breadth per station, generate strip quads
    n_pl = max(2, int(max(ys) / plank_w))
    for k in range(n_pl):
        y_in = (k * max(ys) / n_pl)
        y_out = ((k + 1) * max(ys) / n_pl)
        strip = np.zeros((n, 2, 3))
        for i in range(n):
            yi_in = min(y_in, ys[i] * 0.98)
            yi_out = min(y_out, ys[i] * 0.98)
            strip[i, 0] = [xs[i], yi_in, zd]
            strip[i, 1] = [xs[i], yi_out, zd]
        base = mb.add_grid(strip, mat)
        stripd = strip.copy(); stripd[:, :, 2] -= thk
        bid = mb.add_grid(stripd, mat)
        for i in range(n - 1):
            mb.add_face([base + i * 2, bid + i * 2, bid + (i + 1) * 2, base + (i + 1) * 2], mat)
            mb.add_face([base + (i + 1) * 2 + 1, bid + (i + 1) * 2 + 1, bid + i * 2 + 1, base + i * 2 + 1], mat)
        mb.add_face([base, bid, bid + 1, base + 1], mat)
        b0 = base + (n - 1) * 2; b1 = bid + (n - 1) * 2
        mb.add_face([b0, b1, b1 + 1, b0 + 1], mat)
    mb.mirror_y()
    return mb, zd


def coaming_ring(hull, xs, ys, height, thk=0.015, mat=0, top_round=True):
    """
    Engine-room coaming: vertical plate ring following a rounded-rectangle
    plan (xs = [x0, x1], ys = [y0, y1] half plan) standing on the hull.
    """
    mb = MB("Coamings")
    x0, x1 = xs
    y0, y1 = ys
    r = min(0.30, (x1 - x0) / 3, (y1 - y0) / 3)
    # perimeter CCW (as seen from above), inward face +- thk/2
    per = []
    seg_arc = 8
    corners = [(x1 - r, y1 - r, 0), (x0 + r, y1 - r, 1), (x0 + r, y0 + r, 2), (x1 - r, y0 + r, 3)]
    # build rounded rectangle plan CCW
    plan = []
    for (cx, cy, ci) in corners:
        for k in range(seg_arc + 1):
            a = (math.pi / 2) * (ci + k / seg_arc)
            plan.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    # z base follows hull: sample sheer-relative height at deck level by lookup per x

    def base_z(x, y):
        xi = (hull.loa / 2 - x) / hull.loa
        xi = clamp(xi, 0.0, 1.0)
        # find t where half-breadth ~ y
        ts = np.linspace(0.3, 1.0, 40)
        best = min(ts, key=lambda t: abs(hull.section_pt(xi, t, 0)[1] - y))
        return hull.section_pt(xi, best, -0.02)[2] - 0.01

    n = len(plan)
    grid = np.zeros((n, 2, 3))
    for i, (x, y) in enumerate(plan):
        zb = base_z(x, y)
        grid[i, 0] = [x, y, zb]
        grid[i, 1] = [x, y, zb + height]
    base = mb.add_grid(grid, mat, close_u=True)
    grid_in = grid.copy()
    grid_in[:, :, 1] *= (1 - thk / max(y1 - y0, 1e-6))
    grid_in[:, :, 1] -= np.sign(grid_in[:, :, 1]) * thk
    bin_ = mb.add_grid(grid_in[:, ::-1, :], mat, close_u=True)
    # top edge
    for i in range(n):
        i2 = (i + 1) % n
        mb.add_face([base + i * 2 + 1, bin_ + i * 2 + 1, bin_ + i2 * 2 + 1, base + i2 * 2 + 1], mat)
    return mb


def aft_stem(hull, moulded=0.105, sided=0.050, mat=0):
    """Raked second stem at the double ender's stern (sweep over xi=1 edge)."""
    mb = MB("Aft_Stem")
    n = 24
    for t in np.linspace(0.02, 0.99, n):
        p = hull.section_pt(1.0, t, 0.001)
        m = moulded * (1.0 - 0.35 * t)
        w = sided / 2
        mb.add_sweep_v([[p[0] - 0.006, 0, p[2]]], [[(-m * 0.52, -w), (m * 0.48, -w),
                                                    (m * 0.48, w), (-m * 0.52, w)]]) \
            if False else None
    paths = [[hull.section_pt(1.0, t, 0.001)[0] - 0.006, 0,
              hull.section_pt(1.0, t, 0.001)[2]] for t in np.linspace(0.02, 0.99, n)]
    shapes = [np.array([(-moulded * (1 - 0.35 * t) * 0.52, -sided / 2),
                        (moulded * (1 - 0.35 * t) * 0.48, -sided / 2),
                        (moulded * (1 - 0.35 * t) * 0.48, sided / 2),
                        (-moulded * (1 - 0.35 * t) * 0.52, sided / 2)])
              for t in np.linspace(0.02, 0.99, n)]
    mb.add_sweep(paths, shapes, frames=_profile_frames(paths, fwd=False), mat=mat)
    # apron on the inside face
    paths2 = [[p[0] - moulded * 0.45, 0, p[2]]
              for p in [hull.section_pt(1.0, t, -0.02) for t in np.linspace(0.06, 0.95, n)]]
    shapes2 = [np.array([(-moulded * 0.4, -sided * 0.4), (moulded * 0.4, -sided * 0.4),
                         (moulded * 0.4, sided * 0.4), (-moulded * 0.4, sided * 0.4)])
               for _ in range(n)]
    mb.add_sweep(paths2, shapes2, frames=_profile_frames(paths2, fwd=False), mat=mat)
    return mb

"""
hull.py -- parametric ship's-boat hull definition and structural builders.

The hull is a lofted parametric surface driven by a small number of faired
design curves, in the same way a draughtsman works: a half-breadth curve, a
sheer line, a keel/rocker line, and a set of sectional fullness controls.
Nothing is sculpted by hand, so the form stays fair and every plank, frame
and fitting is placed by rule rather than by eye.

    surface(xi, t) -> point
        xi = 0 at the stem head (bow), 1 at the transom (stern)
        t  = 0 at the keel line, 1 at the top of the sheer strake

Both the clinker (lapstrake) and carvel (double-skin) hulls use this surface,
which guarantees that planking, frames and deck furniture all agree with one
another and with the published principal dimensions.
"""

from __future__ import annotations

import math

import numpy as np

from .geom import (
    MeshBuilder,
    Pchip,
    bolt_row,
    clamp,
    curve,
    cyl,
    lerp,
    smoothstep,
    unit,
)

# --------------------------------------------------------------------------
# steel/brass/etc material slots -- fixed order used by every boat script
# --------------------------------------------------------------------------
MAT = {
    "wood_out": 0,      # varnished exterior planking
    "wood_in": 1,       # painted or varnished interior planking
    "wood_timber": 2,   # frames, keel, deadwood, thwarts
    "wood_deck": 3,     # decks, gratings, floorboards
    "paint_hull": 4,    # painted topside
    "paint_white": 5,
    "brass": 6,
    "iron": 7,
    "steel": 8,
    "rope": 9,
    "canvas": 10,
    "glass": 11,
    "copper": 12,
    "leather": 13,
    "coal": 14,
    "water": 15,
    "red_lead": 16,
}
MAT_NAMES = list(MAT.keys())


class HullDesign:
    """A faired hull form described by design curves in metres."""

    def __init__(
        self,
        name,
        loa,
        bmax,
        sheer_pts,          # (xi, z) of the top of the sheer strake
        keel_pts,           # (xi, z) of the underside of the keel
        hb_pts,             # (xi, fraction of bmax) half-breadth at the keel->sheer mid
        full_aft=1.9,       # section fullness exponent 'a' amidships
        full_fwd=1.15,
        round_aft=2.35,     # section exponent 'b'
        round_fwd=1.55,
        flare_fwd=0.10,     # outward flare of the topsides at the bow
        flare_aft=0.03,
        tumble_aft=0.0,
        stem_rake=0.10,     # forefoot set aft of the stem head (m)
        stern_rake=0.15,    # bottom of transom set fwd of its head (m)
        transom_frac=0.42,  # transom half-breadth as a fraction of bmax
        bow_frac=0.045,     # half-width of the stem head at xi=0
        waterline_z=0.0,
    ):
        self.name = name
        self.loa = loa
        self.bmax = bmax
        self.x_bow = loa * 0.5
        self.x_stern = -loa * 0.5
        self.sheer = curve(sheer_pts)
        self.keel = curve(keel_pts)
        self.hb = curve(hb_pts)
        self.full_aft = full_aft
        self.full_fwd = full_fwd
        self.round_aft = round_aft
        self.round_fwd = round_fwd
        self.flare_fwd = flare_fwd
        self.flare_aft = flare_aft
        self.tumble_aft = tumble_aft
        self.stem_rake = stem_rake
        self.stern_rake = stern_rake
        self.transom_frac = transom_frac
        self.bow_frac = bow_frac
        self.waterline_z = waterline_z

        # numerical normalisation so that max half-breadth == bmax exactly
        self._nt = 161
        self._tsamples = np.linspace(0.0, 1.0, self._nt)
        self._scales = np.array([self._scale_at(x) for x in np.linspace(0, 1, 241)])

    def translate_z(self, dz):
        """Shift the whole form vertically (used to land the solved floating
        waterline exactly on Z = 0)."""
        self.sheer = Pchip(self.sheer.x, self.sheer.y + dz)
        self.keel = Pchip(self.keel.x, self.keel.y + dz)
        return self

    # ---- design curves ---------------------------------------------------
    def x_of(self, xi):
        return self.x_bow - xi * self.loa

    def xi_of(self, x):
        return (self.x_bow - x) / self.loa

    def sheer_z(self, xi):
        return float(self.sheer(xi))

    def keel_z(self, xi):
        return float(self.keel(xi))

    def half_beam(self, xi):
        """Target maximum half-breadth at this station (m)."""
        f = float(self.hb(xi))
        if xi < 0.12:  # blend into the stem head
            f = lerp(self.bow_frac / self.bmax, f, smoothstep(0.0, 0.12, xi))
        if xi > 0.93:  # blend into the transom
            f = lerp(f, self.transom_frac, smoothstep(0.93, 1.0, xi))
        return f * self.bmax

    def _shape_terms(self, xi, t):
        a = lerp(self.full_fwd, self.full_aft, smoothstep(0.0, 0.55, xi))
        b = lerp(self.round_fwd, self.round_aft, smoothstep(0.0, 0.55, xi))
        # superellipse quadrant: 0 at the keel, 1 at the sheer
        y = (1.0 - (1.0 - np.clip(t, 0, 1)) ** a) ** (1.0 / b)
        flare = lerp(self.flare_fwd, self.flare_aft, smoothstep(0.0, 0.5, xi))
        y = y * (1.0 + flare * smoothstep(0.62, 1.0, t))
        tumble = self.tumble_aft * smoothstep(0.75, 1.0, xi) * smoothstep(0.55, 1.0, t)
        y = y * (1.0 - tumble)
        return y

    def _scale_at(self, xi):
        vals = self._shape_terms(xi, self._tsamples)
        return float(np.max(vals)) if np.max(vals) > 1e-9 else 1.0

    # ---- the surface -----------------------------------------------------
    def x_shift(self, xi, t):
        """Stem and sternpost rake: lower points set aft (bow) / fwd (stern)."""
        xi = np.asarray(xi, dtype=float)
        t = np.asarray(t, dtype=float)
        w_bow = smoothstep(0.16, 0.0, xi)
        w_st = smoothstep(0.86, 1.0, xi)
        return -w_bow * self.stem_rake * (1.0 - t) ** 0.7 + w_st * self.stern_rake * ((1.0 - t) ** 1.4)

    def surface(self, xi, t):
        xi = np.clip(xi, 0.0, 1.0)
        t = np.clip(t, 0.0, 1.0)
        z = lerp(self.keel_z(xi), self.sheer_z(xi), t)
        x = self.x_of(xi) + self.x_shift(xi, t)
        xs = np.clip(xi / 1.0, 0, 1)
        scale = np.interp(xs, np.linspace(0, 1, 241), self._scales)
        y = self.half_beam(xi) * self._shape_terms(xi, t) / max(scale, 1e-9)
        return np.array([x, y, z])

    def grid(self, xis, ts):
        """Vectorised surface evaluation -> array (n_xi, n_t, 3)."""
        xi = np.asarray(xis, dtype=float)[:, None]
        t = np.asarray(ts, dtype=float)[None, :]
        xi_b = np.broadcast_to(xi, (len(np.atleast_1d(xis)), len(np.atleast_1d(ts))))
        t_b = np.broadcast_to(t, xi_b.shape)
        z = lerp(self.keel(xi_b), self.sheer(xi_b), t_b)
        x = self.x_bow - xi_b * self.loa + self.x_shift(xi_b, t_b)
        f = self.hb(xi_b)
        f = np.where(xi_b < 0.12,
                     lerp(self.bow_frac / self.bmax, f, smoothstep(0.0, 0.12, xi_b)), f)
        f = np.where(xi_b > 0.93, lerp(f, self.transom_frac, smoothstep(0.93, 1.0, xi_b)), f)
        hb = f * self.bmax
        a = lerp(self.full_fwd, self.full_aft, smoothstep(0.0, 0.55, xi_b))
        b = lerp(self.round_fwd, self.round_aft, smoothstep(0.0, 0.55, xi_b))
        y = (1.0 - (1.0 - np.clip(t_b, 0, 1)) ** a) ** (1.0 / b)
        flare = lerp(self.flare_fwd, self.flare_aft, smoothstep(0.0, 0.5, xi_b))
        y = y * (1.0 + flare * smoothstep(0.62, 1.0, t_b))
        tumble = self.tumble_aft * smoothstep(0.75, 1.0, xi_b) * smoothstep(0.55, 1.0, t_b)
        y = y * (1.0 - tumble)
        scale = np.interp(xi_b, np.linspace(0, 1, 241), self._scales)
        return np.stack([x, hb * y / np.maximum(scale, 1e-9), z], axis=-1)

    def normal(self, xi, t, eps=1e-4):
        p = self.surface(xi, t)
        du = self.surface(min(1.0, xi + eps), t) - self.surface(max(0.0, xi - eps), t)
        dv = self.surface(xi, min(1.0, t + eps)) - self.surface(xi, max(0.0, t - eps))
        n = np.cross(du, dv)
        if np.linalg.norm(n) < 1e-12:
            return np.array([0.0, 1.0, 0.0])
        n = unit(n)
        if n[1] < 0:  # always point outboard on the +Y side
            n = -n
        return n

    def half_section(self, xi, t_samples):
        return np.array([self.surface(xi, t) for t in t_samples])

    # ---- derived: inner surface offsets ---------------------------------
    def inner(self, xi, t, depth):
        return self.surface(xi, t) - self.normal(xi, t) * depth

    def keel_path(self, n=60, xi0=0.020, xi1=0.965, t=0.004):
        return np.array([self.surface(lerp(xi0, xi1, i / (n - 1)), t) for i in range(n)])

    def sheer_path(self, n=80, xi0=0.0, xi1=1.0, t=0.999):
        return np.array([self.surface(lerp(xi0, xi1, i / (n - 1)), t) for i in range(n)])

    def section_length(self, xi, t0=0.0, t1=1.0, n=25):
        pts = [self.surface(xi, lerp(t0, t1, i / (n - 1))) for i in range(n)]
        return float(sum(np.linalg.norm(pts[i + 1] - pts[i]) for i in range(n - 1)))

    def stability_check(self):
        """Sanity: surface must be single-valued, non-self-intersecting,
        monotone in x.  Returns a dict of simple diagnostics."""
        xs = []
        for xi in np.linspace(0, 1, 60):
            for t in (0.02, 0.5, 0.98):
                xs.append(self.surface(xi, t)[0])
        return {"x_min": min(xs), "x_max": max(xs), "loa_actual": max(xs) - min(xs)}


# --------------------------------------------------------------------------
# planking
# --------------------------------------------------------------------------


def _plank_solid(mb, hull, xi_list, t_lo, t_hi, thickness, lap, mat_out, mat_in, n_t=3,
                 inward_only=False, outer_proud=0.0):
    """Build one strake / plank as a closed solid on the hull surface.

    t_lo, t_hi may be scalars or arrays (diagonal planking uses arrays).
    `lap` is how far the lower edge projects outboard past the plank below.
    """
    ts = np.linspace(0.0, 1.0, n_t)
    nxi = len(xi_list)
    grid_out = np.zeros((nxi, n_t, 3))
    grid_in = np.zeros((nxi, n_t, 3))
    for i, xi in enumerate(xi_list):
        lo = t_lo[i] if np.ndim(t_lo) else t_lo
        hi = t_hi[i] if np.ndim(t_hi) else t_hi
        for j, s in enumerate(ts):
            t = lerp(lo, hi, s)
            p = hull.surface(xi, t)
            n = hull.normal(xi, t)
            # outer face: proud at the lower edge (the 'land'), flush at the top
            proud = outer_proud + lap * (1.0 - s) ** 0.8
            grid_out[i, j] = p + n * proud
            grid_in[i, j] = p - n * thickness
    # outer skin
    mb.add_grid(grid_out, mat_out)
    # inner skin (visually the inside of the boat)
    mb.add_grid(grid_in[:, ::-1], mat_in)
    # edges: top and bottom strakes plus the two ends
    for j, flip in ((0, True), (n_t - 1, False)):
        quad_fwd = np.array([[grid_in[i, j], grid_out[i, j]] for i in range(nxi)])
        # build a strip along the length
        strip = np.stack(
            [
                np.array([grid_in[i, j] for i in range(nxi)]),
                np.array([grid_out[i, j] for i in range(nxi)]),
            ],
            axis=1,
        )
        mb.add_grid(strip, mat_out, flip=flip)
    for i, flip in ((0, True), (nxi - 1, False)):
        ring = [grid_out[i, j] for j in range(n_t)] + [grid_in[i, j] for j in range(n_t - 1, -1, -1)]
        # close the plank end with a fan (simple quad strip)
        for j in range(n_t - 1):
            if flip:
                mb.add_quad(grid_in[i, j], grid_out[i, j], grid_out[i, j + 1], grid_in[i, j + 1], mat_out)
            else:
                mb.add_quad(grid_out[i, j], grid_in[i, j], grid_in[i, j + 1], grid_out[i, j + 1], mat_out)
        del ring


def build_clinker_planking(
    mb,
    hull,
    n_strakes=11,
    thickness=0.016,
    lap=0.0045,
    xi0=0.012,
    xi1=0.985,
    n_xi=64,
    butt_length=2.6,
    t_bottom=0.0,
    t_top=1.0,
    mat_out=MAT["wood_out"],
    mat_in=MAT["wood_in"],
):
    """Lapstrake planking: individually modelled, overlapping, butted planks.

    Each strake is divided at butt joints (staggered from its neighbour, as a
    boatbuilder would), and each strake is trimmed where its width closes down
    at the stem, producing proper hood ends.
    """
    xi_all = np.linspace(xi0, xi1, n_xi)
    out = []
    for k in range(n_strakes):
        f0 = lerp(t_bottom, t_top, k / n_strakes)
        f1 = lerp(t_bottom, t_top, (k + 1) / n_strakes)
        # trim the strake to where it still has useful width
        keep = []
        for xi in xi_all:
            if hull.section_length(xi, f0, f1, n=7) > 0.014:
                keep.append(xi)
        if len(keep) < 4:
            continue
        keep = np.array(keep)
        # each strake laps ~28 mm over the one below (the 'land')
        overlap = 0.028
        if k > 0:
            dens = np.array([hull.section_length(xi, f0, f1, n=7) for xi in keep])
            d_t = np.clip(overlap / np.maximum(dens, 1e-3) * (f1 - f0), 0.0, (f1 - f0) * 0.9)
            f0_arr = f0 - d_t
        else:
            f0_arr = np.full_like(keep, f0)
        f1_arr = np.full_like(keep, f1)
        # butt joints, staggered per strake
        L = (keep[-1] - keep[0]) * hull.loa
        n_butts = max(1, int(round(L / butt_length)))
        cuts = [keep[0]]
        for b in range(1, n_butts):
            base = keep[0] + (keep[-1] - keep[0]) * b / n_butts
            offset = 0.55 * (keep[-1] - keep[0]) / n_butts * (1 if k % 2 else -1) * 0.5
            cuts.append(float(np.clip(base + offset, keep[0] + 0.02, keep[-1] - 0.02)))
        cuts.append(keep[-1])
        cuts = sorted(set(cuts))
        mo = mat_out[k] if isinstance(mat_out, (list, tuple)) else mat_out
        mi = mat_in[k] if isinstance(mat_in, (list, tuple)) else mat_in
        for c0, c1 in zip(cuts[:-1], cuts[1:]):
            seg = np.linspace(c0 + 0.0004, c1 - 0.0004, max(8, int((c1 - c0) * n_xi) + 4))
            seg = seg[(seg >= keep[0]) & (seg <= keep[-1])]
            if len(seg) < 3:
                continue
            lo = np.interp(seg, keep, f0_arr)
            hi = np.interp(seg, keep, f1_arr)
            _plank_solid(mb, hull, seg, lo, hi, thickness, lap, mo, mi, n_t=4)
        out.append((f0, f1))
    return out


def build_carvel_planking(
    mb,
    hull,
    n_strakes=12,
    thickness=0.018,
    xi0=0.012,
    xi1=0.985,
    n_xi=70,
    mat_out=MAT["wood_out"],
    mat_in=MAT["wood_in"],
    seam=0.0018,
    outer_proud=0.0,
):
    """Carvel (flush) planking in fore-and-aft strakes, seams showing."""
    xi_all = np.linspace(xi0, xi1, n_xi)
    for k in range(n_strakes):
        f0 = k / n_strakes + seam
        f1 = (k + 1) / n_strakes - seam
        keep = [xi for xi in xi_all if hull.section_length(xi, f0, f1, n=7) > 0.022]
        if len(keep) < 4:
            continue
        mo = mat_out[k] if isinstance(mat_out, (list, tuple)) else mat_out
        mi = mat_in[k] if isinstance(mat_in, (list, tuple)) else mat_in
        _plank_solid(mb, hull, np.array(keep), f0, f1, thickness, 0.0, mo, mi, n_t=3,
                     outer_proud=outer_proud)


def build_diagonal_skin(
    mb,
    hull,
    n_strips=14,
    width=0.055,
    slope=1.7,
    direction=1,
    inset=0.020,
    thickness=0.012,
    xi0=0.02,
    xi1=0.98,
    mat=MAT["wood_timber"],
    n_xi=70,
    clip_range=(0.02, 0.98),
):
    """Inner diagonal (double-diagonal) skin -- evidenced on the Admiralty
    steam cutters (e.g. Steam Cutter 438, 1897: 'double skin teak, inner
    diagonal').  Strips run diagonally across the inner face; they remain
    visible inside the boat and in the cutaway renders."""
    xi = np.linspace(xi0, xi1, n_xi)
    for k in range(n_strips):
        c = clip_range[0] + (clip_range[1] - clip_range[0]) * k / n_strips
        t_lo = c + direction * slope * (xi - xi0) / (xi1 - xi0) * 0.55
        t_hi = t_lo + width
        m = (t_lo > 0.015) & (t_hi < 0.985)
        if m.sum() < 5:
            continue
        tl = t_lo[m]
        th = t_hi[m]
        xs = xi[m]
        grid_o = np.zeros((len(xs), 3, 3))
        grid_i = np.zeros((len(xs), 3, 3))
        for i, x in enumerate(xs):
            for j, s in enumerate(np.linspace(0, 1, 3)):
                t = lerp(tl[i], th[i], s)
                p = hull.surface(x, t) - hull.normal(x, t) * inset
                n = hull.normal(x, t)
                grid_o[i, j] = p
                grid_i[i, j] = p - n * thickness
        mb.add_grid(grid_i[:, ::-1], mat)   # inner face (seen from inside)
        mb.add_grid(grid_o, mat)
        for j, flip in ((0, True), (2, False)):
            strip = np.stack(
                [[grid_o[i, j] for i in range(len(xs))], [grid_i[i, j] for i in range(len(xs))]],
                axis=1,
            )
            mb.add_grid(strip, mat, flip=flip)


# --------------------------------------------------------------------------
# framing
# --------------------------------------------------------------------------


def build_frames(
    mb,
    hull,
    spacing=0.135,
    depth=0.032,
    width=0.022,
    xi0=0.035,
    xi1=0.965,
    t0=0.02,
    t1=0.985,
    mat=MAT["wood_timber"],
    n_t=14,
    taper=(0.75, 1.0),
    floor_timber=False,
    plank_thickness=0.016,
):
    """Steamed-oak transverse timbers against the inside of the planking."""
    span = (xi1 - xi0) * hull.loa
    n = max(2, int(span / spacing))
    for i in range(n + 1):
        xi = lerp(xi0, xi1, i / n)
        ts = np.linspace(t0, t1, n_t)
        path, normals, widths, depths = [], [], [], []
        for t in ts:
            p = hull.inner(xi, t, plank_thickness)
            nrm = hull.normal(xi, t)
            path.append(p)
            normals.append(nrm)
            w = lerp(taper[0], taper[1], smoothstep(t0, t1, t)) * width
            d = depth * lerp(0.85, 1.0, smoothstep(t0, t1, t))
            widths.append(w)
            depths.append(d)
        path = np.array(path)
        # solid loft: two rails offset in +/-X and +/-normal
        grid = np.zeros((n_t, 4, 3))
        for j in range(n_t):
            p = path[j]
            nrm = normals[j]
            w = widths[j] * 0.5
            d = depths[j]
            grid[j, 0] = p + np.array([w, 0, 0])
            grid[j, 1] = p + np.array([w, 0, 0]) - nrm * d
            grid[j, 2] = p + np.array([-w, 0, 0]) - nrm * d
            grid[j, 3] = p + np.array([-w, 0, 0])
        mb.add_grid(grid, mat, close_v=True)
        # end caps
        mb.add_face([len(mb.verts) - 4 + k for k in range(4)][::-1], mat)
        base = len(mb.verts) - 4 * n_t
        mb.add_face([base + k for k in range(4)], mat)
        if floor_timber and i % 2 == 0:
            # floor timber crossing the keel
            pass


def build_keel(hull, mb, width=0.10, depth=0.075, xi0=0.015, xi1=0.965, mat=MAT["wood_timber"]):
    """Keel plank / keel, following the keel line, plus the forefoot."""
    path = []
    n = 70
    for i in range(n):
        xi = lerp(xi0, xi1, i / (n - 1))
        p = hull.surface(xi, 0.004)
        path.append(p)
    path = np.array(path)
    grid = np.zeros((n, 6, 3))
    for i, p in enumerate(path):
        nrm = unit(np.array([0.0, 0.0, -1.0]))  # down
        w = width * 0.5
        # bevel: narrower at the bottom face (garboard rabbet)
        grid[i, 0] = p + np.array([0, -w * 0.62, -depth])
        grid[i, 1] = p + np.array([0, w * 0.62, -depth])
        grid[i, 2] = p + np.array([0, w, 0.0])
        grid[i, 3] = p + np.array([0, w, 0.045])
        grid[i, 4] = p + np.array([0, -w, 0.045])
        grid[i, 5] = p + np.array([0, -w, 0.0])
    base = mb.add_grid(grid, mat, close_v=True)
    mb.add_face([base + i for i in range(6)][::-1], mat)
    end = base + 6 * (n - 1)
    mb.add_face([end + i for i in range(6)], mat)
    return path


def _rounded_section(cx_aft, cx_fwd, half_aft, half_fwd, z=0.0):
    """8-point section for a stem/sternpost: flat aft face, rounded sides,
    flat forward face -- a real timber section, not a knife edge."""
    return np.array([
        [cx_aft, -half_aft, z],
        [cx_fwd + (cx_aft - cx_fwd) * 0.25, -half_fwd * 1.02, z],
        [cx_fwd, -half_fwd * 0.62, z],
        [cx_fwd, half_fwd * 0.62, z],
        [cx_fwd + (cx_aft - cx_fwd) * 0.25, half_fwd * 1.02, z],
        [cx_aft, half_aft, z],
    ])


def build_stem(hull, mb, width=0.115, depth=0.115, mat=MAT["wood_timber"], n=40, head_rise=0.055):
    """Stem: solid timber from the forefoot to the stem head, into which the
    hood ends of the planking land."""
    pts = np.array([hull.surface(0.0, lerp(-0.03, 1.0, i / (n - 1))) for i in range(n)])
    grid = np.zeros((n, 6, 3))
    for i, p in enumerate(pts):
        f = i / (n - 1)
        taper = lerp(1.0, 0.80, smoothstep(0.70, 1.0, f))
        w = width * 0.5 * taper
        wf = width * 0.33 * taper
        d = depth * lerp(1.0, 0.85, f)
        sec = _rounded_section(p[0], p[0] - d, w, wf)
        rise = head_rise * smoothstep(0.93, 1.0, f)
        for j in range(6):
            grid[i, j] = np.array([sec[j, 0], sec[j, 1], p[2] + rise])
    base = mb.add_grid(grid, mat, close_v=True)
    mb.add_face([base + i for i in range(6)][::-1], mat)
    end = base + 6 * (n - 1)
    mb.add_face([end + i for i in range(6)], mat)


def build_sternpost(hull, mb, width=0.080, depth=0.095, mat=MAT["wood_timber"], n=30,
                    t0=-0.02, t1=0.99, aft_face=True):
    """Sternpost from the keel to under the transom."""
    pts = np.array([hull.surface(1.0, lerp(t0, t1, i / (n - 1))) for i in range(n)])
    grid = np.zeros((n, 6, 3))
    for i, p in enumerate(pts):
        w = width * 0.5
        wf = width * 0.30
        d = depth * 0.9
        sec = _rounded_section(p[0], p[0] + d, w, wf)
        for j in range(6):
            grid[i, j] = np.array([sec[j, 0], sec[j, 1], p[2]])
    base = mb.add_grid(grid, mat, close_v=True)
    mb.add_face([base + i for i in range(6)][::-1], mat)
    end = base + 6 * (n - 1)
    mb.add_face([end + i for i in range(6)], mat)


def build_transom(hull, mb, mat_out=MAT["wood_out"], mat_in=MAT["wood_in"], t_lo=0.0, t_top=0.998,
                  camber=0.006, thick=0.030, n_y=15, n_t=20, rim=0.045):
    """Raked transom: the flat stern panel the aftermost planking lands on."""
    ts = np.linspace(t_lo, t_top, n_t)
    ys = np.linspace(-1.0, 1.0, n_y)
    grid_o = np.zeros((n_t, n_y, 3))
    for i, t in enumerate(ts):
        p = hull.surface(1.0, t)
        half = p[1]
        for j, fy in enumerate(ys):
            cam = camber * (1.0 - fy ** 2) * (1.0 - 0.4 * abs(2 * t - 1))
            grid_o[i, j] = np.array([p[0] - cam, fy * half, p[2]])
    mb.add_grid(grid_o, mat_out)
    grid_i = grid_o.copy()
    grid_i[:, :, 0] += thick
    mb.add_grid(grid_i[:, ::-1], mat_in)
    # edge capping so the panel reads as a solid board
    for j, flip in ((0, True), (n_y - 1, False)):
        strip = np.stack([[grid_o[i, j] for i in range(n_t)],
                          [grid_i[i, j] for i in range(n_t)]], axis=1)
        mb.add_grid(strip, mat_out, flip=flip)
    for i, flip in ((0, True), (n_t - 1, False)):
        strip = np.stack([[grid_o[i, j] for j in range(n_y)],
                          [grid_i[i, j] for j in range(n_y)]], axis=1)
        mb.add_grid(strip, mat_out, flip=flip)
    # transom rim: a rubbing band round the edge that hides the plank lands
    if rim > 0:
        for j, flip in ((0, True), (n_y - 1, False)):
            pts_o, pts_i = [], []
            for i in range(n_t):
                p = hull.surface(1.0, ts[i])
                y = ys[j] * p[1]
                pts_o.append(np.array([p[0] - camber * 0.5 - 0.004, y * 1.005, p[2]]))
                pts_i.append(np.array([p[0] - rim, y * 0.985, p[2]]))
            a = np.array(pts_o)
            b = np.array(pts_i)
            strip = np.stack([a, b], axis=1)
            mb.add_grid(strip, mat_out, flip=flip)


def build_gunwale(
    hull,
    mb,
    out_width=0.038,
    in_width=0.085,
    height=0.030,
    mat=MAT["wood_timber"],
    xi0=0.004,
    xi1=0.988,
    n=90,
    rise_inboard=0.008,
):
    """Gunwale with a moulded cap rail.

    A plain vertical bar is what a box looks like; a real gunwale is a capping
    piece with a rounded crown, a little wider than the rail beneath it, and a
    drip groove on the outboard side where the water runs off.  The crown is
    built into the cross-section, so it catches the light along its full
    length and reads as timber rather than as an extrusion.
    """
    xs = np.linspace(xi0, xi1, n)
    grid = np.zeros((n, 10, 3))
    for i, xi in enumerate(xs):
        p = hull.surface(xi, 0.999)
        nrm = hull.normal(xi, 0.999)
        # the gunwale is offset purely transversely, whatever the surface does
        nrm = np.array([0.0, 1.0 if nrm[1] >= 0 else -1.0, 0.0])
        # taper the rail away to nothing at the stem and the transom
        k = smoothstep(0.02, 0.16, p[1]) * smoothstep(0.02, 0.10, abs(hull.x_of(xi) - hull.x_stern))
        out = p + nrm * (out_width * k)
        inn = p - nrm * (in_width * k)
        h = height * max(0.45, k)
        cap = 0.006 * max(0.3, k)        # the cap stands proud of the rail
        ear = 0.005 * max(0.3, k)        # and overhangs it slightly
        z0 = 0.002
        # section, running round: outboard face -> crown -> inboard face
        grid[i, 0] = out - nrm * ear + np.array([0, 0, z0 - 0.004])
        grid[i, 1] = out + np.array([0, 0, z0])
        grid[i, 2] = out + np.array([0, 0, z0 + h * 0.55])
        grid[i, 3] = out - nrm * ear + np.array([0, 0, z0 + h * 0.80])
        grid[i, 4] = (out + inn) * 0.5 + np.array([0, 0, z0 + h + cap])
        grid[i, 5] = inn + nrm * ear + np.array([0, 0, z0 + h * 0.80 + rise_inboard])
        grid[i, 6] = inn + np.array([0, 0, z0 + h * 0.55 + rise_inboard])
        grid[i, 7] = inn + np.array([0, 0, rise_inboard - 0.012])
        grid[i, 8] = inn * 0.5 + out * 0.5 + np.array([0, 0, z0 - 0.010])
        grid[i, 9] = out + np.array([0, 0, z0 - 0.004])
    base = mb.add_grid(grid, mat, close_v=True)
    mb.add_face([base + i for i in range(10)][::-1], mat)
    end = base + 10 * (n - 1)
    mb.add_face([end + i for i in range(10)], mat)


def plank_panel(mb, xs, edge_fn, z_fn, mats, thick=0.030, n_planks=None,
                plank_w=0.115, gap=0.005, tx=0.0):
    """Lay a deck or sole as individual boards rather than one slab.

    `edge_fn(x)` returns the two outboard y values at that station, `z_fn(x)`
    the top height.  Each board is a closed four-sided extrusion with a small
    caulking gap either side; the board count is held constant along the length
    so the planks converge at the ends the way real stolen planks do.  Board
    tone cycles through `mats`, which is what makes the deck read as planking
    from any distance instead of as a painted surface.
    """
    xs = np.asarray(xs, dtype=float)
    if n_planks is None:
        xm = xs[len(xs) // 2]
        y0, y1 = edge_fn(xm)
        n_planks = max(1, int(round(abs(y1 - y0) / plank_w)))
    for k in range(n_planks):
        fa = k / n_planks
        fb = (k + 1) / n_planks
        grid = np.zeros((len(xs), 4, 3))
        for i, x in enumerate(xs):
            y0, y1 = edge_fn(x)
            z = z_fn(x)
            w = y1 - y0
            ya = y0 + w * fa + gap * 0.5
            yb = y0 + w * fb - gap * 0.5
            if yb - ya < 0.012:
                ya = y0 + w * fa
                yb = y0 + w * fb
            grid[i, 0] = (x + tx, ya, z)
            grid[i, 1] = (x + tx, yb, z)
            grid[i, 2] = (x + tx, yb, z - thick)
            grid[i, 3] = (x + tx, ya, z - thick)
        mb.add_grid(grid, mats[k % len(mats)], close_v=True)
        # close the two ends so the board is a solid, not a shell
        for i, flip in ((0, True), (len(xs) - 1, False)):
            q = [grid[i, j] for j in range(4)]
            mb.add_quad(q[0], q[1], q[2], q[3], mats[k % len(mats)], flip=flip)


def build_rubbing_strake(hull, mb, t=0.93, r=0.017, xi0=0.035, xi1=0.965,
                         mat=MAT["wood_timber"], offset=0.004, n=70):
    """Half-round rubbing strake along the topsides.

    The strake takes the wear from fenders, davit falls and the ship's side, so
    it stands proud of the planking and is the first thing to be renewed.  It
    also catches a highlight along the sheer that a bare plank edge never will.
    """
    pts = []
    for xi in np.linspace(xi0, xi1, n):
        p = hull.surface(xi, t)
        nn = hull.normal(xi, t)
        pts.append(p + nn * offset)
    mb.add_tube(np.array(pts), r, segments=8, mat=mat)


def build_stem_band(hull, mb, r=0.020, mat=MAT["brass"], n=14, t0=0.0, t1=0.42):
    """Metal band down the fore side of the stem, from the forefoot to the
    stem head -- the part that takes the knocks when the boat comes alongside."""
    pts = []
    for t in np.linspace(t0, t1, n):
        p = hull.surface(0.0006, t)
        pts.append(p + np.array([-r * 0.55, 0, 0]))
    pts = np.array(pts)
    if len(pts) > 2:
        mb.add_tube(pts, r, segments=8, mat=mat)


def half_breadth_at(hull, xi, z, n=80):
    """Half-breadth of the hull at a given height on a given station."""
    best = 0.0
    for t in np.linspace(0.0, 1.0, n):
        p = hull.surface(xi, t)
        if p[2] <= z + 1e-6:
            best = max(best, p[1])
    return best


def build_keelson(hull, mb, width=0.085, height=0.060, xi0=0.06, xi1=0.93, mat=MAT["wood_timber"]):
    n = 40
    xs = np.linspace(xi0, xi1, n)
    grid = np.zeros((n, 4, 3))
    for i, xi in enumerate(xs):
        p = hull.inner(xi, 0.012, 0.030)
        grid[i, 0] = p + np.array([0, -width * 0.5, 0])
        grid[i, 1] = p + np.array([0, width * 0.5, 0])
        grid[i, 2] = p + np.array([0, width * 0.5, height])
        grid[i, 3] = p + np.array([0, -width * 0.5, height])
    base = mb.add_grid(grid, mat, close_v=True)
    mb.add_face([base + i for i in range(4)][::-1], mat)
    end = base + 4 * (n - 1)
    mb.add_face([end + i for i in range(4)], mat)


# --------------------------------------------------------------------------
# small helpers used by both boats
# --------------------------------------------------------------------------


def sweep_rect(mb, path, normals, width, depth, mat=MAT["wood_timber"], center_offset=0.0):
    """Sweep a rectangular section along a path with a given normal frame."""
    path = np.asarray(path, dtype=float)
    n = len(path)
    grid = np.zeros((n, 4, 3))
    for i in range(n):
        p = path[i]
        nrm = unit(normals[i])
        # local transverse direction = normal x tangent
        t = path[min(n - 1, i + 1)] - path[max(0, i - 1)]
        t = unit(t)
        side = unit(np.cross(nrm, t))
        p = p + nrm * center_offset
        w = width * 0.5
        grid[i, 0] = p + side * w
        grid[i, 1] = p + side * w + nrm * depth
        grid[i, 2] = p - side * w + nrm * depth
        grid[i, 3] = p - side * w
    base = mb.add_grid(grid, mat, close_v=True)
    mb.add_face([base + k for k in range(4)][::-1], mat)
    end = base + 4 * (n - 1)
    mb.add_face([end + k for k in range(4)], mat)




def solid_between_sections(mb, hull, xs, depth, mat=MAT["wood_timber"], n_t=22, cap_front=True,
                           cap_back=True):
    """Fill the interior of the hull between two stations with solid timber --
    the apron at the stem and the transom knee at the stern.  Real boats are
    solid there, so the model is too: without it, looking into the bow shows
    the inside of the planking instead of a stem."""
    rings = []
    for xi in xs:
        ts = np.linspace(0.0, 1.0, n_t)
        half = [hull.inner(xi, t, depth) for t in ts]
        left = [np.array([p[0], -p[1], p[2]]) for p in half]
        ring = half + left[::-1]
        rings.append(np.array(ring))
    n = len(rings[0])
    for a, b in zip(rings[:-1], rings[1:]):
        for i in range(n):
            j = (i + 1) % n
            mb.add_quad(a[i], a[j], b[j], b[i], mat)
    if cap_front:
        mb.add_face([len(mb.verts) - 1 - i for i in range(n)], mat)
    if cap_back:
        base = len(mb.verts) - n * len(rings)
        mb.add_face([base + i for i in range(n)], mat)

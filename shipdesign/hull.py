"""Parametric hull form for SS Aurelian (1889).

The hull is defined the way a Victorian drawing office would have done it:
a SHEER PROFILE (deck and keel lines), a HALF-BREADTH PLAN (waterline
half-breadths) and a BODY PLAN (section shapes).  From those three control
sets this module generates:

    * a watertight section-lofted shell mesh (verts / faces / UVs)
    * stations, waterlines and buttock lines for drawing a lines plan
    * hydrostatics (volume, displacement, Cb, Cp, Cw, LCB, KB, TPC, LCF)
    * deck-edge and shell-plating curves used by the structure generator

All dimensions in metres.  +X forward, +Y port, +Z up from base line.

Section construction follows late-1880s practice for a steel single-screw
liner: wall-sided topsides with a little flare at the bow, a circular bilge
of varying radius, a flat of bottom with slight rise of floor, and fine
V-shaped sections forward of the forefoot and abaft the after body.
"""
from __future__ import annotations
import math
from bisect import bisect_right
import numpy as np

from .spec import SHIP

L = SHIP["loa"]                 # 166.0
HL = L / 2.0                    # 83.0
B = SHIP["beam"]                # 18.4
HB = B / 2.0                    # 9.2
T = SHIP["draft"]               # 6.50
RHO = 1.025                     # salt water t/m3


# ---------------------------------------------------------------------------
# smooth monotone interpolation of control tables (PCHIP, no overshoot)
# ---------------------------------------------------------------------------
def _pchip(xk, yk, x):
    """Monotone cubic interpolation (Fritsch-Carlson).  xk increasing."""
    xk = np.asarray(xk, float); yk = np.asarray(yk, float)
    h = np.diff(xk); d = np.diff(yk) / h
    m = np.zeros_like(yk)
    m[0] = d[0]; m[-1] = d[-1]
    for i in range(1, len(yk) - 1):
        if d[i - 1] * d[i] <= 0:
            m[i] = 0.0
        else:
            w1 = 2 * h[i] + h[i - 1]; w2 = h[i] + 2 * h[i - 1]
            m[i] = (w1 + w2) / (w1 / d[i - 1] + w2 / d[i])
    x = np.atleast_1d(np.asarray(x, float))
    idx = np.clip(np.searchsorted(xk, x) - 1, 0, len(xk) - 2)
    hh = h[idx]; tt = (x - xk[idx]) / hh
    h00 = 2 * tt**3 - 3 * tt**2 + 1; h10 = tt**3 - 2 * tt**2 + tt
    h01 = -2 * tt**3 + 3 * tt**2;    h11 = tt**3 - tt**2
    out = (h00 * yk[idx] + h10 * hh * m[idx] +
           h01 * yk[idx + 1] + h11 * hh * m[idx + 1])
    return out


# ---------------------------------------------------------------------------
# CONTROL CURVES  (x increasing, -83 aft .. +83 forward)
# ---------------------------------------------------------------------------
# Sheer line at side (top of shell / upper-deck stringer).  High at bow with a
# sweeping rise, moderate rise aft — characteristic of Umbria / City of Paris /
# Teutonic.  Amidships 9.40 m, forecastle head 11.05 m, poop 10.30 m.
# Amidships the shell rises to main deck (8.60); forward and aft the sheer
# sweeps up to the forecastle (11.05) and poop (10.20), exactly as in the
# period photographs (Teutonic, Umbria, City of Paris, Majestic).
# The hull's strength deck is the UPPER (SALOON) DECK at 11.80 m amidships -
# this is the 'freeboard deck' and the top of the shell plating.  Sheer rises
# to 13.05 m at the stem and 12.35 m at the transom, which is the profile seen
# in the 1889 photographs of Teutonic and her contemporaries.  The promenade
# deck at 14.40 m is a superstructure deck carried on the deckhouse and on
# brackets off the ship's side (Ocean Magazine, Sept 1889: 'the roof of these
# rooms on the promenade deck is extended to the sides supported by angle
# frames carried up from the ship's side').
_X_SHEER = [-83.0, -81.5, -79.0, -76.0, -72.0, -64.0, -54.0, -44.0, -34.0,
            -24.0, -16.0, -10.0, 0.0, 10.0, 16.0, 24.0, 34.0, 44.0, 54.0,
            64.0, 71.0, 76.0, 80.0, 82.0, 83.0]
_Z_SHEER = [12.35, 12.34, 12.28, 12.18, 12.08, 11.94, 11.86, 11.80, 11.80,
            11.80, 11.80, 11.80, 11.80, 11.80, 11.80, 11.82, 11.90, 12.02,
            12.20, 12.44, 12.68, 12.88, 13.02, 13.05, 13.05]

# Forefoot: the forward end of the waterline (x=+80) must be a continuous,
# monotone rise from the keel to the stem.  Aft the keel sweeps up into the
# counter, the aft end of the waterline falling at x=-79.5.

# Keel / profile line: bottom of shell.  Flat of keel amidships, rising to the
# forefoot and to the counter aft.
_X_KEEL = [-83.0, -81.0, -79.5, -78.5, -77.0, -75.0, -70.0, -60.0, -20.0,
           30.0, 55.0, 66.0, 72.0, 74.5, 76.0, 77.0, 78.0, 79.0, 80.0, 81.0,
           82.0, 83.0]
_Z_KEEL = [9.55, 8.85, 8.10, 6.85, 5.20, 3.20, 1.30, 0.00, 0.00,
           0.00, 0.00, 0.00, 0.35, 1.05, 2.10, 3.05, 4.05, 5.00, 5.90, 6.45,
           6.68, 6.75]

# Half-breadth on the load waterline (z = 7.00).  Zero at x=-78.0 and x=+82.0
# -> LWL = 160.0 m as specified.
# LWL runs from x=-79.0 to x=+80.5  ->  LWL = 159.5 m (spec).
_X_BWL = [-79.000, -71.030, -63.050, -55.080, -47.100, -39.120, -31.150, -23.180, -15.200, -7.230, 0.750, 8.720, 16.700, 24.670, 32.650, 40.620, 48.600, 56.570, 64.550, 72.530, 80.500]
_Y_BWL = [0.000, 2.184, 3.983, 5.500, 6.757, 7.758, 8.503, 8.988, 9.196, 9.200, 9.200, 9.200, 9.189, 9.022, 8.652, 8.071, 7.260, 6.195, 4.818, 3.009, 0.000]

# Half-breadth at the deck edge (plan view of the deck line).
_X_BD = [-83.000, -74.700, -66.400, -58.100, -49.800, -41.500, -33.200, -24.900, -16.600, -8.300, 0.000, 8.300, 16.600, 24.900, 33.200, 41.500, 49.800, 58.100, 66.400, 74.700, 83.000]
_Y_BD = [0.000, 1.593, 3.638, 5.231, 6.521, 7.554, 8.349, 8.902, 9.184, 9.200, 9.200, 9.200, 9.191, 9.009, 8.622, 8.034, 7.231, 6.175, 4.783, 2.816, 0.000]

# Bilge radius as a fraction of the local waterline half-breadth (0..1).
# Full round bilge amidships, hardening to fine V sections at the ends.
_X_BILGE = [-80.0, -76.0, -70.0, -60.0, -40.0, -15.0, 10.0, 35.0, 55.0,
            63.0, 70.0, 75.0, 79.0, 82.0]
_R_BILGE = [0.10, 0.22, 0.36, 0.46, 0.53, 0.55, 0.55, 0.53, 0.48,
            0.42, 0.34, 0.26, 0.16, 0.06]

# Flat-of-bottom half width amidships as fraction of local waterline breadth.
_X_FLAT = [-78.0, -70.0, -50.0, -20.0, 10.0, 40.0, 60.0, 72.0, 80.0]
_K_FLAT = [0.02, 0.16, 0.30, 0.34, 0.34, 0.30, 0.22, 0.10, 0.02]


class HullForm:
    """Analytic hull definition with mesh + hydrostatic evaluation."""

    def __init__(self, scale=1.0):
        self.scale = scale

    # -- 1. primary curves --------------------------------------------------
    def deck_z(self, x):
        x = np.clip(x, -HL, HL)
        return _pchip(_X_SHEER, _Z_SHEER, x)

    def keel_z(self, x):
        x = np.clip(x, -HL, HL)
        return _pchip(_X_KEEL, _Z_KEEL, x)

    def beam_wl(self, x):
        x = np.clip(x, -HL, HL)
        return np.maximum(_pchip(_X_BWL, _Y_BWL, x), 0.0)

    def beam_deck(self, x):
        x = np.clip(x, -HL, HL)
        return np.maximum(_pchip(_X_BD, _Y_BD, x), 0.0)

    def x_at_wl_ends(self):
        return -79.0, 80.5

    # -- 2. section shape ---------------------------------------------------
    def section(self, x, n_below=16, n_above=8, include_keel_flat=True):
        """Return list of (y, z) from keel centreline to deck edge, port side.

        Built the way draftsmen laid out a body plan: flat of bottom, a
        quarter-ellipse bilge, then the wall side to the waterline, then the
        flared topside to the deck edge.  y >= 0.  Empty list if the station
        lies outside the hull.
        """
        x = float(np.clip(x, -HL, HL))
        zb = float(self.keel_z(x)); zd = float(self.deck_z(x))
        bd = float(self.beam_deck(x)); bwl = float(self.beam_wl(x))
        if bd < 0.015 or zd - zb < 0.05:
            return []
        pts = []
        # ---- below water: flat of bottom + elliptic bilge ----------------
        if zb < T - 1e-6 and bwl > 0.03:
            d = T - zb
            kflat = float(_pchip(_X_FLAT, _K_FLAT, x)) * bwl
            kflat = min(kflat, bwl * 0.85)
            frac = float(_pchip(_X_BILGE, _R_BILGE, x))     # bilge radius / bwl
            r = max(0.03, min(frac, 0.95) * bwl)            # horizontal semi-axis
            rv = r * 0.86                                   # vertical semi-axis
            rv = min(rv, d * 0.92)
            pts.append((0.0, zb))
            if kflat > 0.04:
                pts.append((kflat, zb))
            # quarter ellipse from (bwl - r, zb) round to (bwl, zb + rv)
            nb = max(4, n_below // 2)
            for i in range(1, nb + 1):
                a = (i / nb) * (math.pi / 2)
                pts.append((bwl - r + r * math.sin(a), zb + rv * (1 - math.cos(a))))
            # wall side to the waterline (may be zero length)
            nw = max(2, n_below - nb)
            z0 = pts[-1][1]
            if T - z0 > 1e-4:
                for i in range(1, nw + 1):
                    pts.append((bwl, z0 + (T - z0) * (i / nw)))
        else:
            pts.append((0.0, zb))
        # ---- topsides with slight flare ----------------------------------
        zlast = pts[-1][1]; ylast = pts[-1][0]
        if zd > zlast + 1e-4:
            for i in range(1, n_above + 1):
                f = i / n_above
                z = zlast + (zd - zlast) * f
                nfl = 1.85 - 0.65 * min(1.0, max(0.0, (x - 15.0) / 55.0))
                y = ylast + (bd - ylast) * (f ** nfl)
                pts.append((y, z))
        return pts

    def section_closed(self, x, **kw):
        """Half section mirrored into a closed polygon (starboard to port)."""
        half = self.section(x, **kw)
        if not half:
            return []
        poly = [(y, z) for (y, z) in half]
        poly += [(-y, z) for (y, z) in reversed(half[1:-1])]
        return poly

    # -- 3. mesh ------------------------------------------------------------
    def stations(self, n):
        """n stations distributed with tight spacing at the ends."""
        s = np.linspace(-1.0, 1.0, n)
        # cosine-ish distribution: denser at bow/stern
        return HL * np.sign(s) * (np.abs(s) ** 0.92)

    def build_shell(self, n_stations=181, n_below=14, n_above=9):
        """Lofted shell surface.  Returns verts (N,3), quads (M,4), uv (N,2).

        The layout is a regular grid: for each station a row of points from
        port deck edge -> keel -> starboard deck edge, so the same row index
        along all stations forms a longitudinal line.
        """
        xs = self.stations(n_stations)
        rows = []
        for x in xs:
            poly = self.section_closed(x, n_below=n_below, n_above=n_above)
            if len(poly) < 4:
                rows.append(None)
            else:
                rows.append(poly)
        # resample every row to a common count (keep shape) so grid is regular
        counts = [len(r) for r in rows if r]
        if not counts:
            return np.zeros((0, 3)), [], np.zeros((0, 2))
        nmax = max(counts)
        grid = []
        for poly in rows:
            if poly is None:
                grid.append(None); continue
            p = np.array(poly, float)
            # resample by arc length proportion in y,z
            d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(p, axis=0), axis=1))]
            if d[-1] < 1e-6:
                grid.append(p[0][None, :].repeat(nmax, 0)); continue
            u = d / d[-1]
            targ = np.linspace(0, 1, nmax)
            gy = np.interp(targ, u, p[:, 0]); gz = np.interp(targ, u, p[:, 1])
            grid.append(np.c_[gy, gz])
        # stations fully outside (degenerate) -> skip but keep topology
        valid = [i for i, g in enumerate(grid) if g is not None]
        verts = []; uvs = []
        vmap = {}
        for i in valid:
            x = xs[i]
            for j, (y, z) in enumerate(grid[i]):
                vmap[(i, j)] = len(verts)
                verts.append((x, y, z))
                uvs.append((i / (len(xs) - 1), j / (nmax - 1)))
        faces = []
        for a, b in zip(valid[:-1], valid[1:]):
            if b != a + 1:
                continue
            for j in range(nmax - 1):
                v0 = vmap[(a, j)]; v1 = vmap[(a, j + 1)]
                v2 = vmap[(b, j + 1)]; v3 = vmap[(b, j)]
                faces.append((v0, v1, v2, v3))
        return np.array(verts, float), faces, np.array(uvs, float)

    # -- 4. hydrostatics ----------------------------------------------------
    def _section_props(self, half, dz=0.05):
        """Area and first moments of a half section (y,z) between z=0..T."""
        if len(half) < 3:
            return 0.0, 0.0, 0.0
        zs = np.linspace(0.0, T, int(T / dz))
        ys = np.interp(zs, [p[1] for p in half], [p[0] for p in half],
                       left=half[0][0], right=half[-1][0])
        ys = np.clip(ys, 0, None)
        # clamp: only where section exists
        zlo = half[0][1]; zhi = half[-1][1]
        ys[(zs < zlo) | (zs > zhi)] = np.nan
        ok = ~np.isnan(ys)
        area = np.trapz(ys[ok], zs[ok]) * 2
        mz = np.trapz(ys[ok] * zs[ok], zs[ok]) * 2
        return area, mz, area

    def hydrostatics(self, draft=T, nx=321):
        """Volume, displacement, coefficients, LCB, KB, waterplane data."""
        xs = np.linspace(-HL, HL, nx)
        areas = np.zeros(nx); mz = np.zeros(nx); yw = np.zeros(nx)
        for i, x in enumerate(xs):
            half = self.section(x)
            if not half:
                continue
            a, m, _ = self._section_props(half)
            areas[i] = a; mz[i] = m
            # waterplane half breadth at draft
            zs = [p[1] for p in half]; ys = [p[0] for p in half]
            if half[0][1] <= draft <= half[-1][1]:
                yw[i] = float(np.interp(draft, zs, ys))
        # sections are sections of the FULL hull already (mirrored)
        vol = np.trapz(areas, xs)
        mom_x = np.trapz(areas * xs, xs)
        lcb = mom_x / vol if vol else 0.0
        kb = (np.trapz(mz, xs) / vol) if vol else 0.0
        wp_area = np.trapz(yw * 2, xs)
        mom_wp = np.trapz(yw * 2 * xs, xs)
        lcf = mom_wp / wp_area if wp_area else 0.0
        wl_len = xs[np.argmax(yw > 0.01)], xs[len(yw) - 1 - np.argmax(yw[::-1] > 0.01)]
        disp = vol * RHO
        cb = vol / (abs(wl_len[1] - wl_len[0]) * B * draft) if vol else 0
        amax = areas.max()
        cm = amax / (B * draft) if amax else 0
        cw = wp_area / (abs(wl_len[1] - wl_len[0]) * B) if wp_area else 0
        return dict(
            lwl=abs(wl_len[1] - wl_len[0]),
            volume_m3=vol, displacement_t=disp, lcb_m=lcb,
            lcb_pct=lcb / (abs(wl_len[1] - wl_len[0])) * 100,
            kb_m=kb, waterplane_m2=wp_area, lcf_m=lcf,
            cb=cb, cm=cm, cw=cw, cp=cb / cm if cm else 0,
            midship_area_m2=amax, tpc=wp_area * RHO / 100.0,
            wetted_area_m2=self.wetted_area(nx // 2),
        )

    def wetted_area(self, nx=161):
        xs = np.linspace(-HL, HL, nx)
        tot = 0.0
        prev = None
        for x in xs:
            half = self.section(x)
            if not half:
                prev = None; continue
            # arc length below water of the half section, mirrored
            arc = 0.0
            seg = [(y, z) for (y, z) in half if z <= T]
            for (y0, z0), (y1, z1) in zip(seg[:-1], seg[1:]):
                arc += math.hypot(y1 - y0, z1 - z0)
            cur = arc * 2
            if prev is not None:
                tot += (cur + prev) / 2 * (xs[1] - xs[0])
            prev = cur
        return tot

    # -- 5. derived curves used by other modules ---------------------------
    def deck_edge(self, deck_z_target, side=1):
        """x positions where the deck edge (sheer) is at a given height."""
        return None

    def half_beam_at(self, x, z):
        half = self.section(x)
        if not half:
            return 0.0
        zs = [p[1] for p in half]; ys = [p[0] for p in half]
        if z < zs[0] or z > zs[-1]:
            return 0.0
        return float(np.interp(z, zs, ys))


HULL = HullForm()

if __name__ == "__main__":
    import json
    h = HULL.hydrostatics()
    print(json.dumps({k: (round(v, 2) if isinstance(v, float) else v)
                      for k, v in h.items()}, indent=1))

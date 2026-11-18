"""
hull2.py -- parametric boat hull loft (second generation).

The design surface is lofted from faired curves: sheer line, keel line,
half-breadth, and sectional fullness.  Everything structural (strakes, frames,
gunwales, decks) is generated against this one surface so the parts agree.

xi in [0,1]: 0 = stem head (x = +loa/2), 1 = stern (x = -loa/2).
t in [0,1] along a section: 0 = keel, 1 = sheer.
"""

from __future__ import annotations
import math
import numpy as np
from .geom2 import Pchip, curve, unit, clamp, smoothstep


class Hull2:
    def __init__(self, name, loa, beam, sheer_pts, keel_pts, hb_pts,
                 k_fwd=1.9, k_mid=0.85, k_aft=1.6, flare_fwd=0.10, flare_aft=0.03,
                 stem_rake=0.10, transom=True, transom_rake=0.16,
                 stern_rake=0.12):
        self.name = name
        self.loa = float(loa)
        self.beam = float(beam)
        self.W = beam / 2.0
        self.sheer = curve(sheer_pts)
        self.keel = curve(keel_pts)
        self.hb = curve(hb_pts)          # normalized 0..1 (1 at fullest)
        self.k_fwd, self.k_mid, self.k_aft = k_fwd, k_mid, k_aft
        self.flare_fwd, self.flare_aft = flare_fwd, flare_aft
        self.stem_rake = stem_rake       # metres the stem head overhangs forward
        self.transom = transom
        self.transom_rake = transom_rake if transom else stern_rake
        self.stern_rake = stern_rake

    # -- principal curves ----------------------------------------------------
    def X(self, xi):
        return self.loa / 2.0 - xi * self.loa

    def sheer_z(self, xi):
        return self.sheer(xi)

    def keel_z(self, xi):
        return self.keel(xi)

    def depth(self, xi):
        return self.sheer(xi) - self.keel(xi)

    def halfW(self, xi):
        return self.W * max(1e-4, self.hb(xi))

    def shape_k(self, xi):
        # V-sections at the ends, moulded (round/U) amidships
        w_fwd = smoothstep(0.55, 0.0, xi)
        w_aft = smoothstep(0.45, 1.0, xi)
        w_mid = clamp(1.0 - w_fwd - w_aft, 0.0, 1.0)
        return self.k_fwd * w_fwd + self.k_mid * w_mid + self.k_aft * w_aft

    def flare(self, xi):
        return self.flare_fwd * smoothstep(0.5, 0.0, xi) + \
            self.flare_aft * smoothstep(0.5, 1.0, xi)

    # -- sections --------------------------------------------------------------
    def section_pt(self, xi, t, offset=0.0):
        """Point on the section at (xi, t).  offset is outward (m)."""
        xi = clamp(xi, 0.0, 1.0)
        t = clamp(t, 0.0, 1.0)
        z0 = self.keel_z(xi); z1 = self.sheer_z(xi)
        W = self.halfW(xi)
        k = self.shape_k(xi)
        base = math.sin(0.5 * math.pi * t) ** k
        fl = self.flare(xi)
        y = W * min(1.0, base * (1.0 + fl * t ** 2.4))
        # ease the keel corner: below t=tk the section narrows to the keel face
        z = z0 + (z1 - z0) * t
        x = self.X(xi)
        if xi <= 1e-9:      # raked stem profile
            x += self.stem_rake * t ** 1.25
        if xi >= 1 - 1e-9 and self.transom:
            x -= self.transom_rake * t ** 1.15 * self.depth(xi)
        if abs(offset) > 1e-12:
            n = self.section_normal(xi, t)
            y += n[1] * offset
            z += n[2] * offset
        return np.array([x, y, z])

    def section_normal(self, xi, t):
        """Outward unit normal in the section plane (approx, via 2D finite diff)."""
        e = 1e-3
        p0 = self._pt_raw(xi, max(0.0, t - e))
        p1 = self._pt_raw(xi, min(1.0, t + e))
        d = p1 - p0
        n = np.array([0.0, d[2], -d[1]])   # rotate tangent 90deg, outward +Y
        n = unit(n)
        if n[1] < 0:
            n = -n
        return n

    def _pt_raw(self, xi, t):
        z0 = self.keel_z(xi); z1 = self.sheer_z(xi)
        W = self.halfW(xi)
        k = self.shape_k(xi)
        base = math.sin(0.5 * math.pi * t) ** k
        fl = self.flare(xi)
        y = W * min(1.0, base * (1.0 + fl * clamp(t, 0, 1) ** 2.4))
        z = z0 + (z1 - z0) * t
        return np.array([0.0, y, z])

    # -- stations and arc length ------------------------------------------------
    def stations(self, n=41):
        # cosine-clustered: dense at the ends where curvature lives
        u = np.linspace(0, 1, n)
        return 0.5 * (1 - np.cos(math.pi * u))

    def section_poly(self, xi, nt=49, offset=0.0):
        ts = np.linspace(0, 1, nt)
        return np.array([self.section_pt(xi, t, offset) for t in ts])

    def girth(self, xi, offset=0.0, nt=49):
        pts = self.section_poly(xi, nt, offset)
        return float(np.sum(np.linalg.norm(np.diff(pts, axis=0), axis=1)))

    def arc_to_t(self, xi, frac, offset=0.0, nt=49):
        """Map arc-length fraction (0=keel, 1=sheer) to t parameter."""
        pts = self.section_poly(xi, nt, offset)
        seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
        s = np.concatenate([[0.0], np.cumsum(seg)])
        s /= s[-1]
        ts = np.linspace(0, 1, nt)
        return float(np.interp(frac, s, ts))

    def pt_at_arc(self, xi, frac, offset=0.0):
        return self.section_pt(xi, self.arc_to_t(xi, frac), offset)

    def skin_grid(self, nx=61, nt=33, offset=0.0):
        """Lofted half-surface grid (starboard), rows along xi, cols along t."""
        xis = np.linspace(0, 1, nx)
        grid = np.zeros((nx, nt, 3))
        for i, xi in enumerate(xis):
            ts = np.linspace(0, 1, nt)
            for j, t in enumerate(ts):
                grid[i, j] = self.section_pt(xi, t, offset)
        return grid

    # -- hydrostatics ------------------------------------------------------------
    def displaced_volume(self, z_d, nx=41, nt=41):
        """Volume below z_d (Sutherland-Hodgman clip per section, shoelace)."""
        xis = self.stations(nx)
        areas = []
        for xi in xis:
            poly = self.section_poly(xi, nt=nt, offset=0.0)
            ps = [(p[1], p[2]) for p in poly]
            port = [(-p[1], p[2]) for p in poly][::-1]
            ring = ps + port + [ps[0]]
            # clip polygon against half-plane z <= z_d
            out = []
            for i in range(len(ring) - 1):
                y0, z0 = ring[i]
                y1, z1 = ring[i + 1]
                in0 = z0 <= z_d
                in1 = z1 <= z_d
                if in0 and in1:
                    out.append((y1, z1))
                elif in0 and not in1:
                    f = (z_d - z0) / (z1 - z0)
                    out.append((y0 + (y1 - y0) * f, z_d))
                elif not in0 and in1:
                    f = (z_d - z0) / (z1 - z0)
                    out.append((y0 + (y1 - y0) * f, z_d))
                    out.append((y1, z1))
            a = 0.0
            for i in range(len(out)):
                y0, z0 = out[i]
                y1, z1 = out[(i + 1) % len(out)]
                a += 0.5 * (y0 * z1 - y1 * z0)
            areas.append(abs(a))
        xs = np.array([self.X(xi) for xi in xis])
        xs = xs[::-1]  # Simpson needs ascending
        areas = np.array(areas)[::-1]
        # composite Simpson over non-uniform x: use trapz (adequate at 41 st.)
        vol = float(np.trapz(areas, xs))
        # LCB
        num = float(np.trapz(areas * xs, xs))
        lcb = num / vol if vol > 1e-9 else 0.0
        return vol, lcb

    @staticmethod
    def _clip(y0, z0, y1, z1, z_d):
        """Closed polygon piece of segment below the waterline (as trapezoid)."""
        if z0 > z_d and z1 > z_d:
            return []
        if z0 <= z_d and z1 <= z_d:
            return [(y0, z0, y1, z1)]
        f = (z_d - z0) / (z1 - z0)
        yi = y0 + (y1 - y0) * f
        if z0 <= z_d:
            return [(y0, z0, yi, z_d)]
        return [(yi, z_d, y1, z1)]

    def solve_draught(self, mass_kg, waterline_window=(-2.0, 2.0), tol=0.5):
        """Find draught z_d (negative down from Z=0 design WL) giving mass."""
        rho = 1025.0
        lo, hi = waterline_window
        for _ in range(48):
            mid = 0.5 * (lo + hi)
            v, _ = self.displaced_volume(mid)
            if v * rho > mass_kg:
                hi = mid
            else:
                lo = mid
        z = 0.5 * (lo + hi)
        v, lcb = self.displaced_volume(z)
        return z, v * rho, lcb

    def hydro(self, z_d):
        vol, lcb = self.displaced_volume(z_d)
        return {
            "displacement_kg": round(vol * 1025.0, 1),
            "draft_m": round(max(0.0, -z_d + min(0.0, 0)) + max(0.0, -z_d), 3),
            "draft_from_z0_m": round(-min(0.0, z_d), 3),
            "lcb_m": round(lcb, 3),
            "freeboard_amidships_m": round(self.sheer_z(0.5) - max(z_d, -1.0), 3),
        }

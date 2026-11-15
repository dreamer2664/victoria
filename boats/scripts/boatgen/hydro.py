"""
hydro.py -- hydrostatic properties of a HullDesign by numerical integration.

The boat's floating waterline is *solved*, not assumed: given a mass, the
waterline height z at which the displaced volume equals mass/rho is found by
bisection, and draft / freeboard / coefficients follow from it.  This is what
keeps the published weight and the published draft consistent.
"""

from __future__ import annotations

import numpy as np

RHO_SEA = 1025.0  # kg/m3
_trapz = getattr(np, "trapezoid", None) or np.trapz  # numpy <2 / Blender bundled numpy


def _immersed(hull, z_wl, n_xi=160, n_t=90):
    """Return (x, sectional_area, waterplane_halfbreadth) below z_wl."""
    xis = np.linspace(0, 1, n_xi)
    ts = np.linspace(0, 1, n_t)
    g = hull.grid(xis, ts)            # (n_xi, n_t, 3)
    y, z = g[:, :, 1], g[:, :, 2]
    below = z <= z_wl
    # area of the immersed part of each section (left-half breadth = y, times 2 later)
    area = np.zeros(n_xi)
    for i in range(n_xi):
        zb = z[i][below[i]]
        yb = y[i][below[i]]
        if len(zb) < 2:
            continue
        # close the section at the waterline
        if below[i].sum() < n_t:
            j = np.argmax(~below[i])
            if j > 0:
                f = (z_wl - z[i, j - 1]) / (z[i, j] - z[i, j - 1])
                zb = np.append(zb, z_wl)
                yb = np.append(yb, y[i, j - 1] + f * (y[i, j] - y[i, j - 1]))
        area[i] = _trapz(yb, zb)
    x = g[:, 0, 0]
    hb = np.array([y[i][below[i]].max() if below[i].any() else 0.0 for i in range(n_xi)])
    return x, area, hb


def hydrostatics(hull, z_wl=0.0, n_xi=160):
    x, area, hb = _immersed(hull, z_wl, n_xi)
    # integration runs bow -> stern, i.e. decreasing x
    xr = x[::-1]
    ar = area[::-1]
    vol = _trapz(2.0 * ar, xr)
    lcb = _trapz(2.0 * ar * xr, xr) / vol if vol > 1e-9 else 0.0
    awp = _trapz(2.0 * hb[::-1], xr)
    lcf = _trapz(2.0 * hb[::-1] * xr, xr) / awp if awp > 1e-9 else 0.0
    amax = float(np.max(area))
    keep = area > 1e-6
    lwl = float(x[keep].max() - x[keep].min()) if keep.any() else 0.0
    keel_min = min(hull.keel_z(i / 100.0) for i in range(101))
    return {
        "waterline_z_m": round(float(z_wl), 3),
        "draft_m": round(float(z_wl - keel_min), 3),
        "freeboard_amidships_m": round(float(hull.sheer_z(0.5) - z_wl), 3),
        "volume_m3": round(float(vol), 4),
        "displacement_kg": round(float(vol) * RHO_SEA, 1),
        "lcb_m_from_mid": round(float(lcb), 3),
        "lcf_m_from_mid": round(float(lcf), 3),
        "waterplane_m2": round(float(awp), 3),
        "midship_area_m2": round(2.0 * amax, 4),
        "lwl_m": round(lwl, 3),
        "block_coeff": round(float(vol) / (hull.loa * hull.bmax * 2 * max(1e-6, z_wl - keel_min)), 4),
        "prismatic_coeff": round(float(vol) / (hull.loa * 2.0 * amax), 4) if amax > 0 else None,
    }


def solve_waterline(hull, mass_kg, lo=-0.90, hi=0.60, n_xi=110):
    """Waterline height z at which displacement == mass."""
    lo, hi = min(lo, hull.keel_z(0.5) - 0.01), max(hi, hull.sheer_z(0.5) - 0.02)
    for _ in range(34):
        mid = 0.5 * (lo + hi)
        x, area, hb = _immersed(hull, mid, n_xi)
        v = _trapz(2.0 * area[::-1], x[::-1])
        if v * RHO_SEA < mass_kg:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)

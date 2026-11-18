#!/usr/bin/env python3
"""
drawings2.py -- THEMISTOCLES-II lines plans + GA sheets, drawn from the SAME
Hull2 objects the 3D boats are built from.  One sheet per boat.

    python3 drawings2.py

Outputs boats/drawings/d2-00{1,2,3}_{a,b,c}_{lines,ga}.{png,svg}
"""
import os, sys, math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from them2 import specs2 as S

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "boats", "drawings")
os.makedirs(OUT, exist_ok=True)

INK, THIN, FAINT, ACCENT, BLUE = "#1a1a1a", "#4a4a4a", "#9a9a9a", "#8c1c13", "#1f4e79"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7,
                     "lines.linewidth": 0.6})


def ft_in(m):
    ft = m / 0.3048
    return f"{int(ft)} ft {int(round((ft % 1) * 12))} in"


def sheet_lines(hull, wspec, cls, code):
    fig = plt.figure(figsize=(11.7, 8.27))           # A4 landscape
    # ---- sheer plan -----------------------------------------------------
    ax = fig.add_axes([0.05, 0.56, 0.90, 0.40]); ax.set_axis_off()
    xi = np.linspace(0, 1, 241)
    x = (xi - 0.5) * hull.loa
    sheer = np.array([hull.sheer_z(q) for q in xi])
    keel = np.array([hull.keel_z(q) - 0.10 for q in xi])
    ax.plot(x, sheer, color=INK, lw=1.1)
    ax.plot(x, keel, color=INK, lw=0.9)
    # stations
    for q in np.linspace(0, 1, 11):
        px = (q - 0.5) * hull.loa
        ax.plot([px, px], [hull.keel_z(q) - 0.10, hull.sheer_z(q)], color=FAINT,
                lw=0.3, ls=(0, (4, 2)))
        ax.text(px, hull.sheer_z(q) + 0.05, f"{int(round(q*10))}", fontsize=5,
                color=FAINT, ha="center")
    # waterlines (solved)
    for zz, label, col in ((0.0, "LWL (loaded)", BLUE),):
        ax.axhline(zz, color=col, lw=0.5, ls=(0, (6, 2)))
        ax.text(-hull.loa / 2 + 0.05, zz + 0.02, label, fontsize=5.5, color=col)
    for wl in (0.15, 0.30, 0.45):
        ax.axhline(-wl, color=FAINT, lw=0.3, ls=(0, (2, 3)))
        ax.text(-hull.loa / 2 + 0.05, -wl + 0.02, f"WL {-wl:.2f}", fontsize=4.5,
                color=FAINT)
    for t in np.linspace(0.15, 0.95, 5):
        prof = [hull.section_pt(q, hull.arc_to_t(q, t), 0.0) for q in xi[::4]]
        prof = np.array(prof)
        ax.plot(prof[:, 0], prof[:, 2], color=THIN, lw=0.4)
    ax.text(0, max(sheer) + 0.28, "SHEER PLAN  (profile)", fontsize=8,
            ha="center", color=INK)
    ax.set_xlim(-hull.loa / 2 - 0.35, hull.loa / 2 + 0.35)
    ax.set_ylim(min(keel) - 0.25, max(sheer) + 0.42)
    ax.set_aspect("equal")

    # ---- half-breadth plan ----------------------------------------------
    ax2 = fig.add_axes([0.05, 0.13, 0.56, 0.36]); ax2.set_axis_off()
    for t in (0.25, 0.5, 0.75, 0.92):
        pts = np.array([hull.section_pt(q, hull.arc_to_t(q, t), 0.0) for q in xi])
        ax2.plot(pts[:, 0], -pts[:, 1], color=THIN, lw=0.5)
        ax2.text(pts[-1, 0] + 0.05, -pts[-1, 1], f"{t:.2f}", fontsize=4.5, color=FAINT)
    # gunwale
    pts = np.array([hull.section_pt(q, 1.0, 0.0) for q in xi])
    ax2.plot(pts[:, 0], -pts[:, 1], color=INK, lw=1.0)
    ax2.axvline(0, color=FAINT, lw=0.3)
    # stations
    for q in np.linspace(0, 1, 11):
        p0 = hull.section_pt(q, 0.03, 0); p1 = hull.section_pt(q, 1.0, 0)
        ax2.plot([p0[0], p1[0]], [0, -p1[1]], color=FAINT, lw=0.3, ls=(0, (4, 2)))
    ax2.text(0, hull.beam * 0.62, "HALF-BREADTH PLAN (port half)",
             fontsize=8, ha="center", color=INK)
    ax2.set_aspect("equal")
    ax2.set_ylim(hull.beam * 0.66, -(hull.beam * 0.62))

    # ---- body plan -------------------------------------------------------
    ax3 = fig.add_axes([0.66, 0.13, 0.30, 0.36]); ax3.set_axis_off()
    zs = max(sheer) - min(keel)
    for q, side, off in [(0.1, 1, -0.55), (0.2, 1, -0.55), (0.3, 1, -0.55),
                          (0.4, 1, -0.55), (0.5, 1, -0.55), (0.6, 1, 0.55),
                          (0.7, 1, 0.55), (0.8, 1, 0.55), (0.9, 1, 0.55)]:
        ts = np.linspace(0.0, 1.0, 40)
        pts = np.array([hull.section_pt(q, t, 0.0) for t in ts])
        sx = side * (pts[:, 1]) + off
        ax3.plot(sx, pts[:, 2], color=INK, lw=0.5)
        ax3.text(sx[-1] + 0.02, pts[-1, 2], f"{int(q*10)}", fontsize=4.5, color=FAINT)
    ax3.axhline(0, color=BLUE, lw=0.4, ls=(0, (6, 2)))
    ax3.text(0.55 + hull.beam / 2, max(sheer) + 0.06, "BODY PLAN", fontsize=8,
             ha="center", color=INK)
    ax3.set_aspect("equal"); ax3.set_ylim(min(keel) - 0.15, max(sheer) + 0.25)

    # ---- dimension callouts ----------------------------------------------
    d = f"{code} — {cls.replace('_', ' ').upper()}"
    loaded = wspec["loaded"]
    light = wspec["light"]
    ax.text(0, min(keel) - 0.22,
            f"LOA {hull.loa:.3f} m ({ft_in(hull.loa)}) ·  beam {hull.beam:.3f} m "
            f"({ft_in(hull.beam)}) ·  draught {loaded['draft_m']:.2f} m loaded / "
            f"{light['draft_m']:.2f} m light ·  displacement {loaded['displacement_kg']:.0f} / "
            f"{light['displacement_kg']:.0f} kg — solved, not guessed",
            fontsize=7, ha="center", color=INK)
    fig.text(0.05, 0.965, "OPERATION VICTORIA — THEMISTOCLES-II boats",
             fontsize=9, color=INK)
    fig.text(0.05, 0.075, "Frame of reference: +X bow, +Y port, Z=0 at the "
             "LOADED waterline, origin mid-LOA. 1 stud = 0.28 m.",
             fontsize=5.5, color=FAINT)
    for ext in ("png", "svg"):
        fig.savefig(os.path.join(OUT, f"{code}_lines.{ext}"), dpi=200)
    plt.close(fig)
    print("wrote", code)


def main():
    hulls = {
        "a": (S.steam_cutter_hull(), S.STEAM_WEIGHTS, "steam_cutter_1888", "d2-001_a"),
        "b": (S.rowing_cutter_hull(), S.ROW_WEIGHTS, "rowing_cutter_25ft", "d2-002_b"),
        "c": (S.whaler_hull(), S.WHALER_WEIGHTS, "whaler_27ft", "d2-003_c"),
    }
    for k, (h, w, cls, code) in hulls.items():
        h, loaded, light = S.reconcile(h, w)
        sheet_lines(h, {"loaded": loaded, "light": light}, cls, code)


if __name__ == "__main__":
    main()

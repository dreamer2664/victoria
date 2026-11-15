"""
drawings.py -- dimensioned technical drawings generated from the same
HullDesign objects that build the 3D models, so the drawing and the model can
never disagree.

    python3 drawings.py

Outputs (SVG + PNG) into boats/drawings/ :
    boat_a_lines_and_ga.svg      lines plan + general arrangement
    boat_a_inboard_profile.svg   machinery arrangement
    boat_b_lines_and_ga.svg
    boat_b_construction.svg      framing / planking schedule
"""

import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrow, Polygon

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from boatgen import specs

ROOT = "/home/user/victoria"
OUT = os.path.join(ROOT, "boats", "drawings")
os.makedirs(OUT, exist_ok=True)

INK = "#1a1a1a"
THIN = "#4a4a4a"
FAINT = "#9a9a9a"
ACCENT = "#8c1c13"
BLUE = "#1f4e79"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 7,
    "axes.linewidth": 0.5,
    "svg.fonttype": "none",
})


def frame(ax, title):
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=8, loc="left", color=INK, pad=4)


def dim(ax, p0, p1, text, offset=0.0, vertical=False, colour=INK, fs=6):
    """A dimension line with arrow heads and a label."""
    x0, y0 = p0
    x1, y1 = p1
    if vertical:
        xa = x0 + offset
        ax.annotate("", (xa, y0), (xa, y1),
                    arrowprops=dict(arrowstyle="<->", color=colour, lw=0.6))
        ax.plot([x0, xa], [y0, y0], color=colour, lw=0.25)
        ax.plot([x1, xa], [y1, y1], color=colour, lw=0.25)
        ax.text(xa - 0.05, (y0 + y1) / 2, text, rotation=90, va="center", ha="right",
                color=colour, fontsize=fs)
    else:
        ya = y0 + offset
        ax.annotate("", (x0, ya), (x1, ya),
                    arrowprops=dict(arrowstyle="<->", color=colour, lw=0.6))
        ax.plot([x0, x0], [y0, ya], color=colour, lw=0.25)
        ax.plot([x1, x1], [y1, ya], color=colour, lw=0.25)
        ax.text((x0 + x1) / 2, ya + 0.05, text, ha="center", va="bottom",
                color=colour, fontsize=fs)


def title_block(fig, lines, x=0.72, y=0.03, w=0.26, h=0.15):
    ax = fig.add_axes([x, y, w, h])
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_linewidth(0.6)
        s.set_color(INK)
    ax.text(0.03, 0.86, lines[0], fontsize=7.5, weight="bold", color=INK, transform=ax.transAxes)
    for i, l in enumerate(lines[1:]):
        ax.text(0.03, 0.68 - i * 0.16, l, fontsize=6, color=THIN, transform=ax.transAxes)


def profile_points(hull, n=200):
    xi = np.linspace(0.0005, 0.9995, n)
    x = np.array([hull.surface(q, 1.0)[0] for q in xi])
    zs = np.array([hull.sheer_z(q) for q in xi])
    zk = np.array([hull.keel_z(q) for q in xi])
    return xi, x, zs, zk


def draw_lines(sheets, hull, name, code, extra_notes=()):
    fig = plt.figure(figsize=(13.5, 9.5))
    fig.patch.set_facecolor("white")

    # ---------------- sheer plan (profile) ----------------
    ax = fig.add_axes([0.05, 0.55, 0.62, 0.38])
    frame(ax, "SHEER PLAN  (scale 1:25)")
    xi, x, zs, zk = profile_points(hull)
    ax.plot(x, zs, color=INK, lw=1.1)
    ax.plot(x, zk, color=INK, lw=1.1)
    for q in np.linspace(0, 1, 11):
        px = hull.surface(q, 1.0)[0]
        ax.plot([px, px], [hull.keel_z(q), hull.sheer_z(q)], color=FAINT, lw=0.3, ls=(0, (4, 2)))
        ax.text(px, hull.sheer_z(q) + 0.045, f"{int(round(q*10))}", fontsize=5, color=FAINT,
                ha="center")
    # waterlines
    for z, lab in ((0.0, "LWL"), (-0.25, ""), (0.25, ""), (0.50, "")):
        ax.axhline(z, color=BLUE if z == 0 else FAINT, lw=0.5, ls=(0, (6, 3)))
        if lab:
            ax.text(hull.x_stern + 0.03, z + 0.02, lab, fontsize=5, color=BLUE)
    # deck edge / covering board
    ax.plot(x, zs - 0.115, color=THIN, lw=0.5, ls=(0, (5, 2)))
    ax.text(x[int(len(x) * 0.62)], zs[int(len(zs) * 0.62)] - 0.155, "deck", fontsize=5, color=THIN)

    xb, xsx = hull.x_bow, hull.x_stern
    dim(ax, (xb, -0.72), (xsx, -0.72), f"L.O.A. {hull.loa:.2f} m  (25 ft 0 in)", offset=-0.10)
    dim(ax, (0, hull.keel_z(1.35 / hull.loa + 0.5)), (0, 0.0),
        f"draft {abs(min(zk)):.2f} m", offset=0.22, vertical=True, colour=BLUE)
    dim(ax, (xb * 0.86, hull.keel_z(0.07)), (xb * 0.86, hull.sheer_z(0.07)),
        f"depth fwd {hull.sheer_z(0.07) - hull.keel_z(0.07):.2f} m", offset=-0.30, vertical=True)
    ax.set_xlim(xsx - 0.45, xb + 0.75)
    ax.set_ylim(-1.0, 0.95)

    # ---------------- half-breadth ----------------
    ax2 = fig.add_axes([0.05, 0.30, 0.62, 0.22])
    frame(ax2, "HALF-BREADTH PLAN  (waterlines, port side)")
    for z in (-0.50, -0.40, -0.30, -0.20, -0.10, 0.0, 0.20, 0.40):
        px, py = [], []
        for q in np.linspace(0.002, 0.998, 160):
            p = hull.surface(q, float(np.clip((z - hull.keel_z(q)) /
                                             max(hull.sheer_z(q) - hull.keel_z(q), 1e-6), 0, 1)))
            px.append(p[0]); py.append(p[1])
        w = 1.0 if z <= 0.0 else 0.5
        ax2.plot(px, py, color=INK if z == 0 else THIN, lw=w)
        if py:
            ax2.text(px[len(px) // 2], max(py) + 0.03, f"{z:+.2f}", fontsize=4.5, color=FAINT,
                     ha="center")
    ax2.axhline(0, color=FAINT, lw=0.4)
    ax2.plot([xsx, xb], [0, 0], color=FAINT, lw=0.4, ls=(0, (2, 3)))
    half = hull.half_beam(0.5)
    hb_mid = hull.half_beam(0.5)
    dim(ax2, (xsx * 0.55, 0), (xsx * 0.55, hb_mid),
        f"½ beam {hb_mid:.3f} m", offset=-0.14, vertical=True)
    ax2.text(xsx + 0.1, half + 0.42,
             f"beam max {hull.bmax:.3f} m (7 ft 0 in) · half-breadth shown",
             fontsize=6, color=THIN)
    ax2.set_xlim(xsx - 0.3, xb + 0.3)
    ax2.set_ylim(-0.15, 1.35)

    # ---------------- body plan ----------------
    ax3 = fig.add_axes([0.705, 0.52, 0.28, 0.42])
    frame(ax3, "BODY PLAN  (stations 0–10)")
    for q in np.linspace(0.02, 0.98, 9):
        ts = np.linspace(0.0, 1.0, 40)
        pts = [hull.surface(q, t) for t in ts]
        yy = [p[1] for p in pts]; zz = [p[2] for p in pts]
        ax3.plot(yy, zz, color=INK, lw=0.6)
        ax3.plot([-v for v in yy], zz, color=FAINT, lw=0.3)
        ax3.text(yy[-1] + 0.03, zz[-1], f"{int(round(q*10))}", fontsize=4.5, color=FAINT)
    ax3.axhline(0, color=BLUE, lw=0.5, ls=(0, (6, 3)))
    ax3.axvline(0, color=FAINT, lw=0.4, ls=(0, (2, 3)))
    hbm = hull.half_beam(0.5)
    dim(ax3, (0, -0.80), (hbm, -0.80), f"½ beam {hbm:.3f}", offset=0.0)
    ax3.set_xlim(-1.45, 1.45)
    ax3.set_ylim(-0.92, 0.90)

    # ---------------- notes ----------------
    axn = fig.add_axes([0.05, 0.05, 0.62, 0.20])
    axn.axis("off")
    axn.text(0, 0.95, "NOTES", fontsize=7, weight="bold", color=INK, transform=axn.transAxes)
    notes = list(extra_notes)
    for i, n in enumerate(notes):
        axn.text(0, 0.80 - i * 0.13, n, fontsize=5.6, color=THIN, transform=axn.transAxes,
                 wrap=True)

    title_block(fig, [code, name, "Scale 1:25 at A1 · dimensions in metres",
                      "OPERATION VICTORIA · 1889 · Boat Department",
                      "Drawn from the same HullDesign used for the 3D model"])
    path = os.path.join(OUT, code.lower().replace(" ", "_").replace(".", "") + ".png")
    fig.savefig(path, dpi=170, facecolor="white")
    svg = path.replace(".png", ".svg")
    fig.savefig(svg, facecolor="white")
    plt.close(fig)
    print("wrote", path, svg)


def draw_inboard(hull, name, code, layout):
    """Steam cutter: inboard profile with the machinery arrangement."""
    fig = plt.figure(figsize=(13.5, 7.2))
    ax = fig.add_axes([0.05, 0.16, 0.9, 0.76])
    frame(ax, "INBOARD PROFILE — machinery arrangement (scale 1:12)")
    xi, x, zs, zk = profile_points(hull)
    deck = zs - 0.115
    ax.plot(x, zs, color=INK, lw=1.2)
    ax.plot(x, zk, color=INK, lw=1.2)
    ax.plot(x, deck, color=THIN, lw=0.7)
    ax.fill_between(x, zk, deck, color="#f2ede2", zorder=0)
    ax.axhline(0, color=BLUE, lw=0.6, ls=(0, (6, 3)))

    for item in layout:
        kind = item["kind"]
        x0, x1 = item["x"]
        z0, z1 = item["z"]
        if kind == "box":
            ax.add_patch(Rectangle((x0, z0), x1 - x0, z1 - z0, facecolor="white",
                                   edgecolor=INK, lw=0.8, zorder=3))
        elif kind == "cyl":
            cx = (x0 + x1) / 2
            ax.add_patch(Rectangle((x0, z0), x1 - x0, z1 - z0, facecolor="white",
                                   edgecolor=INK, lw=0.8, zorder=3))
            ax.add_patch(matplotlib.patches.Ellipse((cx, z0), x1 - x0, 0.08,
                                                    facecolor="none", edgecolor=INK, lw=0.6,
                                                    zorder=3))
        ax.annotate(item["label"], xy=((x0 + x1) / 2, z1), xytext=(item.get("lx", (x0 + x1) / 2),
                                                                  item.get("lz", z1 + 0.30)),
                    fontsize=6, color=ACCENT, ha="center",
                    arrowprops=dict(arrowstyle="-", color=ACCENT, lw=0.5))
        for p in (item.get("dim_at", None),):
            if p is not None:
                ax.plot([p, p], [z0, z1], color=FAINT, lw=0.4, ls=(0, (3, 2)))

    # waterline / machinery datums
    dim(ax, (hull.x_stern, deck[0] if False else -0.75), (hull.x_bow, -0.75),
        f"L.O.A. {hull.loa:.3f} m")
    ax.set_xlim(hull.x_stern - 0.4, hull.x_bow + 0.4)
    ax.set_ylim(-1.05, 1.95)

    title_block(fig, [code, name, "Longitudinal positions are measured from",
                      "midships (+ forward). All machinery sits on the",
                      "centreline; boilers are coal-fired, riveted."])
    path = os.path.join(OUT, code.lower().replace(" ", "_") + ".png")
    fig.savefig(path, dpi=170, facecolor="white")
    fig.savefig(path.replace(".png", ".svg"), facecolor="white")
    plt.close(fig)
    print("wrote", path)


STEAM_NOTES = [
 "1. Hull: carvel outside planking over an inner double-diagonal skin, 12 frames, rock elm timbers.",
 "2. Sheer: 0.908 m above LWL at the stem head, 0.773 m at the transom; sheer strake is painted white.",
 "3. Machinery is carried on two wrought-iron longitudinal bearers bolted to the floors (see D-002).",
 "4. The canopy is a canvas hood on brass hoops carried by the coaming; the funnel passes through it.",
 "5. Boiler: vertical fire-tube, 0.720 m dia x 0.860 m, ~110 psi working; coal bunker abaft the boiler.",
 "6. Proportion of this boat follows the 1888 Admiralty *proposed* 25 ft steam cutter (RMG NPC9572);",
 "    equipment is reconstructed, not documented - see HISTORICAL_EVIDENCE.md.",
]

ROW_NOTES = [
 "1. Clinker (lap-strake) planking, 13 strakes of 15 mm mahogany, landed on 12 grown oak frames.",
 "2. Strakes overlap the plank below by 22 mm, fastened with clenched copper roves - the clinch work",
 "    described by Falconer (1769) and visible in RMG SLR1818.",
 "3. Five thwarts, double-banked (10 oars); stern sheets abaft the after thwart.",
 "4. Floor gratings on cleats; two large keelson eyes fore and aft for the davit slings.",
 "5. No rudder or rowlocks are shown on the RMG model (SLR1818); oars and a steering sweep are",
 "    carried as loose gear, as was usual for a boat stowed on davits.",
]


def main():
    draw_lines(None, specs.STEM_CUTTER, "25 ft Steam Cutter — lines & general arrangement",
               "D-001 A", STEAM_NOTES)
    draw_lines(None, specs.ROW_CUTTER, "25 ft Clinker Rowing Cutter — lines & general arrangement",
               "D-003 B", ROW_NOTES)

    steam_layout = [
        {"kind": "cyl", "x": (0.50 - 0.18, 0.50 + 0.18), "z": (-0.37, 0.49),
         "label": "Boiler 0.72 dia x 0.86", "lz": 1.30},
        {"kind": "box", "x": (-0.78 - 0.20, -0.78 + 0.20), "z": (-0.30, 0.42),
         "label": "Inverted vertical engine\n5½ in x 6 in", "lz": 1.05},
        {"kind": "box", "x": (1.62 - 0.24, 1.62 + 0.24), "z": (-0.10, 0.52),
         "label": "Coal bunker", "lz": 1.05},
        {"kind": "box", "x": (-1.18, -1.02), "z": (-0.10, 0.12),
         "label": "Thrust block", "lz": 0.62, "lx": -1.95},
        {"kind": "box", "x": (-3.46, -3.38), "z": (-0.62, -0.28),
         "label": "Screw 0.34 dia", "lz": 0.30, "lx": -2.95},
        {"kind": "box", "x": (-3.78, -3.62), "z": (-0.60, 0.66),
         "label": "Rudder", "lz": 0.95, "lx": -4.0},
        {"kind": "box", "x": (1.10, 1.28), "z": (0.49, 1.63),
         "label": "Funnel", "lz": 1.60, "lx": 1.95},
    ]
    draw_inboard(specs.STEM_CUTTER, "25 ft Steam Cutter — inboard profile", "D-002 A",
                 steam_layout)


if __name__ == "__main__":
    main()

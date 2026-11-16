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
    def _ft_in(m):
        # round to whole inches *before* splitting, or 27 ft comes out as
        # "26 ft 12 in" at the floating-point boundary
        total_in = int(round(m / 0.0254))
        return f"{total_in // 12} ft {total_in % 12} in"
    dim(ax, (xb, -0.72), (xsx, -0.72),
        f"L.O.A. {hull.loa:.2f} m  ({_ft_in(hull.loa)})", offset=-0.10)
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
             f"beam max {hull.bmax * 2:.3f} m ({_ft_in(hull.bmax * 2)}) · half-breadth shown",
             fontsize=6, color=THIN)
    ax2.set_xlim(xsx - 0.3, xb + 0.3)
    ax2.set_ylim(-0.15, 1.35)

    # ---------------- body plan ----------------
    ax3 = fig.add_axes([0.705, 0.52, 0.28, 0.42])
    frame(ax3, "BODY PLAN  (stations 0–10)")
    # In a body plan a WATERLINE is a horizontal straight line (a plane of
    # constant z cuts every section at the same height) and a BUTTOCK is a
    # vertical one; only the sections are curves.  Drawing the waterlines as
    # curves looks plausible and is simply wrong.
    hbm = hull.half_beam(0.5)
    for z in (-0.30, -0.15, 0.0, 0.25, 0.50):
        col = BLUE if z == 0 else FAINT
        ax3.plot([-hbm, hbm], [z, z], color=col, lw=0.5 if z == 0 else 0.3,
                 ls=(0, (6, 3)) if z == 0 else (0, (1, 3)), zorder=1)
        ax3.text(hbm + 0.04, z, f"{z:+.2f}", fontsize=4.2, color=FAINT, va="center")
    for y in (0.2, 0.4, 0.6, 0.8):
        if y < hbm:
            ax3.plot([y, y], [-0.55, 0.62], color=FAINT, lw=0.25, ls=(0, (1, 3)), zorder=1)
            ax3.plot([-y, -y], [-0.55, 0.62], color=FAINT, lw=0.25, ls=(0, (1, 3)), zorder=1)
    for i, q in enumerate(np.linspace(0.02, 0.98, 9)):
        ts = np.linspace(0.0, 1.0, 48)
        pts = [hull.surface(q, t) for t in ts]
        yy = [p[1] for p in pts]; zz = [p[2] for p in pts]
        ax3.plot(yy, zz, color=INK, lw=0.7, zorder=2)
        ax3.plot([-v for v in yy], zz, color=THIN, lw=0.5, zorder=2)
        up = 0.055 if i % 2 == 0 else 0.115
        for sgn in (1, -1):
            ax3.plot([sgn * yy[-1], sgn * yy[-1]], [zz[-1], zz[-1] + up * 0.7],
                     color=FAINT, lw=0.3, zorder=2)
            ax3.text(sgn * yy[-1], zz[-1] + up, f"{int(round(q*10))}", fontsize=4.4,
                     color=FAINT, ha="center", va="bottom")
    ax3.axvline(0, color=FAINT, lw=0.4, ls=(0, (2, 3)))
    ax3.set_aspect("equal", adjustable="box")
    ax3.text(0.02, 0.02, "stations 0 (bow) – 10 (stern) · sections mirrored \u00b7 LWL in blue",
             transform=ax3.transAxes, fontsize=4.6, color=FAINT)
    dim(ax3, (0, -0.72), (hbm, -0.72), f"½ beam {hbm:.3f}", offset=0.0)
    ax3.set_xlim(-hbm - 0.24, hbm + 0.24)
    ax3.set_ylim(-0.80, 0.92)

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
        if kind == "line":
            (xa, za), (xb, zb) = item["from"], item["to"]
            ax.plot([xa, xb], [za, zb], color=INK, lw=0.9, ls=(0, (5, 2)), zorder=4)
            mx, mz = (xa + xb) / 2, (za + zb) / 2
            ax.annotate(item["label"], xy=(mx, mz),
                        xytext=(item.get("lx", mx), item.get("lz", mz + 0.34)),
                        fontsize=6, color=ACCENT, ha="center", zorder=8,
                        arrowprops=dict(arrowstyle="-", color=ACCENT, lw=0.5))
            continue
        x0, x1 = item["x"]
        z0, z1 = item["z"]
        if kind == "box":
            ax.add_patch(Rectangle((x0, z0), x1 - x0, z1 - z0, facecolor="white",
                                   edgecolor=INK, lw=0.8, zorder=3))
        elif kind == "cyl":
            cx = (x0 + x1) / 2
            # a riveted vertical boiler stands on legs, clear of the floor
            # plates so the ashpan can be drawn: drawing it as a rectangle from
            # the keel up makes it look like a solid block of iron
            leg = item.get("legs", 0.0)
            zb = z0 + leg
            ax.add_patch(Rectangle((x0, zb), x1 - x0, z1 - zb, facecolor="white",
                                   edgecolor=INK, lw=0.8, zorder=3))
            if leg > 0:
                for frac in (0.14, 0.86):
                    lx = x0 + (x1 - x0) * frac
                    ax.add_patch(Rectangle((lx - 0.016, z0), 0.032, leg, facecolor="white",
                                           edgecolor=INK, lw=0.7, zorder=3))
                # firehole door on the front face
                ax.add_patch(Rectangle((x0 + (x1 - x0) * 0.30, zb + leg * 0.4),
                                       (x1 - x0) * 0.40, 0.13, facecolor="white",
                                       edgecolor=INK, lw=0.6, zorder=4))
            ax.add_patch(matplotlib.patches.Ellipse((cx, z1), x1 - x0, 0.08,
                                                    facecolor="none", edgecolor=INK, lw=0.6,
                                                    zorder=4))
        ax.annotate(item["label"], xy=((x0 + x1) / 2, z1), xytext=(item.get("lx", (x0 + x1) / 2),
                                                                  item.get("lz", z1 + 0.30)),
                    fontsize=6, color=ACCENT, ha="center", zorder=8,
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


WHALER_NOTES = [
 "1. Double ended: pointed stem and pointed stern, no transom. 27 ft x 6 ft, clinker built,",
 "    nine strakes on 68 frames, wych elm, as the RN whaler type was built from the 1890s.",
 "2. Draught 1 ft 5 in with the drop keel raised; the load waterline drawn here is solved from",
 "    the weight table, not assumed, and lands within 5 mm of the documented figure.",
 "3. Five oars, single banked: three from the port side and two from the starboard. The",
 "    bowman's oar is a foot shorter than the other four.",
 "4. Standing-lug yawl rig: 16 ft 6 in mainmast, 13 ft mizzen, 15 ft 3 in main yard. Canvas is",
 "    carried furled and stopped along the yards, which is the stowed condition.",
 "5. Drop keel in a trunk amidships, worked by an iron plate head and handle; plate shown up.",
]


def spec_floor_z(hull):
    """Inside bottom of the hull amidships, as the model computes it."""
    return float(hull.inner(hull.xi_of(0.5), 0.02, 0.020)[2])


def main():
    draw_lines(None, specs.STEM_CUTTER, "25 ft Steam Cutter — lines & general arrangement",
               "D-001 A", STEAM_NOTES)
    draw_lines(None, specs.ROW_CUTTER, "25 ft Clinker Rowing Cutter — lines & general arrangement",
               "D-003 B", ROW_NOTES)
    draw_lines(None, specs.WHALER, "27 ft Double-ended Whaler — lines & general arrangement",
               "D-004 C", WHALER_NOTES)

    # the machinery layout comes from boatgen.layout, the same table the model
    # is built from: a drawing that disagrees with the model is a specification
    # that cannot be met, which is exactly what this sheet used to be
    from boatgen.layout import STEAM as L
    b, e, k = L["boiler"], L["engine"], L["bunker"]
    zf = spec_floor_z(specs.STEM_CUTTER)
    steam_layout = [
        {"kind": "cyl", "x": (b["x"] - b["r"], b["x"] + b["r"]),
         "z": (zf - 0.02, zf + 0.16 + b["h"]), "label": b["label"], "lz": 1.58,
         "lx": -0.55, "legs": 0.18},
        {"kind": "box", "x": (e["x"] - e["hx"], e["x"] + e["hx"]), "z": e["z"],
         "label": e["label"], "lz": 1.05},
        {"kind": "box", "x": (k["x"] - k["hx"], k["x"] + k["hx"]), "z": k["z"],
         "label": k["label"], "lz": 1.05},
        {"kind": "box", "x": L["thrust_block"]["x"], "z": L["thrust_block"]["z"],
         "label": L["thrust_block"]["label"], "lz": 0.62, "lx": -1.95},
        # the line of shafting: raked on purpose, see CONSTRUCTION_A §5
        {"kind": "line", "from": (e["x"] + e["hx"] * 0.2, e["z"][0] + 0.06),
         "to": (L["screw"]["x"] + 0.05, L["screw"]["z"]),
         "label": "line of shafting, 6.3° to the waterline,\nthrough the stern tube",
         "lx": -2.35, "lz": -0.72},
        {"kind": "box", "x": (L["screw"]["x"] + 0.04, L["screw"]["x"] + 0.06),
         "z": (L["screw"]["z"] - 0.17, L["screw"]["z"] + 0.17),
         "label": L["screw"]["label"], "lz": 0.30, "lx": -2.95},
        {"kind": "box", "x": L["rudder"]["x"], "z": L["rudder"]["z"],
         "label": L["rudder"]["label"], "lz": 0.95, "lx": -4.0},
        {"kind": "box", "x": (L["funnel"]["x"] - L["funnel"]["r"],
                             L["funnel"]["x"] + L["funnel"]["r"]),
         "z": (zf + 0.16 + b["h"] + 0.10, zf + 0.16 + b["h"] + 1.05),
         "label": L["funnel"]["label"], "lz": 1.60, "lx": 1.95},
    ]
    draw_inboard(specs.STEM_CUTTER, "25 ft Steam Cutter — inboard profile", "D-002 A",
                 steam_layout)


if __name__ == "__main__":
    main()

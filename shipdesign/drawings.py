"""Technical drawings generated from the parametric hull/spec.

Produces, as both PNG (300 dpi) and SVG:
    * lines plan  (sheer plan / half-breadth plan / body plan)
    * general arrangement profile (outline with funnels, masts, decks)
    * deck plans for every deck

Run:  python3 -m shipdesign.drawings
"""
from __future__ import annotations
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle, FancyArrow
from matplotlib.lines import Line2D

from .spec import SHIP, DECKS, DECK_Z, FUNNELS, MASTS, PALETTE
from . import layout
from .hull import HULL, HL, B, T, HB

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "drawings")
INK = "#1a1a1a"
BLUE = "#26456b"
RED = "#8d2b1e"

WATERLINES = [1.0, 2.0, 3.0, 4.0, 5.0, 6.5]
STATIONS = [-79, -74, -68, -62, -56, -50, -44, -38, -32, -26, -20, -14,
            -8, -2, 4, 10, 16, 22, 28, 34, 40, 46, 52, 58, 62, 66, 70,
            73, 76, 78.5, 80.5]


def _style(ax):
    ax.set_aspect("equal")
    ax.axis("off")
    for sp in ax.spines.values():
        sp.set_visible(False)


def _title_block(fig, title, subtitle, extra=""):
    fig.text(0.5, 0.965, title, ha="center", va="top", fontsize=15,
             family="serif", color=INK, weight="bold")
    fig.text(0.5, 0.935, subtitle, ha="center", va="top", fontsize=9.5,
             family="serif", color=INK)
    if extra:
        fig.text(0.5, 0.912, extra, ha="center", va="top", fontsize=8,
                 family="serif", style="italic", color="#444")


def _frame(ax, w, h):
    ax.add_patch(Rectangle((0, 0), w, h, fill=False, ec=INK, lw=1.4, zorder=20))


def lines_plan(path_prefix=os.path.join(OUT, "lines_plan")):
    os.makedirs(OUT, exist_ok=True)
    fig = plt.figure(figsize=(16.5, 12), dpi=200)
    fig.patch.set_facecolor("#f6f3ea")
    # ---------------------------------------------------------------- sheer
    ax1 = fig.add_axes([0.055, 0.40, 0.89, 0.45])
    _style(ax1)
    xs = np.linspace(-HL, HL, 700)
    zdeck = HULL.deck_z(xs); zkeel = HULL.keel_z(xs)
    ax1.plot(xs, zdeck, color=INK, lw=2.0, label="Sheer line (deck at side)")
    ax1.plot(xs, zkeel, color=INK, lw=2.0, label="Keel / profile line")
    ax1.fill_between(xs, zkeel, zdeck, color="#e9e3d2", zorder=0)
    for w in WATERLINES + [T]:
        ax1.plot([-79, 80.5], [w, w], color=BLUE, lw=0.55, ls=(0, (4, 2)))
    ax1.axhline(T, color=RED, lw=1.0)
    ax1.text(81.5, T + 0.10, "L.W.L. %.2f m" % T, fontsize=7, color=RED)
    # buttock lines (longitudinal vertical planes) in the sheer plan
    for yb in (2.0, 4.0, 6.0, 8.0):
        pts = []
        for x in xs[::3]:
            half = HULL.section(x)
            if not half:
                continue
            zs = [p[1] for p in half]; ys = [p[0] for p in half]
            if yb <= ys[-1]:
                pts.append((x, float(np.interp(yb, ys, zs))))
        if pts:
            p = np.array(pts)
            ax1.plot(p[:, 0], p[:, 1], color=BLUE, lw=0.45, alpha=0.7)
    # decks
    for key, name, z, ext in DECKS:
        x0, x1 = max(ext[0], -HL), min(ext[1], HL)
        ax1.plot([x0, x1], [z, z], color="#8a7a5a", lw=0.7)
        ax1.text(x1 + 0.6, z, name, fontsize=5.4, va="center", color="#6b5b3a")
    # funnels & masts in profile
    for f in FUNNELS:
        ax1.add_patch(Rectangle((f["x"] - f["dia"] / 2, 15.0),
                                f["dia"], f["top_z"] - 15.0,
                                fc="none", ec=INK, lw=1.0))
    for m in MASTS:
        x0 = m["x"] - 0.35
        ax1.plot([x0, x0], [11.0, 11.0 + m["height_m"] * 0.82], color=INK, lw=1.4)
        ax1.plot([m["x"], m["x"] + 6.0], [11.0 + m["height_m"] - 1.0,
                                          11.0 + m["height_m"] - 7.0],
                 color=INK, lw=0.5)
    ax1.set_xlim(-96, 100); ax1.set_ylim(-4.5, 46)
    ax1.text(-94, 45.0, "SHEER PLAN  (profile)", fontsize=9.5, family="serif",
             weight="bold", color=INK, va="top")
    ax1.text(-94, -2.4, "L.O.A. %.1f m      L.B.P. %.1f m      Beam %.1f m      "
                        "Draught %.2f m" % (SHIP["loa"], SHIP["lbp"], SHIP["beam"], T),
             fontsize=7, color="#444")
    _frame(ax1, 196, 50.5)

    # --------------------------------------------------------- half-breadth
    ax2 = fig.add_axes([0.055, 0.075, 0.89, 0.28])
    _style(ax2)
    n = 500
    for w in WATERLINES:
        xs2 = np.linspace(-82, 82, n)
        ys = np.array([HULL.half_beam_at(x, w) for x in xs2])
        ax2.plot(xs2, ys, color=BLUE, lw=0.65)
        if ys.max() > 0.2:
            i = int(np.argmax(ys > 0.15))
            ax2.text(xs2[max(0, i - 6)], ys[max(0, i - 6)] + 0.22,
                     "W.L. %d" % int(w), fontsize=5.6, color=BLUE)
    # deck edge
    xs3 = np.linspace(-HL, HL, n)
    ax2.plot(xs3, HULL.beam_deck(xs3), color=INK, lw=1.6, label="Deck at side")
    ax2.axhline(0, color=INK, lw=0.8)
    ax2.set_xlim(-96, 100); ax2.set_ylim(-1.0, 11.6)
    ax2.text(-94, 11.2, "HALF-BREADTH PLAN  (1/2 of each waterline about centreline)",
             fontsize=9.5, family="serif", weight="bold", color=INK, va="top")
    _frame(ax2, 196, 12.6)

    # ------------------------------------------------------------ body plan
    ax3 = fig.add_axes([0.055, 0.005, 0.42, 0.065])
    # plot in the same figure via inset coordinates: use separate fig instead
    ax3.remove()

    fig.savefig(path_prefix + ".png", facecolor=fig.get_facecolor())
    fig.savefig(path_prefix + ".svg", facecolor=fig.get_facecolor())
    plt.close(fig)

    # --- body plan on its own sheet (period practice: separate plate) -----
    fig2 = plt.figure(figsize=(9, 12), dpi=200)
    fig2.patch.set_facecolor("#f6f3ea")
    axb = fig2.add_axes([0.10, 0.05, 0.80, 0.86])
    _style(axb)
    for x in STATIONS:
        half = HULL.section(x)
        if not half:
            continue
        p = np.array([(y, z) for y, z in half])
        colour = BLUE if x >= 0 else RED
        axb.plot(p[:, 0], p[:, 1], color=colour, lw=0.8)
        axb.plot(-p[:, 0], p[:, 1], color=colour, lw=0.8)
    axb.axhline(0, color=INK, lw=1.0)
    axb.axvline(0, color=INK, lw=1.0)
    for w in WATERLINES + [T]:
        axb.axhline(w, color="#999", lw=0.35, ls=(0, (3, 3)))
    axb.axvline(HB, color="#999", lw=0.35, ls=(0, (3, 3)))
    axb.axvline(-HB, color="#999", lw=0.35, ls=(0, (3, 3)))
    axb.set_xlim(-11.5, 11.5); axb.set_ylim(-1.6, 12.4)
    axb.text(0, 12.1, "BODY PLAN", ha="center", fontsize=12, family="serif",
             weight="bold")
    axb.text(0, 11.6, "Fore body (blue) to starboard, after body (red) to port",
             ha="center", fontsize=7, style="italic")
    axb.text(9.4, T + 0.12, "W.L.", fontsize=6, color=RED)
    for lab, x, y in (("+", 9.2, -0.9), ("-", -9.2, -0.9)):
        axb.text(x, y, lab, fontsize=9, ha="center")
    fig2.savefig(os.path.join(OUT, "body_plan.png"), facecolor=fig2.get_facecolor())
    fig2.savefig(os.path.join(OUT, "body_plan.svg"), facecolor=fig2.get_facecolor())
    plt.close(fig2)
    return path_prefix + ".png"


def _deck_outline(ax, z, clip_x=None, colour=INK, lw=1.4):
    """Draw the hull outline at a given deck height (plan view)."""
    xs = np.linspace(-82, 82, 400)
    ys = np.array([HULL.half_beam_at(x, z) for x in xs])
    if clip_x:
        m = (xs >= clip_x[0]) & (xs <= clip_x[1])
        xs, ys = xs[m], ys[m]
    good = ys > 0.05
    if not good.any():
        return
    xs, ys = xs[good], ys[good]
    ax.plot(xs, ys, color=colour, lw=lw)
    ax.plot(xs, -ys, color=colour, lw=lw)
    ax.plot([xs[0], xs[-1]], [0, 0], color=colour, lw=0.6, ls=":")


def general_arrangement(path=os.path.join(OUT, "general_arrangement.png")):
    fig = plt.figure(figsize=(20, 8.5), dpi=200)
    fig.patch.set_facecolor("#f6f3ea")
    ax = fig.add_axes([0.03, 0.10, 0.94, 0.78])
    _style(ax)
    xs = np.linspace(-HL, HL, 700)
    ax.plot(xs, HULL.deck_z(xs), color=INK, lw=2.2)
    ax.plot(xs, HULL.keel_z(xs), color=INK, lw=2.2)
    # waterline
    ax.plot([-85, 85], [T, T], color=RED, lw=1.0)
    ax.fill_between(xs, HULL.keel_z(xs), np.minimum(HULL.deck_z(xs), T),
                    color="#2b2b2b", alpha=0.92)
    ax.fill_between(xs, np.minimum(HULL.deck_z(xs), T), HULL.deck_z(xs),
                    color="#e9e3d2")
    # superstructure blocks
    from .spec import ZONES
    # superstructure: the promenade deck house sits ON the main-deck house,
    # which itself sits on the hull.  Two tiers, then the bridge.
    # Houses drawn with their sloped sides so the silhouette matches the
    # 3-D model (the promenade house narrows with the ship's side).
    def taper_block(x0, x1, z0, z1, inset0, inset1, lab, colr="#efe8d6"):
        pts = []
        n = 40
        for i in range(n + 1):
            x = x0 + (x1 - x0) * i / n
            pts.append((x, max(HULL.half_beam_at(x, z0) - inset0, 0.2)))
        for i in range(n, -1, -1):
            x = x0 + (x1 - x0) * i / n
            pts.append((x, max(HULL.half_beam_at(x, z1) - inset1, 0.2)))
        top = [(p[0], z1) for p in pts[:n + 1]]
        bot = [(p[0], z0) for p in pts[n + 1:]]
        ax.add_patch(Polygon(bot + top, closed=True, fc=colr, ec=INK, lw=1.0))
        ax.text((x0 + x1) / 2, (z0 + z1) / 2, lab, ha="center", va="center",
                fontsize=5.2, color="#6b5b3a")

    taper_block(-60.0, 54.0, 9.0, 14.40, 0.62, 0.62, "SALOON-DECK HOUSE")
    taper_block(-62.0, 56.0, 14.40, 16.60, 0.30, 0.30, "PROMENADE DECK")
    taper_block(-44.0, 40.0, 16.60, 17.80, 0.40, 0.40, "BOAT DECK")
    ax.add_patch(Rectangle((10.0, 17.80), 20.0, 2.6, fc="#efe8d6", ec=INK,
                           lw=1.0))
    ax.text(20.0, 19.1, "BRIDGE", ha="center", va="center", fontsize=5.2,
            color="#6b5b3a")
    # funnels
    for f in FUNNELS:
        ax.add_patch(Rectangle((f["x"] - f["dia"] / 2, 16.6), f["dia"],
                               f["top_z"] - 16.6, fc="#d9c9a3", ec=INK, lw=1.0))
        ax.add_patch(Rectangle((f["x"] - f["dia"] / 2, f["top_z"] - 2.2),
                               f["dia"], 2.2, fc="#222", ec=INK, lw=1.0))
    # masts + rigging
    for m in MASTS:
        top = 10.5 + m["height_m"]
        ax.plot([m["x"], m["x"]], [10.5, top], color=INK, lw=2.0)
        # shrouds down to the deck edge
        for dx in (-2.6, -1.7, 1.7, 2.6):
            ax.plot([m["x"], m["x"] + dx], [top - 1.4, 14.6],
                    color=INK, lw=0.35, alpha=0.8)
        ax.plot([m["x"], m["x"] + 5.5], [top - 1.2, top - 6.4], color=INK, lw=0.5)
    # lifeboats on boat deck
    from .spec import STARBOARD_BOATS, PORT_BOATS
    for x, kind in STARBOARD_BOATS + PORT_BOATS:
        ax.add_patch(Polygon([(x - 4, 17.9), (x + 4, 17.9), (x + 3.4, 18.7),
                              (x - 3.4, 18.7)], closed=True, fc="#cfd6cf",
                             ec=INK, lw=0.8))
    # deck lines
    for key, name, z, ext in DECKS:
        ax.plot([ext[0], ext[1]], [z, z], color="#9a8a6a", lw=0.6)
    ax.set_xlim(-92, 92); ax.set_ylim(-3.5, 40)
    ax.text(-90, 39.2, "SS “AURELIAN” — GENERAL ARRANGEMENT, PROFILE",
            fontsize=11, family="serif", weight="bold")
    ax.text(-90, 37.6, "Albion & Western Steam Navigation Co. — Birkenhead 1889 — "
                       "scale 1:200", fontsize=7, style="italic")
    # scale bar
    ax.plot([60, 80], [-2.4, -2.4], color=INK, lw=1.2)
    for xx in (60, 70, 80):
        ax.plot([xx, xx], [-2.7, -2.1], color=INK, lw=0.9)
    ax.text(70, -3.2, "0        10        20 m", fontsize=6, ha="center")
    fig.savefig(path, facecolor=fig.get_facecolor())
    fig.savefig(path.replace(".png", ".svg"), facecolor=fig.get_facecolor())
    plt.close(fig)
    return path


DECK_PLANS = {
    "main":  (8.60, [("Dining Saloon (1st cl.)", -52, -14),
                     ("Grand Staircase", -2, 10),
                     ("Pantry", -58, -52),
                     ("Third-class dining", -46, -28),
                     ("2nd class entering vestibule", -66, -58)]),
    "upper": (11.40, [("Dining Saloon 2nd cl.", -64, -50),
                      ("Galley", -74, -66),
                      ("Lobby / staircase", -2, 10),
                      ("Staterooms 1st cl.", 12, 48),
                      ("Staterooms 1st cl. (aft)", -44, -20)]),
    "prom":  (13.60, [("Library", -6, 14), ("Music Room", 16, 30),
                      ("Smoking Saloon (1st)", -34, -18),
                      ("Ladies' Drawing Room", -14, -4),
                      ("Barber", -40, -34), ("2nd cl. smoke room", -66, -54)]),
    "boat":  (15.40, [("Officers", 36, 42), ("Boat stowage", 22, 42),
                      ("Skylight", -6, 6), ("Boat stowage aft", -40, -20)]),
}


DECK_TITLES = {
    "bottom":  "HOLD / TANK TOP",
    "orlop":   "ORLOP DECK",
    "main":    "MAIN DECK",
    "saloon":  "UPPER (SALOON) DECK",
    "prom":    "PROMENADE DECK",
    "boat":    "BOAT DECK",
    "bridge":  "BRIDGE DECK",
}


def _wrapped(label, max_chars=22, max_lines=3):
    """Break a room name into at most three short lines, for the plan."""
    words = label.replace("&", "&").split()
    lines, cur = [], ""
    for w in words:
        if len(cur) + len(w) + 1 > max_chars and cur:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(cur)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1][:max_chars - 1] + "\u2026"
    return "\n".join(lines)


def _fit_fontsize(poly, label, base=6.4):
    """Shrink the label so it fits inside its room box on the plan."""
    xs = [p[0] for p in poly]; ys = [p[1] for p in poly]
    w = max(xs) - min(xs)
    h = max(ys) - min(ys)
    # 1 m of x is about 0.033 in on a 18 in sheet over 176 m
    lines = label.count("\n") + 1
    by_h = h / (lines * 2.4 + 1.0) * 6.0
    by_w = (w / (max(len(l) for l in label.split("\n")) * 0.52)) * 5.4
    return max(2.6, min(base, by_h, by_w))


def deck_plans():
    """One drawing sheet per deck: outline to scale, rooms, labels, dimensions.

    The earlier version drew the whole 176 m ship into a 4.9 in strip, so the
    plan occupied an eighth of the page and every label collided.  Each sheet
    now fills its page, uses the full plan height, places labels with an
    automatic size fit, and carries a dimension line, a scale bar and a north
    (forward) arrow.
    """
    made = []
    plan = {}
    for key, name, z, ext in layout.DECKS:
        plan[key] = (z, ext, [(r["name"], layout.room_polygon(r))
                              for r in layout.rooms_on(key)])
    for key, (z, ext, rooms) in plan.items():
        fig = plt.figure(figsize=(22, 9.0), dpi=170)
        fig.patch.set_facecolor("#f6f3ea")
        ax = fig.add_axes([0.035, 0.085, 0.93, 0.80])
        _style(ax)
        # the deck itself: the plan extent of the ship at this level
        x0, x1 = ext
        xs = np.linspace(x0, x1, 500)
        ys = np.array([layout.hull_side_halfbeam(x, z) for x in xs], dtype=float)
        good = ys > 0.05
        if good.any():
            xg, yg = xs[good], ys[good]
            ax.fill(np.concatenate([xg, xg[::-1]]),
                    np.concatenate([yg, -yg[::-1]]),
                    fc="#e8e0cb", ec=INK, lw=1.6, zorder=1)
        for lab, poly in rooms:
            if not poly:
                continue
            ax.add_patch(Polygon(poly, closed=True, fc="#f7f2e4",
                                 ec="#6b5c40", lw=1.0, zorder=2))
            cx = sum(p[0] for p in poly) / len(poly)
            cy = sum(p[1] for p in poly) / len(poly)
            txt = _wrapped(lab)
            ax.text(cx, cy, txt, ha="center", va="center",
                    fontsize=_fit_fontsize(poly, txt), zorder=3,
                    linespacing=1.15)
        # centreline + frame marks every 10 stations (9.144 m)
        ax.axhline(0, color="#b09865", lw=0.5, ls=(0, (6, 3, 1, 3)), zorder=4)
        for fx in range(-80, 81, 20):
            if x0 <= fx <= x1:
                ax.plot([fx, fx], [-1.6, 1.6], color="#9c8a63", lw=0.5, zorder=4)
        ax.set_xlim(x0 - 5, x1 + 5)
        ax.set_ylim(-12.2, 16.4)
        ax.set_aspect("equal")
        ax.set_xticks(np.arange(-80, 81, 20))
        ax.set_yticks([-9, -6, -3, 0, 3, 6, 9])
        ax.tick_params(labelsize=7)
        ax.set_xlabel("distance from amidships (m)   + forward", fontsize=8)
        ax.set_ylabel("half breadth (m)", fontsize=8)
        # title block
        ax.text(x0, 15.8, "SS AURELIAN  —  %s" % DECK_TITLES.get(key, key.upper()),
                fontsize=16, family="serif", weight="bold", va="top")
        ax.text(x0, 14.4, "Deck at %.2f m above base line   ·   extent %.1f to %.1f m"
                "   ·   all dimensions in metres" % (z, x0, x1),
                fontsize=8.5, style="italic", va="top")
        ax.text(x1, 15.8, "SHEET %s/9" % (list(plan).index(key) + 3),
                fontsize=9, ha="right", family="serif", va="top")
        # graphic scale bar: 20 m
        bar_x, bar_y = x1 - 26, -10.9
        ax.plot([bar_x, bar_x + 20], [bar_y, bar_y], color=INK, lw=2.0,
                solid_capstyle="butt")
        for t in (0, 10, 20):
            ax.plot([bar_x + t, bar_x + t], [bar_y - 0.35, bar_y + 0.35],
                    color=INK, lw=1.0)
        ax.text(bar_x + 10, bar_y - 1.4, "20 m", ha="center", fontsize=7)
        # forward arrow
        ax.annotate("", xy=(x1 - 3, 13.0), xytext=(x1 - 15, 13.0),
                    arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.4))
        ax.text(x1 - 9, 13.5, "FORWARD", ha="center", fontsize=7.5,
                family="serif")
        p = os.path.join(OUT, "deck_%s.png" % key)
        fig.savefig(p, facecolor=fig.get_facecolor())
        fig.savefig(p.replace(".png", ".svg"), facecolor=fig.get_facecolor())
        plt.close(fig)
        made.append(p)
    return made


def run_all():
    os.makedirs(OUT, exist_ok=True)
    a = lines_plan()
    b = general_arrangement()
    c = deck_plans()
    return [a, b] + c


if __name__ == "__main__":
    for p in run_all():
        print("wrote", p)

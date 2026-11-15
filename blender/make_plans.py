#!/usr/bin/env python3
"""
make_plans.py -- draws the measured port layout plans.

The plans are generated from the same layout data the geometry comes from, so they
cannot drift out of step with the model: every footprint here is the footprint the
auditor checked for overlaps, and every berth rectangle is the rectangle the
clearance rule was applied to.

    blender -b --factory-startup -noaudio --python blender/make_plans.py

Writes docs/port_a_plan.svg and docs/port_b_plan.svg.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HERE, "lib"))
sys.path.insert(0, os.path.join(HERE, "ports"))
sys.path.insert(0, HERE)

import bpy
import bsetup
import portsite as site

PAPER = "#f7f4ec"
INK = "#1d1d1b"
MUT = "#7d786d"
WATER = "#c9d6d8"
LAND = "#e7e1d2"
BLDG = "#b9a88c"
BLDG_E = "#6b5c48"
BERTH = "#b8863f"
CRANE = "#4d6b58"


def _rects(v):
    """meta 'water' values are either a single rect or a list of rects."""
    if not v:
        return []
    if isinstance(v[0], (int, float)):
        return [tuple(v)]
    return [tuple(r) for r in v]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def plan(port, meta, audit, out_path, size=1700):
    """Draw the port plan as an SVG: north up, bow right (the RMG plan convention)."""
    items = audit.items
    berths = audit.berths

    site = meta["site"]
    # The drawing extent is the site plus a generous margin of water, NOT the full
    # river rectangle (which is deliberately oversized so it never shows an edge).
    MARGIN = 150
    x0, x1 = site[0] - MARGIN, site[2] + MARGIN
    y0, y1 = site[1] - MARGIN, site[3] + MARGIN

    span_x, span_y = x1 - x0, y1 - y0
    scale = min((size - 190) / span_x, (size - 190) / span_y)
    width = span_x * scale + 190
    height = span_y * scale + 190

    L, T = 120.0, 118.0          # left / top margins in px

    def px(x):
        return L + (x - x0) * scale

    def py(y):
        return T + (y1 - y) * scale          # north up

    def clip_rect(r):
        a, b, c, d = min(r[0], r[2]), min(r[1], r[3]), max(r[0], r[2]), max(r[1], r[3])
        a, c = max(a, x0), min(c, x1)
        b, d = max(b, y0), min(d, y1)
        if c <= a or d <= b:
            return None
        return (a, b, c, d)

    def rect(r, fill, stroke=None, sw=0.8, op=1.0, dash=None):
        r = clip_rect(r)
        if r is None:
            return ""
        a, b, c, d = r
        st = ' stroke="%s" stroke-width="%s"' % (stroke, sw) if stroke else ' stroke="none"'
        da = ' stroke-dasharray="%s"' % dash if dash else ""
        return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s"%s '
                'opacity="%.2f"%s/>'
                % (px(a), py(d), (c - a) * scale, (d - b) * scale, fill, st, op, da))

    def label(x, y, text, size_px=9.5, fill="#3a3227", anchor="middle", weight="normal"):
        return ('<text x="%.1f" y="%.1f" font-size="%s" fill="%s" text-anchor="%s" '
                'font-weight="%s" stroke="#f7f4ec" stroke-width="2.4" paint-order="stroke">'
                '%s</text>' % (px(x), py(y), size_px, fill, anchor, weight, esc(text)))

    out = []
    out.append('<?xml version="1.0" encoding="UTF-8"?>')
    out.append('<svg xmlns="http://www.w3.org/2000/svg" width="%.0f" height="%.0f" '
               'viewBox="0 0 %.0f %.0f" font-family="Georgia,serif">' % (width, height, width, height))
    out.append('<defs><clipPath id="frame"><rect x="%.0f" y="%.0f" width="%.0f" '
               'height="%.0f"/></clipPath></defs>'
               % (L - 6, T - 6, (x1 - x0) * scale + 12, (y1 - y0) * scale + 12))
    out.append('<rect width="100%%" height="100%%" fill="%s"/>' % PAPER)
    out.append('<g clip-path="url(#frame)">')

    # 1. land mass first -- water bodies are HOLES in it, so they must be drawn
    #    over the land slab or the slab would hide every inland dock basin.
    out.append(rect(site, LAND, MUT, 1.1))

    # 2. water (river + every inland basin cut out of the site)
    for k, v in meta.get("water", {}).items():
        for r in _rects(v):
            out.append(rect(r, WATER))

    # 3. graving docks + building slips (cut into the land, so drawn on top of it)
    for d in meta.get("graving_docks", []):
        if d.get("rect"):
            out.append(rect(d["rect"], "#b3a68b", "#5f513c", 1.3))
            cx = (d["rect"][0] + d["rect"][2]) / 2
            cy = (d["rect"][1] + d["rect"][3]) / 2
            out.append(label(cx, cy, "%s  %s" % (d["id"], d["name"]), 9.0, "#4a3f2e"))
    for sl in meta.get("slips", []):
        if sl.get("rect"):
            out.append(rect(sl["rect"], "#d6cbb2", "#6b5c48", 1.0))

    # 4. berth envelopes
    for (name, a, b, c, d, depth) in berths:
        out.append(rect((a, b, c, d), BERTH, BERTH, 1.7, 0.13, dash="8 4"))
        out.append(label((a + c) / 2, (b + d) / 2, name, 10.0, "#8a5f20", weight="bold"))

    # 5. building footprints
    for (name, a, b, c, d, kind) in items:
        out.append(rect((a, b, c, d), BLDG, BLDG_E, 0.9))
        t = name if len(name) <= 20 else name[:19] + "\u2026"
        out.append(label((a + c) / 2, (b + d) / 2, t, 8.4))

    # 6. interaction points
    for it in meta.get("interactions", []):
        cx, cy = px(it["pos"][0]), py(it["pos"][1])
        out.append('<circle cx="%.1f" cy="%.1f" r="9" fill="none" stroke="%s" '
                   'stroke-width="1"/>' % (cx, cy, CRANE))
        out.append('<circle cx="%.1f" cy="%.1f" r="4.2" fill="%s"/>' % (cx, cy, CRANE))

    out.append("</g>")

    # ---- title block
    site_w = site[2] - site[0]
    site_h = site[3] - site[1]
    out.append('<g>')
    out.append('<text x="24" y="42" font-size="22" letter-spacing="1.6" fill="%s">%s</text>'
               % (INK, esc(meta["port"])))
    out.append('<text x="24" y="62" font-size="11.5" fill="%s">LAYOUT PLAN &#183; measured '
               'in metres &#183; north up &#183; 1 Roblox stud = 0.28 m</text>' % MUT)
    out.append('<text x="24" y="82" font-size="10.5" fill="%s">site %.0f &#215; %.0f m '
               '&#183; %d building footprints &#183; %d berths &#183; %d interaction points '
               '&#183; coping +%.2f m</text>'
               % (MUT, site_w, site_h, len(items), len(berths),
                  len(meta.get("interactions", [])), meta["quay_z"]))
    out.append('</g>')

    # ---- legend
    lx, ly = 26, height - 108
    out.append('<g font-size="10" fill="%s">' % INK)
    entries = [("berth envelope", BERTH, "box"), ("building footprint", BLDG, "box"),
               ("water", WATER, "box"), ("graving dock", "#b3a68b", "box"),
               ("interaction point", CRANE, "dot")]
    for i, (text, col, kind) in enumerate(entries):
        yy = ly + i * 17
        if kind == "dot":
            out.append('<circle cx="%d" cy="%d" r="5" fill="%s"/>' % (lx + 13, yy - 3, col))
        else:
            out.append('<rect x="%d" y="%d" width="26" height="11" fill="%s" stroke="%s" '
                       'stroke-width="0.9"/>' % (lx, yy - 10, col, BLDG_E))
        out.append('<text x="%d" y="%d">%s</text>' % (lx + 40, yy, text))
    out.append('</g>')

    # ---- scale bar and north arrow
    bx, by = width - 285, height - 40
    out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2"/>'
               % (bx, by, bx + 100 * scale, by, INK))
    out.append('<text x="%.1f" y="%.1f" font-size="10" fill="%s">100 m</text>'
               % (bx + 100 * scale + 8, by + 4, MUT))
    out.append('<g transform="translate(%.1f,44)"><path d="M0,-25 L8,4 L0,-2 L-8,4 Z" '
               'fill="%s"/><text x="0" y="22" font-size="10" text-anchor="middle" '
               'fill="%s">N</text></g>' % (width - 44, INK, MUT))

    out.append("</svg>")
    open(out_path, "w", encoding="utf-8").write("\n".join(out))
    print("wrote", out_path, "%.0f x %.0f px" % (width, height))


def main():
    import build_ports as BP
    for port, modname in (("a", "port_a"), ("b", "port_b")):
        sc = bsetup.reset_scene()
        bsetup.make_materials()
        coll = bsetup.ensure_coll("PLAN")
        R = bsetup.Registry()
        audit = site.LayoutAuditor()
        mod = __import__(modname)
        meta = mod.build(R, coll, audit)
        for b in meta.get("berths", []):
            r = b["rect"]
            audit.berth(b["id"] + " " + b["name"][:18], r[0], r[1], r[2], r[3], b["depth_m"])
        out = os.path.join(ROOT, "docs", "port_%s_plan.svg" % port)
        plan(port, meta, audit, out)
        # print the measured numbers for the written spec
        print("--", port, "site", meta["site"], "berths", len(meta["berths"]),
              "interactions", len(meta["interactions"]), "buildings", len(audit.items))


main()

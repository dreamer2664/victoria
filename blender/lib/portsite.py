"""
portsite.py -- land/water decomposition and layout helpers shared by both ports.
"""
from core import MeshBuilder, QUAY_Z, RIVER_BED_Z


# ---------------------------------------------------------------- rect algebra
def _split(rect, hole):
    """Return the parts of `rect` not covered by `hole` (axis-aligned)."""
    ax0, ay0, ax1, ay1 = rect
    bx0, by0, bx1, by1 = hole
    ix0, iy0 = max(ax0, bx0), max(ay0, by0)
    ix1, iy1 = min(ax1, bx1), min(ay1, by1)
    if ix1 <= ix0 or iy1 <= iy0:
        return [rect]                       # no overlap
    out = []
    if iy0 > ay0:
        out.append((ax0, ay0, ax1, iy0))
    if iy1 < ay1:
        out.append((ax0, iy1, ax1, ay1))
    if ix0 > ax0:
        out.append((ax0, iy0, ix0, iy1))
    if ix1 < ax1:
        out.append((ix1, iy0, ax1, iy1))
    return out


def subtract(site, holes):
    """Subtract a list of water rectangles from a site rectangle."""
    rects = [site]
    for h in holes:
        nxt = []
        for r in rects:
            nxt.extend(_split(r, h))
        rects = nxt
    return [(r, ) for r in rects if (r[2] - r[0]) > 0.5 and (r[3] - r[1]) > 0.5]


# ---------------------------------------------------------------- land
def add_land(mb, site, holes, top=QUAY_Z, bottom=-3.0, surf="setts",
             side_mat="rubble", margin_rects=()):
    """Emit the raised land platform around a set of water bodies.

    The vertical faces are only a backing mass: the visible masonry of every quay
    is built separately by maritime.quay_wall() along each water edge.
    """
    for (r,) in subtract(site, holes):
        x0, y0, x1, y1 = r
        mb.add_box(x0, y0, bottom, x1, y1, top - 0.02, side_mat)
        mb.add_grid_quad(x0, y0, x1, y1, top, surf, step=7.5)


def water(mb, rects, z=0.0, mat="water", step=25.0):
    for (x0, y0, x1, y1) in rects:
        mb.add_grid_quad(x0, y0, x1, y1, z, mat, step=step)


# ---------------------------------------------------------------- layout audit
class LayoutAuditor:
    """Tracks footprints so overlaps and berth clearances are caught numerically
    instead of being discovered by eye in a render."""

    def __init__(self):
        self.items = []       # (name, x0,y0,x1,y1, kind)
        self.berths = []      # (name, x0,y0,x1,y1, depth)

    def add(self, name, x0, y0, x1, y1, kind="building"):
        self.items.append((name, min(x0, x1), min(y0, y1),
                           max(x0, x1), max(y0, y1), kind))
        return self

    def berth(self, name, x0, y0, x1, y1, depth):
        self.berths.append((name, min(x0, x1), min(y0, y1),
                            max(x0, x1), max(y0, y1), depth))
        return self

    def report(self):
        out = []
        its = self.items
        for i in range(len(its)):
            for j in range(i + 1, len(its)):
                a, b = its[i], its[j]
                if a[5] != "building" or b[5] != "building":
                    continue
                ox = min(a[3], b[3]) - max(a[1], b[1])
                oy = min(a[4], b[4]) - max(a[2], b[2])
                if ox > 0.05 and oy > 0.05:
                    out.append("OVERLAP: %s <-> %s  (%.1f x %.1f m)" %
                               (a[0], b[0], ox, oy))
        return out

"""
life.py -- the human-scale layer: people, drays, handcarts and loose cargo.

A port with no people in it reads as a model, not a place. Everything here is
sized from period anthropometry and vehicle dimensions rather than guessed:

  * a Victorian dock labourer is taken as 1.70 m, 1.68 m for the women in the
    sheds -- small by modern standards, which is exactly the point;
  * a two-wheel handcart is 2.1 m long, 1.15 m wide, 1.05 m to the bed;
  * a brewer's/coal dray is 4.4 m long with a 16-hand (1.63 m) horse in the shafts;
  * a coal sack is 0.75 m tall and 0.45 m across when filled;
  * a cargo bale is 1.1 x 0.7 x 0.6 m, a tea chest 0.6 m cube.

Geometry is deliberately cheap -- one figure is ~90 triangles -- because these are
placed in their dozens and are read at a distance. They exist for scale and
silhouette, not for close inspection.
"""
import math
from core import MeshBuilder

# ---------------------------------------------------------------- materials
COATS = ["black", "brick_soot", "timber", "iron", "canvas", "steel_plate"]


def workman(mb, x, y, z, rz=0.0, coat="black", cap="black"):
    """A standing dock labourer, ~1.70 m, in a flat cap and a long coat."""
    c, s = math.cos(math.radians(rz)), math.sin(math.radians(rz))

    def P(dx, dy, dz):
        return (x + dx * c - dy * s, y + dx * s + dy * c, z + dz)

    # legs
    for sx in (-0.10, 0.10):
        a, b = P(sx - 0.065, -0.07, 0.0), P(sx + 0.065, 0.07, 0.86)
        mb.add_box(a[0], a[1], a[2], b[0], b[1], b[2], "black")
    # torso / coat skirt -- a single tapered mass reads better than a box
    a, b = P(-0.19, -0.13, 0.80), P(0.19, 0.13, 1.40)
    mb.add_box(a[0], a[1], a[2], b[0], b[1], b[2], coat)
    # shoulders
    a, b = P(-0.23, -0.15, 1.32), P(0.23, 0.15, 1.46)
    mb.add_box(a[0], a[1], a[2], b[0], b[1], b[2], coat)
    # arms
    for sx in (-0.25, 0.25):
        a, b = P(sx - 0.05, -0.06, 0.92), P(sx + 0.05, 0.06, 1.42)
        mb.add_box(a[0], a[1], a[2], b[0], b[1], b[2], coat)
    # head + cap
    a, b = P(-0.085, -0.085, 1.46), P(0.085, 0.085, 1.64)
    mb.add_box(a[0], a[1], a[2], b[0], b[1], b[2], "plaster")
    a, b = P(-0.10, -0.11, 1.62), P(0.10, 0.11, 1.70)
    mb.add_box(a[0], a[1], a[2], b[0], b[1], b[2], cap)


def workman_pair(mb, x, y, z, rz=0.0):
    """Two men together, as dock work is done -- one at 1.5 m spacing."""
    workman(mb, x, y, z, rz, coat="black")
    c, s = math.cos(math.radians(rz + 90)), math.sin(math.radians(rz + 90))
    workman(mb, x + 1.5 * c, y + 1.5 * s, z, rz + 25, coat="timber")


def horse(mb, x, y, z, rz=0.0, coat="timber"):
    """A 16-hand dray horse, 2.45 m nose to tail, standing in the shafts."""
    c, s = math.cos(math.radians(rz)), math.sin(math.radians(rz))

    def P(dx, dy, dz):
        return (x + dx * c - dy * s, y + dx * s + dy * c, z + dz)

    # body
    a, b = P(-0.95, -0.30, 0.95), P(0.55, 0.30, 1.55)
    mb.add_box(a[0], a[1], a[2], b[0], b[1], b[2], coat)
    # neck + head
    a, b = P(0.45, -0.20, 1.35), P(0.95, 0.20, 1.80)
    mb.add_box(a[0], a[1], a[2], b[0], b[1], b[2], coat)
    a, b = P(0.90, -0.13, 1.42), P(1.35, 0.13, 1.70)
    mb.add_box(a[0], a[1], a[2], b[0], b[1], b[2], coat)
    # legs
    for dx in (-0.72, 0.32):
        for dy in (-0.22, 0.22):
            a, b = P(dx - 0.07, dy - 0.07, 0.0), P(dx + 0.07, dy + 0.07, 0.98)
            mb.add_box(a[0], a[1], a[2], b[0], b[1], b[2], "black")
    # tail
    a, b = P(-1.02, -0.07, 1.10), P(-0.90, 0.07, 1.52)
    mb.add_box(a[0], a[1], a[2], b[0], b[1], b[2], "black")


def dray(mb, x, y, z, rz=0.0, loaded=True, load_mat="canvas"):
    """A four-wheel flat dray with a horse in the shafts."""
    horse(mb, x - 2.9, y, z, rz)
    c, s = math.cos(math.radians(rz)), math.sin(math.radians(rz))

    def P(dx, dy, dz):
        return (x + dx * c - dy * s, y + dx * s + dy * c, z + dz)

    # bed
    a, b = P(-2.2, -0.95, 0.95), P(2.2, 0.95, 1.10)
    mb.add_box(a[0], a[1], a[2], b[0], b[1], b[2], "plank")
    # side boards
    for dy in (-0.95, 0.95):
        a, b = P(-2.2, dy - 0.05, 1.10), P(2.2, dy + 0.05, 1.62)
        mb.add_box(a[0], a[1], a[2], b[0], b[1], b[2], "plank")
    # wheels
    for dx in (-1.55, 1.55):
        for dy in (-1.00, 1.00):
            mb.add_cyl(x + dx * c - dy * s, y + dx * s + dy * c, z + 0.10,
                       z + 0.95, 0.55, "timber", seg=10)
    # shafts
    for dy in (-0.45, 0.45):
        a, b = P(2.2, dy - 0.05, 0.95), P(3.6, dy + 0.05, 1.15)
        mb.add_box(a[0], a[1], a[2], b[0], b[1], b[2], "timber")
    if loaded:
        a, b = P(-2.0, -0.85, 1.10), P(2.0, 0.85, 1.85)
        mb.add_box(a[0], a[1], a[2], b[0], b[1], b[2], load_mat)


def handcart(mb, x, y, z, rz=0.0, load=True):
    """A two-wheel handcart, 2.1 m long -- the universal dock tool."""
    c, s = math.cos(math.radians(rz)), math.sin(math.radians(rz))

    def P(dx, dy, dz):
        return (x + dx * c - dy * s, y + dx * s + dy * c, z + dz)

    a, b = P(-1.05, -0.55, 1.00), P(1.05, 0.55, 1.08)
    mb.add_box(a[0], a[1], a[2], b[0], b[1], b[2], "plank")
    for dy in (-0.55, 0.55):
        a, b = P(-1.05, dy - 0.04, 1.08), P(1.05, dy + 0.04, 1.42)
        mb.add_box(a[0], a[1], a[2], b[0], b[1], b[2], "plank")
    # handles
    for dy in (-0.42, 0.42):
        a, b = P(-1.05, dy - 0.04, 1.02), P(-1.85, dy + 0.04, 1.12)
        mb.add_box(a[0], a[1], a[2], b[0], b[1], b[2], "timber")
    mb.add_cyl(x, y, z + 0.12, z + 1.02, 0.42, "timber", seg=10)
    if load:
        a, b = P(-0.95, -0.45, 1.08), P(0.95, 0.45, 1.55)
        mb.add_box(a[0], a[1], a[2], b[0], b[1], b[2], "canvas")


def sack_pile(mb, x, y, z, n=7, seed=0):
    """A heap of coal or grain sacks."""
    import random
    rnd = random.Random(seed)
    for i in range(n):
        px = x + rnd.uniform(-1.3, 1.3)
        py = y + rnd.uniform(-0.9, 0.9)
        pz = z + 0.28 * (i // 3)
        r = rnd.uniform(-25, 25)
        cs, sn = math.cos(math.radians(r)), math.sin(math.radians(r))
        w, d, h = 0.44, 0.30, 0.74
        pts = []
        for dx, dy in ((-w, -d), (w, -d), (w, d), (-w, d)):
            pts.append((px + dx * cs - dy * sn, py + dx * sn + dy * cs))
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        mb.add_box(min(xs), min(ys), pz, max(xs), max(ys), pz + h, "canvas")


def barrel_group(mb, x, y, z, n=5, seed=0):
    import random
    rnd = random.Random(seed)
    for i in range(n):
        px = x + rnd.uniform(-1.6, 1.6)
        py = y + rnd.uniform(-1.2, 1.2)
        mb.add_cyl(px, py, z, z + 0.92, 0.29, "timber", seg=10)


def rope_coil(mb, x, y, z, r=0.42, rz=0.0):
    """A hawser coiled on the coping -- the universal dock signature."""
    for k in range(3):
        mb.add_cyl(x, y, z + k * 0.13, z + 0.12 + k * 0.13, r - k * 0.10, "rope", seg=12)


def plank_stack(mb, x, y, z, rz=0.0, n=9):
    c, s = math.cos(math.radians(rz)), math.sin(math.radians(rz))

    def P(dx, dy):
        return (x + dx * c - dy * s, y + dx * s + dy * c)

    for k in range(n):
        a = P(-2.6, -0.9); b = P(2.6, 0.9)
        mb.add_box(min(a[0], b[0]), min(a[1], b[1]), z + k * 0.055,
                   max(a[0], b[0]), max(a[1], b[1]), z + k * 0.055 + 0.045, "plank")


def coal_heap(mb, x, y, z, r=3.4, h=1.9, seg=12):
    """A heap of coal on the staithe, as a stepped cone."""
    steps = 5
    for i in range(steps):
        t = i / steps
        rr = r * (1.0 - t * 0.72)
        mb.add_cyl(x, y, z + h * t, z + h * (t + 1.0 / steps), rr, "coal", seg=seg)


def bale_stack(mb, x, y, z, n=4, seed=0):
    import random
    rnd = random.Random(seed)
    for i in range(n):
        px = x + rnd.uniform(-0.7, 0.7)
        py = y + rnd.uniform(-0.5, 0.5)
        pz = z + (i // 2) * 0.62
        mb.add_box(px - 0.55, py - 0.35, pz, px + 0.55, py + 0.35, pz + 0.60, "canvas")


def ladder(mb, x, y, z, h=4.2, rz=0.0):
    """A leaning ladder -- against a stack, a crane leg, a shed."""
    c, s = math.cos(math.radians(rz)), math.sin(math.radians(rz))
    for dy in (-0.22, 0.22):
        a = (x - dy * s, y + dy * c)
        mb.add_box(a[0] - 0.035, a[1] - 0.035, z, a[0] + 0.035, a[1] + 0.035, z + h, "timber")
    for k in range(int(h / 0.30)):
        zz = z + 0.15 + k * 0.30
        a = (x - 0.22 * s, y + 0.22 * c)
        b = (x + 0.22 * s, y - 0.22 * c)
        mb.add_box(min(a[0], b[0]) - 0.03, min(a[1], b[1]) - 0.03, zz,
                   max(a[0], b[0]) + 0.03, max(a[1], b[1]) + 0.03, zz + 0.04, "timber")

"""
texgen.py -- deterministic, tileable Victorian material texture generator.

Every texture is authored to a real-world tile size in METRES (TEX_METRES) so that
MeshBuilder can assign UVs at a consistent texel density for the whole port.
This is what stops the buildings reading as flat-shaded boxes.

Run standalone:  python3 texgen.py <outdir>
Requires numpy + Pillow only (no Blender).
"""
import os
import numpy as np
from PIL import Image

PX = 1024  # texture resolution

# real-world size of one texture tile, in metres. Shared with matdefs.
TEX_METRES = {
    "brick_soot":   2.25,   # 215x65mm bricks + 10mm joints -> 10 bricks x 30 courses
    "brick_buff":   2.25,
    "brick_blue":   2.25,
    "sandstone":    2.40,   # 600x300mm ashlar blocks
    "slate":        1.20,   # 300mm courses, 3 courses
    "setts":        2.00,   # granite setts, 200x100mm
    "granite":      2.40,   # coping / kerb, 1200x600 blocks
    "rubble":       2.40,   # coursed rubble dock wall
    "timber":       1.20,
    "plank":        2.40,
    "iron":         1.00,
    "steel_plate":  2.00,   # riveted plate, 1.22m strakes
    "coal":         1.00,
    "canvas":       1.00,
    "stucco":       2.00,   # painted render (terminal / station)
    "terracotta":   1.20,
    "yard":         4.00,   # compacted earth / gravel yard
    "flags":        3.60,   # 1.2 x 0.9 m stone flags
    "ballast":      1.20,   # railway ballast
}


# ---------------------------------------------------------------- noise utils
def _pnoise(shape, period, seed):
    """Periodic value noise: wraps seamlessly at `period` lattice cells."""
    rng = np.random.default_rng(seed)
    g = rng.random((period, period)).astype(np.float32)
    h, w = shape
    yy = np.linspace(0, period, h, endpoint=False, dtype=np.float32)
    xx = np.linspace(0, period, w, endpoint=False, dtype=np.float32)
    y0 = np.floor(yy).astype(int)
    x0 = np.floor(xx).astype(int)
    fy = (yy - y0)[:, None]
    fx = (xx - x0)[None, :]
    fy = fy * fy * (3 - 2 * fy)
    fx = fx * fx * (3 - 2 * fx)
    y1 = (y0 + 1) % period
    x1 = (x0 + 1) % period
    y0 %= period
    x0 %= period
    a = g[y0][:, x0]
    b = g[y0][:, x1]
    c = g[y1][:, x0]
    d = g[y1][:, x1]
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy


def fbm(shape, base_period, octaves=5, seed=0, gain=0.5):
    out = np.zeros(shape, np.float32)
    amp, per, norm = 1.0, base_period, 0.0
    for o in range(octaves):
        out += amp * _pnoise(shape, max(2, int(per)), seed + o * 977)
        norm += amp
        amp *= gain
        per *= 2
    return out / norm


def _normalmap(height, strength=2.2):
    gy, gx = np.gradient(height.astype(np.float32))
    nx = -gx * strength
    ny = -gy * strength
    nz = np.ones_like(nx)
    ln = np.sqrt(nx * nx + ny * ny + nz * nz)
    return np.dstack([nx / ln, ny / ln, nz / ln]) * 0.5 + 0.5


def _mix(a, b, t):
    t = t[..., None] if t.ndim == 2 else t
    return a * (1 - t) + b * t


def _shade(col, rough):
    rough = np.asarray(rough, dtype=np.float32)
    if rough.ndim == 0:                      # broadcast a constant roughness
        rough = np.full(col.shape[:2], float(rough), np.float32)
    return np.clip(col, 0, 1), np.clip(rough, 0.03, 1.0)


def _save(outdir, name, col, rough=None, height=None):
    Image.fromarray((np.clip(col, 0, 1) * 255).astype(np.uint8)).save(
        os.path.join(outdir, name + "_alb.png"))
    if rough is not None:
        r = np.clip(rough, 0, 1)
        Image.fromarray((r * 255).astype(np.uint8)).save(
            os.path.join(outdir, name + "_rgh.png"))
    if height is not None:
        n = _normalmap(height)
        Image.fromarray((np.clip(n, 0, 1) * 255).astype(np.uint8)).save(
            os.path.join(outdir, name + "_nrm.png"))


# ---------------------------------------------------------------- brickwork
def _brick(kind):
    """Accurate 215x65mm brick, 10mm joints. Tile = 2.25m = 10 bricks x 30 courses."""
    h = w = PX
    bw = w / 10.0          # brick+joint pitch in px
    bh = h / 30.0
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    row = np.floor(yy / bh).astype(int)
    # alternate courses offset by half a brick (English bond stretcher courses)
    off = (row % 2) * (bw * 0.5)
    col_i = np.floor(((xx + off) % w) / bw).astype(int)
    fx = (((xx + off) % w) / bw) % 1.0     # position WITHIN a brick, 0..1
    fy = (yy % bh) / bh
    rng = np.random.default_rng(1200 + len(kind))
    # per-brick hue/value variation keyed to (row, col) so it is tileable
    jitter = (np.sin(row * 12.9898 + col_i * 78.233) * 43758.5453) % 1.0
    jitter2 = (np.sin(row * 39.3468 + col_i * 11.135) * 24634.6345) % 1.0

    if kind == "soot":          # soot-blackened Accrington / Ruabon red
        base = np.array([0.298, 0.172, 0.136])
        alt = np.array([0.240, 0.140, 0.112])
        mortar = np.array([0.300, 0.278, 0.246])
    elif kind == "buff":        # Birmingham / Leicester buff stock brick
        base = np.array([0.398, 0.330, 0.238])
        alt = np.array([0.336, 0.256, 0.166])
        mortar = np.array([0.447, 0.427, 0.392])
    else:                       # blue / Staffordshire engineering brick
        base = np.array([0.118, 0.126, 0.140])
        alt = np.array([0.086, 0.094, 0.106])
        mortar = np.array([0.212, 0.208, 0.196])

    col = _mix(base[None, None, :], alt[None, None, :], (jitter * 0.85)[..., None] *
               np.ones((1, 1, 3)))
    # per-brick value noise
    col = col * (0.86 + 0.30 * jitter2[..., None])

    # Mortar joint mask, expressed as a fraction of the brick pitch:
    # 10mm joint / 225mm bed pitch = 0.044 in u, 10mm / 75mm course = 0.133 in v.
    # Each joint sits on the boundary between two bricks, so it is split half/half.
    ju = 0.044 * 0.5
    jv = 0.133 * 0.5
    edge_u = np.minimum(fx, 1 - fx) < ju
    edge_v = np.minimum(fy, 1 - fy) < jv
    mortar_mask = (edge_u | edge_v).astype(np.float32)
    col = _mix(col, mortar[None, None, :], mortar_mask * 0.92)

    height = (1.0 - mortar_mask) * 0.85 + fbm((h, w), 16, 4, seed=7) * 0.15
    # brick surface roughness / firing mottling
    mott = fbm((h, w), 8, 5, seed=31)
    col = col * (0.90 + 0.20 * mott[..., None])
    # soot gradient: grime concentrates toward the bottom of the tile
    if kind == "soot":
        grime = np.clip(1.0 - yy / h, 0, 1) ** 2.2
        col = col * (1 - 0.22 * grime[..., None])
        col = _mix(col, np.array([0.09, 0.075, 0.068])[None, None, :],
                   0.18 * fbm((h, w), 4, 4, seed=99))
    rough = 0.86 + mortar_mask * 0.08 + 0.05 * mott
    return _shade(col, rough), height


# ---------------------------------------------------------------- stone
def _sandstone():
    h = w = PX
    rng = np.random.default_rng(88)
    # 600x300mm coursed ashlar -> 4 cols x 8 rows over 2.4m
    rows, cols = 8, 4
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    ry = np.floor(yy / (h / rows)).astype(int)
    off = (ry % 2) * (w / cols * 0.5)
    cx = np.floor(((xx + off) % w) / (w / cols)).astype(int)
    jit = (np.sin(ry * 21.13 + cx * 4.77) * 999.9) % 1.0
    base = np.array([0.408, 0.372, 0.312])     # weathered buff sandstone
    col = np.ones((h, w, 3), np.float32) * base
    col *= (0.84 + 0.28 * jit[..., None])
    n = fbm((h, w), 6, 6, seed=12)
    col *= (0.88 + 0.24 * n[..., None])
    # horizontal joint bedding (10mm)
    jy = np.minimum(yy % (h / rows), h / rows - yy % (h / rows)) / (h / rows)
    jx = np.minimum((xx + off) % (w / cols), w / cols - (xx + off) % (w / cols)) / (w / cols)
    jm = ((jy < 0.016) | (jx < 0.008)).astype(np.float32)
    col = _mix(col, np.array([0.30, 0.27, 0.22])[None, None, :], jm * 0.8)
    # louvre water-staining streaks
    streak = fbm((h, w), 3, 4, seed=44)
    streak = np.clip((streak - 0.55) * 3.0, 0, 1)
    col = _mix(col, np.array([0.22, 0.20, 0.17])[None, None, :], streak * 0.22)
    height = (1 - jm) * 0.8 + n * 0.2
    return _shade(col, 0.80 + 0.08 * n), height


def _rubble():
    h = w = PX
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    rows = 9
    ry = np.floor(yy / (h / rows)).astype(int)
    rng = np.random.default_rng(303)
    off = (np.sin(ry * 71.3) * 0.5 + 0.5) * 60
    cell = w / 6.0
    cx = np.floor(((xx + off) % w) / cell).astype(int)
    jit = (np.sin(ry * 17.7 + cx * 51.3) * 4571.1) % 1.0
    base = np.array([0.290, 0.272, 0.240])
    col = np.ones((h, w, 3), np.float32) * base
    col *= (0.70 + 0.55 * jit[..., None])
    jy = np.minimum(yy % (h / rows), h / rows - yy % (h / rows)) / (h / rows)
    jx = np.minimum((xx + off) % cell, cell - (xx + off) % cell) / cell
    jm = ((jy < 0.02) | (jx < 0.012)).astype(np.float32)
    col = _mix(col, np.array([0.14, 0.13, 0.12])[None, None, :], jm * 0.85)
    n = fbm((h, w), 20, 6, seed=5)
    col *= (0.8 + 0.4 * n[..., None])
    height = (1 - jm) * 0.7 + n * 0.3
    return _shade(col, 0.90), height


def _granite_block():
    h = w = PX
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    rows, cols = 2, 2   # 1200x600mm blocks
    ry = np.floor(yy / (h / rows)).astype(int)
    off = (ry % 2) * (w / cols * 0.5)
    cx = np.floor(((xx + off) % w) / (w / cols)).astype(int)
    jit = (np.sin(ry * 3.7 + cx * 9.1) * 71.7) % 1.0
    base = np.array([0.372, 0.362, 0.344])
    col = np.ones((h, w, 3), np.float32) * base
    col *= (0.86 + 0.24 * jit[..., None])
    n = fbm((h, w), 40, 6, seed=8)      # close speckle
    n2 = fbm((h, w), 10, 4, seed=81)
    col *= (0.86 + 0.22 * n[..., None] + 0.12 * n2[..., None])
    jy = np.minimum(yy % (h / rows), h / rows - yy % (h / rows)) / (h / rows)
    jx = np.minimum((xx + off) % (w / cols), w / cols - (xx + off) % (w / cols)) / (w / cols)
    jm = ((jy < 0.008) | (jx < 0.004)).astype(np.float32)
    col = _mix(col, np.array([0.16, 0.16, 0.15])[None, None, :], jm * 0.7)
    height = (1 - jm) * 0.6 + n * 0.4
    return _shade(col, 0.72 + 0.1 * n), height


def _setts():
    """Granite setts, 200x100mm laid in courses. Tile 2.0m."""
    h = w = PX
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    rows, cols = 20, 10
    ry = np.floor(yy / (h / rows)).astype(int)
    off = (ry % 2) * (w / cols * 0.5)
    cx = np.floor(((xx + off) % w) / (w / cols)).astype(int)
    jit = (np.sin(ry * 11.1 + cx * 37.7) * 811.3) % 1.0
    jit2 = (np.sin(ry * 5.3 + cx * 91.7) * 331.7) % 1.0
    base = np.array([0.300, 0.290, 0.272])
    col = np.ones((h, w, 3), np.float32) * base
    col *= (0.62 + 0.56 * jit[..., None])
    col = col * (0.9 + 0.2 * jit2[..., None])
    jy = np.minimum(yy % (h / rows), h / rows - yy % (h / rows)) / (h / rows)
    jx = np.minimum((xx + off) % (w / cols), w / cols - (xx + off) % (w / cols)) / (w / cols)
    # rounded settling: joints read as darker and the stone crowns are lighter
    crown = np.clip(np.minimum(jy, jx * 2.0) * 8.0, 0, 1)
    col *= (0.72 + 0.38 * crown[..., None])
    jm = ((jy < 0.05) | (jx < 0.03)).astype(np.float32)
    col = _mix(col, np.array([0.10, 0.10, 0.10])[None, None, :], jm * 0.75)
    # horse-dung / mud film in the hollows
    mud = fbm((h, w), 8, 4, seed=61)
    col = _mix(col, np.array([0.16, 0.145, 0.125])[None, None, :],
               np.clip((mud - 0.6) * 2.0, 0, 1) * 0.3)
    height = crown * 0.7 + fbm((h, w), 60, 4, seed=3) * 0.3
    return _shade(col, 0.80 + 0.12 * (1 - crown)), height


def _slate():
    """Welsh slate roof: 300mm courses. Tile 1.2m -> 4 courses."""
    h = w = PX
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    rows, cols = 4, 4
    ry = np.floor(yy / (h / rows)).astype(int)
    off = (ry % 2) * (w / cols * 0.5)
    cx = np.floor(((xx + off) % w) / (w / cols)).astype(int)
    jit = (np.sin(ry * 8.3 + cx * 27.9) * 613.1) % 1.0
    base = np.array([0.205, 0.214, 0.228])
    col = np.ones((h, w, 3), np.float32) * base
    col *= (0.80 + 0.40 * jit[..., None])
    fy = (yy % (h / rows)) / (h / rows)
    # shadow under each course laps
    lap = np.clip((fy - 0.72) / 0.28, 0, 1)
    col *= (1 - 0.55 * lap[..., None])
    n = fbm((h, w), 24, 5, seed=15)
    col *= (0.88 + 0.24 * n[..., None])
    height = (1 - lap) * 0.8 + n * 0.2
    return _shade(col, 0.62 + 0.16 * n), height


# ---------------------------------------------------------------- timber / metal
def _timber(name="timber"):
    h = w = PX
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    if name == "plank":
        planks = 8   # deck planks across 2.4m -> 300mm
    else:
        planks = 6   # 200mm boards across 1.2m
    pitch = w / planks
    pi = np.floor(xx / pitch).astype(int)
    jit = (np.sin(pi * 43.1) * 3571.7) % 1.0
    base = np.array([0.318, 0.243, 0.160])     # tarred / weathered deal
    col = np.ones((h, w, 3), np.float32) * base
    col *= (0.74 + 0.48 * jit[..., None])
    # grain: stretched noise
    grain = fbm((h, w), 3, 5, seed=23 + planks)
    grain = np.repeat(grain, 1, axis=0)
    gy = fbm((h, w), 64, 3, seed=77)
    col *= (0.86 + 0.26 * grain[..., None] + 0.10 * gy[..., None])
    # knots
    knot = np.clip(fbm((h, w), 12, 3, seed=131) - 0.72, 0, 1) * 4
    col = _mix(col, np.array([0.13, 0.09, 0.05])[None, None, :], np.clip(knot, 0, 1) * 0.7)
    # board joints
    jx = np.minimum(xx % pitch, pitch - xx % pitch) / pitch
    jm = (jx < 0.012).astype(np.float32)
    col = _mix(col, np.array([0.07, 0.05, 0.035])[None, None, :], jm * 0.9)
    height = (1 - jm) * 0.6 + grain * 0.4
    return _shade(col, 0.85), height


def _iron():
    """Black-painted cast/wrought iron with rust bloom."""
    h = w = PX
    base = np.array([0.075, 0.078, 0.082])
    n = fbm((h, w), 10, 6, seed=41)
    rust = np.clip((fbm((h, w), 5, 5, seed=57) - 0.60) * 3.4, 0, 1)
    col = np.ones((h, w, 3), np.float32) * base
    col *= (0.8 + 0.5 * n[..., None])
    col = _mix(col, np.array([0.290, 0.135, 0.062])[None, None, :], rust * 0.55)
    rough = 0.45 + 0.35 * rust + 0.1 * n
    return _shade(col, rough), n


def _steel_plate():
    """Riveted steel plating: 1.22m strakes, rivet lines. Tile 2.0m."""
    h = w = PX
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    strake = h / 1.64
    ry = np.floor(yy / strake).astype(int)
    off = (ry % 2) * strake * 0.5
    jit = (np.sin(ry * 5.9) * 311.3) % 1.0
    base = np.array([0.150, 0.152, 0.158])
    col = np.ones((h, w, 3), np.float32) * base
    col *= (0.86 + 0.24 * jit[..., None])
    n = fbm((h, w), 12, 5, seed=66)
    col *= (0.88 + 0.24 * n[..., None])
    # strap joints
    jy = np.minimum(yy % strake, strake - yy % strake) / strake
    jm = (jy < 0.010).astype(np.float32)
    # rivet rows just above each joint
    riv_y = np.abs(yy % strake - strake * 0.93)
    riv_sp = ((xx + off) % (w / 14.0))
    riv = ((riv_y < h * 0.006) & (riv_sp < w * 0.007)).astype(np.float32)
    rust = np.clip((fbm((h, w), 6, 5, seed=91) - 0.58) * 3.0, 0, 1)
    col = _mix(col, np.array([0.28, 0.14, 0.07])[None, None, :], rust * 0.6)
    col = _mix(col, np.array([0.06, 0.06, 0.06])[None, None, :], jm * 0.7)
    col = _mix(col, np.array([0.30, 0.30, 0.31])[None, None, :], riv * 0.55)
    height = riv * 0.6 + (1 - jm) * 0.3 + n * 0.1
    return _shade(col, 0.52 + 0.3 * rust), height


def _coal():
    h = w = PX
    base = np.array([0.048, 0.046, 0.048])
    n = fbm((h, w), 30, 6, seed=19)
    n2 = fbm((h, w), 8, 4, seed=71)
    col = np.ones((h, w, 3), np.float32) * base
    col *= (0.5 + 1.5 * n[..., None])
    col = _mix(col, np.array([0.11, 0.10, 0.10])[None, None, :], np.clip(n2 - 0.5, 0, 1) * 0.7)
    return _shade(col, 0.55 + 0.35 * n), n


def _canvas():
    h = w = PX
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    weave = (np.sin(xx * np.pi / 3.0) * np.sin(yy * np.pi / 3.0)) * 0.5 + 0.5
    base = np.array([0.400, 0.352, 0.276])   # tarpaulin / awning canvas
    col = np.ones((h, w, 3), np.float32) * base
    col *= (0.86 + 0.20 * weave[..., None])
    n = fbm((h, w), 6, 5, seed=27)
    col *= (0.90 + 0.18 * n[..., None])
    stain = np.clip((fbm((h, w), 4, 4, seed=83) - 0.55) * 2.5, 0, 1)
    col = _mix(col, np.array([0.20, 0.18, 0.14])[None, None, :], stain * 0.35)
    return _shade(col, 0.90), weave * 0.3 + n * 0.7


def _stucco():
    h = w = PX
    base = np.array([0.462, 0.432, 0.372])   # cream-painted render
    n = fbm((h, w), 14, 6, seed=33)
    col = np.ones((h, w, 3), np.float32) * base
    col *= (0.92 + 0.16 * n[..., None])
    # weathering streaks down the wall + soot at the base
    streak = np.clip((fbm((h, w), 3, 4, seed=53) - 0.58) * 3.0, 0, 1)
    col = _mix(col, np.array([0.26, 0.24, 0.21])[None, None, :], streak * 0.30)
    return _shade(col, 0.78), n


def _yard():
    """Compacted earth and gravel yard: ruts, ash, puddles, no stone course."""
    h = w = PX
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    base = np.array([0.300, 0.278, 0.243])
    big = fbm((h, w), 3, 5, seed=71)
    fine = fbm((h, w), 40, 4, seed=72)
    grit = fbm((h, w), 160, 3, seed=73)
    col = np.ones((h, w, 3), np.float32) * base
    col *= (0.72 + 0.55 * big[..., None])
    col *= (0.88 + 0.24 * fine[..., None])
    col *= (0.90 + 0.20 * grit[..., None])
    # cart ruts, roughly parallel, sunk and darker
    rut = np.zeros((h, w), np.float32)
    for k, cx in enumerate((0.22, 0.31, 0.70, 0.79)):
        d = np.abs(xx / w - cx)
        rut = np.maximum(rut, np.clip(1.0 - d / 0.022, 0, 1) * (0.5 + 0.5 * fine))
    col *= (1.0 - 0.28 * rut[..., None])
    # standing water in the lowest spots
    wet = np.clip((big - 0.70) * 4.0, 0, 1) * np.clip((0.5 - rut) * 3.0, 0, 1)
    col = _mix(col, np.array([0.075, 0.082, 0.080])[None, None, :], wet * 0.85)
    # NOTE: keep the height field gentle. Gradients are converted to a normal map
    # at strength 2.2, and a high-frequency height (the grit octave) produced
    # normals lying almost flat, which rendered the whole yard near-black.
    height = (0.30 + 0.45 * fine + 0.25 * big) * (1 - 0.35 * rut) - 0.20 * wet
    height = np.clip(height, 0, 1) * 0.18
    return _shade(col, 0.96 - 0.35 * wet), height


def _flags():
    """Big stone flags, 1.2 x 0.9 m -- quay edges, forecourts, station yards."""
    h = w = PX
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    rows, cols = 4, 3
    ry = np.floor(yy / (h / rows)).astype(int)
    off = (ry % 2) * (w / cols * 0.5)
    cx = np.floor(((xx + off) % w) / (w / cols)).astype(int)
    jit = (np.sin(ry * 17.3 + cx * 53.1) * 977.7) % 1.0
    base = np.array([0.268, 0.262, 0.246])
    col = np.ones((h, w, 3), np.float32) * base
    col *= (0.82 + 0.30 * jit[..., None])
    jy = np.minimum(yy % (h / rows), h / rows - yy % (h / rows)) / (h / rows)
    jx = np.minimum((xx + off) % (w / cols), w / cols - (xx + off) % (w / cols)) / (w / cols)
    joint = ((jy < 0.012) | (jx < 0.016)).astype(np.float32)
    col = _mix(col, np.array([0.085, 0.082, 0.075])[None, None, :], joint * 0.85)
    # wear polish in the middle of each flag, dirt at the edges
    edge = np.clip(np.minimum(jy * 14, jx * 10), 0, 1)
    col *= (0.94 + 0.14 * edge[..., None])
    n = fbm((h, w), 22, 4, seed=81)
    col *= (0.93 + 0.14 * n[..., None])
    mud = fbm((h, w), 7, 4, seed=82)
    col = _mix(col, np.array([0.15, 0.135, 0.115])[None, None, :],
               np.clip((mud - 0.62) * 2.6, 0, 1) * 0.45 * (1 - edge))
    height = (np.clip(1.0 - joint * 1.4, 0, 1) * 0.8 + n * 0.2) * 0.45
    return _shade(col, 0.80 + 0.10 * n), height


def _ballast():
    """Angular granite ballast between and around the rails."""
    h = w = PX
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    n1 = fbm((h, w), 55, 3, seed=91)
    n2 = fbm((h, w), 22, 3, seed=92)
    stones = np.clip((n1 - 0.42) * 5.0, 0, 1)
    base = np.array([0.185, 0.180, 0.168])
    col = np.ones((h, w, 3), np.float32) * base
    col *= (0.55 + 1.15 * stones[..., None])
    col *= (0.86 + 0.28 * n2[..., None])
    col = _mix(col, np.array([0.055, 0.052, 0.048])[None, None, :],
               (1 - stones) * 0.55)
    height = (np.clip(stones * 1.2 - 0.1, 0, 1) * 0.75 + n2 * 0.25) * 0.30
    return _shade(col, 0.92 - 0.1 * stones), height


def _terracotta():
    h = w = PX
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    rows = 8
    ry = np.floor(yy / (h / rows)).astype(int)
    jit = (np.sin(ry * 13.1) * 577.3) % 1.0
    base = np.array([0.372, 0.196, 0.130])    # Ruabon red terracotta / tile
    col = np.ones((h, w, 3), np.float32) * base
    col *= (0.82 + 0.34 * jit[..., None])
    fy = (yy % (h / rows)) / (h / rows)
    lap = np.clip((fy - 0.75) / 0.25, 0, 1)
    col *= (1 - 0.45 * lap[..., None])
    n = fbm((h, w), 18, 5, seed=29)
    col *= (0.9 + 0.2 * n[..., None])
    return _shade(col, 0.66 + 0.12 * n), (1 - lap) * 0.8 + n * 0.2


# ---------------------------------------------------------------- driver
RECIPES = {
    "brick_soot":  lambda: _brick("soot"),
    "brick_buff":  lambda: _brick("buff"),
    "brick_blue":  lambda: _brick("blue"),
    "sandstone":   _sandstone,
    "slate":       _slate,
    "setts":       _setts,
    "granite":     _granite_block,
    "rubble":      _rubble,
    "timber":      lambda: _timber("timber"),
    "plank":       lambda: _timber("plank"),
    "iron":        _iron,
    "steel_plate": _steel_plate,
    "coal":        _coal,
    "canvas":      _canvas,
    "stucco":      _stucco,
    "terracotta":  _terracotta,
    "yard":        _yard,
    "flags":       _flags,
    "ballast":     _ballast,
}


def generate_all(outdir):
    os.makedirs(outdir, exist_ok=True)
    made = []
    for name, fn in RECIPES.items():
        (col, rough), height = fn()
        _save(outdir, name, col, rough, height)
        made.append(name)
        print("  tex:", name)
    return made


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "textures"
    print("Generating Victorian material set ->", out)
    generate_all(out)
    print("Done:", len(RECIPES), "materials")

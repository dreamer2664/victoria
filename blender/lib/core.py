"""
core.py -- shared constants, material library and the MeshBuilder geometry engine.
GENERATION II — OPERATION VICTORIA (PERICLES-II)

CONVENTIONS
-----------
* Units are METRES throughout the Blender scenes (1 Blender unit = 1 m).
* Z is up. Water surface is z = 0. Quay coping is z = +4.00 (typical Victorian
  impounded-dock freeboard; Liverpool's Albert Dock quays sit ~4.3 m above water).
* X runs along the quay wall for each port unless a module documents otherwise.
* UVs are generated in WORLD-PLANAR projection scaled by each material's real
  tile size, so texel density is constant everywhere and bricks/stone keep a
  true course no matter how big the object is.

ROBLOX CONVERSION
-----------------
1 Roblox stud = 0.28 m  ->  metres_to_studs = 1 / 0.28 = 3.57142857
"""
import math

STUDS_PER_METRE = 1.0 / 0.28          # 3.57142857

# ---------------------------------------------------------------- levels (m)
WATER_Z = 0.00
HIGH_WATER_Z = 1.20
LOW_WATER_Z = -1.20
QUAY_Z = 4.00          # top of quay coping
SILL_Z = -4.50         # graving dock sill below water datum
RIVER_BED_Z = -11.00   # River Alde / River Lagan channel bed
DOCK_BED_Z = -9.00     # impounded wet dock bed (Trafalgar Dock)
GRAVING_FLOOR_Z = -7.00 # Princess Graving Dock stone floor (11.0 m below coping)

# liner envelope to design berths against (integration allowance for SS Aurelian)
LINER_L = 166.0
LINER_B = 18.4
LINER_DRAFT = 6.5

# ---------------------------------------------------------------- materials
MATERIALS = {
    # masonry / brick
    "brick_soot":  dict(kind="tex", tile=2.25, rough=0.88),   # warehouses, soot-blackened
    "brick_buff":  dict(kind="tex", tile=2.25, rough=0.86),   # offices, station
    "brick_blue":  dict(kind="tex", tile=2.25, rough=0.80),   # engineering brick, plinths
    "brick_red":   dict(kind="tex", tile=2.25, rough=0.85, color=(0.42, 0.16, 0.11)),
    "sandstone":   dict(kind="tex", tile=2.40, rough=0.82),   # Custom House, cornices
    "rubble":      dict(kind="tex", tile=2.40, rough=0.92),   # dock walls below coping
    "granite":     dict(kind="tex", tile=2.40, rough=0.74),   # coping, kerbs, dock altars
    "setts":       dict(kind="tex", tile=2.00, rough=0.82),   # carriageway paving
    "flags":       dict(kind="tex", tile=3.60, rough=0.78),   # big stone flags
    "yard":        dict(kind="tex", tile=4.00, rough=0.95),   # earth yard
    "ballast":     dict(kind="tex", tile=1.20, rough=0.93),   # track ballast
    "terracotta":  dict(kind="tex", tile=1.20, rough=0.68),   # roof tiles, faience bands
    # roofs / timber / metal
    "slate":       dict(kind="tex", tile=1.20, rough=0.64),
    "timber":      dict(kind="tex", tile=1.20, rough=0.86),
    "plank":       dict(kind="tex", tile=2.40, rough=0.84),
    "creosote":    dict(kind="flat", color=(0.045, 0.038, 0.030), rough=0.92), # fender piles
    "iron":        dict(kind="tex", tile=1.00, rough=0.55, metal=0.65),
    "steel":       dict(kind="tex", tile=2.00, rough=0.58, metal=0.70),
    "steel_plate": dict(kind="tex", tile=2.00, rough=0.58, metal=0.70),
    "coal":        dict(kind="tex", tile=1.00, rough=0.72),
    "canvas":      dict(kind="tex", tile=1.00, rough=0.92),
    "stucco":      dict(kind="tex", tile=2.00, rough=0.80),
    # untextured / flat
    "algae":       dict(kind="flat", color=(0.042, 0.075, 0.038), rough=0.92), # tidal mark
    "glass":       dict(kind="flat", color=(0.072, 0.086, 0.098), rough=0.16, metal=0.0, alpha=0.70),
    "glass_lit":   dict(kind="flat", color=(0.42, 0.28, 0.12), rough=0.20, emit=2.0),
    "paint_white": dict(kind="flat", color=(0.72, 0.70, 0.65), rough=0.55),
    "puddle":      dict(kind="flat", color=(0.038, 0.045, 0.048), rough=0.07, metal=0.25),
    "paint_green": dict(kind="flat", color=(0.028, 0.055, 0.042), rough=0.62), # dock-board green
    "paint_red":   dict(kind="flat", color=(0.32, 0.075, 0.055), rough=0.62),
    "brass":       dict(kind="flat", color=(0.58, 0.44, 0.18), rough=0.30, metal=0.92),
    "bronze":      dict(kind="flat", color=(0.48, 0.35, 0.18), rough=0.35, metal=0.90),
    "copper":      dict(kind="flat", color=(0.30, 0.39, 0.34), rough=0.45, metal=0.85),
    "rope":        dict(kind="flat", color=(0.255, 0.205, 0.135), rough=0.95),
    "water":       dict(kind="flat", color=(0.042, 0.065, 0.070), rough=0.08, metal=0.35),
    "mud":         dict(kind="flat", color=(0.105, 0.092, 0.072), rough=0.95),
    "black":       dict(kind="flat", color=(0.024, 0.024, 0.026), rough=0.60),
    "interior":    dict(kind="flat", color=(0.128, 0.118, 0.106), rough=0.92),
    "whitewash":   dict(kind="flat", color=(0.65, 0.62, 0.58), rough=0.90),
    "plaster":     dict(kind="flat", color=(0.412, 0.386, 0.330), rough=0.88),
    "lead":        dict(kind="flat", color=(0.115, 0.124, 0.132), rough=0.42, metal=0.75),
    "brick_in":    dict(kind="flat", color=(0.150, 0.106, 0.092), rough=0.94),
    "lamp_glow":   dict(kind="flat", color=(1.0, 0.75, 0.38), rough=0.25, emit=4.0),
}

MAT_ORDER = list(MATERIALS.keys())
MAT_INDEX = {n: i for i, n in enumerate(MAT_ORDER)}


def tile_of(mat):
    return MATERIALS.get(mat, {}).get("tile", 1.0)


# ---------------------------------------------------------------- vector helpers
def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])

def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])

def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]

def _norm(a):
    L = math.hypot(a[0], a[1], a[2])
    if L < 1e-9: return (0.0, 0.0, 1.0)
    return (a[0] / L, a[1] / L, a[2] / L)


# ================================================================ MeshBuilder
class MeshBuilder:
    """Accumulates triangles and quads with per-face material and planar UVs."""

    __slots__ = ("verts", "faces", "fmats", "fuvs")

    def __init__(self):
        self.verts = []
        self.faces = []
        self.fmats = []
        self.fuvs = []

    def _v(self, p):
        self.verts.append((float(p[0]), float(p[1]), float(p[2])))
        return len(self.verts) - 1

    def add_face(self, pts, mat, uv_rot=0.0, uv_off=(0.0, 0.0), world_uv=True):
        """pts: 3+ coplanar points in CCW order seen from the front."""
        if len(pts) < 3:
            return
        n = _norm(_cross(_sub(pts[1], pts[0]), _sub(pts[2], pts[0])))
        ax = max(range(3), key=lambda i: abs(n[i]))
        t = tile_of(mat)
        uvs = []
        for p in pts:
            if not world_uv:
                u, v = (p[0], p[1])
            elif ax == 2:      # horizontal face -> plan projection
                u, v = p[0], p[1]
            elif ax == 0:      # normal along X -> elevation in YZ
                u, v = p[1], p[2]
            else:              # normal along Y -> elevation in XZ
                u, v = p[0], p[2]
            u, v = u / t + uv_off[0], v / t + uv_off[1]
            if uv_rot:
                c, s = math.cos(uv_rot), math.sin(uv_rot)
                u, v = u * c - v * s, u * s + v * c
            uvs.append((u, v))
        idx = [self._v(p) for p in pts]
        self.faces.append(tuple(idx))
        self.fmats.append(mat)
        self.fuvs.append(uvs)

    def add_quad_uv(self, a, b, c, d, mat, uvs=((0, 0), (1, 0), (1, 1), (0, 1))):
        """Quad with explicit corner UVs -- required for painted signboards."""
        idx = [self._v(p) for p in (a, b, c, d)]
        self.faces.append(tuple(idx))
        self.fmats.append(mat)
        self.fuvs.append([(float(u), float(v)) for u, v in uvs])

    def add_tri(self, a, b, c, mat, **kw):
        self.add_face((a, b, c), mat, **kw)

    def add_quad(self, a, b, c, d, mat, **kw):
        self.add_face((a, b, c, d), mat, **kw)

    # -- solids ------------------------------------------------------------
    def add_box(self, x0, y0, z0, x1, y1, z1, mat, top=None, bottom=None, uvo=(0, 0)):
        """Axis-aligned box from min corner to max corner. Outward-facing."""
        if x1 < x0: x0, x1 = x1, x0
        if y1 < y0: y0, y1 = y1, y0
        if z1 < z0: z0, z1 = z1, z0
        if x1 - x0 < 1e-6 or y1 - y0 < 1e-6 or z1 - z0 < 1e-6:
            return
        m = mat
        self.add_quad((x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1), top or m, uv_off=uvo)   # +Z
        self.add_quad((x0, y0, z0), (x0, y1, z0), (x1, y1, z0), (x1, y0, z0), bottom or m, uv_off=uvo)  # -Z
        self.add_quad((x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1), m, uv_off=uvo)            # -Y
        self.add_quad((x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1), m, uv_off=uvo)            # +X
        self.add_quad((x1, y1, z0), (x0, y1, z0), (x0, y1, z1), (x1, y1, z1), m, uv_off=uvo)            # +Y
        self.add_quad((x0, y1, z0), (x0, y0, z0), (x0, y0, z1), (x0, y1, z1), m, uv_off=uvo)            # -X

    def add_box_c(self, cx, cy, cz, sx, sy, sz, mat, **kw):
        self.add_box(cx - sx / 2, cy - sy / 2, cz - sz / 2,
                     cx + sx / 2, cy + sy / 2, cz + sz / 2, mat, **kw)

    def add_beam(self, p0, p1, w, h, mat, up=(0, 0, 1)):
        """A rectangular-section member running from p0 to p1."""
        d = _norm(_sub(p1, p0))
        if abs(_dot(d, up)) > 0.98:
            up = (1, 0, 0)
        side = _norm(_cross(d, up))
        nrm = _norm(_cross(side, d))
        a = [p0[0] + side[0] * w / 2 + nrm[0] * h / 2, p0[1] + side[1] * w / 2 + nrm[1] * h / 2, p0[2] + side[2] * w / 2 + nrm[2] * h / 2]
        b = [p1[0] + side[0] * w / 2 + nrm[0] * h / 2, p1[1] + side[1] * w / 2 + nrm[1] * h / 2, p1[2] + side[2] * w / 2 + nrm[2] * h / 2]
        c = [p1[0] - side[0] * w / 2 + nrm[0] * h / 2, p1[1] - side[1] * w / 2 + nrm[1] * h / 2, p1[2] - side[2] * w / 2 + nrm[2] * h / 2]
        dd = [p0[0] - side[0] * w / 2 + nrm[0] * h / 2, p0[1] - side[1] * w / 2 + nrm[1] * h / 2, p0[2] - side[2] * w / 2 + nrm[2] * h / 2]
        e = [a[0] - nrm[0] * h, a[1] - nrm[1] * h, a[2] - nrm[2] * h]
        f = [b[0] - nrm[0] * h, b[1] - nrm[1] * h, b[2] - nrm[2] * h]
        g = [c[0] - nrm[0] * h, c[1] - nrm[1] * h, c[2] - nrm[2] * h]
        hh = [dd[0] - nrm[0] * h, dd[1] - nrm[1] * h, dd[2] - nrm[2] * h]
        for q in ((a, b, c, dd), (e, hh, g, f), (a, e, f, b),
                  (b, f, g, c), (c, g, hh, dd), (dd, hh, e, a)):
            self.add_quad(*q, mat)

    def add_cyl(self, cx, cy, z0, z1, r, mat, seg=12, axis="Z", cap=True, r2=None, rot=0.0):
        """Cylinder (or truncated cone when r2 is given) along axis."""
        r2 = r if r2 is None else r2
        pts0, pts1 = [], []
        for i in range(seg):
            a = rot + 2 * math.pi * i / seg
            ca, sa = math.cos(a), math.sin(a)
            if axis == "Z":
                pts0.append((cx + ca * r, cy + sa * r, z0))
                pts1.append((cx + ca * r2, cy + sa * r2, z1))
            elif axis == "X":
                pts0.append((cx, cy + ca * r, z0 + sa * r))
                pts1.append((cx, cy + ca * r2, z1 + sa * r2))
            else:
                pts0.append((cx + ca * r, cy, z0 + sa * r))
                pts1.append((cx + ca * r2, cy, z1 + sa * r2))
        for i in range(seg):
            j = (i + 1) % seg
            self.add_quad(pts0[i], pts0[j], pts1[j], pts1[i], mat)
        if cap:
            self.add_face(list(reversed(pts0)), mat)
            self.add_face(pts1, mat)

    def add_disc(self, cx, cy, cz, r, mat, seg=16, axis="Z", flip=False):
        pts = []
        for i in range(seg):
            a = 2 * math.pi * i / seg
            ca, sa = math.cos(a), math.sin(a)
            if axis == "Z":
                pts.append((cx + ca * r, cy + sa * r, cz))
            elif axis == "X":
                pts.append((cx, cy + ca * r, cz + sa * r))
            else:
                pts.append((cx + ca * r, cy, cz + sa * r))
        if flip:
            pts.reverse()
        self.add_face(pts, mat)

    def add_prism(self, profile, axis, a0, a1, mat, close=True):
        """Extrude a 2D profile along axis ('X'|'Y'|'Z') from a0 to a1."""
        def mk(a, u, v):
            if axis == "Z": return (u, v, a)
            if axis == "X": return (a, u, v)
            return (u, a, v)
        A = [mk(a0, u, v) for u, v in profile]
        B = [mk(a1, u, v) for u, v in profile]
        n = len(profile)
        for i in range(n if close else n - 1):
            j = (i + 1) % n
            self.add_quad(A[i], A[j], B[j], B[i], mat)
        self.add_face(list(reversed(A)), mat)
        self.add_face(B, mat)

    def add_grid_quad(self, x0, y0, x1, y1, z, mat, step=8.0, uv_off=(0.0, 0.0)):
        """A horizontal surface subdivided into cells to avoid shading artefacts."""
        nx = max(1, int(abs(x1 - x0) / step))
        ny = max(1, int(abs(y1 - y0) / step))
        for i in range(nx):
            ax = x0 + (x1 - x0) * i / nx
            bx = x0 + (x1 - x0) * (i + 1) / nx
            for j in range(ny):
                ay = y0 + (y1 - y0) * j / ny
                by = y0 + (y1 - y0) * (j + 1) / ny
                self.add_quad((ax, ay, z), (bx, ay, z), (bx, by, z), (ax, by, z),
                              mat, uv_off=uv_off)

    def add_gable_roof(self, x0, y0, x1, y1, z_eave, pitch_deg, mat, gable="Y",
                       overhang=0.35, ridge_mat=None, end_mat=None):
        """Pitched roof with fully closed solid triangular gable masonry ends and bargeboards.
        
        gable='Y' means the ridge runs parallel to Y (gables at y0 and y1).
        gable='X' means the ridge runs parallel to X (gables at x0 and x1).
        """
        em = end_mat or mat
        rise = (min(x1 - x0, y1 - y0) / 2) * math.tan(math.radians(pitch_deg))
        z_r = z_eave + rise
        ex0, ey0, ex1, ey1 = x0 - overhang, y0 - overhang, x1 + overhang, y1 + overhang

        if gable == "Y":       # ridge runs parallel to Y (roof slopes West and East)
            xm = (x0 + x1) / 2
            # West slope (faces -X, +Z)
            self.add_quad((ex0, ey0, z_eave), (ex0, ey1, z_eave), (xm, ey1, z_r), (xm, ey0, z_r), mat)
            self.add_quad((xm, ey0, z_r), (xm, ey1, z_r), (ex0, ey1, z_eave), (ex0, ey0, z_eave), "interior")
            # East slope (faces +X, +Z)
            self.add_quad((xm, ey0, z_r), (xm, ey1, z_r), (ex1, ey1, z_eave), (ex1, ey0, z_eave), mat)
            self.add_quad((ex1, ey0, z_eave), (ex1, ey1, z_eave), (xm, ey1, z_r), (xm, ey0, z_r), "interior")
            # Solid horizontal ceiling plate closing eaves
            self.add_box(x0 + 0.1, y0 + 0.1, z_eave - 0.08, x1 - 0.1, y1 - 0.1, z_eave, "interior")
            # Ridge roll / lead cap along the apex
            self.add_box(xm - 0.14, ey0, z_r - 0.06, xm + 0.14, ey1, z_r + 0.10, ridge_mat or "lead")
            # Eaves fascia + cast-iron gutters
            for ex in (ex0, ex1):
                self.add_box(ex - 0.05, ey0, z_eave - 0.22, ex + 0.08, ey1, z_eave, "timber")
                self.add_box(ex - 0.12, ey0, z_eave - 0.32, ex + 0.02, ey1, z_eave - 0.18, "iron")

            # SOLID MASONRY GABLE ENDS (completely closing the roof cavity)
            # South gable at y = y0 (outward normal pointing -Y):
            self.add_tri((x0, y0, z_eave), (x1, y0, z_eave), (xm, y0, z_r), em)
            self.add_tri((xm, y0, z_r), (x1, y0, z_eave), (x0, y0, z_eave), em)
            # North gable at y = y1 (outward normal pointing +Y):
            self.add_tri((x1, y1, z_eave), (x0, y1, z_eave), (xm, y1, z_r), em)
            self.add_tri((xm, y1, z_r), (x0, y1, z_eave), (x1, y1, z_eave), em)

            # Verge bargeboard trim along the roof slope overhangs
            for ey, sgn in ((ey0, -1), (ey1, 1)):
                # West bargeboard
                self.add_beam((ex0, ey, z_eave), (xm, ey, z_r), 0.08, 0.22, "timber")
                # East bargeboard
                self.add_beam((xm, ey, z_r), (ex1, ey, z_eave), 0.08, 0.22, "timber")
        else:                  # ridge runs parallel to X (roof slopes South and North)
            ym = (y0 + y1) / 2
            # South slope (faces -Y, +Z)
            self.add_quad((ex0, ey0, z_eave), (ex1, ey0, z_eave), (ex1, ym, z_r), (ex0, ym, z_r), mat)
            self.add_quad((ex0, ym, z_r), (ex1, ym, z_r), (ex1, ey0, z_eave), (ex0, ey0, z_eave), "interior")
            # North slope (faces +Y, +Z)
            self.add_quad((ex0, ym, z_r), (ex1, ym, z_r), (ex1, ey1, z_eave), (ex0, ey1, z_eave), mat)
            self.add_quad((ex0, ey1, z_eave), (ex1, ey1, z_eave), (ex1, ym, z_r), (ex0, ym, z_r), "interior")
            # Solid horizontal ceiling plate closing eaves
            self.add_box(x0 + 0.1, y0 + 0.1, z_eave - 0.08, x1 - 0.1, y1 - 0.1, z_eave, "interior")
            # Ridge roll / lead cap
            self.add_box(ex0, ym - 0.14, z_r - 0.06, ex1, ym + 0.14, z_r + 0.10, ridge_mat or "lead")
            # Eaves fascia + cast-iron gutters
            for ey in (ey0, ey1):
                self.add_box(ex0, ey - 0.05, z_eave - 0.22, ex1, ey + 0.08, z_eave, "timber")
                self.add_box(ex0, ey - 0.12, z_eave - 0.32, ex1, ey + 0.02, z_eave - 0.18, "iron")

            # SOLID MASONRY GABLE ENDS (completely closing the roof cavity)
            # West gable at x = x0 (outward normal pointing -X):
            self.add_tri((x0, y1, z_eave), (x0, y0, z_eave), (x0, ym, z_r), em)
            self.add_tri((x0, ym, z_r), (x0, y0, z_eave), (x0, y1, z_eave), em)
            # East gable at x = x1 (outward normal pointing +X):
            self.add_tri((x1, y0, z_eave), (x1, y1, z_eave), (x1, ym, z_r), em)
            self.add_tri((x1, ym, z_r), (x1, y1, z_eave), (x1, y0, z_eave), em)

            # Verge bargeboard trim along the roof slope overhangs
            for ex in (ex0, ex1):
                self.add_beam((ex, ey0, z_eave), (ex, ym, z_r), 0.08, 0.22, "timber")
                self.add_beam((ex, ym, z_r), (ex, ey1, z_eave), 0.08, 0.22, "timber")

        return z_r

    def add_hip_roof(self, x0, y0, x1, y1, z_eave, pitch_deg, mat, overhang=0.35):
        rise = (min(x1 - x0, y1 - y0) / 2) * math.tan(math.radians(pitch_deg))
        z_r = z_eave + rise
        ex0, ey0, ex1, ey1 = x0 - overhang, y0 - overhang, x1 + overhang, y1 + overhang
        cx, cy = (ex0 + ex1) / 2, (ey0 + ey1) / 2
        ins = min(ex1 - ex0, ey1 - ey0) / 2
        if (ex1 - ex0) >= (ey1 - ey0):
            ra, rb = (ex0 + ins, cy, z_r), (ex1 - ins, cy, z_r)
        else:
            ra, rb = (cx, ey0 + ins, z_r), (cx, ey1 - ins, z_r)
        # Top roof slopes
        self.add_quad((ex0, ey0, z_eave), (ex1, ey0, z_eave), rb, ra, mat)
        self.add_quad((ex1, ey1, z_eave), (ex0, ey1, z_eave), ra, rb, mat)
        self.add_tri((ex1, ey0, z_eave), (ex1, ey1, z_eave), rb, mat)
        self.add_tri((ex0, ey1, z_eave), (ex0, ey0, z_eave), ra, mat)
        # Underside ceiling slopes (prevents backface culling)
        self.add_quad(ra, rb, (ex1, ey0, z_eave), (ex0, ey0, z_eave), "interior")
        self.add_quad(rb, ra, (ex0, ey1, z_eave), (ex1, ey1, z_eave), "interior")
        self.add_tri(rb, (ex1, ey1, z_eave), (ex1, ey0, z_eave), "interior")
        self.add_tri(ra, (ex0, ey0, z_eave), (ex0, ey1, z_eave), "interior")
        # Solid horizontal ceiling plate across eaves
        self.add_box(x0 + 0.1, y0 + 0.1, z_eave - 0.08, x1 - 0.1, y1 - 0.1, z_eave, "interior")
        # Gutters along all four eaves
        for ex in (ex0, ex1):
            self.add_box(ex - 0.10, ey0, z_eave - 0.32, ex + 0.02, ey1, z_eave - 0.18, "iron")
        for ey in (ey0, ey1):
            self.add_box(ex0, ey - 0.10, z_eave - 0.32, ex1, ey + 0.02, z_eave - 0.18, "iron")
        return z_r

    # -- combination -------------------------------------------------------
    def extend(self, other):
        base = len(self.verts)
        self.verts.extend(other.verts)
        for f, m, uv in zip(other.faces, other.fmats, other.fuvs):
            self.faces.append(tuple(i + base for i in f))
            self.fmats.append(m)
            self.fuvs.append(uv)
        return self

    def stats(self):
        tris = sum(max(1, len(f) - 2) for f in self.faces)
        return len(self.verts), len(self.faces), tris

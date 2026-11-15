"""
geom.py -- lightweight geometry kernel for the OPERATION VICTORIA ship's boats.

Pure numpy.  Everything is built as explicit vertex/face lists so that the
result is fully deterministic and inspectable, then handed to bmesh.

Conventions
-----------
  X  : longitudinal, +X = forward (towards the stem / bow)
  Y  : transverse,  +Y = port side
  Z  : vertical,    +Z = up
  Z = 0 is the design / load waterline of the boat.
  Origin on the centreline, longitudinally at the midpoint of the length
  overall (see interfaces/boats_spec.json).

Written for Blender 4.2 (bpy) but the maths is pure numpy so it can be unit
tested outside Blender.
"""

from __future__ import annotations

import math

import numpy as np

# --------------------------------------------------------------------------
# small vector helpers
# --------------------------------------------------------------------------


def unit(v):
    v = np.asarray(v, dtype=float)
    n = np.linalg.norm(v)
    return v / n if n > 1e-12 else np.array([0.0, 0.0, 1.0])


def lerp(a, b, t):
    return a + (b - a) * t


def clamp(x, lo=0.0, hi=1.0):
    return np.clip(x, lo, hi)


def smoothstep(e0, e1, x):
    if e1 == e0:
        return np.zeros_like(np.asarray(x, dtype=float))
    t = np.clip((np.asarray(x, dtype=float) - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


# --------------------------------------------------------------------------
# monotone cubic interpolation (PCHIP / Fritsch-Carlson)
# --------------------------------------------------------------------------
# Used for every "faired" curve in the project: half-breadth curves, sheer
# lines, keel rocker, diagonal planking offsets.  PCHIP is chosen over a
# natural cubic spline deliberately: it cannot overshoot, so a designer's
# control points can never produce a bump or a hollow in a hull line, which
# is exactly the property a naval architect works to.


class Pchip:
    """Monotone piecewise-cubic Hermite interpolant (Fritsch-Carlson)."""

    def __init__(self, xs, ys):
        self.x = np.asarray(xs, dtype=float)
        self.y = np.asarray(ys, dtype=float)
        order = np.argsort(self.x)
        self.x = self.x[order]
        self.y = self.y[order]
        n = len(self.x)
        h = np.diff(self.x)
        d = np.diff(self.y) / h
        m = np.zeros(n)
        if n == 2:
            m[:] = d[0]
        else:
            for i in range(1, n - 1):
                if d[i - 1] * d[i] <= 0.0:
                    m[i] = 0.0
                else:
                    w1 = 2.0 * h[i] + h[i - 1]
                    w2 = h[i] + 2.0 * h[i - 1]
                    m[i] = (w1 + w2) / (w1 / d[i - 1] + w2 / d[i])
            # endpoint slope (shape-preserving one-sided estimate)
            m[0] = ((2.0 * h[0] + h[1]) * d[0] - h[0] * d[1]) / (h[0] + h[1])
            if m[0] * d[0] <= 0.0:
                m[0] = 0.0
            elif abs(m[0]) > 3.0 * abs(d[0]):
                m[0] = 3.0 * d[0]
            m[-1] = ((2.0 * h[-1] + h[-2]) * d[-1] - h[-1] * d[-2]) / (h[-1] + h[-2])
            if m[-1] * d[-1] <= 0.0:
                m[-1] = 0.0
            elif abs(m[-1]) > 3.0 * abs(d[-1]):
                m[-1] = 3.0 * d[-1]
        self.m = m

    def __call__(self, x):
        scalar = np.isscalar(x)
        x = np.atleast_1d(np.asarray(x, dtype=float))
        x = np.clip(x, self.x[0], self.x[-1])
        i = np.clip(np.searchsorted(self.x, x) - 1, 0, len(self.x) - 2)
        h = self.x[i + 1] - self.x[i]
        t = (x - self.x[i]) / h
        t2, t3 = t * t, t * t * t
        h00 = 2 * t3 - 3 * t2 + 1
        h10 = t3 - 2 * t2 + t
        h01 = -2 * t3 + 3 * t2
        h11 = t3 - t2
        y = (
            h00 * self.y[i]
            + h10 * h * self.m[i]
            + h01 * self.y[i + 1]
            + h11 * h * self.m[i + 1]
        )
        return float(y[0]) if scalar else y


def curve(pts):
    """Convenience: build a Pchip from a list of (x, y) pairs."""
    pts = np.asarray(pts, dtype=float)
    return Pchip(pts[:, 0], pts[:, 1])


# --------------------------------------------------------------------------
# mesh accumulation
# --------------------------------------------------------------------------


class MeshBuilder:
    """Accumulates verts/faces (optionally with per-face material index)."""

    def __init__(self, name="part"):
        self.name = name
        self.verts = []
        self.faces = []
        self.face_mats = []
        self.mat_indices = []  # material index for each face

    # ---- low level -------------------------------------------------------
    def add_verts(self, pts):
        base = len(self.verts)
        for p in pts:
            self.verts.append((float(p[0]), float(p[1]), float(p[2])))
        return base

    def add_face(self, idx, mat=0):
        if len(idx) >= 3:
            self.faces.append(tuple(int(i) for i in idx))
            self.mat_indices.append(mat)

    # ---- grid ------------------------------------------------------------
    def add_grid(self, grid, mat=0, close_u=False, close_v=False, flip=False):
        """grid: array (nu, nv, 3).  Quads between consecutive rows/cols."""
        grid = np.asarray(grid, dtype=float)
        nu, nv = grid.shape[0], grid.shape[1]
        base = self.add_verts(grid.reshape(-1, 3))
        for i in range(nu - 1 + (1 if close_u else 0)):
            i2 = (i + 1) % nu
            for j in range(nv - 1 + (1 if close_v else 0)):
                j2 = (j + 1) % nv
                a = base + i * nv + j
                b = base + i * nv + j2
                c = base + i2 * nv + j2
                d = base + i2 * nv + j
                self.add_face([a, b, c, d][::-1] if flip else [a, b, c, d], mat)
        return base

    def add_quad(self, p0, p1, p2, p3, mat=0, flip=False):
        b = self.add_verts([p0, p1, p2, p3])
        idx = [b, b + 1, b + 2, b + 3]
        self.add_face(idx[::-1] if flip else idx, mat)

    def add_tri(self, p0, p1, p2, mat=0, flip=False):
        b = self.add_verts([p0, p1, p2])
        idx = [b, b + 1, b + 2]
        self.add_face(idx[::-1] if flip else idx, mat)

    # ---- solids ----------------------------------------------------------
    def add_box(self, center, size, rot=None, mat=0):
        """Axis-aligned box, optionally rotated by a 3x3 matrix about center."""
        cx, cy, cz = center
        sx, sy, sz = (s * 0.5 for s in size)
        corners = np.array(
            [
                [-sx, -sy, -sz],
                [sx, -sy, -sz],
                [sx, sy, -sz],
                [-sx, sy, -sz],
                [-sx, -sy, sz],
                [sx, -sy, sz],
                [sx, sy, sz],
                [-sx, sy, sz],
            ]
        )
        if rot is not None:
            corners = corners @ np.asarray(rot).T
        corners = corners + np.array([cx, cy, cz])
        b = self.add_verts(corners)
        quads = [
            (0, 3, 2, 1),
            (4, 5, 6, 7),
            (0, 1, 5, 4),
            (1, 2, 6, 5),
            (2, 3, 7, 6),
            (3, 0, 4, 7),
        ]
        for q in quads:
            self.add_face([b + i for i in q], mat)

    def add_prism(self, pts_bottom, pts_top, mat=0, cap=True):
        """Straight-sided prism between two equal-length rings."""
        pb = np.asarray(pts_bottom, dtype=float)
        pt = np.asarray(pts_top, dtype=float)
        n = len(pb)
        bb = self.add_verts(pb)
        bt = self.add_verts(pt)
        for i in range(n):
            j = (i + 1) % n
            self.add_face([bb + i, bb + j, bt + j, bt + i], mat)
        if cap:
            self.add_face([bb + i for i in range(n)][::-1], mat)
            self.add_face([bt + i for i in range(n)], mat)

    def add_lathe(self, profile, segments=24, axis="Z", center=(0, 0, 0), mat=0, close=False):
        """Revolve a 2-D profile [(r, h), ...] about an axis."""
        prof = np.asarray(profile, dtype=float)
        ang = np.linspace(0, 2 * math.pi, segments, endpoint=False)
        rings = []
        for r, h in prof:
            ring = []
            for a in ang:
                if axis == "Z":
                    p = (r * math.cos(a), r * math.sin(a), h)
                elif axis == "X":
                    p = (h, r * math.cos(a), r * math.sin(a))
                else:
                    p = (r * math.cos(a), h, r * math.sin(a))
                ring.append(np.array(p) + np.array(center, dtype=float))
            rings.append(ring)
        grid = np.array(rings)
        self.add_grid(grid, mat, close_v=True)

    def add_tube(self, path, radius, segments=12, mat=0, caps=True, radii=None):
        """Sweep a circle of `radius` along a polyline path (list of points)."""
        path = np.asarray(path, dtype=float)
        n = len(path)
        tangents = np.zeros_like(path)
        for i in range(n):
            if i == 0:
                tangents[i] = path[1] - path[0]
            elif i == n - 1:
                tangents[i] = path[-1] - path[-2]
            else:
                tangents[i] = path[i + 1] - path[i - 1]
        tangents = np.array([unit(t) for t in tangents])
        # parallel-transport frame
        up = np.array([0.0, 0.0, 1.0])
        if abs(np.dot(tangents[0], up)) > 0.95:
            up = np.array([1.0, 0.0, 0.0])
        normals = []
        nrm = unit(np.cross(tangents[0], up))
        normals.append(nrm)
        for i in range(1, n):
            prev = normals[-1]
            t = tangents[i]
            proj = prev - t * np.dot(prev, t)
            if np.linalg.norm(proj) < 1e-9:
                proj = np.cross(t, up)
            normals.append(unit(proj))
        ang = np.linspace(0, 2 * math.pi, segments, endpoint=False)
        rings = []
        for i in range(n):
            t = tangents[i]
            a = normals[i]
            b = np.cross(t, a)
            r = radius if radii is None else radii[i]
            ring = [path[i] + r * (math.cos(x) * a + math.sin(x) * b) for x in ang]
            rings.append(ring)
        self.add_grid(np.array(rings), mat, close_v=True)
        if caps:
            self.add_face([len(self.verts) - 1 - i for i in range(segments)], mat)
            base = len(self.verts) - segments * n
            self.add_face([base + i for i in range(segments)][::-1], mat)

    # ---- symmetry --------------------------------------------------------
    def mirror_y(self):
        """Append an XZ-mirror of everything built so far (starboard half).

        Half-hull construction is the classical way to build a boat model:
        the port side is lofted once and mirrored, guaranteeing symmetry to
        the micron.  Winding is reversed on the copy so shading stays correct.
        """
        n0 = len(self.verts)
        nf0 = len(self.faces)
        for (x, y, z) in list(self.verts):
            self.verts.append((x, -y, z))
        for f, m in zip(list(self.faces[:nf0]), list(self.mat_indices[:nf0])):
            self.faces.append(tuple(n0 + i for i in reversed(f)))
            self.mat_indices.append(m)
        return self

    # ---- output ----------------------------------------------------------
    def to_bmesh(self, bm, mat_remap=None):
        import bmesh

        bverts = [bm.verts.new(v) for v in self.verts]
        bm.verts.index_update()
        faces = []
        for f, m in zip(self.faces, self.mat_indices):
            try:
                face = bm.faces.new([bverts[i] for i in f])
                face.material_index = m if mat_remap is None else mat_remap.get(m, m)
                faces.append(face)
            except ValueError:
                pass  # duplicate face -- harmless, skip
        bm.faces.index_update()
        return faces

    def bounds(self):
        v = np.array(self.verts)
        return v.min(axis=0), v.max(axis=0)


# --------------------------------------------------------------------------
# generic solid generators used by the machinery and fittings libraries
# --------------------------------------------------------------------------


def box(mb, center, size, rot=None, mat=0):
    mb.add_box(center, size, rot=rot, mat=mat)


def cyl(mb, p0, p1, r, seg=16, mat=0, r1=None, caps=True):
    """Cylinder (optionally conical) between two points."""
    p0 = np.asarray(p0, dtype=float)
    p1 = np.asarray(p1, dtype=float)
    axis = p1 - p0
    length = np.linalg.norm(axis)
    if length < 1e-9:
        return
    t = axis / length
    up = np.array([0.0, 0.0, 1.0])
    if abs(np.dot(t, up)) > 0.95:
        up = np.array([1.0, 0.0, 0.0])
    a = unit(np.cross(t, up))
    b = np.cross(t, a)
    r1 = r if r1 is None else r1
    ang = np.linspace(0, 2 * math.pi, seg, endpoint=False)
    ring0 = [p0 + r * (math.cos(x) * a + math.sin(x) * b) for x in ang]
    ring1 = [p1 + r1 * (math.cos(x) * a + math.sin(x) * b) for x in ang]
    mb.add_prism(np.array(ring0), np.array(ring1), mat, cap=caps)


def sphere(mb, center, r, seg=16, rings=10, mat=0, scale=(1, 1, 1)):
    prof = [(r * math.sin(math.pi * i / rings), -r * math.cos(math.pi * i / rings)) for i in range(rings + 1)]
    before = len(mb.verts)
    mb.add_lathe(prof, segments=seg, center=center, mat=mat)
    if scale != (1, 1, 1):
        for i in range(before, len(mb.verts)):
            v = np.array(mb.verts[i]) - np.array(center)
            v = v * np.array(scale)
            mb.verts[i] = tuple(v + np.array(center))


def torus(mb, center, R, r, seg=24, rseg=8, axis="Z", mat=0):
    rings = []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        ring = []
        for j in range(rseg):
            b = 2 * math.pi * j / rseg
            x = (R + r * math.cos(b)) * math.cos(a)
            y = (R + r * math.cos(b)) * math.sin(a)
            z = r * math.sin(b)
            if axis == "Z":
                p = (x, y, z)
            elif axis == "X":
                p = (z, x, y)
            else:
                p = (x, z, y)
            ring.append(np.array(p) + np.array(center, dtype=float))
        rings.append(ring)
    mb.add_grid(np.array(rings), mat, close_u=True, close_v=True)


def bolt_row(mb, path, normal, spacing, radius, height, mat=0, seg=6):
    """A row of rivet heads / bolt heads along a path."""
    path = np.asarray(path, dtype=float)
    d = np.linalg.norm(np.diff(path, axis=0), axis=1)
    s = np.concatenate([[0.0], np.cumsum(d)])
    total = s[-1]
    n = max(2, int(total / spacing))
    for i in range(n + 1):
        target = total * i / n
        k = np.searchsorted(s, target) - 1
        k = max(0, min(k, len(path) - 2))
        t = (target - s[k]) / max(1e-9, s[k + 1] - s[k])
        p = lerp(path[k], path[k + 1], t)
        nrm = unit(normal(k) if callable(normal) else normal)
        cyl(mb, p, p + nrm * height, radius, seg=seg, mat=mat, caps=True)

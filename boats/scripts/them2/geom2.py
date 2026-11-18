"""
geom2.py -- THEMISTOCLES-II mesh kernel.  Pure numpy, explicit verts/faces,
per-face material indices.  Frame: +X fwd (stem), +Y port, +Z up, Z=0 = LWL.
"""

from __future__ import annotations
import math
import numpy as np


def unit(v):
    v = np.asarray(v, dtype=float)
    n = np.linalg.norm(v)
    return v / n if n > 1e-12 else np.array([0.0, 0.0, 1.0])


def lerp(a, b, t):
    return a + (b - a) * t


def clamp(x, lo=0.0, hi=1.0):
    return np.clip(x, lo, hi)


def smoothstep(e0, e1, x):
    d = e1 - e0
    t = np.clip((np.asarray(x, dtype=float) - e0) / (d if abs(d) > 1e-12 else 1e-12),
                0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def rot_axis(axis, ang):
    a = unit(axis)
    x, y, z = a
    c, s = math.cos(ang), math.sin(ang)
    C = 1.0 - c
    return np.array([
        [c + x * x * C, x * y * C - z * s, x * z * C + y * s],
        [y * x * C + z * s, c + y * y * C, y * z * C - x * s],
        [z * x * C - y * s, z * y * C + x * s, c + z * z * C]])


def rot_x(a): return rot_axis([1, 0, 0], a)
def rot_y(a): return rot_axis([0, 1, 0], a)
def rot_z(a): return rot_axis([0, 0, 1], a)


class Pchip:
    """Monotone piecewise-cubic Hermite interpolant (faired lines)."""

    def __init__(self, xs, ys):
        self.x = np.asarray(xs, dtype=float)
        self.y = np.asarray(ys, dtype=float)
        o = np.argsort(self.x)
        self.x = self.x[o]; self.y = self.y[o]
        n = len(self.x)
        h = np.diff(self.x); d = np.diff(self.y) / h
        m = np.zeros(n)
        if n == 2:
            m[:] = d[0]
        else:
            for i in range(1, n - 1):
                if d[i - 1] * d[i] <= 0.0:
                    m[i] = 0.0
                else:
                    w1 = 2.0 * h[i] + h[i - 1]; w2 = h[i] + 2.0 * h[i - 1]
                    m[i] = (w1 + w2) / (w1 / d[i - 1] + w2 / d[i])
            m[0] = ((2 * h[0] + h[1]) * d[0] - h[0] * d[1]) / (h[0] + h[1])
            if m[0] * d[0] <= 0: m[0] = 0.0
            elif abs(m[0]) > 3 * abs(d[0]): m[0] = 3 * d[0]
            m[-1] = ((2 * h[-1] + h[-2]) * d[-1] - h[-1] * d[-2]) / (h[-1] + h[-2])
            if m[-1] * d[-1] <= 0: m[-1] = 0.0
            elif abs(m[-1]) > 3 * abs(d[-1]): m[-1] = 3 * d[-1]
        self.m = m

    def __call__(self, x):
        scalar = np.isscalar(x)
        x = np.atleast_1d(np.asarray(x, dtype=float))
        x = np.clip(x, self.x[0], self.x[-1])
        i = np.clip(np.searchsorted(self.x, x) - 1, 0, len(self.x) - 2)
        h = self.x[i + 1] - self.x[i]
        t = (x - self.x[i]) / h
        t2, t3 = t * t, t * t * t
        y = ((2 * t3 - 3 * t2 + 1) * self.y[i] + (t3 - 2 * t2 + t) * h * self.m[i]
             + (-2 * t3 + 3 * t2) * self.y[i + 1] + (t3 - t2) * h * self.m[i + 1])
        return float(y[0]) if scalar else y


def curve(pts):
    pts = np.asarray(pts, dtype=float)
    return Pchip(pts[:, 0], pts[:, 1])


def triangulate_polygon(poly):
    """Ear-clipping of a simple CCW 2-D polygon -> list of index triples."""
    poly = np.asarray(poly, dtype=float)
    n = len(poly)
    if n < 3:
        return []
    area = 0.0
    for i in range(n):
        x0, y0 = poly[i]; x1, y1 = poly[(i + 1) % n]
        area += x0 * y1 - x1 * y0
    idx = list(range(n)) if area > 0 else list(range(n))[::-1]

    def cross(i, j, k):
        a, b, c = poly[i], poly[j], poly[k]
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

    def inside(p, a, b, c):
        for (u, v) in ((a, b), (b, c), (c, a)):
            if (v[0] - u[0]) * (p[1] - u[1]) - (v[1] - u[1]) * (p[0] - u[0]) <= 0:
                return False
        return True

    tris = []
    guard = 0
    while len(idx) > 3 and guard < 9999:
        guard += 1
        cut = False
        m = len(idx)
        for k in range(m):
            i0, i1, i2 = idx[(k - 1) % m], idx[k], idx[(k + 1) % m]
            if cross(i0, i1, i2) <= 1e-14:
                continue
            if any(inside(poly[j], poly[i0], poly[i1], poly[i2])
                   for j in idx if j not in (i0, i1, i2)):
                continue
            tris.append((i0, i1, i2)); idx.pop(k); cut = True
            break
        if not cut:
            break
    if len(idx) == 3:
        tris.append(tuple(idx))
    else:
        for k in range(1, len(idx) - 1):
            tris.append((idx[0], idx[k], idx[k + 1]))
    return tris


class MB:
    """Mesh accumulator: verts, faces, per-face material index."""

    def __init__(self, name="part"):
        self.name = name
        self.verts = []
        self.faces = []
        self.mat_indices = []

    def add_verts(self, pts):
        base = len(self.verts)
        for p in pts:
            self.verts.append((float(p[0]), float(p[1]), float(p[2])))
        return base

    def add_face(self, idx, mat=0):
        idx = tuple(int(i) for i in idx)
        if len(idx) >= 3:
            self.faces.append(idx)
            self.mat_indices.append(int(mat))
        return self

    # -- grids -----------------------------------------------------------
    def add_grid(self, grid, mat=0, close_u=False, close_v=False, flip=False):
        grid = np.asarray(grid, dtype=float)
        nu, nv = grid.shape[0], grid.shape[1]
        base = self.add_verts(grid.reshape(-1, 3))
        for i in range(nu - 1 + (1 if close_u else 0)):
            i2 = (i + 1) % nu
            for j in range(nv - 1 + (1 if close_v else 0)):
                j2 = (j + 1) % nv
                f = [base + i * nv + j, base + i * nv + j2,
                     base + i2 * nv + j2, base + i2 * nv + j]
                self.add_face(f[::-1] if flip else f, mat)
        return base

    def add_cap_fan(self, ring_base, nv, center, mat=0, flip=False):
        c = self.add_verts([center])
        for j in range(nv):
            j2 = (j + 1) % nv
            f = [c, ring_base + j, ring_base + j2]
            self.add_face(f[::-1] if flip else f, mat)

    # -- solids ------------------------------------------------------------
    def add_box(self, center, size, mat=0, rot=None, chamfer=0.0):
        cx, cy, cz = center
        hx, hy, hz = (s * 0.5 for s in size)
        c = min(chamfer, hx * 0.45, hy * 0.45, hz * 0.45)
        if c > 1e-6:
            hx1, hy1, hz1 = hx - c, hy - c, hz - c
        else:
            hx1, hy1, hz1 = hx, hy, hz
        # 6 face quads built point-wise so chamfers can join them
        def P(x, y, z):
            p = np.array([x, y, z])
            if rot is not None:
                p = rot @ p
            return p + np.array([cx, cy, cz])
        F = {}

        def face(axis, sign):
            n = 4
            pts = []
            for (a, b) in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                if axis == 0:
                    pts.append(P(sign * hx, a * (hy1 if c else hy), b * (hz1 if c else hz)))
                elif axis == 1:
                    pts.append(P(a * (hx1 if c else hx), sign * hy, b * (hz1 if c else hz)))
                else:
                    pts.append(P(a * (hx1 if c else hx), b * (hy1 if c else hy), sign * hz))
            b0 = self.add_verts(pts)
            if sign > 0:
                self.add_face([b0, b0 + 1, b0 + 2, b0 + 3], mat)
            else:
                self.add_face([b0 + 3, b0 + 2, b0 + 1, b0], mat)
            F[(axis, sign)] = [list(pts)] if c else None

        for ax in range(3):
            for sg in (-1, 1):
                face(ax, sg)
        if c > 1e-6:
            # chamfer strips along the 12 edges + 8 corner tris
            def corner(x, y, z, key_axis):
                # the vert of corner (x,y,z) on the face perpendicular to key_axis
                if key_axis == 0:
                    return (x * hx, y * hy1, z * hz1)
                if key_axis == 1:
                    return (x * hx1, y * hy, z * hz1)
                return (x * hx1, y * hy1, z * hz)
            for ya in (-1, 1):
                for za in (-1, 1):  # edges parallel X
                    a = corner(-1, ya, za, 1); b = corner(1, ya, za, 1)
                    d = corner(1, ya, za, 2); e = corner(-1, ya, za, 2)
                    q = [P(*a), P(*b), P(*d), P(*e)]
                    b0 = self.add_verts(q)
                    self.add_face([b0 + s for s in ([0, 1, 2, 3] if ya * za < 0 else [3, 2, 1, 0])], mat)
            for xa in (-1, 1):
                for za in (-1, 1):  # edges parallel Y
                    a = corner(xa, -1, za, 0); b = corner(xa, 1, za, 0)
                    d = corner(xa, 1, za, 2); e = corner(xa, -1, za, 2)
                    q = [P(*a), P(*b), P(*d), P(*e)]
                    b0 = self.add_verts(q)
                    self.add_face([b0 + s for s in ([0, 1, 2, 3] if xa * za > 0 else [3, 2, 1, 0])], mat)
            for xa in (-1, 1):
                for ya in (-1, 1):  # edges parallel Z
                    a = corner(xa, ya, -1, 0); b = corner(xa, ya, 1, 0)
                    d = corner(xa, ya, 1, 1); e = corner(xa, ya, -1, 1)
                    q = [P(*a), P(*b), P(*d), P(*e)]
                    b0 = self.add_verts(q)
                    self.add_face([b0 + s for s in ([0, 1, 2, 3] if xa * ya < 0 else [3, 2, 1, 0])], mat)
            for xa in (-1, 1):
                for ya in (-1, 1):
                    for za in (-1, 1):
                        q = [P(*corner(xa, ya, za, 0)), P(*corner(xa, ya, za, 1)),
                             P(*corner(xa, ya, za, 2))]
                        b0 = self.add_verts(q)
                        self.add_face([b0, b0 + 1, b0 + 2] if xa * ya * za > 0 else [b0 + 2, b0 + 1, b0], mat)
        return self

    def add_prism(self, pts_bottom, pts_top, mat=0, cap=True):
        pb = np.asarray(pts_bottom, dtype=float)
        pt = np.asarray(pts_top, dtype=float)
        n = len(pb)
        bb = self.add_verts(pb); bt = self.add_verts(pt)
        for i in range(n):
            j = (i + 1) % n
            self.add_face([bb + i, bb + j, bt + j, bt + i], mat)
        if cap:
            self.add_face([bb + i for i in range(n)][::-1], mat)
            self.add_face([bt + i for i in range(n)], mat)
        return self

    def add_plate(self, outline, thickness, plane="XZ", origin=(0, 0, 0),
                  basis=None, mat=0):
        """Solid plate from a simple 2-D outline; spans [0, thickness] along n3."""
        pts = np.asarray(outline, dtype=float)
        if basis is not None:
            u3, v3, n3 = (np.asarray(a, dtype=float) for a in basis)
        elif plane == "XY":
            u3, v3, n3 = (np.array([1., 0, 0]), np.array([0., 1, 0]), np.array([0., 0, 1]))
        elif plane == "XZ":
            u3, v3, n3 = (np.array([1., 0, 0]), np.array([0., 0, 1]), np.array([0., -1, 0]))
        else:
            u3, v3, n3 = (np.array([0., 1, 0]), np.array([0., 0, 1]), np.array([1., 0, 0]))
        org = np.asarray(origin, dtype=float)
        n3u = unit(n3)
        p0 = org[None, :] + pts[:, :1] * u3[None, :] + pts[:, 1:2] * v3[None, :]
        p1 = p0 + n3u * thickness
        tris = triangulate_polygon(pts)
        b0 = self.add_verts(p0); b1 = self.add_verts(p1)
        for (i0, i1, i2) in tris:
            self.add_face([b0 + i2, b0 + i1, b0 + i0], mat)
            self.add_face([b1 + i0, b1 + i1, b1 + i2], mat)
        n = len(pts)
        for i in range(n):
            j = (i + 1) % n
            self.add_face([b0 + i, b0 + j, b1 + j, b1 + i], mat)
        return self

    def add_lathe(self, profile, segments=24, axis="Z", center=(0, 0, 0), mat=0,
                  cap_lo=False, cap_hi=False):
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
        base = self.add_grid(np.array(rings), mat, close_v=True)
        npr = len(prof)
        if cap_lo:
            offs = {"Z": np.array([0, 0, prof[0][1]]), "X": np.array([prof[0][1], 0, 0]),
                    "Y": np.array([0, prof[0][1], 0])}[axis]
            self.add_cap_fan(base, segments, np.array(center) + offs, mat, flip=True)
        if cap_hi:
            offs = {"Z": np.array([0, 0, prof[-1][1]]), "X": np.array([prof[-1][1], 0, 0]),
                    "Y": np.array([0, prof[-1][1], 0])}[axis]
            self.add_cap_fan(base + (npr - 1) * segments, segments,
                             np.array(center) + offs, mat)
        return self

    def add_tube(self, path, radius, segments=12, mat=0, caps=True, radii=None,
                 oval=None):
        path = np.asarray(path, dtype=float)
        n = len(path)
        tang = np.zeros_like(path)
        for i in range(n):
            if i == 0:
                tang[i] = path[1] - path[0]
            elif i == n - 1:
                tang[i] = path[-1] - path[-2]
            else:
                tang[i] = path[i + 1] - path[i - 1]
        tang = np.array([unit(t) for t in tang])
        up = np.array([0., 0, 1])
        if abs(np.dot(tang[0], up)) > 0.95:
            up = np.array([1., 0, 0])
        nrm = unit(np.cross(tang[0], up))
        normals = [nrm]
        for i in range(1, n):
            proj = normals[-1] - tang[i] * np.dot(normals[-1], tang[i])
            if np.linalg.norm(proj) < 1e-9:
                proj = np.cross(tang[i], up)
            normals.append(unit(proj))
        ang = np.linspace(0, 2 * math.pi, segments, endpoint=False)
        rings = []
        for i in range(n):
            a = normals[i]; b = np.cross(tang[i], a)
            r = radius if radii is None else radii[i]
            if isinstance(r, (tuple, list)):
                ra, rb = r
            else:
                ra, rb = (r, r) if oval is None else (r * oval[0], r * oval[1])
            rings.append([path[i] + math.cos(x) * ra * a + math.sin(x) * rb * b
                          for x in ang])
        base = self.add_grid(np.array(rings), mat, close_v=True)
        if caps:
            self.add_face([base + i for i in range(segments)][::-1], mat)
            l0 = base + (n - 1) * segments
            self.add_face([l0 + i for i in range(segments)], mat)
        return self

    def add_sweep(self, path, shapes, frames=None, caps=True, mat=0):
        """Loft varying 2-D sections along a path; shapes[i]: (k,2)."""
        path = np.asarray(path, dtype=float)
        m = len(path)
        if not isinstance(shapes, list) or (len(shapes) > 0 and np.ndim(shapes[0]) == 1
                                            and len(shapes) == 2):
            shapes = [np.asarray(shapes, dtype=float)] * m
        k = len(shapes[0])
        tang = np.zeros_like(path)
        for i in range(m):
            di = path[min(i + 1, m - 1)] - path[max(i - 1, 0)]
            tang[i] = di
        tang = np.array([unit(t) for t in tang])
        if frames is None:
            up = np.array([0., 0, 1])
            if abs(np.dot(tang[0], up)) > 0.95:
                up = np.array([1., 0, 0])
            u = unit(np.cross(tang[0], up))
            us = [u]
            for i in range(1, m):
                proj = us[-1] - tang[i] * np.dot(us[-1], tang[i])
                if np.linalg.norm(proj) < 1e-9:
                    proj = np.cross(tang[i], up)
                us.append(unit(proj))
            frames = [(us[i], unit(np.cross(tang[i], us[i]))) for i in range(m)]
        rings = []
        for i in range(m):
            u3, v3 = frames[i]
            s = np.asarray(shapes[i], dtype=float)
            rings.append(path[i][None, :] + s[:, :1] * u3[None, :] + s[:, 1:2] * v3[None, :])
        base = self.add_grid(np.array(rings), mat, close_v=True)
        if caps:
            c0 = self.add_verts([path[0]])
            for j in range(k):
                self.add_face([c0, base + j, base + (j + 1) % k], mat)
            c1 = self.add_verts([path[-1]])
            base1 = base + (m - 1) * k
            for j in range(k):
                self.add_face([c1, base1 + (j + 1) % k, base1 + j], mat)
        return base

    # -- merge / transform ---------------------------------------------------
    def append(self, other, offset=(0., 0, 0), rot=None):
        base = len(self.verts)
        off = np.asarray(offset, dtype=float)
        for v in other.verts:
            p = np.asarray(v, dtype=float)
            if rot is not None:
                p = rot @ p
            self.verts.append(tuple(p + off))
        for f, mmi in zip(other.faces, other.mat_indices):
            self.faces.append(tuple(base + i for i in f))
            self.mat_indices.append(mmi)
        return self

    def mirror_y(self):
        n0 = len(self.verts); nf0 = len(self.faces)
        for (x, y, z) in list(self.verts):
            self.verts.append((x, -y, z))
        for f, mmi in zip(list(self.faces[:nf0]), list(self.mat_indices[:nf0])):
            self.faces.append(tuple(n0 + i for i in reversed(f)))
            self.mat_indices.append(mmi)
        return self

    def bounds(self):
        v = np.array(self.verts)
        return v.min(axis=0), v.max(axis=0)


# ---------------------------------------------------------------------------
# named generators used all over the builds
# ---------------------------------------------------------------------------


def cyl(mb, p0, p1, r, seg=14, mat=0, r1=None, caps=True):
    p0 = np.asarray(p0, float); p1 = np.asarray(p1, float)
    d = p1 - p0
    L = np.linalg.norm(d)
    if L < 1e-9:
        return
    t = d / L
    up = np.array([0., 0, 1]) if abs(t[2]) < 0.95 else np.array([1., 0, 0])
    a = unit(np.cross(t, up)); b = np.cross(t, a)
    r1 = r if r1 is None else r1
    ang = np.linspace(0, 2 * math.pi, seg, endpoint=False)
    ring0 = [p0 + r * (math.cos(x) * a + math.sin(x) * b) for x in ang]
    ring1 = [p1 + r1 * (math.cos(x) * a + math.sin(x) * b) for x in ang]
    mb.add_prism(np.array(ring0), np.array(ring1), mat, cap=caps)


def sphere(mb, center, r, seg=16, rings=10, mat=0, scale=(1, 1, 1), squash_z=1.0):
    prof = [(r * math.sin(math.pi * i / rings), -r * math.cos(math.pi * i / rings) * squash_z)
            for i in range(rings + 1)]
    before = len(mb.verts)
    mb.add_lathe(prof, segments=seg, center=center, mat=mat)
    if scale != (1, 1, 1):
        c = np.array(center)
        for i in range(before, len(mb.verts)):
            mb.verts[i] = tuple((np.array(mb.verts[i]) - c) * np.array(scale) + c)


def dome(mb, center, r, seg=14, rings=6, mat=0, squash=0.6, up=(0, 0, 1)):
    """Button/dome head (rivets, bolls): squashed hemisphere on a small stem."""
    prof = [(r * math.sin(math.pi / 2 * i / rings), r * squash * math.cos(math.pi / 2 * i / rings))
            for i in range(rings + 1)]
    before = len(mb.verts)
    upward = unit(up)
    # lathe around Z then rotate into place
    mb.add_lathe(prof, segments=seg, center=(0, 0, 0), mat=mat)
    z = np.array([0., 0, 1])
    cr = np.cross(z, upward)
    if np.linalg.norm(cr) > 1e-9:
        R = rot_axis(cr, math.acos(clamp(np.dot(z, upward), -1, 1)))
    else:
        R = np.eye(3) if upward[2] > 0 else rot_x(math.pi)
    c = np.array(center)
    for i in range(before, len(mb.verts)):
        mb.verts[i] = tuple(R @ np.array(mb.verts[i]) + c)


def torus(mb, center, R, r, seg=20, rseg=8, axis="Z", mat=0):
    rings = []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        ring = []
        for j in range(rseg):
            b = 2 * math.pi * j / rseg
            x = (R + r * math.cos(b)) * math.cos(a)
            y = (R + r * math.cos(b)) * math.sin(a)
            z = r * math.sin(b)
            p = (x, y, z) if axis == "Z" else ((z, x, y) if axis == "X" else (x, z, y))
            ring.append(np.array(p) + np.array(center, dtype=float))
        rings.append(ring)
    mb.add_grid(np.array(rings), mat, close_u=True, close_v=True)


def rivet_row(mb, path, normal_fn, spacing, radius, height, mat=0, seg=8):
    """Rivet heads (domes) along a polyline."""
    path = np.asarray(path, dtype=float)
    d = np.linalg.norm(np.diff(path, axis=0), axis=1)
    s = np.concatenate([[0.0], np.cumsum(d)])
    total = s[-1]
    n = max(2, int(total / spacing))
    prev_p = None
    for i in range(n + 1):
        tgt = total * i / n
        k = max(0, min(int(np.searchsorted(s, tgt)) - 1, len(path) - 2))
        t = (tgt - s[k]) / max(1e-9, s[k + 1] - s[k])
        p = lerp(path[k], path[k + 1], t)
        if prev_p is not None and np.linalg.norm(p - prev_p) < radius * 0.8:
            continue
        prev_p = p
        nrm = unit(normal_fn(p) if callable(normal_fn) else normal_fn)
        # short stem + dome reads as a rivet head
        cyl(mb, p - nrm * height * 0.4, p + nrm * height * 0.3, radius * 0.92,
            seg=seg, mat=mat)
        dome(mb, p + nrm * height * 0.3, radius * 1.25, seg=seg, rings=4, mat=mat,
             squash=0.55, up=nrm)


def rope_coil(mb, center, R, r_rope, coils=6, pitch=0.0, mat=0, seg=26):
    """Flat rope coil: stacked tori shrinking slightly (a hanging coil)."""
    for i in range(coils):
        rr = R * (1.0 - 0.05 * i / max(1, coils - 1))
        torus(mb, [center[0], center[1], center[2] + i * (r_rope * 1.7 + pitch)],
              rr, r_rope, seg=seg, rseg=6, axis="Z", mat=mat)


def superellipse_section(w, h, n=3.0, seg=14):
    """(k,2) rounded-rectangle/superellipse cross-section, half-extents w,h."""
    pts = []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        ca, sa = math.cos(a), math.sin(a)
        x = w * math.copysign(abs(ca) ** (2.0 / n), ca)
        y = h * math.copysign(abs(sa) ** (2.0 / n), sa)
        pts.append((x, y))
    return np.array(pts)


# ---------------------------------------------------------------------------
# late additions
# ---------------------------------------------------------------------------

def _ico_sphere(mb, cx, cy, cz, r, mat):
    """Small faceted icosphere via subdivided octahedron (cheap lump)."""
    base = [[v * r for v in _ic] for _ic in
            [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]]
    idx = mb.add_verts([[cx + v[0], cy + v[1], cz + v[2]] for v in base])
    faces = [(0, 2, 4), (2, 1, 4), (1, 3, 4), (3, 0, 4),
             (0, 5, 2), (2, 5, 1), (1, 5, 3), (3, 5, 0)]
    mb.faces.extend((idx + a, idx + b, idx + c) for a, b, c in faces)
    mb.mat_indices.extend([mat] * 8)
    return idx


def MB_add_ico(self, cx, cy, cz, r, mat=0):
    return _ico_sphere(self, cx, cy, cz, r, mat)


def MB_add_blade(self, path_pts, widths, mat=0, axis=None):
    """Thin blade swept along path with local width profile (for props)."""
    import numpy as _np
    path = [ _np.asarray(p, float) for p in path_pts ]
    n = len(path)
    if axis is None:
        axis = _np.cross(path[-1] - path[0], [0, 0, 1])
        axis = unit(axis)
    rows = []
    for i, pp in enumerate(path):
        w = widths[i] if i < len(widths) else widths[-1]
        rows.append([pp - unit(_np.asarray(axis)) * w * 0.5 * i * 0,
                     pp + _np.asarray(axis) * w, pp, ])
    # simply: two edges offset ± w along axis, extruded in thickness small
    v0 = []
    v1 = []
    th = 0.006
    ax = _np.asarray(axis, float)
    tg = [unit(path[min(i + 1, n - 1)] - path[max(i - 1, 0)]) for i in range(n)]
    nr = [unit(_np.cross(ax, tg[i])) for i in range(n)]
    for i, pp in enumerate(path):
        w = widths[i] if i < len(widths) else widths[-1]
        v0.append(pp + ax * w)
        v1.append(pp - ax * 0.25 * w)
    b0 = self.add_verts([tuple(v) for v in v0] + [tuple(v) for v in v1])
    for i in range(n - 1):
        self.add_face([b0 + i, b0 + i + 1, b0 + n + i + 1, b0 + n + i], mat)
        self.add_face([b0 + n + i, b0 + n + i + 1, b0 + i + 1, b0 + i], mat)
    return b0


MB.add_ico = MB_add_ico
MB.add_blade = MB_add_blade


def MB_mirrored_y(self):
    import numpy as _np
    n = MB(self.name + "_mir")
    for f, m in zip(self.faces, self.mat_indices):
        n.add_face([n.add_points(self.verts[i] * _np.array([1, -1, 1])) for i in f[::-1]], m)
    return n


MB.mirrored_y = MB_mirrored_y

def MB_translated(self, offset):
    import numpy as _np
    n = MB(self.name)
    off = _np.asarray(offset, float)
    n.verts = [ (self.verts[i] + off).tolist() for i in range(len(self.verts)) ]
    n.faces = list(self.faces)
    n.mat_indices = list(self.mat_indices)
    return n
MB.translated = MB_translated

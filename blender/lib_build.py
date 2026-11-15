"""Blender-side mesh helpers (bmesh/numpy) for the Aurelian build.

Everything here runs inside Blender's Python.  Kept deliberately low-level:
we build vertex/face arrays in numpy and hand them to bmesh for speed, so
that a 200 000-vertex hull takes seconds instead of minutes.
"""
from __future__ import annotations
import math
import bpy
import bmesh
import numpy as np
from mathutils import Vector, Matrix


# ---------------------------------------------------------------------------
# scene / object utilities
# ---------------------------------------------------------------------------
def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.unit_settings.system = 'METRIC'
    sc.unit_settings.scale_length = 1.0
    sc.unit_settings.length_unit = 'METERS'
    return sc


def collection(name, parent=None):
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        (parent or bpy.context.scene.collection).children.link(col)
    return col


def mesh_object(name, verts, faces, col=None, smooth_angle=None, mat=None,
                uv=None):
    # drop any non-finite coordinates: a single NaN crashes from_pydata with
    # "internal error setting the array" and the whole module fails to build
    clean = []
    remap = {}
    for i, v in enumerate(verts):
        if len(v) < 3:
            continue
        if all(c == c and abs(c) < 1e7 for c in v):
            remap[i] = len(clean)
            clean.append((float(v[0]), float(v[1]), float(v[2])))
    fclean = []
    for f in faces:
        g = [remap[i] for i in f if i in remap]
        if len(g) >= 3:
            fclean.append(tuple(g))
    verts, faces = clean, fclean
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.validate(verbose=False)
    me.update()
    if uv is not None and len(uv) == len(clean):
        uvl = me.uv_layers.new(name="UVMap")
        flat = np.zeros(len(me.loops) * 2, dtype=np.float32)
        for i, loop in enumerate(me.loops):
            flat[i * 2] = uv[loop.vertex_index][0]
            flat[i * 2 + 1] = uv[loop.vertex_index][1]
        uvl.data.foreach_set("uv", flat)
    ob = bpy.data.objects.new(name, me)
    (col or bpy.context.scene.collection).objects.link(ob)
    if smooth_angle is not None:
        for p in me.polygons:
            p.use_smooth = True
        me.set_sharp_from_angle if hasattr(me, "set_sharp_from_angle") else None
        if hasattr(me, "use_auto_smooth"):
            me.use_auto_smooth = True
            me.auto_smooth_angle = smooth_angle
        else:
            mod = ob.modifiers.new("Smooth by Angle", 'NODES')
    if mat is not None:
        ob.data.materials.append(mat)
    return ob


def join_objects(objs, name):
    """Join a list of objects into the first one and rename it."""
    # NB: callers may pass None (a builder that returned nothing) - drop those
    # BEFORE choosing the join target, otherwise the first real object is
    # skipped and the join silently succeeds on the wrong body.
    objs = [o for o in objs if o is not None and o.name in bpy.data.objects]
    if not objs:
        return None
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    if len(objs) > 1:
        bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active
    ob.name = name
    ob.data.name = name + "_mesh"
    return ob


# ---------------------------------------------------------------------------
# primitive builders  (all return (verts, faces))
# ---------------------------------------------------------------------------
def box(center, size, rot_z=0.0):
    cx, cy, cz = center
    sx, sy, sz = size
    v = []
    for dz in (-0.5, 0.5):
        for dy in (-0.5, 0.5):
            for dx in (-0.5, 0.5):
                x, y = dx * sx, dy * sy
                if rot_z:
                    c, s = math.cos(rot_z), math.sin(rot_z)
                    x, y = x * c - y * s, x * s + y * c
                v.append((cx + x, cy + y, cz + dz * sz))
    f = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1),
         (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    return v, f


def cylinder(center, radius, height, axis='Z', segments=24, cap=True,
             radius_top=None):
    cx, cy, cz = center
    rt = radius if radius_top is None else radius_top
    v = []
    for k, (r, dz) in enumerate(((radius, -height / 2), (rt, height / 2))):
        for i in range(segments):
            a = 2 * math.pi * i / segments
            x, y, z = r * math.cos(a), r * math.sin(a), dz
            if axis == 'Z':
                v.append((cx + x, cy + y, cz + z))
            elif axis == 'X':
                v.append((cx + z, cy + x, cz + y))
            else:
                v.append((cx + x, cy + z, cz + y))
    f = []
    for i in range(segments):
        j = (i + 1) % segments
        f.append((i, j, segments + j, segments + i))
    if cap:
        f.append(tuple(range(segments - 1, -1, -1)))
        f.append(tuple(range(segments, 2 * segments)))
    return v, f


def tube(points, radius, segments=8, closed_ends=True):
    """Sweep a circle along a polyline (used for pipes, stanchions, ropes)."""
    pts = np.asarray(points, float)
    if len(pts) < 2:
        return [], []
    verts = []
    faces = []
    up = np.array([0, 0, 1.0])
    prev_n = None
    for i, p in enumerate(pts):
        if i == 0:
            t = pts[1] - pts[0]
        elif i == len(pts) - 1:
            t = pts[-1] - pts[-2]
        else:
            t = pts[i + 1] - pts[i - 1]
        t = t / (np.linalg.norm(t) + 1e-9)
        ref = up if abs(np.dot(t, up)) < 0.95 else np.array([1.0, 0, 0])
        n = np.cross(t, ref); n /= (np.linalg.norm(n) + 1e-9)
        b = np.cross(t, n)
        for k in range(segments):
            a = 2 * math.pi * k / segments
            verts.append(tuple(p + radius * (math.cos(a) * n + math.sin(a) * b)))
    for i in range(len(pts) - 1):
        for k in range(segments):
            k2 = (k + 1) % segments
            a = i * segments + k; b2 = i * segments + k2
            c = (i + 1) * segments + k2; d = (i + 1) * segments + k
            faces.append((a, b2, c, d))
    if closed_ends:
        faces.append(tuple(range(segments - 1, -1, -1)))
        base = (len(pts) - 1) * segments
        faces.append(tuple(range(base, base + segments)))
    return verts, faces


def meridian_object(name, meridians, n_theta=24, col=None, mat=None):
    """Lathe a set of (r, z) meridians around the Z axis.

    meridians: list of (x_centre, [(r, z), ...]) - each meridian gets its own
    ring so funnels/masts of different profiles can share one object.
    """
    verts = []; faces = []
    for cx in meridians:
        x0, prof = cx if isinstance(cx, tuple) else (0.0, cx)
        start = len(verts)
        for r, z in prof:
            for i in range(n_theta):
                a = 2 * math.pi * i / n_theta
                verts.append((x0 + r * math.cos(a), r * math.sin(a), z))
        n = len(prof)
        for j in range(n - 1):
            for i in range(n_theta):
                i2 = (i + 1) % n_theta
                faces.append((start + j * n_theta + i,
                              start + j * n_theta + i2,
                              start + (j + 1) * n_theta + i2,
                              start + (j + 1) * n_theta + i))
    return mesh_object(name, verts, faces, col=col, mat=mat)


# ---------------------------------------------------------------------------
# surface builders used for decks / bulkheads that must follow the hull
# ---------------------------------------------------------------------------
def deck_surface_patch(hull, z, x0, x1, nx=90, ny=8, thickness=0.012,
                       col=None, name="deck", mat=None, y_scale=1.0):
    """A deck: a horizontal plate following the hull's half breadth at z.

    Returns the object plus the (x -> half_beam) function used to place walls.
    """
    xs = np.linspace(x0, x1, nx)
    hb = np.array([hull.half_beam_at(x, z) for x in xs]) * y_scale
    ok = hb > 0.02
    xs, hb = xs[ok], hb[ok]
    if len(xs) < 2:
        return None
    verts = []; faces = []
    for x, b in zip(xs, hb):
        for j in range(ny + 1):
            y = -b + 2 * b * j / ny
            verts.append((x, y, z))
    for i in range(len(xs) - 1):
        for j in range(ny):
            a = i * (ny + 1) + j
            faces.append((a, a + 1, a + ny + 2, a + ny + 1))
    return mesh_object(name, verts, faces, col=col, mat=mat)


def vertical_wall_along_hull(hull, z0, z1, x0, x1, side=1, nx=60,
                             thickness=0.012, col=None, name="bulwark",
                             mat=None, offset=0.0):
    """Shell plating between two heights following the hull's side."""
    xs = np.linspace(x0, x1, nx)
    verts = []; faces = []
    nz = 4
    for x in xs:
        b = hull.half_beam_at(x, z0) * 0.97 + offset
        b1 = hull.half_beam_at(x, z1) * 0.97 + offset
        for j in range(nz + 1):
            f = j / nz
            verts.append((x, side * (b + (b1 - b) * f), z0 + (z1 - z0) * f))
    for i in range(len(xs) - 1):
        for j in range(nz):
            a = i * (nz + 1) + j
            q = (a, a + nz + 1, a + nz + 2, a + 1)
            faces.append(q if side > 0 else q[::-1])
    return mesh_object(name, verts, faces, col=col, mat=mat)


def railing(path, z, height=1.07, stanchion_every=1.5, radius=0.035,
            col=None, name="rail", mat_rail=None, mat_stanchion=None):
    """Period railing: stanchions plus two rails.  path = [(x, y), ...]."""
    objs = []
    pts = np.asarray(path, float)
    # rails
    for h in (height, height * 0.52):
        v, f = tube([(p[0], p[1], z + h) for p in pts], radius, 6)
        if v:
            objs.append(mesh_object(name + "_rail", v, f, col=col, mat=mat_rail))
    # stanchions
    d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))]
    n = max(2, int(d[-1] / stanchion_every) + 1)
    tg = np.linspace(0, d[-1], n)
    sx = np.interp(tg, d, pts[:, 0]); sy = np.interp(tg, d, pts[:, 1])
    v = []; f = []
    for x, y in zip(sx, sy):
        vv, ff = cylinder((x, y, z + height / 2), 0.026, height,
                          segments=6, cap=True)
        off = len(v)
        v += vv; f += [tuple(i + off for i in q) for q in ff]
    if v:
        objs.append(mesh_object(name + "_stanchions", v, f, col=col,
                                mat=mat_stanchion))
    return objs


# ---------------------------------------------------------------------------
# materials
# ---------------------------------------------------------------------------
def principled(name, color, rough=0.55, metal=0.0, alpha=1.0, emit=None,
               emit_strength=0.0):
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    if len(color) == 3:
        color = (color[0], color[1], color[2], 1.0)
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    if alpha < 1.0:
        bsdf.inputs["Alpha"].default_value = alpha
        m.blend_method = 'BLEND'
    if emit is not None:
        bsdf.inputs["Emission Color"].default_value = emit
        bsdf.inputs["Emission Strength"].default_value = emit_strength
    return m


def build_palette():
    """Material library shared by every module (names are stable API)."""
    P = {}
    from shipdesign.spec import PALETTE, FUNNEL_COLORS
    P["hull_black"] = principled("Hull_Black", PALETTE["hull_black"], 0.42)
    P["upper_white"] = principled("Upper_White", PALETTE["upper_white"], 0.50)
    P["boot_white"] = principled("Boot_White", PALETTE["boot_white"], 0.5)
    P["deck_wood"] = principled("Deck_Wood", (0.34, 0.25, 0.16, 1), 0.72)
    P["deck_wood_light"] = principled("Deck_Wood_Light", (0.46, 0.36, 0.24, 1), 0.72)
    P["mahogany"] = principled("Mahogany", PALETTE["mahogany"], 0.35)
    P["teak"] = principled("Teak", PALETTE["teak"], 0.45)
    P["oak_light"] = principled("Oak_Light", PALETTE["oak_light"], 0.45)
    P["brass"] = principled("Brass", PALETTE["brass"], 0.22, metal=1.0)
    P["steel"] = principled("Steel", PALETTE["steel"], 0.45, metal=1.0)
    P["cast_iron"] = principled("Cast_Iron", PALETTE["cast_iron"], 0.62, metal=0.8)
    P["funnel"] = principled("Funnel_Buff", FUNNEL_COLORS["body"], 0.55)
    P["funnel_top"] = principled("Funnel_Top", FUNNEL_COLORS["top_band"], 0.60)
    P["funnel_inner"] = principled("Funnel_Inner", FUNNEL_COLORS["inside"], 0.85)
    P["glass"] = principled("Glass", (0.42, 0.52, 0.52, 1), 0.08, alpha=0.35)
    P["glass_ground"] = principled("Glass_Ground",
                                   (0.78, 0.78, 0.70, 1), 0.55, alpha=0.55,
                                   emit=(0.9, 0.86, 0.7, 1), emit_strength=0.6)
    P["white_ceiling"] = principled("Ceiling_White", PALETTE["white_ceiling"], 0.85)
    P["carpet_green"] = principled("Carpet_Green", PALETTE["fabric_green"], 0.95)
    P["carpet_red"] = principled("Carpet_Red", PALETTE["fabric_red"], 0.95)
    P["leather"] = principled("Leather", (0.16, 0.09, 0.06, 1), 0.55)
    P["fabric_gold"] = principled("Fabric_Gold", (0.42, 0.32, 0.14, 1), 0.85)
    P["paint_red"] = principled("Paint_Red", PALETTE["paint_red_lead"], 0.65)
    P["coal"] = principled("Coal", (0.035, 0.035, 0.038, 1), 0.85)
    P["rope"] = principled("Rope", PALETTE["rope_hemp"], 0.85)
    P["canvas"] = principled("Canvas", (0.72, 0.68, 0.56, 1), 0.85)
    P["lamp"] = principled("Lamp_Warm", (1.0, 0.9, 0.7, 1), 0.3,
                           emit=(1.0, 0.82, 0.55, 1), emit_strength=6.0)
    P["copper"] = principled("Copper", (0.55, 0.31, 0.16, 1), 0.30, metal=1.0)
    P["red_oxide"] = principled("Red_Oxide", (0.35, 0.14, 0.09, 1), 0.7)
    P["water"] = principled("Sea_Water", (0.02, 0.07, 0.09, 1), 0.12)
    return P

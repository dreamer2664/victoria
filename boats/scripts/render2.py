"""
render2.py -- THEMISTOCLES render driver (GEN-1 revision, THEMISTOCLES-III).

Usage:
  blender -b <blend> --python render2.py -- --out <dir> --prefix rowing \
      --views broadside[,bow_quarter,...] [--studio 1 --sea 0 | --studio 0 --sea 1]
      [--res 960x600] [--samples 64] [--name exact_file.png]
      [--hide "regex|regex"] [--only "regex"]

What changed for GEN-1 (and why):
* `--res` is honoured (it used to be parsed and ignored); `--samples`
  overrides the sample count; `--name` writes one view to an exact filename.
* Dry studio views no longer put a plane at the waterline.  The old rig
  dropped a flat grey "sea" at Z=0 into studio renders, which flooded every
  open interior to the waterline and hid the thwarts.  The boat now stands on
  timber keel blocks on the studio floor, placed under the actual keel.
* Afloat views drop the studio lamps (they reflected in the water as
  detached white discs); sky + sun light the scene.
* The camera is fitted to the projected VERTICES of the visible boat (not a
  bounding sphere) and oriented explicitly, so every hull end has a stated
  margin and the top view lays the boat lengthwise in a landscape frame.
"""
import os, sys, re, math
import numpy as np
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from them2 import bl2

# dir: camera position direction from the target (+X bow, +Y port, +Z up)
# margin: fraction of the half-frame the subject may fill is 1/margin
VIEWS = {
    "broadside":     dict(dir=(0.0, -1.0, 0.20), lens=60, margin=1.10),
    "bow_quarter":   dict(dir=(1.0, -0.95, 0.50), lens=55, margin=1.10),
    "stern_quarter": dict(dir=(-1.0, -0.90, 0.48), lens=55, margin=1.10),
    "bow_on":        dict(dir=(1.0, -0.06, 0.24), lens=70, margin=1.18),
    "stern_on":      dict(dir=(-1.0, -0.06, 0.26), lens=70, margin=1.18),
    "top":           dict(dir=(0.0, -0.10, 1.0), lens=60, margin=1.12),
    "underside":     dict(dir=(0.55, -0.80, -0.95), lens=55, margin=1.12),
    "interior":      dict(dir=(0.38, -0.55, 1.0), lens=50, margin=1.06),
    "hero":          dict(dir=(0.95, -1.10, 0.42), lens=55, margin=1.08),
    "profile_high":  dict(dir=(0.20, -1.0, 0.62), lens=60, margin=1.08),
    "construction":  dict(dir=(0.75, -0.85, 0.70), lens=55, margin=1.10),
    "machinery":     dict(dir=(0.35, -0.80, 0.85), lens=50, margin=1.06),
}


def visible_boat_objects():
    return [o for o in bpy.context.scene.objects
            if o.type == 'MESH' and not o.name.startswith("TM2_")
            and not o.hide_render]


def world_verts(objs, step=1):
    out = []
    for o in objs:
        mw = np.array(o.matrix_world)
        n = len(o.data.vertices)
        if n == 0:
            continue
        co = np.empty(n * 3)
        o.data.vertices.foreach_get("co", co)
        co = co.reshape(-1, 3)[::step]
        out.append(co @ mw[:3, :3].T + mw[:3, 3])
    return np.concatenate(out) if out else np.zeros((0, 3))


def fit_camera(V, d, lens, margin, aspect, centre_hint=None):
    """Return (target, distance) so every vertex in V projects inside the
    frame with the given margin, for a camera looking along -d."""
    d = d / np.linalg.norm(d)
    f = -d
    zup = np.array([0.0, 0.0, 1.0])
    right = np.cross(f, zup)
    if np.linalg.norm(right) < 1e-6:
        right = np.array([1.0, 0, 0])
    right /= np.linalg.norm(right)
    up = np.cross(right, f)
    tan_h = 18.0 / lens
    tan_v = tan_h / aspect
    t = V.mean(axis=0) if centre_hint is None else np.asarray(centre_hint, float)
    D = 1.0
    for _ in range(6):
        r = V - t
        x = r @ right; y = r @ up; z = r @ d
        # recentre on the projected extent (orthographic approximation)
        t = t + right * (x.max() + x.min()) / 2 + up * (y.max() + y.min()) / 2
        r = V - t
        x = r @ right; y = r @ up; z = r @ d
        D = float(max(np.max(z + np.abs(x) * margin / tan_h),
                      np.max(z + np.abs(y) * margin / tan_v)))
        # perspective recentre: shift so the projected extremes are balanced
        px = x / (D - z); py = y / (D - z)
        t = t + right * (px.max() + px.min()) / 2 * D + up * (py.max() + py.min()) / 2 * D
    r = V - t
    x = r @ right; y = r @ up; z = r @ d
    D = float(max(np.max(z + np.abs(x) * margin / tan_h),
                  np.max(z + np.abs(y) * margin / tan_v)))
    return t, D, right, up


def place_camera(t, d, D, lens, right, up, name="TM2_Cam"):
    cam = bpy.data.objects.get(name)
    if cam is None:
        cam = bpy.data.objects.new(name, bpy.data.cameras.new(name))
        bpy.context.scene.collection.objects.link(cam)
    for c in list(cam.constraints):
        cam.constraints.remove(c)
    d = d / np.linalg.norm(d)
    pos = t + d * D
    # camera looks down its -Z; +Y is up, +X is right
    M = Matrix(((right[0], up[0], d[0], pos[0]),
                (right[1], up[1], d[1], pos[1]),
                (right[2], up[2], d[2], pos[2]),
                (0, 0, 0, 1)))
    cam.matrix_world = M
    cam.data.lens = lens
    cam.data.sensor_fit = 'HORIZONTAL'
    cam.data.sensor_width = 36.0
    cam.data.clip_start = 0.05
    cam.data.clip_end = 500.0
    bpy.context.scene.camera = cam
    return cam


def keel_points(objs, n=2):
    """Lowest boat point near two stations, for the keel blocks."""
    V = world_verts(objs, step=1)
    if len(V) == 0:
        return [], -1.0
    lo, hi = V.min(axis=0), V.max(axis=0)
    L = hi[0] - lo[0]
    pts = []
    for fx in (0.30, 0.70):
        xc = lo[0] + fx * L
        sel = V[(np.abs(V[:, 0] - xc) < 0.12) & (np.abs(V[:, 1]) < 0.06)]
        if len(sel):
            pts.append((xc, float(sel[:, 2].min())))
    return pts, float(lo[2])


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--prefix", default="boat")
    ap.add_argument("--views", default="broadside")
    ap.add_argument("--name", default="")
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--hide", default="")
    ap.add_argument("--only", default="")
    ap.add_argument("--sea", type=int, default=0)
    ap.add_argument("--studio", type=int, default=1)
    ap.add_argument("--res", default="960x600")
    ap.add_argument("--samples", type=int, default=0)
    ap.add_argument("--margin", type=float, default=0.0)
    ap.add_argument("--dir", default="")
    ap.add_argument("--lens", type=float, default=0.0)
    ap.add_argument("--focus", default="")
    args = ap.parse_args(argv)

    s = bpy.context.scene
    pats_hide = [re.compile(p) for p in args.hide.split("|") if p] if args.hide else []
    pat_only = re.compile(args.only) if args.only else None
    for o in s.objects:
        if o.type != 'MESH' or o.name.startswith("TM2_"):
            continue
        hide = bool(pat_only and not pat_only.search(o.name))
        if not hide and any(p.search(o.name) for p in pats_hide):
            hide = True
        o.hide_render = hide
        o.hide_viewport = hide

    rx, ry = (int(v) for v in args.res.lower().split("x"))
    samples = args.samples or (24 if args.quick else 96)
    objs = visible_boat_objects()
    kpts, z_low = keel_points(objs)
    floor_z = z_low - 0.25
    rig = bl2.RenderRig(s, sea=bool(args.sea) and not args.studio, res=(rx, ry),
                        samples=samples, studio=bool(args.studio), floor_z=floor_z)
    if args.studio:
        from them2.studio2 import keel_blocks
        keel_blocks(kpts, floor_z)

    os.makedirs(args.out, exist_ok=True)
    views = [v for v in args.views.split(",") if v]
    V = world_verts(objs, step=3)
    for vname in views:
        v = dict(VIEWS[vname])
        if args.dir:
            v["dir"] = tuple(float(c) for c in args.dir.split(","))
        if args.lens:
            v["lens"] = args.lens
        if args.margin:
            v["margin"] = args.margin
        d = np.asarray(v["dir"], float); d /= np.linalg.norm(d)
        lift = 0.0
        hidden_env = []
        Vv = V
        if vname == "underside":
            # a technical view from below: the boat is hoisted off the floor
            # and the studio shell is removed so the camera sees open sky
            lift = 3.0
            for o in objs:
                o.location.z += lift
            Vv = V + np.array([0, 0, lift])
            rig.bg_cam.inputs[0].default_value = (0.24, 0.27, 0.32, 1.0)
            for nm in ("TM2_Studio_BG", "TM2_Sea", "TM2_KeelBlocks"):
                ob = bpy.data.objects.get(nm)
                if ob and not ob.hide_render:
                    ob.hide_render = True
                    hidden_env.append(ob)
        if args.focus:
            # diagnostic close-ups only: fit the camera to a box
            # "x0,x1,y0,y1,z0,z1" (never used for GEN-1 release frames)
            b = [float(c) for c in args.focus.split(",")]
            m = ((Vv[:, 0] >= b[0]) & (Vv[:, 0] <= b[1]) & (Vv[:, 1] >= b[2]) &
                 (Vv[:, 1] <= b[3]) & (Vv[:, 2] >= b[4]) & (Vv[:, 2] <= b[5]))
            Vv = Vv[m]
        t, D, right, up = fit_camera(Vv, d, v["lens"], v["margin"], rx / ry)
        place_camera(t, d, D, v["lens"], right, up)
        fname = args.name if (args.name and len(views) == 1) else f"{args.prefix}_{vname}.png"
        rig.render(os.path.join(args.out, fname))
        if lift:
            for o in objs:
                o.location.z -= lift
        for ob in hidden_env:
            ob.hide_render = False
        if lift:
            rig.bg_cam.inputs[0].default_value = (0.0026, 0.0034, 0.0042, 1.0)
        print("RENDERED", vname, "->", fname, "dist %.2f" % D)


if __name__ == "__main__":
    main()

"""
bsetup.py -- Blender-side plumbing: scene reset, material library, builder -> object,
modular asset registry with linked-duplicate instancing, cameras, lighting, render.
"""
import os
import math
import bpy
import bmesh
from mathutils import Vector, Euler

from core import MATERIALS, MAT_ORDER, MAT_INDEX

TEXDIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))), "textures")

# ---------------------------------------------------------------- scene
def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.unit_settings.system = 'METRIC'
    sc.unit_settings.scale_length = 1.0
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.render.film_transparent = False
    # AgX/Filmic name their "look" presets differently across versions; probe safely.
    for vt in ('AgX', 'Filmic', 'Standard'):
        try:
            sc.view_settings.view_transform = vt
            break
        except TypeError:
            continue
    for lk in ('AgX - Medium High Contrast', 'Medium High Contrast',
               'Filmic - Medium High Contrast', 'None'):
        try:
            sc.view_settings.look = lk
            break
        except TypeError:
            continue
    return sc


def ensure_coll(name, parent=None):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        (parent or bpy.context.scene.collection).children.link(c)
    return c


# ---------------------------------------------------------------- materials
_MATS = {}


def make_materials():
    """Build one Principled material per entry in MATERIALS, textured from texgen PNGs."""
    global _MATS
    _MATS = {}
    for name in MAT_ORDER:
        spec = MATERIALS[name]
        m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
        m.use_nodes = True
        nt = m.node_tree
        nt.nodes.clear()
        out = nt.nodes.new("ShaderNodeOutputMaterial"); out.location = (600, 0)
        bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled"); bsdf.location = (280, 0)
        nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

        if spec["kind"] == "tex":
            alb = os.path.join(TEXDIR, name + "_alb.png")
            nrm = os.path.join(TEXDIR, name + "_nrm.png")
            tx = nt.nodes.new("ShaderNodeTexImage"); tx.location = (-320, 220)
            if os.path.exists(alb):
                tx.image = bpy.data.images.load(alb, check_existing=True)
                nt.links.new(tx.outputs["Color"], bsdf.inputs["Base Color"])
            if os.path.exists(nrm):
                ti = nt.nodes.new("ShaderNodeTexImage"); ti.location = (-320, -180)
                ti.image = bpy.data.images.load(nrm, check_existing=True)
                ti.image.colorspace_settings.name = 'Non-Color'
                nm = nt.nodes.new("ShaderNodeNormalMap"); nm.location = (-60, -180)
                nm.inputs["Strength"].default_value = 0.55
                nt.links.new(ti.outputs["Color"], nm.inputs["Color"])
                nt.links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
            bsdf.inputs["Roughness"].default_value = spec.get("rough", 0.7)
        else:
            c = spec.get("color", (0.5, 0.5, 0.5))
            bsdf.inputs["Base Color"].default_value = (c[0], c[1], c[2], 1.0)
            bsdf.inputs["Roughness"].default_value = spec.get("rough", 0.5)

        if spec.get("metal"):
            bsdf.inputs["Metallic"].default_value = spec["metal"]
        if spec.get("alpha") is not None:
            bsdf.inputs["Alpha"].default_value = spec["alpha"]
            m.blend_method = 'BLEND'
        if spec.get("emit"):
            bsdf.inputs["Emission Color"].default_value = (
                spec.get("color", (1, 0.8, 0.4))[0], spec.get("color", (1, 0.8, 0.4))[1],
                spec.get("color", (1, 0.8, 0.4))[2], 1.0)
            bsdf.inputs["Emission Strength"].default_value = spec["emit"]
        m.diffuse_color = (*spec.get("color", (0.5, 0.5, 0.5)), 1.0)
        _MATS[name] = m

    # painted signboards (see signs.py) become plain image-mapped materials
    signdir = os.path.join(TEXDIR, "signs")
    if os.path.isdir(signdir):
        for fn in sorted(os.listdir(signdir)):
            if not fn.endswith(".png"):
                continue
            name = fn[:-4]
            m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
            m.use_nodes = True
            nt = m.node_tree
            nt.nodes.clear()
            out = nt.nodes.new("ShaderNodeOutputMaterial"); out.location = (600, 0)
            bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled"); bsdf.location = (280, 0)
            nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
            tx = nt.nodes.new("ShaderNodeTexImage"); tx.location = (-260, 0)
            tx.image = bpy.data.images.load(os.path.join(signdir, fn), check_existing=True)
            tx.interpolation = 'Cubic'
            nt.links.new(tx.outputs["Color"], bsdf.inputs["Base Color"])
            bsdf.inputs["Roughness"].default_value = 0.68
            _MATS[name] = m
    return _MATS


def mat(name):
    if name not in _MATS:
        make_materials()
    return _MATS[name]


# ---------------------------------------------------------------- builder -> object
def builder_to_object(name, mb, coll=None, bevel=0.0, shade_smooth=False):
    """Turn a MeshBuilder into a real Blender object with material slots + UVs."""
    if not mb.faces:
        return None
    me = bpy.data.meshes.new(name)
    me.from_pydata([Vector(v) for v in mb.verts], [], [list(f) for f in mb.faces])
    me.validate(verbose=False)

    # material slots: only the materials actually used, in global order
    used = sorted({m for m in mb.fmats}, key=lambda n: MAT_INDEX.get(n, 999))
    slot_of = {}
    for i, mn in enumerate(used):
        me.materials.append(mat(mn))
        slot_of[mn] = i
    for poly, mn in zip(me.polygons, mb.fmats):
        poly.material_index = slot_of[mn]

    uv = me.uv_layers.new(name="UVMap")
    for poly, fuv in zip(me.polygons, mb.fuvs):
        for k, li in enumerate(poly.loop_indices):
            if k < len(fuv):
                uv.data[li].uv = fuv[k]

    me.update()

    # Make all normals consistent and outward. Facade routines legitimately emit
    # mirrored/mixed winding; this normalises it in one pass instead of trying to
    # hand-track orientation in every component.
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    me.update()

    ob = bpy.data.objects.new(name, me)
    (coll or bpy.context.scene.collection).objects.link(ob)

    if shade_smooth:
        for p in me.polygons:
            p.use_smooth = True
    if bevel > 0:
        mod = ob.modifiers.new("Bevel", 'BEVEL')
        mod.width = bevel
        mod.segments = 1
        mod.limit_method = 'ANGLE'
        mod.angle_limit = math.radians(50)
        mod.harden_normals = False
        # apply immediately so instancing/export sees final geometry
        bpy.context.view_layer.objects.active = ob
        bpy.ops.object.modifier_apply(modifier=mod.name)
    return ob


# ---------------------------------------------------------------- asset registry
class Registry:
    """Holds prototype objects (one mesh each) and instances them as linked duplicates.

    Linked duplicates are the whole point of the modular pipeline: 40 identical
    warehouses cost one mesh in the .blend and one mesh in the GLB, because the
    exporter de-duplicates shared mesh data.
    """

    def __init__(self):
        self.proto = {}          # name -> prototype object (mesh owner)
        self.counts = {}         # name -> number of instances placed
        self.hidden = ensure_coll("_PROTOTYPES")

    def define(self, name, mb, bevel=0.0, smooth=False):
        ob = builder_to_object(name, mb, coll=self.hidden, bevel=bevel, shade_smooth=smooth)
        if ob is None:
            raise ValueError("empty builder for " + name)
        self.proto[name] = ob
        self.counts[name] = 0
        return ob

    def exists(self, name):
        return name in self.proto

    def place(self, name, x, y, z=0.0, rz=0.0, coll=None, label=None):
        src = self.proto[name]
        ob = bpy.data.objects.new(label or name, src.data)     # linked duplicate
        ob.location = (x, y, z)
        ob.rotation_euler = Euler((0, 0, math.radians(rz)), 'XYZ')
        (coll or bpy.context.scene.collection).objects.link(ob)
        self.counts[name] += 1
        return ob

    def report(self):
        tot_inst = sum(self.counts.values())
        tris = 0
        for n, ob in self.proto.items():
            me = ob.data
            tris += sum(max(1, len(p.vertices) - 2) for p in me.polygons) * max(1, self.counts.get(n, 0))
        return tot_inst, tris, len(self.proto)


# ---------------------------------------------------------------- environment
def add_water(coll, x0, y0, x1, y1, z=0.0, matname="water"):
    mb = __import__("core").MeshBuilder()
    mb.add_quad((x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z), matname)
    return builder_to_object("WATER_" + matname, mb, coll=coll)


def add_ground(coll, x0, y0, x1, y1, z=-0.2, matname="mud"):
    mb = __import__("core").MeshBuilder()
    mb.add_quad((x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z), matname)
    return builder_to_object("GROUND", mb, coll=coll)


def setup_world(strength=0.28, top=(0.42, 0.50, 0.60), bottom=(0.62, 0.58, 0.50)):
    w = bpy.data.worlds.new("PortWorld")
    bpy.context.scene.world = w
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld"); out.location = (400, 0)
    bg = nt.nodes.new("ShaderNodeBackground"); bg.location = (200, 0)
    bg.inputs["Strength"].default_value = strength
    grad = nt.nodes.new("ShaderNodeTexGradient"); grad.location = (-200, 0)
    grad.gradient_type = 'EASING'
    mapn = nt.nodes.new("ShaderNodeMapping"); mapn.location = (-400, 0)
    mapn.inputs["Rotation"].default_value = (math.radians(90), 0, 0)
    texc = nt.nodes.new("ShaderNodeTexCoord"); texc.location = (-600, 0)
    ramp = nt.nodes.new("ShaderNodeValToRGB"); ramp.location = (0, 0)
    ramp.color_ramp.elements[0].color = (*top, 1)
    ramp.color_ramp.elements[1].color = (*bottom, 1)
    nt.links.new(texc.outputs["Generated"], mapn.inputs["Vector"])
    nt.links.new(mapn.outputs["Vector"], grad.inputs["Vector"])
    nt.links.new(grad.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])
    return w


def add_sun(coll, azimuth_deg=140.0, elevation_deg=34.0, strength=3.0,
            color=(1.0, 0.93, 0.82)):
    l = bpy.data.lights.new("Sun", 'SUN')
    l.energy = strength
    l.color = color
    l.angle = math.radians(1.6)
    ob = bpy.data.objects.new("Sun", l)
    coll.objects.link(ob)
    az, el = math.radians(azimuth_deg), math.radians(elevation_deg)
    # `d` points FROM the scene TOWARD the sun (i.e. the sun's sky position).
    # A sun lamp emits along its local -Z, so +Z must be aligned with d; light then
    # travels along -d, i.e. downward out of the sky.
    # azimuth_deg is the sun's bearing measured from +X, counter-clockwise.
    d = Vector((math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)))
    ob.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    return ob


def add_fill(coll, azimuth_deg=100.0, elevation_deg=28.0, strength=1.1,
             color=(0.72, 0.78, 0.88)):
    """Soft sky-bounce fill from the shadow side. Keeps Victorian brick readable in
    shadow without flattening the key light's form modelling."""
    l = bpy.data.lights.new("Fill", 'SUN')
    l.energy = strength
    l.color = color
    l.angle = math.radians(25.0)
    l.use_shadow = False
    ob = bpy.data.objects.new("Fill", l)
    coll.objects.link(ob)
    az, el = math.radians(azimuth_deg), math.radians(elevation_deg)
    d = Vector((math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)))
    ob.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    return ob


def add_camera(coll, loc, look_at, lens=35.0, name="Cam"):
    cd = bpy.data.cameras.new(name)
    cd.lens = lens
    cd.sensor_width = 36.0
    ob = bpy.data.objects.new(name, cd)
    coll.objects.link(ob)
    ob.location = Vector(loc)
    d = Vector(look_at) - Vector(loc)
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    return ob


def _out_by_name(node, names):
    """Compositor socket names drift between Blender versions; take the first match."""
    for n in names:
        if n in node.outputs:
            return node.outputs[n]
    return node.outputs[0]


def setup_compositor_haze(fog_color=(0.74, 0.72, 0.68), start=60.0, depth=520.0, max_fog=0.82):
    """Cheap, physically-plausible aerial perspective using the Cycles Mist pass.

    A volumetric domain over 1 km2 is far too slow for CPU rendering; the mist
    pass gives the same industrial haze at a fraction of the cost.
    """
    sc = bpy.context.scene
    sc.use_nodes = True
    vl = sc.view_layers[0]
    vl.use_pass_mist = True
    nt = sc.node_tree
    nt.nodes.clear()
    rl = nt.nodes.new("CompositorNodeRLayers"); rl.location = (-600, 0)
    mr = nt.nodes.new("CompositorNodeMapRange"); mr.location = (-360, -180)
    mr.inputs["From Min"].default_value = start
    mr.inputs["From Max"].default_value = depth
    mr.inputs["To Min"].default_value = 0.0
    mr.inputs["To Max"].default_value = max_fog
    nt.links.new(rl.outputs["Mist"], mr.inputs["Value"])
    mix = nt.nodes.new("CompositorNodeMixRGB"); mix.location = (-100, 0)
    mix.blend_type = 'MIX'
    mix.inputs[2].default_value = (*fog_color, 1)
    # CompositorNodeMapRange exposes its result as "Value" in 4.2 and "Result" later.
    mr_out = mr.outputs.get("Result") or mr.outputs.get("Value") or mr.outputs[0]
    nt.links.new(mr_out, mix.inputs[0])
    nt.links.new(rl.outputs["Image"], mix.inputs[1])
    comp = nt.nodes.new("CompositorNodeComposite"); comp.location = (200, 0)
    nt.links.new(mix.outputs[0], comp.inputs["Image"])
    # gentle bloom on lamps/windows
    gl = nt.nodes.new("CompositorNodeGlare"); gl.location = (0, -260)
    gl.glare_type = 'FOG_GLOW'
    gl.quality = 'MEDIUM'
    gl.threshold = 1.4
    gl.size = 7
    nt.links.new(mix.outputs[0], gl.inputs["Image"])
    nt.links.new(gl.outputs[0], comp.inputs["Image"])


def render_to(path, cam, res=(1600, 900), samples=64, denoise=True, threads=None):
    sc = bpy.context.scene
    sc.camera = cam
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = 'PNG'
    sc.render.filepath = path
    sc.cycles.samples = samples
    sc.cycles.use_denoising = denoise
    sc.cycles.max_bounces = 10
    sc.cycles.diffuse_bounces = 6
    sc.cycles.glossy_bounces = 4
    sc.cycles.transmission_bounces = 4
    sc.cycles.caustics_reflective = False
    sc.cycles.caustics_refractive = False
    sc.cycles.use_fast_gi = False
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.render.render(write_still=True)
    return path

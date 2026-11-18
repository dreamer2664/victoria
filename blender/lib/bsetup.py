"""
bsetup.py -- Blender scene setup: materials, world/sky, camera framing, lighting,
compositor mist/haze, and the MeshBuilder -> Blender Object conversion pipeline.
GENERATION II — OPERATION VICTORIA (PERICLES-II)
"""
import os, sys, math
import bpy, bmesh
from mathutils import Vector, Euler

LIBDIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(LIBDIR))
TEXDIR = os.path.join(ROOT, "textures")

from core import MATERIALS, MAT_INDEX, QUAY_Z, WATER_Z

_MATS = {}


def reset_scene():
    """Wipe everything out of the scene and start clean."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.cycles.preview_samples = 12
    sc.cycles.samples = 64
    sc.view_settings.view_transform = 'AgX'
    sc.view_settings.look = 'AgX - Medium High Contrast'
    sc.view_settings.exposure = -0.15
    sc.unit_settings.system = 'METRIC'
    sc.unit_settings.scale_length = 1.0
    make_materials()
    return sc


def ensure_coll(name, parent=None):
    c = bpy.data.collections.get(name)
    if not c:
        c = bpy.data.collections.new(name)
        (parent or bpy.context.scene.collection).children.link(c)
    return c


# ---------------------------------------------------------------- materials
def make_materials():
    global _MATS
    for name, spec in MATERIALS.items():
        m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
        m.use_nodes = True
        nt = m.node_tree
        nt.nodes.clear()
        out = nt.nodes.new("ShaderNodeOutputMaterial"); out.location = (600, 0)
        bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled"); bsdf.location = (280, 0)
        nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

        c = spec.get("color", (0.5, 0.5, 0.5))
        bsdf.inputs["Base Color"].default_value = (c[0], c[1], c[2], 1.0)
        bsdf.inputs["Roughness"].default_value = spec.get("rough", 0.7)

        if spec["kind"] == "tex":
            alb = os.path.join(TEXDIR, name + "_alb.png")
            nrm = os.path.join(TEXDIR, name + "_nrm.png")
            if not os.path.exists(alb) and name == "brick_red":
                alb = os.path.join(TEXDIR, "brick_buff_alb.png")
                nrm = os.path.join(TEXDIR, "brick_buff_nrm.png")
            elif not os.path.exists(alb) and name == "algae":
                alb = os.path.join(TEXDIR, "granite_alb.png")
                nrm = os.path.join(TEXDIR, "granite_nrm.png")
            if os.path.exists(alb):
                tx = nt.nodes.new("ShaderNodeTexImage"); tx.location = (-320, 220)
                tx.image = bpy.data.images.load(alb, check_existing=True)
                if name == "brick_red":
                    mix_c = nt.nodes.new("ShaderNodeMix")
                    mix_c.data_type = 'RGBA'
                    mix_c.blend_type = 'MULTIPLY'
                    mix_c.inputs["Factor"].default_value = 0.82
                    mix_c.inputs[6].default_value = (0.55, 0.22, 0.16, 1.0)
                    nt.links.new(tx.outputs["Color"], mix_c.inputs[7])
                    nt.links.new(mix_c.outputs[2], bsdf.inputs["Base Color"])
                elif name == "algae":
                    # damp weathered tidal stone tint
                    mix_c = nt.nodes.new("ShaderNodeMix")
                    mix_c.data_type = 'RGBA'
                    mix_c.blend_type = 'MULTIPLY'
                    mix_c.inputs["Factor"].default_value = 0.75
                    mix_c.inputs[6].default_value = (0.42, 0.50, 0.44, 1.0)
                    nt.links.new(tx.outputs["Color"], mix_c.inputs[7])
                    nt.links.new(mix_c.outputs[2], bsdf.inputs["Base Color"])
                else:
                    nt.links.new(tx.outputs["Color"], bsdf.inputs["Base Color"])
            if os.path.exists(nrm):
                ti = nt.nodes.new("ShaderNodeTexImage"); ti.location = (-320, -180)
                ti.image = bpy.data.images.load(nrm, check_existing=True)
                ti.image.colorspace_settings.name = 'Non-Color'
                nm = nt.nodes.new("ShaderNodeNormalMap"); nm.location = (-60, -180)
                nm.inputs["Strength"].default_value = 0.65
                nt.links.new(ti.outputs["Color"], nm.inputs["Color"])
                nt.links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])

        if spec.get("metal"):
            bsdf.inputs["Metallic"].default_value = spec["metal"]
        if spec.get("alpha") is not None:
            bsdf.inputs["Alpha"].default_value = spec["alpha"]
            m.blend_method = 'BLEND'
        if spec.get("emit"):
            ec = spec.get("color", (1.0, 0.8, 0.4))
            if "Emission Color" in bsdf.inputs:
                bsdf.inputs["Emission Color"].default_value = (ec[0], ec[1], ec[2], 1.0)
                bsdf.inputs["Emission Strength"].default_value = spec["emit"]
            elif "Emission" in bsdf.inputs:
                bsdf.inputs["Emission"].default_value = (ec[0], ec[1], ec[2], 1.0)

        # Victorian harbour water realism: turbid, brackish, reflective estuary chop
        if name == "water":
            bsdf.inputs["Base Color"].default_value = (0.024, 0.046, 0.052, 1.0)
            bsdf.inputs["Roughness"].default_value = 0.12
            bsdf.inputs["Metallic"].default_value = 0.18
            bsdf.inputs["IOR"].default_value = 1.333
            tex_coord = nt.nodes.new("ShaderNodeTexCoord")
            tex_coord.location = (-580, -120)
            wave_tex = nt.nodes.new("ShaderNodeTexWave")
            wave_tex.location = (-340, -120)
            wave_tex.inputs["Scale"].default_value = 1.6
            wave_tex.inputs["Distortion"].default_value = 3.6
            wave_tex.inputs["Detail"].default_value = 3.0
            wave_tex.inputs["Detail Roughness"].default_value = 0.60
            nt.links.new(tex_coord.outputs["Object"], wave_tex.inputs["Vector"])
            bump = nt.nodes.new("ShaderNodeBump")
            bump.location = (-100, -120)
            bump.inputs["Strength"].default_value = 0.12
            bump.inputs["Distance"].default_value = 0.05
            nt.links.new(wave_tex.outputs["Color"], bump.inputs["Height"])
            nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

        m.diffuse_color = (*c, 1.0)
        _MATS[name] = m

    # painted signboards (see signs.py)
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
    return _MATS.get(name, _MATS.get("sandstone"))


# ---------------------------------------------------------------- builder -> object
def builder_to_object(name, mb, coll=None, bevel=0.0, shade_smooth=False):
    """Turn a MeshBuilder into an optimized Blender object with UVs and <=19,500 tris."""
    if not mb.faces:
        return None
    me = bpy.data.meshes.new(name)
    me.from_pydata([Vector(v) for v in mb.verts], [], [list(f) for f in mb.faces])
    me.validate(verbose=False)

    # material slots
    used = sorted({m for m in mb.fmats}, key=lambda n: MAT_INDEX.get(n, 999))
    slot_of = {}
    for i, mn in enumerate(used):
        me.materials.append(mat(mn))
        slot_of[mn] = i
    for poly, mn in zip(me.polygons, mb.fmats):
        poly.material_index = slot_of.get(mn, 0)

    uv = me.uv_layers.new(name="UVMap")
    for poly, fuv in zip(me.polygons, mb.fuvs):
        for k, li in enumerate(poly.loop_indices):
            if k < len(fuv):
                uv.data[li].uv = fuv[k]

    me.update()

    # Weld coincident vertices (fixes MeshBuilder vertex bloat) & normalise face normals
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    me.update()

    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob

    if shade_smooth:
        for p in me.polygons:
            p.use_smooth = True

    # STRICT ROBLOX 20,000-TRIANGLE CEILING ENFORCEMENT
    ob.data.calc_loop_triangles()
    n_tris = len(ob.data.loop_triangles)
    if n_tris > 19500:
        mod = ob.modifiers.new("RobloxCap", 'DECIMATE')
        mod.ratio = 18500.0 / n_tris
        bpy.ops.object.modifier_apply(modifier=mod.name)
        ob.data.calc_loop_triangles()

    if coll and coll != bpy.context.scene.collection:
        bpy.context.scene.collection.objects.unlink(ob)
        coll.objects.link(ob)

    return ob


# ---------------------------------------------------------------- asset registry
class Registry:
    """Holds prototype objects and instances them as linked duplicates."""

    def __init__(self):
        self.proto = {}
        self.counts = {}
        self.hidden = bpy.data.collections.get("_Prototypes") or \
                      bpy.data.collections.new("_Prototypes")
        if self.hidden.name not in bpy.context.scene.collection.children:
            bpy.context.scene.collection.children.link(self.hidden)
        self.hidden.hide_render = True
        self.hidden.hide_viewport = True

    def define(self, name, mb, bevel=0.0, smooth=False):
        ob = builder_to_object(name, mb, coll=self.hidden, bevel=bevel, shade_smooth=smooth)
        if ob is None:
            raise ValueError("empty builder for " + name)
        self.proto[name] = ob
        self.counts[name] = 0
        return ob

    def exists(self, name):
        return name in self.proto

    def place(self, name, x, y, z=QUAY_Z, rz=0.0, coll=None, label=None):
        """Place an instance. Default elevation is QUAY_Z (+4.0 m)."""
        src = self.proto[name]
        ob = bpy.data.objects.new(label or name, src.data)     # linked duplicate
        ob.location = (x, y, z)
        ob.rotation_euler = Euler((0, 0, math.radians(rz)), 'XYZ')
        (coll or bpy.context.scene.collection).objects.link(ob)
        self.counts[name] += 1
        return ob

    def report(self):
        tot_inst = sum(self.counts.values())
        tot_tris = 0
        print(f"prototypes defined: {len(self.proto)}, total placed instances: {tot_inst}")
        over_limit = []
        for name, ob in sorted(self.proto.items()):
            ob.data.calc_loop_triangles()
            tris = len(ob.data.loop_triangles)
            tot_tris += tris * self.counts[name]
            if tris > 20000:
                over_limit.append((name, tris))
            print(f"  {name:24s} instances={self.counts[name]:3d} tris/proto={tris:6d}")
        if over_limit:
            print("WARNING: Prototypes exceeding Roblox 20k triangle limit:")
            for n, t in over_limit:
                print(f"  ** {n}: {t} tris")
        else:
            print("ALL PROTOTYPES PASS ROBLOX 20,000-TRIANGLE CEILING!")
        return tot_inst, tot_tris, len(self.proto)


def add_water(coll, x0, y0, x1, y1, z=0.0, matname="water"):
    mb = __import__("core").MeshBuilder()
    mb.add_quad((x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z), matname)
    return builder_to_object("WATER_" + matname, mb, coll=coll)


def add_ground(coll, x0, y0, x1, y1, z=-0.2, matname="mud"):
    mb = __import__("core").MeshBuilder()
    mb.add_quad((x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z), matname)
    return builder_to_object("GROUND", mb, coll=coll)


# ---------------------------------------------------------------- environment setup
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
    geo = nt.nodes.new("ShaderNodeNewGeometry"); geo.location = (-600, 0)
    ramp = nt.nodes.new("ShaderNodeValToRGB"); ramp.location = (0, 0)
    ramp.color_ramp.elements[0].color = (*top, 1)
    ramp.color_ramp.elements[1].color = (*bottom, 1)
    nt.links.new(geo.outputs["Incoming"], mapn.inputs["Vector"])
    nt.links.new(mapn.outputs["Vector"], grad.inputs["Vector"])
    nt.links.new(grad.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])
    return w


def setup_sky(sun_az=215.0, sun_el=41.0, strength=0.62, cloud_cover=0.34,
              cloud_scale=4.6, top=(0.30, 0.42, 0.60), bottom=(0.66, 0.66, 0.62)):
    """A physical sky with a procedural cloud deck."""
    w = bpy.data.worlds.new("PortSky")
    bpy.context.scene.world = w
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()

    out = nt.nodes.new("ShaderNodeOutputWorld"); out.location = (900, 0)
    bg = nt.nodes.new("ShaderNodeBackground"); bg.location = (700, 0)
    bg.inputs["Strength"].default_value = strength

    sky = nt.nodes.new("ShaderNodeTexSky"); sky.location = (460, 200)
    sky.sky_type = 'NISHITA'
    sky.sun_disc = False
    sky.sun_elevation = math.radians(sun_el)
    sky.sun_rotation = math.radians(sun_az - 90.0)
    sky.altitude = 60.0
    sky.air_density = 1.0
    sky.dust_density = 1.2

    geo = nt.nodes.new("ShaderNodeNewGeometry"); geo.location = (-400, -180)
    sep = nt.nodes.new("ShaderNodeSeparateXYZ"); sep.location = (-200, -320)
    nt.links.new(geo.outputs["Incoming"], sep.inputs["Vector"])

    hz = nt.nodes.new("ShaderNodeMapRange"); hz.location = (0, -380)
    hz.inputs["From Min"].default_value = 0.004
    hz.inputs["From Max"].default_value = 0.070
    hz.inputs["To Min"].default_value = 0.0
    hz.inputs["To Max"].default_value = 1.0
    nt.links.new(sep.outputs["Z"], hz.inputs["Value"])

    noise = nt.nodes.new("ShaderNodeTexNoise"); noise.location = (-100, -120)
    noise.noise_dimensions = '3D'
    noise.inputs["Scale"].default_value = cloud_scale
    noise.inputs["Detail"].default_value = 4.0
    noise.inputs["Roughness"].default_value = 0.58
    nt.links.new(geo.outputs["Incoming"], noise.inputs["Vector"])

    cramp = nt.nodes.new("ShaderNodeValToRGB"); cramp.location = (160, -120)
    cramp.color_ramp.elements[0].position = 1.0 - cloud_cover
    cramp.color_ramp.elements[1].position = min(1.0, 1.0 - cloud_cover + 0.18)
    nt.links.new(noise.outputs["Fac"], cramp.inputs["Fac"])

    mask = nt.nodes.new("ShaderNodeMath"); mask.location = (420, -180)
    mask.operation = 'MULTIPLY'
    hz_out = hz.outputs.get("Result") or hz.outputs.get("Value") or hz.outputs[0]
    nt.links.new(cramp.outputs["Color"], mask.inputs[0])
    nt.links.new(hz_out, mask.inputs[1])

    ccol = nt.nodes.new("ShaderNodeValToRGB"); ccol.location = (460, -420)
    ccol.color_ramp.elements[0].position = 0.0
    ccol.color_ramp.elements[0].color = (0.60, 0.66, 0.74, 1)
    ccol.color_ramp.elements[1].position = 1.0
    ccol.color_ramp.elements[1].color = (0.90, 0.88, 0.82, 1)
    nt.links.new(noise.outputs["Fac"], ccol.inputs["Fac"])

    mix = nt.nodes.new("ShaderNodeMix"); mix.location = (700, 120)
    mix.data_type = 'RGBA'
    mix.blend_type = 'MIX'
    nt.links.new(mask.outputs[0], mix.inputs["Factor"])
    nt.links.new(sky.outputs["Color"], mix.inputs[6])
    nt.links.new(ccol.outputs["Color"], mix.inputs[7])

    nt.links.new(mix.outputs[2], bg.inputs["Color"])
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
    d = Vector((math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)))
    ob.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    return ob


def add_fill(coll, azimuth_deg=100.0, elevation_deg=28.0, strength=1.1,
             color=(0.72, 0.78, 0.88)):
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
    cd.clip_end = 10000.0
    ob = bpy.data.objects.new(name, cd)
    coll.objects.link(ob)
    ob.location = Vector(loc)
    d = Vector(look_at) - Vector(loc)
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    return ob


def _out_by_name(node, names):
    for n in names:
        if n in node.outputs:
            return node.outputs[n]
    return node.outputs[0]


def setup_compositor_haze(fog_color=(0.74, 0.72, 0.68), start=60.0, depth=520.0, max_fog=0.82):
    """Clean compositor setup passing rendered image through to composite output."""
    sc = bpy.context.scene
    sc.use_nodes = True
    nt = sc.node_tree
    nt.nodes.clear()
    rl = nt.nodes.new("CompositorNodeRLayers")
    rl.location = (-300, 0)
    comp = nt.nodes.new("CompositorNodeComposite")
    comp.location = (200, 0)
    nt.links.new(rl.outputs["Image"], comp.inputs["Image"])


def render_to(path, cam, res=(1600, 900), samples=64, denoise=False, threads=None):
    sc = bpy.context.scene
    sc.camera = cam
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = 'PNG'
    sc.render.filepath = path
    sc.cycles.samples = samples
    sc.cycles.use_denoising = False
    sc.cycles.max_bounces = 7
    sc.cycles.diffuse_bounces = 4
    sc.cycles.glossy_bounces = 3
    sc.cycles.transmission_bounces = 4
    sc.cycles.caustics_reflective = False
    sc.cycles.caustics_refractive = False
    sc.cycles.use_fast_gi = False
    sc.cycles.use_light_tree = True
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.render.render(write_still=True)
    return path

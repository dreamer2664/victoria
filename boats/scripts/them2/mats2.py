"""
mats2.py -- procedural PBR materials (Blender 4.2, Cycles).

Wood uses a Wave ring texture at two scales distorted by Noise, run through a
ColorRamp; the grain direction comes from Generated coordinates scaled by the
object's bounding aspect, so planks grain along their length.  Metals have
procedural tarnish; canvas and rope have weave/twist bump.

Palette indices (symbolic, see parts2/machinery2):
    0 wood_main   1 wood_trim   2 wood_dark   3 brass     4 iron
    5 galvanised  6 leather     7 rope        8 canvas    9 glass
    10 iron_black(paint) 11 card_white 12 lens_red  13 lens_green
    14 copper     15 steel      16 lagging    17 coal     18 fire_glow
    19 gauge_glass 20 red_lead  21 teak_cleading 22 paint_white 23 paint_grey
    24 varnish_spars
"""
from __future__ import annotations
import bpy
import math


def _mat(name):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    return m, nt


def _out(nt):
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (900, 0)
    bs = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bs.location = (620, 0)
    nt.links.new(bs.outputs["BSDF"], out.inputs["Surface"])
    return bs


def _tex_coord(nt, scale=(1, 1, 1)):
    tc = nt.nodes.new("ShaderNodeTexCoord")
    tc.location = (-900, 0)
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.location = (-720, 0)
    mp.inputs["Scale"].default_value = (scale[0], scale[1], scale[2])
    nt.links.new(tc.outputs["Generated"], mp.inputs["Vector"])
    return tc, mp


def wood(name, c_dark, c_mid, c_light, rough=0.32, varnish=0.55, scale=6.0,
         rings=90.0):
    """Layered procedural wood: elongated growth rings distorted by noise for
    the figure, a fine pore layer on top, grain-linked roughness so the varnish
    pools believably, and a per-object tone shift so no two parts match."""
    m, nt = _mat(name)
    bs = _out(nt)
    tc, mp = _tex_coord(nt, scale=(0.55, 3.2, 3.2))   # stretch cells along grain
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.location = (-700, 220)
    noise.inputs["Scale"].default_value = scale
    noise.inputs["Detail"].default_value = 6.0
    noise.inputs["Roughness"].default_value = 0.72
    nt.links.new(mp.outputs["Vector"], noise.inputs["Vector"])
    wave = nt.nodes.new("ShaderNodeTexWave")
    wave.location = (-700, -60)
    wave.wave_type = 'RINGS'
    wave.rings_direction = 'Z'
    wave.inputs["Scale"].default_value = rings
    wave.inputs["Distortion"].default_value = 9.0
    wave.inputs["Detail"].default_value = 6.0
    nt.links.new(noise.outputs["Fac"], wave.inputs["Vector"])  # unstable vec; ok
    pore = nt.nodes.new("ShaderNodeTexWave")
    pore.location = (-700, -320)
    pore.wave_type = 'RINGS'
    pore.rings_direction = 'Z'
    pore.inputs["Scale"].default_value = rings * 3.4
    pore.inputs["Distortion"].default_value = 3.5
    pore.inputs["Detail"].default_value = 3.0
    nt.links.new(noise.outputs["Fac"], pore.inputs["Vector"])
    blend = nt.nodes.new("ShaderNodeMixRGB")
    blend.blend_type = 'MULTIPLY'
    blend.location = (-420, -140)
    blend.inputs["Fac"].default_value = 0.30
    nt.links.new(wave.outputs["Color"], blend.inputs[1])
    nt.links.new(pore.outputs["Color"], blend.inputs[2])
    mix = nt.nodes.new("ShaderNodeValToRGB")
    mix.location = (-200, 60)
    cr = mix.color_ramp
    cr.elements.remove(cr.elements[1])
    lite = tuple(min(1.0, cl * 0.98) for cl in c_light)
    for pos, col in ((0.0, c_dark), (0.40, c_mid), (0.80, c_light), (1.0, lite)):
        el = cr.elements.new(pos) if pos > 0 else cr.elements[0]
        el.position = pos
        el.color = (*col, 1.0)
    nt.links.new(blend.outputs["Color"], mix.inputs["Fac"])
    # per-object tone shift (subtle; keeps parts from looking cloned)
    oi = nt.nodes.new("ShaderNodeObjectInfo")
    oi.location = (-200, 340)
    hs = nt.nodes.new("ShaderNodeHueSaturation")
    hs.location = (60, 160)
    hs.inputs["Saturation"].default_value = 1.0
    nt.links.new(mix.outputs["Color"], hs.inputs["Color"])
    sat_m = nt.nodes.new("ShaderNodeMath"); sat_m.operation = 'MULTIPLY_ADD'
    sat_m.location = (-60, 330)
    nt.links.new(oi.outputs["Random"], sat_m.inputs[0])
    sat_m.inputs[1].default_value = 0.10
    sat_m.inputs[2].default_value = 0.93
    nt.links.new(sat_m.outputs[0], hs.inputs["Value"])
    nt.links.new(hs.outputs["Color"], bs.inputs["Base Color"])
    bs.inputs["Roughness"].default_value = rough
    bs.inputs["Coat Weight"].default_value = varnish * 0.5
    bs.inputs["Coat Roughness"].default_value = 0.22
    # varnish sinks into the figure: roughness breathes with the grain
    rm = nt.nodes.new("ShaderNodeMath"); rm.operation = 'MULTIPLY_ADD'
    rm.location = (60, -60)
    nt.links.new(blend.outputs["Color"], rm.inputs[0])
    rm.inputs[1].default_value = 0.10
    rm.inputs[2].default_value = rough - 0.05
    nt.links.new(rm.outputs[0], bs.inputs["Roughness"])
    # grain bump (figure + pores)
    bump = nt.nodes.new("ShaderNodeBump")
    bump.location = (350, -220)
    bump.inputs["Strength"].default_value = 0.30
    bump.inputs["Distance"].default_value = 0.0018
    nt.links.new(blend.outputs["Color"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bs.inputs["Normal"])
    return m


def solid(name, color, rough=0.7, metallic=0.0, bump_scale=None, bump_str=0.0):
    m, nt = _mat(name)
    bs = _out(nt)
    bs.inputs["Base Color"].default_value = (*color, 1)
    bs.inputs["Roughness"].default_value = rough
    bs.inputs["Metallic"].default_value = metallic
    if bump_scale:
        tc, mp = _tex_coord(nt)
        noise = nt.nodes.new("ShaderNodeTexNoise")
        noise.location = (-500, -100)
        noise.inputs["Scale"].default_value = bump_scale
        noise.inputs["Detail"].default_value = 4.0
        nt.links.new(mp.outputs["Vector"], noise.inputs["Vector"])
        bump = nt.nodes.new("ShaderNodeBump")
        bump.location = (300, -200)
        bump.inputs["Strength"].default_value = bump_str
        bump.inputs["Distance"].default_value = 0.004
        nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
        nt.links.new(bump.outputs["Normal"], bs.inputs["Normal"])
    return m


def metal(name, color, rough=0.25, tarnish=0.25, patina=None):
    """Polished metal with mottled tarnish; `patina` adds oxidation pockets
    (green for brass/copper, rust for iron) in the low-noise recesses and
    roughens them."""
    m, nt = _mat(name)
    bs = _out(nt)
    tc, mp = _tex_coord(nt)
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.location = (-500, 50)
    noise.inputs["Scale"].default_value = 9.0
    noise.inputs["Detail"].default_value = 3.0
    nt.links.new(mp.outputs["Vector"], noise.inputs["Vector"])
    mix = nt.nodes.new("ShaderNodeValToRGB")
    mix.location = (-230, 50)
    dark = tuple(cl * (1 - tarnish) for cl in color)
    mix.color_ramp.elements[0].color = (*dark, 1)
    mix.color_ramp.elements[1].color = (*color, 1)
    mix.color_ramp.elements[1].position = 0.75
    nt.links.new(noise.outputs["Fac"], mix.inputs["Fac"])
    col_socket = mix.outputs["Color"]
    rough_add = 0.0
    if patina is not None:
        pn = nt.nodes.new("ShaderNodeTexNoise")
        pn.location = (-500, -260)
        pn.inputs["Scale"].default_value = 2.6
        pn.inputs["Detail"].default_value = 4.5
        pn.inputs["Roughness"].default_value = 0.8
        nt.links.new(mp.outputs["Vector"], pn.inputs["Vector"])
        pramp = nt.nodes.new("ShaderNodeValToRGB")
        pramp.location = (-230, -260)
        pramp.color_ramp.interpolation = 'EASE'
        pramp.color_ramp.elements[0].position = 0.28   # pockets -> full patina
        pramp.color_ramp.elements[1].position = 0.52   # high spots -> bare metal
        nt.links.new(pn.outputs["Fac"], pramp.inputs["Fac"])
        pmix = nt.nodes.new("ShaderNodeMixRGB")
        pmix.location = (30, 120)
        pmix.inputs[2].default_value = (*patina, 1)
        nt.links.new(pramp.outputs["Color"], pmix.inputs["Fac"])
        nt.links.new(mix.outputs["Color"], pmix.inputs[1])
        col_socket = pmix.outputs["Color"]
        prm = nt.nodes.new("ShaderNodeMath"); prm.operation = 'MULTIPLY'
        prm.location = (30, -120)
        nt.links.new(pramp.outputs["Color"], prm.inputs[0])
        prm.inputs[1].default_value = 0.30             # patina roughness lift
        rough_add = prm.outputs[0]
    nt.links.new(col_socket, bs.inputs["Base Color"])
    bs.inputs["Metallic"].default_value = 0.95
    bs.inputs["Roughness"].default_value = rough
    mf = nt.nodes.new("ShaderNodeMath"); mf.operation = 'MULTIPLY'
    nt.links.new(noise.outputs["Fac"], mf.inputs[0])
    mf.inputs[1].default_value = 0.22
    rr = nt.nodes.new("ShaderNodeMath"); rr.operation = 'ADD'
    nt.links.new(mf.outputs[0], rr.inputs[0]); rr.inputs[1].default_value = rough
    if patina is not None:
        rr2 = nt.nodes.new("ShaderNodeMath"); rr2.operation = 'ADD'
        nt.links.new(rr.outputs[0], rr2.inputs[0])
        nt.links.new(rough_add, rr2.inputs[1])
        nt.links.new(rr2.outputs[0], bs.inputs["Roughness"])
    else:
        nt.links.new(rr.outputs[0], bs.inputs["Roughness"])
    return m


def glass(name, tint=(0.9, 0.95, 0.95), rough=0.06, ior=1.52):
    m, nt = _mat(name)
    bs = _out(nt)
    bs.inputs["Base Color"].default_value = (*tint, 1)
    bs.inputs["Roughness"].default_value = rough
    bs.inputs["Transmission Weight"].default_value = 1.0
    bs.inputs["IOR"].default_value = ior
    m.surface_render_method = 'DITHERED'
    return m


def canvas(name, color=(0.73, 0.68, 0.55)):
    m, nt = _mat(name)
    bs = _out(nt)
    bs.inputs["Base Color"].default_value = (*color, 1)
    bs.inputs["Roughness"].default_value = 0.88
    tc, mp = _tex_coord(nt)
    wx = nt.nodes.new("ShaderNodeTexWave"); wx.wave_type = 'BANDS'
    wx.bands_direction = 'X'; wx.inputs["Scale"].default_value = 340
    wy = nt.nodes.new("ShaderNodeTexWave"); wy.wave_type = 'BANDS'
    wy.bands_direction = 'Y'; wy.inputs["Scale"].default_value = 340
    nt.links.new(mp.outputs["Vector"], wx.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], wy.inputs["Vector"])
    mmul = nt.nodes.new("ShaderNodeMath"); mmul.operation = 'MULTIPLY'
    nt.links.new(wx.outputs["Color"], mmul.inputs[0])
    nt.links.new(wy.outputs["Color"], mmul.inputs[1])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.3
    bump.inputs["Distance"].default_value = 0.004
    nt.links.new(mmul.outputs[0], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bs.inputs["Normal"])
    return m


def rope_mat(name, color=(0.52, 0.42, 0.28)):
    m, nt = _mat(name)
    bs = _out(nt)
    bs.inputs["Base Color"].default_value = (*color, 1)
    bs.inputs["Roughness"].default_value = 0.92
    tc, mp = _tex_coord(nt, scale=(1, 1, 1))
    w = nt.nodes.new("ShaderNodeTexWave"); w.wave_type = 'BANDS'
    w.bands_direction = 'Z'; w.inputs["Scale"].default_value = 220
    w.inputs["Distortion"].default_value = 3.0
    nt.links.new(mp.outputs["Vector"], w.inputs["Vector"])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.5
    bump.inputs["Distance"].default_value = 0.006
    nt.links.new(w.outputs["Color"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bs.inputs["Normal"])
    return m


def topsides(name="TM2_Topsides", z_af=0.0, z_band=0.235):
    """Service paint scheme keyed to the hull, not the texture space: object-
    space Z (Z=0 = loaded waterline) splits varnished mahogany topsides /
    black boot-top band / red-oxide antifouling, with wear noise feathering
    the paint edges.  Only applied to shell + transom parts."""
    m, nt = _mat(name)
    bs = _out(nt)
    tc, mp = _tex_coord(nt, scale=(0.55, 3.2, 3.2))
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 6.0
    noise.inputs["Detail"].default_value = 6.0
    noise.inputs["Roughness"].default_value = 0.72
    nt.links.new(mp.outputs["Vector"], noise.inputs["Vector"])
    wave = nt.nodes.new("ShaderNodeTexWave")
    wave.wave_type = 'RINGS'
    wave.rings_direction = 'Z'
    wave.inputs["Scale"].default_value = 70.0
    wave.inputs["Distortion"].default_value = 9.0
    wave.inputs["Detail"].default_value = 6.0
    nt.links.new(noise.outputs["Fac"], wave.inputs["Vector"])
    wramp = nt.nodes.new("ShaderNodeValToRGB")
    cr = wramp.color_ramp
    cr.elements.remove(cr.elements[1])
    for pos, col in ((0.0, (0.026, 0.013, 0.007)), (0.40, (0.070, 0.033, 0.014)),
                     (0.80, (0.155, 0.082, 0.034)), (1.0, (0.185, 0.098, 0.040))):
        el = cr.elements.new(pos) if pos > 0 else cr.elements[0]
        el.position = pos
        el.color = (*col, 1.0)
    nt.links.new(wave.outputs["Color"], wramp.inputs["Fac"])
    # object-space Z with wear feather
    tco = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tco.outputs["Object"], sep.inputs["Vector"])
    wear = nt.nodes.new("ShaderNodeTexNoise")
    wear.inputs["Scale"].default_value = 22.0
    wear.inputs["Detail"].default_value = 3.0
    nt.links.new(mp.outputs["Vector"], wear.inputs["Vector"])
    wm = nt.nodes.new("ShaderNodeMath"); wm.operation = 'MULTIPLY_ADD'
    nt.links.new(wear.outputs["Fac"], wm.inputs[0])
    wm.inputs[1].default_value = 0.020
    wm.inputs[2].default_value = -0.010
    zadd = nt.nodes.new("ShaderNodeMath"); zadd.operation = 'ADD'
    nt.links.new(sep.outputs["Z"], zadd.inputs[0])
    nt.links.new(wm.outputs[0], zadd.inputs[1])
    lt_af = nt.nodes.new("ShaderNodeMath"); lt_af.operation = 'LESS_THAN'
    nt.links.new(zadd.outputs[0], lt_af.inputs[0]); lt_af.inputs[1].default_value = z_af
    lt_band = nt.nodes.new("ShaderNodeMath"); lt_band.operation = 'LESS_THAN'
    nt.links.new(zadd.outputs[0], lt_band.inputs[0]); lt_band.inputs[1].default_value = z_band
    band_m = nt.nodes.new("ShaderNodeMath"); band_m.operation = 'SUBTRACT'
    nt.links.new(lt_band.outputs[0], band_m.inputs[0])
    nt.links.new(lt_af.outputs[0], band_m.inputs[1])
    af_mix = nt.nodes.new("ShaderNodeMixRGB")
    af_mix.inputs[2].default_value = (0.30, 0.095, 0.055, 1)    # red oxide
    nt.links.new(lt_af.outputs[0], af_mix.inputs["Fac"])
    nt.links.new(wramp.outputs["Color"], af_mix.inputs[1])
    band_mix = nt.nodes.new("ShaderNodeMixRGB")
    band_mix.inputs[2].default_value = (0.012, 0.014, 0.016, 1)  # boot-top black
    nt.links.new(band_m.outputs[0], band_mix.inputs["Fac"])
    nt.links.new(af_mix.outputs["Color"], band_mix.inputs[1])
    nt.links.new(band_mix.outputs["Color"], bs.inputs["Base Color"])
    bs.inputs["Coat Weight"].default_value = 0.12
    bs.inputs["Coat Roughness"].default_value = 0.22
    # roughness: varnish above, paint at band, chalky antifouling below
    rvar = nt.nodes.new("ShaderNodeMath"); rvar.operation = 'MULTIPLY'
    nt.links.new(lt_af.outputs[0], rvar.inputs[0]); rvar.inputs[1].default_value = 0.28
    rband = nt.nodes.new("ShaderNodeMath"); rband.operation = 'MULTIPLY'
    nt.links.new(band_m.outputs[0], rband.inputs[0]); rband.inputs[1].default_value = 0.08
    rsum = nt.nodes.new("ShaderNodeMath"); rsum.operation = 'ADD'
    nt.links.new(rvar.outputs[0], rsum.inputs[0]); nt.links.new(rband.outputs[0], rsum.inputs[1])
    rfin = nt.nodes.new("ShaderNodeMath"); rfin.operation = 'ADD'
    nt.links.new(rsum.outputs[0], rfin.inputs[0]); rfin.inputs[1].default_value = 0.28
    nt.links.new(rfin.outputs[0], bs.inputs["Roughness"])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.28
    bump.inputs["Distance"].default_value = 0.0018
    nt.links.new(wave.outputs["Color"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bs.inputs["Normal"])
    return m


def chequer_steel(name="TM2_Chequer_Steel"):
    """Rolled steel chequer plate: crossed tread bars, semi-bright."""
    m, nt = _mat(name)
    bs = _out(nt)
    bs.inputs["Base Color"].default_value = (0.135, 0.145, 0.155, 1)
    bs.inputs["Metallic"].default_value = 0.78
    bs.inputs["Roughness"].default_value = 0.42
    tc, mp = _tex_coord(nt, scale=(1, 1, 1))
    wx = nt.nodes.new("ShaderNodeTexWave"); wx.wave_type = 'BANDS'
    wx.bands_direction = 'X'; wx.inputs["Scale"].default_value = 230.0
    wy = nt.nodes.new("ShaderNodeTexWave"); wy.wave_type = 'BANDS'
    wy.bands_direction = 'Y'; wy.inputs["Scale"].default_value = 230.0
    nt.links.new(mp.outputs["Vector"], wx.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], wy.inputs["Vector"])
    mm = nt.nodes.new("ShaderNodeMath"); mm.operation = 'MULTIPLY'
    nt.links.new(wx.outputs["Color"], mm.inputs[0])
    nt.links.new(wy.outputs["Color"], mm.inputs[1])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.5
    bump.inputs["Distance"].default_value = 0.0028
    nt.links.new(mm.outputs[0], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bs.inputs["Normal"])
    return m


def water(name="Sea_Water"):
    m, nt = _mat(name)
    bs = _out(nt)
    bs.inputs["Base Color"].default_value = (0.016, 0.055, 0.062, 1)
    bs.inputs["Roughness"].default_value = 0.05
    bs.inputs["Metallic"].default_value = 0.0
    bs.inputs["Coat Weight"].default_value = 0.6
    tc = nt.nodes.new("ShaderNodeTexCoord")
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 1.7
    noise.inputs["Detail"].default_value = 5.0
    noise.inputs["Roughness"].default_value = 0.8
    noise.inputs["Distortion"].default_value = 0.35
    nt.links.new(tc.outputs["Generated"], noise.inputs["Vector"])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.14
    bump.inputs["Distance"].default_value = 0.20
    nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bs.inputs["Normal"])
    return m


def build_palette():
    """Return the ordered material list shared by every boat part."""
    P = []
    P.append(wood("TM2_Mahogany", (0.030, 0.016, 0.008), (0.085, 0.040, 0.017),
                  (0.215, 0.115, 0.048), rough=0.28, varnish=0.85, rings=70))      # 0
    P.append(wood("TM2_Teak", (0.055, 0.036, 0.016), (0.155, 0.100, 0.047),
                  (0.34, 0.235, 0.125), rough=0.36, varnish=0.6, rings=95))        # 1
    P.append(wood("TM2_Oak_Dark", (0.035, 0.024, 0.012), (0.095, 0.062, 0.030),
                  (0.21, 0.145, 0.075), rough=0.5, varnish=0.3, rings=80))         # 2
    P.append(metal("TM2_Brass", (0.44, 0.27, 0.09), rough=0.16, tarnish=0.35,
                  patina=(0.055, 0.095, 0.070)))                        # 3
    P.append(metal("TM2_Iron", (0.055, 0.06, 0.07), rough=0.45, tarnish=0.30,
                  patina=(0.135, 0.055, 0.022)))                        # 4
    P.append(metal("TM2_Galvanised", (0.36, 0.39, 0.42), rough=0.42, tarnish=0.25))# 5
    P.append(solid("TM2_Leather", (0.13, 0.075, 0.04), rough=0.55, bump_scale=40,
                   bump_str=0.25))                                                 # 6
    P.append(rope_mat("TM2_Rope"))                                                 # 7
    P.append(canvas("TM2_Canvas"))                                                 # 8
    P.append(glass("TM2_Glass"))                                                   # 9
    P.append(solid("TM2_Iron_Paint", (0.035, 0.045, 0.055), rough=0.38,
                   metallic=0.35, bump_scale=8, bump_str=0.10))                    # 10
    P.append(solid("TM2_Card", (0.92, 0.90, 0.83), rough=0.9))                     # 11
    P.append(glass("TM2_Lens_Red", tint=(0.8, 0.02, 0.008), rough=0.05))           # 12
    P.append(glass("TM2_Lens_Green", tint=(0.01, 0.30, 0.05), rough=0.05))         # 13
    P.append(metal("TM2_Copper", (0.42, 0.17, 0.09), rough=0.30, tarnish=0.40,
                  patina=(0.085, 0.215, 0.165)))                        # 14
    P.append(metal("TM2_Steel", (0.32, 0.35, 0.39), rough=0.24, tarnish=0.2))      # 15
    P.append(canvas("TM2_Lagging", color=(0.80, 0.78, 0.72)))                      # 16
    P.append(solid("TM2_Coal", (0.018, 0.018, 0.021), rough=0.42, metallic=0.25,
                   bump_scale=26, bump_str=0.5))                                   # 17
    P.append(solid("TM2_Fire", (0.9, 0.25, 0.03), rough=1.0))                      # 18
    P.append(glass("TM2_Gauge_Glass", tint=(0.85, 0.93, 0.95), rough=0.02))        # 19
    P.append(solid("TM2_RedLead", (0.35, 0.08, 0.04), rough=0.6))                  # 20
    P.append(wood("TM2_Cleading", (0.05, 0.033, 0.015), (0.130, 0.085, 0.040),
                  (0.265, 0.19, 0.10), rough=0.38, varnish=0.6, rings=110))        # 21
    P.append(solid("TM2_Paint_White", (0.83, 0.83, 0.79), rough=0.42,
                   bump_scale=12, bump_str=0.06))                                  # 22
    P.append(solid("TM2_Paint_Grey", (0.20, 0.22, 0.24), rough=0.42,
                   bump_scale=10, bump_str=0.06))                                  # 23
    P.append(wood("TM2_Spar_Varnish", (0.06, 0.040, 0.016), (0.16, 0.105, 0.05),
                  (0.34, 0.245, 0.13), rough=0.26, varnish=0.9, rings=120))        # 24
    P.append(topsides())                                                           # 25
    P.append(chequer_steel())                                                      # 26
    return P


def palette_boat(len_=25):
    return build_palette()

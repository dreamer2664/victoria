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
    m, nt = _mat(name)
    bs = _out(nt)
    tc, mp = _tex_coord(nt)
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.location = (-500, 200)
    noise.inputs["Scale"].default_value = scale
    noise.inputs["Detail"].default_value = 5.0
    noise.inputs["Roughness"].default_value = 0.75
    nt.links.new(mp.outputs["Vector"], noise.inputs["Vector"])
    wave = nt.nodes.new("ShaderNodeTexWave")
    wave.location = (-500, -120)
    wave.wave_type = 'RINGS'
    wave.rings_direction = 'Z'
    wave.inputs["Scale"].default_value = rings
    wave.inputs["Distortion"].default_value = 7.0
    wave.inputs["Detail"].default_value = 5.0
    nt.links.new(noise.outputs["Fac"], wave.inputs["Vector"])  # unstable vec; ok
    mix = nt.nodes.new("ShaderNodeValToRGB")
    mix.location = (-220, 60)
    cr = mix.color_ramp
    cr.elements.remove(cr.elements[1])
    for pos, col in ((0.0, c_dark), (0.45, c_mid), (1.0, c_light)):
        el = cr.elements.new(pos) if pos > 0 else cr.elements[0]
        el.position = pos
        el.color = (*col, 1.0)
    nt.links.new(wave.outputs["Color"], mix.inputs["Fac"])
    nt.links.new(mix.outputs["Color"], bs.inputs["Base Color"])
    bs.inputs["Roughness"].default_value = rough
    bs.inputs["Coat Weight"].default_value = varnish * 0.4
    bs.inputs["Coat Roughness"].default_value = 0.25
    # subtle grain bump
    bump = nt.nodes.new("ShaderNodeBump")
    bump.location = (350, -220)
    bump.inputs["Strength"].default_value = 0.35
    bump.inputs["Distance"].default_value = 0.002
    nt.links.new(mix.outputs["Color"], bump.inputs["Height"])
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


def metal(name, color, rough=0.25, tarnish=0.25):
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
    nt.links.new(mix.outputs["Color"], bs.inputs["Base Color"])
    bs.inputs["Metallic"].default_value = 0.95
    bs.inputs["Roughness"].default_value = rough
    mf = nt.nodes.new("ShaderNodeMath"); mf.operation = 'MULTIPLY'
    nt.links.new(noise.outputs["Fac"], mf.inputs[0])
    mf.inputs[1].default_value = 0.22
    rr = nt.nodes.new("ShaderNodeMath"); rr.operation = 'ADD'
    nt.links.new(mf.outputs[0], rr.inputs[0]); rr.inputs[1].default_value = rough
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
    P.append(metal("TM2_Brass", (0.44, 0.27, 0.09), rough=0.16, tarnish=0.35))     # 3
    P.append(metal("TM2_Iron", (0.055, 0.06, 0.07), rough=0.45, tarnish=0.3))      # 4
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
    P.append(metal("TM2_Copper", (0.42, 0.17, 0.09), rough=0.30, tarnish=0.4))     # 14
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
    return P


def palette_boat(len_=25):
    return build_palette()

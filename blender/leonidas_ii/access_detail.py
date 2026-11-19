"""Connected mast/funnel climbing ladders, not isolated decorative rungs.

Separate frame and rung meshes let the independent auditor ray-test every
rung cap against its side rails, and actual frame mounts against the mast,
funnel shell, deck or nest underside. No avatar climbing/strength is implied.
"""
import math
import numpy as np
from meshkit import Mesh, collection, ACCESS_LADDERS


def emit_ladder(identifier, frame, rungs, metadata, deck):
    frame_name = 'Climbing_Ladder_' + identifier + '_Frame'
    rung_name = 'Climbing_Ladder_' + identifier + '_Rungs'
    frame.emit(frame_name, collection('ExteriorAccess'), kind='fitting', deck=deck)
    rungs.emit(rung_name, collection('ExteriorAccess'), kind='fitting', deck=deck)
    ACCESS_LADDERS.append(dict(id=identifier, frame_prefix=frame_name,
                               rungs_prefix=rung_name, **metadata))


def mast_ladder(name, x, z0, height, radius, nest_z, deck):
    frame, rungs = Mesh(), Mesh()
    # The mizzen rises through an occupied after deckhouse: its exterior
    # climbing frame starts on the actual crowned roof, not through it.
    base = 20.035 if name == 'Mizzen' else z0
    floor_target = (dict(target_prefix='After_DeckCabin_Continuous_CrownedRoof')
                    if name == 'Mizzen' else
                    dict(target_kind='deck', target_deck=deck))
    rake, offset, half_width = .045, radius + .08, .20
    axis_x = lambda z: x - (z-z0)*rake
    plane_x = lambda z: axis_x(z) - offset
    mounts, rung_rows = [], []
    for side in (-1, 1):
        y = side*half_width
        frame.rod((plane_x(base+.02), y, base+.02),
                  (plane_x(nest_z-.025), y, nest_z-.025), .021, 'Iron', 10)
        frame.box((plane_x(base), y, base+.012), (.16, .13, .040), 'Iron', .009)
        mounts.append(dict(role='roof sole' if name == 'Mizzen' else 'deck sole',
                           origin=(plane_x(base), y, base+.10),
                           direction=(0, 0, -1), distance=.30, **floor_target))
        # The rails arrive THROUGH the actual hatch and have lateral
        # cleats under the remaining side rim, plus handholds to its guard.
        frame.rod((plane_x(nest_z-.025),y,nest_z-.025),(plane_x(nest_z-.025),side*.29,nest_z-.025),.021,'Iron',10)
        guard_y=side*math.sqrt(.66**2-(radius+.08)**2)
        frame.tube([(plane_x(nest_z-.025),y,nest_z-.025),(plane_x(nest_z),y,nest_z+.85),(plane_x(nest_z),guard_y,nest_z+.85)],.021,'Iron',10)
        mounts.append(dict(role='nest side rim below real hatch',
                           origin=(plane_x(nest_z-.045), side*.28, nest_z-.15),
                           direction=(0, 0, 1), distance=.30,
                           target_prefix='Masts_Derricks_Crowsnests'))
    for z in np.arange(base+.5, nest_z-.12, .37):
        z = float(z)
        center = (plane_x(z), 0, z)
        rungs.rod((center[0], -half_width, z), (center[0], half_width, z),
                  .014, 'Iron', 8)
        rung_rows.append(dict(center=center, half_width=half_width))
    # A band clasps the tapered pole. A finite T-bracket carries both rails
    # instead of silently stopping each rung 80-180mm in front of the mast.
    levels = list(np.arange(base+.55, nest_z-.4, 3.0)) + [nest_z-.25]
    for z in levels:
        z = float(z)
        mast_radius = radius*(1-.58*(z-z0)/height)
        frame.ring((axis_x(z), 0, z), mast_radius+.018, .026,
                   'Iron', 22, 6)
        frame.rod((axis_x(z)-mast_radius+.020, 0, z),
                  (plane_x(z), 0, z), .020, 'Iron', 10)
        frame.rod((plane_x(z), -.225, z), (plane_x(z), .225, z),
                  .020, 'Iron', 10)
        mounts.append(dict(role='pole clamp and T-bracket',
                           origin=(axis_x(z)-radius-.20, 0, z),
                           direction=(1, 0, 0), distance=.55,
                           target_prefix='Masts_Derricks_Crowsnests'))
    frame.tags['CarrierAndPoleSupportedMastLadder'] += 1
    emit_ladder('Mast_'+name, frame, rungs,
                dict(type='mast', rungs=rung_rows, mounts=mounts), deck)


def funnel_ladder(x, z0=17.2, radius=1.70):
    frame, rungs = Mesh(), Mesh()
    rake, half_width = math.tan(math.radians(5)), .25
    axis_x = lambda z: x-(z-z0)*rake
    plane_x = lambda z: axis_x(z)+2.06
    for side in (-1, 1):
        frame.tube([(plane_x(z), side*half_width, z)
                    for z in (17.48, 21., 25., 29.)], .021, 'Iron', 10)
    # A small shell/coaming-carried landing, not a ladder beginning over
    # the open uptake well. No avatar collision/climbing is inferred.
    frame.box((x+2.16,0,17.46),(.40,.72,.060),'Iron',.008)
    rung_rows, mounts = [], []
    for side in (-1,1):mounts.append(dict(role='coaming entry tread',origin=(x+2.16,side*.25,17.55),direction=(0,0,-1),distance=.20,target_prefix='Funnels_And_CasingWalls'))
    for z in [17.64]+list(np.arange(18., 29., .34)):
        z = float(z)
        rungs.rod((plane_x(z), -half_width, z),
                  (plane_x(z), half_width, z), .014, 'Iron', 8)
        rung_rows.append(dict(center=(plane_x(z), 0, z), half_width=half_width))
    for z in (17.78, 21., 25., 28.8):
        factor = (1.02-.02*(z-z0)/(19.-z0) if z < 19. else
                  1.-.05*(z-19.)/(28.5-19.) if z < 28.5 else .95)
        for side in (-1, 1):
            y = side*half_width
            shell_x = axis_x(z)+radius*1.15*factor*math.sqrt(
                1-(y/(radius*factor))**2)
            frame.rod((shell_x-.025, y, z), (plane_x(z)+.008, y, z),
                      .021, 'Iron', 10)
            mounts.append(dict(role='funnel shell stand-off',
                               origin=(plane_x(z)+.20, y, z),
                               direction=(-1, 0, 0), distance=.65,
                               target_prefix='Funnels_And_CasingWalls'))
    frame.tags['ShellBracketedFunnelLadder'] += 1
    emit_ladder('Funnel_'+format(x, 'g'), frame, rungs,
                dict(type='funnel', rungs=rung_rows, mounts=mounts), 'boat')

"""
layout.py -- where the steam cutter's machinery actually sits.

One source of truth.  These numbers were previously typed twice: once in
build_steam_cutter.py, once in the inboard-profile sheet in drawings.py, and
the two had drifted apart.  The sheet drew a 0.36 m wide boiler where the model
had 0.81 m, put the funnel a metre forward of the boiler it belongs to, and
labelled a coal bunker forward of the boiler while its own note 5 said the
bunker was abaft it.  A drawing that disagrees with the model is worse than no
drawing: it is a specification that cannot be met.

Both files import this now.
"""

# all metres, +X forward, +Y port, +Z up, Z = 0 at the load waterline
STEAM = {
    # the boiler is the datum: everything in the engine room is set out from it
    "boiler": dict(x=0.50, r=0.360, h=0.860,
                   label="Boiler, vertical fire-tube\n0.72 m dia x 0.86 m"),
    # inverted vertical engine, abaft the boiler
    "engine": dict(x=-0.78, hx=0.20, z=(-0.30, 0.42),
                   label="Inverted vertical engine\n5 1/2 in x 6 in"),
    # coal bunker: ABAFT the boiler, forward of the engine, where the fireman
    # stands.  Bunkerage forward of the boiler is a passenger's lap.
    "bunker": dict(x=-0.20, hx=0.24, z=(-0.10, 0.52), label="Coal bunker"),
    "funnel": dict(x=0.52, r=0.095, top=None, label="Funnel"),
    "thrust_block": dict(x=(-1.18, -1.02), z=(-0.10, 0.12), label="Thrust block"),
    "screw": dict(x=-3.42, z=-0.45, dia=0.340, label="Screw 0.34 m dia"),
    "rudder": dict(x=(-3.78, -3.62), z=(-0.60, 0.66), label="Rudder"),
}


def steam_stations() -> dict:
    """The same layout expressed as x extents, for the drawing sheet."""
    b = STEAM["boiler"]
    e = STEAM["engine"]
    k = STEAM["bunker"]
    return dict(
        boiler=(b["x"] - b["r"], b["x"] + b["r"]),
        engine=(e["x"] - e["hx"], e["x"] + e["hx"]),
        bunker=(k["x"] - k["hx"], k["x"] + k["hx"]),
    )

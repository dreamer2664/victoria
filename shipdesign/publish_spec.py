"""Publish interfaces/ship_spec.json and DIMENSION_MANIFEST.json.

Everything here is read straight out of the design modules, so the published
spec can never drift from the geometry that was actually built.  Run:

    python3 -W ignore -m shipdesign.publish_spec
"""
from __future__ import annotations
import json
import os

from .spec import (SHIP, DECK_Z, FUNNELS, MASTS, RIG, LIFEBOATS,
                   STARBOARD_BOATS, PORT_BOATS, SCALE, PALETTE)
from . import layout
from .hull import HULL

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _clean(v):
    if isinstance(v, dict):
        return {k: _clean(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [_clean(x) for x in v]
    if hasattr(v, "item"):
        v = v.item()
    if isinstance(v, float):
        return round(v, 4)
    return v


def build_ship_spec():
    h = HULL.hydrostatics(nx=401)
    return _clean({
        "schema": "victoria.interfaces/ship_spec",
        "version": "1.0",
        "generated": "2026-11-15",
        "from_agent": "03 — The Ocean Liner",
        "for_agent": "02 — The Small Boats (and any other agent integrating a vessel)",
        "units": {
            "length": "metre",
            "roblox": "1 stud = 0.28 m (documented Roblox conversion)",
            "frame": ("ship-local: +X forward, +Y to port, +Z up from the base "
                      "line; origin amidships on the centreline at the base line"),
        },
        "vessel": {
            "name": SHIP["name"],
            "full_name": SHIP["prefix"] + " " + SHIP["name"],
            "line": SHIP["company"],
            "yard_number": SHIP["yard_number"],
            "laid_down": SHIP.get("laid_down"),
            "launched": SHIP.get("launched"),
            "completed": SHIP.get("completed"),
            "route": SHIP["service"],
            "flag": SHIP["flag"],
            "principal_dimensions_m": {
                 "loa": SHIP["loa"], "lwl": SHIP["lwl"],
                 "lbp": SHIP["lbp"], "beam_moulded": SHIP["beam"],
                "depth_moulded": SHIP["depth_moulded"],
                "draft_design": SHIP["draft"],
                "freeboard_main_deck": SHIP["freeboard_main"],
            },
            "tonnage": {
                 "gross": SHIP["gross_register_est"],
                "net": SHIP["net_register_est"],
                "displacement_t": SHIP["displacement_t"],
                "lightship_t": SHIP["lightship_t"],
            },
            "capacity": {
                "cargo_t": SHIP["cargo_capacity_t"],
                "coal_t": SHIP["coal_capacity_t"],
                "coal_per_day_t": SHIP["coal_consumption_tpd"],
            },
            "passengers": {
                 "first": SHIP["passengers"]["first"],
                "second": SHIP["passengers"]["second"],
                "third": SHIP["passengers"]["third"],
                "total": SHIP["passengers"]["total"],
            },
            "crew": SHIP["crew"],
            "propulsion": {
                "type": "vertical inverted direct-acting triple-expansion, single screw",
                "cylinders_m": SHIP["cylinder_dia_m"],
                "stroke_m": SHIP["stroke_m"],
                 "ihp": SHIP["engine_ihp"], "rpm": SHIP["engine_rpm"],
                "boilers": SHIP["boilers"],
                "boiler_pressure_bar": SHIP["boiler_pressure_bar"],
                "propeller": {
                    "diameter_m": SHIP["prop_diameter_m"],
                    "pitch_m": SHIP["prop_pitch_m"],
                    "blades": SHIP["prop_blades"],
                    "shaft_diameter_m": SHIP["shaft_dia_m"],
                },
                "rudder_area_m2": SHIP["rudder_area_m2"],
            },
            "performance": {
                 "service_speed_kn": SHIP["service_speed_kn"],
                "max_speed_kn": SHIP["max_speed_kn"],
            },
            "construction": {
                "frames_spacing_m": SHIP["frame_spacing_m"],
                "frames": SHIP["num_frames"],
                "shell_thickness_mm": SHIP["shell_plate_thickness_mm"],
                "watertight_bulkheads": len(layout.BULKHEADS),
                "strake_width_m": SHIP["strake_height_m"],
            },
        },
        "decks": [{"key": k, "name": n, "height_m": z,
                   "extent_m": list(e)} for k, n, z, e in layout.DECKS],
        "hydrostatics": h,
        "funnels": FUNNELS,
        "masts": MASTS,
        "rig": RIG,
        "boats": {"outfit": LIFEBOATS, "starboard": STARBOARD_BOATS,
                  "port": PORT_BOATS},
        "layout": {
            "rooms": [{"name": r["name"], "deck": r["deck"], "use": r["use"],
                       "x0": r["x0"], "x1": r["x1"],
                       "y0": r["y0"], "y1": r["y1"],
                       "ceiling_m": layout.room_ceiling_z(r["deck"])[1]}
                      for r in layout.ROOMS],
            "doors": layout.DOORS,
            "stairs": layout.STAIRS,
            "bulkhead_stations_m": layout.BULKHEADS,
        },
        "scale": {"metres_per_stud": SCALE["metres_per_stud"],
                  "studs_per_metre": round(1.0 / SCALE["metres_per_stud"], 6),
                  "loa_studs": round(SHIP["loa"] / SCALE["metres_per_stud"], 1),
                  "beam_studs": round(SHIP["beam"] / SCALE["metres_per_stud"], 1)},
        "roblox": {
            "modules": "exports/roblox_modules.json",
            "scripts": ["AurelianShipController.server.lua",
                        "Aurelian_Telegraph.server.lua",
                        "Aurelian_EngineAnim.server.lua",
                        "Aurelian_DoorsAndLighting.server.lua",
                        "Aurelian_SmokeAndWake.client.lua"],
            "attributes": ["Throttle", "ShaftRPM", "ShaftAngle", "SpeedKn",
                           "Heading", "RudderAngle", "Telegraph",
                           "BoilerPressure", "EngineIHP", "SmokeIntensity",
                           "MooringsClear", "EngineRunning", "LightsOut"],
        },
        "interfaces": {"small_boats": "interfaces/boats_spec.json",
                       "exports": "exports/roblox_modules.json"},
    })


def build_manifest():
    """DIMENSION_MANIFEST: every dimension used, with its provenance."""
    h = HULL.hydrostatics(nx=401)
    rows = []

    def d(name, value, unit, source, basis):
        rows.append({"dimension": name, "value": value, "unit": unit,
                     "source": source, "basis": basis})

    S = "shipdesign/spec.py"
    L = "shipdesign/layout.py"
    H = "shipdesign/hull.py (computed hydrostatics)"
    d("length overall", SHIP["loa"], "m", S, "design choice, within the 1884-89 express-liner band")
    d("length between perpendiculars", SHIP["lbp"], "m", S, "design choice")
    d("length on waterline", SHIP["lwl"], "m", S, "design choice")
    d("beam moulded", SHIP["beam"], "m", S, "design choice; Teutonic 17.43 m, Umbria 17.43 m")
    d("depth moulded", SHIP["depth_moulded"], "m", S, "design choice")
    d("draft design", SHIP["draft"], "m", S, "design choice")
    d("block coefficient", h["cb"], "-", H, "computed from the midship sections and the ends")
    d("midship area coefficient", h["cm"], "-", H, "computed")
    d("prismatic coefficient", h["cp"], "-", H, "computed")
    d("waterplane coefficient", h["cw"], "-", H, "computed")
    d("displacement", h["displacement_t"], "t", H, "computed; target 13,600 t from Umbria's 13,300 t")
    d("lightship", SHIP["lightship_t"], "t", S, "displacement less deadweight")
    d("gross tonnage", SHIP["gross_register_est"], "GRT", S, "design choice; Teutonic 9,984, Umbria 7,718")
    d("coal capacity", SHIP["coal_capacity_t"], "t", S, "36 h at full power + 25% reserve")
    d("coal per day at service", SHIP["coal_consumption_tpd"], "t", S, "9 boilers x 4 furnaces, period specific consumption")
    d("service speed", SHIP["service_speed_kn"], "kn", S, "design choice; Teutonic 19.5, Umbria 19")
    d("indicated horsepower", SHIP["engine_ihp"], "IHP", S, "design choice; Umbria 14,500")
    d("revolutions", SHIP["engine_rpm"], "rpm", S, "period practice for a 5.3 m propeller at 19.3 kn")
    d("cylinder diameters (HP/IP/LP)", SHIP["cylinder_dia_m"], "m", S, "triple-expansion ratio 1 : 1.63 : 2.66")
    d("stroke", SHIP["stroke_m"], "m", S, "period practice, stroke ~= 0.5 x LP bore")
    d("boiler pressure", SHIP["boiler_pressure_bar"], "bar", S, "1889 practice, 150-165 lb/in2")
    d("propeller diameter", SHIP["prop_diameter_m"], "m", S, "limited by 6.5 m draft and the aperture")
    d("propeller pitch", SHIP["prop_pitch_m"], "m", S, "1.30 x diameter, giving 12% slip at 62 rpm")
    d("shaft diameter", SHIP["shaft_dia_m"], "m", S, "period rule for 14,000 IHP")
    d("rudder area", SHIP["rudder_area_m2"], "m2", S, "1/60 to 1/70 of the immersed lateral area")
    d("frame spacing", SHIP["frame_spacing_m"], "m", S, "3 ft, the standard British practice")
    d("number of frames", SHIP["num_frames"], "-", S, "LBP / frame spacing")
    d("shell plate thickness", SHIP["shell_plate_thickness_mm"], "mm", S, "Lloyd's 1887 rules for a vessel of this size")
    d("strake width", SHIP["strake_height_m"], "m", S, "6 ft plates")
    d("watertight bulkheads", len(layout.BULKHEADS), "-", L, "10-12 period practice; 14 including the collision bulkheads")
    for k, n, z, e in layout.DECKS:
        d("deck height: %s" % n, z, "m", L, "design choice, sheer and storey heights")
    for f in FUNNELS:
        d("funnel position/diameter", {"x_m": f["x"], "diameter_m": f["dia"],
                                       "top_m": f["top_z"]}, "m", S,
          "rakes clear of the bridge; each rises through its own casing")
    for m in MASTS:
        d("mast %s" % m["name"], {"x_m": m["x"], "height_m": m["height_m"],
                                  "diameter_m": m["diameter"]}, "m", S,
          "stepped on a bulkhead or in a trunked vestibule")
    d("Roblox scale", SCALE["metres_per_stud"], "m/stud", S,
      "documented Roblox conversion, 1 stud = 0.28 m")
    d("stair riser / tread", {"riser_m": 0.178, "tread_m": 0.285}, "m", L,
      "period practice, 7 in riser / 11 in tread")
    return _clean({
        "schema": "victoria.dimension_manifest", "version": "1.0",
        "generated": "2026-11-15",
        "ship": SHIP["name"],
        "note": ("Every dimension the model uses, with the file it comes from "
                 "and the basis for it.  'computed' means derived from the hull "
                 "form by hull.hydrostatics(); 'design choice' means an "
                 "engineering decision inside the historical band, justified "
                 "in HISTORICAL_EVIDENCE.md."),
        "dimensions": rows,
    })


def main():
    sp = build_ship_spec()
    mf = build_manifest()
    for path, data in (("interfaces/ship_spec.json", sp),
                       ("DIMENSION_MANIFEST.json", mf)):
        p = os.path.join(ROOT, path)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as fh:
            json.dump(data, fh, indent=2)
        print("wrote", p)
    print("%d dimensions catalogued" % len(mf["dimensions"]))


if __name__ == "__main__":
    main()

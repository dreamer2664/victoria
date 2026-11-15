"""
specs.py -- single source of truth for the dimensions, weights and interface
geometry of the two ship's boats.

Every number the ship agent needs (davit positions, cradle points, boarding
heights, export origin) comes from here, and interfaces/boats_spec.json is
generated from this module so the JSON can never drift from the model.

Units: metres, kilograms.  Angles in degrees.
Roblox conversion: ROBLOX_STUD_PER_M = 1 / 0.28 (1 stud = 0.28 m).
"""

from __future__ import annotations

STUD_PER_M = 1.0 / 0.28
FOOT = 0.3048
INCH = 0.0254

from .hull import HullDesign
from . import hydro


# --------------------------------------------------------------------------
# BOAT A -- 25 ft steam cutter (1888)
# --------------------------------------------------------------------------
STEM_CUTTER = HullDesign(
    "steam_cutter_1888",
    loa=25 * FOOT,              # 7.620 m -- documented on the 1888 drawing title
    bmax=7 * FOOT / 2,          # 2.134 m beam overall
    sheer_pts=[(0.0, 0.775), (0.10, 0.690), (0.26, 0.600), (0.48, 0.540),
               (0.68, 0.530), (0.84, 0.560), (0.94, 0.600), (1.0, 0.640)],
    keel_pts=[(0.0, -0.300), (0.10, -0.520), (0.22, -0.610), (0.36, -0.655),
              (0.54, -0.665), (0.70, -0.645), (0.82, -0.570), (0.92, -0.430),
              (1.0, -0.240)],
    hb_pts=[(0.0, 0.055), (0.09, 0.500), (0.22, 0.820), (0.40, 0.970),
            (0.58, 1.000), (0.75, 0.985), (0.88, 0.900), (1.0, 0.600)],
    full_fwd=1.25, full_aft=2.05, round_fwd=1.50, round_aft=2.45,
    flare_fwd=0.11, flare_aft=0.03, stem_rake=0.11, stern_rake=0.20,
    transom_frac=0.58,
)


# --------------------------------------------------------------------------
# BOAT B -- 25 ft clinker rowing cutter
# --------------------------------------------------------------------------
ROW_CUTTER = HullDesign(
    "rowing_cutter_25ft",
    loa=25 * FOOT,
    bmax=(6 * FOOT + 3 * INCH) / 2,   # beam 1.905 m overall -> half-breadth
    sheer_pts=[(0.0, 0.720), (0.09, 0.640), (0.24, 0.565), (0.45, 0.518),
               (0.66, 0.505), (0.83, 0.528), (0.93, 0.562), (1.0, 0.600)],
    keel_pts=[(0.0, -0.200), (0.10, -0.400), (0.20, -0.492), (0.35, -0.540),
              (0.52, -0.552), (0.68, -0.535), (0.80, -0.490), (0.90, -0.400),
              (1.0, -0.290)],
    hb_pts=[(0.0, 0.030), (0.10, 0.460), (0.25, 0.780), (0.40, 0.940),
            (0.55, 1.000), (0.70, 0.960), (0.85, 0.820), (0.95, 0.620), (1.0, 0.430)],
    full_fwd=1.10, full_aft=1.85, round_fwd=1.45, round_aft=2.20,
    flare_fwd=0.09, flare_aft=0.02, stem_rake=0.09, stern_rake=0.16,
    transom_frac=0.43,
)

# --------------------------------------------------------------------------
# weights
# --------------------------------------------------------------------------
# A 25 ft pulling cutter is a lightly built hoisting boat.  The 1905
# establishment figures (Kipling Society / ORG) give 34 ft cutter 1.5 tons and
# 27 ft whaler 0.75 tons; scaling by L^3 to 25 ft gives ~0.6-0.8 t for the bare
# boat, and a fully equipped, painted, oared Service cutter comes out near
# 1.0 t.  The table is itemised so it can be audited.
ROW_WEIGHTS = {
    "hull_planking_11_strakes_kg": 470,
    "keel_stem_sternpost_transom_kg": 105,
    "gunwales_inwales_knees_kg": 78,
    "thwarts_benches_floorboards_kg": 96,
    "oars_10_kg": 10 * 17.5,
    "rudder_tiller_kg": 26,
    "fittings_mooring_rowlocks_kg": 38,
    "paint_varnish_kg": 29,
}
ROW_WEIGHTS["light_kg"] = round(sum(ROW_WEIGHTS.values()), 1)
ROW_CREW = 10  # 10 oars, double banked (2 men per thwart) plus coxswain
ROW_WEIGHTS["crew_kg"] = ROW_CREW * 80 + 80
ROW_WEIGHTS["loaded_kg"] = round(ROW_WEIGHTS["light_kg"] + ROW_WEIGHTS["crew_kg"], 1)

# 1905 establishment: 23 ft steam cutter 3 tons, 32 ft 5 3/4 tons; a 25 ft
# boat of the same family interpolates to ~3.3 tons hoisted.  Itemised below.
STEAM_WEIGHTS = {
    "hull_double_skin_kg": 560,
    "frames_and_structure_kg": 235,
    "deck_canopy_bulkheads_kg": 145,
    "boiler_full_of_water_kg": 760,
    "engine_and_shaft_kg": 430,
    "propeller_rudder_steering_kg": 85,
    "funnel_pipework_fittings_kg": 155,
    "coal_bunker_full_kg": 300,
    "seats_locker_joinery_kg": 105,
    "mooring_lifting_nav_gear_kg": 85,
    "fresh_water_tank_and_stores_kg": 320,
    "paint_varnish_kg": 32,
}
STEAM_WEIGHTS["light_kg"] = round(sum(STEAM_WEIGHTS.values()), 1)
STEAM_CREW = 4  # coxswain, engineer, two hands
STEAM_WEIGHTS["crew_kg"] = STEAM_CREW * 80
STEAM_WEIGHTS["loaded_kg"] = round(STEAM_WEIGHTS["light_kg"] + STEAM_WEIGHTS["crew_kg"], 1)


# --------------------------------------------------------------------------
# waterline reconciliation
# --------------------------------------------------------------------------
# The forms above were drawn as a naval architect draws a body plan.  Rather
# than assume where they float, the floating waterline is *solved* for the
# loaded condition and the whole form is then shifted so that this waterline
# lands exactly on Z = 0.  Z = 0 is therefore the true load waterline of the
# published design, and every interface dimension (davit heights, boarding
# heights, cradle points) is measured from a line the boat actually floats on.
def _reconcile(hull, weights):
    z_loaded = hydro.solve_waterline(hull, weights["loaded_kg"])
    hull.translate_z(-z_loaded)
    loaded = hydro.hydrostatics(hull, 0.0)
    light = hydro.hydrostatics(hull, hydro.solve_waterline(hull, weights["light_kg"]))
    return hull, loaded, light


ROW_CUTTER, ROW_LOADED_HYDRO, ROW_LIGHT_HYDRO = _reconcile(ROW_CUTTER, ROW_WEIGHTS)
STEM_CUTTER, STEAM_LOADED_HYDRO, STEAM_LIGHT_HYDRO = _reconcile(STEM_CUTTER, STEAM_WEIGHTS)


def _fmt_ft(m):
    ft = m / FOOT
    whole = int(ft)
    inch = (ft - whole) * 12
    return f"{whole} ft {inch:.1f} in ({m:.3f} m)"


def boats_spec():
    """The interface contract published to the ship agent."""
    return {
        "schema": "victoria.boats/1.0",
        "generated_by": "agent-02 ships boats",
        "ship": "SS Victoria (fictional, 1889) -- OPERATION VICTORIA",
        "units": {"model": "metres", "roblox_stud_m": 0.28, "stud_per_m": round(STUD_PER_M, 6)},
        "orientation": {
            "forward_axis": "+X (stem/stemhead direction)",
            "up_axis": "+Z",
            "port": "+Y",
            "origin": "on centreline, at mid-length of the length overall; Z=0 at the light load waterline drawn on the lines plan",
            "roblox_import": "export GLB with +Y up conversion; in Roblox the boat's LookVector must be set to the vessel's +X",
        },
        "boats": [
            {
                "id": "steam_cutter_1888",
                "name": "25 ft Steam Cutter (1888 pattern)",
                "type": "steam cutter / steam tender, open boat with engine & boiler canopy",
                "reference": "RMG NPC9572, 'Proposed 25ft Steam Cutter', Dangerfield Lith., 18 Jan 1888, scale 1:16",
                "dimensions": {
                    "loa_m": round(STEM_CUTTER.loa, 3),
                    "loa_ft": "25 ft 0 in",
                    "beam_max_m": round(STEM_CUTTER.bmax * 2, 3),
                    "beam_ft": "7 ft 0 in",
                    "depth_moulded_amidships_m": round(STEM_CUTTER.sheer_z(0.5) - STEM_CUTTER.keel_z(0.5), 3),
                    "draft_light_m": STEAM_LIGHT_HYDRO["draft_m"],
                    "draft_loaded_m": STEAM_LOADED_HYDRO["draft_m"],
                    "freeboard_light_m": STEAM_LIGHT_HYDRO["freeboard_amidships_m"],
                    "freeboard_loaded_m": STEAM_LOADED_HYDRO["freeboard_amidships_m"],
                    "sheer_height_bow_m": round(STEM_CUTTER.sheer_z(0.0), 3),
                    "sheer_height_stern_m": round(STEM_CUTTER.sheer_z(1.0), 3),
                },
                "weights": STEAM_WEIGHTS,
                "hydrostatics_loaded": STEAM_LOADED_HYDRO,
                "hydrostatics_light": STEAM_LIGHT_HYDRO,
                "davit_attachment_points": {
                    "note": "two single-arm davits, one pair; slings pass under the hull at the marked stations",
                    "fore_sling_x_m": 2.05,
                    "aft_sling_x_m": -1.55,
                    "sling_spread_m": 3.60,
                    "hook_height_above_sheer_m": 1.15,
                    "lifting_eyes": "forged galvanised eyebolts through the keelson at x=+2.05 and x=-1.55, 24 mm shank",
                    "max_sling_angle_deg": 12,
                },
                "cradle_contact_points": [
                    {"x_m": 1.60, "z_m": round(STEM_CUTTER.keel_z(0.29), 3), "half_breadth_m": 0.62},
                    {"x_m": -1.60, "z_m": round(STEM_CUTTER.keel_z(0.71), 3), "half_breadth_m": 0.66},
                ],
                "boarding": {
                    "boarding_point": "port side amidships, abreast the after thward",
                    "boarding_x_m": 0.35,
                    "boarding_height_above_waterline_m": round(STEM_CUTTER.sheer_z(0.45), 3),
                    "seat_capacity": 10,
                    "coxswain_position_x_m": -2.55,
                },
                "footprint_for_ship": {
                    "length_for_stowage_m": round(STEM_CUTTER.loa + 0.10, 3),
                    "width_for_stowage_m": round(STEM_CUTTER.bmax * 2 + 0.36, 3),
                    "height_above_sheer_m": 1.62,
                    "note": "height includes the canopy and funnel top; funnel may be lowered for stowage under a davit head",
                },
            },
            {
                "id": "rowing_cutter_25ft",
                "name": "25 ft Clinker Rowing Cutter (10-oared)",
                "type": "pulling/sailing cutter, lapstrake (clinker) construction",
                "reference": "RMG SLR1818 clinker cutter; RMG SLR0772 (1838, 1:24); RMG J0780 10-oared 25 ft cutter plan",
                "dimensions": {
                    "loa_m": round(ROW_CUTTER.loa, 3),
                    "loa_ft": "25 ft 0 in",
                    "loa_overall_with_rudder_m": 7.915,
                    "loa_note": "7.620 m is the hull (stem head to transom). The stern-hung plate rudder "
                                "shipped on the transom projects 0.30 m aft, giving 7.915 m overall; the "
                                "boat is stowed and hoisted with the rudder shipped, so the stowage "
                                "length below is the overall figure.",
                    "beam_max_m": round(ROW_CUTTER.bmax * 2, 3),
                    "beam_ft": "6 ft 3 in",
                    "depth_moulded_amidships_m": round(ROW_CUTTER.sheer_z(0.5) - ROW_CUTTER.keel_z(0.5), 3),
                    "draft_light_m": ROW_LIGHT_HYDRO["draft_m"],
                    "draft_loaded_m": ROW_LOADED_HYDRO["draft_m"],
                    "freeboard_light_m": ROW_LIGHT_HYDRO["freeboard_amidships_m"],
                    "freeboard_loaded_m": ROW_LOADED_HYDRO["freeboard_amidships_m"],
                    "sheer_height_bow_m": round(ROW_CUTTER.sheer_z(0.0), 3),
                    "sheer_height_stern_m": round(ROW_CUTTER.sheer_z(1.0), 3),
                },
                "weights": ROW_WEIGHTS,
                "hydrostatics_loaded": ROW_LOADED_HYDRO,
                "hydrostatics_light": ROW_LIGHT_HYDRO,
                "davit_attachment_points": {
                    "note": "single pair of davits; the boat is hoisted by two slings under the hull",
                    "fore_sling_x_m": 1.95,
                    "aft_sling_x_m": -1.60,
                    "sling_spread_m": 3.55,
                    "hook_height_above_sheer_m": 1.10,
                    "lifting_eyes": "galvanised eyebolts through keelson at x=+1.95 / x=-1.60 (as on SLR1818, which shows large eyes fore and aft on the keelson for hoisting to davits)",
                },
                "cradle_contact_points": [
                    {"x_m": 1.55, "z_m": round(ROW_CUTTER.keel_z(0.30), 3), "half_breadth_m": 0.55},
                    {"x_m": -1.55, "z_m": round(ROW_CUTTER.keel_z(0.70), 3), "half_breadth_m": 0.58},
                ],
                "boarding": {
                    "boarding_point": "port side at the after thwart; boat hooks and fenders both sides",
                    "boarding_x_m": 0.55,
                    "boarding_height_above_waterline_m": round(ROW_CUTTER.sheer_z(0.43), 3),
                    "seat_capacity": 11,
                    "rowers": 10,
                    "coxswain_position_x_m": -2.30,
                },
                "footprint_for_ship": {
                    "length_for_stowage_m": round(ROW_CUTTER.loa + 0.40, 3),
                    "width_for_stowage_m": round(ROW_CUTTER.bmax * 2 + 0.30, 3),
                    "width_note": "boats are stowed with the 3.66 m oars laid inboard along the thwarts (the davit condition); with oars out in the rowlocks the boat needs beam + 4.2 m of clear water either side, so rowing is only possible after lowering",
                    "height_above_sheer_m": 0.42,
                },
            },
        ],
    }

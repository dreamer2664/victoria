"""
specs2.py -- THEMISTOCLES-II single source of truth: hull forms, weights,
hydrostatic reconciliation.  Principal dimensions are the documented figures
from HISTORICAL_EVIDENCE.md (unchanged); sectional fullness (k values) was
re-calibrated this generation so the solved draughts match the documented
draughts (0.397 m rowing cutter loaded at 1897 kg, 0.432 m whaler type at
1487.5 kg plate up, ~0.53 m steam cutter loaded at 3532 kg).
"""
from __future__ import annotations
import math
import numpy as np
from .hull2 import Hull2

FOOT = 0.3048
INCH = 0.0254
STUD_PER_M = 1.0 / 0.28


# ---------------------------------------------------------------------------
# hull definitions
# ---------------------------------------------------------------------------

def rowing_cutter_hull() -> Hull2:
    h = Hull2(
        "rowing_cutter_25ft",
        loa=25 * FOOT,
        beam=6 * FOOT + 3 * INCH,
        sheer_pts=[(0.0, 0.720), (0.09, 0.640), (0.24, 0.565), (0.45, 0.518),
                   (0.66, 0.505), (0.83, 0.528), (0.93, 0.562), (1.0, 0.600)],
        keel_pts=[(0.0, -0.200), (0.10, -0.400), (0.20, -0.492), (0.35, -0.540),
                  (0.52, -0.552), (0.68, -0.535), (0.80, -0.490), (0.90, -0.400),
                  (1.0, -0.290)],
        hb_pts=[(0.0, 0.030), (0.10, 0.460), (0.25, 0.780), (0.40, 0.940),
                (0.55, 1.000), (0.70, 0.960), (0.85, 0.820), (0.95, 0.620),
                (1.0, 0.430)],
        k_fwd=1.15, k_mid=0.32, k_aft=1.05,
        flare_fwd=0.09, flare_aft=0.02,
        stem_rake=0.09, transom=True, transom_rake=0.16,
    )
    return h


def whaler_hull() -> Hull2:
    h = Hull2(
        "whaler_27ft",
        loa=27 * FOOT,
        beam=6 * FOOT,
        sheer_pts=[(0.0, 0.700), (0.09, 0.648), (0.22, 0.610), (0.40, 0.588),
                   (0.58, 0.588), (0.76, 0.606), (0.90, 0.636), (1.0, 0.688)],
        keel_pts=[(0.0, -0.300), (0.07, -0.386), (0.20, -0.428), (0.42, -0.444),
                  (0.60, -0.442), (0.78, -0.424), (0.90, -0.380), (1.0, -0.290)],
        hb_pts=[(0.0, 0.028), (0.06, 0.270), (0.16, 0.545), (0.30, 0.780),
                (0.42, 0.880), (0.52, 0.9145), (0.62, 0.880), (0.76, 0.775),
                (0.88, 0.560), (0.96, 0.285), (1.0, 0.028)],
        k_fwd=1.25, k_mid=0.30, k_aft=1.25,
        flare_fwd=0.05, flare_aft=0.05,
        stem_rake=0.10, transom=False, stern_rake=0.12,
    )
    return h


def steam_cutter_hull() -> Hull2:
    h = Hull2(
        "steam_cutter_1888",
        loa=25 * FOOT,
        beam=7 * FOOT,
        sheer_pts=[(0.0, 0.775), (0.10, 0.690), (0.26, 0.600), (0.48, 0.540),
                   (0.68, 0.530), (0.84, 0.560), (0.94, 0.600), (1.0, 0.640)],
        keel_pts=[(0.0, -0.300), (0.10, -0.520), (0.22, -0.610), (0.36, -0.655),
                  (0.54, -0.665), (0.70, -0.645), (0.82, -0.570), (0.92, -0.430),
                  (1.0, -0.240)],
        hb_pts=[(0.0, 0.055), (0.09, 0.500), (0.22, 0.820), (0.40, 0.970),
                (0.58, 1.000), (0.75, 0.985), (0.88, 0.900), (1.0, 0.600)],
        k_fwd=1.00, k_mid=0.28, k_aft=0.85,
        flare_fwd=0.10, flare_aft=0.03,
        stem_rake=0.11, transom=True, transom_rake=0.20,
    )
    return h


ROW_WEIGHTS = {
    "hull_planking_11_strakes_kg": 470, "keel_stem_sternpost_transom_kg": 105,
    "gunwales_inwales_knees_kg": 78, "thwarts_benches_floorboards_kg": 96,
    "oars_10_kg": 10 * 17.5, "rig_spars_sails_kg": 95, "rudder_tiller_kg": 26,
    "fittings_mooring_rowlocks_kg": 38, "paint_varnish_kg": 29,
}
ROW_WEIGHTS["light_kg"] = round(sum(ROW_WEIGHTS.values()), 1)
ROW_CREW_KG = 11 * 80      # 10 rowers + coxswain
ROW_WEIGHTS["crew_kg"] = ROW_CREW_KG
ROW_WEIGHTS["loaded_kg"] = round(ROW_WEIGHTS["light_kg"] + ROW_CREW_KG, 1)

WHALER_WEIGHTS = {
    "hull_planking_9_strakes_kg": 395, "keel_stems_aprons_kg": 105,
    "gunwales_inwales_knees_kg": 78, "thwarts_bench_floorboards_kg": 84,
    "oars_5_kg": 5 * 19.5, "masts_yards_rigging_sails_kg": 122,
    "centreboard_case_plate_kg": 44, "rudder_tiller_yoke_kg": 20,
    "fittings_mooring_kg": 36, "paint_varnish_kg": 26,
}
WHALER_WEIGHTS["light_kg"] = round(sum(WHALER_WEIGHTS.values()), 1)
WHALER_WEIGHTS["crew_kg"] = 6 * 80
WHALER_WEIGHTS["loaded_kg"] = round(WHALER_WEIGHTS["light_kg"] + 6 * 80, 1)

STEAM_WEIGHTS = {
    "hull_double_skin_kg": 560, "frames_and_structure_kg": 235,
    "deck_canopy_bulkheads_kg": 145, "boiler_full_of_water_kg": 760,
    "engine_and_shaft_kg": 430, "propeller_rudder_steering_kg": 85,
    "funnel_pipework_fittings_kg": 155, "coal_bunker_full_kg": 300,
    "seats_locker_joinery_kg": 105, "mooring_lifting_nav_gear_kg": 85,
    "fresh_water_tank_and_stores_kg": 320, "paint_varnish_kg": 32,
}
STEAM_WEIGHTS["light_kg"] = round(sum(STEAM_WEIGHTS.values()), 1)
STEAM_WEIGHTS["crew_kg"] = 4 * 80
STEAM_WEIGHTS["loaded_kg"] = round(STEAM_WEIGHTS["light_kg"] + 4 * 80, 1)


def reconcile(hull: Hull2, weights: dict):
    """Translate the design so Z=0 IS the loaded waterline; return hydrodicts."""
    z_l, m_l, lcb = hull.solve_draught(weights["loaded_kg"])
    shift = -z_l
    hull.sheer = hull.sheer.__class__(hull.sheer.x, hull.sheer.y - shift)
    hull.keel = hull.keel.__class__(hull.keel.x, hull.keel.y - shift)
    z0, m0, lcb0 = hull.solve_draught(weights["light_kg"])
    loaded = {"draft_m": round(float(-min(hull.keel.y)), 3),
              "lcb_m": round(float(lcb), 3),
              "freeboard_amidships_m": round(float(hull.sheer(0.5)), 3),
              "displacement_kg": round(float(m_l), 1)}
    light = {"draft_m": round(float(z0 - min(hull.keel.y)), 3),
             "waterline_z": round(float(z0), 3),
             "lcb_m": round(float(lcb0), 3),
             "freeboard_amidships_m": round(float(hull.sheer(0.5) - z0), 3),
             "displacement_kg": round(float(m0), 1)}
    return hull, loaded, light

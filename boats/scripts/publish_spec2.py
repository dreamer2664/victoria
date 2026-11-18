#!/usr/bin/env python3
"""
publish_spec2.py -- regenerate interfaces/boats_spec.json (THEMISTOCLES-II)
from the export metadata of the three built boats.  Run after export2.py.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))

DIRS = {"rowing_cutter_25ft": "rowing2", "whaler_27ft": "whaler2",
        "steam_cutter_1888": "steam2"}
PRINCIPAL = {
    "rowing_cutter_25ft": dict(loa=7.620, loa_ft="25 ft 0 in", beam=1.905,
                               beam_ft="6 ft 3 in", depth=1.065,
                               type="clinker rowing cutter, 10-oared double-banked",
                               sheer_fwd=0.73, sheer_aft=0.60),
    "whaler_27ft": dict(loa=8.230, loa_ft="27 ft 0 in", beam=1.829,
                        beam_ft="6 ft 0 in", depth=1.032,
                        type="double-ended clinker whaler, 5-oared single-banked",
                        sheer_fwd=0.70, sheer_aft=0.69),
    "steam_cutter_1888": dict(loa=7.620, loa_ft="25 ft 0 in", beam=2.134,
                              beam_ft="7 ft 0 in", depth=1.203,
                              type="steam cutter / steam tender (1888 pattern)",
                              sheer_fwd=0.775, sheer_aft=0.64),
}
DAVIT = {"rowing_cutter_25ft": [1.95, -1.60], "whaler_27ft": [1.85, -1.72],
         "steam_cutter_1888": [2.10, -1.85]}
BOARDING = {"rowing_cutter_25ft": (0.55, 0.52), "whaler_27ft": (0.70, 0.45),
            "steam_cutter_1888": (0.35, 0.60)}
ALIAS = {"cutter_steam_25": "steam_cutter_1888",
         "cutter_rowing_25": "rowing_cutter_25ft", "whaler_27": "whaler_27ft"}


def main():
    boats = []
    for cls, d in DIRS.items():
        meta = json.load(open(os.path.join(REPO, "boats", "exports", d,
                                           cls + "_export_meta.json")))
        pr = PRINCIPAL[cls]
        hy = meta["hydrostatics"]
        wk = meta["weights_kg"]
        boats.append({
            "id": cls,
            "name": pr["loa_ft"] + " " + pr["type"].split()[0].title() + " boat (THEMISTOCLES-II)",
            "type": pr["type"],
            "dimensions": {
                "loa_m": pr["loa"], "loa_ft": pr["loa_ft"],
                "beam_max_m": pr["beam"], "beam_ft": pr["beam_ft"],
                "depth_moulded_amidships_m": pr["depth"],
                "draft_light_m": hy["light"]["draft_m"],
                "draft_loaded_m": hy["loaded"]["draft_m"],
                "freeboard_light_m": hy["light"]["freeboard_amidships_m"],
                "freeboard_loaded_m": hy["loaded"]["freeboard_amidships_m"],
                "sheer_height_bow_m": pr["sheer_fwd"],
                "sheer_height_stern_m": pr["sheer_aft"],
            },
            "weights": wk,
            "hydrostatics_loaded": {
                "waterline_z_m": 0.0,
                "draft_m": hy["loaded"]["draft_m"],
                "displacement_kg": hy["loaded"]["displacement_kg"],
                "lcb_m_fwd_of_midships": hy["loaded"]["lcb_m"],
            },
            "hydrostatics_light": {
                "waterline_z_m": hy["light"]["waterline_z"],
                "draft_m": hy["light"]["draft_m"],
                "displacement_kg": hy["light"]["displacement_kg"],
                "lcb_m_fwd_of_midships": hy["light"]["lcb_m"],
            },
            "davit_slings_x_m": DAVIT[cls],
            "boarding_m": {"x": BOARDING[cls][0], "z": BOARDING[cls][1]},
            "moving_parts": list(meta["pivots"].keys()),
            "export": {"dir": f"boats/exports/{d}/",
                       "combined_glb": f"{cls}.glb",
                       "combined_fbx": f"{cls}.fbx"},
        })
    spec = {
        "schema": "victoria.boats/2.0",
        "generated_by": "THEMISTOCLES-II (boats division, second generation)",
        "ship": "SS Victoria (fictional, 1889) -- OPERATION VICTORIA",
        "units": {"model": "metres", "roblox_stud_m": 0.28, "stud_per_m": 3.571429},
        "orientation": {
            "forward_axis": "+X (stem direction)",
            "up_axis": "+Z",
            "port": "+Y",
            "origin": "centreline at mid-LOA; Z=0 at the LOADED waterline (changed from gen 1)",
            "roblox_import": "GLB with +Y up; set LookVector to vessel +X",
        },
        "integration": {
            "craft_id_aliases": ALIAS,
            "craft_type_enum": ["steam_cutter", "rowing_cutter", "whaler"],
            "davit_rating_required_kg": {
                b["id"]: int(b["hydrostatics_loaded"]["displacement_kg"] * 1.05) + 0
                for b in boats},
            "davit_limit_conflict": (
                "The liner's davit limit is published as 2000 kg. These boats are "
                "weighed, not guessed: solved displacements are "
                + ", ".join(f"{b['id']} light {b['weights']['light_kg']:.0f} kg / "
                            f"loaded {b['hydrostatics_loaded']['displacement_kg']:.0f} kg"
                            for b in boats)
                + ". A 2000 kg davit cannot hoist the steam cutter (3532 kg loaded); "
                  "rate the davits to davit_rating_required_kg or carry the rowing "
                  "cutter (1112 kg light)."),
            "export_contract": {
                "units": "metres in GLB and FBX; Roblox importer multiplies by 3.571429",
                "per_part_triangle_limit": 19000, "uv_layers": 1,
                "parts": "one file per logical part; moving parts keep origin at pivot",
                "origin_of_moving_parts": ("rowlock for oars; shaft hub for the screw; "
                                           "pintle line for the rudder"),
            },
        },
        "boats": boats,
    }
    out = os.path.join(REPO, "interfaces", "boats_spec.json")
    with open(out, "w") as f:
        json.dump(spec, f, indent=2)
    print("WROTE", out)


if __name__ == "__main__":
    main()

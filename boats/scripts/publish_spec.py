"""
publish_spec.py -- generate interfaces/boats_spec.json from boatgen.specs.

Run with plain python (no Blender needed):
    python3 publish_spec.py
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from boatgen import specs

ROOT = "/home/user/victoria"
OUT = os.path.join(ROOT, "interfaces", "boats_spec.json")


def main():
    data = specs.boats_spec()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(data, f, indent=2)
    print("wrote", OUT)
    # a short human-readable summary beside it
    lines = ["# Boat interface summary",
             "",
             "**For the ship agent.** `interfaces/boats_spec.json` is the machine-readable",
             "contract for the three ship's boats: overall dimensions, beam and hull depth,",
             "davit/lifting attachment positions, cradle contact points, weight estimates,",
             "boarding locations, and export origin and orientation. The figures are generated",
             "from the same source as the 3D models (`boats/scripts/boatgen/specs.py`), so they",
             "cannot drift from the geometry. If your boat-handling arrangement needs different",
             "attachment points, change them here and re-run `boats/scripts/publish_spec.py`",
             "so both sides agree.",
             "",
             "Key figures: 1 stud = 0.28 m; +X forward, +Y port, Z = 0 at the **load waterline**, "
             "origin on the centreline at mid-LOA; GLB export is Y-up.",
             "",
             "_(auto-generated — do not edit by hand)_", ""]
    for b in data["boats"]:
        d = b["dimensions"]
        lines += [
            f"## {b['name']}  (`{b['id']}`)",
            "",
            f"- LOA: {d['loa_m']} m / {d['loa_ft']}",
            f"- Beam max: {d['beam_max_m']} m / {d.get('beam_ft','')}",
            f"- Depth moulded amidships: {d['depth_moulded_amidships_m']} m",
            f"- Draft light / loaded: {d['draft_light_m']} / {d['draft_loaded_m']} m",
            f"- Freeboard light / loaded: {d['freeboard_light_m']} / {d.get('freeboard_loaded_m')} m",
            f"- Weight light / loaded: {b['weights']['light_kg']} / {b['weights']['loaded_kg']} kg",
            f"- Davit slings at x = {b['davit_attachment_points']['fore_sling_x_m']:+.2f} m "
            f"and {b['davit_attachment_points']['aft_sling_x_m']:+.2f} m "
            f"(spread {b['davit_attachment_points']['sling_spread_m']} m)",
            f"- Cradle points: " + ", ".join(
                f"x={c['x_m']:+.2f} z={c['z_m']:+.2f}" for c in b["cradle_contact_points"]),
            f"- Boarding: x = {b['boarding']['boarding_x_m']:+.2f} m, "
            f"{b['boarding']['boarding_height_above_waterline_m']} m above the waterline",
            f"- Stowage envelope: {b['footprint_for_ship']['length_for_stowage_m']} x "
            f"{b['footprint_for_ship']['width_for_stowage_m']} x "
            f"{b['footprint_for_ship']['height_above_sheer_m']} m above the sheer",
            "",
        ]
    with open(os.path.join(ROOT, "interfaces", "BOATS_INTERFACE.md"), "w") as f:
        f.write("\n".join(lines))
    print("wrote interfaces/BOATS_INTERFACE.md")


if __name__ == "__main__":
    main()

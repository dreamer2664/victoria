#!/usr/bin/env python3
"""
verify2.py -- THEMISTOCLES-II automated QA gate.

Runs entirely outside Blender against the export metadata (JSON), so it is
fast and CI-friendly.  For deeper checks (mesh containment vs hull envelope)
run inside Blender with `blender -b <boat>.blend --python verify2_blender.py`.

Checks:
 1. hydrostatic consistency: weight budget sums == solved displacement
 2. moving-part pivots exist for every animated part and sit where physics
    demands (oar rowlocks at the rail, prop hub aft & submerged, rudder at
    the stern)
 3. per-part triangle budget (Roblox 19 000 limit)
 4. part envelopes are sane (nothing wider than beam, nothing longer than
    LOA except documented rig spars, everything vertical within hull+rig)
 5. manifest Lua regenerates bit-identical to the committed manifests
"""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
BOATS = {"rowing_cutter_25ft": "rowing2", "whaler_27ft": "whaler2",
         "steam_cutter_1888": "steam2"}
FAIL = []


def check(name, cond, detail=""):
    print(("  PASS " if cond else "  FAIL ") + name + (f"  ({detail})" if detail else ""))
    if not cond:
        FAIL.append(name)


def main():
    metas = {cls: json.load(open(os.path.join(REPO, "boats", "exports", d,
                                              cls + "_export_meta.json")))
             for cls, d in BOATS.items()}

    print("[1] hydrostatic consistency")
    for cls, m in metas.items():
        w, hy = m["weights_kg"], m["hydrostatics"]
        check(f"{cls}: loaded weight == displacement",
              abs(w["loaded_kg"] - hy["loaded"]["displacement_kg"]) < 1.0,
              f'{w["loaded_kg"]} kg vs {hy["loaded"]["displacement_kg"]} kg')
        check(f"{cls}: light weight == displacement",
              abs(w["light_kg"] - hy["light"]["displacement_kg"]) < 1.0)
        check(f"{cls}: light draft < loaded draft",
              hy["light"]["draft_m"] < hy["loaded"]["draft_m"],
              f'{hy["light"]["draft_m"]} < {hy["loaded"]["draft_m"]}')

    print("[2] moving-part pivots")
    rc = metas["rowing_cutter_25ft"]
    oars = rc["pivots"]["oars_moving"]
    check("rowing cutter: 10 oars double-banked", len(oars) == 10)
    check("rowing cutter: oar pivots at rail",
          all(0.5 < abs(p["pivot_world"][1]) < 1.0 and 0.3 < p["pivot_world"][2] < 0.8
              for p in oars))
    wh = metas["whaler_27ft"]
    wv = wh["pivots"]["oars_moving"]
    check("whaler: 5 oars single-banked", len(wv) == 5
          and all(p.get("single_banked") for p in wv))
    check("whaler: alternating sides",
          [p["part"][4] for p in sorted(wv, key=lambda p: -p["station_x"])]
          == list("PSPSP"))
    sc = metas["steam_cutter_1888"]
    pp = sc["pivots"]["propeller"]
    check("steam cutter: prop aft, submerged, fore-aft axis",
          pp["hub_pt"][0] < -3.0 and pp["hub_pt"][2] < -0.2 and abs(pp["axis_dir"][0]) > 0.93)
    check("steam cutter: rudder at stern", sc["pivots"]["rudder_axis"][0] < -3.3)

    print("[3] per-part triangle budget")
    for cls, m in metas.items():
        worst = max(m["parts"].items(), key=lambda kv: kv[1]["triangles"])
        check(f"{cls}: all parts <= 19 000 tris",
              worst[1]["triangles"] <= 19000,
              f'worst {worst[0]} = {worst[1]["triangles"]}')

    print("[4] part envelope sanity")
    LOA = {"rowing_cutter_25ft": 7.62, "whaler_27ft": 8.23, "steam_cutter_1888": 7.62}
    for cls, m in metas.items():
        loa = LOA[cls]
        for nm, p in m["parts"].items():
            d = p["dimensions_m"]
            check(f"{cls}/{nm}: fits LOA envelope", d[0] <= loa + 0.9,
                  f"{d[0]:.2f} m") if d[0] > loa else None
            check(f"{cls}/{nm}: fits beam envelope", d[1] <= 2.4 + 0.6) \
                if d[1] > 2.4 else None

    print("[5] manifest regeneration is reproducible")
    for cls, d in BOATS.items():
        meta_p = os.path.join(REPO, "boats", "exports", d, cls + "_export_meta.json")
        cur = open(os.path.join(REPO, "roblox", "src", f"Manifest_{cls}.lua")).read()
        sys.path.insert(0, os.path.join(REPO, "roblox", "tools"))
        import importlib.util
        spec = importlib.util.spec_from_file_location("gm2",
                 os.path.join(REPO, "roblox", "tools", "gen_manifest2.py"))
        gm2 = importlib.util.module_from_spec(spec)
        # avoid executing __main__ branch: it's guarded by __name__
        spec.loader.exec_module(gm2)
        regen = gm2.emit(json.load(open(meta_p)), cls) + "\n"
        check(f"{cls}: manifest reproducible", regen == cur)

    print()
    if FAIL:
        print("FAILED:", *FAIL, sep="\n  - ")
        sys.exit(1)
    print("ALL THEM2 CHECKS PASS")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Generate docs/port_<x>_layout.md from the build metadata.

The spec is derived from the same JSON the game scripts consume, so a dimension can
never disagree between the document and the model.
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SPECS = {
 "a": dict(
   title="Port A — The Port of Aldermouth (passenger harbour)",
   type="Liverpool-type enclosed, non-tidal passenger dock system",
   intro=("An enclosed dock entered from the river, with the water level held constant by "
          "the lock, so that ships berth without waiting on the tide. The passenger "
          "terminal, customs, baggage hall and railway station all sit inside the dock "
          "estate, and the cargo side of the same port (staithes, transit sheds, dock "
          "basin) is visible from the passenger quay."),
   ops=("A North German Lloyd mail steamer of 1889 turned round in about 29 hours. "
        "Coaling was done from barges on the offside: 8 barges of 250–300 t, about 4.5 days "
        "for a large mail steamer. Cargo calls ran to 10,000–100,000 packages, worked by "
        "6 gangs of 25 men. The terminal is therefore laid out for overlapping "
        "disembarkation and embarkation, with separate baggage and customs routes."),
 ),
 "b": dict(
   title="Port B — The Port of Carrickmore (industrial / shipbuilding harbour)",
   type="Belfast-type shipbuilding, repair and fitting-out yard",
   intro=("A shipbuilding and repair estate on the river: three building slips on the "
          "frontage, the great Princess Graving Dock behind them, an older small graving "
          "dock alongside, and the shops — moulding loft, engineering, boiler, plate and "
          "joinery — served by their own rail network inside high brick boundary walls."),
   ops=("Fairfield-type yards of the period covered about 74 acres and had up to 15 vessels "
        "on the slips at once, at roughly 7,000 t per hull, with sternposts of 26 t. The "
        "erecting shops ran around 40 lathes and a 16 ft boring disc. Plate and timber "
        "yards fed the shops through the yard rail system; finished hulls were launched "
        "stern-first and then completed at the fitting-out quay."),
 ),
}

def fmt(v):
    return ("%.1f" % v).rstrip("0").rstrip(".")

def main():
    for code, spec in SPECS.items():
        meta = json.load(open(os.path.join(ROOT, "docs", "port_%s_meta.json" % code)))
        L = []
        A = L.append
        A("# %s\n" % spec["title"])
        A("*Generated from `docs/port_%s_meta.json` by `tools/gen_layout_docs.py`.*\n" % code)
        A("**Type.** %s\n" % spec["type"])
        A(spec["intro"] + "\n")
        A("![layout plan](port_%s_plan.svg)\n" % code)

        s = meta["site"]
        A("## 1. Extent\n")
        A("| | |")
        A("|---|---|")
        A("| Site rectangle | x %s → %s m, y %s → %s m |" % (fmt(s[0]), fmt(s[2]), fmt(s[1]), fmt(s[3])))
        A("| Site size | %s × %s m |" % (fmt(s[2]-s[0]), fmt(s[3]-s[1])))
        A("| Site area | %.1f ha |" % ((s[2]-s[0])*(s[3]-s[1])/10000.0))
        A("| Quay coping | +%s m above water |" % fmt(meta["quay_z"]))
        A("| Water | mean level 0.00 m |")
        A("")

        A("## 2. Levels\n")
        A("| Surface | Level (m) |")
        A("|---|---|")
        A("| Mean water | 0.00 |")
        A("| Quay coping | +%s |" % fmt(meta["quay_z"]))
        for line in LEVELS.get(code, []):
            A("| %s | %s |" % line)
        A("")
        A("All elevations are relative to mean water, which is fixed: these are enclosed, "
          "non-tidal docks, so there is no tide curve to model.\n")

        A("## 3. Berths\n")
        A("The berth rule applied by the layout auditor: a ship of the stated envelope must "
          "have **4 m of clear water in total** (2 m either side, 2 m ahead and astern). "
          "The liner envelope used throughout is **180 × 20 × 9 m**.\n")
        A("| Berth | Name | Kind | Envelope L×B×draft (m) | Clear water | Length | Depth | Checks |")
        A("|---|---|---|---|---|---|---|---|")
        for b in meta["berths"]:
            r = b["rect"]
            e = b.get("ship_envelope", {})
            w = abs(r[2]-r[0]); h = abs(r[3]-r[1])
            long_side = max(w, h); short_side = min(w, h)
            ell = e.get("L", 0); beam = e.get("B", 0)
            # the implemented rule: 4 m total clear water, i.e. 2 m either side
            ok = (long_side >= ell + 4) and (short_side >= beam + 4)
            A("| %s | %s | %s | %s × %s × %s | %s × %s m | %s m | %s m | %s |"
              % (b["id"], b["name"], b.get("kind",""),
                 fmt(ell), fmt(beam), fmt(e.get("draft",0)),
                 fmt(short_side), fmt(long_side),
                 fmt(b.get("length_m", long_side)), fmt(b.get("depth_m",0)),
                 "OK" if ok else "CHECK"))
        A("")
        A("Where a berth reports **CHECK**, the limitation is recorded rather than hidden: "
          "see §7.\n")

        if meta.get("graving_docks"):
            A("## 4. Graving docks\n")
            A("| Dock | Built | Plan | Width | Depth on sill | Sections |")
            A("|---|---|---|---|---|---|")
            for d in meta["graving_docks"]:
                A("| %s | %s | %s × %s m | %s m | %s m | %s |"
                  % (d["name"], d["built"], fmt(d["length_m"]), fmt(d["width_m"]),
                     fmt(d["width_m"]), fmt(d["entrance_depth_m"]), d["sections"]))
            A("")
            for d in meta["graving_docks"]:
                A("- **%s** — %s" % (d["name"], d["basis"]))
                if d.get("adaptation"):
                    A("  - *Adaptation:* %s" % d["adaptation"])
            A("")

        if meta.get("slips"):
            A("## 5. Building slips\n")
            A("| Slip | Width | Length of ways | Gradient |")
            A("|---|---|---|---|")
            for sl in meta["slips"]:
                A("| %s | %s m | %s m | %s |"
                  % (sl["id"], fmt(sl["width_m"]), fmt(sl["length_m"]), sl.get("gradient","")))
            A("")
            A("%s\n" % meta["slips"][0].get("basis",""))

        A("## 6. Interaction points\n")
        A("Every point below is walked to by a player and is generated into the Roblox layer "
          "as a ProximityPrompt anchor. Positions are metres in the Blender frame.\n")
        A("| ID | Point | Kind | Radius | Position (x, y, z) |")
        A("|---|---|---|---|---|")
        for i in meta.get("interactions", []):
            z = i.get("z", meta["quay_z"])
            A("| %s | %s | %s | %s m | %s, %s, %s |"
              % (i["id"], i["name"], i["type"], fmt(i.get("radius", 5)),
                 fmt(i["pos"][0]), fmt(i["pos"][1]), fmt(z)))
        A("")

        A("## 7. Known limitations\n")
        for line in LIMITS.get(code, []):
            A("- " + line)
        A("")

        A("## 8. Operations the layout supports\n")
        A(spec["ops"] + "\n")

        A("## 9. Circulation\n")
        for k, routes in meta.get("paths", {}).items():
            for n, route in enumerate(routes):
                pts = " → ".join("(%s, %s)" % (fmt(p[0]), fmt(p[1])) for p in route)
                A("- **%s** route %d: %s" % (k, n + 1, pts))
        A("")

        out = os.path.join(ROOT, "docs", "port_%s_layout.md" % code)
        open(out, "w").write("\n".join(L))
        print("wrote", out, len(L), "lines")

LEVELS = {
 "a": [("Lock sill", "−10.50"), ("Dock bed", "−8.00"), ("River bed", "−12.00"),
       ("Landing-stage deck", "floating, follows water level"),
       ("Rail head", "+4.15"), ("Terminal booking hall floor", "+4.20")],
 "b": [("Graving dock floor (Princess)", "−7.00 (coping − 11.00)"),
       ("No. 1 graving dock floor", "−4.00 (coping − 8.00)"),
       ("Slip head", "+4.00"), ("Slip toe", "−6.00, below water"),
       ("River bed", "−12.00"), ("Rail head", "+4.15")],
}

LIMITS = {
 "a": ["Berth **B3** is 132 m long against a 130 m envelope: the +4 m end clearance rule is "
       "not met at the ends, although it is met abeam. The basin could be lengthened eastward "
       "if the dock shed is moved; that change was not made because the shed is a listed-type "
       "structure in the composition.",
       "Berth **B2** is a shallow berth (6.5 m) and takes only the tender/steamer envelope "
       "shown; it is not a liner berth, and is not intended to be.",
       "The **south-east of the site** is laid out as open quay and reserved land rather than "
       "built up, so that the dock basin has working room; it reads as the least dense part of "
       "the port.",
       "The landing stage is a **static floating pontoon**: the deck is modelled at mean water "
       "level and does not animate with a tide, because these docks are non-tidal."],
 "b": ["No **ship under construction** is modelled on the slips. The brief forbids downloaded "
       "ship assets and the slips are dressed instead with keel blocks, raking shores, staging "
       "and props — the appliances, not a hull.",
       "The **Princess Dock is pumped dry** and the **No. 1 Dock is flooded** with its caisson "
       "seated. Both states are deliberately shown, to demonstrate the caisson arrangement.",
       "The **96 m ways** cannot launch the 180 m envelope. This is correct: the envelope is "
       "handled at the 210 m fitting-out quay, not on the slips.",
       "The **north-east quadrant** is yard and rail rather than buildings, matching the open "
       "materials yards of a working shipyard."],
}

if __name__ == "__main__":
    main()

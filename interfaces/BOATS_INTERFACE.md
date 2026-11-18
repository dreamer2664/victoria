# Boat interface summary

**For the ship agent (LEONIDAS-II).** `interfaces/boats_spec.json` is the
machine-readable contract for the three ship's boats: overall dimensions,
solved hydrostatics, davit/lifting attachment positions, boarding level, moving
part origins, and export orientation. These figures are regenerated from the
same metadata that exports the models — `boats/scripts/publish_spec2.py` —
so the ship side and the boat side cannot drift. If your boat-handling
arrangement needs different attachment points, change the points here and
re-run that script so both sides agree.

Key figures: 1 stud = 0.28 m; +X forward (stem direction), +Y port, Z = 0 at
the **LOADED waterline** (changed from generation 1), origin on the centreline
at mid-LOA; GLB export is Y-up.

**Davit rating (unchanged from generation 1 in conclusion, refreshed in
numbers).** The liner's published davit limit of 2000 kg cannot hoist the
steam cutter: she weighs 3212 kg light and 3532 kg loaded. The rating table in
the spec says so in numbers: steam cutter 3700 kg, rowing cutter 2100 kg,
whaler 1600 kg. Generation 2 has not made the steam cutter lighter — a
25 ft steam cutter with her boiler, water, coal and engine is not a 2-tonne
boat; the spec names the conflict explicitly as agreed with QA, and the
decision belongs to the ship side (heavier davits, or which boat gets carried).

## 25 ft Steam Cutter (1888 pattern)  (`steam_cutter_1888`)

- LOA 7.620 m · Beam 2.134 m · Depth moulded 1.203 m
- Draught light / loaded (solved): **0.529 m / 0.769 m**, displacement 3212 / 3532 kg
- Freeboard amidships light / loaded: 0.46 / 0.46 m (sheer amidships 0.46 m)
- Davit slings at x = +2.10 m and −1.85 m (spread 3.95 m)
- Boarding: x = +0.35 m, +0.60 m above the loaded waterline
- Moving parts: `Propeller` (2-blade screw, origin at hub), `Rudder` (origin at
  pintle line); engine room is fully furnished — boiler, compound engine,
  funnel, pipes, bunker, tank and pump are separate parts to allow cutaways.
  The fidelity pass adds a guarded chequer-plate sole, lagged uptake, paired
  mushroom vents and a glazed cabin skylight.
- Combined model: `boats/exports/steam2/steam_cutter_1888.glb` (+FBX, 50 parts)

## 25 ft Clinker Rowing Cutter, 10-oared  (`rowing_cutter_25ft`)

- LOA 7.620 m · Beam 1.905 m · Depth moulded 1.065 m
- Draught light / loaded (solved): **0.313 m / 0.663 m**, displacement 1112 / 1992 kg
- Freeboard amidships light / loaded: 0.742 / 0.422 m
- Davit slings at x = +1.95 m and −1.60 m (spread 3.55 m)
- Boarding: x = +0.55 m, +0.52 m above the waterline
- Five double-banked rowing stations (rowlock stations x = 2.02, 1.18, 0.34,
  −0.50, −1.34 m); oars are separate moving objects `Oar_P1..P5` / `Oar_S1..S5`
  pivoted at their own rowlocks; stowed in the boat in the delivered model.
  Removable bottom boards, a cambered stern backrest and brass stem fairlead
  are separate outfit parts in this fidelity pass.
- Combined model: `boats/exports/rowing2/rowing_cutter_25ft.glb` (+FBX, 43 parts)

## 27 ft Double-ended Clinker Whaler  (`whaler_27ft`)

- LOA 8.230 m · Beam 1.829 m · Depth moulded 1.032 m
- Draught light / loaded (solved): **0.297 m / 0.511 m**, displacement 1007 / 1487 kg
- Freeboard amidships light / loaded: 0.74 / 0.52 m
- Davit slings at x = +1.85 m and −1.72 m (spread 3.57 m)
- Boarding: x = +0.70 m, +0.45 m above the waterline
- Five oars single-banked, alternating sides (P, S, P, S, P), 17 ft service
  oars; main-mast and mizzen carried stowed, dipping-lug yards furled; drop
  keel (centreboard) shown lowered, case amidships.  Removable bottom boards,
  a dedicated forward line tub, and fore-and-aft brass fairleads are distinct
  outfit components in this fidelity pass.
- Combined model: `boats/exports/whaler2/whaler_27ft.glb` (+FBX, 43 parts)

---

**Source of truth.** The numbers above are values from the solver, not
hand-copied text. Generation 2's solved draughts are deliberately *deeper*
than generation 1's hand-tuned numbers (the shallower figures could not carry
the documented crews: see `boats/docs/THEM2_INSPECTION_REPORT.md` §8). Do not
keep any first-generation values on the ship side; the lifting-eye and boarding
positions are similar but re-measured, so re-derive from this spec before
wiring your davits.

_(auto-generated — do not edit by hand; regenerate with
`boats/scripts/publish_spec2.py`)_

# Functional demonstration and testing

Two kinds of testing are recorded here: **what was actually run** and
**what has not been run and must be verified in Roblox Studio by whoever
integrates the boats**. The distinction matters — nothing in this file claims
a Studio test that did not happen.

---

## 1. Tests actually executed

### 1.1 Geometric QA — `boats/scripts/verify.py`

Automated, repeatable, run against the finished `.blend` files. Interpenetration
tests use triangle-level BVH overlap between the actual meshes (not bounding
boxes), so a pass means no triangle of one part crosses a triangle of another.
Full output: [`VERIFICATION.md`](VERIFICATION.md).

**Boat A — 25 ft steam cutter (20 objects, 46 742 verts / 43 086 faces)**

| Check | Result | Detail |
|---|---|---|
| LOA, hull | PASS | 7.565 m modelled vs 7.620 m spec |
| LOA, extreme (rudder, gear) | PASS | 7.664 m |
| Beam | PASS | 2.262 m extreme incl. fenders, 2.134 m hull |
| No loose vertices / degenerate faces | PASS | — |
| Screw clear of the hull skin | PASS | 0 intersecting triangles |
| Screw clear of the keel | PASS | 0 intersecting triangles |
| Screw disc below the local keel line | PASS | disc top −0.274 m, keel −0.238 m |
| Funnel pierces the canvas (must overlap) | PASS | 22 intersecting triangle pairs |
| Boiler crown below the canopy | PASS | boiler +0.853 m, canopy top +1.016 m |
| Funnel crown above the canopy | PASS | funnel +1.634 m, canopy +1.016 m |
| Propeller and rudder are separate objects with their own origins | PASS | screw (−3.42, 0, −0.45); rudder (−3.62, 0, +0.65) |
| Published displacement | PASS | 3532 kg loaded, integrated in `boatgen.hydro` |

**Boat B — 25 ft clinker rowing cutter (24 objects, 31 819 verts / 29 700 faces)**

| Check | Result | Detail |
|---|---|---|
| LOA, hull | PASS | 7.599 m modelled vs 7.620 m spec |
| LOA, extreme (rudder shipped) | PASS | 7.915 m (0.30 m rudder overhang, published in the spec) |
| Beam | PASS | 2.089 m extreme |
| No loose vertices / degenerate faces | PASS | — |
| Rudder does not foul the planking | PASS | 0 intersecting triangles |
| Ten oars present as separate objects | PASS | 10 found |
| Oar origins on the rowlock axis | PASS | all 10 |
| Published displacement | PASS | 1897 kg loaded |

The runs also caught **two real defects which were fixed rather than
documented away**:

1. The propeller was mounted at x = −3.02 m, i.e. under the hull, and its disc
   cut through the keel and the planking (4 intersecting triangle pairs). It
   was moved aft to x = −3.42 m and down to z = −0.45 m, where the disc now
   passes clear of the hull and hangs below the counter as it should.
2. The rudder blade was built spanning z = +0.65 … −0.51, which put its upper
   half inside the transom. It is now hung below the counter (z = +0.04 …
   −0.60) with the stock passing up through the transom to the tiller.

### 1.2 Hydrostatics

`boatgen/hydro.py` integrates the actual modelled sections (Simpson's rule,
41 stations) against the itemised weight schedule:

| | light | loaded |
|---|---|---|
| Steam cutter | 3212 kg → draught 0.500 m | 3532 kg → draught 0.527 m |
| Rowing cutter | 1017 kg → draught 0.272 m | 1897 kg → draught 0.397 m |

Both boats sit at about 0.67 m freeboard loaded, which is the design intent —
they hang from the same davits and must look like a matched pair. A stability
check (`HullDesign.stability_check`) reports the metacentric height for each
loaded condition.

### 1.3 Luau script validation

Every Roblox script was compiled with the **Luau compiler** (`luau-compile`,
Luau release binaries) and linted with `luau-analyze --mode=nonstrict`:

```
Config.lua  WaterSurface.lua  Hydrodynamics.lua  BoatRig.lua  Effects.lua
SteamCutter.lua  RowingCutter.lua  BoatService.lua  BoatClient.lua
BuildBoat.lua  Manifest_steam_cutter_1888.lua  Manifest_rowing_cutter_25ft.lua
    -> 12/12 compile clean, 0 lint findings
```

This proves the scripts are syntactically valid and free of unused/undefined
locals. It does **not** prove they behave correctly at runtime in Roblox — that
is §2.

### 1.4 Robot-scale checks

The scale contract (1 stud = 0.28 m) is applied once, in `Config.STUD_PER_M`
and `BuildBoat.scaleAll`. Every part's size in studs is recorded in
`boats/exports/*/manifest.json`, so a mismatched import is visible by
inspection: the steam cutter's hull must come in at 27.21 studs long and
7.62 studs wide.

---

## 2. Tests NOT executed — Roblox Studio

**Roblox Studio is not available in this environment**, so no Studio test has
been performed. The following is the test procedure the integration engineer
should run, with the expected result for each step. Treat the boats as
"build-ready, unverified in-engine" until this list is done.

### Setup

1. Import `boats/exports/steam/manifest.json` meshes (or the per-part GLBs) as
   a folder; do the same for `rowing`.
2. Run `BuildBoat.assemble("steam_cutter_1888", folder)` and
   `BuildBoat.assemble("rowing_cutter_25ft", folder)` from the command bar.
3. Put `BoatService` in `ServerScriptService`, `BoatClient` in
   `StarterPlayerScripts`, and the other modules in a `ModuleScript` folder
   named `BoatService` (or adjust the `require` paths).
4. Add a water volume: either Terrain water, or a flat part named
   `WaterPlane`.

### Steam cutter — acceptance tests

| # | Test | Expected |
|---|---|---|
| S1 | Sit in the helm seat | HUD reads "25 ft STEAM CUTTER · ENGINE STOPPED" |
| S2 | Press **E** from cold | Smoke builds over ~6 s, then the screw starts; state changes to ENGINE RUNNING |
| S3 | Hold **W** | Boat accelerates; screw spins; smoke rate rises; bow lifts slightly |
| S4 | Release **W** | Boat carries her way and slows; screw idles down |
| S5 | Hold **S** while moving | Screw reverses, boat checks her way and goes astern at reduced power |
| S6 | Hold **A**/**D** at speed | Boat turns; rudder and tiller animate; at zero speed the helm does nothing |
| S7 | Press **E** again | Regulator shuts, smoke dies, screw stops, state returns to ENGINE STOPPED |
| S8 | Drive away from the seat | Controls are released; the boat drifts |
| S9 | Drive over a wave | Boat pitches and rolls; she does not hover rigidly |
| S10 | Ram the dock | The hull collides; the boat does not pass through |

### Rowing cutter — acceptance tests

| # | Test | Expected |
|---|---|---|
| R1 | Sit in the helm seat | HUD reads "25 ft ROWING CUTTER · OARS TRAILED" |
| R2 | Hold **W** | Oars swing to the catch, blades go square, drive, feather and recover — a repeating stroke at ~26 spm |
| R3 | Release **W** | Oars trail; the boat carries her way and slows gradually |
| R4 | Hold **A** while pulling | The boat yaws to port — from the bank imbalance, not a rudder |
| R5 | Hold Shift+W | Stroke power rises; boat accelerates to ~6 knots |
| R6 | Ten oars | All ten animate in step, none detached from its rowlock |
| R7 | Board from the water | The seat is enterable and the player sits down |

### Known risks to watch for

* **Motor6D pivot offsets.** `BoatRig.hinge` builds `C0`/`C1` from the part's
  current world position. If the meshes are imported with a different origin
  convention, the oars will jump on the first frame. Check R6 first.
* **Mass.** `BuildBoat` sets the hull's custom physical properties from the
  published loaded displacement. If the imported hull mesh is not the
  PrimaryPart the buoyancy probes will be misplaced; check S3/S9 first.
* **Thrust tuning.** The `max_thrust_n` values in `Config.lua` are estimates
  in Roblox force units, not Newtons. Expect to adjust them once to get the
  speeds in the spec (6–7 knots steam, 5–6 knots rowing).

---

## 3. What "done" means for these boats

* Geometry: complete, self-consistent, verified — yes.
* Documentation and drawings: complete — yes.
* Roblox integration: **code complete and compiling, not yet run in Studio.**

The boats are not being presented as Studio-tested. Everything that *has*
been tested is listed with its result in §1, and everything that has not is
listed in §2 with a procedure for closing it.

# Functional demonstration and testing

Two kinds of testing are recorded here: **what was actually run** and
**what has not been run and must be verified in Roblox Studio by whoever
integrates the boats**. The distinction matters — nothing in this file claims
a Studio test that did not happen.

---

## 1. Tests actually executed

### 1.1 Geometric QA — `boats/scripts/verify.py`

Automated, repeatable, run against the finished `.blend` files. The last run
reported **64 checks, 0 failures** across the three boats. Full output:
[`VERIFICATION.md`](VERIFICATION.md).

| What is measured | How | Result |
|---|---|---|
| Overall length, beam, depth | model extents vs `boatgen/specs.py` | PASS, all three boats |
| Loose vertices, degenerate faces, ngons | mesh audit; ngons are triangulated at build time | PASS |
| Screw clear of the hull and keel | BVH triangle overlap | PASS, 0 pairs |
| Funnel pierces the canvas, funnel and boiler crowns above/below it | BVH + heights | PASS |
| Boiler crown below the canopy crown | heights | PASS |
| **Joints that must overlap** | BVH, asserted *positive*: 15 named pairs (steam pipe into the boiler, funnel spigot, screw on its shaft, rudder stock through the counter, frames on the inner skin, knees under thwarts, pintles…) | PASS, each with its pair count |
| **Nothing but gear outside the planking** | every vertex of every interior object against an analytic hull envelope, `n_xi=160 × n_t=120` | PASS: A worst 45 mm (one foredeck knee), B and C 20 mm |
| **Every oar pivots in a rowlock** | each oar origin against the nearest rowlock geometry, in x, y *and* z | PASS: worst 16 mm (B), 18 mm (C) |
| **Port sidelight red, starboard green** | material faces by side | PASS: 38 red to port, 38 green to starboard |
| Whaler has no transom; five oars, single banked | station sampling + object list | PASS |
| Centreboard drawn up, inboard of the planking | BVH + containment | PASS |
| Propeller and rudder are separate objects on their own pivots | object origins | PASS |
| Displacement | integrated in `boatgen/hydro.py` | PASS: A 3532 kg, B 1897 kg, C 1487.5 kg loaded |
| **Export contract** (per boat) | read back from `exports/*/manifest.json`: every part ≤ 20 000 triangles, every part with a UV layer, part count | PASS: worst part 19 000 tris, 21/21, 25/25, 19/19 parts with UVs |

**A caveat that matters when reading any interpenetration report.** Blender's
`BVHTree.overlap()` counts *contact candidates*, not intersections. Calibrated
against a pair whose clearance is known exactly — the timbers stand 28 mm clear
of the inside of the carvel planking, with a whole diagonal skin between them —
it still reports 378 "intersecting" triangle pairs. So a pair count is a list of
places to look, not a defect count; every pair in the QA audit was opened,
measured against the drawing intent, and then either fixed, declared a joint
(and asserted positively, above) or dismissed with the geometry cited in
[`AUDIT_RESPONSE.md`](AUDIT_RESPONSE.md).

The three real defects the geometric QA has caught so far are recorded where
they happened: the propeller buried in the keel and the rudder inside the
transom (both fixed, §2), the oars standing out through the planking of two
boats (fixed — see §1.5), and the engine bearers, feed tank, cross floors, deck
edges, thwart knees, mast clamp, boat hook and grapnel found by the containment
test.

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
SteamCutter.lua  RowingCutter.lua  Whaler.lua  BoatService.lua  BoatClient.lua
BuildBoat.lua  Manifest_steam_cutter_1888.lua  Manifest_rowing_cutter_25ft.lua
Manifest_whaler_27ft.lua
    -> 14/14 compile clean, 0 lint findings
```

This proves the scripts are syntactically valid and free of unused/undefined
locals. It does **not** prove they behave correctly at runtime in Roblox — that
is §2. Three runtime faults were nonetheless found by *reading* the audit's
evidence against the code and are now fixed: the buoyancy probes were laid out
athwartships (the assembly puts the bow on −Z, not −X) and all forward of
midships, the thrust point was on the beam rather than at the stern, the hull's
"right" vector was its left, and the steam cutter drove its screw and rudder by
writing `CFrame` on parts that a `Motor6D` was already driving. None of these
would have shown up in a compile.

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

#
**Boat C — 27 ft double-ended whaler (19 objects, 30 584 verts / 28 951 faces)**

| Check | Result | Detail |
|---|---|---|
| LOA, hull | PASS | 8.203 m modelled vs 8.230 m spec |
| LOA, extreme | PASS | 8.737 m including rudder, tiller and ring bolts |
| Beam | PASS | 1.871 m measured over the hull, spars and oars excluded |
| Double ended | PASS | no transom object in the scene |
| Five oars, single banked | PASS | 5 found, 3 to port and 2 to starboard |
| Centreboard drawn up | PASS | lowest point of the assembly −0.435 m, inside the hull |
| Rudder clear of the planking | PASS | 0 triangle pairs intersect |
| Centreboard trunk clear of the planking | PASS | 0 triangle pairs intersect |
| Everything inside the planking | PASS | nothing more than 20 mm proud of the skin |
| Published displacement | PASS | 1487.5 kg loaded, solved in `boatgen.hydro` |

The dimension check needed a per-boat allowance for the whaler: a 15 ft 3 in
yard on a 6 ft beam boat overhangs by design, so beam is measured with the
spars and oars excluded. That is a deliberate change to the test, not a
loosened one -- the boat's own beam is still checked to 30 mm.

### 1.5 Containment: is the gear where the hull is?

The interference tests ask whether two named objects touch. They cannot ask the
matter that actually shows in a render: whether a thwart, an oar or a floor
timber stands a few millimetres proud of the outside of the planking, where it
casts a hard shadow and reads as a dark slash on a varnished topsides.

`verify.py` now measures every vertex of every internal object against the hull
envelope generated from the same design object that built the hull, sampled
into a half-breadth table so the test takes seconds rather than minutes. Above
the sheer band, forward of where the hull is 100 mm wide, and on the objects
that are outside by design (rudder, rowlocks, fenders, spars, backbone timbers)
are skipped.

It found seven real defects that the interference tests had passed, all now
fixed in the builds rather than excused:

| Boat | Defect | How far out |
|---|---|---|
| A | engine bearers, square section in a 0.44 m bilge | 152 mm through the bottom |
| A | feed-water tank and coal bunker, sized to a flat box | 116 mm |
| A | cross floors measured 0.16 m up the topsides | 69 mm |
| A | fore and side deck edges measured above deck level | 39-55 mm |
| B | boat hook, started abreast the fore thwart so its head left the bow | 589 mm |
| B | mast clamp, cut to the breadth at the sheer above it | 33 mm |
| C | stowed oars, straight sticks in a hull that closes in at both ends | 205 mm |
| C | boat hook head | 443 mm |
| C | grapnel, hung in the air outboard of the after topsides | 340 mm |
| C | thwart knees, built as vertical slabs against a falling topsides | 87 mm |

## Known risks to watch for

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

---

## THEMISTOCLES-II additions (2026-11-17)

### `boats/scripts/verify2.py` — headless QA gate (no Blender needed)

Runs against the exported metadata JSON:

1. **Hydrostatic consistency** — the weight budget must equal the solved
   displacement, loaded and light, for all three boats.
2. **Moving-part pivots** — every animated part (10 cutter oars, 5 whaler
   oars, rudder, propeller) must carry a pivot, at rail height for oars, aft
   and submerged for the screw, at the stern for the rudder.
3. **Roblox triangle budget** — no part over 19 000 triangles.
4. **Envelope sanity** — no part longer than the boat (+stowage allowance),
   nothing wider than the fenders.
5. **Manifest reproducibility** — `gen_manifest2.py` run on the export
   metadata must regenerate the committed `roblox/src/Manifest_*.lua`
   byte-for-byte; drift means someone edited one side by hand.

Status at commit: **all 30 checks pass** (`python3 boats/scripts/verify2.py`).

### Studio play-test status (unchanged from generation 1)

The Lua controllers are byte-compatible with the QA'd generation-1 control
stack (same part-name contract, same manifest schema).  They have been
statically reviewed and the manifests machine-verified (table balance,
moving-part cross-references), but the boats have **not** been sailed in a
Roblox Studio session on this branch.  That remains the honest state of the
deliverable until someone opens Studio.

# Response to the QA audit (`agent/qa-audit`, `QUALITY_ASSURANCE_AUDIT.md`)

The audit was made against `agent/boats` at `ec4c3fa`. It names 4 critical
(P0), 4 high (P1) and 3 medium (P2) defects against the boats branch. This is
what was done about each one, in the audit's own numbering.

Three verdicts are used, and nothing is left as "accepted":

* **FIXED** — the defect was real and the geometry or the code changed.
* **DECLARED** — the overlap is real, but it is a joint, not an error; it is now
  an explicit, named pass in `verify.py` with the reason attached, instead of an
  unnoticed collision.
* **DISPUTED** — the audit's reading of the geometry is wrong, and the evidence
  is given.

---

## 3.1 Steam cutter

| Audit item | Verdict | What changed |
|---|---|---|
| **[P0]** starboard sidelight painted `Hull_Black` instead of green | **FIXED** | There was no green in the palette at all. `Signal_Glass_Red` and `Signal_Glass_Green` are now real transmissive glasses (`MAT` slots 17/18), the **lenses** carry the colour and both **housings are brass** — which is how a sidelight is actually built. The fitting was redesigned: hooded brass body, forward-facing lens, brass hood. `verify.py` now asserts that red faces lie to port and green faces to starboard. |
| **[P0]** coal bunker forward of the boiler, contradicting drawings note 5 | **FIXED** | `X_BUNKER` moved from **+1.62 m (the forward passenger cockpit) to −0.20 m**, i.e. abaft the boiler and forward of the engine, where the fireman stands. The bunker is now a riveted iron bin with coal standing proud of its open top and a hinged lid stoved against the boiler. The *cause* of the disagreement was that the layout numbers were typed twice; they now live in `boatgen/layout.py`, which both `build_steam_cutter.py` and `drawings.py` read, so the sheet cannot disagree with the model again. |
| drawing vs model: boiler width, funnel position | **FIXED** | Consequence of the above: the inboard profile now draws the boiler 0.81 m wide at x = 0.14…0.86 and the funnel at x = 0.435…0.605, straight from the model's own constants. `d-002_a` was re-rendered. |
| **[P0]** 58 BVH overlaps | mixed | The set is not homogeneous. See the table below. |
| `Frames ↔ Inner_Diagonal_Skin` (20 880 pairs) | **FIXED — and the fix was wrong the first time** | The stacking of a double-diagonal boat is: planking, first diagonal, second diagonal, then the timbers fastened over both. The build had the planking at 0–24 mm, one diagonal at 24–35 mm, the second at 38 mm — i.e. *inside* the frames — and the timbers from 24 mm, so the second diagonal and both skins ran through the timbers. Moving the second diagonal further in, to 70 mm, "cleared" it by pushing it out the other side of the frames, which is not how a boat is built. The stack is now stated once and used by all four parts: **planking 0–24, first diagonal 24–35, second diagonal 35–46, timbers 46–86 mm**, with 2 mm of bedding compound between the timber face and the skin. |
| `Boiler ↔ Pipework_Fittings` (355), `Boiler ↔ Funnel` (154), `Propeller ↔ Shafting` (86), `Rudder ↔ Transom` (86) | **DECLARED** | These are joints by construction: the steam pipe enters the boiler shell, the funnel spigot enters the smoke box, the screw is on a taper on its shaft, the rudder hangs on pintles through the transom. They are now named in `verify.py` as `MUST_PASS`/joint pairs with the reason, so they cannot be mistaken for silent collisions later. |
| `Keel_Stem_Frames_Gunwale ↔ Planking_Carvel` (3 315), `Frames ↔ Planking_Carvel` | **DECLARED** | Frames are fastened to the planking; the keel, stem, sternpost and gunwale are fastened to the ends of it. What must *not* happen is a timber standing out through the outside of the planking, and that is now a hard test — the containment check below — with a 45 mm pass on this boat (one foredeck knee). |

### A note on what the audit's overlap counts actually measure

While working through the frame/skin pair above, the counts were calibrated
against a pair whose clearance is known exactly. On the finished steam cutter
the timbers stand **28 mm clear** of the inside of the carvel planking — there
is a whole diagonal skin between them — and Blender's `BVHTree.overlap()` still
reports **378 "intersecting" triangle pairs** for `Frames` vs
`Planking_Carvel`. The same test reports 338 for `Frames` vs `Seats` and 334 for
`Frames` vs `Coamings`, both of which are certainly not touching anything.

So `overlap()` counts *contact candidates*, not intersections: it is
conservative, and it cannot tell a 0.1 mm interpenetration from a 5 mm
clearance once the two surfaces are within a triangle's width of each other.
The audit's totals (58 pairs on A, 47 on B) are therefore a list of *places
worth looking at*, not 58 defects — which is how this response has treated
them: each pair was opened individually, measured, and either fixed, declared a
joint, or dismissed with the geometry cited. The measurement that *can* be
trusted to a millimetre is the containment test below, which samples the hull
envelope analytically rather than by triangle proximity.
| **[P0]** shaft slopes 6.27° and hangs underneath | **DISPUTED** | A propeller shaft is raked whenever the engine sits higher than the stern gland, which on a 25 ft launch it must — 6.27° is an ordinary installation angle, not a defect. The outboard length of the shaft already runs inside a stern tube (`machinery.stern_tube`) and the inboard length is under the engine-room floorboards; nothing hangs in the water. No change made, and the slope is now stated in `docs/CONSTRUCTION_A_steam_cutter.md` so it reads as a decision rather than an accident. |
| **[P0]** `Boiler` contains 474 ngons | **FIXED** | Every object now passes through `bl.triangulate_ngons()` at build time: 474 → 0 on the boiler, 78 on the canopy, 44 on the frame, 71 on the engine, and so on across all three boats. |
| **[P0]** `Canopy_Cover` has 548 boundary edges (zero-thickness sheet) | **FIXED** | The canvas is solidified 3.5 mm at build time (`bl.solidify`): it has an inside now, it shades as cloth, and there are no boundary edges. |
| aft cockpit lacks floorboards | **FIXED** | New `Floorboards` part: two grating panels in the after cockpit, lifted on cleats. |
| **[P0]** hull parts exceed Roblox's 20 000-triangle limit (`Planking_Carvel` 23 608, `Inner_Diagonal_Skin` 21 240, complete hull 76 492) | **FIXED** | `export_all.py` now decimates any part over 19 000 triangles **on the export copy only** — the `.blend`, the renders, the drawings and the verification all still use the full-resolution model. 21/21 parts now export at ≤ 19 000. |
| **[P0]** `manifest.json` reports polygon counts, not triangles | **FIXED** | The count is taken after `calc_loop_triangles()`, and the manifest records both `triangles` and `triangles_before_decimation`. |
| **[P0]** 0 UV layers on every part | **FIXED** | Every exported part gets a cube-projected `UVMap` (`bl.uv_unwrap` in the build, and a UV layer is created in the exporter if a part somehow lacks one). 21/21, 25/25, 19/19 parts carry one. |

## 3.2 Rowing cutter

| Audit item | Verdict | What changed |
|---|---|---|
| **[P0]** all 10 `Oar_*` pivots are at the stowed position inboard, not in the rowlocks | **FIXED** | Correct, and worse than the audit knew: the oars were *also* standing out through the planking at the ends, because they lay at a fixed offset from the centreline in a hull that closes in at both ends. Both faults had one cause — a stow position used as a pivot. Each oar object's origin is now computed by `rowlock_pivot()`, the throat of its own crutch, and the stowed mesh is placed from `hull.clear_y()`, the width-limited offset the rest of the boat's gear uses. `verify.py` now measures the pivot in **all three axes**: every oar origin is within 18 mm of a rowlock vertex. The same fix was applied to the whaler. |
| **[P1]** `Thwart_Knees` are plain boxes | **FIXED** | `parts.thwart_knee` now builds a grown **L**: a hanging leg that follows the planking down (tapered, so it cannot stand proud of a falling topsides) and an arm running inboard under the thwart, which is the whole point of a knee. |
| **[P1]** `Floorboards` narrow (0.732 m) | **FIXED** | Seven slats instead of five. |
| **[P1]** `Keel_Stem_Sternpost` has 19 loose edges | **FIXED** | `bl.obj_from_builder` now deletes loose edges and vertices in every object of every boat, so no build can leave them again. |
| **[P1]** `Planking_Clinker` 27 896 tris, hull 48 214 | **FIXED** | Export-side decimation (see above). |
| `Rudder ↔ Keel_Stem_Sternpost` (68), `Rudder ↔ Transom` (52) | **DECLARED** | Pintles through the sternpost and the transom knee: that is what hangs a rudder. Named as joints in `verify.py`. |
| `Frames ↔ Planking_Clinker` (14 167) | **DECLARED** | Frames are riveted to the planking. The test that matters — nothing *through* the planking — is the containment check, and B passes it at 20 mm. |

## 3.3 Roblox scripts

| Audit item | Verdict | What changed |
|---|---|---|
| **[P0]** `gen_manifest.py` emits `parts = {{` | **FIXED before the audit snapshot** (`c9a4598`) | All three manifests compile; `luau-compile` is part of the pipeline check now. |
| **[P0]** `Hydrodynamics.lua` probes all forward, thrust misaligned | **FIXED (and worse than reported)** | The probes were not merely all forward: they were spread along **+X**, which in the assembled boat is *athwartships*, because the importer sets the bow to −Z. They now run fore-and-aft along −Z from −0.42 to +0.45 of the length, and the thrust point is at the stern (**+Z**), below the waterline. The `right` vector was the boat's *left*, so every lateral drag term had the wrong sign — also fixed. A stale damping line that multiplied a term by zero is gone. |
| **[P0]** `BuildBoat` has no whaler manifest | **FIXED** | `MANIFEST_MODULES` had no `whaler_27ft` entry, so the third boat could not be assembled at all. |
| **[P1]** `SteamCutter.lua` fights the rudder Motor6D, reads roll instead of yaw, expects a `FunnelTip` that nothing creates | **FIXED** | The screw and the rudder are now driven **through their joints** (`Motor6D.C0` rebuilt each frame from a captured rest pose), so nothing overwrites `CFrame` and nothing accumulates. The helm is a yaw about the joint, not `asin(RightVector.Y)`. `BoatRig.ensureFunnelTip` creates the smoke attachment at the funnel crown if the export did not carry one. |

## Cross-project (section 1)

| Audit item | Verdict | What changed |
|---|---|---|
| **[P0]** divergent `boats_spec.json` between ship and boats | **FIXED on this side** | `interfaces/boats_spec.json` now carries an `integration` block: `craft_id_aliases` (`cutter_steam_25 → steam_cutter_1888`, `cutter_rowing_25 → rowing_cutter_25ft`, `whaler_27 → whaler_27ft`), a `craft_type_enum`, the export contract (metres, 19 000-triangle cap, one UV layer, moving-part origins) and `davit_rating_required_kg`. |
| **[P0]** steam cutter mass 3 532 kg vs the ship's 2 000 kg davit limit | **DECLARED — a real conflict, on the ship's side** | The weights are weighed, not guessed: the steam cutter is 3 212 kg light, 3 532 kg loaded. A 2 000 kg davit cannot hoist her, and shrinking the model to fit the limit would make it a lie. The spec now publishes `davit_rating_required_kg` (3 900 / 2 100 / 1 700 kg) and states the conflict in plain words, so the liner agent has the number it needs. |
| **[P1]** export units and forward axes differ between repos | **NOT A DEFECT HERE — declared** | The boats export in **metres** with the bow on **+X**, and `BuildBoat` scales by `STUD_PER_M` and yaws the model so the bow is on −Z. The export contract is now written into the spec (`units`, `origin_of_moving_parts`, `per_part_triangle_limit`) so the ship agent can convert with a stated rule rather than a guess. |

---

## What the audit did not catch, and the boats did

Running the audit's method — measure, don't assume — turned up defects of a
kind the audit itself missed, because its BVH pass tests *named pairs* and its
visual pass reads finished renders. Both miss a thwart standing 10 mm out
through the planking: it shadows as a dark sliver, and no pair of named objects
is involved.

`verify.py` now measures every internal vertex against the hull envelope, and
found ten such defects across the three boats, all fixed: engine bearers 152 mm
out through the bottom, a feed tank 116 mm out, cross floors measured 160 mm up
the topsides, deck edges laid to the breadth above deck level, a boat hook
589 mm out through a bow, a mast clamp cut to the wrong height, five oars
205 mm out through the planking, a grapnel hanging in mid-air 340 mm outside
the boat, and thwart knees built as vertical slabs. Frames and keelsons are now
sided down at the stems, where the hull is 6 mm wide and a 23 mm frame blank
was standing outside the planking.

The full list is in `docs/TESTING.md` §1.5 and `docs/REALISM_PASS.md`.

## Verification status after this pass

`verify.py -- both` → **49 checks, 0 failures**, of which:

* 12 interpenetration / joint pairs, each with a stated reason;
* 3 containment checks (one per boat) against the hull envelope;
* 3 export-contract checks per boat (triangle cap, UV layers, part count);
* oar-pivot proximity in three axes, sidelight colour sides, transom-free
  whaler, centreboard drawn up, five oars single banked;
* dimensions, mesh sanity, clearances, pivots and displacement, as before.

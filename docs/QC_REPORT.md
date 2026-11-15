# QC REPORT

The rule applied throughout: **nothing is complete because it exists in Blender.** Every
claim below was produced by a test that could have failed, and the failures that were
found are listed with the failure itself, not just the fix.

---

## 1. Automated checks that run on every build

`blender/build_ports.py` refuses to render a port it has not measured. Three checks run
before the first sample is taken.

### 1.1 Layout overlap audit

Every placed building registers its footprint with `portsite.LayoutAuditor`, which
reports any pair that overlaps by more than 5 cm in both axes.

| Build | Prototypes | Instances | Instanced triangles | Overlaps |
|---|---|---|---|---|
| Port A, first run | 40 | 290 | 520,906 | 0 |
| Port A, first run vs. all berths | — | — | — | 4 berths reported **CHECK** |
| Port A after fixes | 46 | 381 | 770,154 | 1 → **0** |
| Port B, first run | 36 | 269 | 262,423 | 0 |
| Port B after dock fix | 41 | 291 | 378,170 | **0** |

The one overlap caught was `A_goods_shed` ↔ `A_warehouse_3` (2.4 m). It was found by
the auditor, not by eye, and the warehouse was moved 212 → 206 m along the quay.

### 1.2 Berth clearance

A ship of the stated envelope must have 4 m of clear water in total around it. Results
are printed per berth on every run.

| Port | Berth | Clear rectangle | Envelope | Result |
|---|---|---|---|---|
| A | A-B1 | 26 × 212 m @ 11 m | 180 × 20 × 9 | OK |
| A | A-B2 | 20 × 110 m @ 6.5 m | 100 × 14 × 5 | OK |
| A | A-B3 | 24 × 132 m @ 9 m | 130 × 18 × 8 | **CHECK** — 2 m short at the ends |
| A | A-B4 | 22 × 124 m @ 9 m | 116 × 17 × 8 | OK |
| B | B-B1 | 28 × 210 m @ 10 m | 180 × 20 × 9 | OK |
| B | B-B2 | 28 × 320 m @ 9 m | 140 × 18 × 8 | OK |
| B | B-B3 | 18 × 120 m @ 8 m | 105 × 13 × 6.5 | OK |

A-B3's shortfall is real and is recorded in `docs/port_a_layout.md` §7 rather than
being tuned away by relaxing the rule.

### 1.3 Camera placement by ray-cast

A camera inside a building renders a black frame, which is easy to mistake for a
lighting bug. So before a view is trusted, the camera point is ray-probed in ±X, ±Y and
+Z and must have ≥ 8 m of clear space.

This check found a genuine problem and produced a false alarm:

- **Real:** `03_street` at (63, 20, 6.5) sat in a gap that closed to 4 m.
- **False alarm:** an early probe reported the camera "inside `A_station`". That was
  wrong — the ray was hitting the **prototype object**, which lives at the origin in
  the `_PROTOTYPES` collection and is excluded from renders but is still ray-castable.
  Any future probe must exclude `_PROTOTYPES`, or the whole collection will appear to
  be sitting on top of the scene origin.

---

## 2. Visual inspection record

Every image below was opened and looked at. Where something was wrong, what was wrong
is written down.

| View | What was checked | Finding |
|---|---|---|
| A `01_aerial` | overall composition, density, water boundaries | **First version too sparse** — the yard read as tarmac. Densified with hotel, terrace, goods sheds, boundary wall, timber yard, cargo and winches; open ground re-surfaced with setts. |
| A `01_aerial` | ground tone | Ground rendered near-black under AgX. Diagnosed as albedo, not lighting (see §3). Fixed in the texture palette. |
| A `03_street` | street-level legibility, rail, lamps, cranes | Good after the camera was moved to the waterfront apron: rails, gas lamps, hydraulic cranes and a continuous building line all read. |
| A `04_dockside` | quay edge, cabling, cargo | Reads; quay edge and mooring furniture present. |
| A `05_landing_stage` | floating stage against the quay | Present and correctly floating; still water, no tide, as intended. |
| B `01_aerial` | shipyard composition | First version had **the graving docks buried in the land slab** — they had never been cut out of it. Caught here, fixed by adding them to the land's hole list. |
| B `04_graving_dock` | dock interior | After the fix the docks read as voids but the floor was pure black. Investigated at length (§3); the cause turned out to be physically correct shadow, and the light was re-aimed to rake along the docks. |
| B `03_street` | yard interior | Reads as a shadowed working yard; the sun is behind the shop row from this angle, so the elevations are dark. Acceptable but the least attractive view of the set. |
| B `05_slipways` | slip notches, shoring, staging | Slips cut correctly into the frontage with water in the notch. |

---

## 3. Failures investigated, and what they actually were

Recorded because each of these cost real time and each has a lesson.

1. **Black ground.** Hypotheses tested and falsified: Fast GI, the denoiser, ink lines,
   oversized-quad normal mapping, wrong sun vector, exposure. The cause was simply the
   setts albedo under AgX. Two intermediate over-corrections made the ground look like
   concrete (0.352) before settling at 0.174.

2. **Black street frame.** Cause: the camera was inside geometry. The lesson is to
   ray-probe a camera point *before* spending two minutes rendering it.

3. **Black graving-dock floor.** This one was investigated three times and was **not a
   bug**:
   - ray-cast down onto the floor → hit granite at the right elevation, normal +Z;
   - forcing the granite base colour to pure red → the floor lit up red, proving it was
     being shaded and simply very dark;
   - a shadow ray from the floor toward the sun → hit the dock's own wall 12 m away.

   At 40° elevation a sun crossing a 24 m wide, 11 m deep dock puts the whole floor in
   the shadow of its own wall. The fix was to move the sun's azimuth so it rakes along
   the dock's length instead of across its width. **A dark pit is not a broken pit.**

4. **A dock 15 m deep.** The graving dock's `depth` parameter was being measured from
   water level instead of from the coping, which made the dock 3 m deeper than any
   Victorian dry dock. Graving docks are specified from the coping; the parameter now
   means that.

5. **`site.py` shadowing the standard library.** Naming a module `site` inside a
   package breaks the interpreter's own `site` import. Renamed to `portsite.py`.

---

## 4. Performance and asset hygiene

| Measure | Port A | Port B |
|---|---|---|
| Prototypes | 46 | 41 |
| Instances | 381 | 291 |
| Instanced triangles | 770,154 | 378,170 |
| Drawn triangles (worst view, aerial) | ≈ 690 k | ≈ 350 k |
| Materials | 51 shared | 51 shared |
| Texture sets | 16, at 512² albedo/rough/normal | same |
| Sign textures | 23 baked boards | same |
| Lights | sun + fill + world | sun + fill + world |
| Render time, 1280×720 @ 40 spp | 80–240 s | 80–240 s |

Construction is modular: prototypes are defined once and placed as linked duplicates,
so a change to a prototype updates every instance and the mesh data is shared in
memory. That is why 46 prototypes can carry 381 placements.

Material count is deliberately low (51, of which 23 are sign boards sharing one
material each) so that the Roblox import does not produce a draw call per object.

---

## 5. What has NOT been verified

Stated plainly so the next agent does not assume it was done.

- **Roblox import has not been executed.** No Roblox Studio session exists in this
  environment. The Luau is written against the documented API and the layouts are
  generated from the same metadata the model uses, but it has not been run.
- **Collision meshes have not been built or measured.** The plan for them is in
  `ROBLOX_SETUP.md` §4; the exported meshes are render geometry.
- **Interiors are modelled but not lit as interiors.** There is no separate interior
  lighting rig; north-light and window glow carry them.
- **The renders are architectural-visualisation quality, not photoreal.** They are
  honest, consistent and readable, and they are the weakest part of the deliverable
  relative to the geometry.

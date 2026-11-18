# THEMISTOCLES-II — Previous-Generation Inspection Report

**Scope of inspection:** all four branches, all commits (`git log --all`), every file in
`boats/`, `refs/rmg/`, `roblox/`, `interfaces/`, the QA audit on `agent/qa-audit`, the
ship-side contract on `agent/ship`, and every published render, drawing and reference
photograph at full resolution. Inspected 2026-11-16 against the `agent/boats` tip
`6bd984e`.

## 1. What the previous generation actually built

The previous boat agent (call sign abandoned, branch `agent/boats`) delivered three
craft from a procedural `bpy` pipeline (`boats/scripts/boatgen/`):

| | Boat A | Boat B | Boat C |
|---|---|---|---|
| Type | 25 ft steam cutter | 25 ft clinker rowing cutter, 10-oared double-banked | 27 ft double-ended whaler |
| Hull | carvel over double-diagonal, 12 frames | clinker, 11 strakes | clinker, 9 strakes, drop keel |
| File | `blend/boat_a_steam_cutter.blend` | `blend/boat_b_rowing_cutter.blend` | `blend/boat_c_whaler.blend` |
| Faces | 59 163 | 31 076 | 29 587 |

The roster matches the ship-side requirement (`agent/ship/interfaces/boats_spec.json`:
a 25-ft steam cutter and a 25-ft rowing cutter) plus a self-assigned whaler. The choice
of types is historically defensible for an 1889 liner and is **retained**.

## 2. Inspection method

1. **Read the pipeline source** — `geom.py`, `hull.py`, `machinery.py`, `parts.py`,
   `specs.py`, `bl.py`, all three build scripts, `verify.py`, `export_all.py`,
   `render_sheet.py`, `drawings.py`.
2. **Opened every reference photograph** (`refs/rmg/`, six photographs of RMG SLR0772,
   SLR1818, SLR0719) at full resolution.
3. **Opened every published render** in `boats/renders/` (27 images) plus the cutaways
   and the reference board, and every drawing sheet.
4. **Read the QA audit** (`QUALITY_ASSURANCE_AUDIT.md`, `agent/qa-audit`) and the boats
   agent's response (`docs/AUDIT_RESPONSE.md`) line by line; both were checked against
   the geometry scripts.
5. **Read all 14 Luau modules**, the manifests, `gen_manifest.py` and both interface
   specs (boat-side and ship-side).
6. **Checked the ship-side integration numbers** directly: davits at ship-x +38.0 m
   (starboard, steam cutter) and −34.0 m (port, rowing cutter), keel rest z = 17.90 m,
   2.9 m davit span, 2000 kg published limit.

## 3. Components-worth-preserving assessment

| Component | Verdict | Note |
|---|---|---|
| Hull-form design method (PCHIP-faired sheer/keel/half-breadth curves) | **PRESERVE the method, rebuild the mesh** | The parametric approach is sound; the lofted surfaces are too coarse (too few stations, flat shading makes them read as slabs). |
| Hydrostatic solver (`hydro.py`) | **PRESERVE concept** | Simpson integration against itemised weights; re-implement on the new kernel. |
| Principal dimensions + weights + interface spec format | **PRESERVE** | Defensible figures; keep compatible with the ship contract. |
| Part-file export scheme (per-system GLB+FBX + manifest.json) | **PRESERVE scheme, rebuild parts** | Manifests must be regenerated from my geometry. |
| Luau module architecture (service/controller/rig/hydro split) | **PRESERVE, refine** | Compiles clean; improve oar animation and add missing features (rig hoisting state, feeder details); keep the honest "not run in Studio" stance. |
| `verify.py` checks (containment vs hull envelope, oar-pivot-in-rowlock, joint declarations) | **PRESERVE the tests, rewrite against new geometry** | Good ideas; the tests below extend them with interior-fit and clearances checks. |
| Historical evidence file style (DOCUMENTED / RECONSTRUCTED / ASSUMPTION) | **PRESERVE the discipline** | Register rewritten with the mission's three additional RMG references actually consulted in this generation. |
| Drawings via matplotlib from the same design object | **PRESERVE the principle** | Sheets re-drawn from the new hull definition. |

Everything else — every mesh — is rebuilt. See §4.

## 4. Deficiencies found (visual, component-level)

Evidence: `renders/steam_hero.png`, `steam_machinery.png`, `steam_cutaway_c.png`,
`rowing_hero.png`, `rowing_from_above.png`, `rowing_cutaway_b.png`,
`whaler_hero.png`, `drawings/reference_board.png`, build scripts.

### 4.1 Whole-model finish (all three boats)
- **[REBUILD] Flat shading across every part.** Transom faces, coamings, canopy, thwarts,
  boiler drum and canopy hoops all read faceted. Hulls show silhouette banding. This is
  the single largest "game prop" tell.
- **[REBUILD] Materials are flat colours.** No wood grain anywhere; the varnished
  mahogany and the black topsides differ only in RGB; rope, canvas, brass, iron all
  uniform. The reference photographs show grain, seams, tar, and patina.
- **[REBUILD] Edge treatment absent.** Real joinery has chamfered arrises; the models
  have knife edges on thwarts, decks and furniture.

### 4.2 Boat A — steam cutter
- **[REBUILD] Machinery block.** The engine is a vertical cylinder on two slab columns
  with one horizontal pipe. No crosshead, slide bars, connecting rod, crank, eccentric
  or reversing gear visible; no cylinder cleading; no drain cocks. The boiler is a
  riveted drum with a top plate; gauge glass, try cocks, safety valves, whistle, stop
  valve, blow-down and feed check are absent or token. Pipework is two lagged tubes.
  The shaft is a bare rod with one plummer; coupling flanges and the thrust block are
  absent. Visible in `steam_machinery.png` and `steam_cutaway_c.png`.
- **[REBUILD] Boiler mount and bunker.** The boiler stands on two plain blocks; the iron
  coal bunker is an open box with a coal pile as a single blob; fire irons absent.
- **[REBUILD] Canopy.** Canvas is a smooth solid blob; no seams, no hem, no lacing at
  the funnel boot. Hoops are bare brass tubes with no sockets.
- **[REBUILD] Steering.** Tiller absent geometry check shows only stock head; no
  tiller/tackle in the after cockpit.
- **[REBUILD] Propeller.** Two flat paddle-like blades; no helical pitch surface, no
  boss flange or fairwater; blade tips squared.
- **[REBUILD] Fittings.** Sidelight lamps are material-coloured boxes; no lenses, no
  hoods. Compass, bilge pump, feed tank, whistle plumbing absent.
- **[FIXED BY AUDIT, VERIFY IN REBUILD]** sidelight colours, bunker position, triangle
  counts, UVs — recorded fixed in `AUDIT_RESPONSE.md`.

### 4.3 Boat B — rowing cutter
- **[REBUILD] Joinery.** Thwarts are plain planks on slab knees; no thwart risers under
  their ends (visible floating ends in `rowing_cutaway_b.png`); no breasthook, no
  quarter knees, no stern-sheet side benches, no stretchers (footrest boards), no
  seating in the bow. Floorboards are a single long pallet instead of slatted foot
  gratings over the frame bays (SLR1818 shows slatted floors on pegs).
- **[REBUILD] Oars.** Sticks of near-constant section; no shaped blades, no leathers or
  buttons at the rowlock bearing. In `rowing_from_above.png` the stowed oars cross the
  gunwale caps near the bow and lie through thwarts — the stowage is not how a boat is
  actually loaded (oars lie on the thwart *risers*, handles aft, blades clear of the
  side seats).
- **[REBUILD] Rowlocks.** Token Y-crutches; no gunmetal sockets, no gunwale pads; the
  SLR/Service pattern crutch should be a galvanised U in a swivel socket on a shaped
  pad let into the gunwale.
- **[REBUILD] Rudder gear.** A plate rudder hangs on the transom but the pintle/gudgeon
  detail and the tiller with its beckets are absent.
- **[ADD] Sailing rig.** The ship contract expects a dipping lug capability; SLR0719
  shows the mast clamp on the bow thwart which the previous generation modelled — but
  no mast, spars or furled sails are carried. The rebuild carries the rig stowed in the
  boat (davit condition), documented as such.
- **[REBUILD] Keelson lifting eyes.** Present as small rings; SLR1818 shows large forged
  eyes through the keelson — rebuild at the right size, through-bolted.

### 4.4 Boat C — whaler
- **[REBUILD] Rig.** Rigging is single hairlines; no blocks, no belaying pins, no
  mast hoops, and the "furled sails" are smooth cylinders with no gaskets or folds.
- **[REBUILD] Drop keel.** Case present; no handle gear, no clamping screw at the case
  top, no visible plate cap.
- **[REBUILD] Same interior joinery problems as Boat B** (knees, risers, gratings,
  breasthooks both ends since she is double ended).
- **[REBUILD] Rudder/tiller fittings** as Boat B.

### 4.5 Drawings, renders, Roblox
- Drawings (`d-001..d-004`) are good in intent; redraw from the new geometry.
- Renders: re-render everything with smooth shading, procedural materials and closer
  framing; add underside, top-down, transom-on, bow-on, interior down-angle, machinery
  close-up, hull-construction view (skeleton), and a boarding-detail view per boat.
- Roblox scripts compile but are untested in Studio (stated honestly in
  `docs/TESTING.md` §2 — keep that honesty). Regenerate manifests from the new exports;
  keep controls; fix the residual items the audit listed as risks where they can be
  fixed without Studio (deterministic pivot capture at assembly, named-part fallbacks).

## 5. Reconstruction plan (what THEMISTOCLES-II builds)

A new engine, `boats/scripts/them2/`, deterministic and numpy-first like the previous
one, with:

1. **Lofted hull** at 41×25 mesh density per half, smooth-shaded, with section-morphing
   that gives a real hollow garboard turn at the ends and a moulded (rounded) bilge
   amidships — verifiable in the bow-on/stern-on renders.
2. **Planking as strakes** with real hood ends into a stem rabbet, clinker laps with
   visible lands and a shadow line that is geometry, and carvel seams with caulking
   bevels for the steam cutter.
3. **Complete backbone**: keel with hog, stem + forefoot and apron, sternpost, deadwood,
   transom with margin plank and breast knees.
4. **Complete interior joinery**: bent timbers on the skin, floors with limber holes,
   keelson, risers, clamps, breasthook(s), quarter knees, thwarts on knees, side
   benches, stern sheets, slatted foot gratings on bearers, stretchers, lockers with
   lids and hinges.
5. **Complete pulling gear**: correctly lofted oars (blade, loom, grip, leather,
   button) stowed plausibly; swivel rowlocks on pads; steering sweep or rudder+tiller
   with ironwork; mast clamp with mast **and rig carried** (dipping lug, fore + main,
   furled).
6. **A real machinery plant for Boat A**: riveted cross-tube boiler on bearers with
   firehole + ashpit doors, gauge glass and cocks, steam gauge on a syphon, twin
   Ramsbottom safety valves, whistle, stop valve, blow-down, feed check; inverted
   vertical single-cylinder engine with cleaded cylinder, crosshead and slide bars,
   overhung crank, Stephenson link with reversing quadrant, drain cocks; feed tank and
   hot-well with hand feed pump; shaft with two flange couplings, plummer block, thrust
   block, stern tube, stuffing boxes; two-bladed screw with helical pitch and flanged
   boss; plate rudder with pintles; coal bunker with fire irons; bilge pump.
7. **Boat's gear to the HMS Bombay model's outfit list** (SLR0975): full set of oars,
   two boat hooks, fenders, anchor or grapnel with cable, bow painter, gratings, side
   benches, water breaker, baler, compass, sidelights (steam), lifebuoy (steam),
   ensign staff and lifting eyes.
8. **Materials**: procedural ring grain for teak/mahogany/oak (direction-aware via
   Generated coordinates), rope twist, canvas weave, polished brass, wrought iron,
   galvanised rowlocks, varnished vs painted surfaces.
9. **Renders** in Cycles at publishable quality from bow-on, stern-on, beam, quarters,
   top, underside, interior angles, machinery and construction close-ups.
10. **Verification** on the new geometry: dimensions to the published spec, containment
    of every internal vertex inside the hull envelope, oar pivots in rowlock throats,
    machinery clearances, triangle caps and UVs on every exported part, displacement to
    the weight schedule.
11. **Interface regeneration**: `interfaces/boats_spec.json` + `BOATS_INTERFACE.md`
    from the new models, with the integration block the ship agent consumes.

Nothing from other agents (`ship/`, `ports/`, QA artefacts) is modified.

---

## 9. Resolution — what generation 2 actually shipped (2026-11-16)

Status of the 11-point reconstruction plan after the first complete build of the
second generation (branch `agent/themistocles-ii`, geometry engine
`boats/scripts/them2/`, Blender 4.2.3 Cycles headless):

| # | Plan item | Outcome |
|---|---|---|
| 1 | New mesh kernel with smooth shading, per-face materials, caps | `geom2.py` — sweeps, lathes, tubes, plates, grids with cap-fans; all builds export smooth-shaded per-face-material meshes |
| 2 | Hull loft + true hydrostatics | `hull2.py` — PCHIP sheer/keel/half-breadth, arc-mapped section sampling, **Sutherland–Hodgman volume clip**, bisection draught solver; all published figures come from the solver |
| 3 | Clinker planking as real overlapping strakes | `structure2.clinker_strakes` — 11 (cutter) / 9 (whaler) strakes with per-strake offset stack, tapering hood ends, sheer strake painted |
| 4 | Complete structure inventory | keel w/ hog, curved stem, transom w/ frame, bent oak frames, keelson, cap rail + inwale + gunmetal rubbing strake w/ rivets, breasthook, risers, quarter knees |
| 5 | Furnished rowing interior | 5 thwarts w/ rounded ends + hanging knees + risers per the SLR1818/SLR0719 decks, side benches + knees at bow and stern sheets, slatted foot gratings, stretchers, mast step + iron clamp on the bow thwart |
| 6 | Real rowing gear | 10 (17 ft whaler: 5, single-banked) shaped oars with looms, leathers and blank stops; swivel rowlocks with pads; plate rudder with pintles/gudgeons and tiller; forged lifting eyes |
| 7 | Complete steam plant | engine bearers bolted to keelson; vertical multitubular boiler with cleading, brass bands, hold-down stays, open fire door with coal; mountings (gauge glass, steam gauge, Ramsbottom safety, whistle, feed check, syphon pigtail); compound engine w/ columns, cleaded cylinders, crossheads, connecting rods, cranks, Stephenson links, throttle wheel, direct-acting pump, condenser; shaft, tube, A-bracket, helical 2-blade bronze screw; funnel w/ sliding extension, wire spark arrestor, 4 bottle-screw guy stays |
| 8 | Consistent flotation | `specs2.reconcile` translates each hull so Z=0 IS the loaded waterline; **consequence:** sections were made fuller because the generation-1 midship sections could not physically carry the crew (displaced volume at gen-1 draught: insufficient by ~40%). Solved draughts recorded in the meta and interface spec |
| 9 | Stowage + outfit per Bombay model list | stowed lug rig (spars taper, canvas bundles lashed w/ gaskets); anchor, grapnel, 6 rope fenders, painters, boat hooks, baler, bucket, breaker, binnacle compass; whaler adds harpoons (sheathed), line tub, drop keel with pivots; steamer adds sidelights, helm station, teak state cabin, canopy tracks, furled White Ensign |
| 10 | Renders | `renders/them2/`: per boat — broadside, bow & stern quarters, bow & stern on, overhead, underside, hero, interior study, skeletal construction study, on-water heroes; steamer adds a machinery-room study. All cameras framed from geometry bounds |
| 11 | Roblox contract honoured | moving parts are separate objects pivoted at rowlock/pintle/shaft hub; per-part ≤19 000 triangles; manifests regenerated from export metadata; `Config.lua` hydro figures corrected; the QA-accepted controller Lua is reused unchanged in behaviour terms |

### Outstanding, honestly stated

- The boats have **not** been play-tested in Roblox Studio on this branch (unit-level
  Lua checks only).  No "playable" claim is made.
- Blender build time: ~60–100 s per boat on CPU; renders 56 samples ≈ 40 s/view.
- Rig set sails are carried stowed only; standing rigging and full sail hoisting is a
  documented follow-up, exactly as the generation-1 QA demanded.

